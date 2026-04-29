import re
from datetime import datetime


def infer_type(value: str) -> str:
    if not value or value.lower() in ("null", "none", "n/a", ""):
        return "null"
    if value.lower() in ("true", "false", "yes", "no"):
        return "boolean"

    cleaned = re.sub(r"[,$%]", "", value).strip()
    try:
        int(cleaned)
        return "integer"
    except ValueError:
        pass
    try:
        float(cleaned)
        return "number"
    except ValueError:
        pass

    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{2}\s+\w+\s+\d{4}",
        r"\w+\s+\d{1,2},?\s+\d{4}",
    ]
    for pattern in date_patterns:
        if re.fullmatch(pattern, value.strip()):
            return "string"  # JSON Schema uses string with format: date

    return "string"


def get_json_schema_type(inferred: str) -> dict:
    type_map = {
        "string": {"type": "string"},
        "integer": {"type": "integer"},
        "number": {"type": "number"},
        "boolean": {"type": "boolean"},
        "null": {"type": ["string", "null"]},
    }
    return type_map.get(inferred, {"type": "string"})


def is_date_value(value: str) -> bool:
    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
    ]
    return any(re.fullmatch(p, value.strip()) for p in date_patterns)


def is_currency_value(value: str) -> bool:
    return bool(re.match(r"^[\$€£¥]?\s*[\d,]+\.?\d*$", value.strip()))


def normalize_key(key: str) -> str:
    key = key.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")
    return key


def build_field_schema(key: str, value: str) -> dict:
    normalized = normalize_key(key)
    inferred = infer_type(value)
    schema = get_json_schema_type(inferred)
    schema["description"] = f"Extracted from field: {key}"

    if is_date_value(value):
        schema["format"] = "date"
    elif is_currency_value(value):
        schema["description"] += " (currency value)"
        if inferred in ("integer", "number"):
            schema["minimum"] = 0

    return normalized, schema


def generate_table_schema(table_rows: list[str]) -> dict:
    if not table_rows:
        return {}

    first_row = re.split(r"\s{2,}|\t|\|", table_rows[0].strip())
    headers = [normalize_key(h) for h in first_row if h.strip()]

    if not headers:
        return {}

    item_properties = {}
    for header in headers:
        item_properties[header] = {
            "type": "string",
            "description": f"Column: {header}",
        }

    if len(table_rows) > 1:
        sample_row = re.split(r"\s{2,}|\t|\|", table_rows[1].strip())
        for i, cell in enumerate(sample_row):
            if i < len(headers) and cell.strip():
                inferred = infer_type(cell.strip())
                item_properties[headers[i]] = get_json_schema_type(inferred)
                item_properties[headers[i]]["description"] = f"Column: {headers[i]}"

    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": item_properties,
            "required": headers,
        },
        "description": "Table data extracted from document",
    }


def generate_section_schema(section: dict) -> dict:
    properties = {}
    kv_pattern = re.compile(
        r"^([A-Za-z][A-Za-z0-9 _/\-\.]{1,60})\s*[:=]\s*(.+)$", re.MULTILINE
    )

    for match in kv_pattern.finditer(section.get("content", "")):
        key = match.group(1).strip()
        value = match.group(2).strip()
        normalized, field_schema = build_field_schema(key, value)
        properties[normalized] = field_schema

    if not properties:
        return {
            "type": "string",
            "description": f"Content of section: {section.get('title', 'Unknown')}",
        }

    return {
        "type": "object",
        "properties": properties,
        "description": f"Section: {section.get('title', 'Unknown')}",
    }


def generate_schema(parsed_data: dict) -> dict:
    properties: dict = {}
    required_fields: list[str] = []

    # Top-level metadata
    properties["document_metadata"] = {
        "type": "object",
        "properties": {
            "page_count": {
                "type": "integer",
                "description": "Total number of pages in the document",
                "minimum": 1,
            },
            "extraction_date": {
                "type": "string",
                "format": "date-time",
                "description": "Date and time when the schema was generated",
            },
        },
        "required": ["page_count", "extraction_date"],
        "description": "Metadata about the source document",
    }
    required_fields.append("document_metadata")

    # Key-value pairs at top level
    kv_pairs = parsed_data.get("key_value_pairs", [])
    if kv_pairs:
        kv_properties = {}
        kv_required = []
        for pair in kv_pairs:
            normalized, field_schema = build_field_schema(pair["key"], pair["value"])
            if normalized not in kv_properties:
                kv_properties[normalized] = field_schema
                kv_required.append(normalized)

        if kv_properties:
            properties["fields"] = {
                "type": "object",
                "properties": kv_properties,
                "required": kv_required[:10],
                "description": "Key-value fields extracted from the document",
            }
            required_fields.append("fields")

    # Tables as arrays of objects
    tables = parsed_data.get("tables", [])
    if tables:
        table_schemas = []
        for i, table in enumerate(tables):
            table_schema = generate_table_schema(table)
            if table_schema:
                table_schemas.append(table_schema)

        if table_schemas:
            if len(table_schemas) == 1:
                properties["line_items"] = table_schemas[0]
                properties["line_items"]["description"] = "Line items / table data"
            else:
                for i, ts in enumerate(table_schemas):
                    properties[f"table_{i + 1}"] = ts
            required_fields.append("line_items" if len(table_schemas) == 1 else "table_1")

    # Sections as nested objects
    sections = parsed_data.get("sections", [])
    if sections:
        for section in sections:
            section_key = normalize_key(section["title"])
            if section_key and section_key not in properties:
                properties[section_key] = generate_section_schema(section)

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "generated-document-schema",
        "title": "Document Schema",
        "description": "Auto-generated JSON Schema from PDF document analysis",
        "type": "object",
        "properties": properties,
        "required": required_fields,
        "additionalProperties": False,
    }

    return schema

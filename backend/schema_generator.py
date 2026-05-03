import re


def infer_type(value: str) -> str:
    if not value or value.lower() in ("null", "none", "n/a", "unknown", ""):
        return "null"
    if value.lower() in ("true", "false", "yes", "no"):
        return "boolean"

    cleaned = value.strip().replace("%", "").replace("$", "").replace("€", "").replace("£", "").replace("¥", "")
    cleaned = re.sub(r"[, ]", "", cleaned)
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
            return "string"

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
    patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{2}\s+\w+\s+\d{4}",
        r"\w+\s+\d{1,2},?\s+\d{4}",
    ]
    text = value.strip()
    return any(re.fullmatch(pattern, text) for pattern in patterns)


def is_currency_value(value: str) -> bool:
    return bool(re.match(r"^[\$€£¥]?\s*[\d,]+\.?\d*%?$", value.strip()))


def is_percent_value(value: str) -> bool:
    return value.strip().endswith("%")


def normalize_key(key: str) -> str:
    key = key.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")
    return key or "field"


def build_field_schema(key: str, value: str) -> dict:
    normalized = normalize_key(key)
    inferred = infer_type(value)
    schema = get_json_schema_type(inferred)
    schema["description"] = f"Extracted from field: {key}"

    if is_date_value(value):
        schema["format"] = "date"
        schema["pattern"] = r"^\d{4}-\d{2}-\d{2}$"
    elif is_percent_value(value):
        schema["type"] = "number"
        schema["minimum"] = 0
        schema["maximum"] = 100
        schema["description"] += " (percentage)"
    elif is_currency_value(value) and schema.get("type") in ("integer", "number"):
        schema.setdefault("minimum", 0)
        schema["description"] += " (currency)"

    return normalized, schema


def generate_table_schema(table_rows: list[str]) -> dict:
    if not table_rows:
        return {}

    first_row = [cell.strip() for cell in re.split(r"\s{2,}|\t|\|", table_rows[0].strip()) if cell.strip()]
    headers = [normalize_key(h) or f"column_{i+1}" for i, h in enumerate(first_row)]

    if not headers:
        return {}

    item_properties: dict = {}
    for header in headers:
        item_properties[header] = {
            "type": "string",
            "description": f"Column: {header}",
        }

    if len(table_rows) > 1:
        sample_row = [cell.strip() for cell in re.split(r"\s{2,}|\t|\|", table_rows[1].strip()) if cell.strip()]
        for i, cell in enumerate(sample_row):
            if i < len(headers):
                inferred = infer_type(cell)
                schema = get_json_schema_type(inferred)
                schema["description"] = f"Column: {headers[i]}"
                if is_currency_value(cell) and schema.get("type") in ("integer", "number"):
                    schema.setdefault("minimum", 0)
                item_properties[headers[i]] = schema

    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": item_properties,
            "required": headers,
        },
        "minItems": 1,
        "description": "Table data extracted from document",
    }


def generate_section_schema(section: dict) -> dict:
    properties: dict = {}
    kv_pattern = re.compile(
        r"^([A-Za-z][A-Za-z0-9 _/\-\.\(\)]{1,80}?)\s*[:=]\s*(.+)$",
        re.MULTILINE,
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
    required_fields: list[str] = ["document_metadata"]
    
    doc_type = parsed_data.get("document_type", "generic_document")

    properties["document_metadata"] = {
        "type": "object",
        "properties": {
            "document_type": {
                "type": "string",
                "enum": ["invoice", "resume", "contract", "receipt", "bank_statement", "generic_document"],
                "description": "Auto-detected document type",
            },
            "page_count": {
                "type": "integer",
                "description": "Total number of pages in the document",
                "minimum": 1,
            },
            "word_count": {
                "type": "integer",
                "description": "Total word count in the document",
                "minimum": 0,
            },
            "extraction_date": {
                "type": "string",
                "format": "date-time",
                "description": "Date and time when the schema was generated",
            },
        },
        "required": ["page_count", "extraction_date"],
        "description": f"Metadata about the source document (Type: {doc_type})",
    }

    kv_pairs = parsed_data.get("key_value_pairs", [])
    if kv_pairs:
        kv_properties: dict = {}
        for pair in kv_pairs:
            normalized, field_schema = build_field_schema(pair["key"], pair["value"])
            if normalized in kv_properties:
                existing = kv_properties[normalized]
                existing_type = existing.get("type")
                new_type = field_schema.get("type")
                if existing_type != new_type:
                    if isinstance(existing_type, list):
                        existing["type"] = list(dict.fromkeys(existing_type + [new_type]))
                    else:
                        existing["type"] = [existing_type, new_type]
                    existing["description"] = f"Mixed values detected for field: {pair['key']}"
            else:
                kv_properties[normalized] = field_schema

        if kv_properties:
            properties["fields"] = {
                "type": "object",
                "properties": kv_properties,
                "description": "Key-value fields extracted from the document",
            }
            required_fields.append("fields")

    tables = parsed_data.get("tables", [])
    for i, table in enumerate(tables):
        table_schema = generate_table_schema(table)
        if table_schema:
            key = "line_items" if i == 0 else f"table_{i+1}"
            properties[key] = table_schema
            if i == 0:
                required_fields.append(key)

    sections = parsed_data.get("sections", [])
    for section in sections:
        section_key = normalize_key(section.get("title", "section"))
        if section_key and section_key not in properties:
            properties[section_key] = generate_section_schema(section)

    if parsed_data.get("document_summary"):
        properties["document_summary"] = {
            "type": "string",
            "description": "Extracted summary/preview of document content",
            "minLength": 1,
        }

    doc_type = parsed_data.get("document_type", "generic_document")
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"document-schema-{doc_type}",
        "title": f"{doc_type.replace('_', ' ').title()} Schema",
        "description": f"Auto-generated JSON Schema from {doc_type.replace('_', ' ')} document analysis",
        "type": "object",
        "properties": properties,
        "required": required_fields,
        "additionalProperties": True,
    }

    return schema

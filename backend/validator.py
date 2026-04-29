from jsonschema import Draft202012Validator, ValidationError


def validate_schema(schema: dict) -> dict:
    errors: list[str] = []

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:
        errors.append(f"Invalid schema structure: {str(e)}")
        return {"valid": False, "errors": errors}

    if schema.get("type") != "object":
        errors.append("Root schema type should be 'object'")

    properties = schema.get("properties", {})
    if not properties:
        errors.append("Schema has no properties defined")

    required = schema.get("required", [])
    for field in required:
        if field not in properties:
            errors.append(f"Required field '{field}' not found in properties")

    _validate_properties_recursive(properties, errors, path="root")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "stats": _compute_schema_stats(schema),
    }


def _validate_properties_recursive(
    properties: dict, errors: list[str], path: str
) -> None:
    for key, prop in properties.items():
        current_path = f"{path}.{key}"
        prop_type = prop.get("type")

        if not prop_type:
            errors.append(f"Missing type at {current_path}")
            continue

        if prop_type == "object":
            nested = prop.get("properties", {})
            if not nested:
                errors.append(f"Empty object at {current_path}")
            else:
                _validate_properties_recursive(nested, errors, current_path)

        elif prop_type == "array":
            items = prop.get("items")
            if not items:
                errors.append(f"Array at {current_path} missing 'items'")
            elif items.get("type") == "object":
                nested = items.get("properties", {})
                _validate_properties_recursive(nested, errors, f"{current_path}[]")

        if isinstance(prop_type, str) and prop_type in ("integer", "number"):
            min_val = prop.get("minimum")
            max_val = prop.get("maximum")
            if min_val is not None and max_val is not None and min_val > max_val:
                errors.append(
                    f"Invalid range at {current_path}: min ({min_val}) > max ({max_val})"
                )


def _compute_schema_stats(schema: dict) -> dict:
    stats = {
        "total_fields": 0,
        "required_fields": 0,
        "optional_fields": 0,
        "nested_objects": 0,
        "arrays": 0,
        "max_depth": 0,
    }
    _count_fields(schema, stats, depth=0)
    return stats


def _count_fields(schema: dict, stats: dict, depth: int) -> None:
    stats["max_depth"] = max(stats["max_depth"], depth)
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    for key, prop in properties.items():
        stats["total_fields"] += 1
        if key in required:
            stats["required_fields"] += 1
        else:
            stats["optional_fields"] += 1

        prop_type = prop.get("type")
        if prop_type == "object":
            stats["nested_objects"] += 1
            _count_fields(prop, stats, depth + 1)
        elif prop_type == "array":
            stats["arrays"] += 1
            items = prop.get("items", {})
            if items.get("type") == "object":
                _count_fields(items, stats, depth + 1)


def add_validation_rules(schema: dict) -> dict:
    properties = schema.get("properties", {})
    _add_rules_recursive(properties)
    return schema


def _add_rules_recursive(properties: dict) -> None:
    for key, prop in properties.items():
        prop_type = prop.get("type")

        if prop_type == "string":
            if "min" not in prop:
                prop["minLength"] = 1
            if prop.get("format") == "date":
                prop["pattern"] = r"^\d{4}-\d{2}-\d{2}$"

        elif prop_type in ("integer", "number"):
            if "currency" in prop.get("description", "").lower():
                prop.setdefault("minimum", 0)

        elif prop_type == "object":
            nested = prop.get("properties", {})
            _add_rules_recursive(nested)

        elif prop_type == "array":
            prop.setdefault("minItems", 0)
            items = prop.get("items", {})
            if items.get("type") == "object":
                nested = items.get("properties", {})
                _add_rules_recursive(nested)


def validate_data_against_schema(data: dict, schema: dict) -> dict:
    validator = Draft202012Validator(schema)
    errors = []
    for error in validator.iter_errors(data):
        errors.append({
            "path": list(error.absolute_path),
            "message": error.message,
            "validator": error.validator,
        })
    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }

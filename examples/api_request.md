# Example API Requests

## Generate Schema from PDF

```bash
curl -X POST http://localhost:8000/api/generate-schema \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "schema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Document Schema",
    "type": "object",
    "properties": { ... },
    "required": [...]
  },
  "validation": {
    "valid": true,
    "errors": [],
    "stats": {
      "total_fields": 18,
      "required_fields": 10,
      "optional_fields": 8,
      "nested_objects": 3,
      "arrays": 1,
      "max_depth": 2
    }
  },
  "document_info": {
    "filename": "invoice.pdf",
    "pages": 3,
    "fields_detected": 15,
    "tables_detected": 1,
    "sections_detected": 4
  }
}
```

## Validate a Schema

```bash
curl -X POST http://localhost:8000/api/validate-schema \
  -H "Content-Type: application/json" \
  -d '{"schema_payload": {"type": "object", "properties": {"name": {"type": "string"}}}}'
```

## Validate Data Against Schema

```bash
curl -X POST http://localhost:8000/api/validate-data \
  -H "Content-Type: application/json" \
  -d '{
    "schema_payload": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "amount": {"type": "number", "minimum": 0}
      },
      "required": ["name", "amount"]
    },
    "data": {
      "name": "Test Invoice",
      "amount": 150.00
    }
  }'
```

## Get Example Schema

```bash
curl http://localhost:8000/api/example-schema
```

## Health Check

```bash
curl http://localhost:8000/api/health
```

## Register User (Auth Scaffold)

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "securepass123"}'
```

## Login (Auth Scaffold)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "securepass123"}'
```

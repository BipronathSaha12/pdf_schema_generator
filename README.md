# PDF Document to JSON Schema Generator

A production-ready full-stack application that analyzes complex PDF documents (invoices, bank statements, resumes) and generates deeply nested JSON schemas with validation rules.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML + TailwindCSS + Vanilla JS
- **Validation:** jsonschema library
- **PDF Parsing:** PyPDF2
- **Authentication:** JWT (scaffold included)

## Features

- Upload PDF documents (25-150 pages supported)
- Extract text, key-value pairs, tables, and sections from PDFs
- Automatically detect fields and structure
- Generate nested JSON Schema (Draft 2020-12)
- Support for objects within arrays, multi-level nesting, required/optional fields, type inference
- Validation rules: required fields, min/max, null checks, sum validation
- Interactive schema editor in the UI
- Download generated schemas as JSON
- REST API with full OpenAPI documentation
- JWT authentication scaffold

## Quick Start

### 1. Install Dependencies

```bash
cd pdf-schema-generator
pip install -r requirements.txt
```

### 2. Run the Server

```bash
uvicorn backend.main:app --reload
```

### 3. Open the App

Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

### 4. API Documentation

Interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
pdf-schema-generator/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, routes, CORS, example schema
│   ├── pdf_parser.py         # PDF text extraction and structure detection
│   ├── schema_generator.py   # JSON schema generation with type inference
│   ├── validator.py          # Schema validation and data validation
│   └── auth.py               # JWT authentication scaffold
├── frontend/
│   └── index.html            # Single-page UI with TailwindCSS
├── examples/
│   ├── invoice_schema.json   # Example invoice JSON schema
│   └── api_request.md        # Example API requests (curl)
├── requirements.txt
├── venv/                     # Python virtual environment
└── README.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/generate-schema` | Upload PDF and generate JSON schema |
| POST | `/generate-schema` | Alias for the above |
| POST | `/api/validate-schema` | Validate a JSON schema |
| POST | `/api/validate-data` | Validate data against a schema |
| GET | `/api/example-schema` | Get example invoice schema |
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |

## Example Usage

### Upload a PDF via API

```bash
curl -X POST http://localhost:8000/api/generate-schema -F "file=@invoice.pdf"
```

### Using the Web UI

1. Open http://localhost:8000
2. Drag & drop a PDF or click to browse
3. Click "Generate Schema"
4. Edit the schema in the built-in editor
5. Download or copy the result

## Schema Features

Generated schemas include:

- **Type inference:** string, integer, number, boolean, date, null
- **Nested objects:** multi-level nesting from document sections
- **Arrays of objects:** from detected tables
- **Validation rules:** minLength, minimum, maximum, format, pattern, required
- **Document metadata:** page count, extraction timestamp
- **Descriptions:** auto-generated field descriptions

# LICENSE
This PDF Document to JSON Schema Generator is under [MIT LICENSE]()# pdf_schema_generator

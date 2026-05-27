# PDF Document to JSON Schema Generator

A Django-based full-stack application that converts PDF documents into structured JSON Schemas and validates them through a lightweight browser UI.

## Tech Stack

- **Backend:** Django + Django REST Framework
- **Frontend:** HTML + Bootstrap + Vanilla JavaScript
- **Styles:** `frontend/styles.css`
- **Scripts:** `frontend/app.js`
- **PDF Parsing:** custom parser in `backend/pdf_parser.py`
- **Schema Generation:** `backend/schema_generator.py`
- **Validation:** `backend/validator.py`

## Features

- Upload PDF documents and generate JSON Schema output
- Detect document fields, tables, sections, and metadata
- Build nested JSON Schema conforming to Draft 2020-12
- Validate schemas and data via REST endpoints
- Interactive editor with copy, format, validate, and download actions
- Built-in example schema preview and API health check
- JWT authentication scaffold for future extension

## Quick Start

1. Install dependencies

```bash
cd f:\pdf-schema-generator
python -m pip install -r requirements.txt
```

2. Run database migrations (optional on first run)

```bash
python manage.py migrate
```

3. Start the development server

```bash
python manage.py runserver
```

4. Open the app

Navigate to `http://localhost:8000`

## Frontend Files

- `frontend/index.html` — main UI template
- `frontend/bootstrap.css` — Bootstrap stylesheet entrypoint for static loading
- `frontend/styles.css` — extracted CSS styles
- `frontend/app.js` — UI and API integration logic

## Deploying to Render

- `render.yaml` configures a Python web service on Render.
- `Procfile` starts the app with `gunicorn config.wsgi`.
- `whitenoise` is enabled in Django to serve static assets in production.

## Project Structure

```
pdf-schema-generator/
├── backend/
│   ├── __init__.py
│   ├── apps.py
│   ├── pdf_parser.py
│   ├── schema_generator.py
│   ├── serializers.py
│   ├── validator.py
│   ├── views.py
│   └── urls.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── examples/
│   ├── api_request.md
│   └── invoice_schema.json
├── db.sqlite3
├── manage.py
├── README.md
└── requirements.txt
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/generate-schema` | Upload PDF and generate JSON Schema |
| POST | `/generate-schema` | Alias for schema generation |
| POST | `/api/validate-schema` | Validate a JSON schema payload |
| POST | `/api/validate-data` | Validate data against a schema |
| GET | `/api/example-schema` | Fetch an example invoice schema |
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive JWT token |

## Using the Web UI

1. Open `http://localhost:8000`
2. Drop a PDF or click to browse
3. Confirm the selected file
4. Click **Generate Schema**
5. Edit the schema, then copy, validate, format, or download it

## Example API Request

```bash
curl -X POST http://localhost:8000/api/generate-schema -F "file=@invoice.pdf"
```

## Notes

- The frontend is split into `frontend/index.html`, `frontend/styles.css`, and `frontend/app.js`.
- The backend uses Django views and DRF endpoints defined in `backend/views.py` and `backend/urls.py`.

## Database

See [`DATABASE.md`](./DATABASE.md) for a full description of the SQLite database, table list, ER diagram, and inspection commands.

**TL;DR:** SQLite (`db.sqlite3`) holding only Django's built-in `auth_*`, `django_session`, `django_content_type`, `django_migrations`, and `django_admin_log` tables. The project defines **no custom models** — PDF processing is entirely in-memory.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

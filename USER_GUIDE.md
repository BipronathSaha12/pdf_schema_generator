# PDF Schema Generator - User Guide

## ✅ What Has Been Fixed

The backend now generates **unique, accurate JSON schemas** for each document. Previously, all documents produced the same generic schema. Now:

- **Document Type Detection**: System automatically detects invoice, resume, contract, receipt, bank statement, or generic documents
- **Content-Specific Extraction**: Each document generates a unique schema based on its actual content
- **Extracted Data Included**: The API response includes both the schema AND the actual extracted data from your document
- **Better Field Detection**: Improved patterns to capture more accurate key-value pairs, tables, and sections

---

## 📋 How to Use the Application

### Step 1: Upload Your Document
1. Open the application in your browser
2. **Drag & Drop** a PDF file into the center drop zone, OR click to browse and select a file
3. Confirm when prompted

### Step 2: Generate Schema
1. Click the **"Generate Schema"** button
2. The system will:
   - Detect the document type (invoice, resume, contract, etc.)
   - Extract all key-value pairs from the document
   - Identify tables and sections
   - Generate a JSON schema that matches THIS specific document's structure
   - Extract and display actual data from the document

### Step 3: Review Results

The results section shows:

#### **Document Statistics**
- **Pages**: Total number of pages
- **Fields Detected**: Number of key-value pairs found
- **Tables Found**: Number of tables in the document
- **Sections**: Number of document sections identified

#### **Extracted Data**
The response now includes actual data extracted from your document:
```json
{
  "extracted_data": {
    "document_type": "invoice",
    "summary": "First 500 characters of document...",
    "fields": {
      "Invoice Number": "INV-2024-001",
      "Date": "2024-01-15",
      "Customer Name": "John Doe"
    },
    "sections": {
      "PAYMENT TERMS": "Net 30",
      "SHIPPING": "Standard Shipping"
    },
    "tables": [...]
  }
}
```

#### **Generated Schema**
- Shows the JSON Schema structure for this document
- Includes field types (string, number, date, boolean, etc.)
- Shows required vs optional fields
- Contains descriptions of each field

### Step 4: Edit, Validate & Download

- **Copy**: Copy the entire schema to clipboard
- **Format**: Auto-format the JSON for readability
- **Validate**: Check if the schema is valid (green = valid, yellow = warnings)
- **Download**: Save the schema as a JSON file

---

## 🎯 Understanding the Output

### Schema Structure

Each schema now includes:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "document-schema-invoice",
  "title": "Invoice Schema",
  "description": "Auto-generated JSON Schema from invoice document analysis",
  "type": "object",
  "properties": {
    "document_metadata": {
      "type": "object",
      "properties": {
        "document_type": "invoice",
        "page_count": 2,
        "word_count": 1250,
        "extraction_date": "2024-01-15T10:30:00Z"
      }
    },
    "fields": {
      "type": "object",
      "properties": {
        "invoice_number": { "type": "string" },
        "amount": { "type": "number" },
        "date": { "type": "string", "format": "date" }
      }
    }
  }
}
```

### Different Document Types Generate Different Schemas

**Invoice Document:**
- Extracts: Invoice numbers, dates, amounts, customer info
- Detects: Line items, totals, tax information
- Schema includes currency and amount fields

**Resume Document:**
- Extracts: Name, contact info, experience, education
- Detects: Work sections, skill sections
- Schema includes experience periods and skills

**Contract Document:**
- Extracts: Parties, effective date, terms
- Detects: Terms and conditions, obligations
- Schema includes date ranges and legal clauses

**Bank Statement Document:**
- Extracts: Account info, transactions, balances
- Detects: Transaction details, dates
- Schema includes amounts and transaction types

---

## 🔧 How Each File Works

### `backend/pdf_parser.py` - Extracts Content
- **extract_text_from_pdf()**: Reads text from PDF pages
- **extract_key_value_pairs()**: Finds field:value patterns
- **extract_tables()**: Detects table structures
- **detect_sections()**: Identifies document sections
- **detect_document_type()**: Classifies document type based on keywords

### `backend/schema_generator.py` - Creates Schema
- **build_field_schema()**: Infers type from a value
- **generate_table_schema()**: Creates schema for tables
- **generate_section_schema()**: Creates schema for sections
- **generate_schema()**: Combines everything into final JSON schema

### `backend/validator.py` - Validates Quality
- **validate_schema()**: Ensures schema is valid JSON Schema format
- **validate_data_against_schema()**: Checks if extracted data matches schema
- **add_validation_rules()**: Adds constraints (min/max lengths, patterns, etc.)

### `frontend/app.js` - User Interface
- **Drag & Drop**: File upload with visual feedback
- **Theme Toggle**: Light/Dark mode (persisted in localStorage)
- **Schema Editor**: Live editing with syntax highlighting
- **Copy/Download**: Export functionality

---

## ⚠️ Important Notes

### Each Document Gets Unique Output
- Same document type still produces different schemas based on content
- Schemas are NOT generic templates anymore
- Each upload generates fresh analysis

### Supported Document Types
- **Invoice**: Billing and payment documents
- **Resume**: CV and job application documents
- **Contract**: Legal agreement documents
- **Receipt**: Transaction and purchase receipts
- **Bank Statement**: Financial account statements
- **Generic Document**: Any other document type

### Limitations
- Maximum file size: 50MB
- Maximum pages read: 150 pages per document
- Extract limited to first 100 key-value pairs
- Limited to 20 detected sections

---

## 🚀 Troubleshooting

**Q: All my documents still produce the same schema**
A: Clear your browser cache and refresh. The new version should generate unique schemas per document. Check the `document_metadata.document_type` field - it should be different for different documents.

**Q: Some fields are not being extracted**
A: The parser looks for `Key: Value` or `Key = Value` patterns. If your document uses different formatting, it may not be detected. Fields separated by spaces or symbols may need manual adjustment in the editor.

**Q: The extracted data doesn't match my document**
A: Click **Validate** to check for issues. Edit fields directly in the schema editor if needed. The system extracts based on text recognition, so PDFs with images or scanned text may have issues.

**Q: How do I deploy this?**
A: Use the provided `render.yaml` and `Procfile` files to deploy on Render.com. See README.md for deployment instructions.

---

## 📱 Mobile Usage

The application is fully responsive:
- Touch-friendly interface on phones/tablets
- Drop zone works with file picker on mobile
- Schema editor is optimized for smaller screens
- All functions accessible from mobile

Use the **Theme Toggle** (moon icon) to switch between light and dark modes for comfortable viewing.

---

## 💡 Tips & Best Practices

1. **Start Simple**: Begin with standard documents (invoices, resumes) to see how the system works
2. **Check Extracted Data**: Always review the extracted_data field to see what the system found
3. **Validate After Editing**: After modifying the schema, click Validate to ensure it's still valid
4. **Use Document Type**: The auto-detected document_type helps filter and organize schemas
5. **Download & Store**: Download generated schemas for backup and version control

---

## 📞 API Response Example

When you upload a document, you receive:

```json
{
  "schema": { /* Full JSON Schema */ },
  "validation": {
    "valid": true,
    "errors": [],
    "stats": {
      "total_fields": 24,
      "required_fields": 8,
      "optional_fields": 16,
      "max_depth": 3
    }
  },
  "extracted_data": {
    "document_type": "invoice",
    "summary": "Document content preview...",
    "fields": { /* Actual extracted fields */ },
    "sections": { /* Detected sections */ },
    "tables": [ /* Extracted tables */ ]
  },
  "document_info": {
    "filename": "invoice.pdf",
    "document_type": "invoice",
    "pages": 2,
    "word_count": 1250,
    "fields_detected": 15,
    "tables_detected": 1,
    "sections_detected": 4
  }
}
```

---

**Now each document generates a unique, accurate schema that reflects its actual content!**

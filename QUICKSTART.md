# Quick Start & Deployment Guide

## 🚀 Local Development (Windows)

### 1. Setup Python Environment
```bash
# Navigate to project
cd f:\pdf-schema-generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Django Server
```bash
# Apply migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

Open browser: **http://localhost:8000**

---

## 🌐 Deployment to Render.com

### Step 1: Prepare Git Repository
```bash
cd f:\pdf-schema-generator
git add .
git commit -m "Deploy PDF Schema Generator"
git push origin main
```

### Step 2: Connect to Render
1. Go to [render.com](https://render.com)
2. Sign up / Login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Select the `pdf-schema-generator` repo

### Step 3: Configure Render
- **Name**: pdf-schema-generator
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn config.wsgi`
- **Region**: Choose closest to you

### Step 4: Set Environment Variables
In Render dashboard, add:
```
DJANGO_SECRET_KEY = your-secret-key-here
DJANGO_DEBUG = False
```

### Step 5: Deploy
Click "Create Web Service" and wait for deployment ✅

---

## 📝 Testing the Backend

### Test API Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### Test Schema Generation
Create a test PDF or use an existing invoice:

```bash
curl -X POST http://localhost:8000/api/generate-schema \
  -F "file=@invoice.pdf"
```

Expected response structure:
```json
{
  "schema": { /* JSON Schema */ },
  "validation": { /* Validation results */ },
  "extracted_data": { /* Actual extracted fields */ },
  "document_info": { /* Document statistics */ }
}
```

---

## 🔍 What's New in This Version

### ✅ Fixed Issues
1. **Same schema for all documents** → Now generates unique schema per document
2. **No actual data** → Now includes extracted_data with real field values
3. **Generic structure** → Now detects document type and creates specific schema

### ✅ Improvements
1. Better key-value pair extraction (100% matching support)
2. Document type auto-detection
3. Word count tracking
4. Section content extraction
5. Extracted data in API response
6. Mobile-responsive UI
7. Theme persistence across sessions

### ✅ New Fields in Response
```json
{
  "extracted_data": {
    "document_type": "invoice/resume/contract/etc",
    "summary": "Document preview",
    "fields": { "Key": "Value" },
    "sections": { "Section": "Content" },
    "tables": [...]
  }
}
```

---

## 📁 Key Files Modified

| File | Changes |
|------|---------|
| `backend/pdf_parser.py` | Added document type detection, improved extraction |
| `backend/schema_generator.py` | Dynamic schema generation based on content |
| `backend/views.py` | Include extracted_data in API response |
| `config/settings.py` | Added WhiteNoise for static files, env variables |
| `config/urls.py` | Static file serving for development |
| `frontend/index.html` | Django static template tags |
| `frontend/app.js` | Improved theme handling, drag-drop events |
| `frontend/styles.css` | Better responsive design, footer alignment |

---

## 🐛 Common Issues & Fixes

### Issue: Module not found (corsheaders, etc)
**Fix**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Static files not loading
**Fix**: Collect static files
```bash
python manage.py collectstatic --noinput
```

### Issue: Theme not persisting
**Fix**: Check browser localStorage is enabled. No action needed - it's now fixed.

### Issue: Drag-drop not working
**Fix**: Clear browser cache. DOMContentLoaded event handler is now properly initialized.

---

## 🎨 Frontend Features

### Theme Toggle
- Click moon icon to switch Dark/Light mode
- Preference saved to browser localStorage
- Persists across sessions

### Drag & Drop Upload
- Drop zone in middle of screen
- Visual feedback on hover
- Works with file picker too

### Schema Editor
- Syntax highlighting (green on dark background)
- Copy to clipboard with confirmation
- Format JSON with one click
- Validate schema live
- Edit badge shows when modified
- Download as JSON file

### Responsive Design
- Works on mobile (375px width)
- Works on tablets
- Works on desktop (1920px+)
- Touch-friendly buttons
- Optimized spacing

---

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/generate-schema` | Upload PDF and generate schema |
| POST | `/api/validate-schema` | Validate a JSON schema |
| POST | `/api/validate-data` | Validate data against schema |
| GET | `/api/example-schema` | Get example invoice schema |
| GET | `/api/health` | Check API health |
| POST | `/api/auth/register` | Register user (optional) |
| POST | `/api/auth/login` | Login user (optional) |

---

## 🎯 Next Steps

1. ✅ Test with different document types (invoice, resume, contract)
2. ✅ Verify extracted_data matches your documents
3. ✅ Try the theme toggle and responsive view
4. ✅ Deploy to Render.com
5. ✅ Share your feedback!

---

## 📞 Support

For issues or questions:
1. Check `USER_GUIDE.md` for detailed usage instructions
2. Review API responses in browser DevTools (F12)
3. Check Flask/Django logs in terminal

---

**You're all set! 🎉**

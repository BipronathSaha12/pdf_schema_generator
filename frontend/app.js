let selectedFile = null;
let currentSchema = null;
let originalSchema = null;

function setTheme(isDark) {
    const themeIcon = document.getElementById('theme-icon');
    document.body.classList.toggle('dark-theme', isDark);
    if (isDark) {
        themeIcon.classList.remove('bi-moon-stars');
        themeIcon.classList.add('bi-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        themeIcon.classList.remove('bi-sun');
        themeIcon.classList.add('bi-moon-stars');
        localStorage.setItem('theme', 'light');
    }
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme === 'dark');
}

function toggleTheme() {
    const isDark = !document.body.classList.contains('dark-theme');
    setTheme(isDark);
}

window.addEventListener('DOMContentLoaded', () => {
    initTheme();

    const dropZone = document.getElementById('drop-zone');
    if (!dropZone) return;

    ['dragenter', 'dragover'].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].name.toLowerCase().endsWith('.pdf')) {
            selectedFile = files[0];
            showFileInfo();
            showConfirmationDialog();
        }
    });
});

function handleFileSelect(event) {
    selectedFile = event.target.files[0];
    if (selectedFile) {
        showFileInfo();
        showConfirmationDialog();
    }
}

function showConfirmationDialog() {
    document.getElementById('confirm-file-name').textContent = selectedFile.name;
    const sizeMB = (selectedFile.size / (1024 * 1024)).toFixed(2);
    document.getElementById('confirm-file-size').textContent = `${sizeMB} MB`;

    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    confirmModal.show();
}

function confirmGenerateSchema() {
    generateSchema();
}

function showFileInfo() {
    document.getElementById('file-info').classList.remove('d-none');
    document.getElementById('file-name').textContent = selectedFile.name;
    const sizeMB = (selectedFile.size / (1024 * 1024)).toFixed(2);
    document.getElementById('file-size').textContent = `${sizeMB} MB`;
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').classList.add('d-none');
    document.getElementById('results-section').classList.add('d-none');
    document.getElementById('error-section').classList.add('d-none');
}

async function generateSchema() {
    if (!selectedFile) return;

    document.getElementById('loading').classList.remove('d-none');
    document.getElementById('results-section').classList.add('d-none');
    document.getElementById('error-section').classList.add('d-none');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/generate-schema', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to generate schema');
        }

        const data = await response.json();
        currentSchema = data.schema;
        originalSchema = JSON.stringify(data.schema);
        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loading').classList.add('d-none');
    }
}

function displayResults(data) {
    const info = data.document_info;
    document.getElementById('stat-pages').textContent = info.pages;
    document.getElementById('stat-fields').textContent = info.fields_detected;
    document.getElementById('stat-tables').textContent = info.tables_detected;
    document.getElementById('stat-sections').textContent = info.sections_detected;

    displayValidation(data.validation);

    document.getElementById('schema-editor').value = JSON.stringify(data.schema, null, 2);
    document.getElementById('results-section').classList.remove('d-none');
    document.getElementById('edit-badge').classList.add('d-none');
}

function displayValidation(validation) {
    const iconEl = document.getElementById('validation-icon');
    const textEl = document.getElementById('validation-text');
    const statsEl = document.getElementById('schema-stats');

    if (validation.valid) {
        iconEl.innerHTML = '<i class="bi bi-check-circle-fill text-success" style="font-size: 1.5rem;"></i>';
        textEl.textContent = 'Schema is valid';
        textEl.className = 'fw-semibold text-success';
    } else {
        iconEl.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-warning" style="font-size: 1.5rem;"></i>';
        textEl.textContent = `${validation.errors.length} validation warning(s)`;
        textEl.className = 'fw-semibold text-warning';
    }

    if (validation.stats) {
        const s = validation.stats;
        statsEl.innerHTML = `
            <span>Fields: ${s.total_fields}</span>
            <span>Required: ${s.required_fields}</span>
            <span>Optional: ${s.optional_fields}</span>
            <span>Depth: ${s.max_depth}</span>
        `;
    }
}

function onSchemaEdit() {
    const editor = document.getElementById('schema-editor');
    const badge = document.getElementById('edit-badge');
    if (editor.value !== originalSchema) {
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
}

function formatSchema() {
    const editor = document.getElementById('schema-editor');
    try {
        const parsed = JSON.parse(editor.value);
        editor.value = JSON.stringify(parsed, null, 2);
        currentSchema = parsed;
    } catch (e) {
        showError('Invalid JSON: ' + e.message);
    }
}

async function revalidateSchema() {
    const editor = document.getElementById('schema-editor');
    try {
        const parsed = JSON.parse(editor.value);
        const response = await fetch('/api/validate-schema', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ schema_payload: parsed }),
        });
        const result = await response.json();
        displayValidation(result);
    } catch (e) {
        showError('Invalid JSON: ' + e.message);
    }
}

function copySchema(event) {
    const editor = document.getElementById('schema-editor');
    navigator.clipboard.writeText(editor.value).then(() => {
        const btn = event.currentTarget;
        const original = btn.innerHTML;
        btn.innerHTML = '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/></svg> Copied!';
        setTimeout(() => { btn.innerHTML = original; }, 2000);
    });
}

function downloadSchema() {
    const editor = document.getElementById('schema-editor');
    const blob = new Blob([editor.value], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const filename = selectedFile
        ? selectedFile.name.replace('.pdf', '_schema.json')
        : 'schema.json';
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

async function loadExample() {
    try {
        const response = await fetch('/api/example-schema');
        const schema = await response.json();
        currentSchema = schema;
        originalSchema = JSON.stringify(schema);

        document.getElementById('stat-pages').textContent = '3';
        document.getElementById('stat-fields').textContent = '24';
        document.getElementById('stat-tables').textContent = '1';
        document.getElementById('stat-sections').textContent = '6';

        const validation = {
            valid: true,
            stats: { total_fields: 24, required_fields: 14, optional_fields: 10, max_depth: 3 }
        };
        displayValidation(validation);

        document.getElementById('schema-editor').value = JSON.stringify(schema, null, 2);
        document.getElementById('results-section').classList.remove('d-none');
        document.getElementById('edit-badge').classList.add('d-none');
        document.getElementById('error-section').classList.add('d-none');
    } catch (e) {
        showError('Failed to load example: ' + e.message);
    }
}

async function showHealthStatus() {
    const healthModal = new bootstrap.Modal(document.getElementById('healthModal'));
    healthModal.show();

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        const healthContent = document.getElementById('health-content');
        if (response.ok) {
            healthContent.innerHTML = `
                <div class="alert alert-success mb-0">
                    <i class="bi bi-check-circle-fill"></i> <strong>API is Healthy</strong>
                    <hr>
                    <div class="text-start small">
                        <p class="mb-1"><strong>Status:</strong> ${data.status}</p>
                        <p class="mb-0"><strong>Version:</strong> ${data.version}</p>
                    </div>
                </div>
            `;
        } else {
            healthContent.innerHTML = `
                <div class="alert alert-danger mb-0">
                    <i class="bi bi-exclamation-triangle-fill"></i> <strong>API Error</strong>
                    <hr>
                    <pre class="text-start mb-0" style="font-size: 12px; max-height: 200px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
        }
    } catch (error) {
        const healthContent = document.getElementById('health-content');
        healthContent.innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="bi bi-exclamation-triangle-fill"></i> <strong>Connection Error</strong>
                <p class="text-start mt-2 mb-0">${error.message}</p>
            </div>
        `;
    }
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-section').classList.remove('d-none');
}

import re
from typing import Optional

from PyPDF2 import PdfReader


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned_lines: list[str] = []
    for line in lines:
        if line.endswith("-") and cleaned_lines:
            cleaned_lines[-1] += line[:-1]
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def extract_text_from_pdf(file_path: str, max_pages: int = 150) -> str:
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    pages_to_read = min(total_pages, max_pages)

    text_parts: list[str] = []
    for i in range(pages_to_read):
        page = reader.pages[i]
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text.strip())

    raw_text = "\n\n".join(text_parts)
    return clean_text(raw_text)


def extract_key_value_pairs(text: str) -> list[dict]:
    pairs: list[dict] = []
    patterns = [
        r"^([A-Za-z][A-Za-z0-9 _/\-\.\(\)]{1,100}?)\s*:\s*(.+?)(?=\n|$)",
        r"^([A-Za-z][A-Za-z0-9 _/\-\.\(\)]{1,100}?)\s*=\s*(.+?)(?=\n|$)",
    ]
    
    seen_keys = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.MULTILINE):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key and value and len(key) > 2 and len(value) > 1 and key.lower() not in seen_keys:
                pairs.append({"key": key, "value": value})
                seen_keys.add(key.lower())
    
    return pairs[:100]


def extract_tables(text: str) -> list[list[str]]:
    tables: list[list[str]] = []
    current_table: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            if len(current_table) >= 2:
                tables.append(current_table)
            current_table = []
            continue

        separators = stripped.count("|") + stripped.count("\t")
        columns = len([cell for cell in re.split(r"\s{2,}|\t|\|", stripped) if cell.strip()])
        if separators >= 1 or columns >= 3:
            current_table.append(stripped)
        else:
            if len(current_table) >= 2:
                tables.append(current_table)
            current_table = []

    if len(current_table) >= 2:
        tables.append(current_table)

    return tables


def detect_document_type(text: str) -> str:
    """Detect the type of document based on content patterns."""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['invoice', 'bill', 'payment', 'amount due']):
        return 'invoice'
    elif any(word in text_lower for word in ['resume', 'cv', 'experience', 'education', 'skills']):
        return 'resume'
    elif any(word in text_lower for word in ['contract', 'agreement', 'terms', 'conditions']):
        return 'contract'
    elif any(word in text_lower for word in ['receipt', 'transaction', 'purchased']):
        return 'receipt'
    elif any(word in text_lower for word in ['statement', 'account', 'balance', 'transaction']):
        return 'bank_statement'
    else:
        return 'generic_document'


def detect_sections(text: str) -> list[dict]:
    sections: list[dict] = []
    section_pattern = re.compile(r"^([A-Z][A-Z0-9 &/\-.]{2,80})$", re.MULTILINE)

    matches = list(section_pattern.finditer(text))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            sections.append({
                "title": match.group(1).strip(),
                "content": content[:500],
            })

    return sections[:20]


def parse_pdf(file_path: str, max_pages: int = 150) -> dict:
    reader = PdfReader(file_path)
    text = extract_text_from_pdf(file_path, max_pages)
    return {
        "raw_text": text,
        "document_summary": text[:500].strip(),
        "document_type": detect_document_type(text),
        "key_value_pairs": extract_key_value_pairs(text),
        "tables": extract_tables(text),
        "sections": detect_sections(text),
        "page_count": len(reader.pages),
        "word_count": len(text.split()),
    }

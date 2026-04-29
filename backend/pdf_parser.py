import re
from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path: str, max_pages: int = 150) -> str:
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    pages_to_read = min(total_pages, max_pages)

    text_parts: list[str] = []
    for i in range(pages_to_read):
        page_text = reader.pages[i].extract_text()
        if page_text:
            text_parts.append(page_text.strip())

    return "\n\n".join(text_parts)


def extract_key_value_pairs(text: str) -> list[dict]:
    pairs: list[dict] = []
    kv_pattern = re.compile(
        r"^([A-Za-z][A-Za-z0-9 _/\-\.]{1,60})\s*[:=]\s*(.+)$", re.MULTILINE
    )
    for match in kv_pattern.finditer(text):
        key = match.group(1).strip()
        value = match.group(2).strip()
        pairs.append({"key": key, "value": value})
    return pairs


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
        columns = len(re.split(r"\s{2,}|\t|\|", stripped))
        if separators >= 1 or columns >= 3:
            current_table.append(stripped)
        else:
            if len(current_table) >= 2:
                tables.append(current_table)
            current_table = []

    if len(current_table) >= 2:
        tables.append(current_table)

    return tables


def detect_sections(text: str) -> list[dict]:
    sections: list[dict] = []
    section_pattern = re.compile(
        r"^([A-Z][A-Z0-9 &/\-]{2,50})$", re.MULTILINE
    )

    matches = list(section_pattern.finditer(text))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections.append({
            "title": match.group(1).strip(),
            "content": content[:500],
        })

    return sections


def parse_pdf(file_path: str, max_pages: int = 150) -> dict:
    text = extract_text_from_pdf(file_path, max_pages)
    return {
        "raw_text": text,
        "key_value_pairs": extract_key_value_pairs(text),
        "tables": extract_tables(text),
        "sections": detect_sections(text),
        "page_count": len(PdfReader(file_path).pages),
    }

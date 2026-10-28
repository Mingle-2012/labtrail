"""Document ingestion: PDF, Markdown, TXT, CSV parsing and chunking."""
import csv
import io
import logging
from pathlib import Path
from typing import Any

import fitz  # pymupdf

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt", ".csv", ".log"}
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def parse_file(file_path: str, file_name: str) -> list[dict[str, Any]]:
    ext = Path(file_name).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}")

    if ext == ".pdf":
        return parse_pdf(file_path, file_name)
    elif ext == ".md":
        return parse_markdown(file_path, file_name)
    elif ext == ".txt" or ext == ".log":
        return parse_text(file_path, file_name)
    elif ext == ".csv":
        return parse_csv(file_path, file_name)
    return []


def parse_pdf(file_path: str, file_name: str) -> list[dict[str, Any]]:
    chunks = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text().strip()
            if not text:
                continue
            page_chunks = _chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
            for i, chunk_text in enumerate(page_chunks):
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "file_name": file_name,
                        "file_type": "pdf",
                        "page": page_num + 1,
                        "chunk_index": i,
                        "total_chunks": len(page_chunks),
                    },
                })
        doc.close()
    except Exception as e:
        logger.error("PDF parsing error for %s: %s", file_name, e)
        raise ValueError(f"Failed to parse PDF: {e}")
    return chunks


def parse_markdown(file_path: str, file_name: str) -> list[dict[str, Any]]:
    text = Path(file_path).read_text(encoding="utf-8")
    sections = _split_markdown_sections(text)
    chunks = []
    for i, section in enumerate(sections):
        section_chunks = _chunk_text(section, CHUNK_SIZE, CHUNK_OVERLAP)
        for j, chunk_text in enumerate(section_chunks):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "file_name": file_name,
                    "file_type": "markdown",
                    "section": i + 1,
                    "chunk_index": j,
                },
            })
    return chunks


def parse_text(file_path: str, file_name: str) -> list[dict[str, Any]]:
    text = Path(file_path).read_text(encoding="utf-8")
    chunks = []
    text_chunks = _chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    for i, chunk_text in enumerate(text_chunks):
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "file_name": file_name,
                "file_type": "text",
                "chunk_index": i,
                "total_chunks": len(text_chunks),
            },
        })
    return chunks


def parse_csv(file_path: str, file_name: str) -> list[dict[str, Any]]:
    chunks = []
    try:
        text = Path(file_path).read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return chunks

        headers = list(rows[0].keys())
        header_text = f"CSV file: {file_name}\nColumns: {', '.join(headers)}\n"
        chunks.append({
            "text": header_text + f"Total rows: {len(rows)}\nFirst few rows:\n" + "\n".join(
                str(row) for row in rows[:5]
            ),
            "metadata": {
                "file_name": file_name,
                "file_type": "csv",
                "total_rows": len(rows),
                "headers": str(headers),
            },
        })

        batch_size = 20
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            batch_text = "\n".join(str(row) for row in batch)
            chunks.append({
                "text": batch_text,
                "metadata": {
                    "file_name": file_name,
                    "file_type": "csv",
                    "row_start": i,
                    "row_end": min(i + batch_size, len(rows)),
                },
            })
    except Exception as e:
        logger.error("CSV parsing error for %s: %s", file_name, e)
        raise ValueError(f"Failed to parse CSV: {e}")
    return chunks


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


def _split_markdown_sections(text: str) -> list[str]:
    sections = []
    current = []
    for line in text.split("\n"):
        if line.startswith("# ") and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    return sections if sections else [text]

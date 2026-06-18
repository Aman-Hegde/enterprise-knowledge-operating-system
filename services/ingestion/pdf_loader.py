"""Utilities for extracting and chunking text from PDF documents."""

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from every page of a PDF file."""
    pdf_path = Path(file_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Some PDF pages contain images only, so extract_text() may return None.
    reader = PdfReader(pdf_path)
    page_texts = [page.extract_text() or "" for page in reader.pages]

    return "\n".join(page_texts).strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    """Split text into character-based chunks with overlap between them."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap

    # Moving forward by `step` preserves the requested overlap.
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size]
        if chunk:
            chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks

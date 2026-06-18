"""Manual test script for the Sprint 1 PDF ingestion module."""

from pathlib import Path
import sys

# Add the repository root so imports work when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.ingestion.pdf_loader import (
    extract_text_from_pdf,
    split_text_into_chunks,
)


def main() -> None:
    """Extract and chunk the sample PDF, then print a short summary."""
    # Build the path from the repository root so the script works reliably.
    pdf_path = PROJECT_ROOT / "data" / "sample_documents" / "sample.pdf"

    text = extract_text_from_pdf(str(pdf_path))
    chunks = split_text_into_chunks(text)

    print(f"Total characters extracted: {len(text)}")
    print(f"Total chunks created: {len(chunks)}")
    print("\nPreview of first chunk:")
    print(chunks[0] if chunks else "[No text was extracted from the PDF]")


if __name__ == "__main__":
    main()

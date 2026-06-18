"""Manual end-to-end test for the Sprint 3 RAG pipeline."""

from pathlib import Path
import sys

# Add the repository root so this script can be run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.retrieval.rag_pipeline import run_rag_pipeline

QUERY = "What skills does Aman have?"


def main() -> None:
    """Run RAG against the sample PDF and display each pipeline result."""
    pdf_path = PROJECT_ROOT / "data" / "sample_documents" / "sample.pdf"
    answer, retrieved_chunks = run_rag_pipeline(
        pdf_path=str(pdf_path),
        query=QUERY,
        top_k=3,
    )

    print("=" * 60)
    print("QUERY")
    print("=" * 60)
    print(QUERY)

    print("\n" + "=" * 60)
    print("RETRIEVED CONTEXT")
    print("=" * 60)
    for index, chunk in enumerate(retrieved_chunks, start=1):
        print(f"\nChunk {index}:")
        print(chunk)

    print("\n" + "=" * 60)
    print("FINAL GEMINI ANSWER")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()

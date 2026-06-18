"""Manual end-to-end test for the Sprint 6 GraphRAG pipeline."""

from pathlib import Path
import sys

# Add the repository root so this script can be run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.embeddings.embedding_service import generate_embeddings
from services.ingestion.pdf_loader import (
    extract_text_from_pdf,
    split_text_into_chunks,
)
from services.retrieval.graphrag_pipeline import run_graphrag_pipeline
from services.retrieval.vector_store import add_chunks, create_collection

COLLECTION_NAME = "ekos_documents"
QUERY = "What projects has Aman built and what skills does he have?"


def main() -> None:
    """Prepare vector data and run a GraphRAG question."""
    pdf_path = PROJECT_ROOT / "data" / "sample_documents" / "sample.pdf"
    text = extract_text_from_pdf(str(pdf_path))
    chunks = split_text_into_chunks(text)

    if not chunks:
        raise ValueError("No text chunks could be created from the sample PDF")

    # Qdrant is in-memory, so this script indexes the sample on every run.
    embeddings = generate_embeddings(chunks)
    create_collection(COLLECTION_NAME, vector_size=len(embeddings[0]))
    add_chunks(COLLECTION_NAME, chunks, embeddings)

    answer, vector_context, graph_context = run_graphrag_pipeline(
        question=QUERY,
        collection_name=COLLECTION_NAME,
        top_k=3,
    )

    print("=" * 60)
    print("QUERY")
    print("=" * 60)
    print(QUERY)

    print("\n" + "=" * 60)
    print("VECTOR CONTEXT")
    print("=" * 60)
    for index, chunk in enumerate(vector_context, start=1):
        print(f"\nChunk {index}:")
        print(chunk)

    print("\n" + "=" * 60)
    print("GRAPH CONTEXT")
    print("=" * 60)
    print(graph_context or "[No graph relationships found]")

    print("\n" + "=" * 60)
    print("FINAL GRAPHRAG ANSWER")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()

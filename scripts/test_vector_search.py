"""Manual end-to-end test for PDF embedding and vector search."""

from pathlib import Path
import sys

# Add the repository root so this script can be run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.embeddings.embedding_service import (
    generate_embedding,
    generate_embeddings,
)
from services.ingestion.pdf_loader import (
    extract_text_from_pdf,
    split_text_into_chunks,
)
from services.retrieval.vector_store import (
    add_chunks,
    create_collection,
    search,
)

COLLECTION_NAME = "ekos_sample_document"
QUERY = "What skills does Aman have?"


def main() -> None:
    """Run the Sprint 2 PDF-to-vector-search workflow."""
    pdf_path = PROJECT_ROOT / "data" / "sample_documents" / "sample.pdf"

    print(f"Loading PDF: {pdf_path}")
    text = extract_text_from_pdf(str(pdf_path))
    chunks = split_text_into_chunks(text)

    if not chunks:
        print("No text chunks were created from the PDF.")
        return

    print(f"Generating embeddings for {len(chunks)} chunks...")
    embeddings = generate_embeddings(chunks)

    # MiniLM produces 384-dimensional vectors, but deriving the size keeps
    # this script correct if the embedding model changes later.
    vector_size = len(embeddings[0])
    create_collection(COLLECTION_NAME, vector_size)
    add_chunks(COLLECTION_NAME, chunks, embeddings)

    print(f'\nQuery: "{QUERY}"')
    query_embedding = generate_embedding(QUERY)
    results = search(COLLECTION_NAME, query_embedding, top_k=3)

    print("\nTop search results:")
    for rank, result in enumerate(results, start=1):
        payload = result.payload or {}
        chunk_text = str(payload.get("text", "[No chunk text]"))
        print(f"\n{rank}. Score: {result.score:.4f}")
        print(f"   Chunk index: {payload.get('chunk_index', 'unknown')}")
        print(f"   Text: {chunk_text}")


if __name__ == "__main__":
    main()

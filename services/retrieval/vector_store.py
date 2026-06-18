"""In-memory Qdrant vector storage for local EKOS development."""

from qdrant_client import QdrantClient, models

# The in-memory client keeps Sprint 2 simple and requires no Docker service.
qdrant_client = QdrantClient(location=":memory:")


def create_collection(collection_name: str, vector_size: int) -> None:
    """Create an empty collection configured for cosine similarity."""
    if not collection_name.strip():
        raise ValueError("collection_name cannot be empty")

    if vector_size <= 0:
        raise ValueError("vector_size must be greater than 0")

    # Recreate the collection so repeated local test runs start cleanly.
    if qdrant_client.collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name)

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )


def add_chunks(
    collection_name: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    """Store document chunks and their matching embeddings in Qdrant."""
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must contain the same number of items")

    if not chunks:
        return

    points = [
        models.PointStruct(
            id=index,
            vector=embedding,
            payload={"text": chunk, "chunk_index": index},
        )
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    qdrant_client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )


def search(
    collection_name: str,
    query_embedding: list[float],
    top_k: int = 3,
) -> list[models.ScoredPoint]:
    """Return the most similar chunks for a query embedding."""
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=top_k,
        with_payload=True,
    )

    return results.points

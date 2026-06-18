"""Generate text embeddings with a sentence-transformers model."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_embedding_model() -> SentenceTransformer:
    """Load and cache the embedding model so it is created only once."""
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """Generate one embedding vector for a text string."""
    model = load_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)

    # Qdrant accepts regular Python lists as vector values.
    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for multiple text strings in one batch."""
    if not texts:
        return []

    model = load_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)

    return embeddings.tolist()

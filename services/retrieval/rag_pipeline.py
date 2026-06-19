"""Retrieval-augmented answer generation for EKOS."""

from services.agents.gemini_client import generate_answer
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

COLLECTION_NAME = "ekos_documents"


def build_rag_prompt(
    query: str,
    retrieved_chunks: list[dict[str, object]],
) -> str:
    """Build a grounded prompt containing only retrieved document context."""
    context = "\n\n---\n\n".join(
        f"Source: {chunk['filename']}\n{chunk['text']}"
        for chunk in retrieved_chunks
    )

    return f"""You are an enterprise knowledge assistant.
Answer the question using only the context below.
If the answer is not present in the context, say:
"I could not find the answer in the provided context."
Do not add facts from outside knowledge.

Context:
{context}

Question:
{query}

Answer:"""


def answer_from_collection(
    query: str,
    collection_name: str = COLLECTION_NAME,
    top_k: int = 3,
) -> tuple[str, list[dict[str, object]]]:
    """Retrieve context from an existing collection and generate an answer."""
    query_embedding = generate_embedding(query)
    search_results = search(collection_name, query_embedding, top_k=top_k)
    retrieved_chunks = [
        {
            "filename": str(result.payload.get("filename", "unknown")),
            "chunk_index": int(result.payload.get("chunk_index", 0)),
            "text": str(result.payload.get("text", "")),
        }
        for result in search_results
        if result.payload and result.payload.get("text")
    ]

    if not retrieved_chunks:
        raise ValueError("No relevant context was retrieved from the documents")

    prompt = build_rag_prompt(query, retrieved_chunks)
    answer = generate_answer(prompt)

    return answer, retrieved_chunks


def run_rag_pipeline(
    pdf_path: str,
    query: str,
    top_k: int = 3,
) -> tuple[str, list[dict[str, object]]]:
    """Index one PDF, retrieve relevant chunks, and generate an answer."""
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text)

    if not chunks:
        raise ValueError("No text chunks could be created from the PDF")

    # Embed all chunks together because batch generation is more efficient.
    embeddings = generate_embeddings(chunks)
    create_collection(COLLECTION_NAME, vector_size=len(embeddings[0]))
    add_chunks(COLLECTION_NAME, chunks, embeddings)

    return answer_from_collection(query, COLLECTION_NAME, top_k)

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

COLLECTION_NAME = "ekos_rag_documents"


def build_rag_prompt(query: str, retrieved_chunks: list[str]) -> str:
    """Build a grounded prompt containing only retrieved document context."""
    context = "\n\n---\n\n".join(retrieved_chunks)

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


def run_rag_pipeline(
    pdf_path: str,
    query: str,
    top_k: int = 3,
) -> tuple[str, list[str]]:
    """Index one PDF, retrieve relevant chunks, and generate an answer."""
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text)

    if not chunks:
        raise ValueError("No text chunks could be created from the PDF")

    # Embed all chunks together because batch generation is more efficient.
    embeddings = generate_embeddings(chunks)
    create_collection(COLLECTION_NAME, vector_size=len(embeddings[0]))
    add_chunks(COLLECTION_NAME, chunks, embeddings)

    query_embedding = generate_embedding(query)
    search_results = search(COLLECTION_NAME, query_embedding, top_k=top_k)
    retrieved_chunks = [
        str(result.payload.get("text", ""))
        for result in search_results
        if result.payload and result.payload.get("text")
    ]

    if not retrieved_chunks:
        raise ValueError("No relevant context was retrieved from the PDF")

    prompt = build_rag_prompt(query, retrieved_chunks)
    answer = generate_answer(prompt)

    return answer, retrieved_chunks

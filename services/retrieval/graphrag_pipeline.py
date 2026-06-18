"""Combine vector retrieval and Neo4j context for grounded answers."""

from services.agents.gemini_client import generate_answer
from services.embeddings.embedding_service import generate_embedding
from services.retrieval.graph_retriever import (
    find_entity_by_name,
    get_graph_context,
)
from services.retrieval.vector_store import search

COLLECTION_NAME = "ekos_documents"


def identify_main_entity(question: str) -> str:
    """Ask Gemini for the main entity mentioned in a question."""
    prompt = f"""Identify the single main person, organization, project, or
other named entity in the question below.

Return only the entity name. Do not include explanation, labels, or punctuation.

Question:
{question}
"""
    return generate_answer(prompt).strip().strip("\"'")


def build_graphrag_prompt(
    question: str,
    vector_context: list[str],
    graph_context: str,
) -> str:
    """Build a prompt grounded in vector and graph retrieval results."""
    vector_text = "\n\n---\n\n".join(vector_context)
    graph_text = graph_context or "[No graph relationships were found]"

    return f"""You are an enterprise knowledge assistant.
Answer the question using only the vector context and graph context below.
Do not use outside knowledge or infer facts that are not present.
If the provided context does not contain the answer, say:
"I could not find the answer in the provided context."

Vector context:
{vector_text}

Graph context:
{graph_text}

Question:
{question}

Answer:"""


def run_graphrag_pipeline(
    question: str,
    collection_name: str = COLLECTION_NAME,
    top_k: int = 3,
) -> tuple[str, list[str], str]:
    """Retrieve vector and graph context, then generate a grounded answer."""
    query_embedding = generate_embedding(question)
    vector_results = search(collection_name, query_embedding, top_k=top_k)
    vector_context = [
        str(result.payload.get("text", ""))
        for result in vector_results
        if result.payload and result.payload.get("text")
    ]

    if not vector_context:
        raise ValueError("No vector context was retrieved")

    extracted_entity = identify_main_entity(question)
    matched_entity = find_entity_by_name(extracted_entity)
    graph_context = (
        get_graph_context(str(matched_entity["name"]))
        if matched_entity
        else ""
    )

    prompt = build_graphrag_prompt(
        question=question,
        vector_context=vector_context,
        graph_context=graph_context,
    )
    answer = generate_answer(prompt)

    return answer, vector_context, graph_context

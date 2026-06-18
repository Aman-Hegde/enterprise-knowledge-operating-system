"""Response schema for the EKOS GraphRAG endpoint."""

from pydantic import BaseModel


class GraphRAGAnswerResponse(BaseModel):
    """Answer returned with both vector and graph retrieval context."""

    question: str
    answer: str
    vector_context: list[str]
    graph_context: str

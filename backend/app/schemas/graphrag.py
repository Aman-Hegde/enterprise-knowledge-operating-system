"""Response schema for the EKOS GraphRAG endpoint."""

from pydantic import BaseModel

from backend.app.schemas.rag import RetrievedChunk


class GraphRAGAnswerResponse(BaseModel):
    """Answer returned with both vector and graph retrieval context."""

    question: str
    answer: str
    vector_context: list[RetrievedChunk]
    graph_context: str

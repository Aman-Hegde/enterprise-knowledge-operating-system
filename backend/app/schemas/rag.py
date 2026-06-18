"""Request and response schemas for EKOS RAG endpoints."""

from pydantic import BaseModel, Field


class RAGQuestionRequest(BaseModel):
    """Question submitted to the RAG pipeline."""

    question: str = Field(min_length=1)


class RAGAnswerResponse(BaseModel):
    """Grounded answer and the context used to create it."""

    question: str
    answer: str
    retrieved_context: list[str]

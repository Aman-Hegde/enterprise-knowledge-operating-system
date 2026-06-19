"""Response schemas for EKOS document endpoints."""

from pydantic import BaseModel


class DocumentInfo(BaseModel):
    """Metadata for one document in the in-memory knowledge base."""

    filename: str
    chunk_count: int
    status: str


class DocumentUploadResponse(BaseModel):
    """Summary returned after one or more PDFs are indexed."""

    total_documents: int
    total_chunks: int
    uploaded_filenames: list[str]
    graph_extraction_status: dict[str, str]
    warnings: list[str]
    message: str

"""Response schemas for EKOS document endpoints."""

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Summary returned after a PDF is indexed."""

    filename: str
    total_characters: int
    total_chunks: int
    message: str

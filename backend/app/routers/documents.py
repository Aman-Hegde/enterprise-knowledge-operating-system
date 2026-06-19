"""Document explorer endpoints for the in-memory EKOS knowledge base."""

from collections import Counter

from fastapi import APIRouter, Request

from backend.app.schemas.documents import DocumentInfo

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentInfo])
async def list_documents(request: Request) -> list[DocumentInfo]:
    """Return all documents currently indexed in this backend session."""
    indexed_documents: list[str] = request.app.state.indexed_documents
    indexed_chunks: list[dict[str, object]] = request.app.state.indexed_chunks

    chunk_counts = Counter(
        str(chunk.get("filename", ""))
        for chunk in indexed_chunks
        if chunk.get("filename")
    )

    # Preserve upload order while returning each filename only once.
    unique_filenames = list(dict.fromkeys(indexed_documents))

    return [
        DocumentInfo(
            filename=filename,
            chunk_count=chunk_counts.get(filename, 0),
            status="indexed",
        )
        for filename in unique_filenames
    ]

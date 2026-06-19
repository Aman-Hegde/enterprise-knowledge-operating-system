from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.app.schemas.documents import DocumentUploadResponse
from backend.app.schemas.graphrag import GraphRAGAnswerResponse
from backend.app.schemas.rag import RAGAnswerResponse, RAGQuestionRequest
from services.embeddings.embedding_service import generate_embeddings
from services.ingestion.pdf_loader import (
    extract_text_from_pdf,
    split_text_into_chunks,
)
from services.retrieval.graphrag_pipeline import run_graphrag_pipeline
from services.retrieval.rag_pipeline import answer_from_collection
from services.retrieval.vector_store import add_chunks, create_collection

app = FastAPI(
    title="Enterprise Knowledge Operating System",
    description="API service for the EKOS knowledge platform.",
    version="0.1.0",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
COLLECTION_NAME = "ekos_documents"

# The FastAPI process owns the current in-memory document index.
indexed_chunks: list[str] = []
indexed_embeddings: list[list[float]] = []
is_document_indexed = False
latest_filename: str | None = None


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return a simple service health response."""
    return {"status": "ok", "message": "EKOS backend is running"}


@app.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    tags=["Documents"],
)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """Save, extract, embed, and index one uploaded PDF document."""
    global indexed_chunks
    global indexed_embeddings
    global is_document_indexed
    global latest_filename

    original_filename = file.filename or ""
    safe_filename = Path(original_filename).name

    if not safe_filename or Path(safe_filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    saved_path = RAW_DATA_DIRECTORY / safe_filename

    try:
        # Stream the upload to disk instead of reading the whole PDF into memory.
        with saved_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

        text = extract_text_from_pdf(str(saved_path))
        chunks = split_text_into_chunks(text)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No extractable text was found in the PDF",
            )

        embeddings = generate_embeddings(chunks)

        # Sprint 4 keeps one collection and replaces its contents per upload.
        create_collection(COLLECTION_NAME, vector_size=len(embeddings[0]))
        add_chunks(COLLECTION_NAME, chunks, embeddings)

        # Update shared state only after the complete indexing operation succeeds.
        indexed_chunks = chunks.copy()
        indexed_embeddings = [embedding.copy() for embedding in embeddings]
        is_document_indexed = True
        latest_filename = safe_filename
        print(f"[EKOS] Chunks indexed after upload: {len(indexed_chunks)}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process the PDF: {exc}",
        ) from exc
    finally:
        await file.close()

    return DocumentUploadResponse(
        filename=safe_filename,
        total_characters=len(text),
        total_chunks=len(chunks),
        message="PDF uploaded and indexed successfully",
    )


@app.post("/rag/ask", response_model=RAGAnswerResponse, tags=["RAG"])
async def ask_question(request: RAGQuestionRequest) -> RAGAnswerResponse:
    """Answer a question using chunks from the most recently uploaded PDF."""
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be empty")

    try:
        answer, retrieved_chunks = answer_from_collection(
            query=question,
            collection_name=COLLECTION_NAME,
            top_k=3,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Upload and index a PDF before asking a question",
        ) from exc

    return RAGAnswerResponse(
        question=question,
        answer=answer,
        retrieved_context=retrieved_chunks,
    )


@app.post(
    "/graphrag/ask",
    response_model=GraphRAGAnswerResponse,
    tags=["GraphRAG"],
)
async def ask_graphrag_question(
    request: RAGQuestionRequest,
) -> GraphRAGAnswerResponse:
    """Answer a question using both vector and Neo4j graph context."""
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be empty")

    if not is_document_indexed:
        raise HTTPException(
            status_code=400,
            detail="Upload and index a PDF before asking a GraphRAG question",
        )

    print(f"[EKOS] Chunks available before GraphRAG query: {len(indexed_chunks)}")

    try:
        answer, vector_context, graph_context = run_graphrag_pipeline(
            question=question,
            chunks=indexed_chunks,
            embeddings=indexed_embeddings,
            collection_name=COLLECTION_NAME,
            top_k=3,
        )
    except Exception as error:
        print(f"[EKOS][GraphRAG ERROR] {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=400,
            detail=(
                f"GraphRAG query failed: {type(error).__name__}: {error}"
            ),
        ) from error

    return GraphRAGAnswerResponse(
        question=question,
        answer=answer,
        vector_context=vector_context,
        graph_context=graph_context,
    )

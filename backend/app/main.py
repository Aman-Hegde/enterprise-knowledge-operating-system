from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas.documents import DocumentUploadResponse
from backend.app.schemas.graphrag import GraphRAGAnswerResponse
from backend.app.schemas.rag import RAGAnswerResponse, RAGQuestionRequest
from backend.app.routers.documents import router as documents_router
from services.embeddings.embedding_service import generate_embeddings
from services.graph_builder.entity_extractor import extract_entities_and_relationships
from services.graph_builder.graph_service import build_graph, get_graph_network
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

# The frontend fetches graph data directly from FastAPI during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
COLLECTION_NAME = "ekos_documents"

# The FastAPI process owns the current in-memory document index.
indexed_chunks: list[dict[str, object]] = []
indexed_embeddings: list[list[float]] = []
indexed_documents: list[str] = []
is_document_indexed = False

# Routers read the same lists that the upload endpoint updates in this process.
app.state.indexed_chunks = indexed_chunks
app.state.indexed_documents = indexed_documents
app.include_router(documents_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return a simple service health response."""
    return {"status": "ok", "message": "EKOS backend is running"}


@app.get("/graph/network", tags=["Graph"])
async def graph_network() -> dict[str, list[dict[str, str]]]:
    """Return the live Neo4j relationship network for visualization."""
    try:
        return get_graph_network()
    except Exception as error:
        print(f"[EKOS][GRAPH NETWORK ERROR] {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=503,
            detail="Unable to load graph data from Neo4j",
        ) from error


@app.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    tags=["Documents"],
)
async def upload_document(
    files: list[UploadFile] | None = File(default=None),
    file: UploadFile | None = File(default=None),
) -> DocumentUploadResponse:
    """Save, extract, embed, and index one or more PDF documents."""
    global indexed_chunks
    global indexed_embeddings
    global indexed_documents
    global is_document_indexed

    # `file` keeps older clients working while new clients send repeated `files`.
    uploaded_files = list(files or [])
    if file is not None:
        uploaded_files.append(file)

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="Upload at least one PDF file")

    RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    batch_chunks: list[dict[str, object]] = []
    batch_texts: list[str] = []
    uploaded_filenames: list[str] = []
    graph_extraction_status: dict[str, str] = {}
    warnings: list[str] = []

    try:
        for uploaded_file in uploaded_files:
            safe_filename = Path(uploaded_file.filename or "").name

            if (
                not safe_filename
                or Path(safe_filename).suffix.lower() != ".pdf"
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are supported",
                )

            saved_path = RAW_DATA_DIRECTORY / safe_filename

            # Stream each upload to disk instead of loading entire PDFs in memory.
            with saved_path.open("wb") as destination:
                shutil.copyfileobj(uploaded_file.file, destination)

            text = extract_text_from_pdf(str(saved_path))
            text_chunks = split_text_into_chunks(text)

            if not text_chunks:
                raise HTTPException(
                    status_code=400,
                    detail=f"No extractable text was found in {safe_filename}",
                )

            for chunk_index, chunk_text in enumerate(text_chunks):
                batch_chunks.append(
                    {
                        "filename": safe_filename,
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                    }
                )

            batch_texts.extend(text_chunks)
            uploaded_filenames.append(safe_filename)

            # Graph extraction is best-effort. Vector indexing must continue when
            # Gemini is rate-limited or the optional graph step is unavailable.
            try:
                graph_data = extract_entities_and_relationships(text)
                build_graph(graph_data)
                graph_extraction_status[safe_filename] = "completed"
            except Exception as graph_error:
                warning = (
                    f"Graph extraction skipped for {safe_filename} "
                    "due to LLM/quota error"
                )

                graph_extraction_status[safe_filename] = "skipped"
                warnings.append(warning)

                print(
                    "[EKOS][GRAPH EXTRACTION WARNING] "
                    f"{safe_filename}: {type(graph_error).__name__}: {graph_error}"
                )

        batch_embeddings = generate_embeddings(batch_texts)

        combined_chunks = indexed_chunks + batch_chunks
        combined_embeddings = indexed_embeddings + batch_embeddings
        combined_documents = indexed_documents + uploaded_filenames

        # Rebuild one Qdrant collection containing every document in the session.
        create_collection(
            COLLECTION_NAME,
            vector_size=len(combined_embeddings[0]),
        )
        add_chunks(COLLECTION_NAME, combined_chunks, combined_embeddings)

        # Update shared state only after the complete indexing operation succeeds.
        indexed_chunks = [chunk.copy() for chunk in combined_chunks]
        indexed_embeddings = [
            embedding.copy() for embedding in combined_embeddings
        ]
        indexed_documents = combined_documents.copy()
        is_document_indexed = True

        # Refresh app.state because the shared lists above were reassigned.
        app.state.indexed_chunks = indexed_chunks
        app.state.indexed_documents = indexed_documents
        print(f"[EKOS] Chunks indexed after upload: {len(indexed_chunks)}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process the PDF: {exc}",
        ) from exc
    finally:
        for uploaded_file in uploaded_files:
            await uploaded_file.close()

    return DocumentUploadResponse(
        total_documents=len(indexed_documents),
        total_chunks=len(indexed_chunks),
        uploaded_filenames=uploaded_filenames,
        graph_extraction_status=graph_extraction_status,
        warnings=warnings,
        message="PDF documents uploaded and indexed successfully",
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

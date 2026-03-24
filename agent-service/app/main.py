from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.ai.agent import chat_with_ai, get_rag_retriever
from app.ai.rag.document_processor import DocumentProcessor
from app.core.chat_history import clear_conversation
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "OK"}

@app.on_event("startup")
def bootstrap_rag_index() -> None:
    """Build/refresh the RAG index on server startup and log indexed docs."""
    major_sep = "=" * 72
    minor_sep = "-" * 72

    if not settings.RAG_ENABLED:
        print(major_sep)
        print("[RAG] Startup bootstrap skipped because RAG_ENABLED=false")
        print(major_sep)
        return

    data_dir = Path(settings.RAG_DATA_DIR)
    print(major_sep)
    print("[RAG] STARTUP BOOTSTRAP")
    print(minor_sep)
    print(f"[RAG] Startup bootstrap started. data_dir={data_dir}")

    if not data_dir.exists():
        raise RuntimeError(f"RAG data directory not found: {data_dir}")

    rag = get_rag_retriever()
    if rag is None:
        raise RuntimeError("RAG retriever failed to initialize")

    processor = DocumentProcessor(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
    )

    print(minor_sep)
    print("[RAG] PHASE: DOCUMENT SCAN")
    print("[RAG] Scanning documents for indexing...")
    try:
        chunks = processor.process_directory(str(data_dir))
    except Exception as exc:
        print(f"[RAG] Document scan/index preparation failed: {exc}")
        raise RuntimeError("RAG document scan/index preparation failed") from exc

    if not chunks:
        raise RuntimeError(f"No documents found for indexing in {data_dir}")

    print(minor_sep)
    print("[RAG] PHASE: INDEX REFRESH")
    print(f"[RAG] Refreshing RAG store and indexing {len(chunks)} chunks...")
    try:
        rag.clear()
        rag.add_documents(chunks)
    except Exception as exc:
        print(f"[RAG] Indexing failed while writing to vector store: {exc}")
        raise RuntimeError("RAG indexing failed while writing to vector store") from exc
    print("[RAG] Indexing complete.")

    docs = rag.list_documents()
    if not docs:
        print(minor_sep)
        print("[RAG] Indexed documents: none")
        print(major_sep)
        return

    print(minor_sep)
    print("[RAG] PHASE: INDEXED DOCUMENT SUMMARY")
    print(f"[RAG] Indexed documents summary ({len(docs)} sources):")
    for row in docs:
        print(f"[RAG] - {row.get('source_file', 'unknown')} (chunks={row.get('chunks', 0)})")
    print(major_sep)
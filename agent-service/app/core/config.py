import os
from pathlib import Path
from dotenv import load_dotenv


AGENT_SERVICE_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(AGENT_SERVICE_ROOT / ".env")


def normalize_openai_base_url(api_url: str) -> str:
	normalized = (api_url or "").strip().rstrip("/")
	suffix = "/chat/completions"
	if normalized.endswith(suffix):
		return normalized[: -len(suffix)]
	return normalized


class Settings:
	DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()

	NVIDIA_OPENAI_API_KEY = os.getenv("NVIDIA_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
	NVIDIA_OPENAI_API_URL = os.getenv(
		"NVIDIA_OPENAI_API_URL",
		"https://integrate.api.nvidia.com/v1/chat/completions",
	)
	NVIDIA_OPENAI_BASE_URL = normalize_openai_base_url(NVIDIA_OPENAI_API_URL)
	NVIDIA_OPENAI_MODEL = os.getenv("NVIDIA_OPENAI_MODEL", "openai/gpt-oss-20b")
	
	# RAG Configuration
	RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
	RAG_EMBEDDING_PROVIDER = os.getenv("RAG_EMBEDDING_PROVIDER", "mock")  # mock, openai, ollama
	RAG_VECTOR_STORE = os.getenv("RAG_VECTOR_STORE", "memory")  # memory, pinecone, milvus
	RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500")) 
	RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))  # tokens
	RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))  # Number of documents to retrieve
	RAG_DATA_DIR = AGENT_SERVICE_ROOT / "data" / "documents"
	RAG_STORE_PATH = Path(
		os.getenv("RAG_STORE_PATH", str(AGENT_SERVICE_ROOT / "data" / "rag_store.json"))
	)


settings = Settings()


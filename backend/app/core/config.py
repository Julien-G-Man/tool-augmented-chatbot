import os
from pathlib import Path
from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")


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


settings = Settings()


"""
All settings in one place.

Every value is read from environment variables (or backend/.env).
Nothing secret or environment-specific is written in the code.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# backend/ folder
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Avoid a harmless but noisy crash message from the tokenizer threads when Python exits
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "unisarthi.db"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", DATA_DIR / "chroma"))

# ---------- LLM ----------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()  # groq | ollama | mock
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

# ---------- Retrieval ----------
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
TOP_K = int(os.getenv("TOP_K", "5"))
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.60"))

# ---------- Authentication ----------
SECRET_KEY = os.getenv("SECRET_KEY", "")
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "8"))
AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "false").lower() == "true"

# ---------- Frontend ----------
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

# The exact sentence the guide requires when we cannot answer (R3)
NOT_FOUND_MESSAGE = "I could not find this information in the authorised university sources."


def active_model_name() -> str:
    """Name of the LLM in use, for the audit record."""
    if LLM_PROVIDER == "groq":
        return f"groq:{GROQ_MODEL}"
    if LLM_PROVIDER == "ollama":
        return f"ollama:{OLLAMA_MODEL}"
    return "mock"

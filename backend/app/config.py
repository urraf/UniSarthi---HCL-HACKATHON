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
# Used in order when a model hits its daily token limit (each Groq model has its own quota)
GROQ_FALLBACK_MODELS = [m.strip() for m in os.getenv("GROQ_FALLBACK_MODELS", "").split(",") if m.strip()]
# true -> if every Groq model is over its limit (or Groq is unreachable), use the local Ollama model
FALLBACK_TO_OLLAMA = os.getenv("FALLBACK_TO_OLLAMA", "false").lower() == "true"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

# ---------- Retrieval ----------
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
# How embeddings are computed: "sentence-transformers" (PyTorch) or "onnx" (the same all-MiniLM-L6-v2 model
# bundled with ChromaDB; no PyTorch, much less memory - used on Render's free tier)
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "sentence-transformers")
TOP_K = int(os.getenv("TOP_K", "5"))
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.50"))

# ---------- Authentication ----------
SECRET_KEY = os.getenv("SECRET_KEY", "")
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "8"))
AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "false").lower() == "true"

# ---------- MongoDB: accounts, OTPs, chat history ----------
MONGODB_URI = os.getenv("MONGODB_URI", "")          # e.g. mongodb+srv://user:pass@cluster/  (tests: mongomock://)
MONGODB_DB = os.getenv("MONGODB_DB", "unisarthi")

# First staff account, created at startup if both are set (then manage staff with scripts/create_admin.py)
BOOTSTRAP_ADMIN_ID = os.getenv("BOOTSTRAP_ADMIN_ID", "")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")

# ---------- Email (OTP) ----------
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))      # 587 = STARTTLS, 465 = SSL
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "nsut.ac.in")
OTP_MINUTES = int(os.getenv("OTP_MINUTES", "10"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
# Development only: if SMTP is not configured, print the OTP in the server log instead of failing
DEV_PRINT_OTP = os.getenv("DEV_PRINT_OTP", "false").lower() == "true"
# true -> POST /ingest needs a staff (admin) token. false keeps the guide's open contract for judges.
INGEST_REQUIRES_ADMIN = os.getenv("INGEST_REQUIRES_ADMIN", "false").lower() == "true"

# ---------- Frontend ----------
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
# Optional pattern of allowed frontend addresses, e.g. https://.*\.onrender\.com on Render
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX") or None

# The exact sentence the guide requires when we cannot answer (R3)
NOT_FOUND_MESSAGE = "I could not find this information in the authorised university sources."


def active_model_name() -> str:
    """Name of the LLM in use, for the audit record."""
    if LLM_PROVIDER == "groq":
        return f"groq:{GROQ_MODEL}"
    if LLM_PROVIDER == "ollama":
        return f"ollama:{OLLAMA_MODEL}"
    return "mock"

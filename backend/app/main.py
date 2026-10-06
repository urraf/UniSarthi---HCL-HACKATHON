"""
FastAPI app: the endpoints from section 6 of the guide, plus login.

  POST /ask               ask a question (header X-Student-Id; optional login token)
  POST /ingest            add a document while running (file + metadata JSON)
  GET  /health            status of API, vector store, SQLite and LLM
  GET  /audit/{trace_id}  audit record of one answer
  GET  /sources           Source Register: all ingested documents
  GET  /me                the logged-in student's profile and courses
  + account endpoints in account_routes.py (sign up, login, forgot password / roll number, staff login, history)

Run:  uvicorn app.main:app --reload --port 8000     (from the backend/ folder)
Docs: http://localhost:8000/docs
"""
import json
import os

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app import auth, config, db, vectors
from app.account_routes import current, router as account_router, save_exchange
from app.ingest import DocumentMeta, ingest_document
from app.llm import LLMError, chat_json
from app.mongo import get_db
from app.pipeline.graph import run
from app.pipeline.understand import student_courses
from app.schemas import AskRequest, AskResponse, IngestResponse

app = FastAPI(title="UniSarthi - Student Services Assistant", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_origin_regex=config.CORS_ORIGIN_REGEX,
                   allow_methods=["*"], allow_headers=["*"])
db.init_db()
app.include_router(account_router)


@app.on_event("startup")
def create_startup_accounts():
    """First staff account from .env, and (CREATE_DEMO_ACCOUNTS=true) demo student accounts without email."""
    # MongoDB down must not stop the API: questions and documents do not need it, only accounts and chats do
    try:
        if config.BOOTSTRAP_ADMIN_ID and config.BOOTSTRAP_ADMIN_PASSWORD:
            auth.create_admin(config.BOOTSTRAP_ADMIN_ID, config.BOOTSTRAP_ADMIN_PASSWORD)
        if os.getenv("CREATE_DEMO_ACCOUNTS", "false").lower() == "true" and os.getenv("DEFAULT_STUDENT_PASSWORD"):
            from scripts.create_logins import create_demo_accounts
            create_demo_accounts(os.getenv("DEFAULT_STUDENT_PASSWORD"))
    except Exception as e:  # noqa: BLE001 - log any connection problem and keep running
        print(f"WARNING: MongoDB not reachable at startup, accounts/chats unavailable until it is: {e}", flush=True)


# ---------- Identity ----------
def identify(x_student_id: str | None, authorization: str | None) -> tuple[str | None, bool]:
    """
    Who is asking? Identity comes only from request headers, never from the question text (R7).
      - X-Student-Id header: the guide's contract (judges' tests use it).
      - Authorization: Bearer <token> from /login (the React app sends both).
    If a token is sent it must be a valid student token for the same student as X-Student-Id.
    With AUTH_REQUIRED=true, a token is mandatory whenever a student ID is used.
    Returns (student_id, logged_in).
    """
    token_student = None
    if authorization:
        token_student = current(authorization, "student")
    if token_student and x_student_id and token_student != x_student_id.upper():
        raise HTTPException(status_code=403, detail="Login token does not match X-Student-Id")
    student_id = (x_student_id or token_student or "").upper() or None
    if config.AUTH_REQUIRED and student_id and not token_student:
        raise HTTPException(status_code=401, detail="Please log in: a valid token is required")
    return student_id, token_student is not None


# ---------- Endpoints ----------
@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, x_student_id: str | None = Header(default=None),
        authorization: str | None = Header(default=None)):
    student_id, logged_in = identify(x_student_id, authorization)
    response = run(body.question, student_id, body.as_of_date)
    if logged_in:  # keep the chat of logged-in students (MongoDB)
        try:
            response["conversation_id"] = save_exchange(student_id, body.conversation_id, body.question, response)
        except Exception as e:  # noqa: BLE001 - the answer still goes out if the chat cannot be saved
            print(f"WARNING: chat not saved (MongoDB): {e}", flush=True)
    return response


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...), metadata: str = Form(..., description="JSON with Source Register fields"),
                 authorization: str | None = Header(default=None)):
    # University staff add documents. With INGEST_REQUIRES_ADMIN=false (default) the guide's open contract is kept.
    if config.INGEST_REQUIRES_ADMIN or authorization:
        current(authorization, "admin")
    try:
        meta = DocumentMeta(**json.loads(metadata))
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid metadata: {e}")
    try:
        return ingest_document(meta, file.filename, await file.read())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health():
    status = {"api": "ok"}
    try:
        status["sqlite"] = f"ok ({db.query_one('SELECT COUNT(*) AS n FROM students')['n']} students)"
    except Exception as e:  # noqa: BLE001 - report any failure
        status["sqlite"] = f"error: {e}"
    try:
        status["vector_store"] = f"ok ({vectors.collection().count()} chunks)"
    except Exception as e:  # noqa: BLE001
        status["vector_store"] = f"error: {e}"
    try:
        get_db().command("ping")
        status["mongodb"] = "ok"
    except Exception as e:  # noqa: BLE001
        status["mongodb"] = f"error: {str(e)[:200]}"
    try:
        chat_json("Reply with JSON only.", 'Return {"ok": true}')
        status["llm"] = f"ok ({config.active_model_name()})"
    except LLMError as e:
        status["llm"] = f"unavailable: {e}"
    return status


@app.get("/audit/{trace_id}")
def audit(trace_id: str):
    row = db.query_one("SELECT record_json FROM audit_log WHERE trace_id = ?", (trace_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Unknown trace_id")
    return json.loads(row["record_json"])


@app.get("/sources")
def sources():
    return db.query("SELECT * FROM documents ORDER BY authority_level, effective_from")


@app.get("/me")
def me(authorization: str | None = Header(default=None)):
    student_id = current(authorization, "student")
    profile = db.query_one("SELECT student_id, roll_number, full_name, programme, batch_year, current_semester FROM students "
                           "WHERE student_id = ?", (student_id,))
    # The student's courses (used by the app to suggest personal questions)
    profile["courses"] = student_courses(student_id)
    profile["attendance_courses"] = student_courses(student_id, "attendance")
    profile["result_courses"] = student_courses(student_id, "results")
    return profile

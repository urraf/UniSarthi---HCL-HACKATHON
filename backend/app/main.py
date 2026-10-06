"""
FastAPI app: the endpoints from section 6 of the guide, plus login.

  POST /ask               ask a question (header X-Student-Id; optional login token)
  POST /ingest            add a document while running (file + metadata JSON)
  GET  /health            status of API, vector store, SQLite and LLM
  GET  /audit/{trace_id}  audit record of one answer
  GET  /sources           Source Register: all ingested documents
  POST /login             student ID + password -> token (used by the React app)
  GET  /me                the logged-in student's profile and courses

Run:  uvicorn app.main:app --reload --port 8000     (from the backend/ folder)
Docs: http://localhost:8000/docs
"""
import json

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app import auth, config, db, vectors
from app.ingest import DocumentMeta, ingest_document
from app.llm import LLMError, chat_json
from app.pipeline.graph import run
from app.pipeline.understand import student_courses
from app.schemas import AskRequest, AskResponse, IngestResponse, LoginRequest, LoginResponse

app = FastAPI(title="UniSarthi - Student Services Assistant", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
db.init_db()


# ---------- Identity ----------
def identify(x_student_id: str | None, authorization: str | None) -> str | None:
    """
    Who is asking? Identity comes only from request headers, never from the question text (R7).
      - X-Student-Id header: the guide's contract (judges' tests use it).
      - Authorization: Bearer <token> from /login (the React app sends both).
    If a token is sent it must be valid and belong to the same student as X-Student-Id.
    With AUTH_REQUIRED=true, a token is mandatory whenever a student ID is used.
    """
    token_student = None
    if authorization:
        try:
            token_student = auth.verify_token(authorization.removeprefix("Bearer ").strip())
        except auth.AuthError as e:
            raise HTTPException(status_code=401, detail=str(e))
    if token_student and x_student_id and token_student != x_student_id.upper():
        raise HTTPException(status_code=403, detail="Login token does not match X-Student-Id")
    student_id = (x_student_id or token_student or "").upper() or None
    if config.AUTH_REQUIRED and student_id and not token_student:
        raise HTTPException(status_code=401, detail="Please log in: a valid token is required")
    return student_id


# ---------- Endpoints ----------
@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, x_student_id: str | None = Header(default=None),
        authorization: str | None = Header(default=None)):
    student_id = identify(x_student_id, authorization)
    return run(body.question, student_id, body.as_of_date)


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...), metadata: str = Form(..., description="JSON with Source Register fields")):
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


@app.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    try:
        token = auth.login(body.student_id.upper(), body.password)
    except auth.AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    student = db.query_one("SELECT * FROM students WHERE student_id = ?", (body.student_id.upper(),))
    return {"token": token, **{k: student[k] for k in ("student_id", "full_name", "programme", "batch_year")}}


@app.get("/me")
def me(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Please log in")
    student_id = identify(None, authorization)
    profile = db.query_one("SELECT student_id, full_name, programme, batch_year, current_semester FROM students "
                           "WHERE student_id = ?", (student_id,))
    # The student's courses (used by the app to suggest personal questions)
    profile["courses"] = student_courses(student_id)
    return profile

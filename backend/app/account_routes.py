"""
Account endpoints: sign up with email OTP, login, forgot password, forgot roll number,
staff login, and chat history. Data lives in MongoDB (see mongo.py).

  POST /auth/signup/start      {roll_number, email}             -> emails an OTP
  POST /auth/signup/verify     {email, otp, password}           -> creates the account
  POST /login                  {roll_number, password}          -> student token
  POST /auth/forgot-password   {email}                          -> emails an OTP
  POST /auth/reset-password    {email, otp, new_password}
  POST /auth/forgot-roll       {email}                          -> emails the roll number
  POST /admin/login            {admin_id, password}             -> staff token
  GET  /auth/session                                            -> is my login still valid?
  GET  /conversations, GET/DELETE /conversations/{id}          -> the student's saved chats
  GET  /admin/tables/{students|attendance|results|courses|rules} -> staff: read-only table view
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app import auth, config, db
from app.mailer import MailError, send_email
from app.mongo import get_db

router = APIRouter()
# Same reply whether or not the email has an account, so nobody can probe which emails exist
GENERIC_SENT = {"message": "If this email has an account, we have sent it a message."}


class SignupStart(BaseModel):
    roll_number: str
    email: str


class SignupVerify(BaseModel):
    email: str
    otp: str
    password: str


class Login(BaseModel):
    roll_number: str
    password: str


class EmailOnly(BaseModel):
    email: str


class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str


class AdminLogin(BaseModel):
    admin_id: str
    password: str


def _fail(e: Exception, status: int = 400):
    raise HTTPException(status_code=status, detail=str(e))


def _send_otp(email: str, code: str, action: str) -> None:
    send_email(email, f"UniSarthi: your code to {action}",
               f"Your one-time code is {code}.\nIt expires in {config.OTP_MINUTES} minutes. "
               "If you did not ask for it, ignore this email.")


def current(authorization: str | None, role: str) -> str:
    """Subject of a valid token with the right role (student_id or admin_id)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Please log in")
    try:
        token_role, subject = auth.verify_token(authorization.removeprefix("Bearer ").strip())
    except auth.AuthError as e:
        _fail(e, 401)
    if token_role != role:
        raise HTTPException(status_code=403, detail="Not allowed for this account")
    return subject


# ---------- Sign up ----------
@router.post("/auth/signup/start")
def signup_start(body: SignupStart):
    try:
        roll, email = auth.normalise_roll(body.roll_number), auth.normalise_email(body.email)
        student = auth.student_by_roll(roll)
        if get_db().users.find_one({"$or": [{"student_id": student["student_id"]}, {"email": email}]}):
            raise auth.AuthError("An account already exists for this roll number or email. Try logging in.")
        _send_otp(email, auth.create_otp(email, "signup", student["student_id"]), "create your account")
    except (auth.AuthError, MailError) as e:
        _fail(e)
    return {"message": f"We sent a code to {email}."}


@router.post("/auth/signup/verify")
def signup_verify(body: SignupVerify):
    try:
        email = auth.normalise_email(body.email)
        otp = auth.check_otp(email, "signup", body.otp)
        student = db.query_one("SELECT * FROM students WHERE student_id = ?", (otp["student_id"],))
        auth.create_student_account(student["student_id"], student["roll_number"], email, body.password)
    except auth.AuthError as e:
        _fail(e)
    return {"message": "Account created. You can log in now."}


# ---------- Login ----------
@router.post("/login")
def login(body: Login):
    try:
        token, s = auth.student_login(body.roll_number, body.password)
    except auth.AuthError as e:
        _fail(e, 401)
    return {"token": token, "role": "student", "student_id": s["student_id"], "roll_number": s["roll_number"],
            "full_name": s["full_name"], "programme": s["programme"], "batch_year": s["batch_year"]}


@router.post("/admin/login")
def admin_login(body: AdminLogin):
    try:
        token = auth.admin_login(body.admin_id.strip(), body.password)
    except auth.AuthError as e:
        _fail(e, 401)
    return {"token": token, "role": "admin", "admin_id": body.admin_id.strip()}


# ---------- Forgot password / roll number ----------
@router.post("/auth/forgot-password")
def forgot_password(body: EmailOnly):
    try:
        email = auth.normalise_email(body.email)
        if get_db().users.find_one({"email": email}):
            _send_otp(email, auth.create_otp(email, "reset"), "reset your password")
    except (auth.AuthError, MailError) as e:
        _fail(e)
    return GENERIC_SENT


@router.post("/auth/reset-password")
def reset_password(body: ResetPassword):
    try:
        email = auth.normalise_email(body.email)
        auth.check_otp(email, "reset", body.otp)
        auth.set_password(email, body.new_password)
    except auth.AuthError as e:
        _fail(e)
    return {"message": "Password changed. You can log in now."}


@router.post("/auth/forgot-roll")
def forgot_roll(body: EmailOnly):
    try:
        email = auth.normalise_email(body.email)
        user = get_db().users.find_one({"email": email})
        if user:
            send_email(email, "UniSarthi: your roll number",
                       f"Your roll number is {user['roll_number']}. Use it to log in to UniSarthi.")
    except (auth.AuthError, MailError) as e:
        _fail(e)
    return GENERIC_SENT


# ---------- Session check (keeps the user logged in after a page refresh) ----------
@router.get("/auth/session")
def session(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Please log in")
    try:
        role, subject = auth.verify_token(authorization.removeprefix("Bearer ").strip())
    except auth.AuthError as e:
        _fail(e, 401)
    return {"role": role, "subject": subject}


# ---------- Conversations (chat history) ----------
def new_conversation(student_id: str, title: str) -> str:
    conversation_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    get_db().conversations.insert_one({"conversation_id": conversation_id, "student_id": student_id,
                                       "title": title[:60], "created_at": now, "updated_at": now})
    return conversation_id


def save_exchange(student_id: str, conversation_id: str | None, question: str, response: dict) -> str:
    """Store the question and the answer; start a new conversation if needed. Returns its id."""
    db_ = get_db()
    if not conversation_id or not db_.conversations.find_one({"conversation_id": conversation_id, "student_id": student_id}):
        conversation_id = new_conversation(student_id, question)
    now = datetime.now(timezone.utc)
    db_.messages.insert_many([
        {"conversation_id": conversation_id, "student_id": student_id, "role": "user", "text": question, "created_at": now},
        {"conversation_id": conversation_id, "student_id": student_id, "role": "assistant", "text": response["answer"],
         "response": response, "created_at": now},
    ])
    db_.conversations.update_one({"conversation_id": conversation_id}, {"$set": {"updated_at": now}})
    return conversation_id


@router.get("/conversations")
def list_conversations(authorization: str | None = Header(default=None)):
    student_id = current(authorization, "student")
    return list(get_db().conversations.find({"student_id": student_id}, {"_id": 0, "student_id": 0})
                .sort("updated_at", -1).limit(50))


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, authorization: str | None = Header(default=None)):
    student_id = current(authorization, "student")
    return list(get_db().messages.find({"conversation_id": conversation_id, "student_id": student_id},
                                       {"_id": 0, "student_id": 0}).sort("created_at", 1))


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, authorization: str | None = Header(default=None)):
    student_id = current(authorization, "student")
    get_db().conversations.delete_one({"conversation_id": conversation_id, "student_id": student_id})
    get_db().messages.delete_many({"conversation_id": conversation_id, "student_id": student_id})
    return {"message": "Chat deleted"}


# ---------- Staff: read-only view of the database tables ----------
STAFF_TABLES = {
    "students": "SELECT student_id, roll_number, full_name, programme, batch_year, current_semester, cgpa, active_backlogs "
                "FROM students ORDER BY student_id",
    "attendance": "SELECT s.student_id, s.roll_number, s.full_name, a.course_code, c.course_name, a.classes_attended, "
                  "a.classes_held, ROUND(100.0 * a.classes_attended / a.classes_held, 2) AS attendance_pct "
                  "FROM attendance a JOIN students s USING(student_id) JOIN courses c USING(course_code) "
                  "ORDER BY s.student_id, c.course_name",
    "results": "SELECT s.student_id, s.roll_number, s.full_name, r.course_code, c.course_name, r.exam_session, r.exam_type, "
               "r.internal_marks, r.external_marks, r.total_marks, r.max_marks, r.result, r.grade "
               "FROM results r JOIN students s USING(student_id) JOIN courses c USING(course_code) "
               "ORDER BY s.student_id, c.course_name, r.exam_session",
    "courses": "SELECT * FROM courses ORDER BY programme, semester, course_code",
    "rules": "SELECT rule_id, description, parameter, operator, value, scope_programmes, scope_batches, effective_from, "
             "effective_to, source_doc_id, source_section FROM rule_registry ORDER BY rule_id",
}


@router.get("/admin/tables/{name}")
def staff_table(name: str, authorization: str | None = Header(default=None)):
    """University staff only: the rows of one table (fixed queries, read-only; attendance % is computed)."""
    current(authorization, "admin")
    if name not in STAFF_TABLES:
        raise HTTPException(status_code=404, detail=f"Unknown table. Choose one of: {', '.join(STAFF_TABLES)}")
    return db.query(STAFF_TABLES[name])

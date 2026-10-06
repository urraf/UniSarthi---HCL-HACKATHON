"""
Accounts and login (stored in MongoDB), using only the standard library for security.

Passwords:  PBKDF2-SHA256 hash + random salt (never the password itself).
OTPs:       6 random digits, stored only as a hash, expire after OTP_MINUTES, limited attempts.
Tokens:     "<role>.<subject>.<expiry>.<signature>"   role = student | admin
            signature = HMAC-SHA256(SECRET_KEY, "<role>.<subject>.<expiry>")
            Anyone can read a token, but nobody can change it without SECRET_KEY.
Students log in with their roll number (e.g. 2023UIT3015); inside the system they are
identified by student_id (S####, the guide's fixed schema).
"""
import hashlib
import hmac
import re
import secrets
import time
from datetime import datetime, timedelta, timezone

from app import config, db
from app.mongo import get_db

HASH_ITERATIONS = 200_000
ROLL_NUMBER = re.compile(r"^\d{4}[A-Z]{3}\d{4}$")  # e.g. 2023UIT3015
MIN_PASSWORD = 8


class AuthError(Exception):
    """Login, sign-up, OTP or token problem (message is safe to show the user)."""


# ---------- Passwords ----------
def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS).hex()


def _new_hash(password: str) -> dict:
    if len(password) < MIN_PASSWORD:
        raise AuthError(f"Password must be at least {MIN_PASSWORD} characters")
    salt = secrets.token_hex(16)
    return {"salt": salt, "password_hash": hash_password(password, salt)}


def _password_ok(doc: dict | None, password: str) -> bool:
    # compare_digest avoids leaking information through timing
    return bool(doc) and hmac.compare_digest(doc["password_hash"], hash_password(password, doc["salt"]))


# ---------- Validation ----------
def normalise_roll(roll_number: str) -> str:
    roll = roll_number.strip().upper()
    if not ROLL_NUMBER.match(roll):
        raise AuthError("Roll number must look like 2023UIT3015")
    return roll


def normalise_email(email: str) -> str:
    email = email.strip().lower()
    if not re.fullmatch(r"[a-z0-9._%+-]+@" + re.escape(config.ALLOWED_EMAIL_DOMAIN), email):
        raise AuthError(f"Use your university email ending in @{config.ALLOWED_EMAIL_DOMAIN}")
    return email


def student_by_roll(roll: str) -> dict:
    """The student's record in SQLite (the university's data)."""
    student = db.query_one("SELECT * FROM students WHERE roll_number = ?", (roll,))
    if not student:
        raise AuthError("This roll number is not in the university records")
    return student


# ---------- One-time passwords ----------
def _otp_hash(code: str) -> str:
    return hmac.new(config.SECRET_KEY.encode(), code.encode(), hashlib.sha256).hexdigest()


def create_otp(email: str, purpose: str, student_id: str | None = None) -> str:
    """Make a new 6-digit code (replacing any older one for the same email + purpose)."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    get_db().otps.delete_many({"email": email, "purpose": purpose})
    get_db().otps.insert_one({
        "email": email, "purpose": purpose, "student_id": student_id, "code_hash": _otp_hash(code),
        "attempts": 0, "expires_at": datetime.now(timezone.utc) + timedelta(minutes=config.OTP_MINUTES),
    })
    return code


def check_otp(email: str, purpose: str, code: str) -> dict:
    """Return the OTP record if the code is right; it can only be used once."""
    otps = get_db().otps
    doc = otps.find_one({"email": email, "purpose": purpose})
    if not doc or doc["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise AuthError("The code has expired. Please request a new one.")
    if doc["attempts"] >= config.OTP_MAX_ATTEMPTS:
        raise AuthError("Too many wrong attempts. Please request a new code.")
    if not hmac.compare_digest(doc["code_hash"], _otp_hash(code.strip())):
        otps.update_one({"_id": doc["_id"]}, {"$inc": {"attempts": 1}})
        raise AuthError("Wrong code")
    otps.delete_one({"_id": doc["_id"]})
    return doc


# ---------- Student accounts ----------
def create_student_account(student_id: str, roll: str, email: str | None, password: str) -> None:
    users = get_db().users
    if users.find_one({"student_id": student_id}):
        raise AuthError("An account already exists for this roll number")
    if email and users.find_one({"email": email}):
        raise AuthError("This email is already used by another account")
    doc = {"student_id": student_id, "roll_number": roll, "created_at": datetime.now(timezone.utc), **_new_hash(password)}
    if email:
        doc["email"] = email
    users.insert_one(doc)


def set_password(email: str, password: str) -> None:
    get_db().users.update_one({"email": email}, {"$set": _new_hash(password)})


def student_login(roll_number: str, password: str) -> tuple[str, dict]:
    """Check roll number + password. Returns (token, student record)."""
    roll = normalise_roll(roll_number)
    user = get_db().users.find_one({"roll_number": roll})
    if not _password_ok(user, password):
        raise AuthError("Wrong roll number or password")
    student = db.query_one("SELECT * FROM students WHERE student_id = ?", (user["student_id"],))
    return create_token("student", user["student_id"]), student


# ---------- Staff (admin) accounts ----------
def create_admin(admin_id: str, password: str) -> None:
    get_db().admins.update_one({"admin_id": admin_id},
                               {"$set": {"admin_id": admin_id, "created_at": datetime.now(timezone.utc), **_new_hash(password)}},
                               upsert=True)


def admin_login(admin_id: str, password: str) -> str:
    if not _password_ok(get_db().admins.find_one({"admin_id": admin_id}), password):
        raise AuthError("Wrong staff ID or password")
    return create_token("admin", admin_id)


# ---------- Tokens ----------
def _sign(message: str) -> str:
    if not config.SECRET_KEY:
        raise AuthError("SECRET_KEY is not set in backend/.env")
    return hmac.new(config.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()


def create_token(role: str, subject: str) -> str:
    message = f"{role}.{subject}.{int(time.time()) + config.TOKEN_HOURS * 3600}"
    return f"{message}.{_sign(message)}"


def verify_token(token: str) -> tuple[str, str]:
    """Return (role, subject) of a valid token, or raise AuthError."""
    parts = token.split(".")
    if len(parts) < 4:
        raise AuthError("Malformed token")
    # role is first, expiry and signature are last; the subject in between may contain dots (dean.academics)
    role, subject, expiry, signature = parts[0], ".".join(parts[1:-2]), parts[-2], parts[-1]
    if not expiry.isdigit():
        raise AuthError("Malformed token")
    if not hmac.compare_digest(signature, _sign(f"{role}.{subject}.{expiry}")):
        raise AuthError("Invalid token")
    if int(expiry) < time.time():
        raise AuthError("Session expired, please log in again")
    return role, subject

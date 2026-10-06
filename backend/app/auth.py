"""
Simple, standard-library authentication.

Passwords:  stored as PBKDF2-SHA256 hash + random salt (never the password itself).
Tokens:     "<student_id>.<expiry_unix_time>.<signature>"
            signature = HMAC-SHA256(SECRET_KEY, "<student_id>.<expiry>")
            Anyone can read the token, but nobody can change it without SECRET_KEY.
"""
import hashlib
import hmac
import secrets
import time

from app import config, db

HASH_ITERATIONS = 200_000


class AuthError(Exception):
    """Login failed or token is invalid."""


# ---------- Passwords ----------
def hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS)
    return digest.hex()


def set_password(student_id: str, password: str) -> None:
    """Create or change a student's password."""
    salt = secrets.token_hex(16)
    db.execute(
        "INSERT OR REPLACE INTO student_logins (student_id, salt, password_hash) VALUES (?, ?, ?)",
        (student_id, salt, hash_password(password, salt)),
    )


def check_password(student_id: str, password: str) -> bool:
    row = db.query_one("SELECT salt, password_hash FROM student_logins WHERE student_id = ?", (student_id,))
    if not row:
        return False
    # compare_digest avoids leaking information through timing
    return hmac.compare_digest(row["password_hash"], hash_password(password, row["salt"]))


# ---------- Tokens ----------
def _sign(message: str) -> str:
    if not config.SECRET_KEY:
        raise AuthError("SECRET_KEY is not set in backend/.env")
    return hmac.new(config.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()


def create_token(student_id: str) -> str:
    expiry = int(time.time()) + config.TOKEN_HOURS * 3600
    message = f"{student_id}.{expiry}"
    return f"{message}.{_sign(message)}"


def verify_token(token: str) -> str:
    """Return the student_id inside a valid token, or raise AuthError."""
    try:
        student_id, expiry, signature = token.split(".")
    except ValueError:
        raise AuthError("Malformed token")
    if not hmac.compare_digest(signature, _sign(f"{student_id}.{expiry}")):
        raise AuthError("Invalid token signature")
    if int(expiry) < time.time():
        raise AuthError("Token expired, please log in again")
    return student_id


def login(student_id: str, password: str) -> str:
    """Check the password and return a new token."""
    if not check_password(student_id, password):
        raise AuthError("Wrong student ID or password")
    return create_token(student_id)

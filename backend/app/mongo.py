"""
MongoDB: student accounts, staff accounts, one-time passwords (OTPs) and chat history.
(Student records and the rule registry stay in SQLite, as the guide requires.)

Collections:
  users     {student_id, roll_number, email, salt, password_hash, created_at}
  admins    {admin_id, salt, password_hash, created_at}           university staff who add documents
  otps      {email, purpose, code_hash, student_id, attempts, expires_at}   auto-deleted when expired
  messages  {student_id, role, text, response, created_at}        chat history
"""
from pymongo import ASCENDING, MongoClient

from app import config

_db = None


def get_db():
    """Connect once and create the indexes."""
    global _db
    if _db is not None:
        return _db
    if not config.MONGODB_URI:
        raise RuntimeError("MONGODB_URI is not set in backend/.env")
    if config.MONGODB_URI.startswith("mongomock://"):  # in-memory MongoDB (tests / no database yet)
        import mongomock
        client = mongomock.MongoClient()
    else:
        client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
    _db = client[config.MONGODB_DB]

    _db.users.create_index("student_id", unique=True)
    _db.users.create_index("roll_number", unique=True)
    _db.users.create_index("email", unique=True, sparse=True)  # demo accounts may have no email
    _db.admins.create_index("admin_id", unique=True)
    _db.otps.create_index("expires_at", expireAfterSeconds=0)  # MongoDB deletes expired OTPs itself
    _db.otps.create_index([("email", ASCENDING), ("purpose", ASCENDING)])
    _db.messages.create_index([("student_id", ASCENDING), ("created_at", ASCENDING)])
    return _db

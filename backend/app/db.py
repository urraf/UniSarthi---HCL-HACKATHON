"""
SQLite database: student records, rule registry, source register, audit log.
(Accounts, OTPs and chat history are in MongoDB, see mongo.py.)

The first five tables follow the guide's fixed schema (Annex C) exactly.
We only ADD tables/columns, never rename or remove the required ones.
"""
import sqlite3

from app.config import DB_PATH

SCHEMA = """
-- ===== Annex C: student data (fixed schema) =====
CREATE TABLE IF NOT EXISTS students (
    student_id       TEXT PRIMARY KEY,      -- S + 4 digits, e.g. S1001
    full_name        TEXT NOT NULL,         -- synthetic names only
    programme        TEXT NOT NULL,         -- e.g. B.Tech CSE
    batch_year       INTEGER NOT NULL,      -- year of admission
    current_semester INTEGER NOT NULL,      -- 1-10
    cgpa             REAL NOT NULL,         -- 0.00-10.00
    active_backlogs  INTEGER NOT NULL,      -- >= 0
    roll_number      TEXT UNIQUE,           -- extra: university roll number, e.g. 2023UIT3015 (CSV column roll_no)
    email            TEXT                   -- extra: institute email (synthetic)
);

CREATE TABLE IF NOT EXISTS courses (
    course_code TEXT PRIMARY KEY,           -- e.g. CS201
    course_name TEXT NOT NULL,
    programme   TEXT NOT NULL,              -- must match students.programme
    semester    INTEGER NOT NULL,
    credits     INTEGER NOT NULL,
    course_type TEXT                        -- extra: Theory / Lab / Theory+Lab
);

CREATE TABLE IF NOT EXISTS attendance (
    student_id       TEXT NOT NULL REFERENCES students(student_id),
    course_code      TEXT NOT NULL REFERENCES courses(course_code),
    classes_held     INTEGER NOT NULL,      -- > 0
    classes_attended INTEGER NOT NULL,      -- 0 <= attended <= held (% is computed by tools, never stored)
    PRIMARY KEY (student_id, course_code)
);

CREATE TABLE IF NOT EXISTS results (
    student_id     TEXT NOT NULL REFERENCES students(student_id),
    course_code    TEXT NOT NULL REFERENCES courses(course_code),
    exam_session   TEXT NOT NULL,           -- e.g. 2026-MAY
    exam_type      TEXT NOT NULL,           -- REGULAR or SUPPLEMENTARY
    internal_marks INTEGER,                 -- empty for ABSENT / DETAINED
    external_marks INTEGER,
    total_marks    INTEGER,                 -- = internal + external
    max_marks      INTEGER NOT NULL,        -- e.g. 100
    result         TEXT NOT NULL,           -- PASS, FAIL, ABSENT or DETAINED
    grade          TEXT,                    -- extra: letter grade (NSUT grading table)
    PRIMARY KEY (student_id, course_code, exam_session, exam_type)
);

CREATE TABLE IF NOT EXISTS rule_registry (
    rule_id          TEXT PRIMARY KEY,      -- e.g. ATT-MIN-01
    description      TEXT NOT NULL,
    parameter        TEXT NOT NULL,         -- e.g. min_attendance_pct
    operator         TEXT NOT NULL,         -- >=, <=, in ...
    value            TEXT NOT NULL,         -- threshold value(s)
    scope_programmes TEXT NOT NULL DEFAULT 'ALL',
    scope_batches    TEXT NOT NULL DEFAULT 'ALL',
    effective_from   TEXT NOT NULL,         -- YYYY-MM-DD
    effective_to     TEXT DEFAULT '',       -- YYYY-MM-DD or empty
    source_doc_id    TEXT NOT NULL,         -- must exist in documents
    source_section   TEXT NOT NULL          -- clause, section or page
);

-- ===== Our own tables =====

-- Source Register (Annex B): one row per ingested document
CREATE TABLE IF NOT EXISTS documents (
    doc_id           TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    issuer           TEXT NOT NULL,
    authority_level  INTEGER NOT NULL,      -- 1 (highest) .. 5 (unofficial)
    doc_type         TEXT NOT NULL,         -- regulation, circular, notice, faq, handbook, unofficial
    version          TEXT NOT NULL,
    effective_from   TEXT NOT NULL,
    effective_to     TEXT DEFAULT '',
    supersedes       TEXT DEFAULT '',       -- "DOC-ID" or "DOC-ID#clause", separated by ;
    scope_programmes TEXT DEFAULT 'ALL',
    scope_batches    TEXT DEFAULT 'ALL',
    provenance       TEXT DEFAULT '',
    retrieved_on     TEXT DEFAULT '',
    synthetic        TEXT DEFAULT 'N',
    file_name        TEXT DEFAULT '',
    chunks_indexed   INTEGER DEFAULT 0
);

-- One row per /ask response (R10). The full record is stored as JSON.
CREATE TABLE IF NOT EXISTS audit_log (
    trace_id          TEXT PRIMARY KEY,
    timestamp         TEXT NOT NULL,
    student_id        TEXT,
    question_category TEXT,
    answer_type       TEXT,
    record_json       TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    """Open a connection. Rows behave like dicts: row["student_id"]."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create all tables if they do not exist yet."""
    with connect() as conn:
        conn.executescript(SCHEMA)


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a SELECT and return a list of plain dicts."""
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def query_one(sql: str, params: tuple = ()) -> dict | None:
    """Run a SELECT and return the first row (or None)."""
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple = ()) -> None:
    """Run an INSERT / UPDATE / DELETE."""
    with connect() as conn:
        conn.execute(sql, params)

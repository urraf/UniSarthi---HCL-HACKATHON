"""
Test setup: a fresh temporary database with the real source register and rule registry,
plus a few hand-made test students (so tests do not depend on LLM-generated data).
"""
import os
import sys
import tempfile
from pathlib import Path

# Must be set BEFORE app.config is imported
_tmp = tempfile.mkdtemp()
os.environ["DB_PATH"] = str(Path(_tmp) / "test.db")
os.environ["CHROMA_DIR"] = str(Path(_tmp) / "chroma")
os.environ["LLM_PROVIDER"] = "mock"
os.environ["SECRET_KEY"] = "test-secret-only-for-tests"
os.environ["MONGODB_URI"] = "mongomock://"
os.environ["DEV_PRINT_OTP"] = "true"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from app import db  # noqa: E402
from scripts.seed import load_rules, load_source_register  # noqa: E402

TEST_STUDENTS = [
    # id, name, programme, batch, semester, cgpa, backlogs, roll number
    ("S0001", "Test Exact", "B.Tech CSE", 2024, 5, 6.5, 0, "2024UCS0001"),
    ("S0002", "Test Below", "B.Tech CSE", 2024, 5, 8.0, 1, "2024UCS0002"),
    ("S0003", "Test Detained", "B.Tech CSE", 2025, 3, 7.0, 1, "2025UCS0003"),
]
TEST_COURSES = [("TC201", "Test Course A", "B.Tech CSE", 4, 4), ("TC202", "Test Course B", "B.Tech CSE", 4, 4)]
TEST_ATTENDANCE = [
    ("S0001", "TC201", 50, 40),  # exactly 80%
    ("S0002", "TC201", 50, 39),  # one class below 80% (78%), but above 75%
    ("S0003", "TC201", 40, 24),  # 60%
]
TEST_RESULTS = [
    ("S0001", "TC201", "2026-MAY", "REGULAR", 30, 40, 70, 100, "PASS"),
    ("S0002", "TC202", "2026-MAY", "REGULAR", 15, 24, 39, 100, "FAIL"),
    ("S0003", "TC201", "2026-MAY", "REGULAR", 20, 0, 20, 100, "DETAINED"),
]


@pytest.fixture(scope="session", autouse=True)
def test_db():
    db.init_db()
    load_source_register()
    load_rules()
    with db.connect() as conn:
        conn.executemany("INSERT INTO students VALUES (?,?,?,?,?,?,?,?)", TEST_STUDENTS)
        conn.executemany("INSERT INTO courses VALUES (?,?,?,?,?)", TEST_COURSES)
        conn.executemany("INSERT INTO attendance VALUES (?,?,?,?)", TEST_ATTENDANCE)
        conn.executemany("INSERT INTO results VALUES (?,?,?,?,?,?,?,?,?)", TEST_RESULTS)
    yield

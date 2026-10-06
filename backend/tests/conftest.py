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
    ("S0001", "Test Exact", "B.Tech IT", 2023, 7, 6.5, 0, "2023UIT0001"),
    ("S0002", "Test Short", "B.Tech IT", 2023, 7, 8.0, 3, "2023UIT0002"),
    ("S0003", "Test Floor", "B.Tech IT", 2024, 5, 7.0, 1, "2024UIT0003"),
]
TEST_COURSES = [("TC201", "Test Course A", "B.Tech IT", 5, 4), ("TC202", "Test Course B", "B.Tech IT", 5, 4)]
TEST_ATTENDANCE = [
    ("S0001", "TC201", 40, 30),  # exactly 75%
    ("S0002", "TC201", 40, 29),  # one class below 75% (72.5%), above the 60% floor
    ("S0003", "TC201", 40, 23),  # 57.5%: below the 60% floor
]
TEST_RESULTS = [
    ("S0001", "TC201", "2025-DEC", "REGULAR", 30, 40, 70, 100, "PASS"),
    ("S0002", "TC202", "2025-DEC", "REGULAR", 15, 19, 34, 100, "FAIL"),
    ("S0003", "TC201", "2025-DEC", "REGULAR", None, None, None, 100, "DETAINED"),
]


@pytest.fixture(scope="session", autouse=True)
def test_db():
    db.init_db()
    load_source_register()
    load_rules()
    with db.connect() as conn:
        conn.executemany("INSERT INTO students (student_id, full_name, programme, batch_year, current_semester, "
                         "cgpa, active_backlogs, roll_number) VALUES (?,?,?,?,?,?,?,?)", TEST_STUDENTS)
        conn.executemany("INSERT INTO courses (course_code, course_name, programme, semester, credits) "
                         "VALUES (?,?,?,?,?)", TEST_COURSES)
        conn.executemany("INSERT INTO attendance VALUES (?,?,?,?)", TEST_ATTENDANCE)
        conn.executemany("INSERT INTO results (student_id, course_code, exam_session, exam_type, internal_marks, "
                         "external_marks, total_marks, max_marks, result) VALUES (?,?,?,?,?,?,?,?,?)", TEST_RESULTS)
    yield

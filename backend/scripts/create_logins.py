"""
Create logins for students.

  python scripts/create_logins.py                              -> every student without a login
                                                                  gets DEFAULT_STUDENT_PASSWORD (from .env)
  python scripts/create_logins.py --student S1001 --password x -> set one student's password

No password is written in the code.
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import auth, db  # noqa: E402


def create_missing_logins() -> int:
    """Give every student without a login the default password from .env. Returns how many."""
    default_password = os.getenv("DEFAULT_STUDENT_PASSWORD", "")
    if not default_password:
        print("DEFAULT_STUDENT_PASSWORD not set in .env: no logins created")
        return 0
    missing = db.query(
        "SELECT student_id FROM students WHERE student_id NOT IN (SELECT student_id FROM student_logins)"
    )
    for row in missing:
        auth.set_password(row["student_id"], default_password)
    return len(missing)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student")
    parser.add_argument("--password")
    args = parser.parse_args()
    db.init_db()

    if args.student:
        if not args.password:
            raise SystemExit("--password is required with --student")
        if not db.query_one("SELECT 1 FROM students WHERE student_id = ?", (args.student,)):
            raise SystemExit(f"Unknown student {args.student}")
        auth.set_password(args.student, args.password)
        print(f"Password set for {args.student}")
    else:
        print(f"Logins created: {create_missing_logins()}")


if __name__ == "__main__":
    main()

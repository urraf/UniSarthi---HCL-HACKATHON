"""
Demo accounts (MongoDB) so the team and judges can log in without email sign-up.
Real students create their own account (sign up with @nsut.ac.in email + OTP).

  python scripts/create_logins.py                  -> every student without an account gets
                                                      DEFAULT_STUDENT_PASSWORD (from .env), no email
  python scripts/create_logins.py --roll 2024UCS3001 --password <pw>   -> set one demo account

No password is written in the code.
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import auth, db  # noqa: E402
from app.mongo import get_db  # noqa: E402


def create_demo_accounts(password: str) -> int:
    existing = {u["student_id"] for u in get_db().users.find({}, {"student_id": 1})}
    made = 0
    for s in db.query("SELECT student_id, roll_number FROM students WHERE roll_number IS NOT NULL"):
        if s["student_id"] not in existing:
            auth.create_student_account(s["student_id"], s["roll_number"], None, password)
            made += 1
    return made


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roll")
    parser.add_argument("--password")
    args = parser.parse_args()

    if args.roll:
        if not args.password:
            raise SystemExit("--password is required with --roll")
        s = auth.student_by_roll(auth.normalise_roll(args.roll))
        get_db().users.delete_one({"student_id": s["student_id"]})
        auth.create_student_account(s["student_id"], s["roll_number"], None, args.password)
        print(f"Demo account set for {s['roll_number']}")
        return

    password = os.getenv("DEFAULT_STUDENT_PASSWORD", "")
    if not password:
        raise SystemExit("Set DEFAULT_STUDENT_PASSWORD in backend/.env")
    print(f"Demo accounts created: {create_demo_accounts(password)}")


if __name__ == "__main__":
    main()

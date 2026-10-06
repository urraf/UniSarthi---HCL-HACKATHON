"""
Create (or reset) a university staff account that can add documents and see the sources.

  python scripts/create_admin.py --admin-id dean.academics --password <strong password>

No password is written in the code.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import auth  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--admin-id", required=True)
parser.add_argument("--password", required=True)
args = parser.parse_args()
auth.create_admin(args.admin_id.strip(), args.password)
print(f"Staff account ready: {args.admin_id}")

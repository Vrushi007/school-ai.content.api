"""
Seed data script for populating the database with initial curriculum data.

This script reads JSON files from seed_data/ directory and populates the database
in an idempotent manner (safe to run multiple times).

Usage:
    python seed_data.py
    or
    make seed
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.db.session import SessionLocal
from app.db.seed import run_seed


def main():
    """Main seeding function - calls the refactored seed logic"""
    db = SessionLocal()
    
    try:
        # Force seeding (ignore if data already exists)
        run_seed(db, force=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()


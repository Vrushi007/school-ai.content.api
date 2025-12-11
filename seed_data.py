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
from app.models import Board, State, Class, Subject, Chapter
from app.utils.db_utils import get_or_create, get_or_fail
from app.utils.json_loader import load_json


def seed_states(db):
    """Seed states from states.json"""
    print("🌍 Seeding states...")
    states_data = load_json("states.json")
    
    for item in states_data:
        state = get_or_create(
            db,
            State,
            {"code": item["code"]},
            {"name": item["name"]}
        )
        print(f"  ✓ {state.name} ({state.code})")
    
    print(f"✅ Seeded {len(states_data)} states\n")


def seed_boards(db):
    """Seed boards from boards.json"""
    print("📚 Seeding boards...")
    boards_data = load_json("boards.json")
    
    for item in boards_data:
        state = None
        if item.get("state_code"):
            state = db.query(State).filter_by(code=item["state_code"]).first()
            if not state:
                raise ValueError(
                    f"State with code '{item['state_code']}' not found for board '{item['name']}'"
                )
        
        board = get_or_create(
            db,
            Board,
            {"name": item["name"]},
            {
                "description": item.get("description"),
                "state_id": state.id if state else None
            }
        )
        board_type = "State-specific" if state else "National"
        print(f"  ✓ {board.name} ({board_type})")
    
    print(f"✅ Seeded {len(boards_data)} boards\n")


def seed_classes(db):
    """Seed classes from classes.json"""
    print("🎓 Seeding classes...")
    classes_data = load_json("classes.json")
    
    for item in classes_data:
        board_name = item.get("board_name")
        board = db.query(Board).filter(Board.name == board_name).first()
        if not board:
            raise ValueError(f"Board '{board_name}' not found for class '{item['name']}'")

        class_obj = get_or_create(
            db,
            Class,
            {"name": item["name"], "board_id": board.id},
            {"display_order": item.get("display_order", 0)}
        )
        print(f"  ✓ {class_obj.name} (Board: {board.name})")
    
    print(f"✅ Seeded {len(classes_data)} classes\n")


def seed_subjects(db):
    """Seed subjects from subjects.json  
       Requires each entry to contain:
       - class_name
       - name (subject name)
    """
    print("📝 Seeding subjects...")
    subjects_data = load_json("subjects.json")

    for item in subjects_data:
        class_name = item.get("class_name")
        subject_name = item.get("name")
        board_name = item.get("board_name")

        if not class_name or not subject_name or not board_name:
            raise ValueError(
                f"Invalid subject entry: {item}. "
                f"Each subject requires 'class_name', 'name', and 'board_name'."
            )
        
        # Get board (must exist)
        board = get_or_fail(
            db,
            Board,
            {"name": board_name},
            f"Board '{board_name}' not found for subject '{subject_name}'"
        )

        # Get class (must exist)
        class_obj = get_or_fail(
            db,
            Class,
            {"name": class_name, "board_id": board.id},
            f"Class '{class_name}' not found for subject '{subject_name}'"
        )

        # Insert or fetch subject under this class
        subject = get_or_create(
            db,
            Subject,
            {"name": subject_name, "class_id": class_obj.id},
            {}  # no defaults
        )

        print(f"  ✓ {subject.name} (Class: {class_obj.name})")

    print(f"✅ Seeded {len(subjects_data)} subjects\n")



def seed_chapters(db):
    print("📑 Seeding chapters...")
    chapters_data = load_json("chapters.json")

    for item in chapters_data:
        board_object = get_or_fail(
            db,
            Board,
            {"name": item["board_name"]},
            f"Board '{item['board_name']}' not found for chapter '{item['title']}'"
        )
        class_obj = get_or_fail(
            db,
            Class,
            {"name": item["class_name"], "board_id": board_object.id},
            f"Class '{item['class_name']}' not found for chapter '{item['title']}'"
        )

        subject = get_or_fail(
            db,
            Subject,
            {"name": item["subject_name"], "class_id": class_obj.id},
            f"Subject '{item['subject_name']}' not found in class '{class_obj.name}' for chapter '{item['title']}'"
        )

        chapter = get_or_create(
            db,
            Chapter,
            {
                "title": item["title"],
                "chapter_number": item.get("chapter_number"),
                "subject_id": subject.id
            },
            {"description": item.get("description")}
        )

        print(f"  ✓ {chapter.title} → {subject.name} / {class_obj.name}")

    print("✅ Chapters seeded\n")



def main():
    """Main seeding function"""
    print("=" * 60)
    print("🌱 Starting Database Seeding")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Seed in order (respecting foreign key dependencies)
        seed_states(db)
        seed_boards(db)
        seed_classes(db)
        seed_subjects(db)
        seed_chapters(db)
        
        print("=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 60)
        print(f"❌ Error during seeding: {str(e)}")
        print("=" * 60)
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()


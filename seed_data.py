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
from app.models import Board, State, Syllabus, Class, Subject, Chapter
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


def seed_syllabus(db):
    """Seed syllabus from syllabus.json"""
    print("📖 Seeding syllabus...")
    syllabus_data = load_json("syllabus.json")
    
    for item in syllabus_data:
        # Find board by name
        board = get_or_fail(
            db,
            Board,
            {"name": item["board_name"]},
            f"Board '{item['board_name']}' not found for syllabus '{item['name']}'"
        )
        
        # Validate board-state relationship
        if board.state_id is not None:
            # Board is state-specific
            if item.get("state_code") is None:
                raise ValueError(
                    f"Syllabus '{item['name']}' must have state_code for state-specific board '{board.name}'"
                )
            state = get_or_fail(
                db,
                State,
                {"code": item["state_code"]},
                f"State with code '{item['state_code']}' not found for syllabus '{item['name']}'"
            )
            if board.state_id != state.id:
                raise ValueError(
                    f"Syllabus '{item['name']}' state_code '{item['state_code']}' doesn't match board's state"
                )
            state_id = state.id
        else:
            # Board is national
            if item.get("state_code") is not None:
                raise ValueError(
                    f"Syllabus '{item['name']}' cannot have state_code for national board '{board.name}'"
                )
            state_id = None
        
        syllabus = get_or_create(
            db,
            Syllabus,
            {"name": item["name"], "board_id": board.id},
            {
                "state_id": state_id,
                "academic_year": item.get("academic_year")
            }
        )
        print(f"  ✓ {syllabus.name} (Board: {board.name})")
    
    print(f"✅ Seeded {len(syllabus_data)} syllabus entries\n")


def seed_classes(db):
    """Seed classes from classes.json"""
    print("🎓 Seeding classes...")
    classes_data = load_json("classes.json")
    
    for item in classes_data:
        # Find syllabus by name
        syllabus = get_or_fail(
            db,
            Syllabus,
            {"name": item["syllabus_name"]},
            f"Syllabus '{item['syllabus_name']}' not found for class '{item['name']}'"
        )
        
        class_obj = get_or_create(
            db,
            Class,
            {"name": item["name"], "syllabus_id": syllabus.id},
            {"display_order": item.get("display_order", 0)}
        )
        print(f"  ✓ {class_obj.name} (Syllabus: {syllabus.name})")
    
    print(f"✅ Seeded {len(classes_data)} classes\n")


def seed_subjects(db):
    """Seed subjects from subjects.json  
       Requires each entry to contain:
       - syllabus_name
       - class_name
       - name (subject name)
    """
    print("📝 Seeding subjects...")
    subjects_data = load_json("subjects.json")

    for item in subjects_data:
        syllabus_name = item.get("syllabus_name")
        class_name = item.get("class_name")
        subject_name = item.get("name")

        if not syllabus_name or not class_name or not subject_name:
            raise ValueError(
                f"Invalid subject entry: {item}. "
                f"Each subject requires 'syllabus_name', 'class_name', and 'name'."
            )

        # 1️⃣ Get syllabus (must exist)
        syllabus = get_or_fail(
            db,
            Syllabus,
            {"name": syllabus_name},
            f"Syllabus '{syllabus_name}' not found for subject '{subject_name}'"
        )

        # 2️⃣ Get class (must exist AND match syllabus)
        class_obj = get_or_fail(
            db,
            Class,
            {"name": class_name, "syllabus_id": syllabus.id},
            (
                f"Class '{class_name}' not found under syllabus '{syllabus_name}' "
                f"for subject '{subject_name}'"
            )
        )

        # 3️⃣ Insert or fetch subject under this class
        subject = get_or_create(
            db,
            Subject,
            {"name": subject_name, "class_id": class_obj.id},
            {}  # no defaults
        )

        print(f"  ✓ {subject.name} (Class: {class_obj.name}, Syllabus: {syllabus.name})")

    print(f"✅ Seeded {len(subjects_data)} subjects\n")



def seed_chapters(db):
    print("📑 Seeding chapters...")
    chapters_data = load_json("chapters.json")

    for item in chapters_data:
        syllabus = get_or_fail(
            db,
            Syllabus,
            {"name": item["syllabus_name"]},
            f"Syllabus '{item['syllabus_name']}' not found for chapter '{item['title']}'"
        )

        class_obj = get_or_fail(
            db,
            Class,
            {"name": item["class_name"], "syllabus_id": syllabus.id},
            f"Class '{item['class_name']}' not found under syllabus '{item['syllabus_name']}'"
        )

        subject = get_or_fail(
            db,
            Subject,
            {"name": item["subject_name"], "class_id": class_obj.id},
            f"Subject '{item['subject_name']}' not found in class '{class_obj.name}' for syllabus '{syllabus.name}'"
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

        print(f"  ✓ {chapter.title} → {subject.name} / {class_obj.name} / {syllabus.name}")

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
        seed_syllabus(db)
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


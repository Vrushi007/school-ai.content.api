"""
Seed data functions for populating the database with initial curriculum data.

This module provides reusable seed functions that can be called during application
startup or manually via seed_data.py script.
"""
import json
from sqlalchemy.orm import Session

from app.models import (
    Board, State, Class, Subject, Chapter, KeyPoint, KeyPointContent,
    LessonPlanInput, LessonPlanSessionMap, LessonPlanSessionContent
)
from app.utils.db_utils import get_or_create, get_or_fail
from app.utils.json_loader import load_json


def seed_states(db: Session):
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


def seed_boards(db: Session):
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


def seed_classes(db: Session):
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


def seed_subjects(db: Session):
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


def seed_chapters(db: Session):
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


def seed_key_points(db: Session):
    """Seed key points and their content from key_points.json"""
    print("🎯 Seeding key points and content...")
    key_points_data = load_json("key_points.json")

    for item in key_points_data:
        chapter_name = item.get("chapter_name")
        
        if not chapter_name:
            raise ValueError(
                f"Invalid key_point entry: {item}. "
                f"Each key_point requires 'chapter_name'."
            )
        
        # Get chapter (must exist)
        chapter = get_or_fail(
            db,
            Chapter,
            {"title": chapter_name},
            f"Chapter '{chapter_name}' not found for key point '{item['title']}'"
        )

        # Insert or fetch key point
        key_point = get_or_create(
            db,
            KeyPoint,
            {"code": item["code"]},
            {
                "title": item["title"],
                "section": item.get("section"),
                "chapter_id": chapter.id,
                "difficulty_level": item["difficulty_level"],
                "cognitive_level": item["congnitive_level"],  # Note: JSON has typo "congnitive"
                "skill_intent": item["skill_intent"]
            }
        )

        print(f"  ✓ {key_point.code}: {key_point.title[:50]}...")
        
        # Handle content if present
        if item.get("content"):
            try:
                content_dict = json.loads(item["content"])
                
                # Check if content already exists for this key_point
                existing_content = db.query(KeyPointContent).filter_by(
                    key_point_id=key_point.id,
                    is_active=True
                ).first()
                
                if existing_content:
                    # Update existing content
                    existing_content.content = content_dict
                    db.add(existing_content)
                    print(f"    ↻ Updated content")
                else:
                    # Create new content
                    key_point_content = KeyPointContent(
                        key_point_id=key_point.id,
                        content=content_dict,
                        is_active=True
                    )
                    db.add(key_point_content)
                    print(f"    + Added content")
            except json.JSONDecodeError as e:
                print(f"    ⚠ Invalid JSON in content: {e}")

    db.commit()
    print(f"✅ Seeded {len(key_points_data)} key points with content\n")


def seed_lesson_plans(db: Session):
    """Seed lesson plans from session_content_with_lesson_plans.json"""
    print("📚 Seeding lesson plans...")
    sessions_data = load_json("session_content_with_lesson_plans.json")
    
    # Group sessions by input_hash to create lesson plan inputs
    lesson_plans = {}
    for session in sessions_data:
        input_hash = session.get("input_hash")
        if input_hash not in lesson_plans:
            lesson_plans[input_hash] = {
                "board_name": session["board_name"],
                "class": session["class"],
                "subject_name": session["subject_name"],
                "chapter_name": session["chapter_name"],
                "planned_sessions": session["planned_sessions"],
                "sessions": []
            }
        lesson_plans[input_hash]["sessions"].append(session)
    
    # Process each lesson plan
    for input_hash, plan_data in lesson_plans.items():
        # Look up foreign keys
        board = get_or_fail(
            db,
            Board,
            {"name": plan_data["board_name"]},
            f"Board '{plan_data['board_name']}' not found"
        )
        
        class_obj = get_or_fail(
            db,
            Class,
            {"name": str(plan_data["class"]), "board_id": board.id},
            f"Class '{plan_data['class']}' not found for board '{plan_data['board_name']}'"
        )
        
        subject = get_or_fail(
            db,
            Subject,
            {"name": plan_data["subject_name"], "class_id": class_obj.id},
            f"Subject '{plan_data['subject_name']}' not found for class '{plan_data['class']}'"
        )
        
        chapter = get_or_fail(
            db,
            Chapter,
            {"title": plan_data["chapter_name"], "subject_id": subject.id},
            f"Chapter '{plan_data['chapter_name']}' not found for subject '{plan_data['subject_name']}'"
        )
        
        # Create or get LessonPlanInput
        lesson_input = get_or_create(
            db,
            LessonPlanInput,
            {"input_hash": input_hash},
            {
                "board_id": board.id,
                "class_id": class_obj.id,
                "subject_id": subject.id,
                "chapter_id": chapter.id,
                "planned_sessions": plan_data["planned_sessions"]
            }
        )
        
        print(f"  ✓ Lesson plan: {plan_data['chapter_name']} ({plan_data['planned_sessions']} sessions)")
        
        # Process each session
        for session in plan_data["sessions"]:
            session_number = session["session_number"]
            session_title = session["session_title"]
            kp_codes = session.get("kp_codes", [])
            
            # Convert kp_codes to kp_ids
            kp_ids = []
            for code in kp_codes:
                kp = db.query(KeyPoint).filter_by(code=code).first()
                if kp:
                    kp_ids.append(kp.id)
                else:
                    print(f"    ⚠ Key point '{code}' not found, skipping")
            
            # Create or get LessonPlanSessionMap
            session_map = db.query(LessonPlanSessionMap).filter_by(
                input_id=lesson_input.id,
                session_number=session_number
            ).first()
            
            if session_map:
                # Update existing session map
                session_map.session_title = session_title
                session_map.kp_ids = kp_ids
                db.add(session_map)
                print(f"    ↻ Updated session {session_number}: {session_title}")
            else:
                # Create new session map
                session_map = LessonPlanSessionMap(
                    input_id=lesson_input.id,
                    session_number=session_number,
                    session_title=session_title,
                    kp_ids=kp_ids,
                    is_active=True
                )
                db.add(session_map)
                db.flush()  # Ensure session_map.id is available
                print(f"    + Created session {session_number}: {session_title}")
            
            # Handle session content if present
            session_summary = session.get("session_summary")
            session_content = session.get("session_content")
            
            if session_summary or session_content:
                # Check if content already exists
                existing_content = db.query(LessonPlanSessionContent).filter_by(
                    session_id=session_map.id
                ).first()
                
                if existing_content:
                    # Update existing content
                    if session_summary:
                        existing_content.session_summary = session_summary
                    if session_content:
                        existing_content.session_content = session_content
                    db.add(existing_content)
                    print(f"      ↻ Updated content")
                else:
                    # Create new content
                    content = LessonPlanSessionContent(
                        session_id=session_map.id,
                        session_summary=session_summary or {},
                        session_content=session_content
                    )
                    db.add(content)
                    print(f"      + Added content")
    
    db.commit()
    print(f"✅ Seeded {len(lesson_plans)} lesson plans with sessions\n")


def should_seed_data(db: Session) -> bool:
    """
    Check if database should be seeded.
    Returns True if database is empty (no states found).
    """
    state_count = db.query(State).count()
    return state_count == 0


def run_seed(db: Session, force: bool = False):
    """
    Main seeding function that runs all seed functions in dependency order.
    
    Args:
        db: SQLAlchemy database session
        force: If True, runs seeding even if database already has data
    """
    if not force and not should_seed_data(db):
        print("Database already contains data. Skipping seed.")
        return
    
    print("=" * 60)
    print("🌱 Starting Database Seeding")
    print("=" * 60)
    print()
    
    try:
        # Seed in order (respecting foreign key dependencies)
        seed_states(db)
        seed_boards(db)
        seed_classes(db)
        seed_subjects(db)
        seed_chapters(db)
        seed_key_points(db)
        seed_lesson_plans(db)
        
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

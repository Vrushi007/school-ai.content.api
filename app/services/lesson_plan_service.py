from sqlalchemy.orm import Session
from app.models.lesson_plan_input import LessonPlanInput
from app.models.lesson_plan_session_map import LessonPlanSessionMap
from app.models.lesson_plan_session_content import LessonPlanSessionContent
from app.schemas.lesson_plan_input import LessonPlanInputCreate, LessonPlanRequest
from app.schemas.lesson_plan_session_map import LessonPlanSessionMapCreate
from app.schemas.lesson_plan_session_content import LessonPlanSessionContentCreate
from app.utils.hash_utils import generate_input_hash
from typing import Optional, Tuple, List, Dict, Any
import httpx
from app.db.session import AI_SERVICE_URL


def create_lesson_plan_input(db: Session, lesson_input: LessonPlanInputCreate) -> LessonPlanInput:
    """
    Create a new lesson plan input record.
    """
    db_input = LessonPlanInput(**lesson_input.model_dump())
    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    return db_input


def create_session_map(db: Session, session_map: LessonPlanSessionMapCreate) -> LessonPlanSessionMap:
    """
    Create a new session map record.
    """
    db_session_map = LessonPlanSessionMap(**session_map.model_dump())
    db.add(db_session_map)
    db.commit()
    db.refresh(db_session_map)
    return db_session_map


def get_session_maps_by_input_id(db: Session, input_id: int) -> List[LessonPlanSessionMap]:
    """
    Retrieve all session maps for a given lesson plan input.
    """
    return db.query(LessonPlanSessionMap).filter(
        LessonPlanSessionMap.input_id == input_id,
        LessonPlanSessionMap.is_active == True
    ).order_by(LessonPlanSessionMap.session_number).all()


async def call_group_kps_service(
    subject_name: str,
    class_name: str,
    chapter_title: str,
    board_name: str,
    number_of_sessions: int,
    key_points: List[dict]
) -> dict:
    """
    Call the external AI service to group key points into sessions.
    
    Args:
        subject_name: Name of the subject
        class_name: Name of the class
        chapter_title: Title of the chapter
        board_name: Name of the board
        key_points: List of key point dictionaries with kp_id, title, difficulty, cognitive_level, prerequisites
    
    Returns:
        The response JSON from the AI service
    
    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{AI_SERVICE_URL}/api/group-kps-into-sessions"
    
    payload = {
        "board": board_name,
        "chapter": chapter_title,
        "class_name": class_name,
        "subject": subject_name,
        "number_of_sessions": number_of_sessions,
        "session_duration": "40 minutes",
        "knowledge_points": key_points
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def group_kps_into_sessions(
    db: Session,
    request: LessonPlanRequest
) -> Tuple[bool, List[dict], dict]:
    """
    Group key points into sessions or retrieve from cache.
    
    Args:
        db: Database session
        request: LessonPlanRequest with all parameters
    
    Returns:
        Tuple of (from_cache: bool, sessions: list, metadata: dict)
    """
    # Generate hash for the request
    input_hash = generate_input_hash(
        board_id=request.board_id,
        class_id=request.class_id,
        subject_id=request.subject_id,
        chapter_id=request.chapter_id,
        planned_sessions=request.planned_sessions
    )
    
    # Check if we have a cached result
    lesson_input = db.query(LessonPlanInput).filter(LessonPlanInput.input_hash == input_hash).first()
    
    if lesson_input:
        # Check if we have session maps for this input
        session_maps = get_session_maps_by_input_id(db, lesson_input.id)
        
        if session_maps:
            # Query session contents for summary and objectives
            # Get all session_ids from session_maps
            session_ids = [sm.id for sm in session_maps]
            session_contents = db.query(LessonPlanSessionContent).filter(
                LessonPlanSessionContent.session_id.in_(session_ids)
            ).all()
            
            # Create lookup dicts for session contents by session_id
            content_by_session_id = {
                sc.session_id: sc.session_summary
                for sc in session_contents
            }
            
            # Create lookup for session_content availability
            content_available_by_session_id = {
                sc.session_id: sc.session_content is not None
                for sc in session_contents
            }
            
            # Convert to response format
            sessions = [
                {
                    "session_map_id": sm.id,
                    "session_number": sm.session_number,
                    "session_title": sm.session_title,
                    "kp_ids": sm.kp_ids,
                    "summary": content_by_session_id.get(sm.id, {}).get("summary") if sm.id in content_by_session_id else None,
                    "objectives": content_by_session_id.get(sm.id, {}).get("objectives") if sm.id in content_by_session_id else None,
                    "is_detailed_content_available": content_available_by_session_id.get(sm.id, False)
                }
                for sm in session_maps
            ]
            
            # Get metadata from stored data or recreate
            from app.services import subject_service, class_service, chapter_service
            subject = subject_service.get_subject_by_id(db, request.subject_id)
            class_obj = class_service.get_class_by_id(db, request.class_id)
            chapter = chapter_service.get_chapter_by_id(db, request.chapter_id)
            
            metadata = {
                "chapter": chapter.title if chapter else "",
                "subject": subject.name if subject else "",
                "class": class_obj.name if class_obj else "",
                "total_sessions": len(sessions),
                "total_kps": sum(len(s["kp_ids"]) for s in sessions)
            }
            
            return True, sessions, metadata
    
    # Not in cache - need to fetch data and call AI service
    from app.services import subject_service, class_service, chapter_service, board_service, key_point_service
    
    # Get subject, class, chapter, and board details
    subject = subject_service.get_subject_by_id(db, request.subject_id)
    if not subject:
        raise ValueError("Subject not found")
    
    class_obj = class_service.get_class_by_id(db, request.class_id)
    if not class_obj:
        raise ValueError("Class not found")
    
    chapter = chapter_service.get_chapter_by_id(db, request.chapter_id)
    if not chapter:
        raise ValueError("Chapter not found")
    
    board = board_service.get_board_by_id(db, request.board_id)
    if not board:
        raise ValueError("Board not found")
    
    # Get key points for the chapter
    key_points = key_point_service.get_key_points_by_chapter(db, request.chapter_id)
    if not key_points:
        raise ValueError("No key points found for this chapter")
    print(f"Found {len(key_points)} key points for chapter ID {request.chapter_id}")
    # Format key points for AI service
    formatted_kps = [
        {
            "kp_id": kp.id,
            "title": kp.title,
            "difficulty": kp.difficulty_level.value,
            "cognitive_level": kp.cognitive_level.value,
            "prerequisites": []  # Add logic for prerequisites if available in your model
        }
        for kp in key_points
    ]
    
    # Call AI service
    ai_response = await call_group_kps_service(
        subject_name=subject.name,
        class_name=class_obj.name,
        chapter_title=chapter.title,
        board_name=board.name,
        number_of_sessions=request.planned_sessions,
        key_points=formatted_kps
    )
    
    # Check if AI service returned success
    if not ai_response.get("success"):
        raise ValueError(f"AI service error: {ai_response.get('error', 'Unknown error')}")
    
    # Extract session data
    data = ai_response.get("data", {})
    sessions = data.get("sessions", [])
    metadata = data.get("metadata", {})
    
    # Validate that we have sessions before creating input
    if not sessions:
        raise ValueError("AI service returned no sessions")
    
    # Create or get lesson plan input
    if not lesson_input:
        input_create = LessonPlanInputCreate(
            board_id=request.board_id,
            class_id=request.class_id,
            subject_id=request.subject_id,
            chapter_id=request.chapter_id,
            planned_sessions=request.planned_sessions,
            input_hash=input_hash
        )
        lesson_input = create_lesson_plan_input(db, input_create)
    
    # Store each session in the database
    try:
        for session in sessions:
            session_map_create = LessonPlanSessionMapCreate(
                input_id=lesson_input.id,
                session_number=session.get("session_number"),
                session_title=session.get("session_title"),
                kp_ids=session.get("kp_ids"),
                version=None,  # Can be extracted from AI response if available
                is_active=True
            )
            created_session_map = create_session_map(db, session_map_create)
            
            # Add session_map_id, summary and objectives to the session response
            session["session_map_id"] = created_session_map.id
            session["summary"] = None
            session["objectives"] = None
            session["is_detailed_content_available"] = False
    except Exception as e:
        # If session creation fails and we just created the input, rollback by deleting it
        if lesson_input and not db.query(LessonPlanSessionMap).filter(
            LessonPlanSessionMap.input_id == lesson_input.id
        ).first():
            db.delete(lesson_input)
            db.commit()
        raise ValueError(f"Failed to create session maps: {str(e)}")
    
    return False, sessions, metadata


def get_session_map_by_id(db: Session, session_map_id: int) -> Optional[LessonPlanSessionMap]:
    """
    Retrieve a session map by its ID.
    """
    return db.query(LessonPlanSessionMap).filter(LessonPlanSessionMap.id == session_map_id).first()


def create_session_content(db: Session, session_content: LessonPlanSessionContentCreate) -> LessonPlanSessionContent:
    """
    Create a new session content record.
    """
    db_session_content = LessonPlanSessionContent(**session_content.model_dump())
    db.add(db_session_content)
    db.commit()
    db.refresh(db_session_content)
    return db_session_content


async def call_generate_session_summary(
    board: str,
    chapter: str,
    class_name: str,
    subject: str,
    session_title: str,
    knowledge_points: List[Dict[str, Any]]
) -> dict:
    """
    Call the external AI service to generate session summary.
    
    Args:
        board: Board name
        chapter: Chapter title
        class_name: Class name
        subject: Subject name
        session_title: Title of the session
        knowledge_points: List of key points with kp_id, title, difficulty, cognitive_level
    
    Returns:
        The response JSON from the AI service
    
    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{AI_SERVICE_URL}/api/generate-session-summary"
    
    payload = {
        "board": board,
        "chapter": chapter,
        "class": class_name,
        "subject": subject,
        "session_title": session_title,
        "knowledge_points": knowledge_points
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def generate_session_summary(
    db: Session,
    session_map_id: int
) -> Tuple[int, str, str, List[str]]:
    """
    Generate session summary using AI service and store in database.
    
    Args:
        db: Database session
        session_map_id: ID of the session map
    
    Returns:
        Tuple of (session_number, session_title, summary, objectives)
    """
    # Get session map
    session_map = get_session_map_by_id(db, session_map_id)
    if not session_map:
        raise ValueError("Session map not found")
    
    # Get lesson plan input
    lesson_input = db.query(LessonPlanInput).filter(LessonPlanInput.id == session_map.input_id).first()
    if not lesson_input:
        raise ValueError("Lesson plan input not found")
    
    # Get related entities
    from app.services import board_service, class_service, subject_service, chapter_service, key_point_service
    
    board = board_service.get_board_by_id(db, lesson_input.board_id)
    if not board:
        raise ValueError("Board not found")
    
    class_obj = class_service.get_class_by_id(db, lesson_input.class_id)
    if not class_obj:
        raise ValueError("Class not found")
    
    subject = subject_service.get_subject_by_id(db, lesson_input.subject_id)
    if not subject:
        raise ValueError("Subject not found")
    
    chapter = chapter_service.get_chapter_by_id(db, lesson_input.chapter_id)
    if not chapter:
        raise ValueError("Chapter not found")
    
    # Get key points based on kp_ids from session_map
    kp_ids = session_map.kp_ids  # This is a list of kp IDs
    
    # Convert kp_ids from strings to integers if needed
    if kp_ids and isinstance(kp_ids[0], str):
        kp_ids = [int(kp_id) for kp_id in kp_ids]
    
    all_key_points = key_point_service.get_key_points_by_chapter(db, lesson_input.chapter_id)
    
    # Filter key points that match the kp_ids in the session
    filtered_kps = [kp for kp in all_key_points if kp.id in kp_ids]
    
    if not filtered_kps:
        raise ValueError("No key points found for the session")
    
    # Format key points for AI service
    knowledge_points = [
        {
            "kp_id": kp.id,
            "title": kp.title,
            "difficulty": kp.difficulty_level.value,
            "cognitive_level": kp.cognitive_level.value
        }
        for kp in filtered_kps
    ]
    
    # Call AI service
    ai_response = await call_generate_session_summary(
        board=board.name,
        chapter=chapter.title,
        class_name=class_obj.name,
        subject=subject.name,
        session_title=session_map.session_title,
        knowledge_points=knowledge_points
    )
    
    # Check if AI service returned success
    if not ai_response.get("success"):
        raise ValueError(f"AI service error: {ai_response.get('error', 'Unknown error')}")
    
    # Extract data from response
    data = ai_response.get("data", {})
    summary = data.get("summary", "")
    objectives = data.get("objectives", [])
    
    # Create session summary object to store
    session_summary_data = {
        "summary": summary,
        "objectives": objectives
    }
    
    # Store in database
    session_content_create = LessonPlanSessionContentCreate(
        session_id=session_map_id,
        session_summary=session_summary_data,
        session_content=None,  # Will be generated later
        version=None
    )
    create_session_content(db, session_content_create)
    
    return session_map.session_number, session_map.session_title, summary, objectives


def get_session_content_by_id(db: Session, session_id: int) -> Optional[LessonPlanSessionContent]:
    """
    Retrieve session content by its ID.
    """
    return db.query(LessonPlanSessionContent).filter(LessonPlanSessionContent.session_id == session_id).first()

async def call_generate_detailed_content(
    subject_name: str,
    class_name: str,
    title: str,
    duration: str,
    summary: str,
    objectives: List[str],
    kp_list: List[Dict[str, Any]]
) -> dict:
    """
    Call the external AI service to generate detailed session content.
    
    Args:
        subject_name: Subject name
        class_name: Class name
        title: Session title
        duration: Session duration
        summary: Session summary
        objectives: List of objectives
        kp_list: List of key points with title and description
    
    Returns:
        The response JSON from the AI service
    
    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{AI_SERVICE_URL}/api/generate-detailed-content-for-session"
    
    payload = {
        "subject_name": subject_name,
        "class_name": class_name,
        "title": title,
        "duration": duration,
        "summary": summary,
        "objectives": objectives,
        "kp_list": kp_list
    }
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def get_or_generate_session_detailed_content(
    db: Session,
    session_id: int
) -> Tuple[bool, Dict[str, Any]]:
    """
    Get detailed session content from cache or generate it using AI service.
    
    Args:
        db: Database session
        session_id: ID of the session content record
    
    Returns:
        Tuple of (from_cache: bool, content: dict)
    """
    # Get session content record
    session_content = get_session_content_by_id(db, session_id)
    if not session_content:
        raise ValueError("Session content not found")
    
    # Check if detailed content already exists
    if session_content.session_content is not None:
        return True, session_content.session_content
    
    # Need to generate detailed content
    # Get session map to access session details
    session_map = get_session_map_by_id(db, session_content.session_id)
    if not session_map:
        raise ValueError("Session map not found")
    
    # Get lesson plan input to access related entities
    lesson_input = db.query(LessonPlanInput).filter(LessonPlanInput.id == session_map.input_id).first()
    if not lesson_input:
        raise ValueError("Lesson plan input not found")
    
    # Get related entities
    from app.services import subject_service, class_service, key_point_service
    
    subject = subject_service.get_subject_by_id(db, lesson_input.subject_id)
    if not subject:
        raise ValueError("Subject not found")
    
    class_obj = class_service.get_class_by_id(db, lesson_input.class_id)
    if not class_obj:
        raise ValueError("Class not found")
    
    # Get key points based on kp_ids from session_map
    kp_ids = session_map.kp_ids
    
    # Convert kp_ids from strings to integers if needed
    if kp_ids and isinstance(kp_ids[0], str):
        kp_ids = [int(kp_id) for kp_id in kp_ids]
    
    all_key_points = key_point_service.get_key_points_by_chapter(db, lesson_input.chapter_id)
    
    # Filter key points that match the kp_ids in the session
    filtered_kps = [kp for kp in all_key_points if kp.id in kp_ids]
    
    if not filtered_kps:
        raise ValueError("No key points found for the session")
    
    # Format key points for AI service
    kp_list = [
        {
            "title": kp.title,
            "description": kp.content.get("description", "") if hasattr(kp, 'content') and kp.content else ""
        }
        for kp in filtered_kps
    ]
    
    # Extract summary and objectives from session_summary
    summary = session_content.session_summary.get("summary", "")
    objectives = session_content.session_summary.get("objectives", [])
    
    # Call AI service
    ai_response = await call_generate_detailed_content(
        subject_name=subject.name,
        class_name=class_obj.name,
        title=session_map.session_title,
        duration="40 mins",  # Default duration
        summary=summary,
        objectives=objectives,
        kp_list=kp_list
    )
    
    # Check if AI service returned success
    if not ai_response.get("success"):
        raise ValueError(f"AI service error: {ai_response.get('error', 'Unknown error')}")
    
    # Extract content from response
    content = ai_response.get("data", {}).get("content", {})
    
    # Update session_content in database
    session_content.session_content = content
    db.commit()
    db.refresh(session_content)
    
    return False, content


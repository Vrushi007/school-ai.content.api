from sqlalchemy.orm import Session
from app.models.lesson_plan_input import LessonPlanInput
from app.models.lesson_plan_output import LessonPlanOutput
from app.schemas.lesson_plan_input import LessonPlanInputCreate, LessonPlanRequest
from app.schemas.lesson_plan_output import LessonPlanOutputCreate
from app.utils.hash_utils import generate_input_hash
from typing import Optional, Tuple
import httpx
from app.db.session import AI_SERVICE_URL


def get_lesson_plan_by_hash(db: Session, input_hash: str) -> Optional[Tuple[LessonPlanInput, LessonPlanOutput]]:
    """
    Retrieve cached lesson plan by input hash.
    
    Returns:
        Tuple of (LessonPlanInput, LessonPlanOutput) if found, None otherwise
    """
    lesson_input = db.query(LessonPlanInput).filter(LessonPlanInput.input_hash == input_hash).first()
    
    if lesson_input and lesson_input.output:
        return lesson_input, lesson_input.output
    
    return None


def create_lesson_plan_input(db: Session, lesson_input: LessonPlanInputCreate) -> LessonPlanInput:
    """
    Create a new lesson plan input record.
    """
    db_input = LessonPlanInput(**lesson_input.model_dump())
    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    return db_input


def create_lesson_plan_output(db: Session, lesson_output: LessonPlanOutputCreate) -> LessonPlanOutput:
    """
    Create a new lesson plan output record.
    """
    db_output = LessonPlanOutput(**lesson_output.model_dump())
    db.add(db_output)
    db.commit()
    db.refresh(db_output)
    return db_output


async def call_ai_service(
    subject_name: str,
    class_name: str,
    chapter_title: str,
    number_of_sessions: int,
    default_session_duration: str = "40 minutes"
) -> dict:
    """
    Call the external AI service to generate a lesson plan.
    
    Returns:
        The response JSON from the AI service
    
    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{AI_SERVICE_URL}/api/generate-lesson-plan"
    
    payload = {
        "subject_name": subject_name,
        "class_name": class_name,
        "chapter_title": chapter_title,
        "number_of_sessions": number_of_sessions,
        "default_session_duration": default_session_duration
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def generate_or_retrieve_lesson_plan(
    db: Session,
    request: LessonPlanRequest
) -> Tuple[bool, list]:
    """
    Generate a new lesson plan or retrieve from cache.
    
    Args:
        db: Database session
        request: LessonPlanRequest with all parameters
    
    Returns:
        Tuple of (from_cache: bool, lesson_plan: list)
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
    cached = get_lesson_plan_by_hash(db, input_hash)
    
    if cached:
        lesson_input, lesson_output = cached
        return True, lesson_output.response_json.get("lesson_plan", [])
    
    # Not in cache - need to fetch data and call AI service
    from app.services import subject_service, class_service, chapter_service
    
    # Get subject, class, and chapter details
    subject = subject_service.get_subject_by_id(db, request.subject_id)
    if not subject:
        raise ValueError("Subject not found")
    
    class_obj = class_service.get_class_by_id(db, request.class_id)
    if not class_obj:
        raise ValueError("Class not found")
    
    chapter = chapter_service.get_chapter_by_id(db, request.chapter_id)
    if not chapter:
        raise ValueError("Chapter not found")
    
    # Call AI service
    ai_response = await call_ai_service(
        subject_name=subject.name,
        class_name=class_obj.name,
        chapter_title=chapter.title,
        number_of_sessions=request.planned_sessions,
        default_session_duration="40 minutes"
    )
    
    # Check if AI service returned success
    if not ai_response.get("success"):
        raise ValueError(f"AI service error: {ai_response.get('error', 'Unknown error')}")
    
    # Extract lesson plan data
    lesson_plan_data = ai_response.get("data", {}).get("lesson_plan", [])
    
    # Store input
    input_create = LessonPlanInputCreate(
        board_id=request.board_id,
        class_id=request.class_id,
        subject_id=request.subject_id,
        chapter_id=request.chapter_id,
        planned_sessions=request.planned_sessions,
        input_hash=input_hash
    )
    db_input = create_lesson_plan_input(db, input_create)
    
    # Store output
    output_create = LessonPlanOutputCreate(
        input_id=db_input.id,
        response_json={"lesson_plan": lesson_plan_data},
        model_version=None,  # Can be extracted from AI response if available
        prompt_version=None  # Can be extracted from AI response if available
    )
    create_lesson_plan_output(db, output_create)
    
    return False, lesson_plan_data

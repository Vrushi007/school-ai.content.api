from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.lesson_plan_input import LessonPlanRequest, LessonPlanResponse
from app.services import lesson_plan_service

router = APIRouter(prefix="/lesson-plans", tags=["lesson-plans"])


@router.post("/generate", response_model=LessonPlanResponse)
async def generate_lesson_plan(request: LessonPlanRequest, db: Session = Depends(get_db)):
    """
    Generate a lesson plan or retrieve from cache.
    
    This endpoint:
    1. Generates a hash from the request parameters
    2. Checks if a cached lesson plan exists
    3. If cached, returns it with from_cache=True
    4. If not cached:
       - Fetches subject, class, and chapter details from the database
       - Calls the external AI service to generate a lesson plan
       - Stores the input and output in the database
       - Returns the generated plan with from_cache=False
    
    Request body:
    - board_id: Board identifier
    - class_id: Class identifier
    - subject_id: Subject identifier
    - chapter_id: Chapter identifier
    - planned_sessions: Number of sessions to generate
    
    Response:
    - from_cache: Boolean indicating if the result was retrieved from cache
    - lesson_plan: List of session objects with details
    """
    try:
        from_cache, lesson_plan = await lesson_plan_service.generate_or_retrieve_lesson_plan(db, request)
        
        return LessonPlanResponse(
            from_cache=from_cache,
            lesson_plan=lesson_plan
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lesson plan: {str(e)}")



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.lesson_plan_input import LessonPlanRequest
from app.schemas.lesson_plan_session_map import GroupKpsResponse, SessionData, SessionMetadata
from app.schemas.lesson_plan_session_content import (
    SessionSummaryRequest, 
    SessionSummaryResponse,
    SessionDetailedRequest,
    SessionDetailedResponse,
    SessionDetailedData
)
from app.services import lesson_plan_service

router = APIRouter(prefix="/lesson-plans", tags=["lesson-plans"])


@router.post("/group-kps-into-sessions", response_model=GroupKpsResponse)
async def group_kps_into_sessions(request: LessonPlanRequest, db: Session = Depends(get_db)):
    """
    Group key points into sessions or retrieve from cache.
    
    This endpoint:
    1. Generates a hash from the request parameters
    2. Checks if cached session maps exist
    3. If cached, returns them with from_cache=True
    4. If not cached:
       - Fetches subject, class, chapter, and board details from the database
       - Calls the external AI service to group KPs into sessions
       - Stores each session in lesson_plan_session_map table
       - Returns the grouped sessions with from_cache=False
    
    Request body:
    - board_id: Board identifier
    - class_id: Class identifier
    - subject_id: Subject identifier
    - chapter_id: Chapter identifier
    - planned_sessions: Number of sessions (used for hash generation)
    
    Response:
    - from_cache: Boolean indicating if the result was retrieved from cache
    - sessions: List of session objects with session_number, session_title, and kp_ids
    - metadata: Information about chapter, subject, class, total sessions and KPs
    - success: Boolean indicating success
    """
    try:
        from_cache, sessions, metadata = await lesson_plan_service.group_kps_into_sessions(db, request)
        
        # Convert to Pydantic models
        session_data_list = [SessionData(**session) for session in sessions]
        metadata_obj = SessionMetadata(**metadata)
        
        return GroupKpsResponse(
            from_cache=from_cache,
            sessions=session_data_list,
            metadata=metadata_obj,
            success=True
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to group KPs into sessions: {str(e)}")


@router.post("/generate-session-summary", response_model=SessionSummaryResponse)
async def generate_session_summary(request: SessionSummaryRequest, db: Session = Depends(get_db)):
    """
    Generate session summary and objectives using AI service.
    
    This endpoint:
    1. Retrieves the session map using session_map_id
    2. Queries lesson plan input, board, class, subject, and chapter details
    3. Filters key points based on kp_ids from the session map
    4. Calls the external AI service to generate session summary
    5. Stores the summary and objectives in lesson_plan_session_content table
    6. Returns the generated summary and objectives
    
    Request body:
    - session_map_id: ID of the session map from lesson_plan_session_map table
    
    Response:
    - success: Boolean indicating success
    - session_number: Session number
    - session_title: Title of the session
    - summary: Generated session summary
    - objectives: List of session objectives
    """
    try:
        session_number, session_title, summary, objectives = await lesson_plan_service.generate_session_summary(
            db, request.session_map_id
        )
        
        return SessionSummaryResponse(
            success=True,
            session_number=session_number,
            session_title=session_title,
            summary=summary,
            objectives=objectives
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate session summary: {str(e)}")


@router.post("/get-session-detailed-content", response_model=SessionDetailedResponse)
async def get_session_detailed_content(request: SessionDetailedRequest, db: Session = Depends(get_db)):
    """
    Get or generate detailed session content.
    
    This endpoint:
    1. Retrieves the session content record by ID
    2. If detailed content exists, returns it from cache
    3. If detailed content doesn't exist:
       - Fetches related entities (subject, class, chapter, key points)
       - Calls the AI service to generate detailed content
       - Stores the generated content in the database
       - Returns the newly generated content
    
    Request body:
    - session_id: ID of the session content record
    
    Response:
    - success: Boolean indicating success
    - from_cache: Whether content was retrieved from cache
    - data: Object containing:
        - session_id: ID of the session content
        - content: Detailed session content object with teaching script, board work, etc.
    """
    try:
        from_cache, content = await lesson_plan_service.get_or_generate_session_detailed_content(
            db=db,
            session_id=request.session_id
        )
        
        return SessionDetailedResponse(
            success=True,
            from_cache=from_cache,
            data=SessionDetailedData(
                session_id=request.session_id,
                content=content
            )
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get/generate session detailed content: {str(e)}")



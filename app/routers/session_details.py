from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.session_details import SessionDetailsCreate, SessionDetailsResponse, SessionDetailsUpdate
from app.services import session_details_service, session_service

router = APIRouter(prefix="/session-details", tags=["session-details"])


@router.post("", response_model=SessionDetailsResponse, status_code=201)
def create_session_details(session_details: SessionDetailsCreate, db: Session = Depends(get_db)):
    # Validate session exists
    session = session_service.get_session_by_id(db, session_details.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if details already exist
    existing = session_details_service.get_session_details_by_session_id(db, session_details.session_id)
    if existing:
        raise HTTPException(status_code=400, detail="Session details already exist for this session")
    
    return session_details_service.create_session_details(db, session_details)


@router.get("/sessions/{session_id}", response_model=SessionDetailsResponse)
def get_session_details(session_id: int, db: Session = Depends(get_db)):
    details = session_details_service.get_session_details_by_session_id(db, session_id)
    if not details:
        raise HTTPException(status_code=404, detail="Session details not found")
    return details


@router.put("/{session_details_id}", response_model=SessionDetailsResponse)
def update_session_details(session_details_id: int, session_details_update: SessionDetailsUpdate, db: Session = Depends(get_db)):
    updated = session_details_service.update_session_details(db, session_details_id, session_details_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Session details not found")
    return updated


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.services import session_service, chapter_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    # Validate chapter exists
    chapter = chapter_service.get_chapter_by_id(db, session.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return session_service.create_session(db, session)


@router.get("/chapters/{chapter_id}", response_model=List[SessionResponse])
def get_sessions_by_chapter(chapter_id: int, db: Session = Depends(get_db)):
    return session_service.get_sessions_by_chapter(db, chapter_id)


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, session_update: SessionUpdate, db: Session = Depends(get_db)):
    if session_update.chapter_id:
        chapter = chapter_service.get_chapter_by_id(db, session_update.chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
    
    updated = session_service.update_session(db, session_id, session_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    success = session_service.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None


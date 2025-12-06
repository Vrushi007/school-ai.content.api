from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.session_key_point import SessionKeyPointResponse, SessionKeyPointBulkCreate
from app.services import session_key_point_service, session_service, key_point_service

router = APIRouter(prefix="/session-key-points", tags=["session-key-points"])


@router.post("/bulk", response_model=List[SessionKeyPointResponse], status_code=201)
async def create_session_key_points_bulk(bulk_data: SessionKeyPointBulkCreate, db: Session = Depends(get_db)):
    # Validate session exists
    session = session_service.get_session_by_id(db, bulk_data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate all key points exist
    for key_point_id in bulk_data.key_point_ids:
        key_point = key_point_service.get_key_point_by_id(db, key_point_id)
        if not key_point:
            raise HTTPException(status_code=404, detail=f"Key point {key_point_id} not found")
    
    return session_key_point_service.create_session_key_points_bulk(db, bulk_data)


@router.get("/sessions/{session_id}", response_model=List[SessionKeyPointResponse])
async def get_key_points_by_session(session_id: int, db: Session = Depends(get_db)):
    return session_key_point_service.get_key_points_by_session(db, session_id)


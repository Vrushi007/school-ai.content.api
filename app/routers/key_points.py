from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.key_point import KeyPointCreate, KeyPointResponse, KeyPointUpdate, KeyPointBulkCreate
from app.services import key_point_service, chapter_service

router = APIRouter(prefix="/key-points", tags=["key-points"])


@router.post("", response_model=KeyPointResponse, status_code=201)
def create_key_point(key_point: KeyPointCreate, db: Session = Depends(get_db)):
    # Validate chapter exists
    chapter = chapter_service.get_chapter_by_id(db, key_point.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return key_point_service.create_key_point(db, key_point)


@router.post("/bulk", response_model=List[KeyPointResponse], status_code=201)
def create_key_points_bulk(bulk_data: KeyPointBulkCreate, db: Session = Depends(get_db)):
    # Validate chapter exists
    chapter = chapter_service.get_chapter_by_id(db, bulk_data.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return key_point_service.create_key_points_bulk(db, bulk_data)


@router.get("/chapters/{chapter_id}", response_model=List[KeyPointResponse])
def get_key_points_by_chapter(chapter_id: int, db: Session = Depends(get_db)):
    return key_point_service.get_key_points_by_chapter(db, chapter_id)


@router.put("/{key_point_id}", response_model=KeyPointResponse)
def update_key_point(key_point_id: int, key_point_update: KeyPointUpdate, db: Session = Depends(get_db)):
    if key_point_update.chapter_id:
        chapter = chapter_service.get_chapter_by_id(db, key_point_update.chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
    
    updated = key_point_service.update_key_point(db, key_point_id, key_point_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Key point not found")
    return updated


@router.delete("/{key_point_id}", status_code=204)
def delete_key_point(key_point_id: int, db: Session = Depends(get_db)):
    success = key_point_service.delete_key_point(db, key_point_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key point not found")
    return None


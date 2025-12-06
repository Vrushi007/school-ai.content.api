from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.chapter import ChapterCreate, ChapterResponse, ChapterUpdate
from app.services import chapter_service, subject_service

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.post("", response_model=ChapterResponse, status_code=201)
async def create_chapter(chapter: ChapterCreate, db: Session = Depends(get_db)):
    # Validate subject exists
    subject = subject_service.get_subject_by_id(db, chapter.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return chapter_service.create_chapter(db, chapter)


@router.get("/subjects/{subject_id}", response_model=List[ChapterResponse])
async def get_chapters_by_subject(subject_id: int, db: Session = Depends(get_db)):
    return chapter_service.get_chapters_by_subject(db, subject_id)


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = chapter_service.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(chapter_id: int, chapter_update: ChapterUpdate, db: Session = Depends(get_db)):
    if chapter_update.subject_id:
        subject = subject_service.get_subject_by_id(db, chapter_update.subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
    
    updated = chapter_service.update_chapter(db, chapter_id, chapter_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return updated


@router.delete("/{chapter_id}", status_code=204)
async def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    success = chapter_service.delete_chapter(db, chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return None


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services import subject_service, class_service

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    # Validate class exists
    class_obj = class_service.get_class_by_id(db, subject.class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return subject_service.create_subject(db, subject)


@router.get("/classes/{class_id}", response_model=List[SubjectResponse])
async def get_subjects_by_class(class_id: int, db: Session = Depends(get_db)):
    return subject_service.get_subjects_by_class(db, class_id)


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: int, subject_update: SubjectUpdate, db: Session = Depends(get_db)):
    if subject_update.class_id:
        class_obj = class_service.get_class_by_id(db, subject_update.class_id)
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
    
    updated = subject_service.update_subject(db, subject_id, subject_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Subject not found")
    return updated


@router.delete("/{subject_id}", status_code=204)
async def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    success = subject_service.delete_subject(db, subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return None


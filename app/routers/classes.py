from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.class_model import ClassCreate, ClassResponse, ClassUpdate
from app.services import class_service, syllabus_service

router = APIRouter(prefix="/classes", tags=["classes"])


@router.post("", response_model=ClassResponse, status_code=201)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    # Validate syllabus exists
    syllabus = syllabus_service.get_syllabus_by_id(db, class_data.syllabus_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    return class_service.create_class(db, class_data)


@router.get("/syllabus/{syllabus_id}", response_model=List[ClassResponse])
def get_classes_by_syllabus(syllabus_id: int, db: Session = Depends(get_db)):
    return class_service.get_classes_by_syllabus(db, syllabus_id)


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, class_update: ClassUpdate, db: Session = Depends(get_db)):
    if class_update.syllabus_id:
        syllabus = syllabus_service.get_syllabus_by_id(db, class_update.syllabus_id)
        if not syllabus:
            raise HTTPException(status_code=404, detail="Syllabus not found")
    
    updated = class_service.update_class(db, class_id, class_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Class not found")
    return updated


@router.delete("/{class_id}", status_code=204)
def delete_class(class_id: int, db: Session = Depends(get_db)):
    success = class_service.delete_class(db, class_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return None


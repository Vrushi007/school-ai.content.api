from sqlalchemy.orm import Session
from app.models.syllabus import Syllabus
from app.schemas.syllabus import SyllabusCreate, SyllabusUpdate
from typing import List


def create_syllabus(db: Session, syllabus: SyllabusCreate) -> Syllabus:
    db_syllabus = Syllabus(**syllabus.model_dump())
    db.add(db_syllabus)
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus


def get_syllabi(db: Session, skip: int = 0, limit: int = 100) -> List[Syllabus]:
    return db.query(Syllabus).offset(skip).limit(limit).all()


def get_syllabus_by_id(db: Session, syllabus_id: int) -> Syllabus | None:
    return db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()


def update_syllabus(db: Session, syllabus_id: int, syllabus_update: SyllabusUpdate) -> Syllabus | None:
    db_syllabus = get_syllabus_by_id(db, syllabus_id)
    if not db_syllabus:
        return None
    
    update_data = syllabus_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_syllabus, field, value)
    
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus


def delete_syllabus(db: Session, syllabus_id: int) -> bool:
    db_syllabus = get_syllabus_by_id(db, syllabus_id)
    if not db_syllabus:
        return False
    
    db.delete(db_syllabus)
    db.commit()
    return True


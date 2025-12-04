from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate
from typing import List


def create_subject(db: Session, subject: SubjectCreate) -> Subject:
    db_subject = Subject(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_subjects_by_class(db: Session, class_id: int) -> List[Subject]:
    return db.query(Subject).filter(Subject.class_id == class_id).all()


def get_subject_by_id(db: Session, subject_id: int) -> Subject | None:
    return db.query(Subject).filter(Subject.id == subject_id).first()


def update_subject(db: Session, subject_id: int, subject_update: SubjectUpdate) -> Subject | None:
    db_subject = get_subject_by_id(db, subject_id)
    if not db_subject:
        return None
    
    update_data = subject_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subject, field, value)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int) -> bool:
    db_subject = get_subject_by_id(db, subject_id)
    if not db_subject:
        return False
    
    db.delete(db_subject)
    db.commit()
    return True


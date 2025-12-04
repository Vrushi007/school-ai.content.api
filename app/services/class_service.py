from sqlalchemy.orm import Session
from app.models.class_model import Class
from app.schemas.class_model import ClassCreate, ClassUpdate
from typing import List


def create_class(db: Session, class_data: ClassCreate) -> Class:
    db_class = Class(**class_data.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


def get_classes_by_syllabus(db: Session, syllabus_id: int) -> List[Class]:
    return db.query(Class).filter(Class.syllabus_id == syllabus_id).order_by(Class.display_order).all()


def get_class_by_id(db: Session, class_id: int) -> Class | None:
    return db.query(Class).filter(Class.id == class_id).first()


def update_class(db: Session, class_id: int, class_update: ClassUpdate) -> Class | None:
    db_class = get_class_by_id(db, class_id)
    if not db_class:
        return None
    
    update_data = class_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_class, field, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class


def delete_class(db: Session, class_id: int) -> bool:
    db_class = get_class_by_id(db, class_id)
    if not db_class:
        return False
    
    db.delete(db_class)
    db.commit()
    return True


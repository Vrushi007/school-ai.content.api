from sqlalchemy.orm import Session
from app.models.key_point import KeyPoint
from app.schemas.key_point import KeyPointCreate, KeyPointUpdate, KeyPointBulkCreate
from typing import List


def create_key_point(db: Session, key_point: KeyPointCreate) -> KeyPoint:
    db_key_point = KeyPoint(**key_point.model_dump())
    db.add(db_key_point)
    db.commit()
    db.refresh(db_key_point)
    return db_key_point


def create_key_points_bulk(db: Session, bulk_data: KeyPointBulkCreate) -> List[KeyPoint]:
    key_points = []
    for kp_data in bulk_data.key_points:
        kp_dict = kp_data.model_dump()
        kp_dict["chapter_id"] = bulk_data.chapter_id
        db_key_point = KeyPoint(**kp_dict)
        db.add(db_key_point)
        key_points.append(db_key_point)
    
    db.commit()
    for kp in key_points:
        db.refresh(kp)
    return key_points


def get_key_points_by_chapter(db: Session, chapter_id: int) -> List[KeyPoint]:
    return db.query(KeyPoint).filter(KeyPoint.chapter_id == chapter_id).order_by(KeyPoint.order).all()


def get_key_point_by_id(db: Session, key_point_id: int) -> KeyPoint | None:
    return db.query(KeyPoint).filter(KeyPoint.id == key_point_id).first()


def update_key_point(db: Session, key_point_id: int, key_point_update: KeyPointUpdate) -> KeyPoint | None:
    db_key_point = get_key_point_by_id(db, key_point_id)
    if not db_key_point:
        return None
    
    update_data = key_point_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_key_point, field, value)
    
    db.commit()
    db.refresh(db_key_point)
    return db_key_point


def delete_key_point(db: Session, key_point_id: int) -> bool:
    db_key_point = get_key_point_by_id(db, key_point_id)
    if not db_key_point:
        return False
    
    db.delete(db_key_point)
    db.commit()
    return True


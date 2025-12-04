from sqlalchemy.orm import Session
from app.models.session_key_point import SessionKeyPoint
from app.schemas.session_key_point import SessionKeyPointBulkCreate
from typing import List


def create_session_key_point_mapping(db: Session, session_id: int, key_point_id: int, order: int = 0) -> SessionKeyPoint:
    db_mapping = SessionKeyPoint(
        session_id=session_id,
        key_point_id=key_point_id,
        order=order
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


def create_session_key_points_bulk(db: Session, bulk_data: SessionKeyPointBulkCreate) -> List[SessionKeyPoint]:
    mappings = []
    for idx, key_point_id in enumerate(bulk_data.key_point_ids):
        db_mapping = SessionKeyPoint(
            session_id=bulk_data.session_id,
            key_point_id=key_point_id,
            order=idx
        )
        db.add(db_mapping)
        mappings.append(db_mapping)
    
    db.commit()
    for mapping in mappings:
        db.refresh(mapping)
    return mappings


def get_key_points_by_session(db: Session, session_id: int) -> List[SessionKeyPoint]:
    return db.query(SessionKeyPoint).filter(SessionKeyPoint.session_id == session_id).order_by(SessionKeyPoint.order).all()


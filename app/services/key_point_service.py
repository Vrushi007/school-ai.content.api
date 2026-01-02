from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.key_point import KeyPoint
from app.models.key_point_content import KeyPointContent
from app.schemas.key_point import KeyPointCreate, KeyPointUpdate


def create_key_point(db: Session, key_points: List[KeyPointCreate]) -> List[KeyPoint]:
    created_key_points = []
    
    for key_point in key_points:
        # Extract content and version fields (not part of KeyPoint model)
        key_point_data = key_point.model_dump(exclude={'content', 'model_version', 'prompt_version'})
        content_data = key_point.content
        model_version = key_point.model_version
        prompt_version = key_point.prompt_version
        
        # Create the key_point record
        db_key_point = KeyPoint(**key_point_data)
        db.add(db_key_point)
        db.flush()  # Flush to get the ID without committing
        
        # Create the associated key_point_content record
        db_key_point_content = KeyPointContent(
            key_point_id=db_key_point.id,
            content=content_data,
            model_version=model_version,
            prompt_version=prompt_version,
            is_active=True
        )
        db.add(db_key_point_content)
        created_key_points.append(db_key_point)
    
    # Commit all records at once
    db.commit()
    
    # Refresh all created key points
    for kp in created_key_points:
        db.refresh(kp)
    
    return created_key_points


def get_key_point_by_id(db: Session, key_point_id: int) -> Optional[KeyPoint]:
    return db.query(KeyPoint).filter(KeyPoint.id == key_point_id).first()


def get_key_point_by_code(db: Session, code: str) -> Optional[KeyPoint]:
    return db.query(KeyPoint).filter(KeyPoint.code == code).first()


def get_key_points_by_chapter(db: Session, chapter_id: int) -> List[KeyPoint]:
    key_points = (
        db.query(KeyPoint)
        .options(joinedload(KeyPoint.key_point_contents))
        .filter(KeyPoint.chapter_id == chapter_id)
        .order_by(KeyPoint.id)
        .all()
    )
    
    # Manually set content attribute from latest active key_point_content
    for kp in key_points:
        if kp.key_point_contents:
            active_contents = [c for c in kp.key_point_contents if c.is_active]
            if active_contents:
                latest = sorted(active_contents, key=lambda x: x.created_at, reverse=True)[0]
                kp.content = latest.content
            else:
                kp.content = None
        else:
            kp.content = None
    
    return key_points


def get_all_key_points(db: Session, skip: int = 0, limit: int = 100) -> List[KeyPoint]:
    return db.query(KeyPoint).offset(skip).limit(limit).all()


def update_key_point(db: Session, key_point_id: int, key_point_update: KeyPointUpdate) -> Optional[KeyPoint]:
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

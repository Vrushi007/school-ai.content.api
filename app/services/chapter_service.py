from sqlalchemy.orm import Session
from app.models.chapter import Chapter
from app.schemas.chapter import ChapterCreate, ChapterUpdate
from typing import List


def create_chapter(db: Session, chapter: ChapterCreate) -> Chapter:
    db_chapter = Chapter(**chapter.model_dump())
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def get_chapters_by_subject(db: Session, subject_id: int) -> List[Chapter]:
    return db.query(Chapter).filter(Chapter.subject_id == subject_id).order_by(Chapter.chapter_number).all()


def get_chapter_by_id(db: Session, chapter_id: int) -> Chapter | None:
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def update_chapter(db: Session, chapter_id: int, chapter_update: ChapterUpdate) -> Chapter | None:
    db_chapter = get_chapter_by_id(db, chapter_id)
    if not db_chapter:
        return None
    
    update_data = chapter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chapter, field, value)
    
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def delete_chapter(db: Session, chapter_id: int) -> bool:
    db_chapter = get_chapter_by_id(db, chapter_id)
    if not db_chapter:
        return False
    
    db.delete(db_chapter)
    db.commit()
    return True


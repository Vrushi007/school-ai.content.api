from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate
from typing import List


def create_session(db: DBSession, session: SessionCreate) -> Session:
    db_session = Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions_by_chapter(db: DBSession, chapter_id: int) -> List[Session]:
    return db.query(Session).filter(Session.chapter_id == chapter_id).order_by(Session.session_number).all()


def get_session_by_id(db: DBSession, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()


def update_session(db: DBSession, session_id: int, session_update: SessionUpdate) -> Session | None:
    db_session = get_session_by_id(db, session_id)
    if not db_session:
        return None
    
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: DBSession, session_id: int) -> bool:
    db_session = get_session_by_id(db, session_id)
    if not db_session:
        return False
    
    db.delete(db_session)
    db.commit()
    return True


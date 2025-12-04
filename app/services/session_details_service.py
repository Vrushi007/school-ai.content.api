from sqlalchemy.orm import Session
from app.models.session_details import SessionDetails
from app.schemas.session_details import SessionDetailsCreate, SessionDetailsUpdate


def create_session_details(db: Session, session_details: SessionDetailsCreate) -> SessionDetails:
    db_details = SessionDetails(**session_details.model_dump())
    db.add(db_details)
    db.commit()
    db.refresh(db_details)
    return db_details


def get_session_details_by_session_id(db: Session, session_id: int) -> SessionDetails | None:
    return db.query(SessionDetails).filter(SessionDetails.session_id == session_id).first()


def update_session_details(db: Session, session_details_id: int, session_details_update: SessionDetailsUpdate) -> SessionDetails | None:
    db_details = db.query(SessionDetails).filter(SessionDetails.id == session_details_id).first()
    if not db_details:
        return None
    
    update_data = session_details_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_details, field, value)
    
    db.commit()
    db.refresh(db_details)
    return db_details


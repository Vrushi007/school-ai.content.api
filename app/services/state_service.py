from sqlalchemy.orm import Session
from app.models.state import State
from app.schemas.state import StateCreate
from typing import List


def create_state(db: Session, state: StateCreate) -> State:
    db_state = State(**state.model_dump())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


def get_states(db: Session, skip: int = 0, limit: int = 100) -> List[State]:
    return db.query(State).offset(skip).limit(limit).all()


def get_state_by_id(db: Session, state_id: int) -> State | None:
    return db.query(State).filter(State.id == state_id).first()


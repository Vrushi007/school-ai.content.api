from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.state import StateCreate, StateResponse
from app.services import state_service

router = APIRouter(prefix="/states", tags=["states"])


@router.post("", response_model=StateResponse, status_code=201)
async def create_state(state: StateCreate, db: Session = Depends(get_db)):
    return state_service.create_state(db, state)


@router.get("", response_model=List[StateResponse])
async def get_states(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return state_service.get_states(db, skip=skip, limit=limit)


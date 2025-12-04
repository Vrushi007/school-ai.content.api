from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.board import BoardCreate, BoardResponse, BoardUpdate
from app.services import board_service, state_service

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("", response_model=BoardResponse, status_code=201)
def create_board(board: BoardCreate, db: Session = Depends(get_db)):
    # Check if board with same name exists
    existing = board_service.get_board_by_name(db, board.name)
    if existing:
        raise HTTPException(status_code=400, detail="Board with this name already exists")
    
    # Validate state_id if provided
    if board.state_id is not None:
        state = state_service.get_state_by_id(db, board.state_id)
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
    
    return board_service.create_board(db, board)


@router.get("", response_model=List[BoardResponse])
def get_boards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return board_service.get_boards(db, skip=skip, limit=limit)


@router.get("/{board_id}", response_model=BoardResponse)
def get_board(board_id: int, db: Session = Depends(get_db)):
    board = board_service.get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.put("/{board_id}", response_model=BoardResponse)
def update_board(board_id: int, board_update: BoardUpdate, db: Session = Depends(get_db)):
    # Validate state_id if provided
    if board_update.state_id is not None:
        state = state_service.get_state_by_id(db, board_update.state_id)
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
    
    updated = board_service.update_board(db, board_id, board_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Board not found")
    return updated


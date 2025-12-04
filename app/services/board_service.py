from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate
from typing import List


def create_board(db: Session, board: BoardCreate) -> Board:
    db_board = Board(**board.model_dump())
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


def get_boards(db: Session, skip: int = 0, limit: int = 100) -> List[Board]:
    return db.query(Board).offset(skip).limit(limit).all()


def get_board_by_id(db: Session, board_id: int) -> Board | None:
    return db.query(Board).filter(Board.id == board_id).first()


def get_board_by_name(db: Session, name: str) -> Board | None:
    return db.query(Board).filter(Board.name == name).first()


def update_board(db: Session, board_id: int, board_update: BoardUpdate) -> Board | None:
    db_board = get_board_by_id(db, board_id)
    if not db_board:
        return None
    
    update_data = board_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_board, field, value)
    
    db.commit()
    db.refresh(db_board)
    return db_board


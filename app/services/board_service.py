from sqlalchemy.orm import Session, joinedload
from app.models.board import Board
from app.models.state import State
from app.schemas.board import BoardCreate, BoardUpdate
from typing import List


def create_board(db: Session, board: BoardCreate) -> Board:
    db_board = Board(**board.model_dump())
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


def get_boards(db: Session, skip: int = 0, limit: int = 100) -> List[Board]:
    query = (
        db.query(Board)
        .filter(Board.is_active == True)
        .outerjoin(State)
        .options(joinedload(Board.state))
        .offset(skip)
        .limit(limit)
    )
    boards = query.all()
    
    # Add state_name to each board object
    for board in boards:
        if board.state:
            board.state_name = board.state.name
        else:
            board.state_name = None
    
    return boards


def get_board_by_id(db: Session, board_id: int) -> Board | None:
    board = db.query(Board).options(joinedload(Board.state)).filter(Board.id == board_id).first()
    
    if board:
        if board.state:
            board.state_name = board.state.name
        else:
            board.state_name = None
    
    return board


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


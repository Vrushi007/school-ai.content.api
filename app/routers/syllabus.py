from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.syllabus import SyllabusCreate, SyllabusResponse, SyllabusUpdate
from app.services import syllabus_service, board_service, state_service

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.post("", response_model=SyllabusResponse, status_code=201)
def create_syllabus(syllabus: SyllabusCreate, db: Session = Depends(get_db)):
    # Validate board exists
    board = board_service.get_board_by_id(db, syllabus.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Validate state_id based on board type
    # If board is state-specific (board.state_id is not None)
    if board.state_id is not None:
        # Syllabus must have matching state_id
        if syllabus.state_id != board.state_id:
            raise HTTPException(
                status_code=400,
                detail=f"Board '{board.name}' is state-specific. Syllabus state_id must match board's state_id ({board.state_id})"
            )
        # Validate state exists
        state = state_service.get_state_by_id(db, syllabus.state_id)
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
    else:
        # Board is national (state_id is None)
        # Syllabus must also have state_id as None
        if syllabus.state_id is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Board '{board.name}' is a national board. Syllabus state_id must be null"
            )
    
    return syllabus_service.create_syllabus(db, syllabus)


@router.get("", response_model=List[SyllabusResponse])
def get_syllabi(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return syllabus_service.get_syllabi(db, skip=skip, limit=limit)


@router.get("/{syllabus_id}", response_model=SyllabusResponse)
def get_syllabus(syllabus_id: int, db: Session = Depends(get_db)):
    syllabus = syllabus_service.get_syllabus_by_id(db, syllabus_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return syllabus


@router.put("/{syllabus_id}", response_model=SyllabusResponse)
def update_syllabus(syllabus_id: int, syllabus_update: SyllabusUpdate, db: Session = Depends(get_db)):
    # Get existing syllabus
    existing_syllabus = syllabus_service.get_syllabus_by_id(db, syllabus_id)
    if not existing_syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Determine which board to validate against
    # If board_id is being updated, use new value; otherwise use existing
    board_id = syllabus_update.board_id if syllabus_update.board_id is not None else existing_syllabus.board_id
    board = board_service.get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Get update data to check which fields are being updated
    update_data = syllabus_update.model_dump(exclude_unset=True)
    
    # Determine state_id to validate
    # If state_id is in update_data, it's being explicitly set (could be None)
    # Otherwise, use existing value
    if 'state_id' in update_data:
        state_id_to_validate = update_data['state_id']
    else:
        state_id_to_validate = existing_syllabus.state_id
    
    # Validate state_id based on board type
    if board.state_id is not None:
        # Board is state-specific
        if state_id_to_validate != board.state_id:
            raise HTTPException(
                status_code=400,
                detail=f"Board '{board.name}' is state-specific. Syllabus state_id must match board's state_id ({board.state_id})"
            )
        if state_id_to_validate:
            state = state_service.get_state_by_id(db, state_id_to_validate)
            if not state:
                raise HTTPException(status_code=404, detail="State not found")
    else:
        # Board is national
        if state_id_to_validate is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Board '{board.name}' is a national board. Syllabus state_id must be null"
            )
    
    updated = syllabus_service.update_syllabus(db, syllabus_id, syllabus_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return updated


@router.delete("/{syllabus_id}", status_code=204)
def delete_syllabus(syllabus_id: int, db: Session = Depends(get_db)):
    success = syllabus_service.delete_syllabus(db, syllabus_id)
    if not success:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return None


from pydantic import BaseModel, ConfigDict
from typing import Optional


class SyllabusCreate(BaseModel):
    board_id: int
    state_id: Optional[int] = None
    name: str
    academic_year: Optional[str] = None


class SyllabusUpdate(BaseModel):
    board_id: Optional[int] = None
    state_id: Optional[int] = None
    name: Optional[str] = None
    academic_year: Optional[str] = None


class SyllabusResponse(BaseModel):
    id: int
    board_id: int
    state_id: Optional[int] = None
    name: str
    academic_year: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


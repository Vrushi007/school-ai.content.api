from pydantic import BaseModel, ConfigDict
from typing import Optional


class BoardCreate(BaseModel):
    name: str
    description: str | None = None
    state_id: Optional[int] = None


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state_id: Optional[int] = None


class BoardResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    state_id: Optional[int] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


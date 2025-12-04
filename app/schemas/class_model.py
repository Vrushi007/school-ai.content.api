from pydantic import BaseModel, ConfigDict
from typing import Optional


class ClassCreate(BaseModel):
    syllabus_id: int
    name: str
    display_order: int = 0


class ClassUpdate(BaseModel):
    syllabus_id: Optional[int] = None
    name: Optional[str] = None
    display_order: Optional[int] = None


class ClassResponse(BaseModel):
    id: int
    syllabus_id: int
    name: str
    display_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


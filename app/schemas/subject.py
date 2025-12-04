from pydantic import BaseModel, ConfigDict
from typing import Optional


class SubjectCreate(BaseModel):
    class_id: int
    name: str


class SubjectUpdate(BaseModel):
    class_id: Optional[int] = None
    name: Optional[str] = None


class SubjectResponse(BaseModel):
    id: int
    class_id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


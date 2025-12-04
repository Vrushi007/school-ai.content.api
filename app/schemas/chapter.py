from pydantic import BaseModel, ConfigDict
from typing import Optional


class ChapterCreate(BaseModel):
    subject_id: int
    title: str
    description: Optional[str] = None
    chapter_number: int


class ChapterUpdate(BaseModel):
    subject_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    chapter_number: Optional[int] = None


class ChapterResponse(BaseModel):
    id: int
    subject_id: int
    title: str
    description: Optional[str] = None
    chapter_number: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


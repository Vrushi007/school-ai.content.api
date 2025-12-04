from pydantic import BaseModel, ConfigDict
from typing import Optional


class SessionCreate(BaseModel):
    chapter_id: int
    session_number: int
    title: str
    summary: Optional[str] = None
    duration: Optional[str] = None


class SessionUpdate(BaseModel):
    chapter_id: Optional[int] = None
    session_number: Optional[int] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    duration: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    chapter_id: int
    session_number: int
    title: str
    summary: Optional[str] = None
    duration: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


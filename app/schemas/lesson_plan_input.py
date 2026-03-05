from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LessonPlanRequest(BaseModel):
    board_id: int
    class_id: int
    subject_id: int
    chapter_id: int
    planned_sessions: int


class LessonPlanInputBase(BaseModel):
    board_id: int
    class_id: int
    subject_id: int
    chapter_id: int
    planned_sessions: int
    created_by_user_id: Optional[int] = None
    input_hash: str


class LessonPlanInputCreate(LessonPlanInputBase):
    pass


class LessonPlanInputResponse(LessonPlanInputBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

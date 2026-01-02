from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class LessonPlanGenerateRequest(BaseModel):
    board_name: str
    state_name: Optional[str] = None
    class_name: str
    subject_name: str
    chapter_title: str


class LessonPlanGenerateResponse(BaseModel):
    sessions: List[Dict[str, Any]]


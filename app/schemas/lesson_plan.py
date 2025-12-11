from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class LessonPlanGenerateRequest(BaseModel):
    board_name: str
    state_name: Optional[str] = None
    class_name: str
    subject_name: str
    chapter_title: str
    key_points: List[Dict[str, Any]]


class LessonPlanGenerateResponse(BaseModel):
    sessions: List[Dict[str, Any]]
    session_key_point_mapping: Dict[int, List[int]]  # session_number -> key_point_ids


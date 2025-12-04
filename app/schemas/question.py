from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List


class QuestionCreate(BaseModel):
    chapter_id: int
    question_text: str
    question_type: str
    difficulty: str
    marks: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None


class QuestionUpdate(BaseModel):
    chapter_id: Optional[int] = None
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[str] = None
    marks: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None


class QuestionResponse(BaseModel):
    id: int
    chapter_id: int
    question_text: str
    question_type: str
    difficulty: str
    marks: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionBulkCreate(BaseModel):
    chapter_id: int
    questions: List[QuestionCreate]


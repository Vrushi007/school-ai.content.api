from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LessonPlanOutputBase(BaseModel):
    input_id: int
    response_json: dict
    model_version: Optional[str] = None
    prompt_version: Optional[str] = None


class LessonPlanOutputCreate(LessonPlanOutputBase):
    pass


class LessonPlanOutputResponse(LessonPlanOutputBase):
    id: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)

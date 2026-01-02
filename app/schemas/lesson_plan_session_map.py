from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


class SessionData(BaseModel):
    """Single session from AI response"""
    session_map_id: Optional[int] = None
    session_number: int
    session_title: str
    kp_ids: List[str]
    summary: Optional[str] = None
    objectives: Optional[List[str]] = None
    is_detailed_content_available: Optional[bool] = False


class SessionMetadata(BaseModel):
    """Metadata from AI response"""
    chapter: str
    subject: str
    class_name: str = Field(alias="class")
    total_sessions: int
    total_kps: int

    model_config = ConfigDict(populate_by_name=True)


class GroupKpsData(BaseModel):
    """Data portion of AI response"""
    sessions: List[SessionData]
    metadata: SessionMetadata


class GroupKpsResponse(BaseModel):
    """Response from group-kps-into-sessions endpoint"""
    from_cache: bool
    sessions: List[SessionData]
    metadata: SessionMetadata
    success: bool


class LessonPlanSessionMapBase(BaseModel):
    """Base schema for session map"""
    input_id: int
    session_number: int
    session_title: str
    kp_ids: List[str]
    version: Optional[str] = None
    is_active: bool = True


class LessonPlanSessionMapCreate(LessonPlanSessionMapBase):
    """Schema for creating a session map entry"""
    pass


class LessonPlanSessionMapResponse(LessonPlanSessionMapBase):
    """Schema for session map response"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

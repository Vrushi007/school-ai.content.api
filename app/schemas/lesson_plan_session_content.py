from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class SessionSummaryKP(BaseModel):
    """Key point structure for session summary request"""
    kp_id: str
    title: str
    difficulty: str
    cognitive_level: str


class SessionDetailedRequest(BaseModel):
    """Request to get detailed session content"""
    session_id: int


class SessionDetailedData(BaseModel):
    """Data portion of detailed session response"""
    session_id: int
    content: Dict[str, Any]


class SessionDetailedResponse(BaseModel):
    """Response from get-session-detailed endpoint"""
    success: bool
    from_cache: bool
    data: SessionDetailedData


class SessionSummaryRequest(BaseModel):
    """Request to generate session summary"""
    session_map_id: int


class SessionSummaryMetadata(BaseModel):
    """Metadata from AI response"""
    board: str
    chapter: str
    class_name: str = Field(alias="class")
    subject: str
    session_title: str
    total_kps: int

    model_config = ConfigDict(populate_by_name=True)


class SessionSummaryData(BaseModel):
    """Data portion of session summary response"""
    summary: str
    objectives: List[str]
    metadata: SessionSummaryMetadata


class SessionSummaryAIResponse(BaseModel):
    """Response from AI service"""
    success: bool
    data: SessionSummaryData
    message: str
    error: Optional[str] = None


class SessionSummaryResponse(BaseModel):
    """Response from generate-session-summary endpoint"""
    success: bool
    session_number: int
    session_title: str
    summary: str
    objectives: List[str]


class LessonPlanSessionContentBase(BaseModel):
    """Base schema for session content"""
    session_id: int
    session_summary: Dict[str, Any]
    session_content: Optional[Dict[str, Any]] = None
    version: Optional[str] = None


class LessonPlanSessionContentCreate(LessonPlanSessionContentBase):
    """Schema for creating session content"""
    pass


class LessonPlanSessionContentResponse(LessonPlanSessionContentBase):
    """Schema for session content response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

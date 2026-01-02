from pydantic import BaseModel, Field, model_serializer, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.key_point import CognitiveLevel, DifficultyLevel, SkillIntent


class KeyPointCreate(BaseModel):
    code: str = Field(..., max_length=100)
    title: str
    section: Optional[str] = None
    chapter_id: int
    difficulty_level: DifficultyLevel
    cognitive_level: CognitiveLevel
    skill_intent: SkillIntent
    content: Dict[str, Any]  # OpenAI-generated content stored in key_point_content table
    model_version: Optional[str] = Field(None, max_length=50)
    prompt_version: Optional[str] = Field(None, max_length=50)
    
    model_config = ConfigDict(protected_namespaces=())


class KeyPointUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = None
    section: Optional[str] = None
    chapter_id: Optional[int] = None
    difficulty_level: Optional[DifficultyLevel] = None
    cognitive_level: Optional[CognitiveLevel] = None
    skill_intent: Optional[SkillIntent] = None


class KeyPointResponse(BaseModel):
    id: int
    code: str
    title: str
    section: Optional[str]
    chapter_id: int
    difficulty_level: DifficultyLevel
    cognitive_level: CognitiveLevel
    skill_intent: SkillIntent
    created_at: datetime
    content: Optional[Dict[str, Any]] = None  # Latest active content
    
    model_config = {"from_attributes": True}
    
    @model_serializer
    def serialize_model(self):
        data = {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'section': self.section,
            'chapter_id': self.chapter_id,
            'difficulty_level': self.difficulty_level,
            'cognitive_level': self.cognitive_level,
            'skill_intent': self.skill_intent,
            'created_at': self.created_at,
            'content': self.content
        }
        return data

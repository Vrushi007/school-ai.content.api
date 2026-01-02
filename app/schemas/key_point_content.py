from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any


class KeyPointContentCreate(BaseModel):
    key_point_id: int
    content: Dict[str, Any]
    model_version: Optional[str] = Field(None, max_length=50)
    prompt_version: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    
    model_config = ConfigDict(protected_namespaces=())


class KeyPointContentUpdate(BaseModel):
    content: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = Field(None, max_length=50)
    prompt_version: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(protected_namespaces=())


class KeyPointContentResponse(BaseModel):
    id: int
    key_point_id: int
    content: Dict[str, Any]
    model_version: Optional[str]
    prompt_version: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

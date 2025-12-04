from pydantic import BaseModel, ConfigDict
from typing import Optional, Any


class SessionDetailsCreate(BaseModel):
    session_id: int
    introduction: Optional[dict[str, Any]] = None
    main_content: Optional[dict[str, Any]] = None
    activities: Optional[dict[str, Any]] = None
    assessment: Optional[dict[str, Any]] = None
    resources: Optional[dict[str, Any]] = None
    differentiation: Optional[dict[str, Any]] = None


class SessionDetailsUpdate(BaseModel):
    introduction: Optional[dict[str, Any]] = None
    main_content: Optional[dict[str, Any]] = None
    activities: Optional[dict[str, Any]] = None
    assessment: Optional[dict[str, Any]] = None
    resources: Optional[dict[str, Any]] = None
    differentiation: Optional[dict[str, Any]] = None


class SessionDetailsResponse(BaseModel):
    id: int
    session_id: int
    introduction: Optional[dict[str, Any]] = None
    main_content: Optional[dict[str, Any]] = None
    activities: Optional[dict[str, Any]] = None
    assessment: Optional[dict[str, Any]] = None
    resources: Optional[dict[str, Any]] = None
    differentiation: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


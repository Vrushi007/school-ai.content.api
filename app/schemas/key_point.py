from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List


class KeyPointCreate(BaseModel):
    chapter_id: int
    point: str
    order: int = 0
    metadata_json: Optional[dict[str, Any]] = None


class KeyPointUpdate(BaseModel):
    chapter_id: Optional[int] = None
    point: Optional[str] = None
    order: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None


class KeyPointResponse(BaseModel):
    id: int
    chapter_id: int
    point: str
    order: int
    metadata_json: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class KeyPointBulkCreate(BaseModel):
    chapter_id: int
    key_points: List[KeyPointCreate]


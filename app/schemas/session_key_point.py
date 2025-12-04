from pydantic import BaseModel, ConfigDict
from typing import List


class SessionKeyPointCreate(BaseModel):
    session_id: int
    key_point_id: int
    order: int = 0


class SessionKeyPointResponse(BaseModel):
    id: int
    session_id: int
    key_point_id: int
    order: int

    model_config = ConfigDict(from_attributes=True)


class SessionKeyPointBulkCreate(BaseModel):
    session_id: int
    key_point_ids: List[int]


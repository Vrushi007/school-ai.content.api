from pydantic import BaseModel, ConfigDict


class StateCreate(BaseModel):
    name: str
    code: str


class StateResponse(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


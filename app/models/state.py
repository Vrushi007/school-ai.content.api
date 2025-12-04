from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true", index=True)


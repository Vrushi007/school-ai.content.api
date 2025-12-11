from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true", index=True)

    # Relationships
    state = relationship("State", backref="boards")
    classes = relationship("Class", back_populates="board", cascade="all, delete-orphan")


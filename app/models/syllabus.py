from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Syllabus(Base):
    __tablename__ = "syllabus"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    academic_year = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true", index=True)

    # Relationships
    board = relationship("Board", backref="syllabi")
    state = relationship("State", backref="syllabi")
    classes = relationship("Class", back_populates="syllabus", cascade="all, delete-orphan")


from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LessonPlanInput(Base):
    __tablename__ = "lesson_plan_inputs"

    id = Column(BigInteger, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    planned_sessions = Column(Integer, nullable=False)
    input_hash = Column(Text, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    board = relationship("Board")
    class_ = relationship("Class")
    subject = relationship("Subject")
    chapter = relationship("Chapter")
    session_maps = relationship("LessonPlanSessionMap", back_populates="lesson_input", cascade="all, delete-orphan")

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LessonPlanSessionContent(Base):
    __tablename__ = "lesson_plan_session_content"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("lesson_plan_session_map.id"), nullable=False, index=True)
    session_summary = Column(JSONB, nullable=False)
    session_content = Column(JSONB, nullable=True)
    version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    session_map = relationship("LessonPlanSessionMap")

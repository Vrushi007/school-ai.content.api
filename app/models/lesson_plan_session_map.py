from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LessonPlanSessionMap(Base):
    __tablename__ = "lesson_plan_session_map"

    id = Column(BigInteger, primary_key=True, index=True)
    input_id = Column(BigInteger, ForeignKey("lesson_plan_inputs.id"), nullable=False, index=True)
    session_number = Column(Integer, nullable=False)
    session_title = Column(Text, nullable=False)
    kp_ids = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    version = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    lesson_input = relationship("LessonPlanInput", back_populates="session_maps")

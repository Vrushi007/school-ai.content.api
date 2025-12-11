from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LessonPlanOutput(Base):
    __tablename__ = "lesson_plan_outputs"

    id = Column(BigInteger, primary_key=True, index=True)
    input_id = Column(BigInteger, ForeignKey("lesson_plan_inputs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    response_json = Column(JSONB, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    model_version = Column(Text, nullable=True)
    prompt_version = Column(Text, nullable=True)

    # Relationships
    input = relationship("LessonPlanInput", back_populates="output")

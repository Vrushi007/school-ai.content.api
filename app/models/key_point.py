from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, TIMESTAMP, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


# Python Enums for type safety
class CognitiveLevel(str, enum.Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class DifficultyLevel(str, enum.Enum):
    VERY_EASY = "Very_Easy"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    VERY_HARD = "Very_Hard"


class SkillIntent(str, enum.Enum):
    RECALL = "Recall"
    EXPLAIN = "Explain"
    COMPUTE = "Compute"
    INTERPRET = "Interpret"
    REASON = "Reason"
    PROBLEM_SOLVING = "Problem_Solving"
    CRITICAL_THINKING = "Critical_Thinking"


class KeyPoint(Base):
    __tablename__ = "key_points"

    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    section = Column(Text, nullable=True)
    chapter_id = Column(BigInteger, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    difficulty_level = Column(SQLAlchemyEnum(DifficultyLevel, name="difficulty_level_enum", create_type=False), nullable=False)
    cognitive_level = Column(SQLAlchemyEnum(CognitiveLevel, name="cognitive_level_enum", create_type=False), nullable=False)
    skill_intent = Column(SQLAlchemyEnum(SkillIntent, name="skill_intent_enum", create_type=False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, server_default="now()")

    # Relationships
    chapter = relationship("Chapter", back_populates="key_points")
    key_point_contents = relationship("KeyPointContent", back_populates="key_point", cascade="all, delete-orphan")


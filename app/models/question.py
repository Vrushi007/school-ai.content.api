from sqlalchemy import Column, Integer, ForeignKey, Text, String, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # MCQ, Short Answer, Long Answer, etc.
    difficulty = Column(String(20), nullable=False)  # Easy, Medium, Hard
    marks = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    # Relationships
    chapter = relationship("Chapter", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


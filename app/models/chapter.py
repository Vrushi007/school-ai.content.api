from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    chapter_number = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true", index=True)

    # Relationships
    subject = relationship("Subject", back_populates="chapters")
    key_points = relationship("KeyPoint", back_populates="chapter", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="chapter", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="chapter", cascade="all, delete-orphan")


from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    session_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    duration = Column(String(50), nullable=True)

    # Relationships
    chapter = relationship("Chapter", back_populates="sessions")
    session_key_points = relationship("SessionKeyPoint", back_populates="session", cascade="all, delete-orphan")
    session_details = relationship("SessionDetails", back_populates="session", uselist=False, cascade="all, delete-orphan")


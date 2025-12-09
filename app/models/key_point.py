from sqlalchemy import Column, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class KeyPoint(Base):
    __tablename__ = "key_points"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    point = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    metadata_json = Column(JSON, nullable=True)

    # Relationships
    chapter = relationship("Chapter", back_populates="key_points")


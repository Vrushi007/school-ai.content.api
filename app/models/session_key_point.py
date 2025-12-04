from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class SessionKeyPoint(Base):
    __tablename__ = "session_key_points"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    key_point_id = Column(Integer, ForeignKey("key_points.id"), nullable=False, index=True)
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    session = relationship("Session", back_populates="session_key_points")
    key_point = relationship("KeyPoint", back_populates="session_key_points")


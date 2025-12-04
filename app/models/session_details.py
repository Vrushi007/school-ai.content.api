from sqlalchemy import Column, Integer, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class SessionDetails(Base):
    __tablename__ = "session_details"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, unique=True, index=True)
    introduction = Column(JSON, nullable=True)
    main_content = Column(JSON, nullable=True)
    activities = Column(JSON, nullable=True)
    assessment = Column(JSON, nullable=True)
    resources = Column(JSON, nullable=True)
    differentiation = Column(JSON, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="session_details")


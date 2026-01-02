from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.base import Base


class KeyPointContent(Base):
    """
    Stores the full OpenAI-generated knowledge point content as JSONB.
    
    Why separate from key_points?
    - key_points table maintains stable identity & classification (code, title, difficulty, etc.)
    - key_point_content stores rich, evolving pedagogical content from OpenAI
    - Supports versioning: multiple content versions can exist for the same key_point
    - Allows AI-generated content to evolve without affecting core metadata
    - JSONB enables flexible schema for OpenAI payloads (explanations, examples, grading rubrics, etc.)
    """
    __tablename__ = "key_point_content"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    key_point_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("key_points.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        server_default="now()"
    )

    # Relationships
    # Note: We add the relationship only on this side to avoid modifying KeyPoint model
    key_point: Mapped["KeyPoint"] = relationship("KeyPoint", back_populates="key_point_contents")

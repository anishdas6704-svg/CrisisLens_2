"""
CrisisLens - Crisis Update ORM Model
Stores raw text updates + AI-extracted structured information.
Each update is linked to a crisis and optionally to a specific entity.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, ForeignKey, JSON, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.database import Base


class UpdateSource(str, enum.Enum):
    MANUAL = "manual"         # Entered by crisis manager
    RADIO = "radio"           # Transcribed radio report
    SENSOR = "sensor"         # Automated sensor feed
    SOCIAL = "social_media"   # Social media scrape
    AGENCY = "agency"         # Official agency feed
    AI_INFERRED = "ai_inferred"


class ConflictStatus(str, enum.Enum):
    NONE = "none"             # No conflict detected
    CONFLICT = "conflict"     # Contradicts previous state
    RESOLVED = "resolved"     # Conflict manually resolved


class CrisisUpdate(Base):
    __tablename__ = "crisis_updates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    crisis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crises.id", ondelete="CASCADE"), nullable=False
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True
    )

    # Raw input text from user / source
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Source of the update
    source: Mapped[UpdateSource] = mapped_column(
        SAEnum(UpdateSource), nullable=False, default=UpdateSource.MANUAL
    )
    reporter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # AI-extracted structured data (Gemini output)
    ai_extracted: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Example: {
    #   "entity_name": "Highway 12",
    #   "entity_type": "road",
    #   "new_status": "closed",
    #   "reason": "fire activity",
    #   "confidence": 0.95
    # }

    # Previous state before this update (for change detection)
    previous_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_state: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Change detection
    change_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Conflict detection
    conflict_status: Mapped[ConflictStatus] = mapped_column(
        SAEnum(ConflictStatus), nullable=False, default=ConflictStatus.NONE
    )
    conflict_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Gemini processing metadata
    gemini_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    crisis: Mapped["Crisis"] = relationship(back_populates="updates")  # noqa: F821
    entity: Mapped["Entity | None"] = relationship(back_populates="updates")  # noqa: F821

    def __repr__(self) -> str:
        return f"<CrisisUpdate id={self.id} crisis_id={self.crisis_id} change={self.change_detected}>"

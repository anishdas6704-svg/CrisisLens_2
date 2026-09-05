"""
CrisisLens - Entity ORM Model
Entities are trackable objects within a crisis:
  - Roads (Highway 12)
  - Shelters (Riverside High School)
  - Resources (Fire Engine #4)
  - Zones (Evacuation Zone A)
  - Personnel (Captain Rodriguez)
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.database import Base


class EntityType(str, enum.Enum):
    ROAD = "road"
    SHELTER = "shelter"
    RESOURCE = "resource"
    EVACUATION_ZONE = "evacuation_zone"
    PERSONNEL = "personnel"
    HOSPITAL = "hospital"
    UTILITY = "utility"
    OTHER = "other"


class EntityStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    OPERATIONAL = "operational"
    DAMAGED = "damaged"
    UNKNOWN = "unknown"


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    crisis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crises.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(
        SAEnum(EntityType), nullable=False, default=EntityType.OTHER
    )
    status: Mapped[EntityStatus] = mapped_column(
        SAEnum(EntityStatus), nullable=False, default=EntityStatus.UNKNOWN
    )
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    capacity: Mapped[int | None] = mapped_column(nullable=True)
    current_occupancy: Mapped[int | None] = mapped_column(nullable=True)

    # Flexible JSON metadata (e.g., {"direction": "northbound", "lanes": 2})
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    last_known_state: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    crisis: Mapped["Crisis"] = relationship(back_populates="entities")  # noqa: F821
    updates: Mapped[list["CrisisUpdate"]] = relationship(back_populates="entity")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Entity id={self.id} name={self.name} type={self.entity_type} status={self.status}>"

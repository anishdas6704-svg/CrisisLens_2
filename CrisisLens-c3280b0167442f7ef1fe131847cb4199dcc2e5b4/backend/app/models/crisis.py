"""
CrisisLens - Crisis / Incident ORM Model
Represents a crisis event (e.g., wildfire, flood, earthquake)
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.database import Base


class CrisisStatus(str, enum.Enum):
    ACTIVE = "active"
    MONITORING = "monitoring"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class CrisisSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrisisType(str, enum.Enum):
    WILDFIRE = "wildfire"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    CHEMICAL_SPILL = "chemical_spill"
    INFRASTRUCTURE = "infrastructure"
    CIVIL_UNREST = "civil_unrest"
    OTHER = "other"


class Crisis(Base):
    __tablename__ = "crises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    crisis_type: Mapped[CrisisType] = mapped_column(
        SAEnum(CrisisType), nullable=False, default=CrisisType.OTHER
    )
    status: Mapped[CrisisStatus] = mapped_column(
        SAEnum(CrisisStatus), nullable=False, default=CrisisStatus.ACTIVE
    )
    severity: Mapped[CrisisSeverity] = mapped_column(
        SAEnum(CrisisSeverity), nullable=False, default=CrisisSeverity.MEDIUM
    )
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    entities: Mapped[list["Entity"]] = relationship(back_populates="crisis", cascade="all, delete-orphan")  # noqa: F821
    updates: Mapped[list["CrisisUpdate"]] = relationship(back_populates="crisis", cascade="all, delete-orphan")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Crisis id={self.id} name={self.name} status={self.status}>"

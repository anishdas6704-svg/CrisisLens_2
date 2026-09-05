import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Crisis(Base):
    __tablename__ = "crises"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active", index=True)  # active, resolved, monitoring
    description = Column(Text, nullable=True)
    location = Column(String, default="Kolkata, West Bengal")
    latitude = Column(Float, default=22.5726)
    longitude = Column(Float, default=88.3639)
    started_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)

    updates = relationship("CrisisUpdate", back_populates="crisis", cascade="all, delete-orphan", order_by="desc(CrisisUpdate.created_at)")
    entities = relationship("CrisisEntity", back_populates="crisis", cascade="all, delete-orphan")


class CrisisUpdate(Base):
    __tablename__ = "crisis_updates"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    crisis_id = Column(String, ForeignKey("crises.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    source = Column(String, default="manual")  # manual, radio, sensor, social_media, agency
    change_detected = Column(Boolean, default=False)
    conflict_status = Column(String, default="none")  # none, conflict, resolved
    ai_extracted = Column(JSON, default=dict)
    created_at = Column(DateTime, default=get_utc_now, index=True)

    crisis = relationship("Crisis", back_populates="updates")


class CrisisEntity(Base):
    __tablename__ = "crisis_entities"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    crisis_id = Column(String, ForeignKey("crises.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, default="other")  # flood, wildfire, earthquake, infrastructure, shelter, rescue, other
    status = Column(String, default="active")
    details = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=get_utc_now)

    crisis = relationship("Crisis", back_populates="entities")

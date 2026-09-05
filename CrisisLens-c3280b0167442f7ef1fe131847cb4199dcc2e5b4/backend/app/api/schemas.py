"""
CrisisLens - Pydantic Schemas (Request/Response models)
"""
import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.models.crisis import CrisisStatus, CrisisSeverity, CrisisType
from app.models.entity import EntityType, EntityStatus
from app.models.update import UpdateSource, ConflictStatus


# ─── Crisis Schemas ───────────────────────────────────────────────────────────

class CrisisCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    crisis_type: CrisisType = CrisisType.OTHER
    status: CrisisStatus = CrisisStatus.ACTIVE
    severity: CrisisSeverity = CrisisSeverity.MEDIUM
    location: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    started_at: Optional[datetime] = None


class CrisisUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[CrisisStatus] = None
    severity: Optional[CrisisSeverity] = None
    location: Optional[str] = None
    description: Optional[str] = None


class CrisisResponse(BaseModel):
    id: uuid.UUID
    name: str
    crisis_type: CrisisType
    status: CrisisStatus
    severity: CrisisSeverity
    location: Optional[str]
    description: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    started_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Entity Schemas ───────────────────────────────────────────────────────────

class EntityResponse(BaseModel):
    id: uuid.UUID
    crisis_id: uuid.UUID
    name: str
    entity_type: EntityType
    status: EntityStatus
    location: Optional[str]
    capacity: Optional[int]
    current_occupancy: Optional[int]
    extra_data: Optional[dict]
    last_known_state: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Update Processing Schemas ────────────────────────────────────────────────

class ProcessUpdateRequest(BaseModel):
    raw_text: str = Field(..., min_length=5, description="Raw crisis update text")
    source: UpdateSource = UpdateSource.MANUAL
    reporter_name: Optional[str] = None


class ProcessUpdateResponse(BaseModel):
    update_id: str
    crisis_id: str
    entity: dict
    ai_extracted: dict
    change_detected: bool
    change_summary: Optional[str]
    conflict: dict
    previous_state: Optional[str]
    new_state: str
    processed_at: str


class CrisisUpdateResponse(BaseModel):
    id: uuid.UUID
    crisis_id: uuid.UUID
    entity_id: Optional[uuid.UUID]
    raw_text: str
    source: UpdateSource
    reporter_name: Optional[str]
    ai_extracted: Optional[dict]
    previous_state: Optional[str]
    new_state: Optional[str]
    change_detected: bool
    change_summary: Optional[str]
    conflict_status: ConflictStatus
    conflict_detail: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard Schema ─────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_crises: int
    active_crises: int
    total_entities: int
    total_updates: int
    conflicts_pending: int
    recent_updates: list[Any]

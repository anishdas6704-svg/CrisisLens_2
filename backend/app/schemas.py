from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field

# Base schemas
class CrisisBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    location: Optional[str] = "Kolkata, West Bengal"
    latitude: Optional[float] = 22.5726
    longitude: Optional[float] = 88.3639

class CrisisCreate(CrisisBase):
    id: Optional[str] = None

class CrisisResponse(CrisisBase):
    id: str
    started_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateProcessRequest(BaseModel):
    raw_text: str = Field(..., min_length=1, description="Raw crisis update text")
    source: str = Field(default="manual", description="Source of update (manual, radio, sensor, social_media, agency)")


class AIExtractedData(BaseModel):
    entity_type: str = "other"  # flood, wildfire, earthquake, infrastructure, shelter, rescue, other
    confidence: float = 0.94
    severity: str = "medium"    # critical, high, medium, low, info
    action_recommended: Optional[str] = None
    entities_found: List[str] = []
    summary: Optional[str] = None


class EntityInfo(BaseModel):
    name: str
    type: Optional[str] = "other"
    status: Optional[str] = None


class ConflictInfo(BaseModel):
    detected: bool = False
    details: Optional[str] = None


class CrisisUpdateResponse(BaseModel):
    id: str
    crisis_id: str
    raw_text: str
    source: str
    change_detected: bool
    conflict_status: str
    ai_extracted: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessedUpdateResult(BaseModel):
    id: str
    crisis_id: str
    raw_text: str
    source: str
    entity: Optional[EntityInfo] = None
    change_detected: bool = False
    conflict: Optional[ConflictInfo] = None
    ai_extracted: Dict[str, Any]
    created_at: datetime


class DashboardSummary(BaseModel):
    total_crises: int
    active_crises: int
    total_entities: int
    total_updates: int
    conflicts_pending: int
    recent_updates: List[CrisisUpdateResponse]

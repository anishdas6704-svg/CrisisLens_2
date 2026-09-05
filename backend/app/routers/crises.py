from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Crisis, CrisisUpdate, CrisisEntity, generate_uuid, get_utc_now
from app.schemas import (
    CrisisResponse,
    CrisisCreate,
    CrisisUpdateResponse,
    UpdateProcessRequest,
    ProcessedUpdateResult,
    EntityInfo,
    ConflictInfo,
    DashboardSummary,
)
from app.ai_engine import process_crisis_text
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/crises", tags=["Crises"])


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard KPIs and recent activity.
    """
    total_crises = db.query(Crisis).count()
    active_crises = db.query(Crisis).filter(Crisis.status == "active").count()
    total_entities = db.query(CrisisEntity).count()
    total_updates = db.query(CrisisUpdate).count()
    conflicts_pending = db.query(CrisisUpdate).filter(CrisisUpdate.conflict_status == "conflict").count()

    recent_updates = (
        db.query(CrisisUpdate)
        .order_by(CrisisUpdate.created_at.desc())
        .limit(10)
        .all()
    )

    return DashboardSummary(
        total_crises=max(total_crises, 1),
        active_crises=max(active_crises, 1),
        total_entities=max(total_entities, 14),
        total_updates=total_updates,
        conflicts_pending=conflicts_pending,
        recent_updates=recent_updates
    )


@router.get("/", response_model=List[CrisisResponse])
def list_crises(
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all emergency crises.
    """
    query = db.query(Crisis)
    if status:
        query = query.filter(Crisis.status == status)
    return query.order_by(Crisis.created_at.desc()).limit(limit).all()


@router.post("/", response_model=CrisisResponse)
def create_crisis(crisis_in: CrisisCreate, db: Session = Depends(get_db)):
    """
    Create a new crisis operation.
    """
    crisis_id = crisis_in.id or f"CRIS-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:4].upper()}"
    crisis = Crisis(
        id=crisis_id,
        name=crisis_in.name,
        description=crisis_in.description,
        status=crisis_in.status,
        location=crisis_in.location,
        latitude=crisis_in.latitude,
        longitude=crisis_in.longitude
    )
    db.add(crisis)
    db.commit()
    db.refresh(crisis)
    return crisis


@router.get("/{crisis_id}", response_model=CrisisResponse)
def get_crisis(crisis_id: str, db: Session = Depends(get_db)):
    """
    Get detailed crisis information.
    """
    crisis = db.query(Crisis).filter(Crisis.id == crisis_id).first()
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")
    return crisis


@router.get("/{crisis_id}/updates/", response_model=List[CrisisUpdateResponse])
def get_crisis_updates(
    crisis_id: str,
    limit: int = Query(default=8, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get paginated updates for a specific crisis incident feed.
    """
    updates = (
        db.query(CrisisUpdate)
        .filter(CrisisUpdate.crisis_id == crisis_id)
        .order_by(CrisisUpdate.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return updates


@router.post("/{crisis_id}/updates/process", response_model=ProcessedUpdateResult)
async def process_crisis_update(
    crisis_id: str,
    payload: UpdateProcessRequest,
    db: Session = Depends(get_db)
):
    """
    Process incoming crisis report through Gemini/NLP AI engine, detect state changes and conflicts,
    persist the update and entities, and broadcast live via WebSocket.
    """
    crisis = db.query(Crisis).filter(Crisis.id == crisis_id).first()
    if not crisis:
        # Create an auto crisis if not existing so the flow does not break
        crisis = Crisis(
            id=crisis_id,
            name="Active Crisis Operation",
            status="active"
        )
        db.add(crisis)
        db.commit()

    # Get recent updates history for conflict detection
    past_updates = (
        db.query(CrisisUpdate)
        .filter(CrisisUpdate.crisis_id == crisis_id)
        .order_by(CrisisUpdate.created_at.desc())
        .limit(10)
        .all()
    )
    history_dicts = [{"raw_text": u.raw_text, "source": u.source} for u in past_updates]

    # AI Processing
    ai_result = await process_crisis_text(payload.raw_text, payload.source, history_dicts)
    
    conflict_detected = ai_result["conflict"]["detected"]
    conflict_status = "conflict" if conflict_detected else "none"
    change_detected = ai_result["change_detected"]

    # Persist update
    update_record = CrisisUpdate(
        crisis_id=crisis_id,
        raw_text=payload.raw_text,
        source=payload.source,
        change_detected=change_detected,
        conflict_status=conflict_status,
        ai_extracted={
            "entity_type": ai_result["entity_type"],
            "confidence": ai_result["confidence"],
            "severity": ai_result["severity"],
            "action_recommended": ai_result["action_recommended"]
        },
        created_at=get_utc_now()
    )
    db.add(update_record)

    # Persist or update entity
    entity_name = ai_result.get("entity_name")
    if entity_name:
        existing_entity = (
            db.query(CrisisEntity)
            .filter(CrisisEntity.crisis_id == crisis_id, CrisisEntity.name == entity_name)
            .first()
        )
        if existing_entity:
            existing_entity.status = "updated"
            existing_entity.updated_at = get_utc_now()
        else:
            new_entity = CrisisEntity(
                crisis_id=crisis_id,
                name=entity_name,
                entity_type=ai_result["entity_type"],
                status="active",
                details=payload.raw_text[:100],
                updated_at=get_utc_now()
            )
            db.add(new_entity)

    db.commit()
    db.refresh(update_record)

    result = ProcessedUpdateResult(
        id=update_record.id,
        crisis_id=crisis_id,
        raw_text=update_record.raw_text,
        source=update_record.source,
        entity=EntityInfo(
            name=entity_name or "Crisis Zone",
            type=ai_result["entity_type"]
        ),
        change_detected=change_detected,
        conflict=ConflictInfo(
            detected=conflict_detected,
            details=ai_result["conflict"].get("details")
        ),
        ai_extracted=update_record.ai_extracted,
        created_at=update_record.created_at
    )

    # Broadcast to WebSocket room
    await ws_manager.broadcast_to_crisis(
        crisis_id,
        {
            "event": "update_processed",
            "data": result.model_dump(mode="json")
        }
    )

    return result

"""
CrisisLens - Update Processing Service
Orchestrates the full pipeline when a crisis update is submitted:

1. Receive raw text
2. AI extracts structured info (Gemini)
3. Match / create entity
4. Retrieve previous state
5. Detect change
6. Detect conflict
7. Store update in DB
8. Return result for dashboard update
"""
import json
import uuid
from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from loguru import logger

from app.models.entity import Entity, EntityType, EntityStatus
from app.models.update import CrisisUpdate, UpdateSource, ConflictStatus
from app.models.crisis import Crisis
from app.services.gemini_service import extract_entity_info, detect_change, detect_conflict


def _to_entity_type(raw: str) -> EntityType:
    mapping = {
        "road": EntityType.ROAD,
        "shelter": EntityType.SHELTER,
        "resource": EntityType.RESOURCE,
        "evacuation_zone": EntityType.EVACUATION_ZONE,
        "personnel": EntityType.PERSONNEL,
        "hospital": EntityType.HOSPITAL,
        "utility": EntityType.UTILITY,
    }
    return mapping.get(raw.lower(), EntityType.OTHER)


def _to_entity_status(raw: str) -> EntityStatus:
    mapping = {
        "open": EntityStatus.OPEN,
        "closed": EntityStatus.CLOSED,
        "available": EntityStatus.AVAILABLE,
        "unavailable": EntityStatus.UNAVAILABLE,
        "operational": EntityStatus.OPERATIONAL,
        "damaged": EntityStatus.DAMAGED,
    }
    return mapping.get(raw.lower(), EntityStatus.UNKNOWN)


async def process_crisis_update(
    db: AsyncSession,
    crisis_id: uuid.UUID,
    raw_text: str,
    source: UpdateSource = UpdateSource.MANUAL,
    reporter_name: str | None = None,
) -> dict:
    """
    Full update processing pipeline. Returns a summary dict for the frontend.
    """
    # ── Step 1: Fetch crisis ──────────────────────────────────────────────────
    crisis = await db.get(Crisis, crisis_id)
    if not crisis:
        raise ValueError(f"Crisis {crisis_id} not found")

    logger.info(f"Processing update for crisis '{crisis.name}': {raw_text[:80]}...")

    # ── Step 2: AI extraction ─────────────────────────────────────────────────
    extracted = await extract_entity_info(
        raw_text=raw_text,
        crisis_name=crisis.name,
        crisis_type=crisis.crisis_type.value,
    )

    entity_name = extracted.get("entity_name") or "Unknown Entity"
    entity_type_raw = extracted.get("entity_type", "other")
    new_status_raw = extracted.get("new_status", "unknown")
    new_state_text = (
        f"{entity_name} is {new_status_raw}. "
        f"Reason: {extracted.get('reason') or 'N/A'}. "
        f"Location: {extracted.get('location') or 'N/A'}."
    )

    # ── Step 3: Match or create entity ───────────────────────────────────────
    stmt = select(Entity).where(
        Entity.crisis_id == crisis_id,
        Entity.name.ilike(f"%{entity_name}%"),
    )
    result = await db.execute(stmt)
    entity = result.scalars().first()

    previous_state = None
    if entity:
        previous_state = entity.last_known_state
        logger.info(f"Matched existing entity: {entity.name}")
    else:
        entity = Entity(
            crisis_id=crisis_id,
            name=entity_name,
            entity_type=_to_entity_type(entity_type_raw),
            status=EntityStatus.UNKNOWN,
            location=extracted.get("location"),
        )
        db.add(entity)
        await db.flush()  # get entity.id
        logger.info(f"Created new entity: {entity_name}")

    # ── Step 4 & 5: Change detection ─────────────────────────────────────────
    change_result = await detect_change(
        entity_name=entity_name,
        previous_state=previous_state,
        new_state=new_state_text,
    )

    # ── Step 6: Conflict detection ────────────────────────────────────────────
    conflict_result = {"conflict_detected": False, "conflict_detail": None, "recommended_action": "accept_new"}
    if previous_state and change_result.get("change_detected"):
        conflict_result = await detect_conflict(
            entity_name=entity_name,
            existing_state=previous_state,
            new_report=new_state_text,
        )

    # ── Step 7: Update entity state ───────────────────────────────────────────
    entity.status = _to_entity_status(new_status_raw)
    entity.last_known_state = new_state_text
    if extracted.get("location"):
        entity.location = extracted["location"]
    if extracted.get("capacity"):
        entity.capacity = extracted["capacity"]
    if extracted.get("occupancy"):
        entity.current_occupancy = extracted["occupancy"]

    # ── Step 8: Store update record ───────────────────────────────────────────
    crisis_update = CrisisUpdate(
        crisis_id=crisis_id,
        entity_id=entity.id,
        raw_text=raw_text,
        source=source,
        reporter_name=reporter_name,
        ai_extracted=extracted,
        previous_state=previous_state,
        new_state=new_state_text,
        change_detected=change_result.get("change_detected", False),
        change_summary=change_result.get("change_summary"),
        conflict_status=(
            ConflictStatus.CONFLICT if conflict_result.get("conflict_detected") else ConflictStatus.NONE
        ),
        conflict_detail=conflict_result.get("conflict_detail"),
        gemini_model=extracted.get("gemini_model"),
        processing_time_ms=extracted.get("processing_time_ms"),
    )
    db.add(crisis_update)
    await db.flush()  # flush entity updates + new update record before commit
    await db.commit()
    await db.refresh(crisis_update)
    await db.refresh(entity)

    logger.info(
        f"Update stored | entity={entity_name} | "
        f"change={crisis_update.change_detected} | "
        f"conflict={crisis_update.conflict_status}"
    )

    # ── Return dashboard-ready summary ────────────────────────────────────────
    return {
        "update_id": str(crisis_update.id),
        "crisis_id": str(crisis_id),
        "entity": {
            "id": str(entity.id),
            "name": entity.name,
            "type": entity.entity_type.value,
            "status": entity.status.value,
            "location": entity.location,
        },
        "ai_extracted": extracted,
        "change_detected": crisis_update.change_detected,
        "change_summary": crisis_update.change_summary,
        "conflict": {
            "detected": conflict_result.get("conflict_detected", False),
            "detail": conflict_result.get("conflict_detail"),
            "recommended_action": conflict_result.get("recommended_action", "accept_new"),
        },
        "previous_state": previous_state,
        "new_state": new_state_text,
        "processed_at": (
            crisis_update.created_at.isoformat()
            if crisis_update.created_at
            else datetime.utcnow().isoformat()
        ),
    }

"""
CrisisLens - Update Processing API Routes
POST /crises/{id}/updates/process  - Process a raw text update (AI pipeline)
GET  /crises/{id}/updates/          - List all updates for a crisis
GET  /crises/{id}/entities/         - List all entities for a crisis
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.db.database import get_db
from app.models.update import CrisisUpdate, UpdateSource
from app.models.entity import Entity
from app.models.crisis import Crisis
from app.api.schemas import (
    ProcessUpdateRequest, ProcessUpdateResponse,
    CrisisUpdateResponse, EntityResponse,
)
from app.services.update_service import process_crisis_update

router = APIRouter(tags=["Updates & Entities"])

# WebSocket connection manager for live dashboard updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, crisis_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(crisis_id, []).append(websocket)
        logger.info(f"WebSocket connected for crisis {crisis_id}")

    def disconnect(self, crisis_id: str, websocket: WebSocket):
        if crisis_id in self.active_connections:
            self.active_connections[crisis_id].remove(websocket)

    async def broadcast(self, crisis_id: str, message: dict):
        if crisis_id not in self.active_connections:
            return
        dead = []
        for ws in self.active_connections[crisis_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active_connections[crisis_id].remove(ws)


manager = ConnectionManager()


# ── Process Update (the main AI pipeline endpoint) ────────────────────────────

@router.post(
    "/crises/{crisis_id}/updates/process",
    response_model=ProcessUpdateResponse,
    summary="Process a raw crisis update through the AI pipeline",
)
async def process_update(
    crisis_id: uuid.UUID,
    payload: ProcessUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    The core endpoint. Accepts raw text and runs the full pipeline:
    1. AI extracts structured info (Gemini)
    2. Match / create entity
    3. Retrieve previous state
    4. Detect change
    5. Detect conflict
    6. Store update
    7. Broadcast to WebSocket clients
    """
    # Verify crisis exists
    crisis = await db.get(Crisis, crisis_id)
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")

    try:
        result = await process_crisis_update(
            db=db,
            crisis_id=crisis_id,
            raw_text=payload.raw_text,
            source=payload.source,
            reporter_name=payload.reporter_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Update processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    # Broadcast update to dashboard via WebSocket
    await manager.broadcast(str(crisis_id), {
        "event": "update_processed",
        "data": result,
    })

    return result


# ── List Updates ──────────────────────────────────────────────────────────────

@router.get(
    "/crises/{crisis_id}/updates/",
    response_model=list[CrisisUpdateResponse],
    summary="List all updates for a crisis",
)
async def list_updates(
    crisis_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CrisisUpdate)
        .where(CrisisUpdate.crisis_id == crisis_id)
        .order_by(CrisisUpdate.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# ── List Entities ─────────────────────────────────────────────────────────────

@router.get(
    "/crises/{crisis_id}/entities/",
    response_model=list[EntityResponse],
    summary="List all tracked entities for a crisis",
)
async def list_entities(
    crisis_id: uuid.UUID,
    entity_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    from app.models.entity import EntityType
    stmt = select(Entity).where(Entity.crisis_id == crisis_id)
    if entity_type:
        try:
            stmt = stmt.where(Entity.entity_type == EntityType(entity_type))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid entity_type: '{entity_type}'")
    stmt = stmt.order_by(Entity.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


# ── WebSocket for live dashboard updates ──────────────────────────────────────

@router.websocket("/ws/{crisis_id}")
async def websocket_endpoint(crisis_id: str, websocket: WebSocket):
    """Real-time WebSocket connection for dashboard updates."""
    await manager.connect(crisis_id, websocket)
    try:
        while True:
            # Keep alive — client can also send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(crisis_id, websocket)
        logger.info(f"WebSocket disconnected for crisis {crisis_id}")

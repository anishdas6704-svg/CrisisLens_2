"""
CrisisLens - Crisis CRUD API Routes
POST   /crises/          - Create a new crisis
GET    /crises/          - List all crises
GET    /crises/{id}      - Get crisis detail
PATCH  /crises/{id}      - Update crisis metadata
DELETE /crises/{id}      - Delete crisis
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.database import get_db
from app.models.crisis import Crisis
from app.models.entity import Entity
from app.models.update import CrisisUpdate, ConflictStatus
from app.api.schemas import (
    CrisisCreate, CrisisUpdate as CrisisUpdateSchema,
    CrisisResponse, DashboardStats
)

router = APIRouter(prefix="/crises", tags=["Crises"])


@router.post("/", response_model=CrisisResponse, status_code=status.HTTP_201_CREATED)
async def create_crisis(payload: CrisisCreate, db: AsyncSession = Depends(get_db)):
    """Create a new crisis event."""
    crisis = Crisis(**payload.model_dump())
    db.add(crisis)
    await db.commit()
    await db.refresh(crisis)
    logger.info(f"Created crisis: {crisis.name} ({crisis.id})")
    return crisis


@router.get("/", response_model=list[CrisisResponse])
async def list_crises(
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List crises with optional status filter."""
    from app.models.crisis import CrisisStatus
    stmt = select(Crisis).order_by(Crisis.created_at.desc())
    if status_filter:
        try:
            stmt = stmt.where(Crisis.status == CrisisStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status_filter: '{status_filter}'")
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get high-level dashboard statistics."""
    from app.models.crisis import CrisisStatus

    total_crises = await db.scalar(select(func.count()).select_from(Crisis))
    active_crises = await db.scalar(
        select(func.count()).select_from(Crisis).where(Crisis.status == CrisisStatus.ACTIVE)
    )
    total_entities = await db.scalar(select(func.count()).select_from(Entity))
    total_updates = await db.scalar(select(func.count()).select_from(CrisisUpdate))
    conflicts_pending = await db.scalar(
        select(func.count()).select_from(CrisisUpdate).where(
            CrisisUpdate.conflict_status == ConflictStatus.CONFLICT
        )
    )

    # Last 10 updates
    recent_stmt = (
        select(CrisisUpdate)
        .order_by(CrisisUpdate.created_at.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_stmt)
    recent_updates = [
        {
            "id": str(u.id),
            "raw_text": u.raw_text[:100],
            "change_detected": u.change_detected,
            "conflict_status": u.conflict_status.value,
            "created_at": u.created_at.isoformat(),
        }
        for u in recent_result.scalars().all()
    ]

    return DashboardStats(
        total_crises=total_crises or 0,
        active_crises=active_crises or 0,
        total_entities=total_entities or 0,
        total_updates=total_updates or 0,
        conflicts_pending=conflicts_pending or 0,
        recent_updates=recent_updates,
    )


@router.get("/{crisis_id}", response_model=CrisisResponse)
async def get_crisis(crisis_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific crisis by ID."""
    crisis = await db.get(Crisis, crisis_id)
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")
    return crisis


@router.patch("/{crisis_id}", response_model=CrisisResponse)
async def update_crisis(
    crisis_id: uuid.UUID,
    payload: CrisisUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Update crisis metadata."""
    crisis = await db.get(Crisis, crisis_id)
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(crisis, key, value)

    await db.commit()
    await db.refresh(crisis)
    return crisis


@router.delete("/{crisis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crisis(crisis_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a crisis and all related data."""
    crisis = await db.get(Crisis, crisis_id)
    if not crisis:
        raise HTTPException(status_code=404, detail="Crisis not found")
    await db.delete(crisis)
    await db.commit()

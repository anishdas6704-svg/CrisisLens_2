"""
CrisisLens - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.db.database import init_db
from app.api.routes import crises, updates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"DB init skipped (PostgreSQL not available): {e}")
    yield
    logger.info("Shutting down CrisisLens")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## CrisisLens API

AI-powered crisis situational awareness system.

### Key Features
- 🧠 **AI Entity Extraction** – Google Gemini extracts structured info from free-text updates
- 🔄 **Change Detection** – Automatically detects when entity status changes
- ⚠️ **Conflict Detection** – Flags contradicting reports
- 📡 **Real-time Updates** – WebSocket push to dashboard
- 📊 **Dashboard Stats** – Aggregated crisis overview
""",
    contact={"name": "CrisisLens Team"},
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(crises.router, prefix="/api/v1")
app.include_router(updates.router, prefix="/api/v1")


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }

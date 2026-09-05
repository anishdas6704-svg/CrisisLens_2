"""
CrisisLens Backend - Database Connection & Session Management
Async SQLAlchemy with PostgreSQL via asyncpg
"""
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
# pyrefly: ignore [missing-import]
from loguru import logger


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup (dev only — use Alembic for production)."""
    async with engine.begin() as conn:
        from app.models import crisis, entity, update  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables initialized")

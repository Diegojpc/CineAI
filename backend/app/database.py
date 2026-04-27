"""
CineAI Backend - Database Engine & Session
Configura el engine async de SQLAlchemy y el session factory.
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""
    pass


async def get_db() -> AsyncSession:
    """Dependency injection: genera una sesión de DB por request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            logger.error("DB session error, rolling back: %s", exc, exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Crea las tablas si no existen (fallback para desarrollo)."""
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")

# Async SQLAlchemy Database Setup for Neon DB

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create async engine for Neon DB (Serverless Postgres)
# Wrap in try-except to handle invalid DATABASE_URL gracefully
try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    logger.info("Database engine created successfully")
except Exception as e:
    logger.warning(f"Database engine creation failed (Groq-only mode): {e}")
    engine = None
    AsyncSessionLocal = None


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


async def init_db():
    """Initialize database - create all tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def close_db():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


@asynccontextmanager
async def get_db_session():
    """
    Async context manager for database sessions.
    Returns None if database unavailable.
    
    Usage:
        async with get_db_session() as session:
            # use session (check if session is not None)
    """
    if AsyncSessionLocal is None:
        logger.warning("Database not available (Groq-only mode)")
        yield None
        return
        
    try:
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
    except Exception as e:
        logger.warning(f"Could not create database session (Groq-only mode): {e}")
        yield None  # Return None if database is not available


async def get_db():
    """
    Dependency for FastAPI endpoints.
    Returns None if database is not available (Groq-only mode).
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # use db session (check if db is not None)
    """
    if AsyncSessionLocal is None:
        logger.warning("Database not configured (Groq-only mode)")
        yield None
        return
    
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
        await session.commit()
    except Exception as e:
        logger.warning(f"Database error (Groq-only mode): {e}")
        if session:
            await session.rollback()
        # Don't re-raise, just yield None on error
    finally:
        if session:
            await session.close()

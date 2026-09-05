# backend/app/database/connection.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from app.core.config import settings


# ================================================================
# DATABASE URL
# ================================================================

DATABASE_URL = settings.DATABASE_URL


# ================================================================
# ENGINE CONFIGURATION
# ================================================================

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=getattr(
        settings,
        "DEBUG",
        False,
    ),
    pool_pre_ping=True,
    pool_recycle=1800,
)


# ================================================================
# DATABASE DEPENDENCY
# ================================================================

async def get_db() -> AsyncGenerator:
    """
    Compatibility wrapper.

    The actual AsyncSessionLocal/session factory is maintained
    in session.py.
    """

    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ================================================================
# DATABASE CONNECTIVITY CHECK
# ================================================================

async def check_database_connection() -> bool:
    """
    Check whether the database is reachable.

    Returns:
        True if database connection succeeds.
        False if connection fails.
    """

    from sqlalchemy import text

    try:
        async with engine.connect() as connection:
            await connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception:
        return False


# ================================================================
# INITIALIZE DATABASE
# ================================================================

async def init_db() -> None:
    """
    Initialize database tables.

    Normally migrations should be preferred in production.
    This function is useful for development/testing.
    """

    from app.database.base import Base

    # Import models so SQLAlchemy registers them with Base.metadata.
    from app.models import (
        audit_log,
        candidate,
        interview,
        job,
        resume,
        score,
        user,
    )

    # Prevent unused-import lint warnings.
    _ = (
        audit_log,
        candidate,
        interview,
        job,
        resume,
        score,
        user,
    )

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )


# ================================================================
# CLOSE DATABASE
# ================================================================

async def close_db() -> None:
    """
    Dispose the SQLAlchemy connection pool.
    """

    await engine.dispose()


# ================================================================
# DATABASE HEALTH
# ================================================================

async def database_health() -> dict[str, str]:
    """
    Return a simple database health response.
    """

    is_connected = (
        await check_database_connection()
    )

    if is_connected:
        return {
            "status": "healthy",
            "database": "connected",
        }

    return {
        "status": "unhealthy",
        "database": "disconnected",
    }
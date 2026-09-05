# backend/app/database/session.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.database.connection import engine


# ================================================================
# ASYNC SESSION FACTORY
# ================================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ================================================================
# DATABASE SESSION DEPENDENCY
# ================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous SQLAlchemy database session.

    The session is automatically closed after the request.
    If an exception occurs, the transaction is rolled back.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()


# ================================================================
# COMMIT HELPER
# ================================================================

async def commit_session(
    session: AsyncSession,
) -> None:
    """
    Commit the current database transaction.
    """

    try:
        await session.commit()

    except Exception:
        await session.rollback()
        raise


# ================================================================
# ROLLBACK HELPER
# ================================================================

async def rollback_session(
    session: AsyncSession,
) -> None:
    """
    Roll back the current database transaction.
    """

    await session.rollback()


# ================================================================
# FLUSH HELPER
# ================================================================

async def flush_session(
    session: AsyncSession,
) -> None:
    """
    Flush pending database changes without committing.
    """

    await session.flush()


# ================================================================
# REFRESH HELPER
# ================================================================

async def refresh_instance(
    session: AsyncSession,
    instance,
) -> None:
    """
    Refresh an ORM object from the database.
    """

    await session.refresh(instance)
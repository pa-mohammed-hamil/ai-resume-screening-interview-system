# backend/app/database/base.py

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every model in app/models/ should inherit from this class.
    """

    pass


class TimestampMixin:
    """
    Common timestamp fields for database models.

    created_at:
        Set when the record is created.

    updated_at:
        Updated whenever the record is modified.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
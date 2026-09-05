"""
Celery application configuration.

Uses Redis as the broker and result backend by default.
Values are loaded from application settings when available.
"""

from celery import Celery

from app.core.config import settings


def _get_setting(name: str, default: str) -> str:
    """Safely read a setting with a fallback."""
    return getattr(settings, name, default)


CELERY_BROKER_URL = _get_setting(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
)

CELERY_RESULT_BACKEND = _get_setting(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/1",
)


celery_app = Celery(
    "ai_resume_screening",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=1800,
    task_soft_time_limit=1500,
    broker_connection_retry_on_startup=True,
)


# Automatically discover task modules.
celery_app.autodiscover_tasks(
    [
        "app.workers.resume_tasks",
        "app.workers.embedding_tasks",
        "app.workers.interview_tasks",
        "app.workers.report_tasks",
    ]
)

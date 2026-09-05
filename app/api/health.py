from datetime import datetime, timezone

from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Checks whether the API service is running.",
)
async def health_check() -> dict:
    """
    Basic application health check.

    Used by:
    - Load balancers
    - Docker health checks
    - Kubernetes probes
    - Monitoring systems
    """
    return {
        "status": "healthy",
        "service": "ai-resume-screening-interview-system",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
)
async def liveness_check() -> dict:
    """
    Liveness probe.

    Confirms that the application process is alive.
    """
    return {
        "status": "alive",
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
)
async def readiness_check() -> dict:
    """
    Readiness probe.

    Used to determine whether the API is ready
    to receive traffic.
    """

    # Later you can add checks for:
    # - PostgreSQL
    # - Redis
    # - Celery
    # - Vector database
    # - LLM provider

    return {
        "status": "ready",
    }
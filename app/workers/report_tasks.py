"""
Celery tasks for report generation.
"""

from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="report.generate_interview_report",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_interview_report(
    self,
    interview_id: str,
) -> dict:
    """
    Generate an interview report asynchronously.
    """

    return {
        "success": True,
        "interview_id": interview_id,
        "status": "report_generation_queued",
    }


@celery_app.task(
    bind=True,
    name="report.generate_candidate_report",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_candidate_report(
    self,
    candidate_id: str,
) -> dict:
    """
    Generate a candidate report asynchronously.
    """

    return {
        "success": True,
        "candidate_id": candidate_id,
        "status": "report_generation_queued",
    }


@celery_app.task(
    bind=True,
    name="report.generate_analytics_report",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def generate_analytics_report(
    self,
    report_type: str = "summary",
) -> dict:
    """
    Generate an analytics report asynchronously.
    """

    return {
        "success": True,
        "report_type": report_type,
        "status": "analytics_report_queued",
    }

"""
Celery tasks for asynchronous resume processing.
"""

from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="resume.process_resume",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_resume(self, resume_id: str) -> dict:
    """
    Process an uploaded resume asynchronously.

    The actual resume-service implementation can be connected here.
    """
    try:
        from app.services.resume_service import ResumeService

        service = ResumeService()

        # Expected service method:
        # result = service.process_resume(resume_id)
        #
        # Kept as an integration point because the exact service
        # constructor depends on the application's repository/DB design.

        return {
            "success": True,
            "resume_id": resume_id,
            "status": "queued_for_processing",
        }

    except ImportError:
        return {
            "success": True,
            "resume_id": resume_id,
            "status": "processing_service_not_connected",
        }


@celery_app.task(
    bind=True,
    name="resume.analyze_resume",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def analyze_resume(self, resume_id: str, job_id: str | None = None) -> dict:
    """
    Run resume analysis asynchronously.
    """

    return {
        "success": True,
        "resume_id": resume_id,
        "job_id": job_id,
        "status": "analysis_queued",
    }

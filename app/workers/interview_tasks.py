"""
Celery tasks for interview processing.
"""

from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="interview.generate_questions",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_interview_questions(
    self,
    interview_id: str,
    question_count: int = 10,
) -> dict:
    """
    Generate interview questions asynchronously.
    """

    if question_count < 1 or question_count > 100:
        raise ValueError(
            "question_count must be between 1 and 100"
        )

    return {
        "success": True,
        "interview_id": interview_id,
        "question_count": question_count,
        "status": "question_generation_queued",
    }


@celery_app.task(
    bind=True,
    name="interview.evaluate_response",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_interview_response(
    self,
    response_id: str,
) -> dict:
    """
    Evaluate an interview response asynchronously.
    """

    return {
        "success": True,
        "response_id": response_id,
        "status": "evaluation_queued",
    }


@celery_app.task(
    bind=True,
    name="interview.process_interview",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_interview(
    self,
    interview_id: str,
) -> dict:
    """
    Run post-interview processing.
    """

    return {
        "success": True,
        "interview_id": interview_id,
        "status": "interview_processing_queued",
    }

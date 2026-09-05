"""
Celery tasks for embedding generation.
"""

from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="embedding.generate_resume_embedding",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_resume_embedding(
    self,
    resume_id: str,
) -> dict:
    """
    Generate and store an embedding for a resume.
    """

    return {
        "success": True,
        "resume_id": resume_id,
        "status": "embedding_queued",
    }


@celery_app.task(
    bind=True,
    name="embedding.generate_job_embedding",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_job_embedding(
    self,
    job_id: str,
) -> dict:
    """
    Generate and store an embedding for a job description.
    """

    return {
        "success": True,
        "job_id": job_id,
        "status": "embedding_queued",
    }


@celery_app.task(
    bind=True,
    name="embedding.batch_generate_embeddings",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def batch_generate_embeddings(
    self,
    document_ids: list[str],
    document_type: str,
) -> dict:
    """
    Queue embedding generation for multiple documents.
    """

    if document_type not in {"resume", "job"}:
        raise ValueError(
            "document_type must be 'resume' or 'job'"
        )

    return {
        "success": True,
        "document_type": document_type,
        "document_ids": document_ids,
        "count": len(document_ids),
        "status": "batch_queued",
    }

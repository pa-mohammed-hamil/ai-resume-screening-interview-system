# backend/app/services/job_service.py

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobService:
    """Business logic for job and job-description management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================================================================
    # Job Lookup
    # ==================================================================

    async def get_job_by_id(
        self,
        job_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Job]:
        """Return a job by ID, optionally restricted to its owner."""

        query = select(Job).where(
            Job.id == job_id
        )

        if user_id is not None and hasattr(Job, "user_id"):
            query = query.where(
                Job.user_id == user_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_jobs(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> list[Job]:
        """Return jobs with pagination and optional filters."""

        query = select(Job)

        if user_id is not None and hasattr(Job, "user_id"):
            query = query.where(
                Job.user_id == user_id
            )

        if status is not None and hasattr(Job, "status"):
            query = query.where(
                Job.status == status
            )

        if hasattr(Job, "created_at"):
            query = query.order_by(
                Job.created_at.desc()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def count_jobs(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count jobs matching the supplied filters."""

        query = select(
            func.count(Job.id)
        )

        if user_id is not None and hasattr(Job, "user_id"):
            query = query.where(
                Job.user_id == user_id
            )

        if status is not None and hasattr(Job, "status"):
            query = query.where(
                Job.status == status
            )

        result = await self.db.execute(query)

        return int(result.scalar_one() or 0)

    # ==================================================================
    # Job Creation
    # ==================================================================

    async def create_job(
        self,
        user_id: int,
        title: str,
        description: str,
        **job_data: Any,
    ) -> Job:
        """Create a new job posting."""

        data = {
            "user_id": user_id,
            "title": title.strip(),
            "description": description.strip(),
        }

        data.update(job_data)

        job = Job(**data)

        self.db.add(job)

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ==================================================================
    # Job Update
    # ==================================================================

    async def update_job(
        self,
        job: Job,
        updates: dict[str, Any],
    ) -> Job:
        """Update editable job fields."""

        protected_fields = {
            "id",
            "user_id",
            "created_at",
        }

        for field, value in updates.items():
            if field in protected_fields:
                continue

            if hasattr(job, field):
                if isinstance(value, str):
                    value = value.strip()

                setattr(job, field, value)

        if hasattr(job, "updated_at"):
            job.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ==================================================================
    # Delete Job
    # ==================================================================

    async def delete_job(
        self,
        job: Job,
    ) -> bool:
        """Delete a job."""

        await self.db.delete(job)

        await self.db.commit()

        return True

    # ==================================================================
    # Publish Job
    # ==================================================================

    async def publish_job(
        self,
        job: Job,
    ) -> Job:
        """Publish a job and make it active."""

        if hasattr(job, "status"):
            job.status = "published"

        if hasattr(job, "is_active"):
            job.is_active = True

        if hasattr(job, "published_at"):
            job.published_at = datetime.now(timezone.utc)

        if hasattr(job, "updated_at"):
            job.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ==================================================================
    # Close Job
    # ==================================================================

    async def close_job(
        self,
        job: Job,
    ) -> Job:
        """Close a job posting."""

        if hasattr(job, "status"):
            job.status = "closed"

        if hasattr(job, "is_active"):
            job.is_active = False

        if hasattr(job, "closed_at"):
            job.closed_at = datetime.now(timezone.utc)

        if hasattr(job, "updated_at"):
            job.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ==================================================================
    # Reopen Job
    # ==================================================================

    async def reopen_job(
        self,
        job: Job,
    ) -> Job:
        """Reopen a previously closed job."""

        if hasattr(job, "status"):
            job.status = "published"

        if hasattr(job, "is_active"):
            job.is_active = True

        if hasattr(job, "closed_at"):
            job.closed_at = None

        if hasattr(job, "updated_at"):
            job.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ==================================================================
    # JD Analysis
    # ==================================================================

    async def analyze_job_description(
        self,
        job: Job,
        jd_analyzer: Any,
    ) -> dict[str, Any]:
        """
        Analyze a job description.

        Expected analyzer interface:
            analyze(text)
        """

        description = getattr(
            job,
            "description",
            None,
        )

        if not description:
            raise ValueError(
                "Job description is empty."
            )

        analyze_method = getattr(
            jd_analyzer,
            "analyze",
            None,
        )

        if analyze_method is None:
            raise ValueError(
                "JD analyzer must expose an analyze() method."
            )

        result = analyze_method(description)

        if hasattr(result, "__await__"):
            result = await result

        if not isinstance(result, dict):
            result = {
                "result": result,
            }

        await self._set_if_exists(
            job,
            "analysis_data",
            result,
        )

        await self._set_if_exists(
            job,
            "is_analyzed",
            True,
        )

        await self._set_if_exists(
            job,
            "analyzed_at",
            datetime.now(timezone.utc),
        )

        await self.db.commit()
        await self.db.refresh(job)

        return result

    # ==================================================================
    # Requirements Extraction
    # ==================================================================

    async def extract_requirements(
        self,
        job: Job,
        requirement_extractor: Any,
    ) -> dict[str, Any]:
        """Extract required and preferred qualifications."""

        description = getattr(
            job,
            "description",
            None,
        )

        if not description:
            raise ValueError(
                "Job description is empty."
            )

        extract_method = getattr(
            requirement_extractor,
            "extract",
            None,
        )

        if extract_method is None:
            raise ValueError(
                "Requirement extractor must expose an extract() method."
            )

        result = extract_method(description)

        if hasattr(result, "__await__"):
            result = await result

        if not isinstance(result, dict):
            result = {
                "requirements": result,
            }

        await self._set_if_exists(
            job,
            "requirements",
            result.get(
                "requirements",
                result,
            ),
        )

        await self.db.commit()
        await self.db.refresh(job)

        return result

    # ==================================================================
    # Skill Extraction
    # ==================================================================

    async def extract_required_skills(
        self,
        job: Job,
        skill_extractor: Any,
    ) -> list[Any]:
        """Extract skills required by the job."""

        description = getattr(
            job,
            "description",
            None,
        )

        if not description:
            raise ValueError(
                "Job description is empty."
            )

        extract_method = getattr(
            skill_extractor,
            "extract",
            None,
        )

        if extract_method is None:
            raise ValueError(
                "Skill extractor must expose an extract() method."
            )

        result = extract_method(description)

        if hasattr(result, "__await__"):
            result = await result

        if result is None:
            result = []

        if isinstance(result, dict):
            result = result.get(
                "skills",
                [],
            )

        await self._set_if_exists(
            job,
            "required_skills",
            result,
        )

        await self.db.commit()
        await self.db.refresh(job)

        return result

    # ==================================================================
    # Resume / Candidate Matching
    # ==================================================================

    async def match_resume(
        self,
        job: Job,
        resume: Any,
        matcher: Any,
    ) -> dict[str, Any]:
        """Match a resume against this job."""

        match_method = getattr(
            matcher,
            "match",
            None,
        )

        if match_method is None:
            raise ValueError(
                "Matcher must expose a match() method."
            )

        try:
            result = match_method(
                resume=resume,
                job=job,
            )
        except TypeError:
            result = match_method(
                resume,
                job,
            )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "score": float(result),
        }

    # ==================================================================
    # Job Statistics
    # ==================================================================

    async def get_job_statistics(
        self,
        job: Job,
    ) -> dict[str, Any]:
        """
        Return statistics for a job.

        Candidate/interview relationships are intentionally accessed
        only when the corresponding model relationships exist.
        """

        statistics: dict[str, Any] = {
            "job_id": job.id,
            "title": getattr(
                job,
                "title",
                None,
            ),
            "status": getattr(
                job,
                "status",
                None,
            ),
            "is_active": getattr(
                job,
                "is_active",
                None,
            ),
        }

        for attribute in (
            "applicant_count",
            "candidate_count",
            "shortlisted_count",
            "interview_count",
            "hired_count",
            "rejected_count",
        ):
            if hasattr(job, attribute):
                statistics[attribute] = getattr(
                    job,
                    attribute,
                )

        return statistics

    # ==================================================================
    # Job Search
    # ==================================================================

    async def search_jobs(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Job]:
        """Search jobs by title and description."""

        term = f"%{search_term.strip()}%"

        conditions = [
            Job.title.ilike(term),
            Job.description.ilike(term),
        ]

        query = select(Job).where(
            conditions[0] | conditions[1]
        )

        if user_id is not None and hasattr(Job, "user_id"):
            query = query.where(
                Job.user_id == user_id
            )

        if hasattr(Job, "created_at"):
            query = query.order_by(
                Job.created_at.desc()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    # ==================================================================
    # Internal Helper
    # ==================================================================

    @staticmethod
    async def _set_if_exists(
        obj: Any,
        attribute: str,
        value: Any,
    ) -> None:
        """Set a model attribute only when it exists."""

        if hasattr(obj, attribute):
            setattr(
                obj,
                attribute,
                value,
            )
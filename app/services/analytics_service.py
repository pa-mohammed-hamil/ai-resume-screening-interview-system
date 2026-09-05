# backend/app/services/analytics_service.py

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.job import Job
from app.models.resume import Resume


class AnalyticsService:
    """Service layer for recruiter and AI hiring analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ================================================================
    # DASHBOARD OVERVIEW
    # ================================================================

    async def get_dashboard_overview(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return the main recruiter dashboard metrics."""

        candidates = await self.count_candidates(
            user_id=user_id
        )

        resumes = await self.count_resumes(
            user_id=user_id
        )

        jobs = await self.count_jobs(
            user_id=user_id
        )

        interviews = await self.count_interviews(
            user_id=user_id
        )

        completed_interviews = await self.count_interviews(
            user_id=user_id,
            status="completed",
        )

        hired_candidates = await self.count_candidates(
            user_id=user_id,
            status="hired",
        )

        shortlisted_candidates = await self.count_candidates(
            user_id=user_id,
            status="shortlisted",
        )

        rejected_candidates = await self.count_candidates(
            user_id=user_id,
            status="rejected",
        )

        return {
            "candidates": candidates,
            "resumes": resumes,
            "jobs": jobs,
            "interviews": interviews,
            "completed_interviews": completed_interviews,
            "hired_candidates": hired_candidates,
            "shortlisted_candidates": shortlisted_candidates,
            "rejected_candidates": rejected_candidates,
            "hire_rate": self._percentage(
                hired_candidates,
                candidates,
            ),
            "shortlist_rate": self._percentage(
                shortlisted_candidates,
                candidates,
            ),
            "interview_completion_rate": self._percentage(
                completed_interviews,
                interviews,
            ),
        }

    # ================================================================
    # CANDIDATE ANALYTICS
    # ================================================================

    async def get_candidate_analytics(
        self,
        user_id: Optional[int] = None,
        job_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return candidate funnel and status analytics."""

        status_counts = await self.get_candidate_status_counts(
            user_id=user_id,
            job_id=job_id,
        )

        total = sum(status_counts.values())

        return {
            "total_candidates": total,
            "status_counts": status_counts,
            "new": status_counts.get("new", 0),
            "screening": status_counts.get("screening", 0),
            "shortlisted": status_counts.get(
                "shortlisted",
                0,
            ),
            "interview": status_counts.get(
                "interview",
                0,
            ),
            "selected": status_counts.get(
                "selected",
                0,
            ),
            "hired": status_counts.get(
                "hired",
                0,
            ),
            "rejected": status_counts.get(
                "rejected",
                0,
            ),
            "withdrawn": status_counts.get(
                "withdrawn",
                0,
            ),
            "hire_rate": self._percentage(
                status_counts.get("hired", 0),
                total,
            ),
        }

    # ================================================================
    # CANDIDATE STATUS COUNTS
    # ================================================================

    async def get_candidate_status_counts(
        self,
        user_id: Optional[int] = None,
        job_id: Optional[int] = None,
    ) -> dict[str, int]:
        """Count candidates grouped by recruitment status."""

        if not hasattr(Candidate, "status"):
            return {}

        query = select(
            Candidate.status,
            func.count(Candidate.id),
        ).group_by(
            Candidate.status
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        if job_id is not None and hasattr(
            Candidate,
            "job_id",
        ):
            query = query.where(
                Candidate.job_id == job_id
            )

        result = await self.db.execute(query)

        return {
            str(status): int(count)
            for status, count in result.all()
            if status is not None
        }

    # ================================================================
    # RESUME ANALYTICS
    # ================================================================

    async def get_resume_analytics(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return resume processing and ATS analytics."""

        total = await self.count_resumes(
            user_id=user_id
        )

        processed = await self._count_by_possible_status(
            Resume,
            user_id,
            ["processed", "analyzed", "completed"],
        )

        failed = await self._count_by_possible_status(
            Resume,
            user_id,
            ["failed", "error"],
        )

        average_ats_score = await self.get_average_score(
            Resume,
            "ats_score",
            user_id=user_id,
        )

        return {
            "total_resumes": total,
            "processed_resumes": processed,
            "failed_resumes": failed,
            "processing_rate": self._percentage(
                processed,
                total,
            ),
            "average_ats_score": self._round_score(
                average_ats_score
            ),
        }

    # ================================================================
    # JOB ANALYTICS
    # ================================================================

    async def get_job_analytics(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return job and hiring analytics."""

        total_jobs = await self.count_jobs(
            user_id=user_id
        )

        active_jobs = await self._count_by_possible_status(
            Job,
            user_id,
            ["active", "open", "published"],
        )

        closed_jobs = await self._count_by_possible_status(
            Job,
            user_id,
            ["closed", "filled", "archived"],
        )

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "closed_jobs": closed_jobs,
            "open_rate": self._percentage(
                active_jobs,
                total_jobs,
            ),
        }

    # ================================================================
    # INTERVIEW ANALYTICS
    # ================================================================

    async def get_interview_analytics(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return interview performance analytics."""

        total = await self.count_interviews(
            user_id=user_id
        )

        scheduled = await self.count_interviews(
            user_id=user_id,
            status="scheduled",
        )

        in_progress = await self.count_interviews(
            user_id=user_id,
            status="in_progress",
        )

        completed = await self.count_interviews(
            user_id=user_id,
            status="completed",
        )

        cancelled = await self.count_interviews(
            user_id=user_id,
            status="cancelled",
        )

        average_score = await self.get_average_score(
            Interview,
            self._first_existing_field(
                Interview,
                [
                    "final_score",
                    "overall_score",
                ],
            ),
            user_id=user_id,
        )

        return {
            "total_interviews": total,
            "scheduled": scheduled,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "completion_rate": self._percentage(
                completed,
                total,
            ),
            "cancellation_rate": self._percentage(
                cancelled,
                total,
            ),
            "average_score": self._round_score(
                average_score
            ),
        }

    # ================================================================
    # INTERVIEW TYPE ANALYTICS
    # ================================================================

    async def get_interview_type_distribution(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, int]:
        """Return interviews grouped by type."""

        if not hasattr(
            Interview,
            "interview_type",
        ):
            return {}

        query = select(
            Interview.interview_type,
            func.count(Interview.id),
        ).group_by(
            Interview.interview_type
        )

        if user_id is not None and hasattr(
            Interview,
            "user_id",
        ):
            query = query.where(
                Interview.user_id == user_id
            )

        result = await self.db.execute(query)

        return {
            str(interview_type): int(count)
            for interview_type, count in result.all()
            if interview_type is not None
        }

    # ================================================================
    # SCORE ANALYTICS
    # ================================================================

    async def get_score_analytics(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return average AI screening and interview scores."""

        ats_score = await self.get_average_score(
            Resume,
            "ats_score",
            user_id=user_id,
        )

        match_score = await self.get_average_score(
            Candidate,
            "match_score",
            user_id=user_id,
        )

        skill_score = await self.get_average_score(
            Candidate,
            "skill_score",
            user_id=user_id,
        )

        interview_score_field = self._first_existing_field(
            Interview,
            [
                "final_score",
                "overall_score",
            ],
        )

        interview_score = await self.get_average_score(
            Interview,
            interview_score_field,
            user_id=user_id,
        )

        return {
            "average_ats_score": self._round_score(
                ats_score
            ),
            "average_match_score": self._round_score(
                match_score
            ),
            "average_skill_score": self._round_score(
                skill_score
            ),
            "average_interview_score": self._round_score(
                interview_score
            ),
        }

    # ================================================================
    # SCORE DISTRIBUTION
    # ================================================================

    async def get_score_distribution(
        self,
        model: Any,
        score_field: str,
        user_id: Optional[int] = None,
    ) -> dict[str, int]:
        """Return score distribution buckets."""

        field = getattr(
            model,
            score_field,
            None,
        )

        if field is None:
            return {}

        buckets = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0,
        }

        query = select(field)

        if user_id is not None and hasattr(
            model,
            "user_id",
        ):
            query = query.where(
                model.user_id == user_id
            )

        result = await self.db.execute(query)

        for row in result.scalars().all():

            if row is None:
                continue

            try:
                score = float(row)
            except (
                TypeError,
                ValueError,
            ):
                continue

            if score <= 20:
                buckets["0-20"] += 1
            elif score <= 40:
                buckets["21-40"] += 1
            elif score <= 60:
                buckets["41-60"] += 1
            elif score <= 80:
                buckets["61-80"] += 1
            else:
                buckets["81-100"] += 1

        return buckets

    # ================================================================
    # HIRING FUNNEL
    # ================================================================

    async def get_hiring_funnel(
        self,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return recruiter hiring funnel."""

        status_counts = await self.get_candidate_status_counts(
            user_id=user_id
        )

        stages = [
            ("Applied", "new"),
            ("Screening", "screening"),
            ("Shortlisted", "shortlisted"),
            ("Interview", "interview"),
            ("Selected", "selected"),
            ("Hired", "hired"),
        ]

        funnel = []

        previous_count = None

        for label, status in stages:

            count = status_counts.get(
                status,
                0,
            )

            conversion_rate = None

            if previous_count not in (
                None,
                0,
            ):
                conversion_rate = self._percentage(
                    count,
                    previous_count,
                )

            funnel.append(
                {
                    "stage": label,
                    "status": status,
                    "count": count,
                    "conversion_rate": conversion_rate,
                }
            )

            previous_count = count

        return {
            "stages": funnel,
        }

    # ================================================================
    # TIME-SERIES ANALYTICS
    # ================================================================

    async def get_candidate_trend(
        self,
        days: int = 30,
        user_id: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Return daily candidate creation trend."""

        if days < 1:
            raise ValueError(
                "Days must be greater than zero."
            )

        if not hasattr(
            Candidate,
            "created_at",
        ):
            return []

        start_date = datetime.now(
            timezone.utc
        ) - timedelta(days=days - 1)

        query = select(
            func.date(Candidate.created_at).label(
                "date"
            ),
            func.count(Candidate.id).label(
                "count"
            ),
        ).where(
            Candidate.created_at >= start_date
        ).group_by(
            func.date(Candidate.created_at)
        ).order_by(
            func.date(Candidate.created_at)
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        result = await self.db.execute(query)

        rows = result.all()

        return [
            {
                "date": str(date),
                "count": int(count),
            }
            for date, count in rows
        ]

    # ================================================================
    # HIRING TREND
    # ================================================================

    async def get_hiring_trend(
        self,
        days: int = 30,
        user_id: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Return daily hiring trend."""

        if not hasattr(
            Candidate,
            "created_at",
        ):
            return []

        if not hasattr(
            Candidate,
            "status",
        ):
            return []

        start_date = datetime.now(
            timezone.utc
        ) - timedelta(days=days - 1)

        query = select(
            func.date(
                Candidate.created_at
            ).label("date"),
            func.count(
                Candidate.id
            ).label("hired"),
        ).where(
            Candidate.created_at >= start_date,
            Candidate.status == "hired",
        ).group_by(
            func.date(
                Candidate.created_at
            )
        ).order_by(
            func.date(
                Candidate.created_at
            )
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        result = await self.db.execute(query)

        return [
            {
                "date": str(date),
                "hired": int(hired),
            }
            for date, hired in result.all()
        ]

    # ================================================================
    # TOP CANDIDATES
    # ================================================================

    async def get_top_candidates(
        self,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> list[Candidate]:
        """Return candidates with highest AI match scores."""

        if not hasattr(
            Candidate,
            "match_score",
        ):
            return []

        query = select(Candidate).where(
            Candidate.match_score.is_not(None)
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        query = query.order_by(
            Candidate.match_score.desc()
        ).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    # ================================================================
    # TOP JOBS
    # ================================================================

    async def get_top_jobs(
        self,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> list[Job]:
        """Return jobs with the highest candidate volume."""

        if not hasattr(
            Job,
            "id",
        ):
            return []

        candidate_count = func.count(
            Candidate.id
        ).label(
            "candidate_count"
        )

        query = select(
            Job,
            candidate_count,
        ).outerjoin(
            Candidate,
            Candidate.job_id == Job.id,
        ).group_by(
            Job.id
        ).order_by(
            candidate_count.desc()
        ).limit(limit)

        if user_id is not None and hasattr(
            Job,
            "user_id",
        ):
            query = query.where(
                Job.user_id == user_id
            )

        result = await self.db.execute(query)

        return [
            job
            for job, _count in result.all()
        ]

    # ================================================================
    # GENERAL COUNTS
    # ================================================================

    async def count_candidates(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count candidates."""

        query = select(
            func.count(Candidate.id)
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        if status is not None and hasattr(
            Candidate,
            "status",
        ):
            query = query.where(
                Candidate.status == status
            )

        result = await self.db.execute(query)

        return int(result.scalar_one() or 0)

    async def count_resumes(
        self,
        user_id: Optional[int] = None,
    ) -> int:
        """Count resumes."""

        query = select(
            func.count(Resume.id)
        )

        if user_id is not None and hasattr(
            Resume,
            "user_id",
        ):
            query = query.where(
                Resume.user_id == user_id
            )

        result = await self.db.execute(query)

        return int(result.scalar_one() or 0)

    async def count_jobs(
        self,
        user_id: Optional[int] = None,
    ) -> int:
        """Count jobs."""

        query = select(
            func.count(Job.id)
        )

        if user_id is not None and hasattr(
            Job,
            "user_id",
        ):
            query = query.where(
                Job.user_id == user_id
            )

        result = await self.db.execute(query)

        return int(result.scalar_one() or 0)

    async def count_interviews(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count interviews."""

        query = select(
            func.count(Interview.id)
        )

        if user_id is not None and hasattr(
            Interview,
            "user_id",
        ):
            query = query.where(
                Interview.user_id == user_id
            )

        if status is not None and hasattr(
            Interview,
            "status",
        ):
            query = query.where(
                Interview.status == status
            )

        result = await self.db.execute(query)

        return int(result.scalar_one() or 0)

    # ================================================================
    # AVERAGE SCORE
    # ================================================================

    async def get_average_score(
        self,
        model: Any,
        score_field: Optional[str],
        user_id: Optional[int] = None,
    ) -> Optional[float]:
        """Calculate an average score."""

        if not score_field:
            return None

        field = getattr(
            model,
            score_field,
            None,
        )

        if field is None:
            return None

        query = select(
            func.avg(field)
        )

        if user_id is not None and hasattr(
            model,
            "user_id",
        ):
            query = query.where(
                model.user_id == user_id
            )

        result = await self.db.execute(query)

        value = result.scalar_one_or_none()

        if value is None:
            return None

        return float(value)

    # ================================================================
    # STATUS HELPERS
    # ================================================================

    async def _count_by_possible_status(
        self,
        model: Any,
        user_id: Optional[int],
        statuses: list[str],
    ) -> int:
        """Count records matching any supplied status."""

        if not hasattr(
            model,
            "status",
        ):
            return 0

        query = select(
            func.count(model.id)
        ).where(
            model.status.in_(statuses)
        )

        if user_id is not None and hasattr(
            model,
            "user_id",
        ):
            query = query.where(
                model.user_id == user_id
            )

        result = await self.db.execute(query)

        return int(result.scalar_one() or 0)

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    @staticmethod
    def _percentage(
        numerator: int,
        denominator: int,
    ) -> float:
        """Calculate percentage safely."""

        if denominator <= 0:
            return 0.0

        return round(
            (numerator / denominator) * 100,
            2,
        )

    @staticmethod
    def _round_score(
        score: Optional[float],
    ) -> Optional[float]:
        """Round an analytics score."""

        if score is None:
            return None

        return round(
            float(score),
            2,
        )

    @staticmethod
    def _first_existing_field(
        model: Any,
        fields: list[str],
    ) -> Optional[str]:
        """Return the first available model field."""

        for field in fields:
            if hasattr(model, field):
                return field

        return None
# backend/app/services/candidate_service.py

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate


class CandidateService:
    """Service layer for candidate management and recruitment workflows."""

    VALID_STATUSES = {
        "new",
        "screening",
        "shortlisted",
        "interview",
        "selected",
        "hired",
        "rejected",
        "withdrawn",
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    # ================================================================
    # GET CANDIDATE
    # ================================================================

    async def get_candidate_by_id(
        self,
        candidate_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Candidate]:
        """Get a candidate by ID."""

        query = select(Candidate).where(
            Candidate.id == candidate_id
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ================================================================
    # GET CANDIDATES
    # ================================================================

    async def get_candidates(
        self,
        user_id: Optional[int] = None,
        job_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Candidate]:
        """Get candidates with filtering and pagination."""

        query = select(Candidate)

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

        if status is not None and hasattr(
            Candidate,
            "status",
        ):
            query = query.where(
                Candidate.status == status
            )

        if hasattr(Candidate, "created_at"):
            query = query.order_by(
                Candidate.created_at.desc()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    # ================================================================
    # COUNT CANDIDATES
    # ================================================================

    async def count_candidates(
        self,
        user_id: Optional[int] = None,
        job_id: Optional[int] = None,
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

        if job_id is not None and hasattr(
            Candidate,
            "job_id",
        ):
            query = query.where(
                Candidate.job_id == job_id
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

    # ================================================================
    # CREATE CANDIDATE
    # ================================================================

    async def create_candidate(
        self,
        user_id: int,
        **candidate_data: Any,
    ) -> Candidate:
        """Create a new candidate."""

        data = dict(candidate_data)

        data["user_id"] = user_id

        if "status" not in data:
            data["status"] = "new"

        candidate = Candidate(**data)

        self.db.add(candidate)

        await self.db.commit()
        await self.db.refresh(candidate)

        return candidate

    # ================================================================
    # UPDATE CANDIDATE
    # ================================================================

    async def update_candidate(
        self,
        candidate: Candidate,
        updates: dict[str, Any],
    ) -> Candidate:
        """Update candidate information."""

        protected_fields = {
            "id",
            "user_id",
            "created_at",
        }

        for field, value in updates.items():

            if field in protected_fields:
                continue

            if not hasattr(candidate, field):
                continue

            if isinstance(value, str):
                value = value.strip()

            setattr(
                candidate,
                field,
                value,
            )

        if hasattr(candidate, "updated_at"):
            candidate.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(candidate)

        return candidate

    # ================================================================
    # UPDATE STATUS
    # ================================================================

    async def update_status(
        self,
        candidate: Candidate,
        status: str,
        notes: Optional[str] = None,
    ) -> Candidate:
        """Update candidate recruitment status."""

        normalized_status = status.strip().lower()

        if normalized_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid candidate status: {status}"
            )

        if hasattr(candidate, "status"):
            candidate.status = normalized_status

        if notes is not None and hasattr(
            candidate,
            "status_notes",
        ):
            candidate.status_notes = notes

        now = datetime.now(timezone.utc)

        if hasattr(candidate, "updated_at"):
            candidate.updated_at = now

        if (
            normalized_status == "hired"
            and hasattr(candidate, "hired_at")
        ):
            candidate.hired_at = now

        if (
            normalized_status == "rejected"
            and hasattr(candidate, "rejected_at")
        ):
            candidate.rejected_at = now

        await self.db.commit()
        await self.db.refresh(candidate)

        return candidate

    # ================================================================
    # ASSIGN JOB
    # ================================================================

    async def assign_to_job(
        self,
        candidate: Candidate,
        job_id: int,
    ) -> Candidate:
        """Assign candidate to a job."""

        if not hasattr(candidate, "job_id"):
            raise ValueError(
                "Candidate model does not have job_id."
            )

        candidate.job_id = job_id

        if hasattr(candidate, "updated_at"):
            candidate.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(candidate)

        return candidate

    # ================================================================
    # ATTACH RESUME
    # ================================================================

    async def attach_resume(
        self,
        candidate: Candidate,
        resume_id: int,
    ) -> Candidate:
        """Attach a resume to a candidate."""

        if hasattr(candidate, "resume_id"):
            candidate.resume_id = resume_id

        elif hasattr(candidate, "resume_ids"):
            resume_ids = list(
                getattr(
                    candidate,
                    "resume_ids",
                    [],
                )
                or []
            )

            if resume_id not in resume_ids:
                resume_ids.append(resume_id)

            candidate.resume_ids = resume_ids

        else:
            raise ValueError(
                "Candidate model does not support resume association."
            )

        if hasattr(candidate, "updated_at"):
            candidate.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(candidate)

        return candidate

    # ================================================================
    # MATCH CANDIDATE WITH JOB
    # ================================================================

    async def calculate_match_score(
        self,
        candidate: Candidate,
        job: Any,
        matcher: Any,
    ) -> dict[str, Any]:
        """Calculate AI-powered candidate/job match score."""

        match_method = getattr(
            matcher,
            "match",
            None,
        )

        if match_method is None:
            raise ValueError(
                "Matcher must provide a match() method."
            )

        try:
            result = match_method(
                candidate=candidate,
                job=job,
            )
        except TypeError:
            result = match_method(
                candidate,
                job,
            )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            match_data = result
        else:
            match_data = {
                "score": float(result)
            }

        score = match_data.get(
            "overall_match_score",
            match_data.get(
                "match_score",
                match_data.get("score"),
            ),
        )

        if score is not None and hasattr(
            candidate,
            "match_score",
        ):
            candidate.match_score = float(score)

        if hasattr(candidate, "updated_at"):
            candidate.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(candidate)

        return match_data

    # ================================================================
    # RANK CANDIDATES
    # ================================================================

    async def rank_candidates(
        self,
        candidates: list[Candidate],
        ranker: Any,
        job: Any = None,
    ) -> list[Any]:
        """Rank candidates using the AI ranking engine."""

        rank_method = getattr(
            ranker,
            "rank",
            None,
        )

        if rank_method is None:
            raise ValueError(
                "Ranker must provide a rank() method."
            )

        try:
            result = rank_method(
                candidates=candidates,
                job=job,
            )
        except TypeError:
            try:
                result = rank_method(
                    candidates,
                    job,
                )
            except TypeError:
                result = rank_method(candidates)

        if hasattr(result, "__await__"):
            result = await result

        return list(result or [])

    # ================================================================
    # COMPARE CANDIDATES
    # ================================================================

    async def compare_candidates(
        self,
        candidates: list[Candidate],
        comparator: Any,
        job: Any = None,
    ) -> dict[str, Any]:
        """Compare two or more candidates."""

        if len(candidates) < 2:
            raise ValueError(
                "At least two candidates are required."
            )

        compare_method = getattr(
            comparator,
            "compare",
            None,
        )

        if compare_method is None:
            raise ValueError(
                "Comparator must provide a compare() method."
            )

        try:
            result = compare_method(
                candidates=candidates,
                job=job,
            )
        except TypeError:
            try:
                result = compare_method(
                    candidates,
                    job,
                )
            except TypeError:
                result = compare_method(candidates)

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "comparison": result
        }

    # ================================================================
    # SEARCH
    # ================================================================

    async def search_candidates(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        job_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Candidate]:
        """Search candidates by name, email, location, etc."""

        term = f"%{search_term.strip()}%"

        conditions = []

        searchable_fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "location",
            "headline",
            "summary",
        )

        for field_name in searchable_fields:

            field = getattr(
                Candidate,
                field_name,
                None,
            )

            if field is not None:
                conditions.append(
                    field.ilike(term)
                )

        if not conditions:
            return []

        query = select(Candidate).where(
            or_(*conditions)
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

        if hasattr(Candidate, "created_at"):
            query = query.order_by(
                Candidate.created_at.desc()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    # ================================================================
    # CANDIDATE STATISTICS
    # ================================================================

    async def get_candidate_statistics(
        self,
        candidate: Candidate,
    ) -> dict[str, Any]:
        """Return candidate scores and recruitment statistics."""

        fields = (
            "match_score",
            "ats_score",
            "interview_score",
            "skill_score",
            "experience_score",
            "education_score",
            "overall_score",
            "ranking_score",
            "years_of_experience",
        )

        statistics = {
            "candidate_id": candidate.id,
            "status": getattr(
                candidate,
                "status",
                None,
            ),
        }

        for field in fields:
            if hasattr(candidate, field):
                statistics[field] = getattr(
                    candidate,
                    field,
                )

        return statistics

    # ================================================================
    # BULK STATUS UPDATE
    # ================================================================

    async def bulk_update_status(
        self,
        candidate_ids: list[int],
        status: str,
        user_id: Optional[int] = None,
    ) -> int:
        """Update status for multiple candidates."""

        if not candidate_ids:
            return 0

        normalized_status = status.strip().lower()

        if normalized_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid candidate status: {status}"
            )

        query = select(Candidate).where(
            Candidate.id.in_(candidate_ids)
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        result = await self.db.execute(query)

        candidates = list(
            result.scalars().all()
        )

        now = datetime.now(timezone.utc)

        for candidate in candidates:

            if hasattr(candidate, "status"):
                candidate.status = normalized_status

            if hasattr(candidate, "updated_at"):
                candidate.updated_at = now

            if (
                normalized_status == "hired"
                and hasattr(candidate, "hired_at")
            ):
                candidate.hired_at = now

            if (
                normalized_status == "rejected"
                and hasattr(candidate, "rejected_at")
            ):
                candidate.rejected_at = now

        await self.db.commit()

        return len(candidates)

    # ================================================================
    # DELETE
    # ================================================================

    async def delete_candidate(
        self,
        candidate: Candidate,
    ) -> bool:
        """Delete candidate."""

        await self.db.delete(candidate)

        await self.db.commit()

        return True
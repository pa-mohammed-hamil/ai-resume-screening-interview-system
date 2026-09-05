# backend/app/services/copilot_service.py

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume


class CopilotService:
    """Service layer for the AI Recruiter Copilot."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ================================================================
    # ASK COPILOT
    # ================================================================

    async def ask(
        self,
        user_id: int,
        message: str,
        copilot: Any,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Send a recruiter question to the AI Copilot.

        The copilot may use:
        - LLM
        - RAG
        - recruiter context
        - candidate information
        - job information
        - interview information
        """

        if not message or not message.strip():
            raise ValueError(
                "Copilot message cannot be empty."
            )

        context = context or {}

        ask_method = getattr(
            copilot,
            "ask",
            None,
        )

        if ask_method is None:
            ask_method = getattr(
                copilot,
                "chat",
                None,
            )

        if ask_method is None:
            raise ValueError(
                "Copilot must provide ask() or chat()."
            )

        try:
            result = ask_method(
                user_id=user_id,
                message=message.strip(),
                context=context,
            )
        except TypeError:
            try:
                result = ask_method(
                    message=message.strip(),
                    context=context,
                )
            except TypeError:
                result = ask_method(
                    message.strip()
                )

        if hasattr(result, "__await__"):
            result = await result

        return self._normalize_response(
            result
        )

    # ================================================================
    # BUILD RECRUITER CONTEXT
    # ================================================================

    async def build_context(
        self,
        user_id: int,
        candidate_id: Optional[int] = None,
        job_id: Optional[int] = None,
        resume_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Build context for the Recruiter Copilot.

        This context can be passed to the LLM/RAG pipeline.
        """

        context: dict[str, Any] = {
            "user_id": user_id,
        }

        if candidate_id is not None:

            candidate = await self._get_candidate(
                candidate_id,
                user_id,
            )

            if candidate:
                context["candidate"] = (
                    self._serialize_model(
                        candidate
                    )
                )

        if job_id is not None:

            job = await self._get_job(
                job_id,
                user_id,
            )

            if job:
                context["job"] = (
                    self._serialize_model(
                        job
                    )
                )

        if resume_id is not None:

            resume = await self._get_resume(
                resume_id,
                user_id,
            )

            if resume:
                context["resume"] = (
                    self._serialize_model(
                        resume
                    )
                )

        return context

    # ================================================================
    # ASK WITH CANDIDATE CONTEXT
    # ================================================================

    async def ask_about_candidate(
        self,
        user_id: int,
        candidate_id: int,
        message: str,
        copilot: Any,
    ) -> dict[str, Any]:
        """Ask Copilot about a specific candidate."""

        context = await self.build_context(
            user_id=user_id,
            candidate_id=candidate_id,
        )

        if "candidate" not in context:
            raise ValueError(
                "Candidate not found."
            )

        return await self.ask(
            user_id=user_id,
            message=message,
            copilot=copilot,
            context=context,
        )

    # ================================================================
    # ASK ABOUT JOB
    # ================================================================

    async def ask_about_job(
        self,
        user_id: int,
        job_id: int,
        message: str,
        copilot: Any,
    ) -> dict[str, Any]:
        """Ask Copilot about a specific job."""

        context = await self.build_context(
            user_id=user_id,
            job_id=job_id,
        )

        if "job" not in context:
            raise ValueError(
                "Job not found."
            )

        return await self.ask(
            user_id=user_id,
            message=message,
            copilot=copilot,
            context=context,
        )

    # ================================================================
    # MATCH CANDIDATE TO JOB
    # ================================================================

    async def match_candidate_to_job(
        self,
        user_id: int,
        candidate_id: int,
        job_id: int,
        matcher: Any,
    ) -> dict[str, Any]:
        """
        Ask the matching engine to compare a candidate
        against a job description.
        """

        candidate = await self._get_candidate(
            candidate_id,
            user_id,
        )

        if candidate is None:
            raise ValueError(
                "Candidate not found."
            )

        job = await self._get_job(
            job_id,
            user_id,
        )

        if job is None:
            raise ValueError(
                "Job not found."
            )

        match_method = getattr(
            matcher,
            "match",
            None,
        )

        if match_method is None:
            raise ValueError(
                "Matcher must provide match()."
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
            return result

        return {
            "match_score": float(result)
        }

    # ================================================================
    # CANDIDATE RECOMMENDATIONS
    # ================================================================

    async def recommend_candidates(
        self,
        user_id: int,
        job_id: int,
        recommender: Any,
        limit: int = 10,
    ) -> list[Any]:
        """
        Recommend the best candidates for a job.
        """

        if limit < 1:
            raise ValueError(
                "Limit must be greater than zero."
            )

        job = await self._get_job(
            job_id,
            user_id,
        )

        if job is None:
            raise ValueError(
                "Job not found."
            )

        candidates = await self._get_job_candidates(
            job_id=job_id,
            user_id=user_id,
        )

        recommend_method = getattr(
            recommender,
            "recommend",
            None,
        )

        if recommend_method is None:
            recommend_method = getattr(
                recommender,
                "rank",
                None,
            )

        if recommend_method is None:
            raise ValueError(
                "Recommender must provide recommend() or rank()."
            )

        try:
            result = recommend_method(
                candidates=candidates,
                job=job,
                limit=limit,
            )
        except TypeError:
            try:
                result = recommend_method(
                    candidates,
                    job,
                )
            except TypeError:
                result = recommend_method(
                    candidates
                )

        if hasattr(result, "__await__"):
            result = await result

        return list(result or [])[:limit]

    # ================================================================
    # SCREENING SUMMARY
    # ================================================================

    async def generate_screening_summary(
        self,
        user_id: int,
        candidate_id: int,
        summarizer: Any,
    ) -> dict[str, Any]:
        """Generate an AI screening summary for a candidate."""

        candidate = await self._get_candidate(
            candidate_id,
            user_id,
        )

        if candidate is None:
            raise ValueError(
                "Candidate not found."
            )

        summarize_method = getattr(
            summarizer,
            "summarize",
            None,
        )

        if summarize_method is None:
            summarize_method = getattr(
                summarizer,
                "generate",
                None,
            )

        if summarize_method is None:
            raise ValueError(
                "Summarizer must provide summarize() or generate()."
            )

        try:
            result = summarize_method(
                candidate=candidate
            )
        except TypeError:
            result = summarize_method(
                candidate
            )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "summary": result
        }

    # ================================================================
    # RESUME IMPROVEMENT SUGGESTIONS
    # ================================================================

    async def get_resume_suggestions(
        self,
        user_id: int,
        resume_id: int,
        optimizer: Any,
        job_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Generate AI suggestions for improving a resume.
        """

        resume = await self._get_resume(
            resume_id,
            user_id,
        )

        if resume is None:
            raise ValueError(
                "Resume not found."
            )

        job = None

        if job_id is not None:

            job = await self._get_job(
                job_id,
                user_id,
            )

            if job is None:
                raise ValueError(
                    "Job not found."
                )

        optimize_method = getattr(
            optimizer,
            "suggest",
            None,
        )

        if optimize_method is None:
            optimize_method = getattr(
                optimizer,
                "optimize",
                None,
            )

        if optimize_method is None:
            raise ValueError(
                "Optimizer must provide suggest() or optimize()."
            )

        try:
            result = optimize_method(
                resume=resume,
                job=job,
            )
        except TypeError:
            try:
                result = optimize_method(
                    resume,
                    job,
                )
            except TypeError:
                result = optimize_method(
                    resume
                )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "suggestions": result
        }

    # ================================================================
    # JD INSIGHTS
    # ================================================================

    async def analyze_job_description(
        self,
        user_id: int,
        job_id: int,
        jd_analyzer: Any,
    ) -> dict[str, Any]:
        """Generate AI insights for a job description."""

        job = await self._get_job(
            job_id,
            user_id,
        )

        if job is None:
            raise ValueError(
                "Job not found."
            )

        analyze_method = getattr(
            jd_analyzer,
            "analyze",
            None,
        )

        if analyze_method is None:
            raise ValueError(
                "JD analyzer must provide analyze()."
            )

        try:
            result = analyze_method(
                job=job
            )
        except TypeError:
            result = analyze_method(
                job
            )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "analysis": result
        }

    # ================================================================
    # COPILOT ACTION
    # ================================================================

    async def execute_action(
        self,
        user_id: int,
        action: str,
        parameters: Optional[dict[str, Any]],
        action_handler: Any,
    ) -> dict[str, Any]:
        """
        Execute a Copilot action.

        Example actions:
        - shortlist_candidate
        - reject_candidate
        - schedule_interview
        - analyze_resume
        - rank_candidates
        - create_job
        """

        if not action or not action.strip():
            raise ValueError(
                "Action cannot be empty."
            )

        parameters = parameters or {}

        normalized_action = (
            action.strip().lower()
        )

        execute_method = getattr(
            action_handler,
            "execute",
            None,
        )

        if execute_method is None:
            raise ValueError(
                "Action handler must provide execute()."
            )

        try:
            result = execute_method(
                user_id=user_id,
                action=normalized_action,
                parameters=parameters,
            )
        except TypeError:
            try:
                result = execute_method(
                    normalized_action,
                    parameters,
                )
            except TypeError:
                result = execute_method(
                    normalized_action
                )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "action": normalized_action,
            "result": result,
        }

    # ================================================================
    # RAG SEARCH
    # ================================================================

    async def retrieve_context(
        self,
        query: str,
        retriever: Any,
        top_k: int = 5,
    ) -> list[Any]:
        """
        Retrieve relevant documents for Copilot using RAG.
        """

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than zero."
            )

        retrieve_method = getattr(
            retriever,
            "retrieve",
            None,
        )

        if retrieve_method is None:
            retrieve_method = getattr(
                retriever,
                "search",
                None,
            )

        if retrieve_method is None:
            raise ValueError(
                "Retriever must provide retrieve() or search()."
            )

        try:
            result = retrieve_method(
                query=query.strip(),
                top_k=top_k,
            )
        except TypeError:
            result = retrieve_method(
                query.strip(),
                top_k,
            )

        if hasattr(result, "__await__"):
            result = await result

        return list(result or [])

    # ================================================================
    # RECOMMENDATIONS
    # ================================================================

    async def get_recommendations(
        self,
        user_id: int,
        context: dict[str, Any],
        recommendation_engine: Any,
    ) -> list[Any]:
        """Generate proactive recruiter recommendations."""

        recommend_method = getattr(
            recommendation_engine,
            "recommend",
            None,
        )

        if recommend_method is None:
            raise ValueError(
                "Recommendation engine must provide recommend()."
            )

        try:
            result = recommend_method(
                user_id=user_id,
                context=context,
            )
        except TypeError:
            try:
                result = recommend_method(
                    context=context
                )
            except TypeError:
                result = recommend_method(
                    context
                )

        if hasattr(result, "__await__"):
            result = await result

        return list(result or [])

    # ================================================================
    # CONVERSATION RESPONSE NORMALIZER
    # ================================================================

    @staticmethod
    def _normalize_response(
        result: Any,
    ) -> dict[str, Any]:
        """Normalize different LLM response formats."""

        if isinstance(result, dict):

            response = dict(result)

            response.setdefault(
                "timestamp",
                datetime.now(
                    timezone.utc
                ).isoformat(),
            )

            return response

        return {
            "answer": str(result),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    # ================================================================
    # DATABASE HELPERS
    # ================================================================

    async def _get_candidate(
        self,
        candidate_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Candidate]:
        """Get candidate owned by recruiter."""

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

    async def _get_job(
        self,
        job_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Job]:
        """Get job owned by recruiter."""

        query = select(Job).where(
            Job.id == job_id
        )

        if user_id is not None and hasattr(
            Job,
            "user_id",
        ):
            query = query.where(
                Job.user_id == user_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def _get_resume(
        self,
        resume_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Resume]:
        """Get resume owned by recruiter."""

        query = select(Resume).where(
            Resume.id == resume_id
        )

        if user_id is not None and hasattr(
            Resume,
            "user_id",
        ):
            query = query.where(
                Resume.user_id == user_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def _get_job_candidates(
        self,
        job_id: int,
        user_id: Optional[int] = None,
    ) -> list[Candidate]:
        """Get candidates associated with a job."""

        query = select(Candidate).where(
            Candidate.job_id == job_id
        )

        if user_id is not None and hasattr(
            Candidate,
            "user_id",
        ):
            query = query.where(
                Candidate.user_id == user_id
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ================================================================
    # MODEL SERIALIZATION
    # ================================================================

    @staticmethod
    def _serialize_model(
        model: Any,
    ) -> dict[str, Any]:
        """
        Convert a SQLAlchemy model into a simple dictionary.

        Sensitive/internal fields can be excluded here.
        """

        excluded_fields = {
            "password",
            "hashed_password",
            "password_hash",
            "secret",
            "access_token",
            "refresh_token",
        }

        data: dict[str, Any] = {}

        mapper = getattr(
            model,
            "__table__",
            None,
        )

        if mapper is None:
            return data

        for column in mapper.columns:

            name = column.name

            if name in excluded_fields:
                continue

            value = getattr(
                model,
                name,
                None,
            )

            if isinstance(
                value,
                datetime,
            ):
                value = value.isoformat()

            data[name] = value

        return data
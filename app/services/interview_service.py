# backend/app/services/interview_service.py

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview


class InterviewService:
    """Business logic for AI-powered interview management."""

    VALID_STATUSES = {
        "scheduled",
        "in_progress",
        "completed",
        "cancelled",
        "expired",
    }

    VALID_TYPES = {
        "technical",
        "behavioral",
        "mixed",
        "hr",
        "screening",
        "voice",
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    # ================================================================
    # INTERVIEW LOOKUP
    # ================================================================

    async def get_interview_by_id(
        self,
        interview_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Interview]:
        """Get an interview by ID."""

        query = select(Interview).where(
            Interview.id == interview_id
        )

        if user_id is not None and hasattr(
            Interview,
            "user_id",
        ):
            query = query.where(
                Interview.user_id == user_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ================================================================
    # GET INTERVIEWS
    # ================================================================

    async def get_interviews(
        self,
        user_id: Optional[int] = None,
        candidate_id: Optional[int] = None,
        job_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Interview]:
        """Get interviews with filters and pagination."""

        query = select(Interview)

        if user_id is not None and hasattr(
            Interview,
            "user_id",
        ):
            query = query.where(
                Interview.user_id == user_id
            )

        if candidate_id is not None and hasattr(
            Interview,
            "candidate_id",
        ):
            query = query.where(
                Interview.candidate_id == candidate_id
            )

        if job_id is not None and hasattr(
            Interview,
            "job_id",
        ):
            query = query.where(
                Interview.job_id == job_id
            )

        if status is not None and hasattr(
            Interview,
            "status",
        ):
            query = query.where(
                Interview.status == status
            )

        if hasattr(Interview, "scheduled_at"):
            query = query.order_by(
                Interview.scheduled_at.desc()
            )
        elif hasattr(Interview, "created_at"):
            query = query.order_by(
                Interview.created_at.desc()
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())

    # ================================================================
    # COUNT INTERVIEWS
    # ================================================================

    async def count_interviews(
        self,
        user_id: Optional[int] = None,
        candidate_id: Optional[int] = None,
        job_id: Optional[int] = None,
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

        if candidate_id is not None and hasattr(
            Interview,
            "candidate_id",
        ):
            query = query.where(
                Interview.candidate_id == candidate_id
            )

        if job_id is not None and hasattr(
            Interview,
            "job_id",
        ):
            query = query.where(
                Interview.job_id == job_id
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
    # CREATE INTERVIEW
    # ================================================================

    async def create_interview(
        self,
        user_id: int,
        candidate_id: int,
        job_id: Optional[int] = None,
        interview_type: str = "mixed",
        scheduled_at: Optional[datetime] = None,
        **interview_data: Any,
    ) -> Interview:
        """Create an interview."""

        normalized_type = interview_type.strip().lower()

        if normalized_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid interview type: {interview_type}"
            )

        data = dict(interview_data)

        data["user_id"] = user_id
        data["candidate_id"] = candidate_id
        data["interview_type"] = normalized_type

        if job_id is not None:
            data["job_id"] = job_id

        if scheduled_at is not None:
            data["scheduled_at"] = scheduled_at

        data.setdefault(
            "status",
            "scheduled",
        )

        interview = Interview(**data)

        self.db.add(interview)

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ================================================================
    # UPDATE INTERVIEW
    # ================================================================

    async def update_interview(
        self,
        interview: Interview,
        updates: dict[str, Any],
    ) -> Interview:
        """Update interview information."""

        protected_fields = {
            "id",
            "user_id",
            "created_at",
        }

        for field, value in updates.items():

            if field in protected_fields:
                continue

            if not hasattr(interview, field):
                continue

            if isinstance(value, str):
                value = value.strip()

            setattr(
                interview,
                field,
                value,
            )

        if hasattr(interview, "updated_at"):
            interview.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ================================================================
    # SCHEDULE INTERVIEW
    # ================================================================

    async def schedule_interview(
        self,
        interview: Interview,
        scheduled_at: datetime,
    ) -> Interview:
        """Schedule an interview."""

        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(
                tzinfo=timezone.utc
            )

        if hasattr(interview, "scheduled_at"):
            interview.scheduled_at = scheduled_at

        if hasattr(interview, "status"):
            interview.status = "scheduled"

        if hasattr(interview, "updated_at"):
            interview.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ================================================================
    # START INTERVIEW
    # ================================================================

    async def start_interview(
        self,
        interview: Interview,
    ) -> Interview:
        """Start an interview session."""

        if hasattr(interview, "status"):
            interview.status = "in_progress"

        now = datetime.now(timezone.utc)

        if hasattr(interview, "started_at"):
            interview.started_at = now

        if hasattr(interview, "updated_at"):
            interview.updated_at = now

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ================================================================
    # COMPLETE INTERVIEW
    # ================================================================

    async def complete_interview(
        self,
        interview: Interview,
        final_score: Optional[float] = None,
    ) -> Interview:
        """Complete an interview session."""

        if hasattr(interview, "status"):
            interview.status = "completed"

        now = datetime.now(timezone.utc)

        if hasattr(interview, "completed_at"):
            interview.completed_at = now

        if final_score is not None:
            if not 0 <= final_score <= 100:
                raise ValueError(
                    "Final score must be between 0 and 100."
                )

            if hasattr(interview, "final_score"):
                interview.final_score = final_score

            elif hasattr(interview, "overall_score"):
                interview.overall_score = final_score

        if hasattr(interview, "updated_at"):
            interview.updated_at = now

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ================================================================
    # CANCEL INTERVIEW
    # ================================================================

    async def cancel_interview(
        self,
        interview: Interview,
        reason: Optional[str] = None,
    ) -> Interview:
        """Cancel an interview."""

        if hasattr(interview, "status"):
            interview.status = "cancelled"

        if reason is not None and hasattr(
            interview,
            "cancellation_reason",
        ):
            interview.cancellation_reason = reason

        if hasattr(interview, "cancelled_at"):
            interview.cancelled_at = datetime.now(
                timezone.utc
            )

        if hasattr(interview, "updated_at"):
            interview.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)

        return interview

    # ================================================================
    # GENERATE QUESTIONS
    # ================================================================

    async def generate_questions(
        self,
        interview: Interview,
        question_generator: Any,
        candidate: Any = None,
        job: Any = None,
        count: int = 10,
    ) -> list[Any]:
        """Generate AI interview questions."""

        if count < 1:
            raise ValueError(
                "Question count must be at least 1."
            )

        generate_method = getattr(
            question_generator,
            "generate",
            None,
        )

        if generate_method is None:
            raise ValueError(
                "Question generator must provide generate()."
            )

        try:
            result = generate_method(
                interview=interview,
                candidate=candidate,
                job=job,
                count=count,
            )
        except TypeError:
            try:
                result = generate_method(
                    candidate=candidate,
                    job=job,
                    count=count,
                )
            except TypeError:
                result = generate_method(
                    count=count
                )

        if hasattr(result, "__await__"):
            result = await result

        questions = list(result or [])

        if hasattr(interview, "questions"):
            interview.questions = questions

        if hasattr(interview, "question_count"):
            interview.question_count = len(questions)

        if hasattr(interview, "updated_at"):
            interview.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)

        return questions

    # ================================================================
    # EVALUATE ANSWER
    # ================================================================

    async def evaluate_answer(
        self,
        interview: Interview,
        question: Any,
        answer: str,
        evaluator: Any,
    ) -> dict[str, Any]:
        """Evaluate an interview answer using AI."""

        if not answer or not answer.strip():
            raise ValueError(
                "Answer cannot be empty."
            )

        evaluate_method = getattr(
            evaluator,
            "evaluate",
            None,
        )

        if evaluate_method is None:
            raise ValueError(
                "Evaluator must provide evaluate()."
            )

        try:
            result = evaluate_method(
                interview=interview,
                question=question,
                answer=answer,
            )
        except TypeError:
            result = evaluate_method(
                question,
                answer,
            )

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            evaluation = result
        else:
            evaluation = {
                "score": float(result)
            }

        await self._append_answer(
            interview,
            question,
            answer,
            evaluation,
        )

        return evaluation

    # ================================================================
    # ADAPTIVE NEXT QUESTION
    # ================================================================

    async def get_next_question(
        self,
        interview: Interview,
        adaptive_engine: Any,
        previous_answer: Optional[str] = None,
        previous_evaluation: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Generate the next adaptive interview question."""

        next_method = getattr(
            adaptive_engine,
            "next_question",
            None,
        )

        if next_method is None:
            next_method = getattr(
                adaptive_engine,
                "generate_next",
                None,
            )

        if next_method is None:
            raise ValueError(
                "Adaptive engine must provide next_question()."
            )

        try:
            result = next_method(
                interview=interview,
                previous_answer=previous_answer,
                previous_evaluation=previous_evaluation,
            )
        except TypeError:
            result = next_method(interview)

        if hasattr(result, "__await__"):
            result = await result

        return result

    # ================================================================
    # SCORE INTERVIEW
    # ================================================================

    async def calculate_score(
        self,
        interview: Interview,
        evaluator: Any,
    ) -> dict[str, Any]:
        """Calculate the overall interview score."""

        score_method = getattr(
            evaluator,
            "calculate_score",
            None,
        )

        if score_method is None:
            score_method = getattr(
                evaluator,
                "score",
                None,
            )

        if score_method is None:
            raise ValueError(
                "Evaluator must provide score() or calculate_score()."
            )

        try:
            result = score_method(
                interview=interview
            )
        except TypeError:
            result = score_method(interview)

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            score_data = result
        else:
            score_data = {
                "overall_score": float(result)
            }

        score = score_data.get(
            "overall_score",
            score_data.get(
                "final_score",
                score_data.get("score"),
            ),
        )

        if score is not None:

            score = float(score)

            if not 0 <= score <= 100:
                raise ValueError(
                    "Interview score must be between 0 and 100."
                )

            if hasattr(interview, "final_score"):
                interview.final_score = score

            elif hasattr(interview, "overall_score"):
                interview.overall_score = score

        if hasattr(interview, "score_data"):
            interview.score_data = score_data

        if hasattr(interview, "updated_at"):
            interview.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)

        return score_data

    # ================================================================
    # VOICE INTERVIEW
    # ================================================================

    async def process_voice_answer(
        self,
        interview: Interview,
        audio_path: str,
        speech_to_text: Any,
        evaluator: Any = None,
        question: Any = None,
    ) -> dict[str, Any]:
        """Process an audio answer."""

        if not audio_path:
            raise ValueError(
                "Audio path is required."
            )

        transcribe_method = getattr(
            speech_to_text,
            "transcribe",
            None,
        )

        if transcribe_method is None:
            raise ValueError(
                "Speech-to-text service must provide transcribe()."
            )

        result = transcribe_method(audio_path)

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            transcription = result
            text = result.get(
                "text",
                "",
            )
        else:
            text = str(result)
            transcription = {
                "text": text
            }

        response = {
            "transcription": transcription,
        }

        if evaluator is not None and text:

            evaluation = await self.evaluate_answer(
                interview=interview,
                question=question,
                answer=text,
                evaluator=evaluator,
            )

            response["evaluation"] = evaluation

        return response

    # ================================================================
    # REPORT GENERATION
    # ================================================================

    async def generate_report(
        self,
        interview: Interview,
        report_generator: Any,
    ) -> dict[str, Any]:
        """Generate the final AI interview report."""

        generate_method = getattr(
            report_generator,
            "generate",
            None,
        )

        if generate_method is None:
            raise ValueError(
                "Report generator must provide generate()."
            )

        try:
            result = generate_method(
                interview=interview
            )
        except TypeError:
            result = generate_method(interview)

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            report = result
        else:
            report = {
                "report": result
            }

        if hasattr(interview, "report_data"):
            interview.report_data = report

        if hasattr(interview, "report_generated_at"):
            interview.report_generated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)

        return report

    # ================================================================
    # INTERVIEW STATISTICS
    # ================================================================

    async def get_interview_statistics(
        self,
        interview: Interview,
    ) -> dict[str, Any]:
        """Return interview scores and metadata."""

        statistics = {
            "interview_id": interview.id,
            "status": getattr(
                interview,
                "status",
                None,
            ),
            "interview_type": getattr(
                interview,
                "interview_type",
                None,
            ),
            "candidate_id": getattr(
                interview,
                "candidate_id",
                None,
            ),
            "job_id": getattr(
                interview,
                "job_id",
                None,
            ),
        }

        fields = (
            "final_score",
            "overall_score",
            "technical_score",
            "communication_score",
            "confidence_score",
            "behavioral_score",
            "question_count",
            "answered_count",
            "duration",
            "duration_seconds",
        )

        for field in fields:
            if hasattr(interview, field):
                statistics[field] = getattr(
                    interview,
                    field,
                )

        return statistics

    # ================================================================
    # DELETE
    # ================================================================

    async def delete_interview(
        self,
        interview: Interview,
    ) -> bool:
        """Delete an interview."""

        await self.db.delete(interview)

        await self.db.commit()

        return True

    # ================================================================
    # INTERNAL: STORE ANSWER
    # ================================================================

    async def _append_answer(
        self,
        interview: Interview,
        question: Any,
        answer: str,
        evaluation: dict[str, Any],
    ) -> None:
        """Store an answer and evaluation when supported by the model."""

        if not hasattr(interview, "answers"):
            return

        answers = list(
            getattr(
                interview,
                "answers",
                [],
            )
            or []
        )

        answers.append(
            {
                "question": question,
                "answer": answer,
                "evaluation": evaluation,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        )

        interview.answers = answers

        if hasattr(interview, "answered_count"):
            interview.answered_count = len(answers)

        if hasattr(interview, "updated_at"):
            interview.updated_at = datetime.now(
                timezone.utc
            )

        await self.db.commit()
        await self.db.refresh(interview)
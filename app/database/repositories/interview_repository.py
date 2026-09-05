"""Repository for interview database operations."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview


class InterviewRepository:
    """Data-access layer for interviews."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        interview_id: str,
    ) -> Optional[Interview]:
        result = await self.db.execute(
            select(Interview).where(
                Interview.id == interview_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_candidate_id(
        self,
        candidate_id: str,
    ) -> List[Interview]:
        result = await self.db.execute(
            select(Interview)
            .where(
                Interview.candidate_id == candidate_id
            )
            .order_by(Interview.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_job_id(
        self,
        job_id: str,
    ) -> List[Interview]:
        result = await self.db.execute(
            select(Interview)
            .where(Interview.job_id == job_id)
            .order_by(Interview.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        interview: Interview,
    ) -> Interview:
        self.db.add(interview)
        await self.db.commit()
        await self.db.refresh(interview)
        return interview

    async def update(
        self,
        interview: Interview,
    ) -> Interview:
        self.db.add(interview)
        await self.db.commit()
        await self.db.refresh(interview)
        return interview

    async def delete(
        self,
        interview: Interview,
    ) -> None:
        await self.db.delete(interview)
        await self.db.commit()

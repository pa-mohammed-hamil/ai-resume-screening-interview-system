"""Repository for job database operations."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    """Data-access layer for jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, job_id: str) -> Optional[Job]:
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> List[Job]:
        result = await self.db.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, job: Job) -> Job:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def update(self, job: Job) -> Job:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def delete(self, job: Job) -> None:
        await self.db.delete(job)
        await self.db.commit()

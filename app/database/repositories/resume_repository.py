"""Repository for resume database operations."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    """Data-access layer for resumes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, resume_id: str) -> Optional[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> List[Resume]:
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def update(self, resume: Resume) -> Resume:
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def delete(self, resume: Resume) -> None:
        await self.db.delete(resume)
        await self.db.commit()

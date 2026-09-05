"""Repository for candidate database operations."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate


class CandidateRepository:
    """Data-access layer for candidates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        candidate_id: str,
    ) -> Optional[Candidate]:
        result = await self.db.execute(
            select(Candidate).where(
                Candidate.id == candidate_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Candidate]:
        result = await self.db.execute(
            select(Candidate).order_by(
                Candidate.created_at.desc()
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        candidate: Candidate,
    ) -> Candidate:
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def update(
        self,
        candidate: Candidate,
    ) -> Candidate:
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def delete(
        self,
        candidate: Candidate,
    ) -> None:
        await self.db.delete(candidate)
        await self.db.commit()

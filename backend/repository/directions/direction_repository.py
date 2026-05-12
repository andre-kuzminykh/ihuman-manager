"""
## Трассируемость
Feature: F009
Scenarios: SC022, SC023, SC024
"""

from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.directions.direction_model import DirectionModel
from repository.base_repository import BaseRepository


class DirectionRepository(BaseRepository[DirectionModel]):
    def __init__(self) -> None:
        super().__init__(DirectionModel)

    async def list_for_user(self, session: AsyncSession, user_id: int) -> list[DirectionModel]:
        stmt = (
            select(DirectionModel)
            .where(DirectionModel.user_id == user_id)
            .order_by(DirectionModel.name.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_name(
        self, session: AsyncSession, user_id: int, name: str
    ) -> DirectionModel | None:
        stmt = select(DirectionModel).where(
            and_(
                DirectionModel.user_id == user_id,
                func.lower(DirectionModel.name) == name.strip().lower(),
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def favorite_ids_for_user(self, session: AsyncSession, user_id: int) -> list[int]:
        stmt = select(DirectionModel.id).where(
            and_(DirectionModel.user_id == user_id, DirectionModel.is_favorite.is_(True))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

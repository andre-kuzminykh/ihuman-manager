"""
## Трассируемость
Feature: F020
"""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.people.person_model import PersonModel
from repository.base_repository import BaseRepository


class PersonRepository(BaseRepository[PersonModel]):
    def __init__(self) -> None:
        super().__init__(PersonModel)

    async def get_by_telegram_id(
        self, session: AsyncSession, telegram_user_id: int
    ) -> PersonModel | None:
        result = await session.execute(
            select(PersonModel).where(PersonModel.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def find_by_username(
        self, session: AsyncSession, username: str
    ) -> PersonModel | None:
        result = await session.execute(
            select(PersonModel).where(PersonModel.username == username)
        )
        return result.scalar_one_or_none()

    async def list_all(self, session: AsyncSession) -> list[PersonModel]:
        result = await session.execute(
            select(PersonModel).order_by(PersonModel.last_seen_at.desc().nullslast())
        )
        return list(result.scalars().all())

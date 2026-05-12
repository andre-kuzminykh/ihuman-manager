"""
BaseRepository — generic CRUD на базе SQLAlchemy AsyncSession.
"""

from __future__ import annotations

from typing import Generic, Type, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.base_model import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]) -> None:
        self.model = model

    async def get_by_id(self, session: AsyncSession, obj_id: int) -> T | None:
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[T]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, **kwargs) -> T:
        obj = self.model(**kwargs)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: int) -> int:
        result = await session.execute(delete(self.model).where(self.model.id == obj_id))
        return result.rowcount or 0

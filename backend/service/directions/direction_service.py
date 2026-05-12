"""
DirectionService.

## Трассируемость
Feature: F009
Scenarios: SC022, SC023, SC024
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import ConflictError, NotFoundError, ValidationError
from model.directions.direction_model import DirectionModel
from repository.directions.direction_repository import DirectionRepository


class DirectionService:
    def __init__(self, repo: DirectionRepository | None = None) -> None:
        self._repo = repo or DirectionRepository()

    async def create(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        name: str,
        is_favorite: bool = False,
    ) -> DirectionModel:
        cleaned = (name or "").strip()
        if not cleaned:
            raise ValidationError("Имя направления не может быть пустым")
        existing = await self._repo.get_by_user_name(session, user_id, cleaned)
        if existing is not None:
            raise ConflictError("Direction already exists")
        return await self._repo.create(
            session, user_id=user_id, name=cleaned, is_favorite=is_favorite
        )

    async def list_for_user(
        self, session: AsyncSession, user_id: int
    ) -> list[DirectionModel]:
        return await self._repo.list_for_user(session, user_id)

    async def get_or_404(
        self, session: AsyncSession, direction_id: int
    ) -> DirectionModel:
        d = await self._repo.get_by_id(session, direction_id)
        if d is None:
            raise NotFoundError(f"Direction {direction_id} not found")
        return d

    async def update(
        self,
        session: AsyncSession,
        direction_id: int,
        *,
        name: str | None = None,
        is_favorite: bool | None = None,
    ) -> DirectionModel:
        d = await self.get_or_404(session, direction_id)
        if name is not None:
            cleaned = name.strip()
            if not cleaned:
                raise ValidationError("Имя направления не может быть пустым")
            if cleaned.lower() != d.name.lower():
                existing = await self._repo.get_by_user_name(session, d.user_id, cleaned)
                if existing is not None:
                    raise ConflictError("Direction already exists")
            d.name = cleaned
        if is_favorite is not None:
            d.is_favorite = bool(is_favorite)
        await session.flush()
        await session.refresh(d)
        return d

    async def set_favorite(
        self, session: AsyncSession, direction_id: int, *, value: bool
    ) -> DirectionModel:
        return await self.update(session, direction_id, is_favorite=value)

    async def delete(self, session: AsyncSession, direction_id: int) -> None:
        d = await self.get_or_404(session, direction_id)
        await session.delete(d)
        await session.flush()

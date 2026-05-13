"""
## Трассируемость
Feature: F018
Scenarios: SC036, SC037
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.business.business_connection_model import BusinessConnectionModel
from repository.base_repository import BaseRepository


class BusinessConnectionRepository(BaseRepository[BusinessConnectionModel]):
    def __init__(self) -> None:
        super().__init__(BusinessConnectionModel)

    async def get_by_connection_id(
        self, session: AsyncSession, business_connection_id: str
    ) -> BusinessConnectionModel | None:
        stmt = select(BusinessConnectionModel).where(
            BusinessConnectionModel.business_connection_id == business_connection_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

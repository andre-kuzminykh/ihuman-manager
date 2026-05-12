"""
Тест SC024 — дубликат имени направления (case-insensitive) → 409.

## Трассируемость
Feature: F009
Scenario: SC024
"""

import pytest

from core.exceptions import ConflictError
from service.directions.direction_service import DirectionService


@pytest.mark.asyncio
async def test_duplicate_direction_name(async_session):
    service = DirectionService()
    await service.create(async_session, user_id=1, name="Продажи")
    with pytest.raises(ConflictError):
        await service.create(async_session, user_id=1, name="продажи")

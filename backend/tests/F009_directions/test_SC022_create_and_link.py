"""
Тест SC022 — создание направления и привязка к задаче.

## Трассируемость
Feature: F009
Scenario: SC022
"""

from datetime import timedelta

import pytest

from service.directions.direction_service import DirectionService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_create_direction_and_link_task(async_session):
    direction_service = DirectionService()
    task_service = TaskService()

    d = await direction_service.create(async_session, user_id=1, name="Продажи")
    task = await task_service.create_from_text(
        async_session, user_id=1, text="x", deadline=now_msk() + timedelta(days=2)
    )
    updated = await task_service.update(async_session, task.id, direction_id=d.id)
    assert updated.direction_id == d.id

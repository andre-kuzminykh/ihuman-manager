"""
Тест SC032 — ручное создание с явными полями.

## Трассируемость
Feature: F014
Scenario: SC032
"""

from datetime import timedelta

import pytest

from service.directions.direction_service import DirectionService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_manual_create_with_direction(async_session):
    d_service = DirectionService()
    direction = await d_service.create(async_session, user_id=50, name="Личное")

    t_service = TaskService()
    deadline = now_msk() + timedelta(days=1)
    task, is_dup = await t_service.create_or_find_duplicate(
        async_session,
        user_id=50,
        text="Купить молоко",
        title="Купить молоко",
        deadline=deadline,
        direction_id=direction.id,
        force=True,
    )
    assert is_dup is False
    assert task.title == "Купить молоко"
    assert task.direction_id == direction.id
    assert task.deadline == deadline

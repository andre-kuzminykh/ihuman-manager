"""
Тест SC023 — избранное направление → задачи в нём считаются избранными.

## Трассируемость
Feature: F009
Scenario: SC023
"""

from datetime import timedelta

import pytest

from service.directions.direction_service import DirectionService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_favorite_direction_marks_tasks(async_session):
    direction_service = DirectionService()
    task_service = TaskService()

    d = await direction_service.create(async_session, user_id=1, name="Финансы")
    t1 = await task_service.create_from_text(
        async_session, user_id=1, text="a", deadline=now_msk() + timedelta(days=1)
    )
    t2 = await task_service.create_from_text(
        async_session, user_id=1, text="b", deadline=now_msk() + timedelta(days=1)
    )
    await task_service.update(async_session, t1.id, direction_id=d.id)
    await task_service.update(async_session, t2.id, direction_id=d.id)
    await direction_service.set_favorite(async_session, d.id, value=True)

    items = await task_service.list_for_user(async_session, 1, favorite_only=True)
    ids = {t["id"] for t in items}
    assert {t1.id, t2.id}.issubset(ids)

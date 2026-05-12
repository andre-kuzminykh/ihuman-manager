"""
Тест SC010 — удаление из избранного.

## Трассируемость
Feature: F004
Scenario: SC010
"""

from datetime import timedelta

import pytest

from service.tasks.task_favorite_service import TaskFavoriteService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_remove_favorite(client, async_session):
    service = TaskService()
    fav_service = TaskFavoriteService()
    task = await service.create_from_text(
        async_session, user_id=1, text="t", deadline=now_msk() + timedelta(days=2)
    )
    await fav_service.add(async_session, user_id=1, task_id=task.id)
    await async_session.commit()

    response = await client.request(
        "DELETE",
        f"/api/v1/tasks/{task.id}/favorite",
        json={"user_id": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_favorite"] is False

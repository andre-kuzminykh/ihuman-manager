"""
Тест SC009 — добавление задачи в избранное.

## Трассируемость
Feature: F004
Scenario: SC009
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_add_favorite(client, async_session):
    service = TaskService()
    task = await service.create_from_text(
        async_session, user_id=1, text="t", deadline=now_msk() + timedelta(days=2)
    )
    await async_session.commit()

    response = await client.post(
        f"/api/v1/tasks/{task.id}/favorite",
        json={"user_id": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_favorite"] is True

    response = await client.get(
        "/api/v1/tasks", params={"user_id": 1, "favorite_only": True}
    )
    items = response.json()
    assert any(t["id"] == task.id for t in items)

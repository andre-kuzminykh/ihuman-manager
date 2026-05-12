"""
Тест SC018 — утренний дайджест возвращает задачи на день.

## Трассируемость
Feature: F007
Scenario: SC018
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import end_of_msk_day, now_msk


@pytest.mark.asyncio
async def test_digest_returns_tasks(client, async_session):
    service = TaskService()
    today_deadline = end_of_msk_day(now_msk()) - timedelta(hours=1)
    for i in range(3):
        await service.create_from_text(
            async_session, user_id=99, text=f"task {i}", deadline=today_deadline
        )
    await async_session.commit()

    response = await client.get("/api/v1/digest/99")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["is_empty"] is False

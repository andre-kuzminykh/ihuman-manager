"""
Тест SC017 — не повторять уведомление.

## Трассируемость
Feature: F006
Scenario: SC017
"""

from datetime import timedelta

import pytest

from service.scheduler.scheduler_service import SchedulerService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_no_duplicate_deadline_notification(async_session):
    service = TaskService()
    n = now_msk()
    task = await service.create_from_text(
        async_session, user_id=1, text="x", deadline=n - timedelta(minutes=1), now=n
    )
    scheduler = SchedulerService(task_service=service)
    first = await scheduler.tick(async_session, now=n)
    assert any(p["task_id"] == task.id for p in first["deadline_notifications"])

    second = await scheduler.tick(async_session, now=n + timedelta(minutes=5))
    assert not any(p["task_id"] == task.id for p in second["deadline_notifications"])

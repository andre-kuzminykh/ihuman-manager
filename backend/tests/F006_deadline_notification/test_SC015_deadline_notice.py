"""
Тест SC015 — уведомление о дедлайне.

## Трассируемость
Feature: F006
Scenario: SC015
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.scheduler.scheduler_service import SchedulerService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_deadline_notification_emitted(async_session):
    service = TaskService()
    n = now_msk()
    task = await service.create_from_text(
        async_session, user_id=1, text="due now", deadline=n - timedelta(minutes=1), now=n
    )
    await service.transition_status(async_session, task.id, to=TaskStatus.IN_PROGRESS)

    scheduler = SchedulerService(task_service=service)
    result = await scheduler.tick(async_session, now=n)

    notifs = result["deadline_notifications"]
    assert any(p["task_id"] == task.id for p in notifs)

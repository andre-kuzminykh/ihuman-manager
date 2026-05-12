"""
Тест SC007 — backlog → todo автоматически за 7 дней до дедлайна.

## Трассируемость
Feature: F003
Scenario: SC007
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.scheduler.scheduler_service import SchedulerService
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_auto_promote_backlog(async_session):
    service = TaskService()
    n = now_msk()
    # дедлайн через 10 дней → попадает в backlog
    task = await service.create_from_text(
        async_session, user_id=1, text="late task", deadline=n + timedelta(days=10), now=n
    )
    assert task.status == TaskStatus.BACKLOG.value

    # имитируем тик через 4 дня — до дедлайна остаётся <7
    scheduler = SchedulerService(task_service=service)
    result = await scheduler.tick(async_session, now=n + timedelta(days=4))
    assert task.id in result["promoted_task_ids"]

    await async_session.refresh(task)
    assert task.status == TaskStatus.TODO.value

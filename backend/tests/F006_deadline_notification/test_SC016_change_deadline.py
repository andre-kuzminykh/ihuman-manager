"""
Тест SC016 — изменение дедлайна через PUT.

## Трассируемость
Feature: F006
Scenario: SC016
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_change_deadline(async_session):
    service = TaskService()
    n = now_msk()
    task = await service.create_from_text(
        async_session, user_id=1, text="x", deadline=n - timedelta(hours=1), now=n
    )
    new_deadline = n + timedelta(days=1)
    updated = await service.update(async_session, task.id, deadline=new_deadline)
    assert updated.deadline == new_deadline
    assert updated.status in {TaskStatus.TODO.value, TaskStatus.BACKLOG.value, TaskStatus.IN_PROGRESS.value}

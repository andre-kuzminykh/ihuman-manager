"""
Тест SC006 — переход todo → in_progress.

## Трассируемость
Feature: F003
Scenario: SC006
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_todo_to_in_progress(async_session):
    service = TaskService()
    task = await service.create_from_text(
        async_session,
        user_id=1,
        text="Test",
        deadline=now_msk() + timedelta(days=1),
    )
    assert task.status == TaskStatus.TODO.value

    updated = await service.transition_status(
        async_session, task.id, to=TaskStatus.IN_PROGRESS, changed_by=1
    )
    assert updated.status == TaskStatus.IN_PROGRESS.value

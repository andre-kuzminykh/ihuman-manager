"""
Тест SC031 — переход in_progress → blocked.

## Трассируемость
Feature: F013
Scenario: SC031
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_block_in_progress(async_session):
    service = TaskService()
    task = await service.create_from_text(
        async_session, user_id=40, text="x", deadline=now_msk() + timedelta(days=1)
    )
    await service.transition_status(async_session, task.id, to=TaskStatus.IN_PROGRESS)
    updated = await service.transition_status(async_session, task.id, to=TaskStatus.BLOCKED)
    assert updated.status == TaskStatus.BLOCKED.value

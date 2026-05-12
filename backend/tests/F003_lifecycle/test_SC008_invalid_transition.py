"""
Тест SC008 — некорректный переход done → in_progress → ошибка.

## Трассируемость
Feature: F003
Scenario: SC008
"""

from datetime import timedelta

import pytest

from core.exceptions import InvalidTransitionError
from model.enums import TaskStatus
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_invalid_transition_done_to_in_progress(async_session):
    service = TaskService()
    task = await service.create_from_text(
        async_session, user_id=1, text="Test", deadline=now_msk() + timedelta(days=1)
    )
    await service.transition_status(async_session, task.id, to=TaskStatus.IN_PROGRESS)
    await service.transition_status(async_session, task.id, to=TaskStatus.DONE)

    with pytest.raises(InvalidTransitionError):
        await service.transition_status(async_session, task.id, to=TaskStatus.IN_PROGRESS)

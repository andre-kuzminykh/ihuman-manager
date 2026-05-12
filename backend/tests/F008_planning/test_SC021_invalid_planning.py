"""
Тест SC021 — planned_end_at <= planned_start_at → ошибка.

## Трассируемость
Feature: F008
Scenario: SC021
"""

from datetime import timedelta

import pytest

from core.exceptions import ValidationError
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_invalid_planning_raises(async_session):
    service = TaskService()
    task = await service.create_from_text(
        async_session, user_id=1, text="x", deadline=now_msk() + timedelta(days=1)
    )
    start = now_msk() + timedelta(hours=2)
    with pytest.raises(ValidationError):
        await service.update(
            async_session,
            task.id,
            planned_start_at=start,
            planned_end_at=start - timedelta(minutes=1),
        )

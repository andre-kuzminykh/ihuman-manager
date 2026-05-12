"""
Тест SC020 — planned_end_at = planned_start_at + 30 мин по умолчанию.

## Трассируемость
Feature: F008
Scenario: SC020
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_default_duration_30min(async_session):
    service = TaskService()
    task = await service.create_from_text(
        async_session, user_id=1, text="x", deadline=now_msk() + timedelta(days=1)
    )
    start = now_msk() + timedelta(hours=2)
    updated = await service.update(async_session, task.id, planned_start_at=start)
    assert updated.planned_end_at == start + timedelta(minutes=30)

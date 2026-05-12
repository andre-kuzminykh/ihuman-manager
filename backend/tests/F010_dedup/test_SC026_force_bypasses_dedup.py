"""
Тест SC026 — force=True пропускает дедуп.

## Трассируемость
Feature: F010
Scenario: SC026
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_force_creates_new(async_session):
    service = TaskService()
    n = now_msk()
    await service.create_from_text(
        async_session,
        user_id=1,
        text="Подготовить квартальный отчёт",
        deadline=n + timedelta(days=2),
    )
    task, is_dup = await service.create_or_find_duplicate(
        async_session,
        user_id=1,
        text="Подготовить квартальный отчёт",
        deadline=n + timedelta(days=1),
        force=True,
    )
    assert is_dup is False
    assert task.id is not None

"""
Тест SC025 — повторный create возвращает существующую задачу.

## Трассируемость
Feature: F010
Scenario: SC025
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_duplicate_returns_existing(async_session):
    service = TaskService()
    n = now_msk()
    original = await service.create_from_text(
        async_session,
        user_id=1,
        text="Подготовить квартальный отчёт",
        deadline=n + timedelta(days=2),
    )

    task, is_dup = await service.create_or_find_duplicate(
        async_session,
        user_id=1,
        text="подготовить квартальный отчёт сегодня",
        deadline=n + timedelta(days=1),
    )
    assert is_dup is True
    assert task.id == original.id

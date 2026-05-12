"""
Тест SC027 — topic-prefix отсекает разнотемные.

## Трассируемость
Feature: F010
Scenario: SC027
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_different_topics_create_separate(async_session):
    service = TaskService()
    n = now_msk()
    await service.create_from_text(
        async_session,
        user_id=1,
        text="купить молоко",
        deadline=n + timedelta(days=1),
    )
    task, is_dup = await service.create_or_find_duplicate(
        async_session,
        user_id=1,
        text="сделать презу",
        deadline=n + timedelta(days=1),
    )
    assert is_dup is False
    assert task.title.lower().startswith("сделать")

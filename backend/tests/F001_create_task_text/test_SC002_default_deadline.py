"""
Тест SC002 — нет даты в тексте → дедлайн сегодня 18:00 МСК.

## Трассируемость
Feature: F001
Scenario: SC002
"""

import pytest

from model.enums import TaskStatus
from service.tasks.task_service import TaskService


@pytest.mark.asyncio
async def test_default_deadline(async_session, fixed_now):
    service = TaskService()
    task = await service.create_from_text(
        async_session, user_id=42, text="Позвонить Алине", now=fixed_now
    )
    assert task.status == TaskStatus.TODO.value
    d = task.deadline
    assert (d.year, d.month, d.day) == (2026, 5, 12)
    assert d.hour == 18 and d.minute == 0

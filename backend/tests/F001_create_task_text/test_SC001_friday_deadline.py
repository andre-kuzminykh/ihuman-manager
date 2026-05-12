"""
Тест SC001 — текст с дедлайном "до пятницы".

## Трассируемость
Feature: F001
Scenario: SC001

## BDD
Given: сегодня среда 2026-05-12 10:00 МСК
When:  POST /api/v1/tasks с user_id=42, text='Подготовить отчёт до пятницы'
Then:  создана задача с deadline=2026-05-15T18:00 МСК, status='todo'
"""

import pytest

from model.enums import TaskStatus
from service.tasks.task_service import TaskService


@pytest.mark.asyncio
async def test_friday_deadline(async_session, fixed_now):
    service = TaskService()
    task = await service.create_from_text(
        async_session,
        user_id=42,
        text="Подготовить отчёт до пятницы",
        now=fixed_now,
    )
    assert task.title == "Подготовить отчёт до пятницы"
    assert task.status == TaskStatus.TODO.value
    deadline = task.deadline
    assert deadline.day == 15 and deadline.month == 5 and deadline.year == 2026
    assert deadline.hour == 18 and deadline.minute == 0

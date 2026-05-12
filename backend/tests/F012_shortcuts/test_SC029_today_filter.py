"""
Тест SC029 — /today возвращает только задачи сегодня.

## Трассируемость
Feature: F012
Scenario: SC029
"""

from datetime import timedelta

import pytest

from service.tasks.task_service import TaskService
from service.utils.time_utils import end_of_msk_day, now_msk, start_of_msk_day


@pytest.mark.asyncio
async def test_today_filter(async_session):
    service = TaskService()
    n = now_msk()
    today_start = start_of_msk_day(n)
    today_end = end_of_msk_day(n)

    await service.create_from_text(
        async_session, user_id=20, text="yest", deadline=today_start - timedelta(hours=1)
    )
    today_task = await service.create_from_text(
        async_session, user_id=20, text="today", deadline=today_end - timedelta(hours=1)
    )
    await service.create_from_text(
        async_session, user_id=20, text="tomorrow", deadline=today_end + timedelta(days=1)
    )

    items = await service.list_for_user(
        async_session,
        20,
        deadline_after=today_start,
        deadline_before=today_end + timedelta(microseconds=1),
    )
    ids = {t["id"] for t in items}
    assert today_task.id in ids
    assert len(ids) == 1

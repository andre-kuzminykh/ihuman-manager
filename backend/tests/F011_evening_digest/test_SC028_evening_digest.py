"""
Тест SC028 — вечерний дайджест группирует done/in_progress/overdue.

## Трассируемость
Feature: F011
Scenario: SC028
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.digest.digest_service import DigestService
from service.tasks.task_service import TaskService
from service.utils.time_utils import end_of_msk_day, now_msk


@pytest.mark.asyncio
async def test_evening_digest_groups(async_session):
    tasks = TaskService()
    n = now_msk()

    # 1) сделанная сегодня
    done = await tasks.create_from_text(
        async_session, user_id=10, text="done one", deadline=n + timedelta(hours=2)
    )
    await tasks.transition_status(async_session, done.id, to=TaskStatus.IN_PROGRESS)
    await tasks.transition_status(async_session, done.id, to=TaskStatus.DONE)

    # 2) в работе
    wip = await tasks.create_from_text(
        async_session, user_id=10, text="wip two", deadline=n + timedelta(hours=4)
    )
    await tasks.transition_status(async_session, wip.id, to=TaskStatus.IN_PROGRESS)

    # 3) просрочка (deadline в прошлом, статус активный)
    await tasks.create_from_text(
        async_session, user_id=10, text="overdue three", deadline=n - timedelta(hours=1)
    )

    digest = await DigestService().build_evening(async_session, user_id=10)
    assert digest.is_empty is False
    labels = {g.label for g in digest.groups}
    assert "✅ Завершено сегодня" in labels
    assert "🔵 В работе" in labels
    assert "⏱ Просрочено" in labels

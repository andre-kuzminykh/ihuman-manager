"""
Тест SC030 — /overdue показывает только активные просрочки.

## Трассируемость
Feature: F012
Scenario: SC030
"""

from datetime import timedelta

import pytest

from model.enums import TaskStatus
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


@pytest.mark.asyncio
async def test_overdue_excludes_done(async_session):
    service = TaskService()
    n = now_msk()

    done = await service.create_from_text(
        async_session, user_id=30, text="overdue done", deadline=n - timedelta(hours=2)
    )
    await service.transition_status(async_session, done.id, to=TaskStatus.IN_PROGRESS)
    await service.transition_status(async_session, done.id, to=TaskStatus.DONE)

    active_overdue = await service.create_from_text(
        async_session, user_id=30, text="overdue todo", deadline=n - timedelta(hours=1)
    )

    items = await service.list_for_user(
        async_session,
        30,
        deadline_before=n,
        statuses=[TaskStatus.BACKLOG, TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.PAUSED],
    )
    ids = {t["id"] for t in items}
    assert active_overdue.id in ids
    assert done.id not in ids

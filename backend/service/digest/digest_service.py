"""
DigestService — собирает утренний и вечерний дайджест.

## Трассируемость
Feature: F007, F008, F011
Scenarios: SC018, SC019, SC020, SC028
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from model.enums import TaskStatus
from schema.digest.digest_schema import DigestGroupSchema, DigestResponseSchema
from schema.tasks.task_schema import TaskListItemSchema
from service.tasks.task_service import TaskService
from service.utils.time_utils import MSK, end_of_msk_day, start_of_msk_day


class DigestService:
    def __init__(self, task_service: TaskService | None = None) -> None:
        self._task_service = task_service or TaskService()

    async def build(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        day: datetime | None = None,
    ) -> DigestResponseSchema:
        day_start = start_of_msk_day(day)
        day_end = end_of_msk_day(day)

        # Берём задачи: deadline в пределах дня ИЛИ planned_start_at в этом дне.
        tasks_by_deadline = await self._task_service.list_for_user(
            session,
            user_id,
            deadline_before=day_end + timedelta(microseconds=1),
            deadline_after=day_start,
            statuses=[
                TaskStatus.BACKLOG,
                TaskStatus.TODO,
                TaskStatus.IN_PROGRESS,
                TaskStatus.PAUSED,
            ],
        )
        # planned_start_at — фильтруем в Python (не очень частая выборка).
        all_active = await self._task_service.list_for_user(
            session,
            user_id,
            statuses=[
                TaskStatus.BACKLOG,
                TaskStatus.TODO,
                TaskStatus.IN_PROGRESS,
                TaskStatus.PAUSED,
            ],
        )
        merged: dict[int, dict] = {t["id"]: t for t in tasks_by_deadline}
        for t in all_active:
            ps = t.get("planned_start_at")
            if ps and day_start <= ps.astimezone(MSK) <= day_end:
                merged[t["id"]] = t

        items = list(merged.values())
        items.sort(
            key=lambda t: (
                t.get("planned_start_at") or t.get("deadline"),
                t["id"],
            )
        )

        groups_raw: dict[str, list[dict]] = defaultdict(list)
        for t in items:
            label = self._group_label(t["status"])
            groups_raw[label].append(t)

        order = ["В работе", "К сегодня", "Backlog", "Пауза", "Заблокировано"]
        groups = [
            DigestGroupSchema(
                label=label,
                tasks=[TaskListItemSchema(**t) for t in groups_raw.get(label, [])],
            )
            for label in order
            if groups_raw.get(label)
        ]

        return DigestResponseSchema(
            user_id=user_id,
            date=day_start.date(),
            is_empty=not items,
            groups=groups,
            total=len(items),
        )

    @staticmethod
    def _group_label(status: str) -> str:
        if status == TaskStatus.IN_PROGRESS.value:
            return "В работе"
        if status == TaskStatus.TODO.value:
            return "К сегодня"
        if status == TaskStatus.BACKLOG.value:
            return "Backlog"
        if status == TaskStatus.PAUSED.value:
            return "Пауза"
        if status == TaskStatus.BLOCKED.value:
            return "Заблокировано"
        return "Прочее"

    async def build_evening(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        day: datetime | None = None,
    ) -> DigestResponseSchema:
        """Вечерний дайджест: что сделано / в работе / просрочено.

        ## Трассируемость
        Feature: F011
        Scenarios: SC028
        """
        day_start = start_of_msk_day(day)
        day_end = end_of_msk_day(day)

        # Завершено сегодня — completed_at в окне дня.
        done_today = await self._task_service.list_for_user(
            session, user_id, statuses=[TaskStatus.DONE]
        )
        done_today = [
            t
            for t in done_today
            if t.get("completed_at")
            and day_start <= t["completed_at"].astimezone(MSK) <= day_end
        ]

        # В работе.
        in_progress = await self._task_service.list_for_user(
            session, user_id, statuses=[TaskStatus.IN_PROGRESS]
        )

        # Просрочки — активные с deadline < now.
        overdue = await self._task_service.list_for_user(
            session,
            user_id,
            deadline_before=day_end,
            statuses=[
                TaskStatus.BACKLOG,
                TaskStatus.TODO,
                TaskStatus.IN_PROGRESS,
                TaskStatus.PAUSED,
                TaskStatus.BLOCKED,
            ],
        )
        # отфильтруем те, что не на сегодня/раньше
        overdue = [
            t for t in overdue if t.get("deadline") and t["deadline"].astimezone(MSK) <= day_end
        ]

        groups_raw = {
            "✅ Завершено сегодня": done_today,
            "🔵 В работе": in_progress,
            "⏱ Просрочено": [t for t in overdue if t["id"] not in {x["id"] for x in done_today}],
        }
        groups = [
            DigestGroupSchema(label=label, tasks=[TaskListItemSchema(**t) for t in tasks])
            for label, tasks in groups_raw.items()
            if tasks
        ]
        total = sum(len(g.tasks) for g in groups)
        return DigestResponseSchema(
            user_id=user_id,
            date=day_start.date(),
            is_empty=total == 0,
            groups=groups,
            total=total,
        )

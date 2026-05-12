"""
SchedulerService — периодический tick: backlog→todo, дедлайн-уведомления, дайджест.

## Трассируемость
Feature: F003 (SC007), F006 (SC015, SC017), F007 (SC018, SC019)

## Возвращает
Структуру с метриками: списком инициированных уведомлений и переведённых задач.
Бот-клиент потом разошлёт уведомления.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.chats.chat_subscription_model import ChatSubscriptionModel
from model.enums import NotificationKind, TaskStatus
from repository.notifications.notification_log_repository import NotificationLogRepository
from repository.tasks.task_repository import TaskRepository
from service.digest.digest_service import DigestService
from service.tasks.task_service import TaskService
from service.utils.time_utils import (
    MSK,
    end_of_msk_day,
    now_msk,
    start_of_msk_day,
)
from core.config import config


class SchedulerService:
    def __init__(
        self,
        task_service: TaskService | None = None,
        task_repo: TaskRepository | None = None,
        notification_repo: NotificationLogRepository | None = None,
        digest_service: DigestService | None = None,
    ) -> None:
        self._task_service = task_service or TaskService()
        self._task_repo = task_repo or TaskRepository()
        self._notification_repo = notification_repo or NotificationLogRepository()
        self._digest_service = digest_service or DigestService(task_service=self._task_service)

    async def tick(
        self, session: AsyncSession, *, now: datetime | None = None
    ) -> dict[str, Any]:
        n = (now or now_msk()).astimezone(MSK)

        promoted = await self._task_service.promote_backlog_to_todo(session, now=n)

        # Deadline notifications: задачи c deadline ≤ now и status не done/cancelled.
        deadline_candidates = await self._task_repo.list_due_in_window(
            session, not_after=n
        )
        deadline_payload = []
        for task in deadline_candidates:
            already = await self._notification_repo.exists_for_task(
                session, task_id=task.id, kind=NotificationKind.DEADLINE.value
            )
            if already:
                continue
            await self._notification_repo.add(
                session,
                user_id=task.user_id,
                task_id=task.id,
                kind=NotificationKind.DEADLINE.value,
            )
            deadline_payload.append(
                {
                    "user_id": task.user_id,
                    "task_id": task.id,
                    "title": task.title,
                    "deadline": task.deadline.isoformat(),
                }
            )

        # Morning digest: ровно в 09:00 МСК, один раз в сутки.
        digest_payload: list[dict[str, Any]] = []
        if n.hour == config.MORNING_DIGEST_HOUR_MSK and n.minute < 10:
            day_start = start_of_msk_day(n)
            digest_payload = await self._collect_morning_digests(session, day_start)

        return {
            "now": n.isoformat(),
            "promoted_task_ids": [t.id for t in promoted],
            "deadline_notifications": deadline_payload,
            "morning_digests": digest_payload,
        }

    async def _collect_morning_digests(
        self, session: AsyncSession, day_start: datetime
    ) -> list[dict[str, Any]]:
        # Получаем всех владельцев — пока через подписки чатов.
        subs = await session.execute(select(ChatSubscriptionModel))
        owner_ids = {row.owner_user_id for row in subs.scalars().all()}
        owner_ids.update(await self._extract_owner_ids_from_tasks(session))

        payload: list[dict[str, Any]] = []
        for owner_id in owner_ids:
            already = await self._notification_repo.exists_for_user_on_date(
                session,
                user_id=owner_id,
                kind=NotificationKind.MORNING_DIGEST.value,
                date_value=day_start,
            )
            if already:
                continue
            digest = await self._digest_service.build(session, user_id=owner_id, day=day_start)
            await self._notification_repo.add(
                session,
                user_id=owner_id,
                task_id=None,
                kind=NotificationKind.MORNING_DIGEST.value,
            )
            payload.append({"user_id": owner_id, "digest": digest.model_dump(mode="json")})
        return payload

    async def _extract_owner_ids_from_tasks(self, session: AsyncSession) -> set[int]:
        from model.tasks.task_model import TaskModel

        result = await session.execute(select(TaskModel.user_id).distinct())
        return {row for row in result.scalars().all()}

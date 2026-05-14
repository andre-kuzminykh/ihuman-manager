"""
TaskService — основной сервис управления задачами.

## Трассируемость
Feature: F001, F002, F003, F005, F008, F009
Scenarios: SC001–SC008, SC013, SC014, SC020, SC021

## Зависимости
- TaskRepository
- TaskStatusChangeRepository
- ExtractorService (для парсинга дедлайна и заголовка)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import config
from core.exceptions import InvalidTransitionError, NotFoundError, ValidationError
from model.enums import ALLOWED_TRANSITIONS, TaskPriority, TaskSource, TaskStatus
from model.tasks.task_model import TaskModel
from repository.tasks.task_favorite_repository import TaskFavoriteRepository
from repository.tasks.task_repository import TaskRepository
from repository.tasks.task_status_change_repository import TaskStatusChangeRepository
from repository.directions.direction_repository import DirectionRepository
from service.dedup.task_dedup_service import TaskDedupService
from service.extractor.extractor_service import ExtractorService
from service.utils.time_utils import MSK, now_msk, today_msk_default_deadline


def _coerce_status(value: TaskStatus | str) -> TaskStatus:
    return value if isinstance(value, TaskStatus) else TaskStatus(value)


def _enrich_with_favorites(
    task: TaskModel,
    favorite_task_ids: set[int],
    favorite_direction_ids: set[int],
) -> dict:
    is_fav = task.id in favorite_task_ids or (
        task.direction_id is not None and task.direction_id in favorite_direction_ids
    )
    data = {
        "id": task.id,
        "user_id": task.user_id,
        "chat_id": task.chat_id,
        "source_message_id": task.source_message_id,
        "source_sender_username": task.source_sender_username,
        "source_sender_display": task.source_sender_display,
        "source_chat_username": task.source_chat_username,
        "title": task.title,
        "text": task.text,
        "description": task.description,
        "status": task.status,
        "source_kind": task.source_kind,
        "priority": task.priority,
        "deadline": task.deadline,
        "planned_start_at": task.planned_start_at,
        "planned_end_at": task.planned_end_at,
        "direction_id": task.direction_id,
        "is_favorite": is_fav,
        "paused_at": task.paused_at,
        "completed_at": task.completed_at,
        "cancelled_at": task.cancelled_at,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    return data


class TaskService:
    def __init__(
        self,
        repo: TaskRepository | None = None,
        status_repo: TaskStatusChangeRepository | None = None,
        favorite_repo: TaskFavoriteRepository | None = None,
        direction_repo: DirectionRepository | None = None,
        extractor: ExtractorService | None = None,
        dedup_service: TaskDedupService | None = None,
    ) -> None:
        self._repo = repo or TaskRepository()
        self._status_repo = status_repo or TaskStatusChangeRepository()
        self._favorite_repo = favorite_repo or TaskFavoriteRepository()
        self._direction_repo = direction_repo or DirectionRepository()
        self._extractor = extractor or ExtractorService()
        self._dedup = dedup_service or TaskDedupService(task_repo=self._repo)

    # ------- helpers -------

    def _initial_status(self, deadline: datetime, now: datetime | None = None) -> TaskStatus:
        n = (now or now_msk()).astimezone(MSK)
        delta = deadline.astimezone(MSK) - n
        if delta <= timedelta(days=config.DEADLINE_TODO_WINDOW_DAYS):
            return TaskStatus.TODO
        return TaskStatus.BACKLOG

    def _build_title(self, text: str) -> str:
        cleaned = text.strip()
        if "." in cleaned:
            first_sentence = cleaned.split(".", 1)[0]
            return first_sentence[:120].strip()
        return cleaned[:120].strip()

    # ------- create -------

    async def create_from_text(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        text: str,
        chat_id: int | None = None,
        source_message_id: int | None = None,
        source_sender_username: str | None = None,
        source_sender_display: str | None = None,
        source_chat_username: str | None = None,
        source_kind: TaskSource = TaskSource.TEXT,
        title: str | None = None,
        description: str | None = None,
        deadline: datetime | None = None,
        direction_id: int | None = None,
        priority: TaskPriority | str | None = None,
        now: datetime | None = None,
    ) -> TaskModel:
        cleaned = (text or "").strip()
        if not cleaned:
            raise ValidationError("Текст задачи не может быть пустым")

        if deadline is None:
            parsed = await self._extractor.parse_deadline(cleaned, now=now)
            deadline = parsed or today_msk_default_deadline(now)

        if direction_id is not None:
            direction = await self._direction_repo.get_by_id(session, direction_id)
            if direction is None or direction.user_id != user_id:
                raise ValidationError("Направление не найдено для пользователя")

        final_title = (title or self._build_title(cleaned))[:200]
        status = self._initial_status(deadline, now=now)
        prio_value = (
            priority.value if isinstance(priority, TaskPriority) else (priority or TaskPriority.MEDIUM.value)
        )

        task = await self._repo.create(
            session,
            user_id=user_id,
            chat_id=chat_id,
            source_message_id=source_message_id,
            source_sender_username=source_sender_username,
            source_sender_display=source_sender_display,
            source_chat_username=source_chat_username,
            source_kind=source_kind.value if isinstance(source_kind, TaskSource) else source_kind,
            title=final_title,
            text=cleaned,
            description=description,
            status=status.value,
            priority=prio_value,
            deadline=deadline,
            direction_id=direction_id,
        )
        await self._status_repo.add(
            session,
            task_id=task.id,
            from_status=None,
            to_status=status.value,
            changed_by=user_id,
            reason="initial",
        )
        return task

    async def create_or_find_duplicate(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        text: str,
        chat_id: int | None = None,
        source_message_id: int | None = None,
        source_sender_username: str | None = None,
        source_sender_display: str | None = None,
        source_chat_username: str | None = None,
        source_kind: TaskSource = TaskSource.TEXT,
        title: str | None = None,
        description: str | None = None,
        deadline: datetime | None = None,
        direction_id: int | None = None,
        priority: TaskPriority | str | None = None,
        now: datetime | None = None,
        force: bool = False,
    ) -> tuple[TaskModel, bool]:
        cleaned = (text or "").strip()
        if not cleaned:
            raise ValidationError("Текст задачи не может быть пустым")
        if not force:
            provisional_title = (title or self._build_title(cleaned))[:200]
            existing = await self._dedup.find_duplicate(
                session, user_id=user_id, title=provisional_title, now=now
            )
            if existing is not None:
                return existing, True
        task = await self.create_from_text(
            session,
            user_id=user_id,
            text=cleaned,
            chat_id=chat_id,
            source_message_id=source_message_id,
            source_sender_username=source_sender_username,
            source_sender_display=source_sender_display,
            source_chat_username=source_chat_username,
            source_kind=source_kind,
            title=title,
            description=description,
            deadline=deadline,
            direction_id=direction_id,
            priority=priority,
            now=now,
        )
        return task, False

    async def create_many_from_extraction(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        extracted: list[dict],
        chat_id: int | None = None,
        source_message_id: int | None = None,
        source_sender_username: str | None = None,
        source_sender_display: str | None = None,
        source_chat_username: str | None = None,
        source_kind: TaskSource = TaskSource.TEXT,
        now: datetime | None = None,
        force: bool = False,
    ) -> list[tuple[TaskModel, bool]]:
        """Создать несколько задач из мульти-extract результата.

        ## Трассируемость
        Feature: F015 (BR044)
        Scenarios: SC033, SC035

        Возвращает список (task, is_duplicate). Дедуп применяется к каждой.
        """
        if not extracted:
            return []
        out: list[tuple[TaskModel, bool]] = []
        for item in extracted:
            title = (item.get("title") or "").strip()
            text = (item.get("text") or title).strip()
            if not text:
                continue
            task, dup = await self.create_or_find_duplicate(
                session,
                user_id=user_id,
                text=text,
                chat_id=chat_id,
                source_message_id=source_message_id,
                source_sender_username=source_sender_username,
                source_sender_display=source_sender_display,
                source_chat_username=source_chat_username,
                source_kind=source_kind,
                title=title or None,
                description=item.get("description"),
                deadline=item.get("deadline"),
                priority=item.get("priority"),
                now=now,
                force=force,
            )
            out.append((task, dup))
        return out

    # ------- read -------

    async def get_or_404(self, session: AsyncSession, task_id: int) -> TaskModel:
        task = await self._repo.get_by_id(session, task_id)
        if task is None or task.deleted_at is not None:
            raise NotFoundError(f"Task {task_id} not found")
        return task

    async def list_for_user(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        statuses: Iterable[TaskStatus] | None = None,
        deadline_before: datetime | None = None,
        deadline_after: datetime | None = None,
        direction_id: int | None = None,
        favorite_only: bool = False,
    ) -> list[dict]:
        tasks = await self._repo.list_for_user(
            session,
            user_id,
            statuses=statuses,
            deadline_before=deadline_before,
            deadline_after=deadline_after,
            direction_id=direction_id,
            favorite_only=favorite_only,
        )
        fav_ids = set(await self._favorite_repo.task_ids_for_user(session, user_id))
        fav_dirs = set(await self._direction_repo.favorite_ids_for_user(session, user_id))
        return [_enrich_with_favorites(t, fav_ids, fav_dirs) for t in tasks]

    async def to_response(
        self, session: AsyncSession, task: TaskModel
    ) -> dict:
        fav_ids = set(await self._favorite_repo.task_ids_for_user(session, task.user_id))
        fav_dirs = set(
            await self._direction_repo.favorite_ids_for_user(session, task.user_id)
        )
        return _enrich_with_favorites(task, fav_ids, fav_dirs)

    # ------- update -------

    async def update(
        self,
        session: AsyncSession,
        task_id: int,
        *,
        title: str | None = None,
        text: str | None = None,
        description: str | None = None,
        deadline: datetime | None = None,
        direction_id: int | None = None,
        priority: TaskPriority | str | None = None,
        planned_start_at: datetime | None = None,
        planned_end_at: datetime | None = None,
        unset_direction: bool = False,
        unset_planned: bool = False,
        unset_description: bool = False,
    ) -> TaskModel:
        task = await self.get_or_404(session, task_id)

        if title is not None:
            task.title = title[:200]
        if text is not None:
            cleaned = text.strip()
            if not cleaned:
                raise ValidationError("Текст задачи не может быть пустым")
            task.text = cleaned
        if unset_description:
            task.description = None
        elif description is not None:
            task.description = description.strip() or None
        if priority is not None:
            task.priority = priority.value if isinstance(priority, TaskPriority) else str(priority)
        if deadline is not None:
            task.deadline = deadline
            if task.status == TaskStatus.DONE.value:
                task.status = TaskStatus.TODO.value
                task.completed_at = None
            elif task.status == TaskStatus.BACKLOG.value:
                new_status = self._initial_status(deadline)
                if new_status != TaskStatus.BACKLOG:
                    task.status = new_status.value
        if unset_direction:
            task.direction_id = None
        elif direction_id is not None:
            direction = await self._direction_repo.get_by_id(session, direction_id)
            if direction is None or direction.user_id != task.user_id:
                raise ValidationError("Направление не найдено")
            task.direction_id = direction_id
        if unset_planned:
            task.planned_start_at = None
            task.planned_end_at = None
        else:
            if planned_start_at is not None or planned_end_at is not None:
                start = planned_start_at if planned_start_at is not None else task.planned_start_at
                end = planned_end_at if planned_end_at is not None else task.planned_end_at
                if start is not None and end is None:
                    end = start + timedelta(minutes=config.DEFAULT_TASK_DURATION_MINUTES)
                if start is not None and end is not None and end <= start:
                    raise ValidationError(
                        "planned_end_at must be greater than planned_start_at"
                    )
                task.planned_start_at = start
                task.planned_end_at = end
        await session.flush()
        await session.refresh(task)
        return task

    # ------- status -------

    async def transition_status(
        self,
        session: AsyncSession,
        task_id: int,
        *,
        to: TaskStatus | str,
        changed_by: int | None = None,
        reason: str | None = None,
    ) -> TaskModel:
        task = await self.get_or_404(session, task_id)
        cur = _coerce_status(task.status)
        target = _coerce_status(to)
        if cur == target:
            return task
        allowed = ALLOWED_TRANSITIONS.get(cur, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f"Invalid transition {cur.value} → {target.value}"
            )
        task.status = target.value
        now = now_msk()
        if target == TaskStatus.PAUSED:
            task.paused_at = now
        elif target == TaskStatus.DONE:
            task.completed_at = now
        elif target == TaskStatus.CANCELLED:
            task.cancelled_at = now
        elif target == TaskStatus.IN_PROGRESS:
            task.paused_at = None
        elif target == TaskStatus.TODO:
            task.completed_at = None
            task.cancelled_at = None
            task.paused_at = None
        await session.flush()
        await self._status_repo.add(
            session,
            task_id=task.id,
            from_status=cur.value,
            to_status=target.value,
            changed_by=changed_by,
            reason=reason,
        )
        await session.refresh(task)
        return task

    # ------- delete -------

    async def soft_delete(self, session: AsyncSession, task_id: int) -> None:
        task = await self.get_or_404(session, task_id)
        task.deleted_at = now_msk()
        await session.flush()

    # ------- scheduler hooks -------

    async def promote_backlog_to_todo(
        self, session: AsyncSession, *, now: datetime | None = None
    ) -> list[TaskModel]:
        n = (now or now_msk()).astimezone(MSK)
        cutoff = n + timedelta(days=config.DEADLINE_TODO_WINDOW_DAYS)
        candidates = await self._repo.list_for_todo_promotion(
            session, deadline_before=cutoff
        )
        result: list[TaskModel] = []
        for task in candidates:
            try:
                updated = await self.transition_status(
                    session,
                    task.id,
                    to=TaskStatus.TODO,
                    reason="auto_promote_within_7_days",
                )
                result.append(updated)
            except InvalidTransitionError:
                continue
        return result

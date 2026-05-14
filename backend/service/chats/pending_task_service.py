"""
PendingTaskService — управление черновиками задач (до апрува).

## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import ConflictError, NotFoundError, ValidationError
from model.chats.pending_task_model import PendingTaskModel
from model.enums import TaskSource
from repository.chats.pending_task_repository import PendingTaskRepository
from service.tasks.task_service import TaskService
from service.utils.time_utils import now_msk


class PendingTaskService:
    def __init__(
        self,
        repo: PendingTaskRepository | None = None,
        task_service: TaskService | None = None,
    ) -> None:
        self._repo = repo or PendingTaskRepository()
        self._task_service = task_service or TaskService()

    async def create(
        self,
        session: AsyncSession,
        *,
        chat_id: int,
        message_id: int,
        owner_user_id: int,
        source_text: str,
        source_sender: str | None,
        draft: dict[str, Any],
        is_auto_approved: bool = False,
    ) -> PendingTaskModel:
        return await self._repo.create(
            session,
            chat_id=chat_id,
            message_id=message_id,
            owner_user_id=owner_user_id,
            source_text=source_text,
            source_sender=source_sender,
            draft=draft,
            is_auto_approved=is_auto_approved,
        )

    async def get_or_404(
        self, session: AsyncSession, pending_id: int
    ) -> PendingTaskModel:
        obj = await self._repo.get_by_id(session, pending_id)
        if obj is None:
            raise NotFoundError(f"PendingTask {pending_id} not found")
        return obj

    async def list_for_owner(
        self, session: AsyncSession, owner_user_id: int, *, only_unapproved: bool = True
    ) -> list[PendingTaskModel]:
        return await self._repo.list_for_owner(
            session, owner_user_id, only_unapproved=only_unapproved
        )

    async def update_draft(
        self,
        session: AsyncSession,
        pending_id: int,
        *,
        draft: dict[str, Any] | None = None,
        title: str | None = None,
        text: str | None = None,
        deadline: datetime | None = None,
        direction_id: int | None = None,
    ) -> PendingTaskModel:
        obj = await self.get_or_404(session, pending_id)
        if obj.approved:
            raise ConflictError("PendingTask already approved")
        current = dict(obj.draft or {})
        if draft is not None:
            current.update(draft)
        if title is not None:
            current["title"] = title.strip()
        if text is not None:
            cleaned = text.strip()
            if not cleaned:
                raise ValidationError("Текст задачи не может быть пустым")
            current["text"] = cleaned
        if deadline is not None:
            current["deadline"] = deadline.isoformat()
        if direction_id is not None:
            current["direction_id"] = direction_id
        obj.draft = current
        await session.flush()
        await session.refresh(obj)
        return obj

    async def approve(
        self, session: AsyncSession, pending_id: int, *, force: bool = False
    ) -> PendingTaskModel:
        obj = await self.get_or_404(session, pending_id)
        if obj.approved:
            return obj
        draft = obj.draft or {}
        text = draft.get("text") or obj.source_text
        title = draft.get("title")
        deadline_str = draft.get("deadline")
        deadline = (
            datetime.fromisoformat(deadline_str)
            if isinstance(deadline_str, str)
            else None
        )
        direction_id = draft.get("direction_id")
        task, _is_duplicate = await self._task_service.create_or_find_duplicate(
            session,
            user_id=obj.owner_user_id,
            text=text,
            chat_id=obj.chat_id,
            force=force,
            source_message_id=obj.message_id,
            source_sender_username=obj.source_sender,
            source_kind=TaskSource.CHAT,
            title=title,
            description=draft.get("description"),
            deadline=deadline,
            direction_id=direction_id,
            priority=draft.get("priority"),
        )
        obj.approved = True
        obj.approved_at = now_msk()
        obj.created_task_id = task.id
        await session.flush()
        await session.refresh(obj)
        return obj

    async def reject(
        self, session: AsyncSession, pending_id: int
    ) -> PendingTaskModel:
        obj = await self.get_or_404(session, pending_id)
        if obj.approved:
            raise ConflictError("PendingTask already approved")
        obj.rejected_at = now_msk()
        await session.flush()
        await session.refresh(obj)
        return obj

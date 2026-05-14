"""
MessageIngestService — обработка входящего сообщения из подписанного чата.

## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014 (BR012–BR016)

## Бизнес-контекст
1. Дедуп по (chat_id, message_id).
2. Записать в message_context (sliding window 10).
3. Проверить подписку. Если нет — `not_subscribed`.
4. Получить контекст 10 предыдущих сообщений.
5. Классифицировать сообщение через ExtractorService.
6. Если задача:
   - bot_mentioned=True → авто-апрув: создать pending + apply task.
   - иначе → создать pending в ожидании апрува.
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import config


log = logging.getLogger("message_ingest")
from repository.chats.message_context_repository import MessageContextRepository
from repository.chats.processed_message_repository import ProcessedMessageRepository
from schema.chats.message_ingest_schema import (
    MessageIngestResultSchema,
    MessageIngestSchema,
)
from service.chats.chat_subscription_service import ChatSubscriptionService
from service.chats.pending_task_service import PendingTaskService
from service.extractor.extractor_service import ExtractorService
from service.people.person_service import PersonService
from service.tasks.task_service import TaskService
from service.utils.time_utils import today_msk_default_deadline


def _resolve_display_name(
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    username: str | None = None,
) -> str | None:
    full = " ".join(filter(None, [first_name, last_name])).strip()
    if full and username:
        return f"{full} (@{username})"
    if full:
        return full
    if username:
        return f"@{username}"
    return None


class MessageIngestService:
    def __init__(
        self,
        sub_service: ChatSubscriptionService | None = None,
        msg_repo: MessageContextRepository | None = None,
        processed_repo: ProcessedMessageRepository | None = None,
        pending_service: PendingTaskService | None = None,
        extractor: ExtractorService | None = None,
        task_service: TaskService | None = None,
        person_service: PersonService | None = None,
    ) -> None:
        self._sub_service = sub_service or ChatSubscriptionService()
        self._msg_repo = msg_repo or MessageContextRepository()
        self._person_service = person_service or PersonService()
        self._processed_repo = processed_repo or ProcessedMessageRepository()
        self._pending_service = pending_service or PendingTaskService()
        self._task_service = task_service or TaskService()
        self._extractor = extractor or ExtractorService()

    async def ingest(
        self, session: AsyncSession, payload: MessageIngestSchema
    ) -> MessageIngestResultSchema:
        log.info(
            "INGEST start: chat=%s msg=%s sender=%s mentioned=%s text=%r",
            payload.chat_id,
            payload.message_id,
            payload.sender_username,
            payload.is_bot_mentioned,
            payload.text[:300],
        )
        # 1. dedup
        if await self._processed_repo.is_processed(
            session, payload.chat_id, payload.message_id
        ):
            log.info("INGEST duplicate: chat=%s msg=%s", payload.chat_id, payload.message_id)
            return MessageIngestResultSchema(decision="duplicate")

        # 2. subscription
        sub = await self._sub_service.get_active(session, payload.chat_id)
        if sub is None:
            return MessageIngestResultSchema(decision="not_subscribed")

        # 3. store context
        await self._msg_repo.create(
            session,
            chat_id=payload.chat_id,
            message_id=payload.message_id,
            sender_user_id=payload.sender_user_id,
            sender_username=payload.sender_username,
            text=payload.text,
            sent_at=payload.sent_at,
        )
        await self._msg_repo.prune_old(session, payload.chat_id, keep=config.MAX_CONTEXT_MESSAGES)
        await self._processed_repo.mark_processed(
            session, payload.chat_id, payload.message_id
        )

        # 4. context for LLM
        context = await self._msg_repo.latest_for_chat(
            session, payload.chat_id, limit=config.MAX_CONTEXT_MESSAGES
        )
        context_payload = [
            {"sender_username": m.sender_username, "text": m.text}
            for m in context
            if m.message_id != payload.message_id
        ]
        log.info(
            "INGEST context size=%d, last_messages=%s",
            len(context_payload),
            [f"{m['sender_username'] or 'user'}: {m['text'][:80]}" for m in context_payload[-5:]],
        )

        # 5. Подтягиваем имя отправителя — сначала из payload (если бот
        #    передал), потом fallback из People (если уже видели).
        sender_first = payload.sender_first_name
        sender_last = payload.sender_last_name
        if not (sender_first or sender_last) and payload.sender_user_id:
            from repository.people.person_repository import PersonRepository

            person = await PersonRepository().get_by_telegram_id(
                session, payload.sender_user_id
            )
            if person is not None:
                sender_first = sender_first or person.first_name
                sender_last = sender_last or person.last_name
        sender_display = _resolve_display_name(
            first_name=sender_first,
            last_name=sender_last,
            username=payload.sender_username,
        )
        log.info("INGEST sender_display=%r", sender_display)

        # 6. Извлекаем массив задач (всегда). Если 0 — игнор. Если >=1 —
        #    либо авто-апрув (бот тегнут), либо N PendingTask на согласование.
        from model.enums import TaskSource as _TaskSource

        extracted = await self._extractor.extract_multiple(
            payload.text,
            context_messages=context_payload,
            sender_display=sender_display,
        )
        if not extracted:
            return MessageIngestResultSchema(
                decision="ignored", detail="not_a_task"
            )

        if payload.is_bot_mentioned:
            results = await self._task_service.create_many_from_extraction(
                session,
                user_id=sub.owner_user_id,
                extracted=extracted,
                chat_id=payload.chat_id,
                source_message_id=payload.message_id,
                source_sender_username=payload.sender_username,
                source_chat_username=payload.chat_username,
                source_kind=_TaskSource.CHAT,
            )
            task_ids = [t.id for t, _ in results]
            if len(task_ids) > 1:
                return MessageIngestResultSchema(
                    decision="auto_approved_multi", task_ids=task_ids
                )
            return MessageIngestResultSchema(
                decision="auto_approved",
                task_id=task_ids[0] if task_ids else None,
                task_ids=task_ids,
            )

        # Не тегнут → каждая задача = отдельный pending для согласования.
        pending_ids: list[int] = []
        for item in extracted:
            deadline = item.get("deadline")
            if deadline is None:
                deadline = today_msk_default_deadline()
            draft = {
                "title": item["title"],
                "description": item.get("description"),
                "text": item.get("text") or item["title"],
                "deadline": deadline.isoformat() if isinstance(deadline, datetime) else deadline,
                "priority": item.get("priority") or "medium",
                "confidence": item.get("confidence"),
            }
            pending = await self._pending_service.create(
                session,
                chat_id=payload.chat_id,
                message_id=payload.message_id,
                owner_user_id=sub.owner_user_id,
                source_text=payload.text,
                source_sender=payload.sender_username,
                source_chat_username=payload.chat_username,
                draft=draft,
                is_auto_approved=False,
            )
            pending_ids.append(pending.id)

        if len(pending_ids) > 1:
            return MessageIngestResultSchema(
                decision="pending_created_multi",
                pending_task_ids=pending_ids,
            )
        return MessageIngestResultSchema(
            decision="pending_created",
            pending_task_id=pending_ids[0] if pending_ids else None,
            pending_task_ids=pending_ids,
        )

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

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import config
from repository.chats.message_context_repository import MessageContextRepository
from repository.chats.processed_message_repository import ProcessedMessageRepository
from schema.chats.message_ingest_schema import (
    MessageIngestResultSchema,
    MessageIngestSchema,
)
from service.chats.chat_subscription_service import ChatSubscriptionService
from service.chats.pending_task_service import PendingTaskService
from service.extractor.extractor_service import ExtractorService
from service.utils.time_utils import today_msk_default_deadline


class MessageIngestService:
    def __init__(
        self,
        sub_service: ChatSubscriptionService | None = None,
        msg_repo: MessageContextRepository | None = None,
        processed_repo: ProcessedMessageRepository | None = None,
        pending_service: PendingTaskService | None = None,
        extractor: ExtractorService | None = None,
    ) -> None:
        self._sub_service = sub_service or ChatSubscriptionService()
        self._msg_repo = msg_repo or MessageContextRepository()
        self._processed_repo = processed_repo or ProcessedMessageRepository()
        self._pending_service = pending_service or PendingTaskService()
        self._extractor = extractor or ExtractorService()

    async def ingest(
        self, session: AsyncSession, payload: MessageIngestSchema
    ) -> MessageIngestResultSchema:
        # 1. dedup
        if await self._processed_repo.is_processed(
            session, payload.chat_id, payload.message_id
        ):
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

        # 5. classify
        classification = await self._extractor.classify_message(
            payload.text, context_messages=context_payload
        )
        if not classification.get("is_task"):
            return MessageIngestResultSchema(
                decision="ignored", detail="not_a_task"
            )

        # 6. draft
        deadline = classification.get("deadline")
        if deadline is None:
            deadline = await self._extractor.parse_deadline(payload.text)
        if deadline is None:
            deadline = today_msk_default_deadline()

        draft = {
            "title": classification.get("title") or self._extractor.build_title(payload.text),
            "text": payload.text,
            "deadline": deadline.isoformat() if isinstance(deadline, datetime) else deadline,
            "confidence": classification.get("confidence"),
        }

        pending = await self._pending_service.create(
            session,
            chat_id=payload.chat_id,
            message_id=payload.message_id,
            owner_user_id=sub.owner_user_id,
            source_text=payload.text,
            source_sender=payload.sender_username,
            draft=draft,
            is_auto_approved=payload.is_bot_mentioned,
        )

        if payload.is_bot_mentioned:
            approved = await self._pending_service.approve(session, pending.id)
            return MessageIngestResultSchema(
                decision="auto_approved",
                pending_task_id=approved.id,
                task_id=approved.created_task_id,
            )

        return MessageIngestResultSchema(
            decision="pending_created",
            pending_task_id=pending.id,
        )

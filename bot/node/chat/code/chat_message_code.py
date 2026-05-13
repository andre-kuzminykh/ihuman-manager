"""
ChatMessageCode — обработка нового сообщения в групповом чате.

## Трассируемость
Feature: F005
Scenarios: SC012, SC013

## Бизнес-логика
1. Определить, упомянут ли бот (`@<BOT_USERNAME>` в тексте).
2. Передать в /messages/ingest.
3. По decision:
   - pending_created → owner получит карточку (см. PendingCardAnswer).
   - auto_approved / auto_approved_multi → owner получит карточку(и) задач.
   - not_subscribed + бот тегнут → ответить в чате просьбой вызвать /setup_chat.
   - ignored / duplicate без тега — silent.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram.types import Message

from core.config import config
from service.api.base_api import APIError
from service.api.chats_api import ChatsAPI
from service.api.pending_tasks_api import PendingTasksAPI
from service.api.tasks_api import TasksAPI


log = logging.getLogger("chat_message_code")


def _is_bot_mentioned(message: Message) -> bool:
    bot_username = f"@{config.BOT_USERNAME.lower().lstrip('@')}"
    text = (message.text or message.caption or "").lower()
    return bot_username in text


class ChatMessageCode:
    def __init__(
        self,
        chats_api: ChatsAPI | None = None,
        pending_api: PendingTasksAPI | None = None,
        tasks_api: TasksAPI | None = None,
    ) -> None:
        self._chats_api = chats_api or ChatsAPI()
        self._pending_api = pending_api or PendingTasksAPI()
        self._tasks_api = tasks_api or TasksAPI()

    async def run(self, message: Message) -> dict:
        text = (message.text or message.caption or "").strip()
        if not text:
            return {"answer_name": "noop", "data": {}}
        mentioned = _is_bot_mentioned(message)
        log.info(
            "incoming chat message: chat_id=%s msg_id=%s sender=%s mentioned=%s text=%r",
            message.chat.id,
            message.message_id,
            message.from_user.username if message.from_user else None,
            mentioned,
            text[:160],
        )
        sent_at = message.date or datetime.now(timezone.utc)
        try:
            result = await self._chats_api.ingest_message(
                chat_id=message.chat.id,
                message_id=message.message_id,
                sender_user_id=message.from_user.id if message.from_user else None,
                sender_username=message.from_user.username if message.from_user else None,
                text=text,
                sent_at=sent_at,
                is_bot_mentioned=mentioned,
            )
        except APIError as exc:
            log.warning("ingest API failed: %s", exc.message)
            return {"answer_name": "noop", "data": {}}

        decision = result.get("decision")
        log.info("ingest decision=%s payload=%s", decision, result)

        if decision == "pending_created":
            pending = await self._pending_api.get(result["pending_task_id"])
            return {"answer_name": "pending_card_dm", "data": {"pending": pending}}
        if decision == "auto_approved":
            task = await self._tasks_api.get(result["task_id"])
            return {"answer_name": "task_created_dm", "data": {"task": task, "from_chat": True}}
        if decision == "auto_approved_multi":
            tasks = []
            for tid in result.get("task_ids", []):
                tasks.append(await self._tasks_api.get(tid))
            return {
                "answer_name": "tasks_created_multi_dm",
                "data": {"tasks": tasks, "from_chat": True},
            }
        return {"answer_name": "noop", "data": {"decision": decision}}

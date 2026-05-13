"""
Виджет: business_message — сообщения из DM-чатов бизнес-аккаунта.

## Трассируемость
Feature: F018
Scenarios: SC037

Telegram присылает business_message за каждое сообщение в DM-чатах
владельца бизнес-аккаунта. Мы:
1. Достаём business_connection_id → находим owner_user_id.
2. Авто-подписываем (chat_id, owner_user_id) если ещё нет.
3. Прогоняем через MessageIngestService (та же логика что для групп).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import Message

from core.loader import get_bot
from node.chat.code.chat_message_code import _is_bot_mentioned
from node.pending.answer.pending_card_answer import PendingCardAnswer
from node.task.answer.task_created_answer import build_task_card_kb, render_task_card
from service.api.base_api import APIError
from service.api.business_api import BusinessAPI
from service.api.chats_api import ChatsAPI
from service.api.pending_tasks_api import PendingTasksAPI
from service.api.tasks_api import TasksAPI


router = Router(name="business.F018.message")
log = logging.getLogger("business_message")


@router.business_message(F.text | F.caption)
async def on_business_message(message: Message) -> None:
    if message.from_user is not None and message.from_user.is_bot:
        return
    bc_id = getattr(message, "business_connection_id", None)
    if bc_id is None:
        return

    owner = await BusinessAPI().get_owner(bc_id)
    if owner is None:
        log.warning("business_message: connection %s not registered, skipping", bc_id)
        return

    text = (message.text or message.caption or "").strip()
    if not text:
        return

    # Ингестим ВСЁ — и входящие, и сообщения самого владельца:
    # его собственные «надо позвонить...», «напомни...» — тоже задачи.

    chats_api = ChatsAPI()
    # Авто-подписка чата (DM с этим контактом).
    try:
        await chats_api.subscribe(
            chat_id=message.chat.id,
            owner_user_id=owner,
            title=(message.chat.title or message.chat.full_name if hasattr(message.chat, "full_name") else None),
        )
    except APIError as exc:
        log.warning("auto-subscribe (business) failed: %s", exc.message)

    sent_at = message.date or datetime.now(timezone.utc)
    try:
        result = await chats_api.ingest_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
            sender_user_id=message.from_user.id if message.from_user else None,
            sender_username=message.from_user.username if message.from_user else None,
            text=text,
            sent_at=sent_at,
            is_bot_mentioned=_is_bot_mentioned(message),
        )
    except APIError as exc:
        log.warning("business ingest failed: %s", exc.message)
        return

    log.info("business ingest decision=%s payload=%s", result.get("decision"), result)
    decision = result.get("decision")
    bot = get_bot()

    if decision == "pending_created":
        pending_api = PendingTasksAPI()
        pending = await pending_api.get(result["pending_task_id"])
        await PendingCardAnswer().send(owner_chat_id=owner, pending=pending)
    elif decision == "auto_approved":
        tasks_api = TasksAPI()
        task = await tasks_api.get(result["task_id"])
        await bot.send_message(
            owner,
            "📥 Задача из бизнес-чата (автоапрув):\n\n" + render_task_card(task),
            reply_markup=build_task_card_kb(task),
            disable_web_page_preview=True,
        )
    elif decision == "auto_approved_multi":
        tasks_api = TasksAPI()
        await bot.send_message(
            owner, f"📥 Из бизнес-чата извлечено задач: {len(result.get('task_ids', []))}"
        )
        for tid in result.get("task_ids", []):
            task = await tasks_api.get(tid)
            await bot.send_message(
                owner,
                render_task_card(task),
                reply_markup=build_task_card_kb(task),
                disable_web_page_preview=True,
            )

"""
Виджет: автоподписка чата при добавлении бота.

## Трассируемость
Feature: F005
Scenarios: SC011 (новое поведение — без явной команды)

Слушаем событие my_chat_member: когда статус бота в чате меняется на
'member' или 'administrator', автоматически создаём подписку.
"""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import ChatMemberUpdated

from service.api.base_api import APIError
from service.api.chats_api import ChatsAPI


router = Router(name="chat.F005.auto_subscribe")
log = logging.getLogger("auto_subscribe")


@router.my_chat_member()
async def on_my_chat_member(event: ChatMemberUpdated) -> None:
    new_status = event.new_chat_member.status
    old_status = event.old_chat_member.status
    log.info(
        "my_chat_member: chat=%s title=%r %s → %s, by user=%s",
        event.chat.id,
        event.chat.title,
        old_status,
        new_status,
        event.from_user.id if event.from_user else None,
    )
    if new_status not in {"member", "administrator"}:
        # left / kicked / restricted — пока ничего не делаем
        return
    if event.from_user is None:
        return

    api = ChatsAPI()
    try:
        await api.subscribe(
            chat_id=event.chat.id,
            owner_user_id=event.from_user.id,
            title=event.chat.title,
        )
    except APIError as exc:
        log.warning("auto-subscribe failed: %s", exc.message)
        return

    # В чат НИЧЕГО не пишем — тихо подписались.
    # Опционально, короткий DM владельцу — что добавлен чат.
    try:
        from core.loader import get_bot

        bot = get_bot()
        await bot.send_message(
            event.from_user.id,
            f"✅ Подписался на чат «{event.chat.title or event.chat.id}». "
            "Буду слушать и присылать задачи сюда в DM.",
        )
    except Exception:  # pragma: no cover — пользователь мог не нажать /start
        log.info("owner DM not sent (likely user hasn't started the bot)")

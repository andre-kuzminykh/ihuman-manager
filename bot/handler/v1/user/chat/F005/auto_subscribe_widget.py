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

    # Дружелюбное «привет, я готов» в чат (если есть права писать).
    try:
        from core.loader import get_bot

        bot = get_bot()
        await bot.send_message(
            event.chat.id,
            "Привет! Я iHuman Manager.\n"
            "Буду слушать чат и присылать задачи владельцу на согласование. "
            "Тегайте меня @{username}, чтобы создать задачу без согласования. "
            "Чтобы перестать — удалите меня из чата.".format(
                username=(await bot.get_me()).username
            ),
        )
    except Exception:  # pragma: no cover — права на пост могут отсутствовать
        log.info("welcome message not sent (no rights or other issue)")

"""
Виджет: бизнес-подключение бота к Premium-аккаунту пользователя.

## Трассируемость
Feature: F018
Scenarios: SC036

Telegram присылает business_connection при:
- подключении бота в Settings → Telegram Business → Chatbots
- изменении прав (can_reply и т.п.)
- отключении (is_enabled=False)
"""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import BusinessConnection

from service.api.base_api import APIError
from service.api.business_api import BusinessAPI


router = Router(name="business.F018.connection")
log = logging.getLogger("business_connection")


@router.business_connection()
async def on_business_connection(event: BusinessConnection) -> None:
    log.info(
        "business_connection id=%s user_id=%s is_enabled=%s can_reply=%s",
        event.id,
        event.user.id,
        event.is_enabled,
        getattr(event, "can_reply", False),
    )
    api = BusinessAPI()
    try:
        await api.upsert_connection(
            business_connection_id=event.id,
            owner_user_id=event.user.id,
            is_enabled=event.is_enabled,
            can_reply=getattr(event, "can_reply", False),
        )
    except APIError as exc:
        log.warning("upsert business connection failed: %s", exc.message)
        return

    # Короткий DM в личку владельцу.
    try:
        from core.loader import get_bot

        bot = get_bot()
        if event.is_enabled:
            await bot.send_message(
                event.user.id,
                "✅ Подключён к твоему Telegram Business аккаунту.\n"
                "Я буду слушать DM-чаты, извлекать задачи и присылать карточки сюда.",
            )
        else:
            await bot.send_message(
                event.user.id,
                "🔌 Бизнес-подключение отключено. "
                "Если хочешь снова — Settings → Business → Chatbots.",
            )
    except Exception:  # pragma: no cover
        log.info("owner DM not sent")

"""
app.py — точка входа бота.

Делает три вещи:
1. Регистрирует роутеры виджетов.
2. Поднимает фоновый таск, который раз в N сек дёргает /scheduler/tick на бэкенде
   и рассылает уведомления (F003, F006, F007).
3. Запускает long-polling.
"""

from __future__ import annotations

import asyncio
import logging

from core import dp
from core.config import config
from core.loader import get_bot
from handler import include_routers
from scheduler_runner import run_scheduler_loop


def setup_logging() -> None:
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def main() -> None:
    setup_logging()
    log = logging.getLogger("ihuman-bot")
    log.info("Starting iHuman Manager bot, BOT_USERNAME=%s", config.BOT_USERNAME)

    include_routers(dp)

    bot = get_bot()

    # Явно перечисляем нужные update-типы. resolve_used_update_types() иногда
    # пропускает channel_post при regex-handler'ах — поэтому фиксируем сами.
    allowed_updates = [
        "message",
        "edited_message",
        "channel_post",
        "edited_channel_post",
        "callback_query",
        "my_chat_member",
        "chat_member",
    ]
    log.info("Polling allowed_updates=%s", allowed_updates)

    me = await bot.get_me()
    log.info(
        "Bot identity: @%s id=%s; can_join_groups=%s can_read_all_group_messages=%s",
        me.username,
        me.id,
        getattr(me, "can_join_groups", None),
        getattr(me, "can_read_all_group_messages", None),
    )

    scheduler_task: asyncio.Task | None = None
    if config.BOT_SCHEDULER_TICK_SECONDS > 0:
        scheduler_task = asyncio.create_task(
            run_scheduler_loop(interval_seconds=config.BOT_SCHEDULER_TICK_SECONDS)
        )

    try:
        await dp.start_polling(bot, allowed_updates=allowed_updates)
    finally:
        if scheduler_task:
            scheduler_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())

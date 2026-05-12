"""
core.loader — глобальные Bot/Dispatcher.

Чтобы загрузка модулей не падала при пустом BOT_TOKEN (например, в тестах),
bot создаётся лениво.
"""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import config

_bot: Bot | None = None
dp: Dispatcher = Dispatcher(storage=MemoryStorage())


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        if not config.BOT_TOKEN:
            raise RuntimeError(
                "BOT_TOKEN is empty. Set it in .env or environment before starting the bot."
            )
        _bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


class _BotProxy:
    """Прокси, чтобы `from core import bot` не падал при импорте без токена."""

    def __getattr__(self, item):
        return getattr(get_bot(), item)


bot = _BotProxy()

"""
Виджет: /start, /help, /menu — приветствие и список команд.

## Трассируемость
Общий — без фичи. Onboarding (логически связан с F001–F009).
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from core import vocab


router = Router(name="start")


@router.message(CommandStart())
@router.message(Command("help"))
@router.message(Command("menu"))
async def handle_start(message: Message) -> None:
    await message.answer(vocab.START)


@router.message(F.text == "/version")
async def handle_version(message: Message) -> None:
    await message.answer("iHuman Manager v0.1.0")

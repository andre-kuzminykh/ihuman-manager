"""
include_router — собирает все роутеры виджетов и подключает к Dispatcher.
"""

from __future__ import annotations

from aiogram import Dispatcher

from handler.v1.user.router import build_user_router


def include_routers(dp: Dispatcher) -> None:
    dp.include_router(build_user_router())

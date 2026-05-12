"""
## Трассируемость
Feature: F007
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class DigestActionCallback(CallbackData, prefix="dig"):
    action: str  # start_day | refresh

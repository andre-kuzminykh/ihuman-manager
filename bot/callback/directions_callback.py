"""
## Трассируемость
Feature: F009
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class DirectionActionCallback(CallbackData, prefix="dir"):
    direction_id: int
    action: str  # favorite | unfavorite | delete | rename

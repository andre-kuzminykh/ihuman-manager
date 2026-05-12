"""
## Трассируемость
Feature: F005
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class PendingActionCallback(CallbackData, prefix="pend"):
    pending_id: int
    action: str  # approve | reject | edit_title | edit_deadline

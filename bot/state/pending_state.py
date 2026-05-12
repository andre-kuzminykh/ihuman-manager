"""
## Трассируемость
Feature: F005
Scenarios: SC014
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class PendingEditStates(StatesGroup):
    awaiting_title = State()
    awaiting_deadline = State()

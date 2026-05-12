"""
## Трассируемость
Feature: F009
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class DirectionStates(StatesGroup):
    awaiting_name = State()
    awaiting_rename = State()

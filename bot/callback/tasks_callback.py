"""
## Трассируемость
Feature: F003, F004, F006, F008
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class TaskCardCallback(CallbackData, prefix="tcard"):
    task_id: int
    action: str  # show | back


class TaskActionCallback(CallbackData, prefix="task"):
    task_id: int
    action: str  # start | pause | done | cancel | favorite | unfavorite |
                 # set_deadline_tomorrow | set_start_now | set_start_in_1h

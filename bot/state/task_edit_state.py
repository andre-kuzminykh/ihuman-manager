"""
FSM-состояния виджета редактирования задачи.

## Трассируемость
Feature: F024
Scenarios: SC044, SC045, SC046, SC047, SC048
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class TaskEditStates(StatesGroup):
    """Состояния редактора задачи.

    main — основной экран; принимает свободный текст/голос → LLM-edit.
    awaiting_title — ждём новое название (текст/голос).
    awaiting_description — ждём новое описание (текст/голос).
    picking_date — открыт календарь.
    picking_time — открыт time-picker.
    """

    main = State()
    awaiting_title = State()
    awaiting_description = State()
    picking_date = State()
    picking_time = State()

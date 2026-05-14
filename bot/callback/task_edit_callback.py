"""
TaskEditCallback — callbacks для виджета редактирования задачи.

## Трассируемость
Feature: F024
Scenarios: SC044, SC045, SC046, SC047, SC048
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class TaskEditCallback(CallbackData, prefix="te"):
    """Главный экран редактирования и быстрые действия.

    action:
      - open: открыть экран редактирования (с карточки задачи)
      - main: вернуться на главный экран редактирования
      - title: открыть подэкран «изменить название»
      - desc: открыть подэкран «изменить описание»
      - date: открыть календарь
      - time: открыть time-picker
      - prio_low / prio_medium / prio_high: переключить приоритет на главном экране
      - clear_desc: стереть описание
      - clear_deadline: стереть дедлайн
      - accept: завершить редактирование (закрыть и показать карточку)
      - cancel: отменить (вернуться к карточке без сохранения отсутствующих правок)
    """

    task_id: int
    action: str


class TaskEditDateCallback(CallbackData, prefix="ted"):
    """Календарь.

    action:
      - prev_y / next_y — год ←/→
      - prev_m / next_m — месяц ←/→
      - day — выбрать день (вместе со значением day из payload)
      - accept — применить выбранную дату (сохраняет current_time из FSM, иначе 09:00)
      - back — назад на главный экран
    """

    task_id: int
    action: str
    year: int = 0
    month: int = 0
    day: int = 0


class TaskEditTimeCallback(CallbackData, prefix="tet"):
    """Time-picker.

    action:
      - prev_h / next_h — час ←/→
      - min — выбрать минуты (вместе со значением minute)
      - accept — применить выбранные час+минуты (соединяется с датой из FSM)
      - back — назад на главный экран
    """

    task_id: int
    action: str
    hour: int = 0
    minute: int = 0

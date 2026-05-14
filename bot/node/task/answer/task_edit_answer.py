"""
TaskEditAnswer — экран редактирования задачи и его подэкраны.

## Трассируемость
Feature: F024
Scenarios: SC044, SC045, SC046, SC047, SC048

Экранов пять:
  1. main      — главный экран редактирования (название/описание/дата/время/приоритет).
  2. title     — подэкран ввода названия (текст/голос/кружок).
  3. description — подэкран ввода описания (текст/голос/кружок).
  4. date      — календарь: год ←/→, месяц ←/→, дни 11×3, Back+Accept.
  5. time      — time-picker: час ←/→, минуты 2×6 (00,05,…,55), Back+Accept.

Все экраны рисуются `edit_text` поверх одного сообщения, чтобы не плодить
карточки в DM.
"""

from __future__ import annotations

import calendar
import html
from datetime import date, datetime, timedelta, timezone

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callback.task_edit_callback import (
    TaskEditCallback,
    TaskEditDateCallback,
    TaskEditTimeCallback,
)


_MSK = timezone(timedelta(hours=3))
_PRIORITY_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}
_PRIORITY_LABEL = {"low": "🟢 Низкий", "medium": "🟡 Средний", "high": "🔴 Высокий"}
_MONTHS_RU = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]


def _to_msk(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).astimezone(_MSK)
    return dt.astimezone(_MSK)


def _fmt_deadline(value: str | datetime | None) -> str:
    if not value:
        return "—"
    if isinstance(value, datetime):
        return _to_msk(value).strftime("%d.%m.%Y · %H:%M")
    try:
        return _to_msk(datetime.fromisoformat(value)).strftime("%d.%m.%Y · %H:%M")
    except (TypeError, ValueError):
        return str(value)


# ---------- MAIN screen ----------


def render_main(task: dict) -> str:
    title = html.escape(task.get("title") or "—")
    desc = task.get("description")
    desc_line = html.escape(desc) if desc else "—"
    prio = (task.get("priority") or "medium").lower()
    prio_label = _PRIORITY_LABEL.get(prio, _PRIORITY_LABEL["medium"])
    deadline_line = _fmt_deadline(task.get("deadline"))
    return (
        "✏️ <b>Редактирование задачи</b>\n\n"
        f"📌 <b>{title}</b>\n"
        f"📝 {desc_line}\n"
        f"📅 {deadline_line}\n"
        f"{prio_label}\n\n"
        "Можно поменять любое поле кнопкой ниже,\n"
        "или просто отправь <b>текстом</b>, <b>голосом</b> или <b>кружком</b> —\n"
        "разберу естественный язык."
    )


def build_main_kb(task: dict) -> InlineKeyboardMarkup:
    tid = task["id"]
    prio = (task.get("priority") or "medium").lower()
    has_desc = bool(task.get("description"))
    has_deadline = bool(task.get("deadline"))

    def _prio(label_prio: str) -> InlineKeyboardButton:
        is_active = prio == label_prio
        emoji = _PRIORITY_EMOJI[label_prio]
        text = f"● {emoji}" if is_active else emoji
        return InlineKeyboardButton(
            text=text,
            callback_data=TaskEditCallback(task_id=tid, action=f"prio_{label_prio}").pack(),
        )

    rows: list[list[InlineKeyboardButton]] = [
        # Row 1 — название.
        [
            InlineKeyboardButton(
                text="📌 Изменить название",
                callback_data=TaskEditCallback(task_id=tid, action="title").pack(),
            )
        ],
        # Row 2 — описание (+ очистка).
        [
            InlineKeyboardButton(
                text="📝 Изменить описание",
                callback_data=TaskEditCallback(task_id=tid, action="desc").pack(),
            )
        ],
    ]
    if has_desc:
        rows.append([
            InlineKeyboardButton(
                text="🗑 Стереть описание",
                callback_data=TaskEditCallback(task_id=tid, action="clear_desc").pack(),
            )
        ])
    # Row 3 — дата · время.
    rows.append([
        InlineKeyboardButton(
            text="📅 Дата",
            callback_data=TaskEditCallback(task_id=tid, action="date").pack(),
        ),
        InlineKeyboardButton(
            text="🕐 Время",
            callback_data=TaskEditCallback(task_id=tid, action="time").pack(),
        ),
    ])
    if has_deadline:
        rows.append([
            InlineKeyboardButton(
                text="🗑 Снять дедлайн",
                callback_data=TaskEditCallback(task_id=tid, action="clear_deadline").pack(),
            )
        ])
    # Row 4 — приоритет (тогл).
    rows.append([_prio("low"), _prio("medium"), _prio("high")])
    # Row 5 — отмена / accept.
    rows.append([
        InlineKeyboardButton(
            text="🚫 Отмена",
            callback_data=TaskEditCallback(task_id=tid, action="cancel").pack(),
        ),
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data=TaskEditCallback(task_id=tid, action="accept").pack(),
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- TITLE sub-screen ----------


def render_title(task: dict) -> str:
    current = html.escape(task.get("title") or "—")
    return (
        "📌 <b>Новое название</b>\n\n"
        f"Текущее: <b>{current}</b>\n\n"
        "Отправь новое название <b>текстом</b>, <b>голосом</b> или <b>кружком</b>."
    )


def build_back_only_kb(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="← Назад",
                callback_data=TaskEditCallback(task_id=task_id, action="main").pack(),
            )
        ]]
    )


# ---------- DESCRIPTION sub-screen ----------


def render_description(task: dict) -> str:
    current = task.get("description")
    current_line = html.escape(current) if current else "—"
    return (
        "📝 <b>Новое описание</b>\n\n"
        f"Текущее: {current_line}\n\n"
        "Отправь новое описание <b>текстом</b>, <b>голосом</b> или <b>кружком</b>.\n"
        "Чтобы стереть — нажми кнопку ниже."
    )


def build_description_kb(task_id: int, has_desc: bool) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if has_desc:
        rows.append([
            InlineKeyboardButton(
                text="🗑 Стереть описание",
                callback_data=TaskEditCallback(task_id=task_id, action="clear_desc").pack(),
            )
        ])
    rows.append([
        InlineKeyboardButton(
            text="← Назад",
            callback_data=TaskEditCallback(task_id=task_id, action="main").pack(),
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- DATE picker ----------


def _initial_date_from_task(task: dict) -> date:
    """Какую дату подсветить при первом открытии календаря."""
    dl = task.get("deadline")
    if dl:
        try:
            return _to_msk(datetime.fromisoformat(dl)).date()
        except (TypeError, ValueError):
            pass
    return datetime.now(tz=_MSK).date()


def _safe_day(year: int, month: int, day: int) -> int:
    """Если день не помещается в месяц (31 → февраль) — урезаем."""
    last = calendar.monthrange(year, month)[1]
    return min(day, last)


def render_date(year: int, month: int, day: int) -> str:
    return (
        "📅 <b>Выберите дату</b>\n\n"
        f"<b>{_MONTHS_RU[month - 1]} {year}</b>\n"
        f"Выбрано: <b>{day:02d}.{month:02d}.{year}</b>"
    )


def build_date_kb(
    task_id: int, year: int, month: int, day: int, *, has_deadline: bool = False
) -> InlineKeyboardMarkup:
    """Календарь.

    Раскладка:
      Row 1: ← <year> →
      Row 2: ← <месяц> →
      Rows 3..N: дни месяца по 7 в ряд (Telegram inline-row cap = 8,
                 даже для 31-дневных месяцев укладываемся в 5 рядов).
                 Выбранный день — с точкой ●.
      Row N+1: ← Назад · [🗑 Снять] · ✅ Применить
                «Снять дедлайн» появляется только если у задачи он есть.
    """
    def _cb(action: str, **kw: int) -> str:
        return TaskEditDateCallback(
            task_id=task_id, action=action, year=year, month=month, day=day, **kw
        ).pack()

    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="←", callback_data=_cb("prev_y")),
            InlineKeyboardButton(text=str(year), callback_data="te:noop"),
            InlineKeyboardButton(text="→", callback_data=_cb("next_y")),
        ],
        [
            InlineKeyboardButton(text="←", callback_data=_cb("prev_m")),
            InlineKeyboardButton(text=_MONTHS_RU[month - 1], callback_data="te:noop"),
            InlineKeyboardButton(text="→", callback_data=_cb("next_m")),
        ],
    ]

    last_day = calendar.monthrange(year, month)[1]
    cols = 7
    days = list(range(1, last_day + 1))
    for chunk_start in range(0, len(days), cols):
        chunk = days[chunk_start : chunk_start + cols]
        rows.append([
            InlineKeyboardButton(
                text=(f"●{d}" if d == day else str(d)),
                callback_data=TaskEditDateCallback(
                    task_id=task_id, action="day", year=year, month=month, day=d
                ).pack(),
            )
            for d in chunk
        ])

    bottom_row: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text="← Назад",
            callback_data=TaskEditDateCallback(
                task_id=task_id, action="back", year=year, month=month, day=day
            ).pack(),
        )
    ]
    if has_deadline:
        bottom_row.append(
            InlineKeyboardButton(
                text="🗑 Снять",
                callback_data=TaskEditDateCallback(
                    task_id=task_id, action="clear", year=year, month=month, day=day
                ).pack(),
            )
        )
    bottom_row.append(
        InlineKeyboardButton(
            text="✅ Применить",
            callback_data=TaskEditDateCallback(
                task_id=task_id, action="accept", year=year, month=month, day=day
            ).pack(),
        )
    )
    rows.append(bottom_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shift_date(year: int, month: int, day: int, *, dy: int = 0, dm: int = 0) -> tuple[int, int, int]:
    """Меняем год/месяц безопасно (день обрезается до последнего в месяце)."""
    new_year = year + dy
    new_month = month + dm
    while new_month < 1:
        new_month += 12
        new_year -= 1
    while new_month > 12:
        new_month -= 12
        new_year += 1
    return new_year, new_month, _safe_day(new_year, new_month, day)


# ---------- TIME picker ----------


def _initial_time_from_task(task: dict) -> tuple[int, int]:
    """Какое время подсветить при первом открытии time-picker'a."""
    dl = task.get("deadline")
    if dl:
        try:
            dt = _to_msk(datetime.fromisoformat(dl))
            return dt.hour, (dt.minute // 5) * 5
        except (TypeError, ValueError):
            pass
    return 9, 0


def render_time(hour: int, minute: int) -> str:
    return (
        "🕐 <b>Выберите время</b>\n\n"
        f"Выбрано: <b>{hour:02d}:{minute:02d}</b>"
    )


def build_time_kb(
    task_id: int, hour: int, minute: int, *, has_deadline: bool = False
) -> InlineKeyboardMarkup:
    """Time-picker:
      Row 1: ← HH →
      Rows 2..7: минуты, 2 столбца × 6 строк = 12 кнопок (00,05,…,55).
      Row 8: ← Назад · [🗑 Снять] · ✅ Применить
              «Снять дедлайн» появляется только если у задачи он есть.
    """
    def _cb(action: str, **kw: int) -> str:
        return TaskEditTimeCallback(
            task_id=task_id, action=action, hour=hour, minute=minute, **kw
        ).pack()

    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="←", callback_data=_cb("prev_h")),
            InlineKeyboardButton(text=f"{hour:02d}", callback_data="te:noop"),
            InlineKeyboardButton(text="→", callback_data=_cb("next_h")),
        ],
    ]

    minutes = [i * 5 for i in range(12)]  # 0..55
    for r in range(6):
        left = minutes[r * 2]
        right = minutes[r * 2 + 1]
        rows.append([
            InlineKeyboardButton(
                text=(f"●{hour:02d}:{left:02d}" if left == minute else f"{hour:02d}:{left:02d}"),
                callback_data=TaskEditTimeCallback(
                    task_id=task_id, action="min", hour=hour, minute=left
                ).pack(),
            ),
            InlineKeyboardButton(
                text=(f"●{hour:02d}:{right:02d}" if right == minute else f"{hour:02d}:{right:02d}"),
                callback_data=TaskEditTimeCallback(
                    task_id=task_id, action="min", hour=hour, minute=right
                ).pack(),
            ),
        ])

    bottom_row: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text="← Назад",
            callback_data=TaskEditTimeCallback(
                task_id=task_id, action="back", hour=hour, minute=minute
            ).pack(),
        )
    ]
    if has_deadline:
        bottom_row.append(
            InlineKeyboardButton(
                text="🗑 Снять",
                callback_data=TaskEditTimeCallback(
                    task_id=task_id, action="clear", hour=hour, minute=minute
                ).pack(),
            )
        )
    bottom_row.append(
        InlineKeyboardButton(
            text="✅ Применить",
            callback_data=TaskEditTimeCallback(
                task_id=task_id, action="accept", hour=hour, minute=minute
            ).pack(),
        )
    )
    rows.append(bottom_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shift_hour(hour: int, dh: int) -> int:
    return (hour + dh) % 24


# ---------- builder facade ----------


def screen_main(task: dict) -> tuple[str, InlineKeyboardMarkup]:
    return render_main(task), build_main_kb(task)


def screen_title(task: dict) -> tuple[str, InlineKeyboardMarkup]:
    return render_title(task), build_back_only_kb(task["id"])


def screen_description(task: dict) -> tuple[str, InlineKeyboardMarkup]:
    return render_description(task), build_description_kb(
        task["id"], has_desc=bool(task.get("description"))
    )


def screen_date(task: dict, *, year: int, month: int, day: int) -> tuple[str, InlineKeyboardMarkup]:
    return render_date(year, month, day), build_date_kb(
        task["id"], year, month, day, has_deadline=bool(task.get("deadline"))
    )


def screen_time(task: dict, *, hour: int, minute: int) -> tuple[str, InlineKeyboardMarkup]:
    return render_time(hour, minute), build_time_kb(
        task["id"], hour, minute, has_deadline=bool(task.get("deadline"))
    )

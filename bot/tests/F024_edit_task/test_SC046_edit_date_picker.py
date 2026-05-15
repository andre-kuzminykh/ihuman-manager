"""
SC046 — календарь для редактирования дедлайна:
- ряд года с ←/→
- ряд месяца с ←/→
- дни не более 7 в ряд (Telegram inline-row cap = 8; даже 31-дневные
  месяцы укладываются в 5 рядов)
- последний ряд: «← Назад» (и «🗑 Снять» если есть дедлайн) · «✅ Применить»
- shift_date корректно меняет месяц/год и обрезает день.

## Трассируемость
Feature: F024
Scenario: SC046 — date-picker.
"""

from __future__ import annotations

from node.task.answer.task_edit_answer import build_date_kb, render_date, shift_date


def test_render_date_shows_selected() -> None:
    text = render_date(2026, 5, 14)
    assert "Май 2026" in text
    assert "14.05.2026" in text


def test_date_kb_year_row_then_month_row() -> None:
    kb = build_date_kb(7, 2026, 5, 14)
    # Row 0: ← 2026 →
    row0 = [b.text for b in kb.inline_keyboard[0]]
    assert row0 == ["←", "2026", "→"]
    # Row 1: ← Май →
    row1 = [b.text for b in kb.inline_keyboard[1]]
    assert row1 == ["←", "Май", "→"]


def test_date_kb_day_rows_have_at_most_7_cols() -> None:
    """Telegram-лимит на inline-ряд — 8 кнопок; используем 7 (week-like)."""
    kb = build_date_kb(7, 2026, 5, 14)
    day_rows = kb.inline_keyboard[2:-1]
    for row in day_rows:
        assert len(row) <= 7, f"row has {len(row)} buttons (cap 7)"
    flat = [b.text for row in day_rows for b in row]
    highlighted = [x for x in flat if x.startswith("●")]
    assert highlighted == ["●14"]
    # Все 31 день мая представлены
    expected_days = {str(d) for d in range(1, 32)}
    presented = {x.lstrip("●") for x in flat}
    assert expected_days.issubset(presented)


def test_date_kb_31_day_month_fits_in_5_rows_max() -> None:
    """Январь = 31 день, ceil(31/7) = 5 рядов."""
    kb = build_date_kb(7, 2026, 1, 15)
    day_rows = kb.inline_keyboard[2:-1]
    assert len(day_rows) <= 5


def test_date_kb_last_row_is_back_and_accept_always() -> None:
    """Нижний ряд календаря — только «Назад» и «Применить»,
    независимо от has_deadline. Снять дедлайн — голосом/текстом."""
    for has_dl in (False, True):
        kb = build_date_kb(7, 2026, 5, 14, has_deadline=has_dl)
        last = [b.text for b in kb.inline_keyboard[-1]]
        assert last == ["← Назад", "✅ Применить"]
        assert "🗑 Снять" not in last


def test_shift_date_month_overflow_keeps_year() -> None:
    assert shift_date(2026, 5, 14, dm=+1) == (2026, 6, 14)
    assert shift_date(2026, 5, 14, dm=-1) == (2026, 4, 14)


def test_shift_date_year_overflow() -> None:
    assert shift_date(2026, 1, 14, dm=-1) == (2025, 12, 14)
    assert shift_date(2026, 12, 14, dm=+1) == (2027, 1, 14)


def test_shift_date_clamps_day_when_target_month_shorter() -> None:
    # 31 января → февраль → 28 (или 29 в високосном). 2026 — невисокосный → 28.
    assert shift_date(2026, 1, 31, dm=+1) == (2026, 2, 28)


def test_shift_date_year_jump() -> None:
    assert shift_date(2026, 5, 14, dy=+1) == (2027, 5, 14)
    assert shift_date(2026, 5, 14, dy=-1) == (2025, 5, 14)

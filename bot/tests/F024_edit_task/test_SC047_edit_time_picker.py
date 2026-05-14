"""
SC047 — time-picker:
- 1 ряд — час с ←/→
- 6 рядов × 2 столбца — минуты (00,05,…,55)
- последний ряд — «← Назад» и «✅ Применить»
- shift_hour корректно крутит 0..23.

## Трассируемость
Feature: F024
Scenario: SC047 — time-picker.
"""

from __future__ import annotations

from node.task.answer.task_edit_answer import build_time_kb, render_time, shift_hour


def test_render_time_shows_selected_value() -> None:
    assert "09:00" in render_time(9, 0)
    assert "23:55" in render_time(23, 55)


def test_time_kb_hour_row_first() -> None:
    kb = build_time_kb(7, 9, 0)
    row0 = [b.text for b in kb.inline_keyboard[0]]
    assert row0 == ["←", "09", "→"]


def test_time_kb_minute_grid_2x6_5min_steps() -> None:
    kb = build_time_kb(7, 9, 25)
    # Минутные ряды — между header и footer.
    minute_rows = kb.inline_keyboard[1:-1]
    assert len(minute_rows) == 6
    for row in minute_rows:
        assert len(row) == 2

    flat = [b.text for row in minute_rows for b in row]
    # 12 кнопок: 00,05,10,…,55, плюс одна с точкой
    assert len(flat) == 12
    highlighted = [x for x in flat if x.startswith("●")]
    assert highlighted == ["●09:25"]
    cleaned = [x.lstrip("●") for x in flat]
    expected = [f"09:{m:02d}" for m in range(0, 60, 5)]
    assert sorted(cleaned) == sorted(expected)


def test_time_kb_footer_back_and_accept_when_no_deadline() -> None:
    kb = build_time_kb(7, 9, 0, has_deadline=False)
    last = [b.text for b in kb.inline_keyboard[-1]]
    assert last == ["← Назад", "✅ Применить"]


def test_time_kb_footer_includes_clear_when_has_deadline() -> None:
    kb = build_time_kb(7, 9, 0, has_deadline=True)
    last = [b.text for b in kb.inline_keyboard[-1]]
    assert last == ["← Назад", "🗑 Снять", "✅ Применить"]


def test_shift_hour_wraps_24h() -> None:
    assert shift_hour(0, -1) == 23
    assert shift_hour(23, +1) == 0
    assert shift_hour(12, +5) == 17

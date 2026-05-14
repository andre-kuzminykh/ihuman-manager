"""
SC044 — главный экран редактирования содержит все обязательные ряды кнопок.

## Трассируемость
Feature: F024
Scenario: SC044 — главный экран редактирования.
"""

from __future__ import annotations

from node.task.answer.task_edit_answer import build_main_kb, render_main


def _task(**overrides: object) -> dict:
    base = {
        "id": 7,
        "title": "Подготовить отчёт",
        "description": "По продажам Q1",
        "deadline": "2026-05-14T15:00:00+03:00",
        "priority": "medium",
    }
    base.update(overrides)
    return base


def _row_texts(kb) -> list[list[str]]:
    return [[b.text for b in row] for row in kb.inline_keyboard]


def test_main_screen_text_includes_current_fields() -> None:
    text = render_main(_task())
    assert "Подготовить отчёт" in text
    assert "По продажам Q1" in text
    # MSK rendering: deadline +03 → 15:00
    assert "14.05.2026 · 15:00" in text
    # Hint instructing user about text/voice/circle input.
    assert "голосом" in text.lower()


def test_main_kb_layout_with_description_and_deadline() -> None:
    rows = _row_texts(build_main_kb(_task()))
    # 1) изменить название (full row)
    assert rows[0] == ["📌 Изменить название"]
    # 2) изменить описание (full row)
    assert rows[1] == ["📝 Изменить описание"]
    # 3) очистка описания, т.к. есть current description
    assert rows[2] == ["🗑 Стереть описание"]
    # 4) дата · время (две кнопки)
    assert rows[3] == ["📅 Дата", "🕐 Время"]
    # 5) очистка дедлайна, т.к. есть current deadline
    assert rows[4] == ["🗑 Снять дедлайн"]
    # 6) приоритет (три кнопки, текущий — с точкой)
    prio_row = rows[5]
    assert len(prio_row) == 3
    assert any("●" in x for x in prio_row)  # current selected highlight
    # 7) отмена · готово
    assert rows[-1] == ["🚫 Отмена", "✅ Готово"]


def test_main_kb_no_clear_buttons_when_empty() -> None:
    rows = _row_texts(build_main_kb(_task(description=None, deadline=None)))
    flat = [b for row in rows for b in row]
    assert "🗑 Стереть описание" not in flat
    assert "🗑 Снять дедлайн" not in flat


def test_main_kb_priority_highlight_follows_value() -> None:
    for prio in ("low", "medium", "high"):
        rows = _row_texts(build_main_kb(_task(priority=prio)))
        prio_row = next(r for r in rows if any("🟢" in x or "🟡" in x or "🔴" in x for x in r))
        assert len(prio_row) == 3
        highlighted = [x for x in prio_row if "●" in x]
        assert len(highlighted) == 1
        # the highlighted button corresponds to current priority
        emoji_map = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        assert emoji_map[prio] in highlighted[0]

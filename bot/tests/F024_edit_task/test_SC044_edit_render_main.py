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


def test_main_kb_layout_compact_5_rows() -> None:
    """Раскладка после убирания «Стереть описание» / «Снять дедлайн»:
       ровно 5 рядов независимо от наличия описания/дедлайна.
    """
    rows = _row_texts(build_main_kb(_task()))
    assert rows[0] == ["📌 Изменить название"]
    assert rows[1] == ["📝 Изменить описание"]
    assert rows[2] == ["📅 Дата", "🕐 Время"]
    prio_row = rows[3]
    assert len(prio_row) == 3
    assert any("●" in x for x in prio_row)
    assert rows[4] == ["🚫 Отмена", "✅ Готово"]
    assert len(rows) == 5


def test_main_kb_has_no_clear_buttons_ever() -> None:
    """Кнопок 🗑 «Стереть описание» / «Снять дедлайн» нет ни при наличии,
    ни при отсутствии соответствующих полей — очистка только текстом/голосом."""
    for desc, deadline in [
        ("есть", "2026-05-14T15:00:00+03:00"),
        (None, None),
        ("есть", None),
        (None, "2026-05-14T15:00:00+03:00"),
    ]:
        rows = _row_texts(build_main_kb(_task(description=desc, deadline=deadline)))
        flat = [b for row in rows for b in row]
        assert "🗑 Стереть описание" not in flat
        assert "🗑 Снять дедлайн" not in flat
        assert "🗑 Стереть" not in flat
        assert "🗑 Снять" not in flat


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

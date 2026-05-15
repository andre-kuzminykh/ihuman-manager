"""
SC045 — подэкраны «название» и «описание» рисуют текущие значения
и предлагают ввод текстом/голосом/кружком.

## Трассируемость
Feature: F024
Scenario: SC045 — подэкраны редактирования полей.
"""

from __future__ import annotations

from node.task.answer.task_edit_answer import (
    render_description,
    render_title,
    screen_description,
    screen_title,
)


def _task(**o: object) -> dict:
    base = {
        "id": 1,
        "title": "Старое название",
        "description": "Старое описание",
        "deadline": None,
        "priority": "medium",
    }
    base.update(o)
    return base


def test_title_screen_shows_current_and_input_hint() -> None:
    text = render_title(_task())
    assert "Старое название" in text
    assert "голосом" in text.lower() or "голос" in text.lower()
    assert "кружком" in text or "кружок" in text


def test_description_screen_shows_current() -> None:
    text = render_description(_task())
    assert "Старое описание" in text


def test_description_screen_handles_empty() -> None:
    text = render_description(_task(description=None))
    assert "—" in text  # placeholder


def test_screen_title_kb_has_only_back() -> None:
    _, kb = screen_title(_task())
    flat = [b.text for row in kb.inline_keyboard for b in row]
    assert "← Назад" in flat


def test_screen_description_kb_only_back() -> None:
    """Подэкран описания — только «← Назад». Стирание делается текстом/голосом."""
    for desc in ("есть", None):
        _, kb = screen_description(_task(description=desc))
        flat = [b.text for row in kb.inline_keyboard for b in row]
        assert flat == ["← Назад"]
        assert "🗑 Стереть описание" not in flat

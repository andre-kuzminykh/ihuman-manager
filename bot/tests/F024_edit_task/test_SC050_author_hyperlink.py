"""
Author hyperlink (👤) and title source-link must render in:
  - task card (TaskCreatedAnswer / TaskCardAnswer / chat-ingested cards)
  - F024 edit screen (render_main)

Regression catch: оба рендерера должны строить идентичный 👤-блок и
кликабельный заголовок из task["source_sender_*"] / task["source_chat_*"].

## Трассируемость
Feature: F001, F003, F005, F024
Scenario: SC050 — гиперссылка на автора в карточке (и в экране редактирования).
"""

from __future__ import annotations

import pytest

from node.task.answer.task_created_answer import render_task_card
from node.task.answer.task_edit_answer import render_main


def _task(**overrides: object) -> dict:
    base: dict = {
        "id": 1,
        "title": "Подготовить отчёт",
        "description": "По продажам Q1",
        "deadline": None,
        "priority": "medium",
        "source_sender_display": "Анна Иванова",
        "source_sender_user_id": 123456,
        "source_sender_username": "anna_ivanova",
        "source_chat_username": "team_chat",
        "chat_id": -1001234567890,
        "source_message_id": 42,
    }
    base.update(overrides)
    return base


# ---------- task card (created/ingested) ----------


def test_task_card_renders_author_hyperlink_via_user_id() -> None:
    """user_id есть → ссылка на профиль `tg://user?id=...`."""
    text = render_task_card(_task())
    assert '👤 <a href="tg://user?id=123456">Анна Иванова</a>' in text


def test_task_card_falls_back_to_username_when_no_user_id() -> None:
    """Если user_id нет — ссылка на https://t.me/<username>."""
    text = render_task_card(_task(source_sender_user_id=None))
    assert '👤 <a href="https://t.me/anna_ivanova">Анна Иванова</a>' in text


def test_task_card_plain_text_author_when_neither_user_id_nor_username() -> None:
    """Если нет ни id, ни username — имя без гиперссылки, но 👤 остаётся."""
    text = render_task_card(_task(
        source_sender_user_id=None, source_sender_username=None
    ))
    assert "👤 Анна Иванова" in text
    assert "<a href=" not in text or "tg://user" not in text


def test_task_card_no_author_line_on_self_write() -> None:
    """Self-write → source_sender_display=None → строка 👤 не рендерится."""
    text = render_task_card(_task(source_sender_display=None))
    assert "👤" not in text


def test_task_card_title_links_to_supergroup_message() -> None:
    """Для супергруппы (chat_id < -100…) ссылка вида t.me/c/<id>/<msg>."""
    text = render_task_card(_task())
    # -1001234567890 → t.me/c/1234567890/42
    assert '<a href="https://t.me/c/1234567890/42">' in text


def test_task_card_escapes_html_in_sender_display() -> None:
    """HTML-инъекция в имени должна быть экранирована."""
    text = render_task_card(_task(source_sender_display="<script>x</script>"))
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


# ---------- edit screen (F024 render_main) ----------


def test_edit_screen_renders_author_hyperlink() -> None:
    """В режиме редактирования 👤-строка тоже должна быть с гиперссылкой."""
    text = render_main(_task())
    assert '👤 <a href="tg://user?id=123456">Анна Иванова</a>' in text


def test_edit_screen_renders_title_source_link() -> None:
    """Заголовок в режиме редактирования — кликабелен на исходное сообщение."""
    text = render_main(_task())
    assert '<a href="https://t.me/c/1234567890/42"><b>Подготовить отчёт</b></a>' in text


def test_edit_screen_no_author_line_on_self_write() -> None:
    text = render_main(_task(source_sender_display=None))
    assert "👤" not in text


def test_edit_screen_title_plain_when_no_source_url() -> None:
    """Если нет ни chat_id, ни chat_username — заголовок без обёртки <a>.
    👤 при этом может быть кликабельным — это отдельная строка."""
    text = render_main(_task(
        chat_id=None,
        source_chat_username=None,
        source_message_id=None,
    ))
    # Заголовок — просто bold, не link.
    assert "📌 <b>Подготовить отчёт</b>" in text
    # И никаких t.me/c/ ссылок:
    assert "t.me/c/" not in text


def test_edit_screen_falls_back_to_username() -> None:
    text = render_main(_task(source_sender_user_id=None))
    assert '👤 <a href="https://t.me/anna_ivanova">Анна Иванова</a>' in text

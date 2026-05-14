"""
SC048 — LLM-edit на главном экране редактирования.

Свободный текст или транскрибированное аудио уходит в /tasks/{id}/llm-edit и
карточка перерисовывается с обновлёнными полями.

## Трассируемость
Feature: F024
Scenario: SC048 — естественный язык на главном экране.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handler.v1.user.task.F024 import task_edit_widget as tew


@pytest.mark.asyncio
async def test_main_text_routes_to_llm_edit_and_refreshes_card() -> None:
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "task_id": 7,
        "card_chat_id": 42,
        "card_message_id": 99,
    })
    state.update_data = AsyncMock()

    message = AsyncMock()
    message.text = "поменяй приоритет на высокий"
    message.delete = AsyncMock()

    fake_api = MagicMock()
    fake_api.llm_edit = AsyncMock(return_value={
        "id": 7,
        "title": "Подготовить отчёт",
        "description": None,
        "deadline": None,
        "priority": "high",
    })
    fake_bot = MagicMock()
    fake_bot.edit_message_text = AsyncMock()

    with patch.object(tew, "TasksAPI", return_value=fake_api), \
         patch.object(tew, "get_bot", return_value=fake_bot):
        await tew.on_main_text(message, state)

    fake_api.llm_edit.assert_awaited_once_with(7, "поменяй приоритет на высокий")
    message.delete.assert_awaited()
    fake_bot.edit_message_text.assert_awaited()
    # обновили именно ту карточку, что в FSM
    kwargs = fake_bot.edit_message_text.call_args.kwargs
    assert kwargs["chat_id"] == 42
    assert kwargs["message_id"] == 99


@pytest.mark.asyncio
async def test_main_text_empty_does_not_call_api() -> None:
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"task_id": 7})
    message = AsyncMock()
    message.text = ""
    message.delete = AsyncMock()

    fake_api = MagicMock()
    fake_api.llm_edit = AsyncMock()

    with patch.object(tew, "TasksAPI", return_value=fake_api):
        await tew.on_main_text(message, state)
    fake_api.llm_edit.assert_not_called()
    message.delete.assert_awaited()


@pytest.mark.asyncio
async def test_title_text_updates_title_via_update_then_back_to_main() -> None:
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "task_id": 7,
        "card_chat_id": 42,
        "card_message_id": 99,
    })
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()

    message = AsyncMock()
    message.text = "Новый заголовок"
    message.delete = AsyncMock()

    fake_api = MagicMock()
    fake_api.update = AsyncMock(return_value={"id": 7})
    fake_api.get = AsyncMock(return_value={
        "id": 7,
        "title": "Новый заголовок",
        "description": None,
        "deadline": None,
        "priority": "medium",
    })
    fake_bot = MagicMock()
    fake_bot.edit_message_text = AsyncMock()

    with patch.object(tew, "TasksAPI", return_value=fake_api), \
         patch.object(tew, "get_bot", return_value=fake_bot):
        await tew.on_title_text(message, state)

    fake_api.update.assert_awaited_once()
    kwargs = fake_api.update.call_args
    assert kwargs.args[0] == 7
    assert kwargs.kwargs["title"] == "Новый заголовок"
    state.set_state.assert_awaited()


@pytest.mark.asyncio
async def test_desc_text_clear_keyword_unsets_description() -> None:
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "task_id": 7,
        "card_chat_id": 42,
        "card_message_id": 99,
    })
    state.set_state = AsyncMock()

    message = AsyncMock()
    message.text = "удалить"
    message.delete = AsyncMock()

    fake_api = MagicMock()
    fake_api.update = AsyncMock(return_value={"id": 7})
    fake_api.get = AsyncMock(return_value={
        "id": 7, "title": "Х", "description": None,
        "deadline": None, "priority": "medium",
    })
    fake_bot = MagicMock()
    fake_bot.edit_message_text = AsyncMock()

    with patch.object(tew, "TasksAPI", return_value=fake_api), \
         patch.object(tew, "get_bot", return_value=fake_bot):
        await tew.on_desc_text(message, state)

    fake_api.update.assert_awaited_once()
    # на пустое описание идёт unset_description=True
    assert fake_api.update.call_args.kwargs.get("unset_description") is True

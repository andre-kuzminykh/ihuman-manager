"""
SC048 — LLM-edit на главном экране редактирования.

Свободный текст или транскрибированное аудио уходит в /tasks/{id}/llm-edit и
карточка перерисовывается с обновлёнными полями.

Также: при нажатии ✏️ на карточке задачи **старая карточка удаляется**,
а ниже появляется **новое** сообщение — экран редактирования.

## Трассируемость
Feature: F024
Scenario: SC048 — естественный язык на главном экране.
                 BR066 — Edit click deletes old card and posts new edit-screen
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from callback.tasks_callback import TaskActionCallback
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
async def test_open_edit_deletes_old_card_and_sends_new_edit_screen() -> None:
    """Старая карточка задачи исчезает (delete), и **ниже** появляется
    новая — экран редактирования. В FSM сохраняем id/координаты НОВОГО
    сообщения, не старого."""
    state = AsyncMock()
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()

    old_msg = AsyncMock()
    old_msg.chat = MagicMock(id=42)
    old_msg.message_id = 11
    old_msg.delete = AsyncMock()
    new_msg = MagicMock()
    new_msg.chat = MagicMock(id=42)
    new_msg.message_id = 999
    old_msg.answer = AsyncMock(return_value=new_msg)

    cb = AsyncMock()
    cb.message = old_msg
    cb.answer = AsyncMock()

    fake_api = MagicMock()
    fake_api.get = AsyncMock(return_value={
        "id": 7,
        "title": "Подготовить отчёт",
        "description": None,
        "deadline": None,
        "priority": "medium",
    })

    with patch.object(tew, "TasksAPI", return_value=fake_api):
        await tew.on_open_from_card(
            cb, TaskActionCallback(task_id=7, action="edit"), state
        )

    old_msg.delete.assert_awaited_once()
    old_msg.answer.assert_awaited_once()
    # FSM хранит координаты НОВОГО сообщения, не старого.
    update_kwargs = state.update_data.call_args.kwargs
    assert update_kwargs["card_chat_id"] == 42
    assert update_kwargs["card_message_id"] == 999
    assert update_kwargs["task_id"] == 7


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

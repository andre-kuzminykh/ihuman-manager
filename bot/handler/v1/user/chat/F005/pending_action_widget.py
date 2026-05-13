"""
Виджет: действия на карточке-согласовании (Reject / Edit / Accept).

## Трассируемость
Feature: F005, F017
Scenarios: SC012, SC013, SC014, F017 — естественный язык меняет поля.

Edit-flow:
1. Пользователь нажимает ✏️ Edit.
2. Бот показывает «Edit draft #N (before Accept)» с текущими полями + просит
   написать естественным языком (или ввести команду).
3. Следующее сообщение пользователя летит в `/pending-tasks/{id}/llm-edit`.
4. Бот заново отрисовывает карточку с обновлёнными полями.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callback.pending_callback import PendingActionCallback
from node.pending.answer.pending_card_answer import (
    build_pending_kb,
    render_pending_text,
)
from node.pending.code.pending_approve_code import PendingApproveCode
from node.task.answer.task_card_answer import TaskCardAnswer
from service.api.base_api import APIError
from service.api.pending_tasks_api import PendingTasksAPI
from state.pending_state import PendingEditStates


router = Router(name="chat.F005.pending_action")


_PRIORITY_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}


def _render_edit_draft(pending: dict) -> str:
    draft = pending.get("draft") or {}
    title = draft.get("title") or pending.get("source_text", "")[:80]
    description = draft.get("description") or "—"
    deadline = draft.get("deadline") or "—"
    priority = (draft.get("priority") or "medium").lower()
    prio_emoji = _PRIORITY_EMOJI.get(priority, "🟡")
    return (
        f"✏ Edit draft #{pending.get('id')} (before Accept)\n\n"
        f"Сейчас задано:\n"
        f"📌 Title — {title}\n"
        f"📝 Description — {description}\n"
        f"{prio_emoji} Priority — {priority}\n"
        f"📅 Due — {deadline}\n\n"
        "Напиши что изменить — пойму естественный язык.\n"
        "Можно одним сообщением сразу несколько полей: "
        "«переименуй на X, дедлайн пятница 18:00, приоритет высокий».\n"
        "Или просто отправь /cancel чтобы вернуться к карточке."
    )


@router.callback_query(PendingActionCallback.filter(F.action == "approve"))
async def on_approve(cb: CallbackQuery, callback_data: PendingActionCallback) -> None:
    code = PendingApproveCode()
    result = await code.approve(callback_data.pending_id)
    if result["answer_name"] == "task_created":
        await TaskCardAnswer().run(
            event=cb,
            user_lang="ru",
            data={"task": result["data"]["task"], "title_prefix": "✅ Задача создана"},
        )
    else:
        await cb.answer(result["data"].get("message", "Ошибка"), show_alert=True)


@router.callback_query(PendingActionCallback.filter(F.action == "reject"))
async def on_reject(cb: CallbackQuery, callback_data: PendingActionCallback) -> None:
    code = PendingApproveCode()
    result = await code.reject(callback_data.pending_id)
    text = (
        "🚫 Отклонено"
        if result["answer_name"] == "pending_rejected"
        else result["data"].get("message", "Ошибка")
    )
    if cb.message is not None:
        await cb.message.edit_text(text)
    await cb.answer()


@router.callback_query(PendingActionCallback.filter(F.action == "edit"))
async def on_edit(
    cb: CallbackQuery,
    callback_data: PendingActionCallback,
    state: FSMContext,
) -> None:
    api = PendingTasksAPI()
    try:
        pending = await api.get(callback_data.pending_id)
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return
    await state.set_state(PendingEditStates.awaiting_title)  # переиспользуем как «жду текст»
    await state.update_data(pending_id=callback_data.pending_id)
    if cb.message is not None:
        await cb.message.answer(_render_edit_draft(pending))
    await cb.answer()


@router.message(PendingEditStates.awaiting_title, F.text == "/cancel")
async def on_cancel_edit(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Окей, возвращаемся к карточке.")


@router.message(PendingEditStates.awaiting_title)
async def on_edit_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    pending_id = data.get("pending_id")
    if not pending_id or not message.text:
        await state.clear()
        return
    api = PendingTasksAPI()
    try:
        updated = await api.llm_edit(pending_id, message.text.strip())
    except APIError as exc:
        await message.answer(f"Ошибка: {exc.message}")
        await state.clear()
        return
    await message.answer(
        render_pending_text(updated),
        reply_markup=build_pending_kb(updated["id"]),
        disable_web_page_preview=True,
    )
    await state.clear()
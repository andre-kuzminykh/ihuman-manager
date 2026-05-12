"""
Виджет: действия на карточке-согласовании (approve/reject/edit).

## Трассируемость
Feature: F005
Scenarios: SC012, SC013, SC014
"""

from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callback.pending_callback import PendingActionCallback
from node.pending.code.pending_approve_code import PendingApproveCode
from node.task.answer.task_card_answer import TaskCardAnswer
from service.api.base_api import APIError
from service.api.pending_tasks_api import PendingTasksAPI
from state.pending_state import PendingEditStates


router = Router(name="chat.F005.pending_action")


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


@router.callback_query(PendingActionCallback.filter(F.action == "edit_title"))
async def on_edit_title(
    cb: CallbackQuery,
    callback_data: PendingActionCallback,
    state: FSMContext,
) -> None:
    await state.set_state(PendingEditStates.awaiting_title)
    await state.update_data(pending_id=callback_data.pending_id)
    await cb.message.answer("Введите новый заголовок:") if cb.message else None
    await cb.answer()


@router.callback_query(PendingActionCallback.filter(F.action == "edit_deadline"))
async def on_edit_deadline(
    cb: CallbackQuery,
    callback_data: PendingActionCallback,
    state: FSMContext,
) -> None:
    await state.set_state(PendingEditStates.awaiting_deadline)
    await state.update_data(pending_id=callback_data.pending_id)
    await cb.message.answer(
        "Введите дедлайн (например, 'завтра 18:00' или '2026-05-20 15:00'):"
    ) if cb.message else None
    await cb.answer()


@router.message(PendingEditStates.awaiting_title)
async def on_title_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    pending_id = data.get("pending_id")
    if not pending_id or not message.text:
        await state.clear()
        return
    api = PendingTasksAPI()
    try:
        await api.update(pending_id, title=message.text.strip())
    except APIError as exc:
        await message.answer(f"Ошибка: {exc.message}")
        await state.clear()
        return
    await message.answer("✏️ Заголовок обновлён. Нажмите «Принять» на карточке выше.")
    await state.clear()


@router.message(PendingEditStates.awaiting_deadline)
async def on_deadline_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    pending_id = data.get("pending_id")
    if not pending_id or not message.text:
        await state.clear()
        return
    # Простейший парсер ISO; полный парсер находится на бэкенде (extractor).
    parsed = _try_parse_iso(message.text.strip())
    if parsed is None:
        # фоллбек: оставляем как текст в draft, бэкенд разберёт
        api = PendingTasksAPI()
        try:
            await api.update(pending_id, draft={"deadline_hint": message.text.strip()})
        except APIError as exc:
            await message.answer(f"Ошибка: {exc.message}")
            await state.clear()
            return
        await message.answer("🕒 Дедлайн сохранён в подсказке. Нажмите «Принять».")
        await state.clear()
        return
    api = PendingTasksAPI()
    try:
        await api.update(pending_id, deadline=parsed)
    except APIError as exc:
        await message.answer(f"Ошибка: {exc.message}")
        await state.clear()
        return
    await message.answer("📅 Дедлайн обновлён. Нажмите «Принять» на карточке.")
    await state.clear()


def _try_parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None

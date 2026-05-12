"""
Виджет: управление направлениями.

## Трассируемость
Feature: F009
Scenarios: SC022, SC023, SC024
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callback.directions_callback import DirectionActionCallback
from node.directions.answer.direction_created_answer import DirectionCreatedAnswer
from node.directions.answer.directions_list_answer import DirectionsListAnswer
from service.api.base_api import APIError
from service.api.directions_api import DirectionsAPI
from state.direction_state import DirectionStates


router = Router(name="directions.F009")


@router.message(Command("directions"))
async def on_directions(message: Message) -> None:
    api = DirectionsAPI()
    items = await api.list(user_id=message.from_user.id) if message.from_user else []
    await DirectionsListAnswer().run(event=message, user_lang="ru", data={"directions": items})


@router.message(Command("direction"))
async def on_direction_create(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not command.args:
        await state.set_state(DirectionStates.awaiting_name)
        await message.answer("Введите название направления:")
        return
    await _create_direction(message, command.args.strip())


@router.message(DirectionStates.awaiting_name)
async def on_direction_name(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.clear()
    await _create_direction(message, message.text.strip())


async def _create_direction(message: Message, name: str) -> None:
    api = DirectionsAPI()
    user_id = message.from_user.id if message.from_user else 0
    try:
        direction = await api.create(user_id=user_id, name=name)
    except APIError as exc:
        await DirectionCreatedAnswer().run(
            event=message,
            user_lang="ru",
            data={"direction": None, "message": exc.message},
        )
        return
    await DirectionCreatedAnswer().run(
        event=message, user_lang="ru", data={"direction": direction}
    )


@router.callback_query(DirectionActionCallback.filter(F.action.in_({"favorite", "unfavorite"})))
async def on_favorite_toggle(
    cb: CallbackQuery, callback_data: DirectionActionCallback
) -> None:
    api = DirectionsAPI()
    value = callback_data.action == "favorite"
    try:
        await api.set_favorite(callback_data.direction_id, value)
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return
    items = await api.list(user_id=cb.from_user.id) if cb.from_user else []
    if cb.message is not None:
        from node.directions.answer.directions_list_answer import DirectionsListAnswer

        # перерисовываем
        await cb.message.delete()
        await DirectionsListAnswer().run(
            event=cb.message, user_lang="ru", data={"directions": items}
        )
    await cb.answer()


@router.callback_query(DirectionActionCallback.filter(F.action == "delete"))
async def on_delete(cb: CallbackQuery, callback_data: DirectionActionCallback) -> None:
    api = DirectionsAPI()
    try:
        await api.delete(callback_data.direction_id)
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return
    await cb.answer("Удалено")
    if cb.message is not None:
        items = await api.list(user_id=cb.from_user.id) if cb.from_user else []
        await cb.message.delete()
        await DirectionsListAnswer().run(
            event=cb.message, user_lang="ru", data={"directions": items}
        )

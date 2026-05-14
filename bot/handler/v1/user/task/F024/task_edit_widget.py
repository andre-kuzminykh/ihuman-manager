"""
Виджет: редактирование уже созданной задачи (F024).

## Трассируемость
Feature: F024
Scenarios: SC044, SC045, SC046, SC047, SC048

UX-контракт:
1. На карточке задачи есть кнопка ✏️ «Редактировать» → её жмут.
2. Карточка превращается в экран редактирования (edit_text над тем же
   сообщением, ничего нового не присылаем).
3. Главный экран:
     - 📌 Изменить название (вся строка)
     - 📝 Изменить описание (вся строка)
     - 📅 Дата · 🕐 Время (две кнопки)
     - 🟢 🟡 🔴 (приоритет — мгновенный тогл)
     - 🚫 Отмена · ✅ Готово
   Плюс на главном можно прислать текст/голос/кружок — он уйдёт в LLM-edit.
4. На подэкране «название/описание» — ввод текстом/голосом/кружком,
   виджет обновляется в реальном времени, есть «← Назад».
5. На подэкране «дата» — календарь: год ←/→, месяц ←/→,
   дни 11×3, «← Назад» и «✅ Применить».
6. На подэкране «время» — час ←/→, минуты 2×6 (00,05,…,55),
   «← Назад» и «✅ Применить».
7. По «Готово»/«Отмена»/любому Accept мы возвращаемся к карточке задачи.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from callback.task_edit_callback import (
    TaskEditCallback,
    TaskEditDateCallback,
    TaskEditTimeCallback,
)
from callback.tasks_callback import TaskActionCallback
from core.loader import get_bot
from node.task.answer.task_card_answer import TaskCardAnswer
from node.task.answer.task_created_answer import build_task_card_kb, render_task_card
from node.task.answer.task_edit_answer import (
    _initial_date_from_task,
    _initial_time_from_task,
    screen_date,
    screen_description,
    screen_main,
    screen_time,
    screen_title,
    shift_date,
    shift_hour,
)
from service.api.base_api import APIError
from service.api.tasks_api import TasksAPI
from service.api.voice_api import VoiceAPI
from state.task_edit_state import TaskEditStates


log = logging.getLogger("task.F024.edit")
router = Router(name="task.F024.edit")

_MSK = timezone(timedelta(hours=3))


# ---------- helpers ----------


async def _show_card(cb: CallbackQuery, task: dict) -> None:
    """Восстановить вид карточки задачи поверх того же сообщения."""
    text = render_task_card(task)
    kb = build_task_card_kb(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            # текст не изменился — игнор
            pass


async def _edit_in_place(
    state: FSMContext, text: str, kb: InlineKeyboardMarkup
) -> None:
    """Обновить главное сообщение редактора (карточку) по сохранённым координатам."""
    data = await state.get_data()
    chat_id = data.get("card_chat_id")
    message_id = data.get("card_message_id")
    if not chat_id or not message_id:
        return
    bot = get_bot()
    try:
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=kb,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        log.warning("edit_in_place failed: %s", exc)


async def _refresh_task(state: FSMContext, task_id: int) -> dict:
    api = TasksAPI()
    return await api.get(task_id)


def _combine_deadline(year: int, month: int, day: int, hour: int, minute: int) -> str:
    dt = datetime(year, month, day, hour, minute, tzinfo=_MSK)
    return dt.isoformat()


def _split_deadline(task: dict) -> tuple[int, int, int, int, int]:
    """Достаём (Y, M, D, h, m) из текущего deadline задачи или дефолт."""
    dl = task.get("deadline")
    if dl:
        try:
            dt = datetime.fromisoformat(dl)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(_MSK)
            return dt.year, dt.month, dt.day, dt.hour, (dt.minute // 5) * 5
        except (TypeError, ValueError):
            pass
    today = datetime.now(tz=_MSK)
    return today.year, today.month, today.day, 9, 0


# ---------- entrypoint ----------


@router.callback_query(TaskActionCallback.filter(F.action == "edit"))
async def on_open_from_card(
    cb: CallbackQuery, callback_data: TaskActionCallback, state: FSMContext
) -> None:
    """Жмём ✏️ «Редактировать» на карточке задачи.

    UX: старая карточка задачи **исчезает** (delete), а ниже появляется
    **новое** сообщение — экран редактирования. Дальше все подэкраны
    (название/описание/дата/время) перерисовываются поверх этого нового
    сообщения через edit_text — никаких новых сообщений не плодим.
    """
    api = TasksAPI()
    try:
        task = await api.get(callback_data.task_id)
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return

    text, kb = screen_main(task)
    if cb.message is not None:
        # 1) Старая карточка исчезает.
        try:
            await cb.message.delete()
        except Exception as exc:
            log.warning("delete old card failed: %s", exc)
        # 2) Появляется новая — экран редактирования.
        try:
            new_msg = await cb.message.answer(
                text, reply_markup=kb, disable_web_page_preview=True
            )
        except Exception as exc:
            log.warning("send edit screen failed: %s", exc)
            await cb.answer("Не удалось открыть редактор", show_alert=True)
            return
        await state.set_state(TaskEditStates.main)
        await state.update_data(
            task_id=callback_data.task_id,
            card_chat_id=new_msg.chat.id,
            card_message_id=new_msg.message_id,
        )
    await cb.answer()


# ---------- main-screen actions ----------


@router.callback_query(TaskEditCallback.filter(F.action == "main"))
async def on_back_to_main(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    text, kb = screen_main(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.main)
    await cb.answer()


@router.callback_query(TaskEditCallback.filter(F.action == "title"))
async def on_open_title(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    text, kb = screen_title(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.awaiting_title)
    await cb.answer()


@router.callback_query(TaskEditCallback.filter(F.action == "desc"))
async def on_open_desc(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    text, kb = screen_description(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.awaiting_description)
    await cb.answer()


@router.callback_query(TaskEditCallback.filter(F.action == "clear_desc"))
async def on_clear_desc(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    api = TasksAPI()
    try:
        await api.update(callback_data.task_id, unset_description=True)
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return
    task = await _refresh_task(state, callback_data.task_id)
    text, kb = screen_main(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.main)
    await cb.answer("Описание стёрто")


@router.callback_query(TaskEditCallback.filter(F.action == "clear_deadline"))
async def on_clear_deadline(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    api = TasksAPI()
    try:
        await api.llm_edit(callback_data.task_id, "снять дедлайн, deadline=null")
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return
    task = await _refresh_task(state, callback_data.task_id)
    text, kb = screen_main(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.main)
    await cb.answer("Дедлайн снят")


@router.callback_query(TaskEditCallback.filter(F.action.in_({"prio_low", "prio_medium", "prio_high"})))
async def on_toggle_priority(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    prio = callback_data.action.removeprefix("prio_")
    api = TasksAPI()
    try:
        await api.update(callback_data.task_id, priority=prio)
    except APIError as exc:
        await cb.answer(exc.message, show_alert=True)
        return
    task = await _refresh_task(state, callback_data.task_id)
    text, kb = screen_main(task)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await cb.answer()


@router.callback_query(TaskEditCallback.filter(F.action == "cancel"))
async def on_cancel(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    await state.clear()
    await _show_card(cb, task)
    await cb.answer()


@router.callback_query(TaskEditCallback.filter(F.action == "accept"))
async def on_accept(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    await state.clear()
    await _show_card(cb, task)
    await cb.answer("Сохранено")


# ---------- DATE picker ----------


@router.callback_query(TaskEditCallback.filter(F.action == "date"))
async def on_open_date(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    d = _initial_date_from_task(task)
    text, kb = screen_date(task, year=d.year, month=d.month, day=d.day)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.picking_date)
    await state.update_data(
        edit_year=d.year, edit_month=d.month, edit_day=d.day
    )
    await cb.answer()


@router.callback_query(TaskEditDateCallback.filter())
async def on_date_action(
    cb: CallbackQuery, callback_data: TaskEditDateCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    year = callback_data.year or _initial_date_from_task(task).year
    month = callback_data.month or _initial_date_from_task(task).month
    day = callback_data.day or _initial_date_from_task(task).day

    if callback_data.action == "prev_y":
        year, month, day = shift_date(year, month, day, dy=-1)
    elif callback_data.action == "next_y":
        year, month, day = shift_date(year, month, day, dy=+1)
    elif callback_data.action == "prev_m":
        year, month, day = shift_date(year, month, day, dm=-1)
    elif callback_data.action == "next_m":
        year, month, day = shift_date(year, month, day, dm=+1)
    elif callback_data.action == "day":
        day = callback_data.day
    elif callback_data.action == "back":
        text, kb = screen_main(task)
        if cb.message is not None:
            try:
                await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except Exception:
                pass
        await state.set_state(TaskEditStates.main)
        await cb.answer()
        return
    elif callback_data.action == "clear":
        # 🗑 Снять дедлайн прямо из календаря.
        api = TasksAPI()
        try:
            await api.llm_edit(callback_data.task_id, "снять дедлайн, deadline=null")
        except APIError as exc:
            await cb.answer(exc.message, show_alert=True)
            return
        task = await _refresh_task(state, callback_data.task_id)
        text, kb = screen_main(task)
        if cb.message is not None:
            try:
                await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except Exception:
                pass
        await state.set_state(TaskEditStates.main)
        await cb.answer("Дедлайн снят")
        return
    elif callback_data.action == "accept":
        # Применяем дату; время — текущее из task (или 09:00).
        _, _, _, hh, mm = _split_deadline(task)
        iso = _combine_deadline(year, month, day, hh, mm)
        api = TasksAPI()
        try:
            await api.update(callback_data.task_id, deadline=iso)
        except APIError as exc:
            await cb.answer(exc.message, show_alert=True)
            return
        task = await _refresh_task(state, callback_data.task_id)
        text, kb = screen_main(task)
        if cb.message is not None:
            try:
                await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except Exception:
                pass
        await state.set_state(TaskEditStates.main)
        await cb.answer("Дата применена")
        return
    else:
        await cb.answer()
        return

    # Перерисовать календарь с обновлёнными координатами.
    await state.update_data(edit_year=year, edit_month=month, edit_day=day)
    text, kb = screen_date(task, year=year, month=month, day=day)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await cb.answer()


# ---------- TIME picker ----------


@router.callback_query(TaskEditCallback.filter(F.action == "time"))
async def on_open_time(
    cb: CallbackQuery, callback_data: TaskEditCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    hh, mm = _initial_time_from_task(task)
    text, kb = screen_time(task, hour=hh, minute=mm)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await state.set_state(TaskEditStates.picking_time)
    await state.update_data(edit_hour=hh, edit_minute=mm)
    await cb.answer()


@router.callback_query(TaskEditTimeCallback.filter())
async def on_time_action(
    cb: CallbackQuery, callback_data: TaskEditTimeCallback, state: FSMContext
) -> None:
    task = await _refresh_task(state, callback_data.task_id)
    hh, mm = callback_data.hour, callback_data.minute

    if callback_data.action == "prev_h":
        hh = shift_hour(hh, -1)
    elif callback_data.action == "next_h":
        hh = shift_hour(hh, +1)
    elif callback_data.action == "min":
        mm = callback_data.minute
    elif callback_data.action == "back":
        text, kb = screen_main(task)
        if cb.message is not None:
            try:
                await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except Exception:
                pass
        await state.set_state(TaskEditStates.main)
        await cb.answer()
        return
    elif callback_data.action == "clear":
        api = TasksAPI()
        try:
            await api.llm_edit(callback_data.task_id, "снять дедлайн, deadline=null")
        except APIError as exc:
            await cb.answer(exc.message, show_alert=True)
            return
        task = await _refresh_task(state, callback_data.task_id)
        text, kb = screen_main(task)
        if cb.message is not None:
            try:
                await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except Exception:
                pass
        await state.set_state(TaskEditStates.main)
        await cb.answer("Дедлайн снят")
        return
    elif callback_data.action == "accept":
        y, m, d, _, _ = _split_deadline(task)
        iso = _combine_deadline(y, m, d, hh, mm)
        api = TasksAPI()
        try:
            await api.update(callback_data.task_id, deadline=iso)
        except APIError as exc:
            await cb.answer(exc.message, show_alert=True)
            return
        task = await _refresh_task(state, callback_data.task_id)
        text, kb = screen_main(task)
        if cb.message is not None:
            try:
                await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except Exception:
                pass
        await state.set_state(TaskEditStates.main)
        await cb.answer("Время применено")
        return
    else:
        await cb.answer()
        return

    await state.update_data(edit_hour=hh, edit_minute=mm)
    text, kb = screen_time(task, hour=hh, minute=mm)
    if cb.message is not None:
        try:
            await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    await cb.answer()


# ---------- FSM-bound message handlers (text/voice in edit flow) ----------


async def _safe_delete(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass


async def _transcribe_message(message: Message) -> str | None:
    """Скачиваем и расшифровываем voice/audio/video_note/video через VoiceAPI."""
    bot = get_bot()
    media = message.voice or message.audio or message.video_note or message.video
    if media is None:
        return None
    file_name = "voice.ogg"
    if message.video_note or message.video:
        file_name = "video.mp4"
    elif message.audio:
        file_name = "audio.ogg"
    from io import BytesIO

    buffer = BytesIO()
    try:
        await bot.download(media, destination=buffer)
    except Exception as exc:
        log.warning("download failed: %s", exc)
        return None
    try:
        text = await VoiceAPI().transcribe(audio_bytes=buffer.getvalue(), file_name=file_name)
    except Exception as exc:
        log.warning("transcribe failed: %s", exc)
        return None
    return (text or "").strip() or None


async def _apply_field(
    state: FSMContext,
    task_id: int,
    *,
    field: str,
    value: str | None,
) -> dict | None:
    """field ∈ {title, description}. Возвращает обновлённую задачу или None."""
    api = TasksAPI()
    try:
        if field == "title" and value:
            await api.update(task_id, title=value)
        elif field == "description":
            if value:
                await api.update(task_id, description=value)
            else:
                await api.update(task_id, unset_description=True)
        else:
            return None
    except APIError as exc:
        log.warning("apply_field failed: %s", exc.message)
        return None
    return await _refresh_task(state, task_id)


async def _apply_llm(
    state: FSMContext, task_id: int, instruction: str
) -> dict | None:
    api = TasksAPI()
    try:
        return await api.llm_edit(task_id, instruction)
    except APIError as exc:
        log.warning("llm_edit failed: %s", exc.message)
        return None


# main: free-form text → LLM-edit
@router.message(TaskEditStates.main, F.chat.type == ChatType.PRIVATE, F.text)
async def on_main_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_id = data.get("task_id")
    await _safe_delete(message)
    if not task_id or not message.text:
        return
    task = await _apply_llm(state, task_id, message.text.strip())
    if task is None:
        return
    text, kb = screen_main(task)
    await _edit_in_place(state, text, kb)


# main: voice/audio/video_note/video → transcribe → LLM-edit
@router.message(
    TaskEditStates.main,
    F.chat.type == ChatType.PRIVATE,
    F.voice | F.audio | F.video_note | F.video,
)
async def on_main_voice(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_id = data.get("task_id")
    transcribed = await _transcribe_message(message)
    await _safe_delete(message)
    if not task_id or not transcribed:
        return
    task = await _apply_llm(state, task_id, transcribed)
    if task is None:
        return
    text, kb = screen_main(task)
    await _edit_in_place(state, text, kb)


# title: text/voice → set title
@router.message(TaskEditStates.awaiting_title, F.chat.type == ChatType.PRIVATE, F.text)
async def on_title_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_id = data.get("task_id")
    raw = (message.text or "").strip()
    await _safe_delete(message)
    if not task_id or not raw:
        return
    task = await _apply_field(state, task_id, field="title", value=raw[:200])
    if task is None:
        return
    text, kb = screen_main(task)
    await _edit_in_place(state, text, kb)
    await state.set_state(TaskEditStates.main)


@router.message(
    TaskEditStates.awaiting_title,
    F.chat.type == ChatType.PRIVATE,
    F.voice | F.audio | F.video_note | F.video,
)
async def on_title_voice(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_id = data.get("task_id")
    transcribed = await _transcribe_message(message)
    await _safe_delete(message)
    if not task_id or not transcribed:
        return
    task = await _apply_field(state, task_id, field="title", value=transcribed[:200])
    if task is None:
        return
    text, kb = screen_main(task)
    await _edit_in_place(state, text, kb)
    await state.set_state(TaskEditStates.main)


# description: text/voice → set description
@router.message(TaskEditStates.awaiting_description, F.chat.type == ChatType.PRIVATE, F.text)
async def on_desc_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_id = data.get("task_id")
    raw = (message.text or "").strip()
    await _safe_delete(message)
    if not task_id or not raw:
        return
    if raw.lower() in {"удалить", "стереть", "очистить", "-", "—"}:
        task = await _apply_field(state, task_id, field="description", value=None)
    else:
        task = await _apply_field(state, task_id, field="description", value=raw[:2000])
    if task is None:
        return
    text, kb = screen_main(task)
    await _edit_in_place(state, text, kb)
    await state.set_state(TaskEditStates.main)


@router.message(
    TaskEditStates.awaiting_description,
    F.chat.type == ChatType.PRIVATE,
    F.voice | F.audio | F.video_note | F.video,
)
async def on_desc_voice(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_id = data.get("task_id")
    transcribed = await _transcribe_message(message)
    await _safe_delete(message)
    if not task_id or not transcribed:
        return
    task = await _apply_field(state, task_id, field="description", value=transcribed[:2000])
    if task is None:
        return
    text, kb = screen_main(task)
    await _edit_in_place(state, text, kb)
    await state.set_state(TaskEditStates.main)


# ---------- noop swallow for placeholder buttons ----------


@router.callback_query(F.data == "te:noop")
async def on_noop(cb: CallbackQuery) -> None:
    await cb.answer()

"""
core.vocab — текстовые ресурсы (RU).
"""

from __future__ import annotations

START = (
    "Привет! Я iHuman Manager — помогу вести задачи.\n\n"
    "• /new <текст> — создать задачу\n"
    "• голосовое — задача из голоса\n"
    "• /tasks — список задач\n"
    "• /favorites — избранные\n"
    "• /directions — направления\n"
    "• /digest — задачи на сегодня\n"
    "• /setup_chat (в чате) — слушать чат и извлекать задачи"
)

EMPTY_TEXT = "Текст задачи не может быть пустым."
VOICE_FAILED = "Не удалось распознать голос. Попробуйте ещё раз."
NOT_SUBSCRIBED_CHAT = "Чат не подписан. Вызови /setup_chat в нужном чате."
CHAT_SUBSCRIBED = "Чат подписан — слушаю и буду присылать задачи на согласование."
TASK_CREATED = "✅ Задача создана"
TASK_UPDATED = "✏️ Задача обновлена"
PENDING_CARD_TITLE = "📋 На согласование"
DEADLINE_NOTICE_TITLE = "⏰ Дедлайн"
MORNING_DIGEST_TITLE = "☀️ Доброе утро! План на сегодня"
NO_TASKS_TODAY = "На сегодня задач нет, добавьте /new"
DRAFT_ASK_EDIT = "Что меняем?"
INVALID_TRANSITION = "Этот переход недоступен"
STATUS_LABEL = {
    "backlog": "📌 Backlog",
    "todo": "🟡 Todo",
    "in_progress": "🔵 В работе",
    "paused": "⏸ Пауза",
    "done": "✅ Готово",
    "cancelled": "🚫 Отменено",
}


def status_label(status: str) -> str:
    return STATUS_LABEL.get(status, status)

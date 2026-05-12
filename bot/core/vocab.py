"""
core.vocab — текстовые ресурсы (RU).
"""

from __future__ import annotations

START = (
    "Привет! Я iHuman Manager — помогу вести задачи.\n\n"
    "• /new <текст> — создать задачу (LLM-парсинг)\n"
    "• /task <title> | <deadline> | <direction> — ручной ввод одной строкой\n"
    "• голосовое — задача из голоса\n"
    "• /tasks — список задач\n"
    "• /today — задачи на сегодня\n"
    "• /overdue — просрочки\n"
    "• /active — todo + in_progress + blocked\n"
    "• /favorites — избранные\n"
    "• /directions — направления\n"
    "• /digest — дайджест на сегодня\n"
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
EVENING_DIGEST_TITLE = "🌙 Итоги дня"
NO_TASKS_TODAY = "На сегодня задач нет, добавьте /new"
NO_OVERDUE = "Просрочек нет."
NO_ACTIVE = "Активных задач нет."
DUPLICATE_FOUND = "Похожая активная задача уже есть"
DRAFT_ASK_EDIT = "Что меняем?"
INVALID_TRANSITION = "Этот переход недоступен"
STATUS_LABEL = {
    "backlog": "📌 Backlog",
    "todo": "🟡 Todo",
    "in_progress": "🔵 В работе",
    "paused": "⏸ Пауза",
    "blocked": "🛑 Заблокировано",
    "done": "✅ Готово",
    "cancelled": "🚫 Отменено",
}


def status_label(status: str) -> str:
    return STATUS_LABEL.get(status, status)

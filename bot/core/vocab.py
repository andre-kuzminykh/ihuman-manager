"""
core.vocab — текстовые ресурсы (RU).
"""

from __future__ import annotations

START = (
    "Привет! Отправь задачу <b>текстом</b> или <b>голосом</b> — я её сохраню."
)
START_LEGACY = (
    "<b>Команды:</b>\n"
    "• /new — создать задачу из текста (то же, что обычное сообщение)\n"
    "• /task — ручной ввод одной строкой: /task Заголовок | YYYY-MM-DDTHH:MM | Направление\n"
    "• /tasks — все задачи\n"
    "• /today — на сегодня\n"
    "• /overdue — просрочки\n"
    "• /active — активные\n"
    "• /favorites — избранные ⭐\n"
    "• /directions — направления\n"
    "• /people — контакты, с кем общался\n"
    "• /digest — план на сегодня\n"
    "• /evening — итоги дня"
)

MULTI_TASKS_FOUND = "Нашёл несколько задач — создаю {count}:"

EMPTY_TEXT = "Текст задачи не может быть пустым."
VOICE_FAILED = "Не удалось распознать голос. Попробуйте ещё раз."
NOT_SUBSCRIBED_CHAT = "Чат не подписан. Вызови /setup_chat в нужном чате."
CHAT_SUBSCRIBED = "Чат подписан — слушаю и буду присылать задачи на согласование."
TASK_CREATED = "✅ Задача создана"
TASK_UPDATED = "✏️ Задача обновлена"
PENDING_CARD_TITLE = "📋 На согласование"
DEADLINE_NOTICE_TITLE = "⏰ Дедлайн"
MORNING_DIGEST_TITLE = "☀️ Доброе утро!"
MORNING_DIGEST_SUBTITLE = "План на сегодня"
EVENING_DIGEST_TITLE = "🌙 Итоги дня"
EVENING_DIGEST_SUBTITLE = "Что было сегодня"
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

"""
core.vocab — текстовые ресурсы (RU).
"""

from __future__ import annotations

START = (
    "Привет! Я iHuman Manager — помогу вести задачи.\n\n"
    "📝 <b>Просто пришли мне текст или голосовое</b> — и я заведу из них задачи. "
    "В одном сообщении можно сразу несколько задач — я их разделю.\n\n"
    "<b>Команды:</b>\n"
    "• /new &lt;текст&gt; — то же, что просто сообщение (явная команда)\n"
    "• /task &lt;title&gt; | &lt;deadline&gt; | &lt;direction&gt; — ручной ввод одной строкой\n"
    "• /tasks — все задачи\n"
    "• /today — на сегодня\n"
    "• /overdue — просрочки\n"
    "• /active — активные\n"
    "• /favorites — избранные ⭐\n"
    "• /directions — направления\n"
    "• /digest — план на сегодня\n"
    "• /evening — итоги дня\n"
    "• /setup_chat (в групповом чате) — слушать чат и извлекать задачи"
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

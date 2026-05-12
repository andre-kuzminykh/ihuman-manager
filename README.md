# iHuman Manager

Telegram-бот + бэкенд для управления задачами CEO/соло-предпринимателя.

## Что умеет

| ID | Фича | Как пользоваться |
|----|------|-------------------|
| F001 | Создание задачи текстом | `/new текст задачи` или просто сообщение в DM боту |
| F002 | Создание задачи голосом | Voice-сообщение боту → распознаётся → задача |
| F003 | Жизненный цикл (backlog → todo → in_progress → done) | inline-кнопки на карточке, /tasks |
| F004 | Избранное (⭐) | inline-кнопка ⭐ на карточке |
| F005 | Извлечение задач из группового чата/канала | Добавь бота в чат → `/setup_chat` → бот шлёт карточки-согласования |
| F006 | Уведомление о дедлайне | Приходит в момент дедлайна, можно перенести/завершить/отменить/паузить |
| F007 | Утренний дайджест 09:00 МСК | Автоматически каждое утро |
| F008 | Планирование (старт/конец) | Кнопка ⏰ или `/schedule TASK_ID HH:MM` |
| F009 | Направления | `/directions`, привязка к задаче, избранное направление = задачи избранные |

## Архитектура

```
┌─────────────────┐       HTTP / REST        ┌──────────────────────┐
│  Telegram Bot   │ ──────────────────────▶  │  Backend Service     │
│  (aiogram 3)    │                          │  (FastAPI)           │
│  виджеты:       │  ◀── JSON responses ──   │  model → repo →      │
│  Trigger/Code/  │  ── HTTP requests ───▶   │  service → API       │
│  Answer         │                          │  PostgreSQL          │
└─────────────────┘                          └──────────────────────┘
```

Подробности: см. `prd.json` (источник правды), `backend/`, `bot/`.

## Запуск (dev)

1. Скопируй переменные окружения:
   ```bash
   cp .env.example .env
   # отредактируй .env — впиши BOT_TOKEN, OPENAI_API_KEY, BOT_USERNAME
   ```
2. Подними БД и бэкенд:
   ```bash
   docker compose up -d postgres
   cd backend
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn main:app --reload --port 8000
   ```
3. В новой сессии — бота:
   ```bash
   cd bot
   pip install -r requirements.txt
   python app.py
   ```

## Тесты

```bash
# backend
cd backend && pytest -q
# bot
cd bot && pytest -q
```

## Переменные окружения

См. `.env.example`. Главное:

- `BOT_TOKEN` — токен Telegram-бота (BotFather)
- `BOT_USERNAME` — username бота без `@`, нужно для определения тегов в чатах
- `OPENAI_API_KEY` — для LLM-извлечения задач и распознавания голоса
- `BACKEND_URL` — куда бот ходит за API (по умолчанию `http://localhost:8000`)
- `DB_*` — креды Postgres

## Структура

```
ihuman-manager/
├── prd.json                  # источник правды по фичам/сценариям
├── docker-compose.yml
├── .env.example
├── backend/                  # FastAPI: model/schema/repo/service/api
└── bot/                      # aiogram 3: node + handler/widget + service/api
```

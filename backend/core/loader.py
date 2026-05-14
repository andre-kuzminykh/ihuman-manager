"""
core.loader — FastAPI app + регистрация роутеров и обработчиков ошибок.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from core.config import config


# Конфигурируем root logger РАНЬШЕ всех импортов, чтобы log.info() работал
# в alembic env.py и в каждом сервисе. uvicorn по умолчанию оставляет root
# на WARNING — поэтому без этого вызова INFO-трейсы тонут.
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,  # перебиваем настройку uvicorn если она уже что-то поставила
)


app = FastAPI(
    title="iHuman Manager Backend",
    version="0.1.0",
    description="Backend for Telegram task management bot (PRD F001–F009).",
)


def _wire() -> None:
    from api.v1.include_router import include_routers
    from api.v1.exception_handlers import register_exception_handlers

    register_exception_handlers(app)
    include_routers(app)


_wire()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

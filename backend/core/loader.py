"""
core.loader — FastAPI app + регистрация роутеров и обработчиков ошибок.
"""

from __future__ import annotations

from fastapi import FastAPI

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

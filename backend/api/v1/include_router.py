"""
api.v1.include_router — подключение всех роутеров под /api/v1.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.v1.endpoints import (
    chats_router,
    digest_router,
    directions_router,
    extractor_router,
    pending_tasks_router,
    scheduler_router,
    tasks_router,
    voice_router,
)
from core.config import config


def include_routers(app: FastAPI) -> None:
    prefix = config.API_V1_PREFIX
    app.include_router(tasks_router, prefix=prefix)
    app.include_router(directions_router, prefix=prefix)
    app.include_router(chats_router, prefix=prefix)
    app.include_router(pending_tasks_router, prefix=prefix)
    app.include_router(extractor_router, prefix=prefix)
    app.include_router(voice_router, prefix=prefix)
    app.include_router(digest_router, prefix=prefix)
    app.include_router(scheduler_router, prefix=prefix)

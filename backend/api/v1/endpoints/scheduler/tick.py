"""
## Трассируемость
Feature: F003, F006, F007
Scenarios: SC007, SC015, SC017, SC018, SC019
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from service.scheduler.scheduler_service import SchedulerService


router = APIRouter()
_service = SchedulerService()


class _TickRequest(BaseModel):
    now: datetime | None = None


@router.post("/tick")
async def tick(
    body: _TickRequest | None = None,
    session: AsyncSession = Depends(db_connect.get_session),
) -> dict[str, Any]:
    return await _service.tick(session, now=(body.now if body else None))

"""
## Трассируемость
Feature: F007, F011
Scenarios: SC018, SC019, SC028
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.digest.digest_schema import DigestResponseSchema
from service.digest.digest_service import DigestService


router = APIRouter()
_service = DigestService()


@router.get("/{user_id}", response_model=DigestResponseSchema)
async def get_digest(
    user_id: int,
    day: datetime | None = None,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DigestResponseSchema:
    return await _service.build(session, user_id=user_id, day=day)


@router.get("/{user_id}/evening", response_model=DigestResponseSchema)
async def get_evening_digest(
    user_id: int,
    day: datetime | None = None,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DigestResponseSchema:
    """Вечерний дайджест (F011)."""
    return await _service.build_evening(session, user_id=user_id, day=day)

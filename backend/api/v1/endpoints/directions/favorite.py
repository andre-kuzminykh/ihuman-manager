"""
## Трассируемость
Feature: F009
Scenarios: SC023
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.directions.direction_schema import DirectionResponseSchema
from service.directions.direction_service import DirectionService


router = APIRouter()
_service = DirectionService()


@router.post("/{direction_id}/favorite", response_model=DirectionResponseSchema)
async def add_favorite(
    direction_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DirectionResponseSchema:
    d = await _service.set_favorite(session, direction_id, value=True)
    return DirectionResponseSchema.model_validate(d)


@router.delete("/{direction_id}/favorite", response_model=DirectionResponseSchema)
async def remove_favorite(
    direction_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DirectionResponseSchema:
    d = await _service.set_favorite(session, direction_id, value=False)
    return DirectionResponseSchema.model_validate(d)

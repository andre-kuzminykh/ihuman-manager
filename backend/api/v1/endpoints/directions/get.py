"""
## Трассируемость
Feature: F009
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.directions.direction_schema import DirectionResponseSchema
from service.directions.direction_service import DirectionService


router = APIRouter()
_service = DirectionService()


@router.get("", response_model=list[DirectionResponseSchema])
async def list_directions(
    user_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> list[DirectionResponseSchema]:
    items = await _service.list_for_user(session, user_id)
    return [DirectionResponseSchema.model_validate(d) for d in items]


@router.get("/{direction_id}", response_model=DirectionResponseSchema)
async def get_direction(
    direction_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DirectionResponseSchema:
    d = await _service.get_or_404(session, direction_id)
    return DirectionResponseSchema.model_validate(d)

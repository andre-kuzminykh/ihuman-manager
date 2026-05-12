"""
## Трассируемость
Feature: F009
Scenarios: SC022, SC024
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.directions.direction_schema import (
    DirectionCreateSchema,
    DirectionResponseSchema,
)
from service.directions.direction_service import DirectionService


router = APIRouter()
_service = DirectionService()


@router.post("", response_model=DirectionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_direction(
    data: DirectionCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> DirectionResponseSchema:
    d = await _service.create(
        session, user_id=data.user_id, name=data.name, is_favorite=data.is_favorite
    )
    return DirectionResponseSchema.model_validate(d)

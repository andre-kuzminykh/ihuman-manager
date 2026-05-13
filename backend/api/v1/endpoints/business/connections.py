"""
POST /api/v1/business/connections — upsert бизнес-подключения.
GET  /api/v1/business/connections/{bc_id} — узнать owner_user_id.

## Трассируемость
Feature: F018
Scenarios: SC036, SC037
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.business.business_connection_schema import (
    BusinessConnectionCreateSchema,
    BusinessConnectionResponseSchema,
)
from service.business.business_connection_service import BusinessConnectionService


router = APIRouter()
_service = BusinessConnectionService()


@router.post("/connections", response_model=BusinessConnectionResponseSchema)
async def upsert_connection(
    data: BusinessConnectionCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> BusinessConnectionResponseSchema:
    obj = await _service.upsert(
        session,
        business_connection_id=data.business_connection_id,
        owner_user_id=data.owner_user_id,
        is_enabled=data.is_enabled,
        can_reply=data.can_reply,
    )
    return BusinessConnectionResponseSchema.model_validate(obj)


@router.get(
    "/connections/{business_connection_id}",
    response_model=BusinessConnectionResponseSchema,
)
async def get_connection(
    business_connection_id: str,
    session: AsyncSession = Depends(db_connect.get_session),
) -> BusinessConnectionResponseSchema:
    from repository.business.business_connection_repository import (
        BusinessConnectionRepository,
    )

    obj = await BusinessConnectionRepository().get_by_connection_id(
        session, business_connection_id
    )
    if obj is None:
        raise HTTPException(404, "business connection not found")
    return BusinessConnectionResponseSchema.model_validate(obj)

"""
## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.chat_subscription_schema import (
    ChatSubscriptionCreateSchema,
    ChatSubscriptionResponseSchema,
)
from service.chats.chat_subscription_service import ChatSubscriptionService


router = APIRouter()
_service = ChatSubscriptionService()


@router.post(
    "/subscribe",
    response_model=ChatSubscriptionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_chat(
    data: ChatSubscriptionCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> ChatSubscriptionResponseSchema:
    sub = await _service.subscribe(
        session,
        chat_id=data.chat_id,
        owner_user_id=data.owner_user_id,
        title=data.title,
    )
    return ChatSubscriptionResponseSchema.model_validate(sub)


@router.delete("/subscribe/{chat_id}")
async def unsubscribe_chat(
    chat_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> dict:
    await _service.unsubscribe(session, chat_id)
    return {"unsubscribed": True, "chat_id": chat_id}

"""
Chats endpoints.

## Трассируемость
Feature: F005
"""

from fastapi import APIRouter

from api.v1.endpoints.chats.subscribe import router as subscribe_router
from api.v1.endpoints.chats.ingest import router as ingest_router


router = APIRouter(tags=["chats"])
router.include_router(subscribe_router, prefix="/chats")
router.include_router(ingest_router, prefix="/messages")

__all__ = ["router"]

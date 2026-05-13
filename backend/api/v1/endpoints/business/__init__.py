"""
Business endpoints.

## Трассируемость
Feature: F018
"""

from fastapi import APIRouter

from api.v1.endpoints.business.connections import router as conn_router


router = APIRouter(prefix="/business", tags=["business"])
router.include_router(conn_router)

__all__ = ["router"]

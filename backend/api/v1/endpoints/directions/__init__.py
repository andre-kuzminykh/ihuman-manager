"""
Directions endpoints.

## Трассируемость
Feature: F009
"""

from fastapi import APIRouter

from api.v1.endpoints.directions.post import router as post_router
from api.v1.endpoints.directions.get import router as get_router
from api.v1.endpoints.directions.put import router as put_router
from api.v1.endpoints.directions.delete import router as delete_router
from api.v1.endpoints.directions.favorite import router as favorite_router


router = APIRouter(prefix="/directions", tags=["directions"])
router.include_router(post_router)
router.include_router(get_router)
router.include_router(put_router)
router.include_router(delete_router)
router.include_router(favorite_router)

__all__ = ["router"]

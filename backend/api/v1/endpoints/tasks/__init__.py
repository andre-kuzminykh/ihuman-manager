"""
Tasks endpoints.

## Трассируемость
Feature: F001, F002, F003, F004, F008, F009
"""

from fastapi import APIRouter

from api.v1.endpoints.tasks.post import router as post_router
from api.v1.endpoints.tasks.get import router as get_router
from api.v1.endpoints.tasks.put import router as put_router
from api.v1.endpoints.tasks.patch import router as patch_router
from api.v1.endpoints.tasks.delete import router as delete_router
from api.v1.endpoints.tasks.favorite import router as favorite_router


router = APIRouter(prefix="/tasks", tags=["tasks"])
router.include_router(post_router)
router.include_router(get_router)
router.include_router(put_router)
router.include_router(patch_router)
router.include_router(delete_router)
router.include_router(favorite_router)

__all__ = ["router"]

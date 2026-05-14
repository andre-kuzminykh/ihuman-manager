from api.v1.endpoints.tasks import router as tasks_router
from api.v1.endpoints.directions import router as directions_router
from api.v1.endpoints.chats import router as chats_router
from api.v1.endpoints.pending_tasks import router as pending_tasks_router
from api.v1.endpoints.extractor import router as extractor_router
from api.v1.endpoints.voice import router as voice_router
from api.v1.endpoints.digest import router as digest_router
from api.v1.endpoints.scheduler import router as scheduler_router
from api.v1.endpoints.business import router as business_router
from api.v1.endpoints.people import router as people_router

__all__ = [
    "tasks_router",
    "directions_router",
    "chats_router",
    "pending_tasks_router",
    "extractor_router",
    "voice_router",
    "digest_router",
    "scheduler_router",
    "business_router",
    "people_router",
]

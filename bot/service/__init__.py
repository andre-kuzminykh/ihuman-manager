"""
service — HTTP-клиенты к бэкенду. Бот не ходит в БД напрямую.
"""

from service.api.base_api import BaseAPI
from service.api.tasks_api import TasksAPI
from service.api.directions_api import DirectionsAPI
from service.api.chats_api import ChatsAPI
from service.api.pending_tasks_api import PendingTasksAPI
from service.api.voice_api import VoiceAPI
from service.api.extractor_api import ExtractorAPI
from service.api.digest_api import DigestAPI
from service.api.scheduler_api import SchedulerAPI

__all__ = [
    "BaseAPI",
    "TasksAPI",
    "DirectionsAPI",
    "ChatsAPI",
    "PendingTasksAPI",
    "VoiceAPI",
    "ExtractorAPI",
    "DigestAPI",
    "SchedulerAPI",
]

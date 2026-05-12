"""
repository — слой доступа к БД (только Model + Session).
"""

from repository.base_repository import BaseRepository
from repository.tasks.task_repository import TaskRepository
from repository.tasks.task_favorite_repository import TaskFavoriteRepository
from repository.tasks.task_status_change_repository import TaskStatusChangeRepository
from repository.directions.direction_repository import DirectionRepository
from repository.chats.chat_subscription_repository import ChatSubscriptionRepository
from repository.chats.message_context_repository import MessageContextRepository
from repository.chats.processed_message_repository import ProcessedMessageRepository
from repository.chats.pending_task_repository import PendingTaskRepository
from repository.notifications.notification_log_repository import NotificationLogRepository

__all__ = [
    "BaseRepository",
    "TaskRepository",
    "TaskFavoriteRepository",
    "TaskStatusChangeRepository",
    "DirectionRepository",
    "ChatSubscriptionRepository",
    "MessageContextRepository",
    "ProcessedMessageRepository",
    "PendingTaskRepository",
    "NotificationLogRepository",
]

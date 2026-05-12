"""
schema — Pydantic-схемы (DTO) для API.
"""

from schema.tasks.task_schema import (
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskStatusUpdateSchema,
    TaskResponseSchema,
    TaskListItemSchema,
)
from schema.directions.direction_schema import (
    DirectionCreateSchema,
    DirectionUpdateSchema,
    DirectionResponseSchema,
)
from schema.chats.chat_subscription_schema import (
    ChatSubscriptionCreateSchema,
    ChatSubscriptionResponseSchema,
)
from schema.chats.message_ingest_schema import MessageIngestSchema, MessageIngestResultSchema
from schema.chats.pending_task_schema import (
    PendingTaskResponseSchema,
    PendingTaskUpdateSchema,
)
from schema.extractor.extract_schema import ExtractRequestSchema, ExtractResponseSchema
from schema.voice.voice_schema import VoiceTranscribeResponseSchema
from schema.digest.digest_schema import DigestResponseSchema

__all__ = [
    "TaskCreateSchema",
    "TaskUpdateSchema",
    "TaskStatusUpdateSchema",
    "TaskResponseSchema",
    "TaskListItemSchema",
    "DirectionCreateSchema",
    "DirectionUpdateSchema",
    "DirectionResponseSchema",
    "ChatSubscriptionCreateSchema",
    "ChatSubscriptionResponseSchema",
    "MessageIngestSchema",
    "MessageIngestResultSchema",
    "PendingTaskResponseSchema",
    "PendingTaskUpdateSchema",
    "ExtractRequestSchema",
    "ExtractResponseSchema",
    "VoiceTranscribeResponseSchema",
    "DigestResponseSchema",
]

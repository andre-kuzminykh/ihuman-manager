"""
model.enums — общие enum-типы домена.
"""

from __future__ import annotations

import enum


class TaskStatus(str, enum.Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


# Граф допустимых переходов (BR008 + BR038)
ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.BACKLOG: {
        TaskStatus.TODO,
        TaskStatus.IN_PROGRESS,
        TaskStatus.BLOCKED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.TODO: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.PAUSED,
        TaskStatus.BLOCKED,
        TaskStatus.DONE,
        TaskStatus.CANCELLED,
        TaskStatus.BACKLOG,
    },
    TaskStatus.IN_PROGRESS: {
        TaskStatus.PAUSED,
        TaskStatus.BLOCKED,
        TaskStatus.DONE,
        TaskStatus.CANCELLED,
        TaskStatus.TODO,
    },
    TaskStatus.PAUSED: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.BLOCKED,
        TaskStatus.CANCELLED,
        TaskStatus.DONE,
        TaskStatus.TODO,
    },
    TaskStatus.BLOCKED: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.TODO,
        TaskStatus.DONE,
        TaskStatus.CANCELLED,
        TaskStatus.PAUSED,
    },
    TaskStatus.DONE: {TaskStatus.TODO},
    TaskStatus.CANCELLED: {TaskStatus.TODO, TaskStatus.BACKLOG},
}


class TaskSource(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    CHAT = "chat"
    MANUAL = "manual"


class NotificationKind(str, enum.Enum):
    DEADLINE = "deadline"
    MORNING_DIGEST = "morning_digest"
    EVENING_DIGEST = "evening_digest"

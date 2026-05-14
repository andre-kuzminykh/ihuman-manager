"""
forward_helper — извлечь инфо об оригинальном авторе пересланного сообщения.

## Трассируемость
Feature: F023 — поддержка forward
"""

from __future__ import annotations

from aiogram.types import Message


def extract_forward_info(message: Message) -> dict | None:
    """Если сообщение переслано — вернуть {'name': str, 'origin_kind': str} или None."""
    origin = getattr(message, "forward_origin", None)
    if origin is None:
        # старый API — forward_from / forward_from_chat
        ff = getattr(message, "forward_from", None)
        if ff is not None:
            full = " ".join(filter(None, [getattr(ff, "first_name", None), getattr(ff, "last_name", None)])).strip()
            name = full or (f"@{ff.username}" if getattr(ff, "username", None) else "Unknown")
            return {"name": name, "origin_kind": "user"}
        fc = getattr(message, "forward_from_chat", None)
        if fc is not None:
            name = getattr(fc, "title", None) or (f"@{fc.username}" if getattr(fc, "username", None) else "Channel")
            return {"name": name, "origin_kind": "chat"}
        return None

    # aiogram 3: forward_origin — discriminated union.
    sender_user = getattr(origin, "sender_user", None)
    if sender_user is not None:
        full = " ".join(filter(None, [getattr(sender_user, "first_name", None), getattr(sender_user, "last_name", None)])).strip()
        name = full or (f"@{sender_user.username}" if getattr(sender_user, "username", None) else "Unknown")
        return {"name": name, "origin_kind": "user"}
    sender_user_name = getattr(origin, "sender_user_name", None)
    if sender_user_name:
        return {"name": sender_user_name, "origin_kind": "hidden_user"}
    chat = getattr(origin, "chat", None) or getattr(origin, "sender_chat", None)
    if chat is not None:
        name = getattr(chat, "title", None) or (f"@{chat.username}" if getattr(chat, "username", None) else "Channel")
        return {"name": name, "origin_kind": "chat"}
    return None


def prefix_text_with_forward(text: str, message: Message) -> str:
    """Если сообщение переслано — добавить в начало текста '[Переслано от: <X>] '."""
    info = extract_forward_info(message)
    if not info:
        return text
    return f"[Переслано от: {info['name']}] {text}"

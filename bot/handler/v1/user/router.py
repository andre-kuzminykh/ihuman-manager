"""
router.py — корневой роутер v1/user. Собирает sub-routers по тегам/фичам.
"""

from __future__ import annotations

from aiogram import Router


def build_user_router() -> Router:
    root = Router(name="v1.user")

    # task
    from handler.v1.user.task.F001.new_task_widget import router as new_task_router
    from handler.v1.user.task.F003.task_status_widget import router as task_status_router
    from handler.v1.user.task.F003.tasks_list_widget import router as tasks_list_router
    from handler.v1.user.task.F004.favorite_widget import router as favorite_router
    from handler.v1.user.task.F012.shortcut_widget import router as shortcut_router
    from handler.v1.user.task.F014.manual_task_widget import router as manual_task_router

    # voice
    from handler.v1.user.voice.F002.voice_widget import router as voice_router

    # chat / pending
    from handler.v1.user.chat.F005.auto_subscribe_widget import router as auto_subscribe_router
    from handler.v1.user.chat.F005.setup_chat_widget import router as setup_chat_router
    from handler.v1.user.chat.F005.chat_message_widget import router as chat_message_router
    from handler.v1.user.chat.F005.pending_action_widget import router as pending_action_router

    # business (F018)
    from handler.v1.user.business.F018.business_connection_widget import (
        router as business_connection_router,
    )
    from handler.v1.user.business.F018.business_message_widget import (
        router as business_message_router,
    )

    # directions
    from handler.v1.user.directions.F009.directions_widget import router as directions_router

    # digest
    from handler.v1.user.digest.F007.digest_widget import router as digest_router

    # generic / start
    from handler.v1.user.start.start_widget import router as start_router

    for r in (
        start_router,
        auto_subscribe_router,
        business_connection_router,
        setup_chat_router,  # оставляем как ручной fallback
        manual_task_router,  # /task раньше /new — Command чёткий, конфликта нет
        shortcut_router,
        new_task_router,
        voice_router,
        task_status_router,
        tasks_list_router,
        favorite_router,
        pending_action_router,
        directions_router,
        digest_router,
        chat_message_router,  # catch-all для групповых сообщений — в конец
        business_message_router,  # business messages catch-all
    ):
        root.include_router(r)
    return root

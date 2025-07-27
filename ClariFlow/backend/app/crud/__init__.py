"""
CRUD operations for ClariFlow models.
"""

from .user import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user_last_seen,
    upsert_user,
    get_all_users,
    delete_user
)

from .chat_history import (
    create_chat_history,
    get_chat_history_by_user,
    get_chat_history_by_session,
    get_chat_history_by_id,
    update_chat_history,
    delete_chat_history,
    delete_chat_history_by_user,
    delete_chat_history_by_session,
    get_chat_history_count_by_user,
    get_chat_history_with_user
)

__all__ = [
    # User CRUD operations
    "get_user_by_email",
    "get_user_by_id", 
    "create_user",
    "update_user_last_seen",
    "upsert_user",
    "get_all_users",
    "delete_user",
    
    # Chat History CRUD operations
    "create_chat_history",
    "get_chat_history_by_user",
    "get_chat_history_by_session",
    "get_chat_history_by_id",
    "update_chat_history",
    "delete_chat_history",
    "delete_chat_history_by_user",
    "delete_chat_history_by_session",
    "get_chat_history_count_by_user",
    "get_chat_history_with_user"
] 
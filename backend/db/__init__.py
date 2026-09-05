"""
backend.db — database management package.

Public API (identical to the old flat backend/db.py):

    from backend.db import (
        init_db,
        get_next_thread_id, save_thread, get_all_threads,
        update_thread_time, rename_thread, remove_thread,
    )

Internal sub-modules
--------------------
connection   — get_db_path(), open_connection(), execute_with_retry()
threads      — all thread CRUD operations + init_db()
"""

from backend.db.connection import get_db_path, open_connection, execute_with_retry
from backend.db.threads import (
    init_db,
    get_next_thread_id,
    save_thread,
    get_all_threads,
    update_thread_time,
    rename_thread,
    remove_thread,
)

__all__ = [
    # connection helpers
    "get_db_path",
    "open_connection",
    "execute_with_retry",
    # thread operations
    "init_db",
    "get_next_thread_id",
    "save_thread",
    "get_all_threads",
    "update_thread_time",
    "rename_thread",
    "remove_thread",
]

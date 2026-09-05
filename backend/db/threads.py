"""
Thread CRUD operations for the ChatBot database.

All functions use execute_with_retry() from connection.py so transient
SQLite lock errors are handled transparently.

IMPORTANT: remove_thread() also deletes from LangGraph's internal tables
(checkpoints, writes, etc.). If LangGraph changes its schema in a future
version, those DELETEs may silently no-op — monitor release notes when
upgrading langgraph.
"""

# Standard library
import logging
import sqlite3
import traceback
import uuid

from backend.db.connection import get_db_path, open_connection, execute_with_retry

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database schema.

    Idempotent — safe to call every time the app starts.
    Creates the `threads` table if it doesn't already exist.
    """
    try:
        db_path = get_db_path()
        conn = open_connection(db_path)
        conn.commit()
        conn.close()
        logger.info("Database initialized at: %s", db_path)
    except Exception:
        logger.error("init_db failed:\n%s", traceback.format_exc())
        raise


def get_next_thread_id() -> str:
    """
    Return the next sequential thread ID (e.g., 'thread4').

    Scans existing IDs matching 'thread<N>' and returns the next unused
    one. Falls back to a UUID if the DB is unavailable.

    Returns
    -------
    str
        A thread ID like 'thread5', or a UUID fallback on failure.
    """
    db_path = get_db_path()

    def _op(conn: sqlite3.Connection) -> str:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id FROM threads WHERE thread_id LIKE 'thread%'")
        max_num = 0
        for (tid,) in cursor.fetchall():
            try:
                num = int(tid.replace("thread", ""))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass  # Skip non-numeric suffixes (e.g., UUID fallbacks)
        return f"thread{max_num + 1}"

    try:
        return execute_with_retry(db_path, _op)
    except Exception:
        logger.error("get_next_thread_id failed — using UUID fallback:\n%s", traceback.format_exc())
        return str(uuid.uuid4())


def save_thread(thread_id: str, thread_name: str) -> None:
    """
    Persist a new thread record. Idempotent (INSERT OR IGNORE).

    Parameters
    ----------
    thread_id : str
        Unique identifier for the thread.
    thread_name : str
        User-visible display name shown in the sidebar.
    """
    db_path = get_db_path()

    def _op(conn: sqlite3.Connection) -> None:
        conn.execute(
            "INSERT OR IGNORE INTO threads (thread_id, thread_name) VALUES (?, ?)",
            (thread_id, thread_name),
        )
        conn.commit()

    try:
        execute_with_retry(db_path, _op)
    except Exception:
        logger.error("save_thread failed for '%s':\n%s", thread_id, traceback.format_exc())


def get_all_threads() -> list[dict]:
    """
    Retrieve all threads ordered by last activity (most recent first).

    Returns
    -------
    list of dict
        Each dict has 'thread_id' and 'thread_name' keys.
        Returns [] on any failure.
    """
    db_path = get_db_path()

    def _op(conn: sqlite3.Connection) -> list[dict]:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id, thread_name FROM threads ORDER BY updated_at DESC")
        return [{"thread_id": r[0], "thread_name": r[1]} for r in cursor.fetchall()]

    try:
        return execute_with_retry(db_path, _op)
    except Exception:
        logger.error("get_all_threads failed:\n%s", traceback.format_exc())
        return []


def update_thread_time(thread_id: str) -> None:
    """
    Update the 'updated_at' timestamp so this thread rises to the top of the sidebar.

    Parameters
    ----------
    thread_id : str
        The thread to touch.
    """
    db_path = get_db_path()

    def _op(conn: sqlite3.Connection) -> None:
        conn.execute(
            "UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
            (thread_id,),
        )
        conn.commit()

    try:
        execute_with_retry(db_path, _op)
    except Exception:
        logger.error("update_thread_time failed for '%s':\n%s", thread_id, traceback.format_exc())


def rename_thread(thread_id: str, new_name: str) -> bool:
    """
    Rename a thread in the database.

    Parameters
    ----------
    thread_id : str
        The thread to rename.
    new_name : str
        The new display name (whitespace is stripped).

    Returns
    -------
    bool
        True on success, False on any failure.
    """
    db_path = get_db_path()

    def _op(conn: sqlite3.Connection) -> bool:
        conn.execute(
            "UPDATE threads SET thread_name = ? WHERE thread_id = ?",
            (new_name.strip(), thread_id),
        )
        conn.commit()
        return True

    try:
        return execute_with_retry(db_path, _op)
    except Exception:
        logger.error("rename_thread failed for '%s':\n%s", thread_id, traceback.format_exc())
        return False


def remove_thread(thread_id: str) -> None:
    """
    Delete a thread and its LangGraph checkpoints from the database.

    Parameters
    ----------
    thread_id : str
        The thread to delete.
    """
    db_path = get_db_path()

    def _op(conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM threads WHERE thread_id = ?", (thread_id,))

        # Remove LangGraph checkpoint data for this thread.
        # Tables are internal to SqliteSaver — handle schema changes gracefully.
        for table in ("checkpoints", "writes", "checkpoint_blobs", "checkpoint_migrations"):
            try:
                conn.execute(f"DELETE FROM {table} WHERE thread_id = ?", (thread_id,))  # noqa: S608
            except sqlite3.OperationalError:
                pass  # Table doesn't exist in this LangGraph version — safe to skip

        conn.commit()

    try:
        execute_with_retry(db_path, _op)
    except Exception:
        logger.error("remove_thread failed for '%s':\n%s", thread_id, traceback.format_exc())

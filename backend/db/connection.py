"""
SQLite connection helpers and retry logic for the db package.

All public DB functions in threads.py use _execute_with_retry() so
transient WAL lock contention is handled transparently.
"""

# Standard library
import logging
import sqlite3
import time
import traceback
from typing import Any, Callable

from backend.config import load_config

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """
    Resolve the database file path from config.json.

    Returns
    -------
    str
        Path to the SQLite database file (absolute or relative to CWD).
    """
    return load_config().get("database_path", "chatbot.db")


def open_connection(db_path: str) -> sqlite3.Connection:
    """
    Open a WAL-mode SQLite connection and ensure the threads table exists.

    WAL (Write-Ahead Logging) allows one writer and many concurrent readers,
    which is essential when LangGraph's SqliteSaver is holding its own
    long-lived connection to the same file.

    check_same_thread=False is required because Streamlit may invoke DB
    calls from different threads during reruns.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.

    Returns
    -------
    sqlite3.Connection
        A ready-to-use database connection.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id   TEXT PRIMARY KEY,
            thread_name TEXT,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


def execute_with_retry(
    db_path: str,
    operation: Callable[[sqlite3.Connection], Any],
    max_retries: int = 3,
    base_delay: float = 0.1,
) -> Any:
    """
    Execute a database operation with exponential-backoff retry on lock errors.

    SQLite in WAL mode can briefly lock when LangGraph's writer commits a
    checkpoint at the same moment as a thread metadata update. Retrying with
    a small delay resolves this transient contention without surfacing errors
    to the user.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    operation : callable
        A function that accepts a sqlite3.Connection and performs the work.
        It should commit within itself where needed.
    max_retries : int
        Maximum number of retry attempts after the initial failure (default: 3).
    base_delay : float
        Base delay in seconds before the first retry; doubles each attempt (default: 0.1).

    Returns
    -------
    Any
        The return value of operation(conn).

    Raises
    ------
    sqlite3.OperationalError
        Re-raised after all retries are exhausted.
    """
    for attempt in range(max_retries + 1):
        conn = None
        try:
            conn = open_connection(db_path)
            return operation(conn)
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "DB locked (attempt %d/%d) — retrying in %.2fs", attempt + 1, max_retries, delay
                )
                time.sleep(delay)
            else:
                raise
        finally:
            if conn:
                conn.close()

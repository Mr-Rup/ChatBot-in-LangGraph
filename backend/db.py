"""
Database management operations for the ChatBot.
"""

# Standard library
import sqlite3
import traceback
import uuid

# ============================================================
# Connection Management
# ============================================================

def get_db_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database and initialize tables.

    Returns
    -------
    sqlite3.Connection
        The configured SQLite database connection.
    """
    try:
        conn = sqlite3.connect('chatbot.db', check_same_thread=False, timeout=10.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                thread_name TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        return conn
    except Exception as e:
        print(f"[ERROR in backend/db.py -> get_db_connection] Failed to connect/init DB:\n{traceback.format_exc()}")
        raise e

# ============================================================
# Thread Operations
# ============================================================

def get_next_thread_id() -> str:
    """
    Retrieve the next available sequential thread ID.

    Returns
    -------
    str
        The next sequential thread ID (e.g., 'thread1', 'thread2') or a UUID on failure.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id FROM threads WHERE thread_id LIKE 'thread%'")
        rows = cursor.fetchall()
        max_num = 0
        for r in rows:
            try:
                num = int(r[0].replace('thread', ''))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
        return f"thread{max_num + 1}"
    except Exception as e:
        print(f"[ERROR in backend/db.py -> get_next_thread_id] Failed to get next thread ID:\n{traceback.format_exc()}")
        return str(uuid.uuid4())
    finally:
        conn.close()

def save_thread(thread_id: str, thread_name: str) -> None:
    """
    Save a new thread to the database.

    Parameters
    ----------
    thread_id : str
        The unique identifier for the thread.
    thread_name : str
        The user-friendly name of the thread.
    """
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR IGNORE INTO threads (thread_id, thread_name) VALUES (?, ?)', (thread_id, thread_name))
        conn.commit()
    except Exception as e:
        print(f"[ERROR in backend/db.py -> save_thread] Failed to save thread:\n{traceback.format_exc()}")
    finally:
        conn.close()

def get_all_threads() -> list[dict]:
    """
    Retrieve all chat threads ordered by their last updated time.

    Returns
    -------
    list of dict
        A list of dictionaries containing 'thread_id' and 'thread_name'.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Order by updated_at descending so the most recently active chats appear first
        cursor.execute('SELECT thread_id, thread_name FROM threads ORDER BY updated_at DESC')
        rows = cursor.fetchall()
        return [{'thread_id': r[0], 'thread_name': r[1]} for r in rows]
    except Exception as e:
        print(f"[ERROR in backend/db.py -> retrieve_all_threads] Failed to retrieve threads:\n{traceback.format_exc()}")
        return []
    finally:
        conn.close()

def update_thread_time(thread_id: str) -> None:
    """
    Update the 'updated_at' timestamp for a specific thread to the current time.

    Parameters
    ----------
    thread_id : str
        The unique identifier for the thread to update.
    """
    conn = get_db_connection()
    try:
        conn.execute("UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?", (thread_id,))
        conn.commit()
    except Exception as e:
        print(f"[ERROR in backend/db.py -> update_thread_time] Error updating thread time:\n{traceback.format_exc()}")
    finally:
        conn.close()

def remove_thread(thread_id: str) -> None:
    """
    Remove a thread and all associated checkpoints from the database.

    Parameters
    ----------
    thread_id : str
        The unique identifier for the thread to remove.
    """
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM threads WHERE thread_id = ?', (thread_id,))
        # Also clean up langgraph checkpoints to free space
        conn.execute('DELETE FROM checkpoints WHERE thread_id = ?', (thread_id,))
        conn.execute('DELETE FROM writes WHERE thread_id = ?', (thread_id,))
        conn.commit()
    except Exception as e:
        print(f"[ERROR in backend/db.py -> remove_thread] Error removing thread from database:\n{traceback.format_exc()}")
    finally:
        conn.close()

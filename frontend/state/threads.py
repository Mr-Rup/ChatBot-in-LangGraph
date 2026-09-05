"""
Thread ID generation and sidebar CRUD — session state + database.
"""

# Standard library
import logging
import traceback
import uuid

# Third-party
import streamlit as st

# Local
from backend.constants import (
    SESSION_THREAD_ID,
    SESSION_THREAD_NAME,
    SESSION_CHAT_THREADS,
    SESSION_MSG_HISTORY,
    DEFAULT_THREAD_NAME,
    DEFAULT_CHAT_NAME,
)

logger = logging.getLogger(__name__)


def generate_thread_id() -> str:
    """
    Generate a new sequential thread ID from the database.

    Falls back to a UUID if the database is unavailable.

    Returns
    -------
    str
        A thread ID like 'thread5', or a UUID string as a fallback.
    """
    try:
        from backend.db import get_next_thread_id
        return get_next_thread_id()
    except Exception:
        logger.error("generate_thread_id failed — using UUID:\n%s", traceback.format_exc())
        return str(uuid.uuid4())


def add_thread(thread_id: str, thread_name: str) -> None:
    """
    Add a new thread to session state and persist it to the database.

    Idempotent: if the thread already exists in session state it won't be
    added again; INSERT OR IGNORE handles the DB side.

    Parameters
    ----------
    thread_id : str
        Unique ID for the thread.
    thread_name : str
        Display name shown in the sidebar.
    """
    try:
        from backend.db import save_thread

        if SESSION_CHAT_THREADS not in st.session_state:
            st.session_state[SESSION_CHAT_THREADS] = []

        already_exists = any(
            t["thread_id"] == thread_id
            for t in st.session_state[SESSION_CHAT_THREADS]
        )
        if not already_exists:
            st.session_state[SESSION_CHAT_THREADS].insert(
                0, {"thread_id": thread_id, "thread_name": thread_name}
            )
            save_thread(thread_id, thread_name)
    except Exception:
        logger.error("add_thread failed for '%s':\n%s", thread_id, traceback.format_exc())


def delete_thread(thread_id: str) -> None:
    """
    Delete a thread from the database and session state.

    If the deleted thread is currently active, a new empty thread is
    created automatically.

    Parameters
    ----------
    thread_id : str
        The ID of the thread to delete.
    """
    try:
        from backend.db import remove_thread
        remove_thread(thread_id)

        st.session_state[SESSION_CHAT_THREADS] = [
            t for t in st.session_state[SESSION_CHAT_THREADS]
            if t["thread_id"] != thread_id
        ]

        # If the active thread was deleted, reset to a fresh conversation
        if st.session_state.get(SESSION_THREAD_ID) == thread_id:
            st.session_state[SESSION_THREAD_ID] = generate_thread_id()
            st.session_state[SESSION_THREAD_NAME] = DEFAULT_THREAD_NAME
            st.session_state[SESSION_MSG_HISTORY] = []
    except Exception:
        logger.error("delete_thread failed for '%s':\n%s", thread_id, traceback.format_exc())


def rename_thread_in_state(thread_id: str, new_name: str) -> bool:
    """
    Rename a thread in the database and update session state immediately.

    Parameters
    ----------
    thread_id : str
        The ID of the thread to rename.
    new_name : str
        The new display name.

    Returns
    -------
    bool
        True if the database rename succeeded, False otherwise.
    """
    try:
        from backend.db import rename_thread
        success = rename_thread(thread_id, new_name)

        if success:
            # Update sidebar list in-place
            for t in st.session_state.get(SESSION_CHAT_THREADS, []):
                if t["thread_id"] == thread_id:
                    t["thread_name"] = new_name
                    break
            # Also update thread_name if this is the active thread
            if st.session_state.get(SESSION_THREAD_ID) == thread_id:
                st.session_state[SESSION_THREAD_NAME] = new_name

        return success
    except Exception:
        logger.error("rename_thread_in_state failed for '%s':\n%s", thread_id, traceback.format_exc())
        return False

"""
Streamlit session state initialization.

init_session_state() is called once per app run (in app.py).
All session keys are seeded here with safe defaults so every other module
can assume they exist without null-checking.
"""

# Standard library
import logging
import traceback

# Third-party
import streamlit as st

# Local
from backend.constants import (
    SESSION_MSG_HISTORY,
    SESSION_THREAD_ID,
    SESSION_THREAD_NAME,
    SESSION_CHAT_THREADS,
    SESSION_TEMPERATURE,
    DEFAULT_THREAD_NAME,
)
from frontend.state.threads import generate_thread_id

logger = logging.getLogger(__name__)


def init_session_state() -> None:
    """
    Initialize all required Streamlit session state variables.

    Guards with 'not in' checks so existing values are never overwritten
    during normal Streamlit reruns — only missing keys are seeded.
    """
    # Active message history for the current thread
    if SESSION_MSG_HISTORY not in st.session_state:
        st.session_state[SESSION_MSG_HISTORY] = []

    # Active thread identity — generate a fresh ID for the very first session
    if SESSION_THREAD_ID not in st.session_state or SESSION_THREAD_NAME not in st.session_state:
        st.session_state[SESSION_THREAD_ID] = generate_thread_id()
        st.session_state[SESSION_THREAD_NAME] = DEFAULT_THREAD_NAME

    # Conversation list — loaded from DB once; cached in session state after that
    if SESSION_CHAT_THREADS not in st.session_state:
        try:
            from backend.db import get_all_threads
            st.session_state[SESSION_CHAT_THREADS] = get_all_threads()
        except Exception:
            logger.error("init_session_state: failed to load threads:\n%s", traceback.format_exc())
            st.session_state[SESSION_CHAT_THREADS] = []

    # Temperature slider default — seeded from the active model's config
    if SESSION_TEMPERATURE not in st.session_state:
        try:
            from backend.bot import get_model_config
            cfg = get_model_config()
            st.session_state[SESSION_TEMPERATURE] = float(cfg.get("model_temperature", 0.1))
        except Exception:
            st.session_state[SESSION_TEMPERATURE] = 0.1

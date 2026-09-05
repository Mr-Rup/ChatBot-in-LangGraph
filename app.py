"""
Main application entry point for the Streamlit ChatBot.

Startup sequence
----------------
1. Configure the Python logging system (precise format with file + line info).
2. Initialize the SQLite database schema (idempotent).
3. Initialize Streamlit session state variables.
4. Render sidebar and chat UI components.

Run with:
    streamlit run app.py
"""

# Standard library
import logging
import traceback

# Third-party
import streamlit as st

# ── Logging must be configured before any local module is imported ──
# This ensures every logger created by sub-modules uses the correct format.
from backend.logger import setup_logging
setup_logging(
    level=logging.INFO,
    # Uncomment the line below to also write logs to a rotating file:
    # log_file="logs/chatbot.log",
)

# Local (imported after logging is configured)
from frontend.state import init_session_state
from frontend.ui import render_sidebar, render_chat

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Initialize the application and render the Streamlit UI.
    """
    try:
        # Initialize the DB schema once at startup (CREATE TABLE IF NOT EXISTS)
        from backend.db import init_db
        init_db()

        # Initialize session state (safe on every rerun — guards prevent overwrites)
        init_session_state()

        # Render the two top-level UI components
        render_sidebar()
        render_chat()

    except Exception:
        logger.critical("Application crashed:\n%s", traceback.format_exc())
        st.error(
            "A critical error occurred. Please check the terminal / console for details."
        )


if __name__ == "__main__":
    main()

"""
Modal dialogs for the ChatBot UI.

Dialogs are decorated with @st.dialog so Streamlit renders them as
modal overlays. They interact with session state directly and call
st.rerun() on successful submission.
"""

# Standard library
import logging

# Third-party
import streamlit as st
import streamlit.components.v1 as components

# Local
from frontend.state import generate_thread_id, rename_thread_in_state
from backend.constants import (
    SESSION_THREAD_ID,
    SESSION_THREAD_NAME,
    SESSION_MSG_HISTORY,
    DEFAULT_CHAT_NAME,
)

logger = logging.getLogger(__name__)


@st.dialog("Create New Chat")
def create_new_chat_dialog() -> None:
    """
    Modal dialog for naming and creating a new chat thread.

    On submission the active thread is replaced with a fresh one and the
    message history is cleared. The JavaScript snippet auto-focuses and
    selects the name input so the user can type immediately without clicking.
    """
    with st.form(key="new_chat_dialog_form"):
        new_chat_name = st.text_input("Chat Name", value=DEFAULT_CHAT_NAME)

        # Auto-focus + select-all on the text input inside the dialog.
        # Uses window.parent to reach the Streamlit iframe's parent document.
        components.html(
            """
            <script>
            setTimeout(function() {
                var dialog = window.parent.document.querySelector('[role="dialog"]');
                if (dialog) {
                    var input = dialog.querySelector('input');
                    if (input) { input.focus(); input.select(); }
                }
            }, 100);
            </script>
            """,
            height=0,
            width=0,
        )

        if st.form_submit_button("Create"):
            st.session_state[SESSION_THREAD_ID] = generate_thread_id()
            st.session_state[SESSION_THREAD_NAME] = new_chat_name.strip() or DEFAULT_CHAT_NAME
            st.session_state[SESSION_MSG_HISTORY] = []
            st.rerun()


@st.dialog("Rename Conversation")
def rename_thread_dialog(thread_id: str, current_name: str) -> None:
    """
    Modal dialog for renaming an existing chat thread.

    Parameters
    ----------
    thread_id : str
        The ID of the thread to rename.
    current_name : str
        The current name, pre-filled in the input field.
    """
    with st.form(key=f"rename_form_{thread_id}"):
        new_name = st.text_input("New conversation name", value=current_name)
        if st.form_submit_button("Save"):
            new_name = new_name.strip()
            if new_name and new_name != current_name:
                rename_thread_in_state(thread_id, new_name)
            st.rerun()

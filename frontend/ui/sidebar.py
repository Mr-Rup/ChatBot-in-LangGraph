"""
Sidebar UI component.

Renders the left panel with:
1. Header + New Chat button
2. Active model display with specs expander
3. Temperature (creativity) slider
4. Conversation list with switch / rename / delete controls
"""

# Standard library
import logging

# Third-party
import streamlit as st

# Local
from frontend.state import load_conversation, delete_thread
from frontend.ui.dialogs import create_new_chat_dialog, rename_thread_dialog
from backend.constants import (
    SESSION_THREAD_ID,
    SESSION_THREAD_NAME,
    SESSION_CHAT_THREADS,
    SESSION_MSG_HISTORY,
    SESSION_TEMPERATURE,
)

logger = logging.getLogger(__name__)


def render_sidebar() -> None:
    """
    Render the left sidebar with model info, settings, and conversation list.
    """
    from backend.bot import get_model_config
    model_cfg = get_model_config()

    # ── Section 1: Header ──
    st.sidebar.title("My ChatBot")
    st.sidebar.markdown("A chatbot built with **Streamlit** and **LangGraph**.")

    if st.sidebar.button("➕ New Chat"):
        create_new_chat_dialog()

    # ── Section 2: Active Model Info ──
    st.sidebar.header("Active Model")
    model_display_name = model_cfg.get("name", model_cfg.get("model_name", "Unknown"))
    st.sidebar.caption(f"🤖 **{model_display_name}**")

    specs = model_cfg.get("specs", {})
    if specs:
        with st.sidebar.expander("Model Specifications", expanded=False):
            st.write(f"**Parameters:** {specs.get('parameters', 'N/A')}")
            st.write(f"**VRAM Required:** {specs.get('vram_required', 'N/A')}")
            st.write(f"**RAM Required:** {specs.get('ram_required', 'N/A')}")
            st.write(f"**Tool Support:** {specs.get('tool_support', 'N/A')}")
            if model_cfg.get("description"):
                st.info(model_cfg["description"])

    # ── Section 3: Temperature Slider ──
    # Value is stored in session state so render_chat() can read it
    # without receiving it as a function argument.
    st.sidebar.header("Settings")
    st.session_state[SESSION_TEMPERATURE] = st.sidebar.slider(
        "Creativity (Temperature)",
        min_value=0.01,
        max_value=1.0,
        value=float(st.session_state.get(SESSION_TEMPERATURE, model_cfg.get("model_temperature", 0.1))),
        step=0.01,
        help="Higher values make responses more creative. Lower values improve tool-use reliability.",
    )

    # ── Section 4: Conversation List ──
    st.sidebar.header("Conversations")

    for thread in st.session_state[SESSION_CHAT_THREADS]:
        tid = thread["thread_id"]
        tname = thread["thread_name"]

        # Three columns: [thread name] [✏️ rename] [🗑️ delete]
        col_name, col_rename, col_delete = st.sidebar.columns([4, 1, 1])

        if col_name.button(tname, key=f"switch_{tid}"):
            st.session_state[SESSION_THREAD_ID] = tid
            st.session_state[SESSION_THREAD_NAME] = tname
            st.session_state[SESSION_MSG_HISTORY] = load_conversation(tid)
            st.rerun()

        if col_rename.button("✏️", key=f"rename_{tid}", help="Rename this conversation"):
            rename_thread_dialog(tid, tname)

        if col_delete.button("🗑️", key=f"del_{tid}", help="Delete this conversation"):
            delete_thread(tid)
            st.rerun()

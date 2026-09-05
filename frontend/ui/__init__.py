"""
frontend.ui — Streamlit UI components package.

Public API (identical to the old flat frontend/ui.py):

    from frontend.ui import render_sidebar, render_chat

Internal sub-modules
--------------------
dialogs   — create_new_chat_dialog(), rename_thread_dialog()
sidebar   — render_sidebar()
chat      — render_chat()
"""

from frontend.ui.sidebar import render_sidebar
from frontend.ui.chat import render_chat

__all__ = [
    "render_sidebar",
    "render_chat",
]

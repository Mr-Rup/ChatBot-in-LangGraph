"""
frontend.state — session state and thread management package.

Public API (identical to the old flat frontend/state.py):

    from frontend.state import (
        init_session_state,
        generate_thread_id, add_thread, delete_thread, rename_thread_in_state,
        load_conversation,
    )

Internal sub-modules
--------------------
threads      — generate_thread_id(), add_thread(), delete_thread(), rename_thread_in_state()
conversation — load_conversation()
session      — init_session_state()
"""

from frontend.state.threads import (
    generate_thread_id,
    add_thread,
    delete_thread,
    rename_thread_in_state,
)
from frontend.state.conversation import load_conversation
from frontend.state.session import init_session_state

__all__ = [
    "generate_thread_id",
    "add_thread",
    "delete_thread",
    "rename_thread_in_state",
    "load_conversation",
    "init_session_state",
]

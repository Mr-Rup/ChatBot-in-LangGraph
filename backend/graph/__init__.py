"""
backend.graph — LangGraph assembly package.

Public API (identical to the old flat backend/graph.py):

    from backend.graph import create_chatbot, ChatState
    from backend.graph import parse_tool_call_from_text   # if needed directly

Internal sub-modules
--------------------
state    — ChatState TypedDict
parser   — parse_tool_call_from_text()
builder  — create_chatbot()
"""

from backend.graph.state import ChatState
from backend.graph.parser import parse_tool_call_from_text
from backend.graph.builder import create_chatbot

__all__ = [
    "ChatState",
    "parse_tool_call_from_text",
    "create_chatbot",
]

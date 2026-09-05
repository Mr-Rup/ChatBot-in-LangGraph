"""
Project-wide constants to avoid magic strings scattered across files.

Add new constants here rather than using raw string literals in code.
"""

# ============================================================
# Streamlit Session State Keys
# ============================================================

# The active chat thread ID (e.g., 'thread1')
SESSION_THREAD_ID = "thread_id"

# The human-readable name of the active thread
SESSION_THREAD_NAME = "thread_name"

# In-memory list of all chat threads: [{'thread_id': ..., 'thread_name': ...}]
SESSION_CHAT_THREADS = "chat_threads"

# The rendered message history for the current thread
SESSION_MSG_HISTORY = "msg_history"

# The current temperature slider value (0.01 – 1.0)
SESSION_TEMPERATURE = "temperature"

# ============================================================
# Message Role Labels (used in msg_history dicts)
# ============================================================

ROLE_USER = "user"
ROLE_AI = "ai"
ROLE_TOOL_CALL = "tool_call"   # UI-only role for displaying tool-use events

# ============================================================
# Thread Naming
# ============================================================

DEFAULT_THREAD_NAME = "New Conversation"
DEFAULT_CHAT_NAME = "New chat"

# ============================================================
# LangGraph Message Types
# ============================================================

MSG_TYPE_HUMAN = "human"
MSG_TYPE_AI = "ai"
MSG_TYPE_AI_CHUNK = "AIMessageChunk"
MSG_TYPE_TOOL = "tool"

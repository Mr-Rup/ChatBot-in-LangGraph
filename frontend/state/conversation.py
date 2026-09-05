"""
Conversation loading from LangGraph's checkpoint store.

Translates raw LangGraph message objects into simple role/content dicts
that the Streamlit UI can render without knowing about LangGraph internals.
"""

# Standard library
import logging
import traceback

# Local
from backend.constants import (
    ROLE_USER,
    ROLE_AI,
    ROLE_TOOL_CALL,
    MSG_TYPE_HUMAN,
    MSG_TYPE_AI,
    MSG_TYPE_AI_CHUNK,
    MSG_TYPE_TOOL,
)

logger = logging.getLogger(__name__)


def load_conversation(thread_id: str) -> list[dict]:
    """
    Load the conversation history for a thread from LangGraph memory.

    Tool messages are hidden from the output — the LLM's follow-up text
    provides the user-facing summary. Tool *call* events (where the LLM
    decided to use a tool) are shown as ROLE_TOOL_CALL indicator rows.

    Parameters
    ----------
    thread_id : str
        The ID of the thread to load.

    Returns
    -------
    list of dict
        Each dict has 'role' (ROLE_USER / ROLE_AI / ROLE_TOOL_CALL)
        and 'content' keys. Returns [] on any failure.
    """
    try:
        from backend.bot import get_chatbot
        chatbot = get_chatbot()

        if chatbot is None:
            logger.warning("load_conversation: chatbot is None — returning empty history.")
            return []

        state = chatbot.get_state({"configurable": {"thread_id": thread_id}})

        if not (hasattr(state, "values") and "messages" in state.values):
            return []

        history: list[dict] = []

        for msg in state.values["messages"]:
            if msg.type == MSG_TYPE_HUMAN:
                history.append({"role": ROLE_USER, "content": msg.content})

            elif msg.type in (MSG_TYPE_AI, MSG_TYPE_AI_CHUNK):
                # Show a tool-use indicator row for each tool the LLM called
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        history.append({
                            "role": ROLE_TOOL_CALL,
                            "content": f"🛠️ Using tool: **{tc['name']}**...",
                        })
                # Append the LLM's text response (if any)
                if msg.content:
                    content_str = msg.content if isinstance(msg.content, str) else str(msg.content)
                    history.append({"role": ROLE_AI, "content": content_str})

            elif msg.type == MSG_TYPE_TOOL:
                pass  # Hidden — the LLM's next message provides the user-facing answer

        return history

    except Exception:
        logger.error(
            "load_conversation failed for thread '%s':\n%s",
            thread_id, traceback.format_exc(),
        )
        return []

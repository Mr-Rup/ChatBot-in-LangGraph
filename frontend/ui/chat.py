"""
Chat area UI component.

Renders the main chat interface:
- Displays the existing conversation history from session state
- Accepts new user input via st.chat_input
- Streams the AI response token-by-token
- Shows tool-use indicators inline during streaming
- Reloads conversation from LangGraph memory after each turn
"""

# Standard library
import logging
import traceback

# Third-party
import streamlit as st
from langchain_core.messages import HumanMessage

# Local
from frontend.state import add_thread, load_conversation
from backend.constants import (
    SESSION_THREAD_ID,
    SESSION_THREAD_NAME,
    SESSION_CHAT_THREADS,
    SESSION_MSG_HISTORY,
    SESSION_TEMPERATURE,
    ROLE_USER,
    ROLE_AI,
    ROLE_TOOL_CALL,
    DEFAULT_THREAD_NAME,
    DEFAULT_CHAT_NAME,
    MSG_TYPE_AI,
    MSG_TYPE_AI_CHUNK,
)

logger = logging.getLogger(__name__)


def render_chat() -> None:
    """
    Render the main chat area: history display, input, and AI response streaming.

    Flow per user message
    ---------------------
    1. Display existing history from session state.
    2. Accept user input; append to history and show immediately.
    3. Save thread to DB on first message (or update its timestamp after that).
    4. Auto-name the thread from the first 60 chars of the user's message.
    5. Apply the current temperature from the slider to the model.
    6. Stream the AI response; show tool-use indicators as they appear.
    7. Reload full conversation from LangGraph memory, then rerun.
    """
    from backend.bot import get_chatbot, get_base_model, get_model_config

    chatbot = get_chatbot()
    base_model = get_base_model()
    model_cfg = get_model_config()

    # ── Display existing history ──
    for msg in st.session_state[SESSION_MSG_HISTORY]:
        if msg["role"] == ROLE_TOOL_CALL:
            st.info(msg["content"])
        else:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Chat input ──
    user_input = st.chat_input("Type your message here")
    if not user_input:
        return  # Nothing entered — exit early, avoid triggering any state changes

    is_first_msg = len(st.session_state[SESSION_MSG_HISTORY]) == 0

    # Append to session history for optimistic rendering
    st.session_state[SESSION_MSG_HISTORY].append({"role": ROLE_USER, "content": user_input})

    # ── Persist thread metadata ──
    if is_first_msg:
        # Auto-name: use the first 60 chars of the first message if still at default name
        current_name = st.session_state[SESSION_THREAD_NAME]
        if current_name in (DEFAULT_THREAD_NAME, DEFAULT_CHAT_NAME):
            st.session_state[SESSION_THREAD_NAME] = user_input[:60].strip()
        add_thread(st.session_state[SESSION_THREAD_ID], st.session_state[SESSION_THREAD_NAME])
    else:
        # Update timestamp so this thread rises to the top of the sidebar list
        from backend.db import update_thread_time
        update_thread_time(st.session_state[SESSION_THREAD_ID])

    # Keep active thread at position 0 in the sidebar list for instant UI feedback
    active_tid = st.session_state[SESSION_THREAD_ID]
    active_tname = st.session_state[SESSION_THREAD_NAME]
    st.session_state[SESSION_CHAT_THREADS] = [
        t for t in st.session_state[SESSION_CHAT_THREADS] if t["thread_id"] != active_tid
    ]
    st.session_state[SESSION_CHAT_THREADS].insert(0, {"thread_id": active_tid, "thread_name": active_tname})

    # ── Show user message ──
    with st.chat_message(ROLE_USER):
        st.markdown(user_input)

    # ── Stream AI response ──
    with st.chat_message(ROLE_AI):
        if chatbot is None:
            st.error("⚠️ Chatbot failed to initialize. Please check the logs.")
            return

        # Apply temperature from the sidebar slider to the underlying model.
        # Best-effort: log but don't block the response if it fails.
        temperature = st.session_state.get(SESSION_TEMPERATURE, 0.1)
        if base_model is not None:
            try:
                if model_cfg.get("model_type") == "local":
                    base_model.llm.pipeline.model.generation_config.temperature = temperature
                else:
                    base_model.llm.temperature = temperature
            except Exception:
                logger.debug("Temperature update skipped: %s", traceback.format_exc())

        placeholder = st.empty()
        full_response = ""

        try:
            with st.spinner("Thinking..."):
                for msg, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"thread_id": st.session_state[SESSION_THREAD_ID]}},
                    stream_mode="messages",
                ):
                    # Show tool-use indicators as the LLM decides to call a tool
                    if msg.type in (MSG_TYPE_AI, MSG_TYPE_AI_CHUNK):
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                st.info(f"🛠️ Using tool: **{tc['name']}**...")
                        # Accumulate and stream text tokens progressively
                        if msg.content and isinstance(msg.content, str):
                            full_response += msg.content
                            placeholder.markdown(full_response + "▌")
                    # tool messages are hidden; LLM's follow-up provides the answer

            placeholder.markdown(full_response)

        except Exception:
            logger.error("chatbot.stream failed:\n%s", traceback.format_exc())
            st.error("An error occurred while generating the response. Please try again.")

    # ── Reload from LangGraph memory ──
    # Captures any messages added by the tool node that weren't visible during streaming.
    st.session_state[SESSION_MSG_HISTORY] = load_conversation(st.session_state[SESSION_THREAD_ID])
    st.rerun()

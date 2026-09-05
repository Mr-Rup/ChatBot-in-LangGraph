"""
LangGraph chatbot builder.

Graph topology
--------------
    START → chat_node ──(tools_condition)──► tools → chat_node → ...
                      ↓
                    END

- chat_node : calls the LLM; injects a system prompt on the first turn;
              runs the fallback tool-call parser for models that emit
              tool calls as raw JSON.
- tools     : LangGraph's built-in ToolNode that routes to the correct tool
              and appends the ToolMessage result to the conversation.
"""

# Standard library
import logging
import sqlite3
import traceback
from typing import Any

# Third-party
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

# Local
from backend.tools import available_tools
from backend.config import load_config
from backend.graph.state import ChatState
from backend.graph.parser import parse_tool_call_from_text

logger = logging.getLogger(__name__)


def create_chatbot(model: Any) -> Any:
    """
    Assemble and compile the LangGraph chatbot.

    The graph persists conversation state to SQLite via SqliteSaver.
    Each invocation is associated with a thread_id (in the config dict)
    so separate conversations are stored independently.

    Parameters
    ----------
    model : Any
        Initialized language model (ChatHuggingFace or compatible).
        Must support .bind_tools() and .invoke().

    Returns
    -------
    CompiledStateGraph
        The compiled, executable chatbot graph.

    Raises
    ------
    Exception
        Re-raised from graph compilation so the caller (bot.py) can
        handle it (e.g., show an error in the UI).
    """
    try:
        config = load_config()
        db_path = config.get("database_path", "chatbot.db")

        # ── SQLite checkpointer ──
        # check_same_thread=False: Streamlit may invoke the graph from different
        # threads across reruns. WAL mode allows concurrent reads and writes.
        # This connection is kept open for the graph's lifetime.
        db_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        db_conn.execute("PRAGMA journal_mode=WAL;")
        checkpointer = SqliteSaver(conn=db_conn)

        # ── Tool setup ──
        tools = available_tools()
        tool_node = ToolNode(tools)
        registered_tool_names: set[str] = {t.name for t in tools}

        # ── System prompt — built once when the graph is compiled ──
        # Pre-computing here (outside chat_node) avoids rebuilding on every call.
        base_prompt = config.get(
            "system_prompt",
            (
                "You are a highly capable AI assistant with access to external tools. "
                "You MUST use these tools when asked to perform math, search, or look up information. "
                "Do NOT refuse to use tools. Do NOT perform calculations yourself. "
                "Always output the correct JSON format to invoke the tool when needed."
            ),
        )
        tool_descs = "\n".join(
            f"Tool Name: {t.name}\nDescription: {t.description}\nArguments: {t.args}\n"
            for t in tools
        )
        full_system_prompt = (
            f"{base_prompt}\n\n"
            f"You have access to the following tools:\n{tool_descs}\n\n"
            "To use a tool, output ONLY a valid JSON object in this format:\n"
            '{"name": "tool_name", "arguments": {"arg_name": "arg_value"}}\n\n'
            "Once you receive the tool's result, respond to the user naturally. Do NOT output JSON in your final answer."
        )

        # ── Graph node: chat_node ──
        def chat_node(state: ChatState) -> dict:
            """
            Process the conversation state through the LLM.

            Steps
            -----
            1. Prepend the system prompt on the first turn (when no SystemMessage exists).
            2. Invoke the LLM with tools bound.
            3. If the response has no native tool_calls but contains raw JSON,
               extract the tool call via parse_tool_call_from_text().
            4. Return the updated messages list.
            """
            try:
                messages = state["messages"]

                # Step 1: inject system prompt on first turn only
                if not any(msg.type == "system" for msg in messages):
                    messages = [SystemMessage(content=full_system_prompt)] + messages

                # Step 2: call the LLM
                llm_with_tools = model.bind_tools(tools)
                response = llm_with_tools.invoke(messages)

                # Step 3: fallback tool-call extraction for models that output raw JSON
                if not getattr(response, "tool_calls", None) and response.content:
                    parsed_call = parse_tool_call_from_text(
                        str(response.content), registered_tool_names
                    )
                    if parsed_call:
                        response.tool_calls = [parsed_call]
                        # Clear raw JSON so users don't see the internal call format
                        response.content = ""

                # Step 4: return updated state
                return {"messages": [response]}

            except Exception:
                logger.error("chat_node failed:\n%s", traceback.format_exc())
                raise

        # ── Assemble the graph ──
        graph = StateGraph(ChatState)
        graph.add_node("chat_node", chat_node)
        graph.add_node("tools", tool_node)

        # START always enters chat_node.
        # After chat_node: tools_condition routes to 'tools' if a tool was called, else END.
        # After 'tools': loop back to chat_node so the LLM can process the tool result.
        graph.add_edge(START, "chat_node")
        graph.add_conditional_edges("chat_node", tools_condition)
        graph.add_edge("tools", "chat_node")

        chatbot = graph.compile(checkpointer=checkpointer)
        logger.info("Chatbot graph compiled successfully.")
        return chatbot

    except Exception:
        logger.error("create_chatbot failed:\n%s", traceback.format_exc())
        raise

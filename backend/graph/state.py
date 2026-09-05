"""
LangGraph state definition for the ChatBot.

ChatState is the single mutable object passed between every node in the graph.
"""

# Standard library
from typing import Annotated

# Third-party
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import TypedDict


class ChatState(TypedDict):
    """
    TypedDict representing the conversation graph's mutable state.

    Attributes
    ----------
    messages : list of BaseMessage
        The full conversation history. The add_messages reducer *appends*
        new messages rather than replacing the list, which enables LangGraph's
        built-in message accumulation across turns.
    """
    messages: Annotated[list[BaseMessage], add_messages]

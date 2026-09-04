"""
LangGraph conversation state and graph assembly for the ChatBot.
"""

# Standard library
import sqlite3
import traceback
from typing import TypedDict, Annotated, Any

# Third-party
try:
   from langchain_core.messages import BaseMessage
   from langgraph.graph import StateGraph, START
   from langgraph.graph.message import add_messages
   from langgraph.prebuilt import ToolNode, tools_condition
   from langgraph.checkpoint.sqlite import SqliteSaver
except Exception as e:
   print(f"[ERROR in backend/graph.py -> Imports] Failed to import third-party modules:\n{traceback.format_exc() if 'traceback' in globals() else e}")
   raise ImportError(f"Failed to import necessary modules in graph.py: {e}")

# Local
try:
   from backend.tools import available_tools
except Exception as e:
   print(f"[ERROR in backend/graph.py -> Imports] Failed to import local modules:\n{traceback.format_exc() if 'traceback' in globals() else e}")
   raise ImportError(f"Failed to import necessary modules in graph.py: {e}")

# ============================================================
# State Definition
# ============================================================

class ChatState(TypedDict):
   """
   TypedDict representing the state of the conversation graph.
   Maintains the message history.
   """
   messages: Annotated[list[BaseMessage], add_messages]

# ============================================================
# Graph Construction
# ============================================================

def create_chatbot(model: Any) -> Any:
   """
   Assemble and compile the LangGraph for the chatbot.

   Parameters
   ----------
   model : Any
       The initialized language model to bind to the graph.

   Returns
   -------
   CompiledStateGraph
       The compiled executable graph representing the chatbot.
   """
   try:
      # create sqlite connection
      connect = sqlite3.connect('chatbot.db', check_same_thread=False, timeout=10.0)
      connect.execute('PRAGMA journal_mode=WAL;')
      # create checkpointer for memory using sqlite
      check_pointer = SqliteSaver(conn=connect)

      # create graph instance
      graph = StateGraph(ChatState)

      tools = available_tools()

      # Create chat node function
      def chat_node(state: ChatState) -> dict:
         """
         Process the current state through the language model and return the AI's response.
         """
         try:
            messages = state['messages']
            
            # Force Qwen to use tools by injecting a strong system prompt
            if not any(msg.type == 'system' for msg in messages):
               from langchain_core.messages import SystemMessage
               sys_prompt = (
                  "You are a highly capable AI assistant with access to external tools. "
                  "You MUST use these tools when asked to perform math, search, or look up information. "
                  "Do NOT refuse to use tools. Do NOT perform calculations yourself. "
                  "Always output the correct JSON format to invoke the tool when needed."
               )
               messages = [SystemMessage(content=sys_prompt)] + messages

            llm_with_tools = model.bind_tools(tools)
            response = llm_with_tools.invoke(messages)
            return {'messages': [response]}
         except Exception as e:
            print(f"[ERROR in backend/graph.py -> chat_node] Failed to execute chat node:\n{traceback.format_exc()}")
            raise e

      # add nodes to the graph 
      graph.add_node('chat_node', chat_node)
      graph.add_node('tools', ToolNode(tools))

      # add edges to the graph
      graph.add_edge(START, 'chat_node')
      graph.add_conditional_edges('chat_node', tools_condition)
      graph.add_edge('tools', 'chat_node')

      chatbot = graph.compile(checkpointer = check_pointer)
      return chatbot
   except Exception as e:
      print(f"[ERROR in backend/graph.py -> create_chatbot] Failed to create chatbot graph:\n{traceback.format_exc()}")
      raise e
try:
   from langgraph.graph import StateGraph, START, END
   from typing import TypedDict, Annotated
   from langchain_core.messages import BaseMessage
   from langgraph.graph.message import add_messages
   from langgraph.checkpoint.sqlite import SqliteSaver
   import sqlite3
except Exception as e:
   raise ImportError(f"Failed to import necessary modules in graph.py: {e}")

# -------------------------------------------------------------------
# create chatstate
# -------------------------------------------------------------------

class ChatState(TypedDict):
   messages: Annotated[list[BaseMessage], add_messages]

def create_chatbot(model):
   # create sqlite connection
   import sqlite3
   connect = sqlite3.connect('chatbot.db', check_same_thread=False, timeout=10.0)
   connect.execute('PRAGMA journal_mode=WAL;')
   # create checkpointer for memory using sqlite
   check_pointer = SqliteSaver(conn=connect)

   # Create chat node function
   def chat_node(state: ChatState):
      messages = state['messages']
      response = model.invoke(messages)
      return {'messages': [response]}

   # create graph instance
   graph = StateGraph(ChatState)
   # add nodes to the graph 
   graph.add_node('chat_node', chat_node)
   # add edges to the graph
   graph.add_edge(START, 'chat_node')
   graph.add_edge('chat_node', END)

   chatbot = graph.compile(checkpointer = check_pointer)
   return chatbot
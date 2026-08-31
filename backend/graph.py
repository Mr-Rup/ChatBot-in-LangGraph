try:
   from langgraph.graph import StateGraph, START, END
   from typing import TypedDict, Annotated
   from langchain_core.messages import BaseMessage
   from langgraph.graph.message import add_messages
   from langgraph.checkpoint.memory import InMemorySaver
except Exception as e:
   raise ImportError(f"Failed to import necessary modules in graph.py: {e}")

# -------------------------------------------------------------------
# create chatstate
# -------------------------------------------------------------------

class ChatState(TypedDict):
   messages: Annotated[list[BaseMessage], add_messages]

def create_chatbot(model):
   # create checkpointer for memory
   check_pointer = InMemorySaver()

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

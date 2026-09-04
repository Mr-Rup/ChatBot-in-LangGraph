"""
Streamlit session state and thread management.
"""

# Standard library
import traceback
import uuid

# Third-party
import streamlit as st

# Local
from backend.bot import chatbot

# -------------------------------------------------------------------
# Utility functions for managing session state and chat threads
# ============================================================
# Thread Management
# ============================================================

def generate_thread_id() -> str:
   """
   Generate a new thread ID.

   Returns
   -------
   str
       The newly generated thread ID.
   """
   try:
      from backend.db import get_next_thread_id
      return get_next_thread_id()
   except Exception as e:
      print(f"[ERROR in frontend/state.py -> generate_thread_id]:\n{traceback.format_exc()}")
      return str(uuid.uuid4())

def add_thread(thread_id: str, thread_name: str) -> None:
   """
   Add a new thread to the UI session state and save it to the database.

   Parameters
   ----------
   thread_id : str
       The unique ID of the thread.
   thread_name : str
       The display name of the thread.
   """
   try:
      from backend.db import save_thread
      
      if 'chat_threads' not in st.session_state:
         st.session_state['chat_threads'] = []
      if not any(t['thread_id'] == thread_id for t in st.session_state['chat_threads']):
         st.session_state['chat_threads'].insert(0, {'thread_id': thread_id, 'thread_name': thread_name})
         save_thread(thread_id, thread_name)
   except Exception as e:
      print(f"[ERROR in frontend/state.py -> add_thread]:\n{traceback.format_exc()}")

def load_conversation(thread_id: str) -> list[dict]:
   """
   Load conversation history for a given thread from LangGraph memory.

   Parameters
   ----------
   thread_id : str
       The ID of the thread to load.

   Returns
   -------
   list of dict
       The mapped message history for the UI.
   """
   try:
      from backend.bot import chatbot
      config = {'configurable': {'thread_id': thread_id}}
      state = chatbot.get_state(config)
      
      if hasattr(state, 'values') and 'messages' in state.values:
         messages = state.values['messages']
         history = []
         for msg in messages:
            if msg.type == 'human':
               history.append({'role': 'user', 'content': msg.content})
            elif msg.type in ['ai', 'AIMessageChunk']:
               if hasattr(msg, 'tool_calls') and msg.tool_calls:
                  for tc in msg.tool_calls:
                     history.append({'role': 'tool_call', 'content': f"🛠️ Using tool: {tc['name']}..."})
               if msg.content:
                  if isinstance(msg.content, str):
                     history.append({'role': 'ai', 'content': msg.content})
                  else:
                     history.append({'role': 'ai', 'content': str(msg.content)})
            elif msg.type == 'tool':
               history.append({'role': 'tool_result', 'content': f"✔️ Tool '{msg.name}' returned: {msg.content}"})
         return history
      return []
   except Exception as e:
      print(f"[ERROR in frontend/state.py -> load_conversation] Failed to load conversation from memory:\n{traceback.format_exc()}")
      return []

# ============================================================
# Session Initialization and Cleanup
# ============================================================

def init_session_state() -> None:
   """
   Initialize necessary variables in Streamlit session state.
   """
   # -------------------------------------------------------------------
   # create a session state to store message history if not previously available
   # -------------------------------------------------------------------
   if 'msg_history' not in st.session_state:
      st.session_state['msg_history'] = []

   if 'thread_id' not in st.session_state or 'thread_name' not in st.session_state:
      st.session_state['thread_id'] = generate_thread_id()
      st.session_state['thread_name'] = "Default Conversation"

   try:
      if 'chat_threads' not in st.session_state:
         from backend.db import get_all_threads
         st.session_state['chat_threads'] = get_all_threads()
   except Exception as e:
      print(f"[ERROR in frontend/state.py -> init_session_state]:\n{traceback.format_exc()}")
      st.session_state['chat_threads'] = []

def delete_thread(thread_id: str) -> None:
   """
   Delete a thread from the database and the active session state.

   Parameters
   ----------
   thread_id : str
       The ID of the thread to delete.
   """
   try:
      from backend.db import remove_thread
      remove_thread(thread_id)
      st.session_state['chat_threads'] = [t for t in st.session_state['chat_threads'] if t['thread_id'] != thread_id]
      
      if st.session_state.get('thread_id') == thread_id:
         st.session_state['thread_id'] = generate_thread_id()
         st.session_state['thread_name'] = "New Conversation"
         st.session_state['msg_history'] = []
   except Exception as e:
      print(f"[ERROR in frontend/state.py -> delete_thread]:\n{traceback.format_exc()}")

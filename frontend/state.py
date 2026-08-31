import streamlit as st
import uuid
from backend.bot import chatbot

# -------------------------------------------------------------------
# Utility functions for managing session state and chat threads
# -------------------------------------------------------------------
def generate_thread_id():
   from backend.db import get_next_thread_id
   return get_next_thread_id()

def add_thread(thread_id, thread_name):
   from backend.db import save_thread
   
   if 'chat_threads' not in st.session_state:
      st.session_state['chat_threads'] = []
   if not any(t['thread_id'] == thread_id for t in st.session_state['chat_threads']):
      st.session_state['chat_threads'].insert(0, {'thread_id': thread_id, 'thread_name': thread_name})
      save_thread(thread_id, thread_name)

def load_conversation(thread_id):
   if chatbot is None:
      return []
   try:
      config = {'configurable': {'thread_id': thread_id}}
      state = chatbot.get_state(config)
      if hasattr(state, 'values') and 'messages' in state.values:
         messages = state.values['messages']
         history = []
         for msg in messages:
            if msg.type == 'human':
               history.append({'role': 'user', 'content': msg.content})
            elif msg.type in ['ai', 'AIMessageChunk']:
               history.append({'role': 'ai', 'content': msg.content})
         return history
      return []
   except Exception as e:
      print(f"Error loading conversation: {e}")
      return []

def init_session_state():
   # -------------------------------------------------------------------
   # create a session state to store message history if not previously available
   # -------------------------------------------------------------------
   if 'msg_history' not in st.session_state:
      st.session_state['msg_history'] = []

   if 'thread_id' not in st.session_state or 'thread_name' not in st.session_state:
      st.session_state['thread_id'] = generate_thread_id()
      st.session_state['thread_name'] = "Default Conversation"

   if 'chat_threads' not in st.session_state:
      from backend.db import retrieve_all_threads
      st.session_state['chat_threads'] = retrieve_all_threads()

def delete_thread(thread_id):
   from backend.db import remove_thread
   remove_thread(thread_id)
   st.session_state['chat_threads'] = [t for t in st.session_state['chat_threads'] if t['thread_id'] != thread_id]
   
   if st.session_state.get('thread_id') == thread_id:
      st.session_state['thread_id'] = generate_thread_id()
      st.session_state['thread_name'] = "New Conversation"
      st.session_state['msg_history'] = []

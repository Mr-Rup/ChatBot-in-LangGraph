"""
Streamlit user interface components for the ChatBot.
"""

# Standard library
import traceback

# Third-party
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage

# Local
try:
   from backend.bot import chatbot, base_model, DEFAULT_MODEL_CONFIG
   from frontend.state import generate_thread_id, add_thread, load_conversation
except Exception as e:
   print(f"[ERROR in frontend/ui.py -> Imports]:\n{traceback.format_exc()}")

# ============================================================
# Dialogs
# ============================================================

@st.dialog("Create New Chat")
def create_new_chat_dialog() -> None:
   """
   Render a dialog for creating a new chat thread.
   It sets up a new thread ID and clears the active message history.
   """
   with st.form(key='new_chat_dialog_form'):
      new_chat_name = st.text_input("Chat Name", value="New chat")
      
      # Inject JavaScript to auto-focus the input and select the text
      components.html(
         """
         <script>
         setTimeout(function() {
            var dialog = window.parent.document.querySelector('[role="dialog"]');
            if (dialog) {
               var input = dialog.querySelector('input');
               if (input) {
                  input.focus();
                  input.select();
               }
            }
         }, 100);
         </script>
         """,
         height=0,
         width=0
      )

      submit_button = st.form_submit_button("Create")
      if submit_button:
         st.session_state['thread_id'] = generate_thread_id()
         st.session_state['thread_name'] = new_chat_name
         st.session_state['msg_history'] = []
         st.rerun()

# ============================================================
# Sidebar Interface
# ============================================================

def render_sidebar() -> None:
   """
   Render the left sidebar containing chat history and model settings.
   """
   # -------------------------------------------------------------------
   # sidebar ui
   # -------------------------------------------------------------------
   st.sidebar.title('My ChatBot')
   st.sidebar.markdown('This is a simple chatbot application built using Streamlit and LangGraph.')

   if st.sidebar.button("New Chat"):
      create_new_chat_dialog()

   st.sidebar.header('Active Model')
   model_display_name = DEFAULT_MODEL_CONFIG.get('name', DEFAULT_MODEL_CONFIG.get('model_name', 'Unknown'))
   st.sidebar.caption(f"🤖 **{model_display_name}**")
   
   specs = DEFAULT_MODEL_CONFIG.get('specs', {})
   if specs:
      with st.sidebar.expander("Model Specifications", expanded=False):
         st.write(f"**Parameters:** {specs.get('parameters', 'N/A')}")
         st.write(f"**VRAM Required:** {specs.get('vram_required', 'N/A')}")
         st.write(f"**RAM Required:** {specs.get('ram_required', 'N/A')}")
         st.write(f"**Tool Support:** {specs.get('tool_support', 'N/A')}")
         if DEFAULT_MODEL_CONFIG.get('description'):
            st.info(DEFAULT_MODEL_CONFIG['description'])

   st.sidebar.header('Settings')
   temperature = st.sidebar.slider("Creativity (Temperature)", min_value=0.01, max_value=1.0, value=float(DEFAULT_MODEL_CONFIG.get('model_temperature', 0.1)), step=0.01, help="Higher values make output more creative. Lower values are better for tool reliability.")

   st.sidebar.header('Conversations')

   for thread in st.session_state['chat_threads']:
      col1, col2 = st.sidebar.columns([4, 1])
      if col1.button(thread['thread_name'], key=thread['thread_id']):
         st.session_state['thread_id'] = thread['thread_id']
         st.session_state['thread_name'] = thread['thread_name']
         st.session_state['msg_history'] = load_conversation(thread['thread_id'])
         st.rerun()
      if col2.button("🗑️", key=f"del_{thread['thread_id']}"):
         from frontend.state import delete_thread
         delete_thread(thread['thread_id'])
         st.rerun()

# ============================================================
# Chat Interface
# ============================================================

def render_chat() -> None:
   """
   Render the main chat interface, displaying conversation history 
   and processing new user inputs.
   """
   # -------------------------------------------------------------------
   # loading conversaton history from session_state
   # -------------------------------------------------------------------
   for msg in st.session_state['msg_history']:
      if msg['role'] == 'tool_call':
         st.info(msg['content'])
      elif msg['role'] == 'tool_result':
         st.success(msg['content'])
      else:
         with st.chat_message(msg['role']):
            st.markdown(msg['content'])

   # -------------------------------------------------------------------
   # take user queries and get ai response from chatbot in streaming mode
   # -------------------------------------------------------------------
   user_input = st.chat_input('Type your message here')
   if user_input:
      is_first_msg = len(st.session_state['msg_history']) == 0
      
      # add the user message to the message history
      st.session_state['msg_history'].append({'role': 'user', 'content': user_input})
      
      if is_first_msg:
         from frontend.state import add_thread
         add_thread(st.session_state['thread_id'], st.session_state['thread_name'])
      else:
         # Update thread timestamp in db for existing threads
         from backend.db import update_thread_time
         update_thread_time(st.session_state['thread_id'])
      
      # Move this thread to the top of the session state list so UI updates instantly
      st.session_state['chat_threads'] = [t for t in st.session_state['chat_threads'] if t['thread_id'] != st.session_state['thread_id']]
      st.session_state['chat_threads'].insert(0, {'thread_id': st.session_state['thread_id'], 'thread_name': st.session_state['thread_name']})
         
      # display the input message in the chat window
      with st.chat_message('user'):
         st.markdown(user_input)

      # get ai response from chatbot in streaming mode
      with st.chat_message('ai'):
         if chatbot is None:
            st.error("Chatbot failed to initialize. Please check the backend logs.")
         else:
            with st.spinner('Thinking...'):
               # Dynamically update the temperature of the underlying model
               if base_model:
                  if DEFAULT_MODEL_CONFIG['model_type'] == 'local':
                     try:
                        base_model.llm.pipeline.model.generation_config.temperature = temperature
                     except Exception as e:
                        pass
                  else:
                     try:
                        base_model.llm.temperature = temperature
                     except Exception as e:
                        pass

               placeholder = st.empty()
               full_response = ""
               
               try:
                  for msg, metadata in chatbot.stream(
                     {'messages': [HumanMessage(content= user_input)]},
                     config = {'configurable': {'thread_id': st.session_state['thread_id']}},
                     stream_mode = 'messages'
                  ):
                     if msg.type in ['ai', 'AIMessageChunk']:
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                           for tool_call in msg.tool_calls:
                              st.info(f"🛠️ Using tool: {tool_call['name']}...")
                        if msg.content:
                           if isinstance(msg.content, str):
                              full_response += msg.content
                              placeholder.markdown(full_response + "▌")
                     elif msg.type == 'tool':
                        st.success(f"✔️ Tool '{msg.name}' returned: {msg.content}")

                  placeholder.markdown(full_response)
               except Exception as e:
                  print(f"[ERROR in frontend/ui.py -> chatbot.stream] LLM Streaming failed:\n{traceback.format_exc()}")
                  st.error(f"An error occurred while generating the response: {e}")
                  
      # Refresh message history directly from LangGraph to get everything (including tools)
      st.session_state['msg_history'] = load_conversation(st.session_state['thread_id'])
      st.rerun()

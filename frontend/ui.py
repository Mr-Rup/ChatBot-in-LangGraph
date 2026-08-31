import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage
from backend.bot import chatbot
from frontend.state import generate_thread_id, add_thread, load_conversation

@st.dialog("Create New Chat")
def create_new_chat_dialog():
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
         add_thread(st.session_state['thread_id'], st.session_state['thread_name'])
         st.rerun()

def render_sidebar():
   # -------------------------------------------------------------------
   # sidebar ui
   # -------------------------------------------------------------------
   st.sidebar.title('My ChatBot')
   st.sidebar.markdown('This is a simple chatbot application built using Streamlit and LangGraph.')

   if st.sidebar.button("New Chat"):
      create_new_chat_dialog()

   st.sidebar.header('Conversations')

   for thread in st.session_state['chat_threads']:
      if st.sidebar.button(thread['thread_name'], key=thread['thread_id']):
         st.session_state['thread_id'] = thread['thread_id']
         st.session_state['thread_name'] = thread['thread_name']
         st.session_state['msg_history'] = load_conversation(thread['thread_id'])
         st.rerun()

def render_chat():
   # -------------------------------------------------------------------
   # loading conversaton history from session_state
   # -------------------------------------------------------------------
   for msg in st.session_state['msg_history']:
      with st.chat_message(msg['role']):
         st.markdown(msg['content'])

   # -------------------------------------------------------------------
   # take user queries and get ai response from chatbot in streaming mode
   # -------------------------------------------------------------------
   user_input = st.chat_input('Type your message here')
   if user_input:
      # add the user message to the message history
      st.session_state['msg_history'].append({'role': 'user', 'content': user_input})
      # display the input message in the chat window
      with st.chat_message('user'):
         st.markdown(user_input)

      # get ai response from chatbot in streaming mode
      with st.chat_message('ai'):
         if chatbot is None:
            st.error("Chatbot failed to initialize. Please check the backend logs.")
            ai_msg = "Error: Chatbot not available."
         else:
            with st.spinner('Thinking...'):
               ai_msg = st.write_stream(
                  message_chunk.content for message_chunk, metadata in chatbot.stream(
                     {'messages': [HumanMessage(content= user_input)]},
                     config = {'configurable': {'thread_id': st.session_state['thread_id']}},
                     stream_mode = 'messages'
                  ) if message_chunk.type in ['ai', 'AIMessageChunk']
               )

      # add the ai message to the message history
      st.session_state['msg_history'].append({'role': 'ai', 'content': ai_msg})

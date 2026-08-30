try:
   import streamlit as st
   from Backend import chatbot
   from langchain_core.messages import HumanMessage
except Exception as e:
   raise ImportError(f"Import failed in frontend_streaming.py \n {e}")

# create a session state to store message history if not previously available
if 'msg_history' not in st.session_state:
   st.session_state['msg_history'] = []

# loading conversaton history from session_state
for msg in st.session_state['msg_history']:
   with st.chat_message(msg['role']):
      st.markdown(msg['content'])

user_input = st.chat_input('Type your message here')
if user_input:
   # add the user message to the message history
   st.session_state['msg_history'].append({'role': 'user', 'content': user_input})
   # display the input message in the chat window
   with st.chat_message('user'):
      st.markdown(user_input)

   # get ai response from chatbot in streaming mode
   with st.chat_message('ai'):
      with st.spinner('Thinking...'):
         ai_msg = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
               {'messages': [HumanMessage(content= user_input)]},
               config = {'configurable': {'thread_id': 'user-1'}},
               stream_mode = 'messages'
            )
         )

   # add the ai message to the message history
   st.session_state['msg_history'].append({'role': 'ai', 'content': ai_msg})
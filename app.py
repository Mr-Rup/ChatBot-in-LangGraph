try:
   import streamlit as st
   from frontend.state import init_session_state
   from frontend.ui import render_sidebar, render_chat
except Exception as e:
   raise ImportError(f"Import failed in app.py \n {e}")

# Initialize session state and threads
init_session_state()

# Render UI components
render_sidebar()
render_chat()

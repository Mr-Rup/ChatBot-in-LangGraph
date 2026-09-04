"""
Main application entry point for the Streamlit Chatbot.

Initializes the session state and renders the Streamlit UI components.
"""

# Standard library
import traceback

# Third-party
try:
   import streamlit as st
except Exception as e:
   print(f"[ERROR in app.py -> Imports] Failed to import third-party modules:\n{traceback.format_exc()}")
   raise ImportError(f"Import failed in app.py \n {e}")

# Local
try:
   from frontend.state import init_session_state
   from frontend.ui import render_sidebar, render_chat
except Exception as e:
   print(f"[ERROR in app.py -> Imports] Failed to import local modules:\n{traceback.format_exc()}")
   raise ImportError(f"Import failed in app.py \n {e}")


def main() -> None:
   """
   Initialize session state and render the main Streamlit UI components.
   """
   try:
      # Initialize session state and threads
      init_session_state()

      # Render UI components
      render_sidebar()
      render_chat()
   except Exception as e:
      print(f"[ERROR in app.py -> Main Execution] Application crashed:\n{traceback.format_exc()}")
      if 'st' in globals():
         st.error("A critical error occurred while running the application. Check the console for details.")

if __name__ == "__main__":
   main()

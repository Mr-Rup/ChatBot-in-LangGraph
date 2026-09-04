"""
ChatBot class definition and default initialization.
"""

# Standard library
import traceback
from typing import Literal

# Local
try:
   from backend.model import create_hf_model
   from backend.graph import create_chatbot
except Exception as e:
   print(f"[ERROR in backend/bot.py -> Imports] Failed to import:\n{traceback.format_exc()}")
   raise ImportError(f"Failed to import necessary modules in bot.py: {e}")

# ============================================================
# ChatBot Class Definition
# ============================================================

class ChatBot:
   """
   Wrapper class to manage the initialization of the language model and conversation graph.
   """
   
   def __init__(self, model_type: Literal['api','local'], model_name: str, model_task: str, model_temperature: float, model_max_new_tokens: int) -> None:
      """
      Initialize the ChatBot.

      Parameters
      ----------
      model_type : Literal['api', 'local']
          Whether to use a local or API-based HuggingFace model.
      model_name : str
          The HuggingFace repository ID of the model.
      model_task : str
          The task type (e.g., 'text-generation').
      model_temperature : float
          The creativity parameter for generation.
      model_max_new_tokens : int
          The maximum number of tokens to generate.
      """
      self.model = create_hf_model(model_type, model_name, model_task, model_temperature, model_max_new_tokens)
      self.bot = create_chatbot(self.model)

# ============================================================
# Default Configuration & Initialization
# ============================================================

DEFAULT_MODEL_CONFIG = {
   'model_type': 'local',
   'model_name': 'Qwen/Qwen2.5-3B-Instruct',  # Great performance, fits comfortably in 6GB VRAM
   'model_task': 'text-generation',
   'model_temperature': 0.1,
   'model_max_new_tokens': 512
}

# Create default chatbot instance
try:
   chatbot_app = ChatBot(**DEFAULT_MODEL_CONFIG)
   chatbot = chatbot_app.bot
   base_model = chatbot_app.model
except Exception as e:
   print(f"[ERROR in backend/bot.py -> ChatBot Initialization] Failed to initialize ChatBot:\n{traceback.format_exc()}")
   chatbot = None
   base_model = None

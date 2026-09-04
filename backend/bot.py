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
   from backend.config import get_active_model_config
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
# Dynamic Configuration & ChatBot Initialization
# ============================================================

try:
   active_cfg = get_active_model_config()
   DEFAULT_MODEL_CONFIG = active_cfg
   chatbot_app = ChatBot(
      model_type=active_cfg['model_type'],
      model_name=active_cfg['model_name'],
      model_task=active_cfg['model_task'],
      model_temperature=active_cfg['model_temperature'],
      model_max_new_tokens=active_cfg['model_max_new_tokens']
   )
   chatbot = chatbot_app.bot
   base_model = chatbot_app.model
except Exception as e:
   print(f"[ERROR in backend/bot.py -> ChatBot Initialization] Failed to initialize ChatBot:\n{traceback.format_exc()}")
   chatbot = None
   base_model = None
   DEFAULT_MODEL_CONFIG = {
      'model_type': 'local',
      'model_name': 'Qwen/Qwen2.5-3B-Instruct',
      'model_task': 'text-generation',
      'model_temperature': 0.1,
      'model_max_new_tokens': 512
   }

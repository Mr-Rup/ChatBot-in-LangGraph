try:
   from typing import Literal
   from backend.model import create_hf_model
   from backend.graph import create_chatbot
except Exception as e:
   raise ImportError(f"Failed to import necessary modules in bot.py: {e}")

class ChatBot:
   def __init__(self, model_type: Literal['api','local'], model_name: str, model_task: str, model_temperature: float, model_max_new_tokens: int):
      self.model = create_hf_model(model_type, model_name, model_task, model_temperature, model_max_new_tokens)
      self.bot = create_chatbot(self.model)

# -------------------------------------------------------------------
# Default configuration for local Hugging Face model
# -------------------------------------------------------------------

DEFAULT_MODEL_CONFIG = {
   'model_type': 'local',
   'model_name': 'Qwen/Qwen2.5-3B-Instruct',  # Great performance, fits comfortably in 6GB VRAM
   'model_task': 'text-generation',
   'model_temperature': 0.7,
   'model_max_new_tokens': 512
}

# Create default chatbot instance
try:
   chatbot = ChatBot(**DEFAULT_MODEL_CONFIG).bot
except Exception as e:
   print(f"Error initializing default chatbot: {e}")
   chatbot = None

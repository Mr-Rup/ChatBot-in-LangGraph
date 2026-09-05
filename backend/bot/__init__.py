"""
backend.bot — chatbot lifecycle package.

Public API (identical to the old flat backend/bot.py):

    from backend.bot import get_chatbot, get_base_model, get_model_config

Internal sub-modules
--------------------
chatbot   — ChatBot class (pairs model + graph)
factory   — _build_chatbot(), get_chatbot(), get_base_model(), get_model_config()
"""

from backend.bot.chatbot import ChatBot
from backend.bot.factory import get_chatbot, get_base_model, get_model_config

__all__ = [
    "ChatBot",
    "get_chatbot",
    "get_base_model",
    "get_model_config",
]

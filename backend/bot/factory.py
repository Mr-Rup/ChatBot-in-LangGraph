"""
Lazy chatbot factory using Streamlit's cache.

@st.cache_resource keeps a single ChatBot instance alive across all reruns.
To force a reload (e.g., after a model switch), call st.cache_resource.clear().

Usage from any frontend module:
    from backend.bot import get_chatbot, get_base_model, get_model_config
"""

# Standard library
import logging
import traceback
from typing import Any

# Third-party
import streamlit as st

# Local
from backend.bot.chatbot import ChatBot
from backend.config import get_active_model_config

logger = logging.getLogger(__name__)


@st.cache_resource(show_spinner="Loading AI model...")
def _build_chatbot() -> tuple[Any, Any, dict]:
    """
    Build and cache the ChatBot instance.

    Wrapped with @st.cache_resource so Streamlit keeps one instance alive
    across all reruns. The cache can be cleared by calling
    st.cache_resource.clear() — useful for model hot-swapping.

    Returns
    -------
    tuple of (graph, model, config_dict)
        graph       : CompiledStateGraph or None
        model       : CustomChatHuggingFace or None
        config_dict : the active model config used to build this instance
    """
    try:
        cfg = get_active_model_config()
        instance = ChatBot(
            model_type=cfg["model_type"],
            model_name=cfg["model_name"],
            model_task=cfg["model_task"],
            model_temperature=cfg["model_temperature"],
            model_max_new_tokens=cfg["model_max_new_tokens"],
        )
        return instance.bot, instance.model, cfg
    except Exception:
        logger.error("_build_chatbot failed:\n%s", traceback.format_exc())
        # Return None so callers show an error instead of crashing
        return None, None, get_active_model_config()


def get_chatbot() -> Any:
    """
    Return the cached compiled chatbot graph (or None on failure).

    Returns
    -------
    CompiledStateGraph or None
    """
    bot, _, _ = _build_chatbot()
    return bot


def get_base_model() -> Any:
    """
    Return the cached base language model instance (or None on failure).

    Returns
    -------
    CustomChatHuggingFace or None
    """
    _, model, _ = _build_chatbot()
    return model


def get_model_config() -> dict:
    """
    Return the active model configuration dict used by the cached chatbot.

    Returns
    -------
    dict
        Keys: key, name, model_type, model_name, model_task,
              model_temperature, model_max_new_tokens, specs, description.
    """
    _, _, cfg = _build_chatbot()
    return cfg

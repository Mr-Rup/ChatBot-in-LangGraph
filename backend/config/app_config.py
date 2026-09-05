"""
App-wide configuration: loading, saving, and environment application.

Reads from / writes to config.json at the project root.
"""

# Standard library
import json
import logging
import os
import traceback
from typing import Any

from backend.config.defaults import CONFIG_FILE_PATH, DEFAULT_FALLBACK_CONFIG
from backend.config.validation import validate_config

logger = logging.getLogger(__name__)


def load_config() -> dict[str, Any]:
    """
    Load project-wide settings from config.json.

    Returns
    -------
    dict
        The validated config, or built-in defaults if the file is missing
        or corrupted.
    """
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return validate_config(raw)
        logger.warning("config.json not found at %s — using built-in defaults.", CONFIG_FILE_PATH)
        return DEFAULT_FALLBACK_CONFIG.copy()
    except Exception:
        logger.error("Failed to load config.json:\n%s", traceback.format_exc())
        return DEFAULT_FALLBACK_CONFIG.copy()


def save_config(config_data: dict[str, Any]) -> bool:
    """
    Persist the given configuration dict to config.json.

    Parameters
    ----------
    config_data : dict
        The configuration to serialize.

    Returns
    -------
    bool
        True on success, False on any write error.
    """
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception:
        logger.error("Failed to save config.json:\n%s", traceback.format_exc())
        return False


def apply_environment_settings() -> None:
    """
    Push HF cache directory and LangSmith settings from config.json into os.environ.

    Must be called before any HuggingFace or LangSmith imports so the
    environment variables are set during their initialization.
    """
    try:
        config = load_config()

        # --- HuggingFace cache directory ---
        # Skip if already set externally, or if llm_cache_dir is None
        # (None means: let HF use its own platform default).
        cache_dir = config.get("llm_cache_dir") or config.get("hf_home")
        if cache_dir and not os.environ.get("HF_HOME"):
            os.environ["HF_HOME"] = cache_dir
            logger.info("HF_HOME set to: %s", cache_dir)

        # --- LangSmith tracing ---
        langsmith = config.get("langsmith", {})
        if langsmith.get("tracing", False):
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if langsmith.get("project"):
                os.environ["LANGCHAIN_PROJECT"] = langsmith["project"]
            if langsmith.get("endpoint"):
                os.environ["LANGCHAIN_ENDPOINT"] = langsmith["endpoint"]
            logger.info("LangSmith tracing enabled — project: %s", langsmith.get("project"))
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"

    except Exception:
        logger.error("apply_environment_settings failed:\n%s", traceback.format_exc())

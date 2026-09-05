"""
Model catalog management: loading, saving, querying, and switching models.

Reads from / writes to backend/models.json.
"""

# Standard library
import json
import logging
import os
import traceback
from typing import Any

from backend.config.defaults import MODELS_FILE_PATH, DEFAULT_FALLBACK_MODELS
from backend.config.validation import validate_model_entry
from backend.config.app_config import load_config, save_config

logger = logging.getLogger(__name__)


def load_models() -> dict[str, Any]:
    """
    Load the AI model catalog from backend/models.json.

    Returns
    -------
    dict
        A dict mapping model IDs to their specification blocks.
        Falls back to built-in defaults if the file is missing or corrupted.
    """
    try:
        if os.path.exists(MODELS_FILE_PATH):
            with open(MODELS_FILE_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Validate every entry; bad values are clamped with warnings
            return {key: validate_model_entry(key, entry) for key, entry in raw.items()}
        logger.warning("models.json not found at %s — using built-in defaults.", MODELS_FILE_PATH)
        return DEFAULT_FALLBACK_MODELS.copy()
    except Exception:
        logger.error("Failed to load models.json:\n%s", traceback.format_exc())
        return DEFAULT_FALLBACK_MODELS.copy()


def save_models(models_data: dict[str, Any]) -> bool:
    """
    Persist the model catalog to backend/models.json.

    Parameters
    ----------
    models_data : dict
        The models dictionary to serialize.

    Returns
    -------
    bool
        True on success, False on any write error.
    """
    try:
        with open(MODELS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(models_data, f, indent=2)
        return True
    except Exception:
        logger.error("Failed to save models.json:\n%s", traceback.format_exc())
        return False


def get_available_models() -> dict[str, Any]:
    """Return all models from models.json, keyed by model ID."""
    return load_models()


def get_active_model_config() -> dict[str, Any]:
    """
    Resolve and return the configuration for the currently active model.

    Reads the active_model key from config.json, looks it up in models.json,
    and returns a normalized dict with all runtime parameters. Falls back
    gracefully at each level if something is missing.

    Returns
    -------
    dict
        Normalized model config with keys: key, name, model_type, model_name,
        model_task, model_temperature, model_max_new_tokens, specs, description.
    """
    try:
        config = load_config()
        models = load_models()
        active_key = config.get("active_model", "qwen-2.5-3b")

        if active_key in models:
            m = models[active_key]
        else:
            # Configured key not in catalog — fall back to first available model
            first_key = next(iter(models), None)
            if first_key:
                logger.warning(
                    "Active model '%s' not in models.json — falling back to '%s'.",
                    active_key, first_key,
                )
                active_key, m = first_key, models[first_key]
            else:
                # Catalog is completely empty — use built-in default
                logger.warning("models.json is empty — using built-in default model.")
                active_key = "qwen-2.5-3b"
                m = DEFAULT_FALLBACK_MODELS["qwen-2.5-3b"]

        return {
            "key": active_key,
            "name": m.get("name", "Unknown Model"),
            "model_type": m.get("model_type", "local"),
            "model_name": m.get("repo_id", "Qwen/Qwen2.5-3B-Instruct"),
            "model_task": m.get("task", "text-generation"),
            "model_temperature": float(m.get("temperature", 0.1)),
            "model_max_new_tokens": int(m.get("max_new_tokens", 512)),
            "specs": m.get("specs", {}),
            "description": m.get("description", ""),
        }
    except Exception:
        logger.error("get_active_model_config failed:\n%s", traceback.format_exc())
        fb = DEFAULT_FALLBACK_MODELS["qwen-2.5-3b"]
        return {
            "key": "qwen-2.5-3b",
            "name": fb["name"],
            "model_type": fb["model_type"],
            "model_name": fb["repo_id"],
            "model_task": fb["task"],
            "model_temperature": fb["temperature"],
            "model_max_new_tokens": fb["max_new_tokens"],
            "specs": fb["specs"],
            "description": fb["description"],
        }


def set_active_model(model_key: str) -> bool:
    """
    Update the active_model key in config.json.

    Parameters
    ----------
    model_key : str
        The model ID to activate (must exist in models.json).

    Returns
    -------
    bool
        True if saved successfully, False otherwise.
    """
    try:
        if model_key not in load_models():
            logger.warning("set_active_model: key '%s' not found in models.json.", model_key)
            return False
        config = load_config()
        config["active_model"] = model_key
        return save_config(config)
    except Exception:
        logger.error("set_active_model failed:\n%s", traceback.format_exc())
        return False

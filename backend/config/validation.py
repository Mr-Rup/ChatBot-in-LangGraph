"""
Input validation helpers for config and model entries.

These functions sanitize values loaded from config.json and models.json,
correcting out-of-range values instead of crashing, while emitting log
warnings so the correction is always visible in the terminal output.
"""

# Standard library
import logging
from typing import Any

from backend.config.defaults import DEFAULT_FALLBACK_CONFIG

logger = logging.getLogger(__name__)


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and sanitize a loaded app configuration dictionary.

    Parameters
    ----------
    config : dict
        Raw configuration loaded from config.json.

    Returns
    -------
    dict
        The validated (and possibly corrected) configuration.
    """
    # active_model must be a non-empty string
    if not isinstance(config.get("active_model"), str) or not config["active_model"].strip():
        logger.warning(
            "config.json: 'active_model' is missing or blank — using fallback '%s'",
            DEFAULT_FALLBACK_CONFIG["active_model"],
        )
        config["active_model"] = DEFAULT_FALLBACK_CONFIG["active_model"]

    # database_path must be a non-empty string
    if not isinstance(config.get("database_path"), str) or not config["database_path"].strip():
        logger.warning(
            "config.json: 'database_path' is missing or blank — using fallback '%s'",
            DEFAULT_FALLBACK_CONFIG["database_path"],
        )
        config["database_path"] = DEFAULT_FALLBACK_CONFIG["database_path"]

    return config


def validate_model_entry(key: str, m: dict[str, Any]) -> dict[str, Any]:
    """
    Validate a single model entry from models.json.

    Parameters
    ----------
    key : str
        The model ID (used only for logging).
    m : dict
        The raw model entry to validate.

    Returns
    -------
    dict
        The validated (and possibly corrected) model entry.
    """
    # Temperature must be in the range (0, 1.0]
    temp = m.get("temperature", 0.1)
    if not isinstance(temp, (int, float)) or not (0 < temp <= 1.0):
        logger.warning(
            "models.json [%s]: 'temperature' %r out of range (0, 1] — clamping to 0.1", key, temp
        )
        m["temperature"] = 0.1

    # max_new_tokens must be a positive integer
    tokens = m.get("max_new_tokens", 512)
    if not isinstance(tokens, int) or tokens <= 0:
        logger.warning(
            "models.json [%s]: 'max_new_tokens' %r invalid — clamping to 512", key, tokens
        )
        m["max_new_tokens"] = 512

    # model_type must be 'api' or 'local'
    if m.get("model_type") not in ("api", "local"):
        logger.warning(
            "models.json [%s]: 'model_type' %r invalid — defaulting to 'local'",
            key, m.get("model_type"),
        )
        m["model_type"] = "local"

    return m

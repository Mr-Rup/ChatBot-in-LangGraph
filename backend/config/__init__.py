"""
backend.config — configuration management package.

Public API (identical to the old flat backend/config.py):

    from backend.config import (
        load_config, save_config, apply_environment_settings,
        load_models, save_models, get_available_models,
        get_active_model_config, set_active_model,
        prompt_model_selection,
    )

Internal sub-modules
--------------------
defaults        — file paths and fallback dicts
validation      — validate_config(), validate_model_entry()
app_config      — load_config(), save_config(), apply_environment_settings()
models_config   — load_models(), save_models(), get_active_model_config(), set_active_model()
cli             — prompt_model_selection() (used by run.bat)
"""

from backend.config.defaults import (
    ROOT_DIR,
    CONFIG_FILE_PATH,
    MODELS_FILE_PATH,
    DEFAULT_FALLBACK_CONFIG,
    DEFAULT_FALLBACK_MODELS,
)
from backend.config.validation import validate_config, validate_model_entry
from backend.config.app_config import load_config, save_config, apply_environment_settings
from backend.config.models_config import (
    load_models,
    save_models,
    get_available_models,
    get_active_model_config,
    set_active_model,
)
from backend.config.cli import prompt_model_selection

__all__ = [
    # paths & defaults
    "ROOT_DIR",
    "CONFIG_FILE_PATH",
    "MODELS_FILE_PATH",
    "DEFAULT_FALLBACK_CONFIG",
    "DEFAULT_FALLBACK_MODELS",
    # validation
    "validate_config",
    "validate_model_entry",
    # app config
    "load_config",
    "save_config",
    "apply_environment_settings",
    # models
    "load_models",
    "save_models",
    "get_available_models",
    "get_active_model_config",
    "set_active_model",
    # cli
    "prompt_model_selection",
]

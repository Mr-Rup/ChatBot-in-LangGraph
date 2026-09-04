"""
Configuration and model management services for the ChatBot.

Manages general runtime configurations via `config.json` and AI model
catalog specifications via `backend/models.json`.
"""

# Standard library
import json
import os
import traceback
from typing import Any

# ============================================================
# Paths & Default Fallbacks
# ============================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(ROOT_DIR, "config.json")
MODELS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.json")

DEFAULT_FALLBACK_CONFIG: dict[str, Any] = {
    "active_model": "qwen-2.5-3b",
    "llm_cache_dir": "S:/ollama_models",
    "database_path": "chatbot.db",
    "langsmith": {
        "tracing": False,
        "project": "ChatBot-LangGraph",
        "endpoint": "https://api.smith.langchain.com"
    },
    "system_prompt": (
        "You are a highly capable AI assistant with access to external tools. "
        "You MUST use these tools when asked to perform math, search, or look up information. "
        "Do NOT refuse to use tools. Do NOT perform calculations yourself. "
        "Always output the correct JSON format to invoke the tool when needed."
    )
}

DEFAULT_FALLBACK_MODELS: dict[str, Any] = {
    "qwen-2.5-3b": {
        "name": "Qwen 2.5 3B Instruct",
        "repo_id": "Qwen/Qwen2.5-3B-Instruct",
        "model_type": "local",
        "task": "text-generation",
        "temperature": 0.1,
        "max_new_tokens": 512,
        "specs": {
            "parameters": "3.09B",
            "vram_required": "~2.0 GB (4-bit quantized)",
            "ram_required": "8 GB",
            "tool_support": "High",
            "recommended_hardware": "NVIDIA GPU with 4GB+ VRAM or modern multi-core CPU"
        },
        "description": "Recommended. Outstanding balance of deep reasoning, concise answers, and tool-use reliability."
    }
}

# ============================================================
# Configuration Loading & Persistence (config.json)
# ============================================================

def load_config() -> dict[str, Any]:
    """
    Load project-wide settings from config.json.

    Returns
    -------
    dict of str to Any
        The configuration dictionary, or default fallbacks if missing or corrupted.
    """
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return DEFAULT_FALLBACK_CONFIG.copy()
    except Exception as e:
        print(f"[ERROR in backend/config.py -> load_config] Failed to load config.json:\n{traceback.format_exc()}")
        return DEFAULT_FALLBACK_CONFIG.copy()


def save_config(config_data: dict[str, Any]) -> bool:
    """
    Save project configuration changes to config.json.

    Parameters
    ----------
    config_data : dict of str to Any
        The configuration dictionary to serialize.

    Returns
    -------
    bool
        True if the write succeeded, False otherwise.
    """
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR in backend/config.py -> save_config] Failed to save config.json:\n{traceback.format_exc()}")
        return False

# ============================================================
# Model Catalog Loading & Persistence (backend/models.json)
# ============================================================

def load_models() -> dict[str, Any]:
    """
    Load the AI model catalog from backend/models.json.

    Returns
    -------
    dict of str to Any
        A dictionary mapping model IDs to their specification blocks.
    """
    try:
        if os.path.exists(MODELS_FILE_PATH):
            with open(MODELS_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return DEFAULT_FALLBACK_MODELS.copy()
    except Exception as e:
        print(f"[ERROR in backend/config.py -> load_models] Failed to load models.json:\n{traceback.format_exc()}")
        return DEFAULT_FALLBACK_MODELS.copy()


def save_models(models_data: dict[str, Any]) -> bool:
    """
    Save changes to the model catalog in backend/models.json.

    Parameters
    ----------
    models_data : dict of str to Any
        The models dictionary to serialize.

    Returns
    -------
    bool
        True if the write succeeded, False otherwise.
    """
    try:
        with open(MODELS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(models_data, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR in backend/config.py -> save_models] Failed to save models.json:\n{traceback.format_exc()}")
        return False

# ============================================================
# Model Queries & Selection
# ============================================================

def get_available_models() -> dict[str, Any]:
    """
    Retrieve all available AI models from backend/models.json.

    Returns
    -------
    dict of str to Any
        Dictionary of available models.
    """
    return load_models()


def get_active_model_config() -> dict[str, Any]:
    """
    Retrieve the configuration for the active model specified in config.json.

    Returns
    -------
    dict of str to Any
        Model configuration dictionary with runtime parameters and specs.
    """
    try:
        config = load_config()
        models = load_models()
        active_key = config.get("active_model", "qwen-2.5-3b")

        if active_key in models:
            m = models[active_key]
        else:
            first_key = next(iter(models)) if models else "qwen-2.5-3b"
            m = models.get(first_key, DEFAULT_FALLBACK_MODELS["qwen-2.5-3b"])

        return {
            "key": active_key,
            "name": m.get("name", "Unknown Model"),
            "model_type": m.get("model_type", "local"),
            "model_name": m.get("repo_id", "Qwen/Qwen2.5-3B-Instruct"),
            "model_task": m.get("task", "text-generation"),
            "model_temperature": float(m.get("temperature", 0.1)),
            "model_max_new_tokens": int(m.get("max_new_tokens", 512)),
            "specs": m.get("specs", {}),
            "description": m.get("description", "")
        }
    except Exception as e:
        print(f"[ERROR in backend/config.py -> get_active_model_config]:\n{traceback.format_exc()}")
        fallback = DEFAULT_FALLBACK_MODELS["qwen-2.5-3b"]
        return {
            "key": "qwen-2.5-3b",
            "name": fallback["name"],
            "model_type": fallback["model_type"],
            "model_name": fallback["repo_id"],
            "model_task": fallback["task"],
            "model_temperature": fallback["temperature"],
            "model_max_new_tokens": fallback["max_new_tokens"],
            "specs": fallback["specs"],
            "description": fallback["description"]
        }


def set_active_model(model_key: str) -> bool:
    """
    Update the active model key in config.json.

    Parameters
    ----------
    model_key : str
        The unique ID of the model to activate.

    Returns
    -------
    bool
        True if the update was saved successfully, False otherwise.
    """
    try:
        models = load_models()
        if model_key not in models:
            print(f"[WARNING in backend/config.py -> set_active_model] Model '{model_key}' not in backend/models.json")
            return False

        config = load_config()
        config["active_model"] = model_key
        return save_config(config)
    except Exception as e:
        print(f"[ERROR in backend/config.py -> set_active_model]:\n{traceback.format_exc()}")
        return False

# ============================================================
# Environment Settings Application
# ============================================================

def apply_environment_settings() -> None:
    """
    Apply runtime environment variables (HF cache directory, LangSmith tracing)
    from config.json into os.environ.
    """
    try:
        config = load_config()

        # Cache directory
        cache_dir = config.get("llm_cache_dir", config.get("hf_home", "S:/ollama_models"))
        if not os.environ.get("HF_HOME"):
            os.environ["HF_HOME"] = cache_dir

        # LangSmith tracing settings
        langsmith = config.get("langsmith", {})
        if langsmith.get("tracing", False):
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if langsmith.get("project"):
                os.environ["LANGCHAIN_PROJECT"] = langsmith["project"]
            if langsmith.get("endpoint"):
                os.environ["LANGCHAIN_ENDPOINT"] = langsmith["endpoint"]
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"

    except Exception as e:
        print(f"[ERROR in backend/config.py -> apply_environment_settings]:\n{traceback.format_exc()}")

# ============================================================
# Interactive CLI Selector (Invoked by run.bat)
# ============================================================

def prompt_model_selection() -> None:
    """
    Display an interactive command-line interface for selecting the AI model.
    Designed for seamless execution inside run.bat before launching Streamlit.
    """
    try:
        config = load_config()
        models = load_models()
        active_key = config.get("active_model", "")
        active_model = models.get(active_key, {})

        print("\n" + "=" * 62)
        print("  AI Model Configuration & Selection")
        print("=" * 62)

        active_name = active_model.get("name", active_key)
        specs = active_model.get("specs", {})
        vram = specs.get("vram_required", "N/A")
        ram = specs.get("ram_required", "N/A")
        tool_sup = specs.get("tool_support", "N/A")

        print(f"Current Active Model: {active_name} [{active_key}]")
        print(f"Hardware Specs:       VRAM: {vram} | RAM: {ram} | Tool Support: {tool_sup}")
        print("-" * 62)
        print("1. Keep current model & Launch ChatBot (Default)")
        print("2. Select a different model")
        print("=" * 62)

        choice = input("Enter choice [1/2] (Press Enter to continue): ").strip()

        if choice != "2":
            print(f"\n[INFO] Launching with '{active_name}'...\n")
            return

        print("\nAvailable Models in backend/models.json:")
        model_keys = list(models.keys())
        for idx, key in enumerate(model_keys, start=1):
            m = models[key]
            m_specs = m.get("specs", {})
            marker = " (ACTIVE)" if key == active_key else ""
            print(f"\n[{idx}] {m.get('name', key)}{marker}")
            print(f"    - Repo:         {m.get('repo_id')}")
            print(f"    - Hardware:     VRAM: {m_specs.get('vram_required', 'N/A')} | RAM: {m_specs.get('ram_required', 'N/A')}")
            print(f"    - Tool Support: {m_specs.get('tool_support', 'N/A')}")
            print(f"    - Description:  {m.get('description', '')}")

        print("\n" + "-" * 62)
        selection = input(f"Select model number [1-{len(model_keys)}] (or Enter to cancel): ").strip()

        if selection.isdigit():
            idx_chosen = int(selection) - 1
            if 0 <= idx_chosen < len(model_keys):
                selected_key = model_keys[idx_chosen]
                set_active_model(selected_key)
                selected_name = models[selected_key].get("name", selected_key)
                print(f"\n[SUCCESS] Active model updated to: {selected_name} [{selected_key}]\n")
                return

        print("\n[INFO] No changes made. Launching with current model...\n")

    except Exception as e:
        print(f"[ERROR in backend/config.py -> prompt_model_selection]:\n{traceback.format_exc()}")

"""
Default fallback values and file-path constants for the config package.

These are the single source of truth for:
- Where config.json and models.json live on disk
- What values to use when those files are missing or corrupted
"""

# Standard library
import os
from typing import Any

# ============================================================
# File Paths
# ============================================================

# This file lives at: backend/config/defaults.py
# So: __file__ → backend/config/defaults.py
#       dirname  → backend/config/
#       dirname  → backend/
#       dirname  → project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# config.json lives at the project root
CONFIG_FILE_PATH = os.path.join(ROOT_DIR, "config.json")

# models.json lives in backend/ (one level above this file's directory)
MODELS_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models.json")

# ============================================================
# Default Fallback Config
# ============================================================

# Used when config.json is missing or corrupted.
# llm_cache_dir=None → HuggingFace uses its own platform default
# (~/.cache/huggingface on Linux/macOS, %USERPROFILE%\.cache\huggingface on Windows).
DEFAULT_FALLBACK_CONFIG: dict[str, Any] = {
    "active_model": "qwen-2.5-3b",
    "llm_cache_dir": None,
    "database_path": "chatbot.db",
    "langsmith": {
        "tracing": False,
        "project": "ChatBot-LangGraph",
        "endpoint": "https://api.smith.langchain.com",
    },
    "system_prompt": (
        "You are a highly capable AI assistant with access to external tools. "
        "You MUST use these tools when asked to perform math, search, or look up information. "
        "Do NOT refuse to use tools. Do NOT perform calculations yourself. "
        "Always output the correct JSON format to invoke the tool when needed. "
        "IMPORTANT FORMATTING RULES: "
        "1. Never use LaTeX brackets like \\[ or \\( for math. Always use standard markdown instead. "
        "2. Do not use custom tags or pseudo-code to explain tool usage. Just output the standard tool call format. "
        "3. Provide all text responses in clean, standard Markdown format."
    ),
}

# ============================================================
# Default Fallback Models
# ============================================================

# Used when backend/models.json is missing or corrupted.
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
            "recommended_hardware": "NVIDIA GPU with 4GB+ VRAM or modern multi-core CPU",
        },
        "description": (
            "Recommended. Outstanding balance of deep reasoning, "
            "concise answers, and tool-use reliability."
        ),
    }
}

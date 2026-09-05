"""
Interactive CLI model selector — invoked by run.bat before launching Streamlit.

Presents a numbered list of available models from models.json, lets the user
pick one, and persists the choice to config.json.
"""

# Standard library
import logging
import traceback

from backend.config.app_config import load_config
from backend.config.models_config import load_models, set_active_model

logger = logging.getLogger(__name__)


def prompt_model_selection() -> None:
    """
    Display an interactive CLI for selecting the active AI model.

    Reads the current active model and all available models, then
    prompts the user to keep the current one or switch. Called by
    run.bat before `streamlit run app.py`.
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
        print(f"Current Active Model: {active_name} [{active_key}]")
        print(
            f"Hardware Specs:       "
            f"VRAM: {specs.get('vram_required', 'N/A')} | "
            f"RAM: {specs.get('ram_required', 'N/A')} | "
            f"Tool Support: {specs.get('tool_support', 'N/A')}"
        )
        print("-" * 62)
        print("1. Keep current model & Launch ChatBot (Default)")
        print("2. Select a different model")
        print("=" * 62)

        choice = input("Enter choice [1/2] (Press Enter to continue): ").strip()
        if choice != "2":
            print(f"\n[INFO] Launching with '{active_name}'...\n")
            return

        # ── Model selection menu ──
        print("\nAvailable Models in backend/models.json:")
        model_keys = list(models.keys())

        for idx, key in enumerate(model_keys, start=1):
            m = models[key]
            m_specs = m.get("specs", {})
            marker = " (ACTIVE)" if key == active_key else ""
            print(f"\n[{idx}] {m.get('name', key)}{marker}")
            print(f"    - Repo:         {m.get('repo_id')}")
            print(
                f"    - Hardware:     "
                f"VRAM: {m_specs.get('vram_required', 'N/A')} | "
                f"RAM: {m_specs.get('ram_required', 'N/A')}"
            )
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

    except Exception:
        logger.error("prompt_model_selection failed:\n%s", traceback.format_exc())

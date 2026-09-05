"""
backend.tools — self-registering tool discovery package.

════════════════════════════════════════════════════════════════
HOW TO ADD A NEW TOOL
════════════════════════════════════════════════════════════════
1. Create a new file in this folder, e.g., backend/tools/my_tool.py
2. Define your tool using @tool or BaseTool subclass.
3. At the bottom of your file, declare:

       TOOLS: list[BaseTool] = [my_tool_instance]

That's it. This __init__.py will automatically discover and register
your tool on the next run. No changes needed in any other file.

════════════════════════════════════════════════════════════════
HOW TO REMOVE A TOOL
════════════════════════════════════════════════════════════════
Delete (or rename with a leading underscore) its file. Done.

════════════════════════════════════════════════════════════════
HOW TO TEMPORARILY DISABLE A TOOL
════════════════════════════════════════════════════════════════
Set TOOLS = [] in the tool's file. The file stays but nothing is registered.

════════════════════════════════════════════════════════════════
Discovery mechanism
════════════════════════════════════════════════════════════════
pkgutil.iter_modules scans this package for all sub-modules.
Files whose names start with '_' are skipped (private/internal).
Each discovered module is imported and its TOOLS list is collected.
"""

# Standard library
import importlib
import logging
import pkgutil
import traceback

# Third-party
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# ── Auto-discovery ──
# Walk every .py file in this package (except private ones starting with '_').
# Import each, read its TOOLS list, and add everything to the registry.
_TOOL_REGISTRY: list[BaseTool] = []

for _module_info in pkgutil.iter_modules(__path__):
    if _module_info.name.startswith("_"):
        continue  # Skip __init__ and any private helper modules

    try:
        _mod = importlib.import_module(f"backend.tools.{_module_info.name}")
        _tools_in_module: list[BaseTool] = getattr(_mod, "TOOLS", [])

        if not isinstance(_tools_in_module, list):
            logger.warning(
                "backend/tools/%s.py: TOOLS is not a list — skipping.", _module_info.name
            )
            continue

        for _t in _tools_in_module:
            if isinstance(_t, BaseTool):
                _TOOL_REGISTRY.append(_t)
                logger.debug("Registered tool: '%s' from backend/tools/%s.py", _t.name, _module_info.name)
            else:
                logger.warning(
                    "backend/tools/%s.py: item %r in TOOLS is not a BaseTool — skipping.",
                    _module_info.name, _t,
                )

    except Exception:
        logger.error(
            "Failed to load tools from backend/tools/%s.py:\n%s",
            _module_info.name, traceback.format_exc(),
        )
        # Continue loading other tool modules even if one fails


def available_tools() -> list[BaseTool]:
    """
    Return all auto-discovered and registered tools.

    Callers (graph/builder.py) use this to bind tools to the LLM and
    to build the ToolNode. The list order follows filesystem discovery
    order (alphabetical on most platforms).

    Returns
    -------
    list of BaseTool
        A copy of the registry so callers can't accidentally mutate it.
    """
    return list(_TOOL_REGISTRY)


# Public surface — mirrors the old flat tools.py
__all__ = ["available_tools", "TOOLS"]

# Expose the registry as TOOLS for consistency with individual tool files
TOOLS = _TOOL_REGISTRY

"""
Fallback tool-call parser for local HuggingFace models.

Some local models (e.g., Qwen variants) don't produce native tool_call
objects even when bind_tools() is used. They instead emit the call as
plain JSON text or inside <tool_call>...</tool_call> XML tags.

This module tries multiple extraction strategies in order, then validates
the extracted tool name against the registered tool registry to avoid
treating unrelated JSON (e.g., a code example in the reply) as a tool call.
"""

# Standard library
import json
import logging
import re
import uuid

logger = logging.getLogger(__name__)


def parse_tool_call_from_text(
    content: str,
    registered_tool_names: set[str],
) -> dict | None:
    """
    Attempt to extract a tool-call dict from raw assistant text.

    Strategies tried in order
    -------------------------
    1. Qwen/Mistral ``<tool_call>{ ... }</tool_call>`` XML block
    2. Fenced ``\\`\\`\\`json { ... }\\`\\`\\`` code block
    3. Bare JSON object as the entire response (starts with ``{``, ends with ``}``)

    Safety
    ------
    The extracted tool name is validated against ``registered_tool_names``.
    If it doesn't match, ``None`` is returned so the text is treated as a
    normal assistant message.

    Parameters
    ----------
    content : str
        The raw text content of the assistant's response.
    registered_tool_names : set of str
        Set of valid tool names to validate against.

    Returns
    -------
    dict or None
        A tool-call dict with keys ``name``, ``args``, ``id``, ``type``,
        or ``None`` if no valid tool call was detected.
    """
    content = content.strip()
    json_str: str | None = None

    # ── Strategy 1: <tool_call>{ ... }</tool_call> ──
    tag_match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", content, re.DOTALL)
    if tag_match:
        json_str = tag_match.group(1)

    # ── Strategy 2: ```json { ... }``` fenced block ──
    if not json_str:
        block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if block_match:
            json_str = block_match.group(1)

    # ── Strategy 3: Bare JSON as the entire response ──
    if not json_str and content.startswith("{") and content.endswith("}"):
        json_str = content

    if not json_str:
        return None

    # ── Parse JSON ──
    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    # ── Resolve tool name and args from various key conventions ──
    tool_name: str | None = None
    args: dict = {}

    if "name" in parsed:
        # Standard: {"name": "tool", "arguments": {...}}
        tool_name = parsed["name"]
        args = parsed.get("arguments", parsed.get("args", {}))
    elif "tool" in parsed:
        # Alternative: {"tool": "tool_name", "arguments": {...}}
        tool_name = parsed["tool"]
        args = parsed.get("arguments", parsed.get("args", parsed.get("operands", {})))
    elif len(parsed) == 1:
        # Shorthand: {"tool_name": {"arg": "val"}}
        tool_name = list(parsed.keys())[0]
        args = parsed[tool_name] if isinstance(parsed[tool_name], dict) else {}

    if not tool_name:
        return None

    # ── Safety check: reject names not in the registry ──
    if tool_name not in registered_tool_names:
        logger.debug(
            "parse_tool_call_from_text: '%s' not in registry %s — ignoring.",
            tool_name, registered_tool_names,
        )
        return None

    return {
        "name": tool_name,
        "args": args if isinstance(args, dict) else {},
        "id": str(uuid.uuid4()),
        "type": "tool_call",
    }

"""
Arithmetic calculator tool.

Supported operations: add, sub, mul, div, pow, mod.

To add a new operation, add a key to _OPERATIONS below — no other file changes needed.
To add a completely new math tool, create a new file in backend/tools/ instead.
"""

# Standard library
import logging
import traceback

# Third-party
from langchain_core.tools import tool, BaseTool

logger = logging.getLogger(__name__)


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.

    Supported operations: add, sub, mul, div, pow, mod.

    Parameters
    ----------
    first_num : float
        The first operand.
    second_num : float
        The second operand.
    operation : str
        One of: 'add', 'sub', 'mul', 'div', 'pow', 'mod'.

    Returns
    -------
    dict
        On success: {'first_num', 'second_num', 'operation', 'result'}.
        On failure: {'error': '<reason>'}.
    """
    # ── Operation map ──
    # To add a new operation (e.g., 'sqrt'), simply add a new key here.
    # The key is what the LLM must pass as the `operation` argument.
    _OPERATIONS = {
        "add": lambda a, b: a + b,
        "sub": lambda a, b: a - b,
        "mul": lambda a, b: a * b,
        "div": lambda a, b: a / b,   # zero-divisor guarded below
        "pow": lambda a, b: a ** b,
        "mod": lambda a, b: a % b,   # zero-divisor guarded below
    }

    try:
        if operation not in _OPERATIONS:
            supported = ", ".join(_OPERATIONS.keys())
            return {"error": f"Unsupported operation '{operation}'. Supported: {supported}"}

        # Guard zero-divisor before invoking the lambda
        if operation in ("div", "mod") and second_num == 0:
            return {"error": f"'{operation}' by zero is not allowed"}

        result = _OPERATIONS[operation](first_num, second_num)
        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }

    except Exception:
        logger.error("calculator tool failed:\n%s", traceback.format_exc())
        return {"error": "An unexpected error occurred in the calculator tool."}


# ── Tool registry for this module ──
# The tools/__init__.py auto-discovers this list.
TOOLS: list[BaseTool] = [calculator]

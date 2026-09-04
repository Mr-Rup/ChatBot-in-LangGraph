"""
Agent tools definitions for the ChatBot.
"""

# Standard library
import traceback

# Third-party
try:
   from langchain_community.tools import DuckDuckGoSearchResults
   from langchain_core.tools import tool
   from langchain_core.tools import BaseTool
except Exception as e:
   print(f"[ERROR in backend/tools.py -> Imports] Failed to import:\n{traceback.format_exc()}")
   raise ImportError(f'Failed to import necessary modules in tools.py: {e}')

# ============================================================
# Search Tools
# ============================================================

search_tool = DuckDuckGoSearchResults(region='us-en')

# ============================================================
# Calculators
# ============================================================

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div.

    Parameters
    ----------
    first_num : float
        The first operand.
    second_num : float
        The second operand.
    operation : str
        The operation to perform (add, sub, mul, div).

    Returns
    -------
    dict
        A dictionary containing the operands, operation, and the result, or an error.
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        print(f"[ERROR in backend/tools.py -> calculator tool] Failed to calculate:\n{traceback.format_exc()}")
        return {"error": str(e)}

   
# ============================================================
# Tool Registry
# ============================================================

def available_tools() -> list[BaseTool]:
   """
   Collect all tools defined in this module for the language model to use.

   Returns
   -------
   list of BaseTool
       A list of callable LangChain tools available in the global scope.
   """
   try:
      tools = [i for i in globals().values() if callable(i) and hasattr(i, "_is_tool")]
      print(tools)
      return tools
   except Exception as e:
      print(f"[ERROR in backend/tools.py -> available_tools] Failed to collect tools:\n{traceback.format_exc()}")
      return []
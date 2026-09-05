"""
DuckDuckGo web search tool.

Adding this file to backend/tools/ is all that's needed — the package
auto-discovers it and registers the TOOLS list automatically.
"""

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool

# region='us-en' targets English-language results; change to your locale if needed.
# num_results controls how many snippets are returned per query.
_search = DuckDuckGoSearchResults(region="us-en", num_results=4)

# ── Tool registry for this module ──
# The tools/__init__.py auto-discovers this list. Add more search variants here
# (e.g., DuckDuckGoSearchRun for plain text) if needed.
TOOLS: list[BaseTool] = [_search]

from __future__ import annotations

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from .list_read_tools import register_list_read_tools
from .search_graph_tools import register_search_graph_tools
from .stats_tools import register_stats_tools


def register_framework_query_tools(mcp: FastMCP) -> None:
    register_stats_tools(mcp)
    register_list_read_tools(mcp)
    register_search_graph_tools(mcp)

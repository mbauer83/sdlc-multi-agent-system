from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]


logger = logging.getLogger(__name__)


def normalize_incoming_tool_name(tool_name: str, *, known_tools: set[str]) -> str:
    """Normalize an incoming tool name from bridges that namespace tools."""

    if tool_name in known_tools:
        return tool_name

    for sep in ("-", ":", ".", "/"):
        if sep in tool_name:
            candidate = tool_name.rsplit(sep, 1)[-1]
            if candidate in known_tools:
                return candidate
    return tool_name


def install_call_tool_normalizer(mcp: FastMCP) -> None:
    """Override FastMCP CallTool handler to normalize bridged tool names."""

    async def _call_tool_handler_with_normalization(name: str, arguments: dict[str, Any]) -> Any:
        tools = mcp._tool_manager.list_tools()  # type: ignore[attr-defined]
        known = {t.name for t in tools}
        normalized = normalize_incoming_tool_name(name, known_tools=known)
        if normalized != name:
            logger.info("Normalized incoming tool name %r -> %r", name, normalized)
        context = mcp.get_context()
        return await mcp._tool_manager.call_tool(  # type: ignore[attr-defined]
            normalized,
            arguments,
            context=context,
            convert_result=True,
        )

    mcp._mcp_server.call_tool(validate_input=False)(_call_tool_handler_with_normalization)  # type: ignore[attr-defined]

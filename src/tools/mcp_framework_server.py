"""MCP server exposing framework/spec query and graph tools."""

from __future__ import annotations

import argparse
import os

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.framework_mcp import (
    install_call_tool_normalizer,
    normalize_incoming_tool_name,
    register_framework_query_tools,
)

_INSTRUCTIONS = (
    "Framework/spec query tools with section-level search and formal reference graph traversal. "
    "Use query-first retrieval and summary-first reads."
)

_HOST = os.getenv("SDLC_MCP_HOST", "127.0.0.1")
_PORT = int(os.getenv("SDLC_MCP_PORT", "8002"))
_LOG_LEVEL = os.getenv("SDLC_MCP_LOG_LEVEL", "INFO")
_SERVER_NAME = os.getenv("SDLC_MCP_SERVER_NAME", "sdlc_framework")
_MOUNT_PATH = os.getenv("SDLC_MCP_MOUNT_PATH", "/")
_SSE_PATH = os.getenv("SDLC_MCP_SSE_PATH", "/sse")
_MESSAGE_PATH = os.getenv("SDLC_MCP_MESSAGE_PATH", "/messages/")
_STREAMABLE_HTTP_PATH = os.getenv("SDLC_MCP_STREAMABLE_HTTP_PATH", "/mcp")
_JSON_RESPONSE = os.getenv("SDLC_MCP_JSON_RESPONSE", "1") in {"1", "true", "TRUE", "yes", "YES"}
_STATELESS_HTTP = os.getenv("SDLC_MCP_STATELESS_HTTP", "1") in {"1", "true", "TRUE", "yes", "YES"}

mcp = FastMCP(
    name=_SERVER_NAME,
    instructions=_INSTRUCTIONS,
    host=_HOST,
    port=_PORT,
    mount_path=_MOUNT_PATH,
    sse_path=_SSE_PATH,
    message_path=_MESSAGE_PATH,
    streamable_http_path=_STREAMABLE_HTTP_PATH,
    json_response=_JSON_RESPONSE,
    stateless_http=_STATELESS_HTTP,
    log_level=_LOG_LEVEL,  # type: ignore[arg-type]
)



def _normalize_incoming_tool_name(tool_name: str, *, known_tools: set[str]) -> str:
    return normalize_incoming_tool_name(tool_name, known_tools=known_tools)


install_call_tool_normalizer(mcp)
register_framework_query_tools(mcp)



def main() -> None:
    parser = argparse.ArgumentParser(prog="sdlc-mcp-framework")
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default=os.getenv("SDLC_MCP_TRANSPORT", "streamable-http"),
        help="MCP transport",
    )
    parser.add_argument(
        "--mount-path",
        default=os.getenv("SDLC_MCP_MOUNT_PATH"),
        help="Optional mount path for SSE transport",
    )
    args = parser.parse_args()
    mcp.run(transport=args.transport, mount_path=args.mount_path)


if __name__ == "__main__":
    main()

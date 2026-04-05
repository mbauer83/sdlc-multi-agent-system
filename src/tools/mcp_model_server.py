"""MCP server exposing ERP v2.0 model tools (query + verification + write).

This module is intentionally small: it wires together tool-registration modules
under src/tools/model_mcp/.

Tool logic lives in:
- src/tools/model_mcp/*_tools.py (MCP tool wrappers)
- src/common/* (domain-ish logic)
- src/tools/model_write/* (writer I/O operations)
"""

from __future__ import annotations

import argparse
import logging
import os

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp import (
    install_call_tool_normalizer,
    normalize_incoming_tool_name,
    register_query_tools,
    register_verify_tools,
    register_watch_tools,
    register_write_tools,
)

# Re-export commonly used tool functions for direct calling in tests.
from src.tools.model_mcp.write_tools import (  # noqa: F401
    model_create_connection,
    model_create_diagram,
    model_create_entity,
    model_write_help,
)
from src.tools.model_mcp.verify_tools import (  # noqa: F401
    model_verify_all,
    model_verify_file,
)


logger = logging.getLogger(__name__)


_INSTRUCTIONS = (
    "ERP v2.0 model query + model verifier + model writer tools. "
    "Targets an ERP v2.0 architecture repository (model-entities/, connections/, diagram-catalog/). "
    "By default mounts both ENG-001 engagement repo + enterprise-repository; use repo_scope to restrict."
)

_HOST = os.getenv("SDLC_MCP_HOST", "127.0.0.1")
_PORT = int(os.getenv("SDLC_MCP_PORT", "8000"))
_LOG_LEVEL = os.getenv("SDLC_MCP_LOG_LEVEL", "INFO")
_SERVER_NAME = os.getenv("SDLC_MCP_SERVER_NAME", "sdlc_model")
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
    """Backward-compatible alias used by tests."""

    return normalize_incoming_tool_name(tool_name, known_tools=known_tools)


# Install CallTool name normalization handler.
install_call_tool_normalizer(mcp)

# Register tool groups.
register_query_tools(mcp)
register_verify_tools(mcp)
register_watch_tools(mcp)
register_write_tools(mcp)


def main() -> None:
    """Run the MCP server.

    Default transport is stdio. For containerized deployments where the MCP host
    cannot spawn a stdio subprocess, use SSE/HTTP transports.
    """

    parser = argparse.ArgumentParser(prog="sdlc-mcp-model")
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default=os.getenv("SDLC_MCP_TRANSPORT", "streamable-http"),
        help="MCP transport (default: stdio)",
    )
    parser.add_argument(
        "--mount-path",
        default=os.getenv("SDLC_MCP_MOUNT_PATH"),
        help="Optional mount path for SSE transport (advanced)",
    )
    args = parser.parse_args()

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

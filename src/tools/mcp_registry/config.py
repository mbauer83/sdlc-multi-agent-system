from __future__ import annotations

import os
from pathlib import Path


def workspace_root() -> Path:
    # .../src/tools/mcp_registry/config.py -> parents[0]=mcp_registry, [1]=tools, [2]=src, [3]=repo
    return Path(__file__).resolve().parents[3]


def default_agents_root() -> Path:
    env = os.getenv("SDLC_MCP_AGENTS_ROOT")
    if env:
        path = Path(env).expanduser()
        if not path.is_absolute():
            path = workspace_root() / path
        return path
    return workspace_root() / "agents"


def agents_root_path(agents_root: str | None) -> Path:
    if agents_root is None:
        return default_agents_root()
    path = Path(agents_root).expanduser()
    if not path.is_absolute():
        path = workspace_root() / path
    return path


def as_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw in {"1", "true", "TRUE", "yes", "YES"}


INSTRUCTIONS = (
    "Agent + Skill registry tools. "
    "Scans an agents directory for <agent_id>/AGENT.md and <agent_id>/skills/*.md. "
    "Intended for bifrost/goose to discover identities and cacheable skill procedures."
)

HOST = os.getenv("SDLC_MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("SDLC_MCP_PORT", "8001"))
LOG_LEVEL = os.getenv("SDLC_MCP_LOG_LEVEL", "INFO")
SERVER_NAME = os.getenv("SDLC_MCP_SERVER_NAME", "sdlc_registry")
MOUNT_PATH = os.getenv("SDLC_MCP_MOUNT_PATH", "/")
SSE_PATH = os.getenv("SDLC_MCP_SSE_PATH", "/sse")
MESSAGE_PATH = os.getenv("SDLC_MCP_MESSAGE_PATH", "/messages/")
STREAMABLE_HTTP_PATH = os.getenv("SDLC_MCP_STREAMABLE_HTTP_PATH", "/mcp")
JSON_RESPONSE = as_bool_env("SDLC_MCP_JSON_RESPONSE", default=True)
STATELESS_HTTP = as_bool_env("SDLC_MCP_STATELESS_HTTP", default=True)

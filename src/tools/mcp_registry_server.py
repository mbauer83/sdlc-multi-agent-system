"""MCP server exposing agent and skill discovery tools."""

from __future__ import annotations

import argparse
import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.mcp_registry.config import (
    HOST,
    INSTRUCTIONS,
    JSON_RESPONSE,
    LOG_LEVEL,
    MESSAGE_PATH,
    MOUNT_PATH,
    PORT,
    SERVER_NAME,
    SSE_PATH,
    STATELESS_HTTP,
    STREAMABLE_HTTP_PATH,
)
from src.tools.mcp_registry.service import (
    check_skill_readiness as service_check_skill_readiness,
    get_skill_details as service_get_skill_details,
    list_agent_skills as service_list_agent_skills,
    list_agents as service_list_agents,
    list_skill_triggers as service_list_skill_triggers,
    load_agent_identity as service_load_agent_identity,
    normalize_incoming_tool_name,
)


logger = logging.getLogger(__name__)


def _normalize_incoming_tool_name(tool_name: str, *, known_tools: set[str]) -> str:
    return normalize_incoming_tool_name(tool_name, known_tools=known_tools)

mcp = FastMCP(
    name=SERVER_NAME,
    instructions=INSTRUCTIONS,
    host=HOST,
    port=PORT,
    mount_path=MOUNT_PATH,
    sse_path=SSE_PATH,
    message_path=MESSAGE_PATH,
    streamable_http_path=STREAMABLE_HTTP_PATH,
    json_response=JSON_RESPONSE,
    stateless_http=STATELESS_HTTP,
    log_level=LOG_LEVEL,  # type: ignore[arg-type]
)


async def _call_tool_handler_with_normalization(name: str, arguments: dict[str, Any]) -> Any:
    tools = mcp._tool_manager.list_tools()  # type: ignore[attr-defined]
    known = {t.name for t in tools}
    normalized = _normalize_incoming_tool_name(name, known_tools=known)
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


@mcp.tool(
    name="list_agents",
    title="Registry: List Agents",
    description=(
        "Scan the agents root directory and return valid agent IDs (directory names). "
        "A directory is considered valid if it contains an AGENT.md file." 
        "\n\nBy default, agents_root is resolved from SDLC_MCP_AGENTS_ROOT or ./agents."
    ),
    structured_output=True,
)
def list_agents(*, agents_root: str | None = None) -> list[str]:
    return service_list_agents(agents_root=agents_root)


@mcp.tool(
    name="load_agent_identity",
    title="Registry: Load Agent Identity",
    description=(
        "Load and parse <agent_id>/AGENT.md. By default returns runtime-relevant frontmatter, "
        "system-prompt-identity, and the Runtime Behavioral Stance subsection. "
        "Set include_full_frontmatter=true to return the full YAML frontmatter."
    ),
    structured_output=True,
)
def load_agent_identity(
    agent_id: str,
    *,
    agents_root: str | None = None,
    include_full_frontmatter: bool = False,
) -> dict[str, object] | None:
    return service_load_agent_identity(
        agent_id,
        agents_root=agents_root,
        include_full_frontmatter=include_full_frontmatter,
    )


@mcp.tool(
    name="list_agent_skills",
    title="Registry: List Agent Skills",
    description=(
        "List skill IDs for an agent by scanning <agent_id>/skills/*.md and returning file basenames." 
        "Results are sorted for stable caching."
    ),
    structured_output=True,
)
def list_agent_skills(
    agent_id: str,
    *,
    agents_root: str | None = None,
) -> list[str]:
    return service_list_agent_skills(agent_id, agents_root=agents_root)


@mcp.tool(
    name="list_skill_triggers",
    title="Registry: List Skill Triggers",
    description=(
        "Return trigger metadata for skills without loading full skill sections. "
        "Provides skill_id, agent_id, trigger_phases, trigger_conditions, invoke_when, and entry_points. "
        "If agent_id is omitted, scans all agents."
    ),
    structured_output=True,
)
def list_skill_triggers(
    *,
    agent_id: str | None = None,
    agents_root: str | None = None,
) -> list[dict[str, object]]:
    return service_list_skill_triggers(agent_id=agent_id, agents_root=agents_root)


@mcp.tool(
    name="get_skill_details",
    title="Registry: Get Skill Details",
    description=(
        "Parse <agent_id>/skills/<skill_id>.md and return runtime-relevant skill payloads by default: "
        "runtime frontmatter + runtime sections (Inputs Required, Procedure/Steps, Algedonic Triggers, Feedback Loop, Outputs). "
        "The procedure section is also returned separately for compatibility. "
        "Set include_full_frontmatter=true to return full YAML frontmatter."
    ),
    structured_output=True,
)
def get_skill_details(
    agent_id: str,
    skill_id: str,
    *,
    agents_root: str | None = None,
    include_full_frontmatter: bool = False,
) -> dict[str, object] | None:
    return service_get_skill_details(
        agent_id,
        skill_id,
        agents_root=agents_root,
        include_full_frontmatter=include_full_frontmatter,
    )


@mcp.tool(
    name="check_skill_readiness",
    title="Registry: Check Skill Readiness",
    description=(
        "Cross-reference a skill's '## Inputs Required' table against provided input keys. "
        "If skill_id is not unique across agents, returns candidates."
    ),
    structured_output=True,
)
def check_skill_readiness(
    skill_id: str,
    provided_inputs: list[str],
    *,
    agents_root: str | None = None,
) -> dict[str, object]:
    return service_check_skill_readiness(
        skill_id,
        provided_inputs,
        agents_root=agents_root,
    )


def main() -> None:
    """Run the MCP registry server.

    Default transport is stdio. For containerized deployments where the MCP host
    cannot spawn a stdio subprocess, use SSE/HTTP transports.
    """

    parser = argparse.ArgumentParser(prog="sdlc-mcp-registry")
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

    mcp.run(transport=args.transport, mount_path=args.mount_path)


if __name__ == "__main__":
    main()

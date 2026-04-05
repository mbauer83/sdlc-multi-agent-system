"""MCP server exposing agent + skill discovery tools ("registry librarian").

This server is intentionally filesystem-backed and read-only:
- Agents are discovered from an agents root directory.
- Identities are loaded from: <agents_root>/<agent_id>/AGENT.md
- Skills are loaded from: <agents_root>/<agent_id>/skills/<skill_id>.md

Parsing
-------
- Uses python-frontmatter to extract YAML frontmatter.
- Uses anyio for async file reads (tools are sync wrappers).

Design goals
------------
- Highly cacheable outputs for LLM prompt caching: deterministic ordering,
  stable string normalization, and avoidance of dynamic fields.
- Runtime-relevant payloads by default (agent identity + runtime stance,
  skill runtime frontmatter + executable sections).
- Optional compatibility path for full frontmatter via tool flags.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anyio  # type: ignore[import-not-found]
import frontmatter  # type: ignore[import-not-found]
from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]


logger = logging.getLogger(__name__)


def _workspace_root() -> Path:
    # .../src/tools/mcp_registry_server.py -> parents[0]=tools, [1]=src, [2]=repo root
    return Path(__file__).resolve().parents[2]


def _default_agents_root() -> Path:
    env = os.getenv("SDLC_MCP_AGENTS_ROOT")
    if env:
        p = Path(env).expanduser()
        if not p.is_absolute():
            p = _workspace_root() / p
        return p
    return _workspace_root() / "agents"


async def _read_text(path: Path) -> str:
    async with await anyio.open_file(path, "r", encoding="utf-8") as f:
        return await f.read()


def _read_text_sync(path: Path) -> str:
    return anyio.run(_read_text, path)


def _normalize_newlines(text: str) -> str:
    # Ensure consistent output across platforms.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Avoid trailing whitespace differences affecting caching.
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    # Collapse excessive trailing blank lines.
    return text.strip("\n") + "\n"


_SECTION_RE = re.compile(r"^##\s+(?P<title>[^\n]+?)\s*$", re.MULTILINE)
_H3_SECTION_RE = re.compile(r"^###\s+(?P<title>[^\n]+?)\s*$", re.MULTILINE)

_AGENT_RUNTIME_FRONTMATTER_KEYS: tuple[str, ...] = (
    "agent-id",
    "name",
    "display-name",
    "role-type",
    "vsm-position",
    "primary-phases",
    "owns-repository",
    "runtime-ref",
    "system-prompt-identity",
)

_SKILL_RUNTIME_FRONTMATTER_KEYS: tuple[str, ...] = (
    "skill-id",
    "agent",
    "name",
    "invoke-when",
    "trigger-phases",
    "primary-outputs",
    "complexity-class",
)

_SKILL_RUNTIME_SECTION_ORDER: tuple[str, ...] = (
    "Inputs Required",
    "Procedure",
    "Algedonic Triggers",
    "Feedback Loop",
    "Outputs",
)


def _extract_h2_section(markdown: str, *, title: str) -> str | None:
    """Extract an H2 section (## Title) body as markdown.

    Returns the body content (excluding the heading line), normalized.
    """

    markdown = _normalize_newlines(markdown)
    matches = list(_SECTION_RE.finditer(markdown))
    for i, m in enumerate(matches):
        if m.group("title").strip().lower() != title.strip().lower():
            continue
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        body = markdown[body_start:body_end]
        # Strip leading/trailing blank lines inside the section for stability.
        body = body.strip("\n") + "\n"
        return body
    return None


def _extract_h3_subsection(markdown: str, *, h2_title: str, h3_title: str) -> str | None:
    """Extract an H3 subsection body under a specific H2 section.

    Returns the subsection body content (excluding heading line), normalized.
    """

    h2_body = _extract_h2_section(markdown, title=h2_title)
    if h2_body is None:
        return None

    h2_body = _normalize_newlines(h2_body)
    matches = list(_H3_SECTION_RE.finditer(h2_body))
    for i, m in enumerate(matches):
        if m.group("title").strip().lower() != h3_title.strip().lower():
            continue
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(h2_body)
        body = h2_body[body_start:body_end]
        body = body.strip("\n") + "\n"
        return body
    return None


def _filter_frontmatter(meta: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {k: meta[k] for k in keys if k in meta}


def _extract_skill_runtime_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for title in _SKILL_RUNTIME_SECTION_ORDER:
        body = _extract_h2_section(markdown, title=title)
        # Backward compatibility: some skills use "Steps" instead of "Procedure".
        if body is None and title == "Procedure":
            body = _extract_h2_section(markdown, title="Steps")
        if body is not None:
            sections[title] = _normalize_newlines(body)
    return sections


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _agents_root_path(agents_root: str | None) -> Path:
    if agents_root is None:
        return _default_agents_root()
    p = Path(agents_root).expanduser()
    if not p.is_absolute():
        p = _workspace_root() / p
    return p


def _agent_dir(agents_root: Path, agent_id: str) -> Path:
    # Defensive: avoid path traversal.
    agent_id = agent_id.strip().strip("/\\")
    if agent_id in {"", ".", ".."} or "/" in agent_id or "\\" in agent_id:
        raise ValueError("invalid agent_id")
    return agents_root / agent_id


def _skill_path(agents_root: Path, agent_id: str, skill_id: str) -> Path:
    skill_id = skill_id.strip().strip("/\\")
    if skill_id in {"", ".", ".."} or "/" in skill_id or "\\" in skill_id:
        raise ValueError("invalid skill_id")
    return _agent_dir(agents_root, agent_id) / "skills" / f"{skill_id}.md"


@dataclass(frozen=True)
class ParsedMarkdown:
    frontmatter: dict[str, Any]
    content: str


def _parse_frontmatter(markdown: str) -> ParsedMarkdown:
    post = frontmatter.loads(markdown)
    meta: dict[str, Any] = dict(post.metadata or {})
    # Normalize frontmatter key ordering deterministically when returned.
    meta_sorted = {k: meta[k] for k in sorted(meta.keys())}
    content = _normalize_newlines(post.content or "")
    return ParsedMarkdown(frontmatter=meta_sorted, content=content)


_INSTRUCTIONS = (
    "Agent + Skill registry tools. "
    "Scans an agents directory for <agent_id>/AGENT.md and <agent_id>/skills/*.md. "
    "Intended for bifrost/goose to discover identities and cacheable skill procedures."
)

_HOST = os.getenv("SDLC_MCP_HOST", "127.0.0.1")
_PORT = int(os.getenv("SDLC_MCP_PORT", "8001"))
_LOG_LEVEL = os.getenv("SDLC_MCP_LOG_LEVEL", "INFO")
_SERVER_NAME = os.getenv("SDLC_MCP_SERVER_NAME", "sdlc_registry")
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
    """Normalize an incoming tool name from bridges that namespace tools.

    Some MCP→OpenAI bridges expose tool names like "ServerName-tool_name" to the
    model, and then forward that *prefixed* name back to the MCP server.

    This server only registers the canonical tool names (e.g. "list_agents").
    To remain compatible without polluting the tool list, we strip prefixes if the
    suffix matches a registered tool.
    """

    if tool_name in known_tools:
        return tool_name

    for sep in ("-", ":", ".", "/"):
        if sep in tool_name:
            candidate = tool_name.rsplit(sep, 1)[-1]
            if candidate in known_tools:
                return candidate
    return tool_name


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
    root = _agents_root_path(agents_root)
    if not root.exists() or not root.is_dir():
        return []

    agent_ids: list[str] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        if (child / "AGENT.md").is_file():
            agent_ids.append(child.name)
    return agent_ids


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
    root = _agents_root_path(agents_root)
    agent_dir = _agent_dir(root, agent_id)
    path = agent_dir / "AGENT.md"
    if not path.is_file():
        return None

    raw = _read_text_sync(path)
    parsed = _parse_frontmatter(raw)
    system_prompt = parsed.frontmatter.get("system-prompt-identity")
    if not isinstance(system_prompt, str):
        system_prompt = None

    runtime_behavioral_stance = _extract_h3_subsection(
        parsed.content,
        h2_title="11. Personality & Behavioral Stance",
        h3_title="Runtime Behavioral Stance",
    )

    runtime_frontmatter = _filter_frontmatter(parsed.frontmatter, _AGENT_RUNTIME_FRONTMATTER_KEYS)

    return {
        "agent_id": agent_id,
        "path": str(path),
        "frontmatter": parsed.frontmatter if include_full_frontmatter else runtime_frontmatter,
        "runtime_frontmatter": runtime_frontmatter,
        "system_prompt_identity": system_prompt,
        "runtime_behavioral_stance": runtime_behavioral_stance,
    }


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
    root = _agents_root_path(agents_root)
    skills_dir = _agent_dir(root, agent_id) / "skills"
    if not skills_dir.is_dir():
        return []

    skill_ids: list[str] = []
    for p in sorted(skills_dir.iterdir(), key=lambda x: x.name):
        if p.is_file() and p.suffix.lower() == ".md":
            skill_ids.append(p.stem)
    return skill_ids


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
    root = _agents_root_path(agents_root)

    agents = [agent_id] if isinstance(agent_id, str) and agent_id.strip() else list_agents(agents_root=str(root))
    out: list[dict[str, object]] = []

    for aid in agents:
        for sid in list_agent_skills(aid, agents_root=str(root)):
            path = _skill_path(root, aid, sid)
            if not path.is_file():
                continue

            raw = _read_text_sync(path)
            parsed = _parse_frontmatter(raw)
            fm = parsed.frontmatter

            trigger_phases = fm.get("trigger-phases")
            if isinstance(trigger_phases, list):
                phases = [str(x) for x in trigger_phases]
            elif trigger_phases is None:
                phases = []
            else:
                phases = [str(trigger_phases)]

            trigger_conditions = fm.get("trigger-conditions")
            if isinstance(trigger_conditions, list):
                conditions = [str(x) for x in trigger_conditions]
            elif trigger_conditions is None:
                conditions = []
            else:
                conditions = [str(trigger_conditions)]

            entry_points = fm.get("entry-points")
            if isinstance(entry_points, list):
                eps = [str(x) for x in entry_points]
            elif entry_points is None:
                eps = []
            else:
                eps = [str(entry_points)]

            invoke_when = fm.get("invoke-when")
            invoke_when_str = str(invoke_when).strip() if invoke_when is not None else None

            out.append(
                {
                    "agent_id": aid,
                    "skill_id": sid,
                    "path": str(path),
                    "trigger_phases": phases,
                    "trigger_conditions": conditions,
                    "invoke_when": invoke_when_str,
                    "entry_points": eps,
                }
            )

    out.sort(key=lambda r: (str(r["agent_id"]), str(r["skill_id"])))
    return out


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
    root = _agents_root_path(agents_root)
    path = _skill_path(root, agent_id, skill_id)
    if not path.is_file():
        return None

    raw = _read_text_sync(path)
    parsed = _parse_frontmatter(raw)
    runtime_sections = _extract_skill_runtime_sections(parsed.content)
    procedure = runtime_sections.get("Procedure")

    # Cache-friendly: always return a string (or None) plus a hash.
    procedure_norm = _normalize_newlines(procedure) if procedure is not None else None
    procedure_hash = _sha256_text(procedure_norm) if isinstance(procedure_norm, str) else None
    runtime_frontmatter = _filter_frontmatter(parsed.frontmatter, _SKILL_RUNTIME_FRONTMATTER_KEYS)
    runtime_blob = "\n\n".join(
        f"## {name}\n{body.rstrip()}" for name, body in runtime_sections.items()
    )
    runtime_sha256 = _sha256_text(runtime_blob) if runtime_blob else None

    return {
        "agent_id": agent_id,
        "skill_id": skill_id,
        "path": str(path),
        "frontmatter": parsed.frontmatter if include_full_frontmatter else runtime_frontmatter,
        "runtime_frontmatter": runtime_frontmatter,
        "runtime_sections": runtime_sections,
        "runtime_sha256": runtime_sha256,
        "procedure_markdown": procedure_norm,
        "procedure_sha256": procedure_hash,
    }


def _parse_inputs_required_table(markdown: str) -> tuple[list[str], list[dict[str, str]]]:
    """Parse required input keys from an '## Inputs Required' markdown table.

    Returns (required_keys, rows) where rows is a list of cell dicts keyed by header.

    Heuristic:
    - Treat rows as required unless the row contains the word 'optional' (any cell).
    - The key name is taken from the first column.
    """

    section = _extract_h2_section(markdown, title="Inputs Required")
    if section is None:
        return ([], [])

    lines = [ln for ln in _normalize_newlines(section).split("\n") if ln.strip()]
    # Find the first markdown table header line.
    header_idx = next((i for i, ln in enumerate(lines) if ln.strip().startswith("|") and ln.count("|") >= 2), None)
    if header_idx is None or header_idx + 1 >= len(lines):
        return ([], [])

    header_line = lines[header_idx]
    sep_line = lines[header_idx + 1]
    if "---" not in sep_line:
        return ([], [])

    def split_row(row: str) -> list[str]:
        row = row.strip().strip("|")
        return [c.strip() for c in row.split("|")]

    headers = split_row(header_line)
    rows: list[dict[str, str]] = []
    required_keys: list[str] = []

    for ln in lines[header_idx + 2 :]:
        if not ln.strip().startswith("|"):
            break
        cells = split_row(ln)
        if len(cells) < 1:
            continue
        # Pad cells to headers.
        if len(cells) < len(headers):
            cells = cells + [""] * (len(headers) - len(cells))
        row_dict = {headers[i]: cells[i] for i in range(len(headers))}
        rows.append(row_dict)

        key = cells[0]
        key = re.sub(r"^`(.+?)`$", r"\1", key.strip())
        key = re.sub(r"\*\*(.+?)\*\*", r"\1", key).strip()
        if not key:
            continue

        joined = " ".join(cells).lower()
        if "optional" in joined:
            continue
        required_keys.append(key)

    # Stable ordering, but preserve table order if possible.
    seen: set[str] = set()
    ordered_required: list[str] = []
    for k in required_keys:
        if k not in seen:
            ordered_required.append(k)
            seen.add(k)

    return (ordered_required, rows)


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
    root = _agents_root_path(agents_root)
    candidates: list[tuple[str, Path]] = []

    for agent in list_agents(agents_root=str(root)):
        p = _skill_path(root, agent, skill_id)
        if p.is_file():
            candidates.append((agent, p))

    if not candidates:
        return {"skill_id": skill_id, "found": False, "reason": "not_found", "candidates": []}

    if len(candidates) > 1:
        return {
            "skill_id": skill_id,
            "found": False,
            "reason": "ambiguous",
            "candidates": [a for a, _ in candidates],
        }

    agent_id, path = candidates[0]
    raw = _read_text_sync(path)
    parsed = _parse_frontmatter(raw)
    required_keys, _rows = _parse_inputs_required_table(parsed.content)

    provided_set = {k.strip() for k in provided_inputs if isinstance(k, str) and k.strip()}
    missing = [k for k in required_keys if k not in provided_set]

    return {
        "skill_id": skill_id,
        "agent_id": agent_id,
        "path": str(path),
        "found": True,
        "required_inputs": required_keys,
        "provided_inputs": sorted(provided_set),
        "missing_inputs": missing,
        "ready": len(missing) == 0,
    }


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

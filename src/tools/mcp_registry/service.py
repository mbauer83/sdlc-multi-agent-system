from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import anyio  # type: ignore[import-not-found]

from src.tools.mcp_registry.config import agents_root_path
from src.tools.mcp_registry.markdown_utils import (
    extract_h3_subsection,
    extract_skill_runtime_sections,
    filter_frontmatter,
    normalize_newlines,
    parse_frontmatter,
    parse_inputs_required_table,
    sha256_text,
)

AGENT_RUNTIME_FRONTMATTER_KEYS: tuple[str, ...] = (
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

SKILL_RUNTIME_FRONTMATTER_KEYS: tuple[str, ...] = (
    "skill-id",
    "agent",
    "name",
    "invoke-when",
    "trigger-phases",
    "primary-outputs",
    "complexity-class",
)


async def read_text(path: Path) -> str:
    async with await anyio.open_file(path, "r", encoding="utf-8") as file:
        return await file.read()


def read_text_sync(path: Path) -> str:
    return anyio.run(read_text, path)


def agent_dir(root: Path, agent_id: str) -> Path:
    clean_agent_id = agent_id.strip().strip("/\\")
    if clean_agent_id in {"", ".", ".."} or "/" in clean_agent_id or "\\" in clean_agent_id:
        raise ValueError("invalid agent_id")
    return root / clean_agent_id


def skill_path(root: Path, agent_id: str, skill_id: str) -> Path:
    clean_skill_id = skill_id.strip().strip("/\\")
    if clean_skill_id in {"", ".", ".."} or "/" in clean_skill_id or "\\" in clean_skill_id:
        raise ValueError("invalid skill_id")
    return agent_dir(root, agent_id) / "skills" / f"{clean_skill_id}.md"


def list_agents(*, agents_root: str | None) -> list[str]:
    root = agents_root_path(agents_root)
    if not root.exists() or not root.is_dir():
        return []

    agent_ids: list[str] = []
    for child in sorted(root.iterdir(), key=lambda path: path.name):
        if child.is_dir() and (child / "AGENT.md").is_file():
            agent_ids.append(child.name)
    return agent_ids


def list_agent_skills(agent_id: str, *, agents_root: str | None) -> list[str]:
    root = agents_root_path(agents_root)
    skills_dir = agent_dir(root, agent_id) / "skills"
    if not skills_dir.is_dir():
        return []

    skill_ids: list[str] = []
    for path in sorted(skills_dir.iterdir(), key=lambda x: x.name):
        if path.is_file() and path.suffix.lower() == ".md":
            skill_ids.append(path.stem)
    return skill_ids


def load_agent_identity(
    agent_id: str,
    *,
    agents_root: str | None,
    include_full_frontmatter: bool,
) -> dict[str, object] | None:
    root = agents_root_path(agents_root)
    path = agent_dir(root, agent_id) / "AGENT.md"
    if not path.is_file():
        return None

    raw = read_text_sync(path)
    parsed = parse_frontmatter(raw)
    system_prompt = parsed.frontmatter.get("system-prompt-identity")
    if not isinstance(system_prompt, str):
        system_prompt = None

    runtime_behavioral_stance = extract_h3_subsection(
        parsed.content,
        h2_title="11. Personality & Behavioral Stance",
        h3_title="Runtime Behavioral Stance",
    )
    runtime_frontmatter = filter_frontmatter(parsed.frontmatter, AGENT_RUNTIME_FRONTMATTER_KEYS)

    return {
        "agent_id": agent_id,
        "path": str(path),
        "frontmatter": parsed.frontmatter if include_full_frontmatter else runtime_frontmatter,
        "runtime_frontmatter": runtime_frontmatter,
        "system_prompt_identity": system_prompt,
        "runtime_behavioral_stance": runtime_behavioral_stance,
    }


def list_skill_triggers(*, agent_id: str | None, agents_root: str | None) -> list[dict[str, object]]:
    root = agents_root_path(agents_root)
    agents = [agent_id] if isinstance(agent_id, str) and agent_id.strip() else list_agents(agents_root=str(root))
    rows: list[dict[str, object]] = []

    for current_agent_id in agents:
        for current_skill_id in list_agent_skills(current_agent_id, agents_root=str(root)):
            path = skill_path(root, current_agent_id, current_skill_id)
            if not path.is_file():
                continue

            parsed = parse_frontmatter(read_text_sync(path))
            frontmatter = parsed.frontmatter
            rows.append(
                {
                    "agent_id": current_agent_id,
                    "skill_id": current_skill_id,
                    "path": str(path),
                    "trigger_phases": _as_list(frontmatter.get("trigger-phases")),
                    "trigger_conditions": _as_list(frontmatter.get("trigger-conditions")),
                    "invoke_when": _as_optional_string(frontmatter.get("invoke-when")),
                    "entry_points": _as_list(frontmatter.get("entry-points")),
                }
            )

    rows.sort(key=lambda row: (str(row["agent_id"]), str(row["skill_id"])))
    return rows


def get_skill_details(
    agent_id: str,
    skill_id: str,
    *,
    agents_root: str | None,
    include_full_frontmatter: bool,
) -> dict[str, object] | None:
    root = agents_root_path(agents_root)
    path = skill_path(root, agent_id, skill_id)
    if not path.is_file():
        return None

    parsed = parse_frontmatter(read_text_sync(path))
    runtime_sections = extract_skill_runtime_sections(parsed.content)
    procedure = runtime_sections.get("Procedure")
    procedure_norm = normalize_newlines(procedure) if procedure is not None else None
    procedure_hash = sha256_text(procedure_norm) if isinstance(procedure_norm, str) else None
    runtime_frontmatter = filter_frontmatter(parsed.frontmatter, SKILL_RUNTIME_FRONTMATTER_KEYS)
    runtime_blob = "\n\n".join(f"## {name}\n{body.rstrip()}" for name, body in runtime_sections.items())
    runtime_sha256 = sha256_text(runtime_blob) if runtime_blob else None

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


def check_skill_readiness(
    skill_id: str,
    provided_inputs: list[str],
    *,
    agents_root: str | None,
) -> dict[str, object]:
    root = agents_root_path(agents_root)
    candidates: list[tuple[str, Path]] = []

    for aid in list_agents(agents_root=str(root)):
        path = skill_path(root, aid, skill_id)
        if path.is_file():
            candidates.append((aid, path))

    if not candidates:
        return {"skill_id": skill_id, "found": False, "reason": "not_found", "candidates": []}

    if len(candidates) > 1:
        return {
            "skill_id": skill_id,
            "found": False,
            "reason": "ambiguous",
            "candidates": [aid for aid, _ in candidates],
        }

    agent_id, path = candidates[0]
    parsed = parse_frontmatter(read_text_sync(path))
    required_keys, _rows = parse_inputs_required_table(parsed.content)
    provided_set = {key.strip() for key in provided_inputs if isinstance(key, str) and key.strip()}
    missing = [key for key in required_keys if key not in provided_set]

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


def normalize_incoming_tool_name(tool_name: str, *, known_tools: set[str]) -> str:
    if tool_name in known_tools:
        return tool_name
    for separator in ("-", ":", ".", "/"):
        if separator in tool_name:
            candidate = tool_name.rsplit(separator, 1)[-1]
            if candidate in known_tools:
                return candidate
    return tool_name


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def _as_optional_string(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip()

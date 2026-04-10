"""
PydanticAI diagram tools for SDLC agents.

Provides agent-accessible tools for diagram macro generation, validation,
rendering, and ER content assembly. Only SA and SwA agents register these
tools (they own the diagram-catalog/).

Implements the AIF-005 DiagramToolsPort interface as PydanticAI tool functions.
Governed by framework/diagram-conventions.md §5 (D1–D5 protocol) and
framework/agent-runtime-spec.md §6.

Non-SA/SwA agents needing a §display ###<language> block in an entity they do
not own should emit a ``diagram.display-spec-request`` handoff event rather
than calling these tools directly — governed by diagram-conventions.md §5 (D5).
"""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic_ai import Agent, RunContext

from src.agents.deps import AgentDeps
from src.agents.tools._diagram_io import (
    read_er_block,
    resolve_arch_repo,
    resolve_puml_path,
    run_plantuml,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_diagram_tools(agent: Agent) -> None:
    """
    Register agent-facing diagram tools for SA and SwA.

    Note: regenerate_macros is NOT registered here — it is triggered
    automatically by write_artifact when an entity with a §display ###archimate
    block is written (per CLAUDE.md rule #16 and AIF-005 spec). Agents never
    need to call it explicitly.
    """
    agent.tool(generate_er_content)
    agent.tool(generate_er_relations)
    agent.tool(validate_diagram)
    agent.tool(render_diagram)


# ---------------------------------------------------------------------------
# Tool: regenerate_macros
# ---------------------------------------------------------------------------


def regenerate_macros(
    ctx: RunContext[AgentDeps],
    repo_path: str | None = None,
) -> str:
    """
    Regenerate the _macros.puml ArchiMate macro library from entity §display
    ###archimate blocks in the architecture repository.

    repo_path: optional path to the architecture repository root. Defaults to
               the engagement architecture-repository.

    Returns a summary string (macro count or error message). Call this after
    creating or updating any entity with a §display ###archimate block, and
    before rendering ArchiMate diagrams that include !include ../_macros.puml.
    """
    try:
        from src.tools.generate_macros import generate_macros as _gen
    except ImportError as exc:
        return f"[Error] generate_macros module unavailable: {exc}"

    root = resolve_arch_repo(ctx, repo_path)
    if root is None:
        return "[Error] Could not locate architecture-repository. Pass repo_path explicitly."

    try:
        out_path = _gen(root)
        content = out_path.read_text(encoding="utf-8")
        macro_count = content.count("!define DECL_")
        rel = out_path.relative_to(root)
        return f"Regenerated {rel} — {macro_count} ArchiMate macro(s) written."
    except Exception as exc:  # noqa: BLE001
        return f"[Error] regenerate_macros failed: {exc}"


# ---------------------------------------------------------------------------
# Tool: generate_er_content
# ---------------------------------------------------------------------------


def generate_er_content(
    ctx: RunContext[AgentDeps],
    entity_ids: list[str],
) -> str:
    """
    Read the §display ###er blocks from the given entity files and return
    the PlantUML class declarations for pasting into an ER diagram.

    entity_ids: list of artifact IDs (e.g. ["DOB-001", "DOB-002"]).

    Returns concatenated PUML class declarations, or a warning line for each
    entity whose §display ###er block is missing.
    """
    root = resolve_arch_repo(ctx, None)
    if root is None:
        return "[Error] Could not locate architecture-repository."

    lines: list[str] = []
    for eid in entity_ids:
        block = read_er_block(root, eid)
        lines.append(block.strip() if block else f"' [Warning] No §display ###er block for {eid}")
    return "\n".join(lines) if lines else "(no content)"


# ---------------------------------------------------------------------------
# Tool: generate_er_relations
# ---------------------------------------------------------------------------


def generate_er_relations(
    ctx: RunContext[AgentDeps],
    connection_ids: list[str],
) -> str:
    """
    Read the §display ###er blocks from the given connection files and return
    the PlantUML cardinality/relation lines for an ER diagram.

    connection_ids: list of connection artifact IDs.
    """
    root = resolve_arch_repo(ctx, None)
    if root is None:
        return "[Error] Could not locate architecture-repository."

    lines: list[str] = []
    for cid in connection_ids:
        block = read_er_block(root, cid)
        lines.append(block.strip() if block else f"' [Warning] No §display ###er block for {cid}")
    return "\n".join(lines) if lines else "(no relations)"


# ---------------------------------------------------------------------------
# Tool: validate_diagram
# ---------------------------------------------------------------------------


def validate_diagram(
    ctx: RunContext[AgentDeps],
    puml_path: str,
) -> str:
    """
    Validate a PUML diagram file against the ModelRegistry:
    - All PUML aliases must resolve to ModelRegistry entries.
    - Each resolved entity must have the appropriate §display ###<language> block.
    - ArchiMate/use-case diagrams must include !include _macros.puml.

    puml_path: path to the .puml file, relative to the engagement directory or
               as an absolute path.

    Returns "Valid — N checks passed." or a list of violations.
    """
    root = resolve_arch_repo(ctx, None)
    if root is None:
        return "[Error] Could not locate architecture-repository."
    resolved = resolve_puml_path(ctx, puml_path)
    if resolved is None or not resolved.exists():
        return f"[Error] PUML file not found: {puml_path}"

    try:
        from src.common.model_verifier import ModelRegistry, ModelVerifier

        registry = ModelRegistry(root)
        result = ModelVerifier(registry).verify_diagram_file(resolved)

        if result.valid:
            return f"Valid — {resolved.name}: no issues detected."

        errors = [
            (f"[{i.code}] {i.message} (line {i.location})" if i.location else f"[{i.code}] {i.message}")
            for i in result.issues
            if i.severity in ("error", "critical")
        ]
        warnings = [f"[{i.code}] {i.message}" for i in result.issues if i.severity == "warning"]
        parts: list[str] = []
        if errors:
            parts.append(f"Errors ({len(errors)}):\n" + "\n".join(f"  {e}" for e in errors))
        if warnings:
            parts.append(f"Warnings ({len(warnings)}):\n" + "\n".join(f"  {w}" for w in warnings))
        return "\n".join(parts) or "Issues detected (no details)."
    except Exception as exc:  # noqa: BLE001
        return f"[Error] Validation failed: {exc}"


# ---------------------------------------------------------------------------
# Tool: render_diagram
# ---------------------------------------------------------------------------


def render_diagram(
    ctx: RunContext[AgentDeps],
    puml_path: str,
) -> str:
    """
    Render a PUML diagram to SVG using the local plantuml CLI.

    puml_path: path to the .puml file (relative to engagement directory or
               absolute).

    SVG is written to the sibling diagram-catalog/rendered/ directory (never
    into diagram-catalog/diagrams/rendered/). Only call at sprint boundary or
    when explicitly requested by PM.

    Returns the path to the rendered SVG, or an error/skip string if plantuml
    is not installed or rendering fails.
    """
    resolved = resolve_puml_path(ctx, puml_path)
    if resolved is None or not resolved.exists():
        return f"[Error] PUML file not found: {puml_path}"

    # Output → diagram-catalog/rendered/ (not diagrams/rendered/)
    diagram_catalog = resolved.parent.parent  # diagram-catalog/
    rendered_dir = diagram_catalog / "rendered"
    return run_plantuml(resolved, rendered_dir)

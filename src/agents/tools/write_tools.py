"""
write_artifact: path-constrained artifact write tool.

Each agent is given a write tool pre-bound to its allowed paths.
Writes outside designated paths raise RepositoryBoundaryError (→ ALG-007).

Per framework/agent-runtime-spec.md §6 and CLAUDE.md authoring rule #8:
  "No agent writes outside its designated engagement work-repository path."

Factory function build_write_tool(agent_id, allowed_paths) returns a tool
closure that agents register. Paths are checked at call time, not build time.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps

log = logging.getLogger(__name__)


class RepositoryBoundaryError(PermissionError):
    """Raised when an agent tries to write outside its designated paths."""


# Canonical allowed roots per agent role (relative to engagement work-repositories/)
_AGENT_ALLOWED_DIRS: dict[str, list[str]] = {
    "SA":   ["architecture-repository/model-entities/motivation",
             "architecture-repository/model-entities/strategy",
             "architecture-repository/model-entities/business",
             "architecture-repository/connections",
             "architecture-repository/diagram-catalog",
             "architecture-repository/decisions",
             "architecture-repository/overview"],
    "SwA":  ["architecture-repository/model-entities/application",
             "architecture-repository/model-entities/implementation",
             "architecture-repository/connections",
             "architecture-repository/diagram-catalog",
             "technology-repository"],
    "PM":   ["project-repository"],
    "PO":   ["project-repository/requirements"],
    "DE":   ["delivery-repository"],
    "DO":   ["devops-repository", "delivery-repository"],
    "QA":   ["qa-repository"],
    "SMM":  ["project-repository/market-analysis"],
    "CSCO": ["safety-repository"],
}


def build_write_tool(agent_id: str) -> Any:
    """
    Return a PydanticAI tool function pre-bound to agent_id's allowed paths.
    Register the returned function with agent.tool().
    """
    allowed_dirs = _AGENT_ALLOWED_DIRS.get(agent_id, [])

    def write_artifact(
        ctx: RunContext[AgentDeps],
        relative_path: str,
        content: str,
        artifact_id: str | None = None,
        version: str = "0.1.0",
    ) -> str:
        """
        Write a file to a work-repository.  Both relative_path AND content are
        REQUIRED in every call — the tool creates or overwrites the file in one shot.

        relative_path: path relative to work-repositories/ (e.g.
                       "architecture-repository/model-entities/motivation/STK-001.friendly-name.md").
                       Must be a relative path (no leading slash).
        content:       COMPLETE file content as a string (markdown with YAML frontmatter).
                       Must be provided; omitting it is an error.
        artifact_id:   optional artifact-id; if provided, emits an artifact event.
        version:       artifact version string (default "0.1.0").
        Returns the absolute path of the written file.
        """
        work_repos = ctx.deps.work_repos_path
        target = (work_repos / relative_path).resolve()
        log.debug("write_artifact: target=%s allowed=%s", target, allowed_dirs)

        # Boundary check — return error string so the model can self-correct
        if not _is_allowed(target, work_repos, allowed_dirs):
            log.warning("write_artifact: boundary violation — path=%s not in allowed_dirs=%s", target, allowed_dirs)
            _emit_boundary_violation(ctx, str(target))
            return (
                f"[BoundaryError] Agent '{agent_id}' is not permitted to write to '{relative_path}'. "
                f"Allowed roots (relative to work-repositories/): {allowed_dirs}. "
                "Use one of the listed subdirectories as the prefix for relative_path."
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        target.write_text(content, encoding="utf-8")

        # Auto-regenerate _macros.puml when an entity with an archimate display block
        # is written — keeps the macro library in sync transparently (per AIF-005 spec).
        if _has_archimate_display(content):
            _regenerate_macros_for(ctx)

        # Emit artifact event — auto-derive artifact_id from filename if not provided
        effective_id = artifact_id or _derive_artifact_id(target)
        if effective_id:
            _emit_artifact_event(ctx, effective_id, version, str(target), existed)

        return str(target)

    write_artifact.__name__ = f"write_artifact_{agent_id.lower()}"
    return write_artifact


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_ARCHIMATE_DISPLAY_RE = __import__("re").compile(
    r"<!--\s*§display\s*-->.*###\s*archimate", __import__("re").IGNORECASE | __import__("re").DOTALL
)


def _has_archimate_display(content: str) -> bool:
    """Return True if content contains a §display ###archimate block."""
    return bool(_ARCHIMATE_DISPLAY_RE.search(content))


def _regenerate_macros_for(ctx: RunContext[AgentDeps]) -> None:
    """
    Regenerate _macros.puml for the engagement's architecture repository.
    Best-effort: failures are logged but never propagate to the caller.
    """
    try:
        from src.tools.generate_macros import generate_macros

        arch_repo = ctx.deps.work_repos_path / "architecture-repository"
        if arch_repo.is_dir():
            generate_macros(arch_repo)
    except Exception:  # noqa: BLE001
        log.debug("_regenerate_macros_for: skipped (generate_macros unavailable or failed)")


def _derive_artifact_id(path: Path) -> str | None:
    """Extract artifact-id from a filename like STK-001.friendly-name.md → 'STK-001'."""
    import re
    stem_prefix = path.stem.split(".")[0]
    if re.match(r"^[A-Z]+-\d{3}$", stem_prefix):
        return stem_prefix
    return None


def _is_allowed(target: Path, work_repos: Path, allowed_dirs: list[str]) -> bool:
    for allowed in allowed_dirs:
        allowed_path = (work_repos / allowed).resolve()
        try:
            target.relative_to(allowed_path)
            return True
        except ValueError:
            pass
    return False


def _emit_artifact_event(
    ctx: RunContext[AgentDeps],
    artifact_id: str,
    version: str,
    path: str,
    existed: bool,
) -> None:
    from src.events.models.artifact import ArtifactBaselinedPayload, ArtifactDraftedPayload

    is_baselined = not version.startswith("0.")
    try:
        if is_baselined:
            payload: Any = ArtifactBaselinedPayload(
                artifact_id=artifact_id, version=version, path=path
            )
            ctx.deps.event_store.append(
                payload, actor=ctx.deps.agent_id, correlation_id=artifact_id
            )
        elif not existed:
            payload = ArtifactDraftedPayload(
                artifact_id=artifact_id,
                artifact_type=artifact_id.split("-")[0] if "-" in artifact_id else "unknown",
                version=version,
                path=path,
            )
            ctx.deps.event_store.append(
                payload, actor=ctx.deps.agent_id, correlation_id=artifact_id
            )
    except Exception:  # noqa: BLE001
        pass  # event emission is best-effort; the file write already succeeded


def _emit_boundary_violation(ctx: RunContext[AgentDeps], target_path: str) -> None:
    """Emit an algedonic signal for a boundary violation attempt."""
    try:
        from src.events.models.algedonic import AlgedonicRaisedPayload
        import uuid

        sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"
        payload = AlgedonicRaisedPayload(
            signal_id=sig_id,
            trigger_id="ALG-007",
            category="GV",
            severity="S2",
        )
        ctx.deps.event_store.append(
            payload, actor=ctx.deps.agent_id, correlation_id=sig_id
        )
    except Exception:  # noqa: BLE001
        pass

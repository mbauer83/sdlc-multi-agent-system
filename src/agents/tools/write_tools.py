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

from pathlib import Path
from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps


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
        Write content to a work-repository file.

        relative_path: path relative to work-repositories/ (e.g.
                       "architecture-repository/model-entities/motivation/STK-001.md")
        content:       full file content (markdown)
        artifact_id:   if provided, emits artifact.drafted or artifact.baselined event
        version:       artifact version string
        Returns the absolute path of the written file.
        """
        work_repos = ctx.deps.work_repos_path
        target = (work_repos / relative_path).resolve()

        # Boundary check
        if not _is_allowed(target, work_repos, allowed_dirs):
            _emit_boundary_violation(ctx, str(target))
            raise RepositoryBoundaryError(
                f"Agent '{agent_id}' is not permitted to write to '{relative_path}'. "
                f"Allowed roots: {allowed_dirs}"
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        target.write_text(content, encoding="utf-8")

        # Emit artifact event
        if artifact_id:
            _emit_artifact_event(ctx, artifact_id, version, str(target), existed)

        return str(target)

    write_artifact.__name__ = f"write_artifact_{agent_id.lower()}"
    return write_artifact


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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

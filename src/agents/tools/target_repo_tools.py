"""
Target repository tools — role-scoped access to multi-repo target repositories.

Thin wrappers over TargetRepoManager that enforce per-role access control and
surface target-repo operations as PydanticAI tool functions.

Access policy (non-negotiable):
  DE + DO → read-write (via git worktree for write operations)
  All other roles → read-only

Governed by:
  src/sources/target_repo.py (TargetRepoManager)
  specs/IMPLEMENTATION_PLAN.md §5b / §5d
  framework/agent-runtime-spec.md §6 (target_repo_tools group)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps
from src.sources.target_repo import (
    TargetRepoManager,
    TargetRepoAccessDeniedError,
    TargetRepoNotFoundError,
)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def list_target_repos(ctx: RunContext[AgentDeps]) -> list[dict[str, Any]]:
    """
    List all target repositories registered for this engagement.

    Returns id, label, role, domain, primary flag, and clone path for each repo.
    Available to all agent roles.
    """
    mgr = _manager(ctx)
    results: list[dict[str, Any]] = []
    for repo_id in mgr.get_repo_ids():
        record = mgr.get_record(repo_id)
        results.append({
            "id": record.id,
            "label": record.label,
            "role": record.role,
            "domain": record.domain,
            "primary": record.primary,
            "clone_path": str(mgr.get_clone_path(repo_id)),
            "access": mgr.check_access(repo_id, ctx.deps.agent_id),
        })
    return results


def read_target_repo(
    ctx: RunContext[AgentDeps],
    path: str,
    repo_id: str | None = None,
) -> str:
    """
    Read a file from a target repository.

    path:    Path relative to the repository root (e.g. "src/main.py").
    repo_id: Target repo identifier; None → primary repo.

    Returns the file content as text, or an error message if the file does
    not exist.  Available to all agent roles (read access is universal).
    """
    mgr = _manager(ctx)
    try:
        clone_path = mgr.get_clone_path(repo_id)
    except TargetRepoNotFoundError as exc:
        return f"[TargetRepoNotFoundError: {exc}]"

    target = clone_path / path
    if not target.exists():
        return f"[File not found: {path} in repo '{repo_id or 'primary'}']"
    if not target.is_file():
        return f"[Not a file: {path}]"

    return target.read_text(errors="replace")


def scan_target_repo(
    ctx: RunContext[AgentDeps],
    repo_id: str | None = None,
    glob_pattern: str = "**/*",
    max_files: int = 200,
) -> list[str]:
    """
    List files in a target repository matching a glob pattern.

    Used during Discovery Layer 4 to enumerate target repo contents without
    reading individual files.  Returns relative paths (sorted).

    repo_id:      Target repo identifier; None → primary repo.
    glob_pattern: Glob to filter results (e.g. "**/*.py", "src/**/*.ts").
    max_files:    Maximum number of paths to return.
    """
    mgr = _manager(ctx)
    try:
        clone_path = mgr.get_clone_path(repo_id)
    except TargetRepoNotFoundError as exc:
        return [f"[TargetRepoNotFoundError: {exc}]"]

    if not clone_path.exists():
        return [f"[Repo not cloned: '{repo_id or 'primary'}'. Call clone_target_repo first.]"]

    paths = sorted(
        str(p.relative_to(clone_path))
        for p in clone_path.glob(glob_pattern)
        if p.is_file() and ".git" not in p.parts
    )
    return paths[:max_files]


def write_target_repo(
    ctx: RunContext[AgentDeps],
    path: str,
    content: str,
    repo_id: str | None = None,
) -> str:
    """
    Write a file to a target repository worktree.

    Only DE and DO may call this tool.  All writes go to the agent's dedicated
    git worktree (not the main clone) to prevent cross-contamination.

    path:    Path relative to the worktree root.
    content: File content to write.
    repo_id: Target repo identifier; None → primary repo.

    Returns the absolute path written, or an error message on failure.
    """
    mgr = _manager(ctx)
    agent_role = ctx.deps.agent_id

    try:
        mgr.assert_write_access(repo_id or (mgr.get_primary_id() or ""), agent_role)
    except (TargetRepoAccessDeniedError, TargetRepoNotFoundError) as exc:
        return f"[AccessDenied: {exc}]"

    # Writes go to the worktree, not the clone directly
    sprint_branch = f"feature/{agent_role.lower()}-{ctx.deps.engagement_id}"
    try:
        wt_path = mgr.get_worktree_path(repo_id or (mgr.get_primary_id() or ""), sprint_branch)
    except TargetRepoNotFoundError as exc:
        return f"[TargetRepoNotFoundError: {exc}]"

    if not wt_path.exists():
        return (
            f"[Worktree not initialised for branch '{sprint_branch}'. "
            "Ask the PM to set up the worktree before writing files.]"
        )

    target = wt_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return str(target)


# ---------------------------------------------------------------------------
# Tool registration helpers
# ---------------------------------------------------------------------------

def register_read_only_target_repo_tools(agent: Any) -> None:
    """Register read-only target-repo tools for SA, SwA, QA, PO, SMM, CSCO roles."""
    for fn in (list_target_repos, read_target_repo, scan_target_repo):
        agent.tool(fn)


def register_readwrite_target_repo_tools(agent: Any) -> None:
    """Register read-write target-repo tools for DE and DO roles."""
    for fn in (list_target_repos, read_target_repo, scan_target_repo, write_target_repo):
        agent.tool(fn)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _manager(ctx: RunContext[AgentDeps]) -> TargetRepoManager:
    """Build a TargetRepoManager from the AgentDeps context."""
    return TargetRepoManager.from_config(
        engagement_id=ctx.deps.engagement_id,
        repo_root=ctx.deps.engagement_path.parent.parent,  # engagements/<id>/ → repo root
    )

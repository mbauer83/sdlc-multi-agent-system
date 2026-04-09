"""
TargetRepoManager — multi-repo aware clone and worktree manager.

Reads the engagement's target-repositories config and provides:
  - Path resolution for clones at engagements/<id>/target-repos/<repo-id>/
  - Per-role access control (DE + DO get read-write; all others read-only)
  - Git worktree creation for agent-isolated writes (non-negotiable for DE/DO)
  - Backward-compatible single-repo support (id="default")

Git worktrees are the non-negotiable isolation mechanism for concurrent agent
writes.  Each agent (DE, DO) gets its own worktree per sprint so code changes
never cross-contaminate.  Worktrees are merged back at sprint close.

Governed by specs/IMPLEMENTATION_PLAN.md §5d.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Literal

import yaml


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TargetRepoNotFoundError(KeyError):
    """Raised when repo_id is not registered in the engagement config."""


class TargetRepoAccessDeniedError(PermissionError):
    """Raised when an agent attempts a write without read-write access."""


class GitWorktreeError(RuntimeError):
    """Raised when git worktree creation fails."""


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

AccessLevel = Literal["read-write", "read-only", "none"]

# Only DE and DO may write to target repositories
_READ_WRITE_ROLES: frozenset[str] = frozenset({"DE", "DO"})


# ---------------------------------------------------------------------------
# RepoRecord
# ---------------------------------------------------------------------------

class RepoRecord:
    """Parsed representation of one entry in target-repositories list."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.id: str = data["id"]
        self.label: str = data.get("label", self.id)
        self.role: str = data.get("role", "monolith")
        self.domain: str = data.get("domain", "")
        self.primary: bool = bool(data.get("primary", False))
        self.url: str | None = data.get("url")

    def __repr__(self) -> str:
        return f"RepoRecord(id={self.id!r}, primary={self.primary})"


# ---------------------------------------------------------------------------
# TargetRepoManager
# ---------------------------------------------------------------------------

class TargetRepoManager:
    """
    Multi-repo aware target repository manager.

    Parameters
    ----------
    engagement_id:
        Engagement identifier, e.g. "ENG-001".
    repo_root:
        Framework repository root.  Clone paths live at
        ``repo_root / "engagements" / engagement_id / "target-repos" / repo_id``.
    repos:
        Parsed list of RepoRecord instances (call ``from_config`` instead of
        passing this directly in production code).
    """

    def __init__(
        self,
        engagement_id: str,
        repo_root: Path,
        repos: list[RepoRecord],
    ) -> None:
        self._engagement_id = engagement_id
        self._repo_root = repo_root
        self._repos: dict[str, RepoRecord] = {r.id: r for r in repos}
        self._base_path = (
            repo_root / "engagements" / engagement_id / "target-repos"
        )

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_config(
        cls,
        engagement_id: str,
        repo_root: Path,
        config_path: Path | None = None,
    ) -> "TargetRepoManager":
        """
        Build from engagements-config.yaml.

        Supports both multi-repo (target-repositories list) and backward-
        compatible single-repo (target-repository singular) formats.
        """
        config_path = config_path or repo_root / "engagements-config.yaml"
        repos: list[RepoRecord] = []

        if config_path.exists():
            raw: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
            eng_block = raw.get("engagements", {})
            active: list[dict] = (
                eng_block.get("active-engagements", [])
                if isinstance(eng_block, dict)
                else []
            )
            for eng in active:
                if not isinstance(eng, dict) or eng.get("id") != engagement_id:
                    continue

                multi = eng.get("target-repositories", [])
                if multi:
                    repos = [RepoRecord(r) for r in multi]
                elif single := eng.get("target-repository"):
                    repos = [RepoRecord({**single, "id": "default", "primary": True})]
                break  # engagement found

        return cls(engagement_id=engagement_id, repo_root=repo_root, repos=repos)

    # ------------------------------------------------------------------
    # Registry queries
    # ------------------------------------------------------------------

    def get_repo_ids(self) -> list[str]:
        """Return all registered repository IDs in insertion order."""
        return list(self._repos)

    def get_primary_id(self) -> str | None:
        """Return the primary repo ID, or None if no repos are configured."""
        for record in self._repos.values():
            if record.primary:
                return record.id
        # Fall back to first repo if none is flagged primary
        if self._repos:
            return next(iter(self._repos))
        return None

    def get_record(self, repo_id: str) -> RepoRecord:
        """Return the RepoRecord for *repo_id*, raising TargetRepoNotFoundError if absent."""
        if repo_id not in self._repos:
            raise TargetRepoNotFoundError(
                f"Repository '{repo_id}' is not registered in engagement "
                f"'{self._engagement_id}'. Registered: {list(self._repos)}"
            )
        return self._repos[repo_id]

    # ------------------------------------------------------------------
    # Path resolution
    # ------------------------------------------------------------------

    def get_clone_path(self, repo_id: str | None = None) -> Path:
        """
        Resolve the local clone path for *repo_id*.

        repo_id=None → primary repo (or raises if no repos configured).
        """
        resolved = repo_id if repo_id is not None else self.get_primary_id()
        if resolved is None:
            raise TargetRepoNotFoundError(
                f"No repos configured for engagement '{self._engagement_id}'"
            )
        if resolved not in self._repos:
            raise TargetRepoNotFoundError(
                f"Repository '{resolved}' is not registered in engagement "
                f"'{self._engagement_id}'. Registered: {list(self._repos)}"
            )
        return self._base_path / resolved

    def get_worktree_path(self, repo_id: str, branch_name: str) -> Path:
        """
        Return the expected path for a git worktree.

        Convention: ``<base_path>/<repo_id>-wt-<sanitised-branch>``.
        The worktree is NOT created; call create_worktree() for that.
        """
        safe_branch = branch_name.replace("/", "-").replace("\\", "-")
        return self._base_path / f"{repo_id}-wt-{safe_branch}"

    # ------------------------------------------------------------------
    # Access control
    # ------------------------------------------------------------------

    def check_access(self, repo_id: str, agent_role: str) -> AccessLevel:
        """
        Return the access level for *agent_role* on *repo_id*.

        DE and DO → read-write.
        All other roles → read-only.
        Unknown repo → "none".
        """
        if repo_id not in self._repos:
            return "none"
        if agent_role in _READ_WRITE_ROLES:
            return "read-write"
        return "read-only"

    def assert_write_access(self, repo_id: str, agent_role: str) -> None:
        """Raise TargetRepoAccessDeniedError unless agent_role has read-write access."""
        level = self.check_access(repo_id, agent_role)
        if level != "read-write":
            raise TargetRepoAccessDeniedError(
                f"Agent role '{agent_role}' does not have write access to "
                f"repo '{repo_id}'. Access level: '{level}'."
            )

    # ------------------------------------------------------------------
    # Clone management
    # ------------------------------------------------------------------

    def clone_or_update(self, repo_id: str) -> Path:
        """
        Clone or fetch a target repository.

        If the clone path already exists (has a .git dir), runs ``git fetch``.
        Otherwise runs ``git clone`` using the URL from the repo record.
        Returns the clone path.

        Raises:
            TargetRepoNotFoundError: if repo_id is not registered.
            GitWorktreeError: if git clone / fetch fails.
        """
        record = self.get_record(repo_id)
        clone_path = self.get_clone_path(repo_id)

        if (clone_path / ".git").exists():
            self._git(["fetch", "--prune"], cwd=clone_path)
        else:
            if record.url is None:
                raise GitWorktreeError(
                    f"Cannot clone repo '{repo_id}': no URL configured."
                )
            clone_path.parent.mkdir(parents=True, exist_ok=True)
            self._git(["clone", record.url, str(clone_path)])

        return clone_path

    # ------------------------------------------------------------------
    # Worktree management
    # ------------------------------------------------------------------

    def create_worktree(self, repo_id: str, branch_name: str) -> Path:
        """
        Create a git worktree for isolated agent writes.

        The worktree is placed at ``get_worktree_path(repo_id, branch_name)``.
        If the worktree already exists (idempotent re-entry), returns the path.

        The clone directory at ``get_clone_path(repo_id)`` must exist and be a
        valid git repository; call ``clone_or_update()`` first if needed.

        Raises:
            TargetRepoNotFoundError: if repo_id is not registered.
            GitWorktreeError: if git worktree add fails.
        """
        self.get_record(repo_id)  # validates repo_id
        clone_path = self.get_clone_path(repo_id)
        wt_path = self.get_worktree_path(repo_id, branch_name)

        if wt_path.exists():
            return wt_path  # idempotent

        wt_path.parent.mkdir(parents=True, exist_ok=True)
        self._git(
            ["worktree", "add", "-b", branch_name, str(wt_path)],
            cwd=clone_path,
        )
        return wt_path

    def remove_worktree(self, repo_id: str, branch_name: str, *, force: bool = False) -> None:
        """
        Remove a git worktree after sprint-close merge.

        Parameters
        ----------
        force:
            Pass ``--force`` to git worktree remove (required if the worktree
            has uncommitted changes that have already been merged by the caller).
        """
        self.get_record(repo_id)
        clone_path = self.get_clone_path(repo_id)
        wt_path = self.get_worktree_path(repo_id, branch_name)

        if not wt_path.exists():
            return  # already removed; idempotent

        cmd = ["worktree", "remove", str(wt_path)]
        if force:
            cmd.append("--force")
        self._git(cmd, cwd=clone_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _git(args: list[str], cwd: Path | None = None) -> str:
        """Run a git command; raise GitWorktreeError on non-zero exit."""
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise GitWorktreeError(
                f"git {' '.join(args)} failed:\n{result.stderr.strip()}"
            )
        return result.stdout.strip()

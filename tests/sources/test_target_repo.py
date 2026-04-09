"""BDD scenarios for TargetRepoManager.

Tests cover:
  - Config parsing (multi-repo, single-repo backward-compat, empty)
  - Path resolution (named repo, None → primary, unknown → error)
  - Access control (DE/DO → read-write; others → read-only; unknown → none)
  - Git worktree creation and isolation (neuralgic — safety-critical for
    concurrent agent writes)

Git worktree tests use real git repos initialised in tmp_path so we exercise
the actual subprocess path without network calls.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml
from pytest_bdd import given, parsers, scenarios, then, when

from src.sources.target_repo import (
    RepoRecord,
    TargetRepoManager,
    TargetRepoNotFoundError,
)

scenarios("features/target_repo.feature")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_config(repo_root: Path, engagement_id: str, repos: list[dict]) -> Path:
    """Write engagements-config.yaml with a multi-repo engagement."""
    cfg = {
        "engagements": {
            "active-engagements": [
                {
                    "id": engagement_id,
                    "entry-point": "EP-0",
                    "target-repositories": repos,
                }
            ]
        }
    }
    path = repo_root / "engagements-config.yaml"
    path.write_text(yaml.dump(cfg))
    return path


def _init_bare_git(path: Path) -> None:
    """Initialise a bare git repo at *path* (used as remote origin)."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--bare", str(path)], check=True, capture_output=True)


def _clone_bare(bare: Path, clone: Path) -> None:
    """Clone *bare* to *clone*."""
    clone.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", str(bare), str(clone)], check=True, capture_output=True)
    # Need at least one commit so branches can be created
    subprocess.run(["git", "-C", str(clone), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clone), "config", "user.name", "Test"], check=True, capture_output=True)
    (clone / "README.md").write_text("# test repo\n")
    subprocess.run(["git", "-C", str(clone), "add", "README.md"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clone), "commit", "-m", "init"], check=True, capture_output=True)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

ENGAGEMENT_ID = "ENG-TRM-TEST"


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse('a multi-repo engagement config with repos "{r0}" (primary), "{r1}", "{r2}"'),
    target_fixture="manager",
)
def multi_repo_config(repo_root: Path, r0: str, r1: str, r2: str) -> TargetRepoManager:
    _write_config(
        repo_root,
        ENGAGEMENT_ID,
        [
            {"id": r0, "label": r0, "role": "api-gateway", "domain": "core", "primary": True},
            {"id": r1, "label": r1, "role": "microfrontend", "domain": "ui", "primary": False},
            {"id": r2, "label": r2, "role": "microservice", "domain": "processing", "primary": False},
        ],
    )
    return TargetRepoManager.from_config(ENGAGEMENT_ID, repo_root)


@given("a single-repo engagement config", target_fixture="manager")
def single_repo_config(repo_root: Path) -> TargetRepoManager:
    cfg = {
        "engagements": {
            "active-engagements": [
                {
                    "id": ENGAGEMENT_ID,
                    "entry-point": "EP-0",
                    "target-repository": {
                        "label": "monolith",
                        "role": "monolith",
                        "domain": "all",
                        "url": "https://example.com/repo.git",
                    },
                }
            ]
        }
    }
    (repo_root / "engagements-config.yaml").write_text(yaml.dump(cfg))
    return TargetRepoManager.from_config(ENGAGEMENT_ID, repo_root)


@given("an empty engagement config", target_fixture="manager")
def empty_config(repo_root: Path) -> TargetRepoManager:
    cfg = {"engagements": {"active-engagements": [{"id": ENGAGEMENT_ID}]}}
    (repo_root / "engagements-config.yaml").write_text(yaml.dump(cfg))
    return TargetRepoManager.from_config(ENGAGEMENT_ID, repo_root)


@given('a real git repository cloned as "api"', target_fixture="manager_with_clone")
def real_git_repo(repo_root: Path) -> tuple[TargetRepoManager, Path]:
    # Build a bare "remote" and a local clone
    bare = repo_root / "bare-remote.git"
    _init_bare_git(bare)

    _write_config(
        repo_root,
        ENGAGEMENT_ID,
        [{"id": "api", "label": "API", "role": "api-gateway", "domain": "core",
          "primary": True, "url": str(bare)}],
    )
    manager = TargetRepoManager.from_config(ENGAGEMENT_ID, repo_root)
    clone_path = manager.get_clone_path("api")
    _clone_bare(bare, clone_path)
    return manager, clone_path


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("TargetRepoManager is initialised")
def already_initialised(manager: TargetRepoManager) -> None:
    pass  # manager created in given step


@pytest.fixture
def wt_paths() -> list[Path]:
    """Accumulator for worktree paths created within a single scenario."""
    return []


@when(parsers.parse('create_worktree("{repo_id}", "{branch}") is called'))
def create_worktree(
    manager_with_clone: tuple[TargetRepoManager, Path],
    repo_id: str,
    branch: str,
    wt_paths: list[Path],
) -> None:
    """Append the new worktree path to the shared accumulator fixture."""
    mgr, _ = manager_with_clone
    path = mgr.create_worktree(repo_id, branch)
    wt_paths.append(path)


# ---------------------------------------------------------------------------
# Then steps — registry queries
# ---------------------------------------------------------------------------


@then(parsers.parse('get_repo_ids() returns {expected}'))
def check_repo_ids(manager: TargetRepoManager, expected: str) -> None:
    import ast
    expected_list: list[str] = ast.literal_eval(expected)
    assert manager.get_repo_ids() == expected_list


@then(parsers.parse('get_primary_id() returns "{expected}"'))
def check_primary_id_str(manager: TargetRepoManager, expected: str) -> None:
    assert manager.get_primary_id() == expected


@then("get_primary_id() returns None")
def check_primary_id_none(manager: TargetRepoManager) -> None:
    assert manager.get_primary_id() is None


# ---------------------------------------------------------------------------
# Then steps — path resolution
# ---------------------------------------------------------------------------


@then(parsers.parse('get_clone_path("{repo_id}") returns the path engagements/<id>/target-repos/{repo_id_expected}'))
def check_clone_path(
    manager: TargetRepoManager,
    repo_root: Path,
    repo_id: str,
    repo_id_expected: str,
) -> None:
    expected = repo_root / "engagements" / ENGAGEMENT_ID / "target-repos" / repo_id_expected
    assert manager.get_clone_path(repo_id) == expected


@then("get_clone_path(None) returns the path engagements/<id>/target-repos/api")
def check_clone_path_primary(manager: TargetRepoManager, repo_root: Path) -> None:
    expected = repo_root / "engagements" / ENGAGEMENT_ID / "target-repos" / "api"
    assert manager.get_clone_path(None) == expected


@then(parsers.parse('get_clone_path("{repo_id}") raises TargetRepoNotFoundError'))
def check_clone_path_error(manager: TargetRepoManager, repo_id: str) -> None:
    with pytest.raises(TargetRepoNotFoundError):
        manager.get_clone_path(repo_id)


# ---------------------------------------------------------------------------
# Then steps — access control
# ---------------------------------------------------------------------------


@then(parsers.parse('check_access("{repo_id}", "{role}") returns "{expected}"'))
def check_access_level(
    manager: TargetRepoManager, repo_id: str, role: str, expected: str
) -> None:
    assert manager.check_access(repo_id, role) == expected


# ---------------------------------------------------------------------------
# Then steps — worktree creation
# ---------------------------------------------------------------------------


@then("a worktree directory exists at the expected path")
def worktree_dir_exists(
    manager_with_clone: tuple[TargetRepoManager, Path],
    wt_paths: list[Path],
) -> None:
    mgr, _ = manager_with_clone
    assert len(wt_paths) >= 1
    wt_path = wt_paths[0]
    assert wt_path.exists(), f"Worktree directory does not exist: {wt_path}"
    assert wt_path.is_dir()


@then(parsers.parse('the worktree is on branch "{branch}"'))
def worktree_on_branch(
    manager_with_clone: tuple[TargetRepoManager, Path],
    wt_paths: list[Path],
    branch: str,
) -> None:
    wt_path = wt_paths[0]
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(wt_path),
        capture_output=True,
        text=True,
        check=True,
    )
    current_branch = result.stdout.strip()
    assert current_branch == branch, (
        f"Expected branch '{branch}', got '{current_branch}'"
    )


@then("the worktree path is separate from the main clone path")
def worktree_separate_from_clone(
    manager_with_clone: tuple[TargetRepoManager, Path],
    wt_paths: list[Path],
) -> None:
    mgr, _ = manager_with_clone
    clone_path = mgr.get_clone_path("api")
    wt_path = wt_paths[0]
    assert wt_path != clone_path
    assert clone_path not in wt_path.parents


@then("the two worktree paths are different directories")
def two_worktrees_are_different(wt_paths: list[Path]) -> None:
    assert len(wt_paths) == 2, f"Expected 2 worktree paths, got {len(wt_paths)}"
    assert wt_paths[0] != wt_paths[1], (
        f"Worktree paths must be different: {wt_paths[0]} == {wt_paths[1]}"
    )

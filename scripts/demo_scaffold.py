"""
ENG-DEMO engagement scaffolding.

Creates the full directory tree, target repository source files, engagement
profile, and engagements-config.yaml entry for the TaskFlow API demo scenario.

Public API
----------
scaffold_demo(repo_root, engagement_id, verbose) -> Path
teardown_demo(repo_root, engagement_id, verbose) -> None
"""

from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

from scripts._demo_taskflow import (
    ENGAGEMENT_DIRS,
    GITIGNORE,
    TASKFLOW_MAIN,
    TASKFLOW_MODELS,
    TASKFLOW_README,
    TASKFLOW_REQUIREMENTS,
    WORK_REPO_DIRS,
)

ENGAGEMENT_ID = "ENG-DEMO"
TARGET_REPO_ID = "taskflow-api"

# Inserted verbatim into engagements-config.yaml; removable by string replacement.
_CONFIG_BLOCK = """\

    - id: {eid}
      name: "TaskFlow API — Phase A Demo"
      path: engagements/{eid}/
      entry-point: EP-0
      cycle-level: capability
      status: active

      target-repository:
        url: null
        default-branch: main
        local-clone-path: engagements/{eid}/target-repos/taskflow-api/
        access:
          implementing-developer: read-write
          devops-platform-engineer: read-write
          qa-engineer: read-only
          solution-architect: read-only
          software-architect: read-only
          all-others: none
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scaffold_demo(
    repo_root: Path,
    engagement_id: str = ENGAGEMENT_ID,
    verbose: bool = False,
) -> Path:
    """
    Create the engagement directory tree, target repo, and config entry.
    Idempotent — safe to call when the engagement already partially exists.
    Returns the engagement path.
    """
    engagement_path = repo_root / "engagements" / engagement_id
    target_repo_path = engagement_path / "target-repos" / TARGET_REPO_ID

    _log(verbose, f"Creating directories under {engagement_path}")
    for d in ENGAGEMENT_DIRS:
        (engagement_path / d).mkdir(parents=True, exist_ok=True)
    work_repos = engagement_path / "work-repositories"
    for d in WORK_REPO_DIRS:
        (work_repos / d).mkdir(parents=True, exist_ok=True)

    _log(verbose, "Writing target repository source files")
    _write_target_repo(target_repo_path)

    _log(verbose, "Writing engagement-profile.md")
    _write_engagement_profile(engagement_path, engagement_id)

    _log(verbose, "Updating engagements-config.yaml")
    _add_to_config(repo_root / "engagements-config.yaml", engagement_id)

    return engagement_path


def teardown_demo(
    repo_root: Path,
    engagement_id: str = ENGAGEMENT_ID,
    verbose: bool = False,
) -> None:
    """Remove the engagement directory and revert engagements-config.yaml."""
    engagement_path = repo_root / "engagements" / engagement_id
    if engagement_path.exists():
        _log(verbose, f"Removing {engagement_path}")
        shutil.rmtree(engagement_path)
    else:
        _log(verbose, "Engagement directory not found — nothing to remove")

    _remove_from_config(repo_root / "engagements-config.yaml", engagement_id, verbose)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _write_target_repo(target_repo_path: Path) -> None:
    target_repo_path.mkdir(parents=True, exist_ok=True)
    (target_repo_path / "README.md").write_text(TASKFLOW_README, encoding="utf-8")
    (target_repo_path / "requirements.txt").write_text(TASKFLOW_REQUIREMENTS, encoding="utf-8")
    (target_repo_path / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    src = target_repo_path / "src"
    src.mkdir(exist_ok=True)
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text(TASKFLOW_MAIN, encoding="utf-8")
    (src / "models.py").write_text(TASKFLOW_MODELS, encoding="utf-8")


def _write_engagement_profile(engagement_path: Path, engagement_id: str) -> None:
    content = textwrap.dedent(f"""\
        ---
        engagement-id: {engagement_id}
        name: TaskFlow API — Phase A Demo
        entry-point: EP-0
        warm-start: false
        status: active
        ---

        # Engagement Profile — {engagement_id}

        **Project:** TaskFlow API
        **Engagement type:** Greenfield development
        **Entry point:** EP-0 (pre-engagement scoping)
        **Phase scope:** Phase A (Architecture Vision)

        ## Context

        TaskFlow API is a Python/FastAPI task management system for EU-hosted
        Kubernetes infrastructure. Phase A establishes the Architecture Vision:
        stakeholder map, architecture principles, key drivers, and initial goals.

        ## Target Repository

        Local path: `target-repos/taskflow-api/`
        Language: Python 3.12 / FastAPI
        Database: PostgreSQL 16
        Deployment: GKE (EU-West / Frankfurt)
        """)
    (engagement_path / "engagement-profile.md").write_text(content, encoding="utf-8")


def _add_to_config(config_path: Path, engagement_id: str) -> None:
    text = config_path.read_text(encoding="utf-8")
    if f"- id: {engagement_id}" in text:
        return  # already present
    block = _CONFIG_BLOCK.format(eid=engagement_id)
    # Insert before the multi-repo example comment block
    sep = "\n# ---------------------------------------------------------------------------"
    idx = text.find(sep)
    if idx != -1:
        text = text[:idx] + block + text[idx:]
    else:
        text += block
    config_path.write_text(text, encoding="utf-8")


def _remove_from_config(config_path: Path, engagement_id: str, verbose: bool) -> None:
    if not config_path.exists():
        return
    text = config_path.read_text(encoding="utf-8")
    block = _CONFIG_BLOCK.format(eid=engagement_id)
    if block in text:
        _log(verbose, f"Removing {engagement_id} from engagements-config.yaml")
        config_path.write_text(text.replace(block, ""), encoding="utf-8")
    else:
        _log(verbose, f"{engagement_id} entry not found in engagements-config.yaml")


def _log(verbose: bool, msg: str) -> None:
    if verbose:
        print(f"  [scaffold] {msg}")

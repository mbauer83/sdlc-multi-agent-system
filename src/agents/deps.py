"""
AgentDeps: dependency container injected into every PydanticAI agent call.

Passed via pydantic_ai.RunContext[AgentDeps] to tool functions.
All fields are read-only at runtime — agents must not mutate deps directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from src.events.event_store import EventStore
from src.events.models.state import WorkflowState


@dataclass(frozen=True)
class AgentDeps:
    """
    Runtime context available to every agent tool.

    engagement_id:      Canonical identifier for this engagement (e.g. "ENG-001").
    event_store:        EventStore for the engagement — emit events via this.
    active_skill_id:    skill-id from the currently loaded skill's frontmatter.
    workflow_state:     Snapshot of WorkflowState at invocation time (immutable).
    engagement_path:    Path to engagements/<engagement_id>/ directory.
    framework_path:     Path to the framework/ directory (for framework tools).
    agent_id:           Canonical agent identifier (e.g. "SA", "PM", "SwA").
    invocation_mode:    "workflow" (full engagement) or "express" (standalone).
                        Controls which skill sections are injected at Layer 3.
    """

    engagement_id: str
    event_store: EventStore
    active_skill_id: str
    workflow_state: WorkflowState
    engagement_path: Path
    framework_path: Path
    agent_id: str
    invocation_mode: Literal["workflow", "express"] = field(default="workflow")

    @property
    def work_repos_path(self) -> Path:
        """Shortcut to the work-repositories directory."""
        return self.engagement_path / "work-repositories"

    @property
    def architecture_repo_path(self) -> Path:
        return self.work_repos_path / "architecture-repository"

    @property
    def enterprise_repo_path(self) -> Path:
        return self.framework_path.parent / "enterprise-repository"

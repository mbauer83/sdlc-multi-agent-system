"""
EngagementSession: top-level entry point for the SDLC multi-agent system.

MVP implementation: boots an engagement, initialises the EventStore, and
can invoke a single specialist agent turn (no full LangGraph graph yet).

Full LangGraph topology (build_sdlc_graph, PM routing loop, phase subgraphs)
is Stage 5c. This module provides the bootstrap + single-agent execution path
that validates the full stack end-to-end.

CLI usage:
    uv run python -m src.orchestration.session \\
        --engagement ENG-001 \\
        --phase A \\
        --agent SA \\
        --skill SA-PHASE-A \\
        --task "Produce the Architecture Vision for the engagement."
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

import yaml

from src.events.event_store import EventStore
from src.events.models.phase import PhaseEnteredPayload
from src.events.models.sprint import SprintOpenedPayload


# ---------------------------------------------------------------------------
# Engagement configuration loading
# ---------------------------------------------------------------------------

class EngagementConfig:
    """Parsed view of engagements-config.yaml for one engagement."""

    def __init__(self, data: dict[str, Any], engagement_id: str) -> None:
        self.engagement_id = engagement_id
        self.entry_point: str = data.get("entry-point", "EP-0")
        repos_raw: list[dict] = data.get("target-repositories", [])
        if not repos_raw and (single := data.get("target-repository")):
            repos_raw = [{**single, "id": "default", "primary": True}]
        self.target_repositories: list[dict] = repos_raw
        self.primary_repo_id: str | None = next(
            (r["id"] for r in repos_raw if r.get("primary")), None
        )

    @staticmethod
    def load(engagements_config: Path, engagement_id: str) -> "EngagementConfig":
        if not engagements_config.exists():
            return EngagementConfig({"entry-point": "EP-0"}, engagement_id)
        raw = yaml.safe_load(engagements_config.read_text()) or {}
        # Structure: raw["engagements"]["active-engagements"] list
        eng_block = raw.get("engagements", {})
        active = (
            eng_block.get("active-engagements", [])
            if isinstance(eng_block, dict)
            else []
        )
        for eng in active:
            if isinstance(eng, dict) and eng.get("id") == engagement_id:
                return EngagementConfig(eng, engagement_id)
        return EngagementConfig({}, engagement_id)


# ---------------------------------------------------------------------------
# EngagementSession
# ---------------------------------------------------------------------------

class EngagementSession:
    """
    Bootstrap and runtime context for one engagement run.

    Responsibilities:
      1. Load engagements-config.yaml
      2. Initialise EventStore (replay or fresh)
      3. Provide invoke_specialist() for single-agent execution
    """

    def __init__(
        self,
        engagement_id: str,
        repo_root: Path | None = None,
    ) -> None:
        self.repo_root = repo_root or Path.cwd()
        self.engagement_id = engagement_id
        self.engagement_path = self.repo_root / "engagements" / engagement_id
        self.framework_path = self.repo_root / "framework"
        self.agents_root = self.repo_root / "agents"

        # Load configuration
        config_path = self.repo_root / "engagements-config.yaml"
        self.config = EngagementConfig.load(config_path, engagement_id)

        # Initialise EventStore
        db_path = self.engagement_path / "workflow.db"
        self.event_store = EventStore(engagement_id=engagement_id, db_path=db_path)

        # Recover state
        self.workflow_state = self.event_store.current_state()

    # ------------------------------------------------------------------
    # Single-specialist execution (MVP path)
    # ------------------------------------------------------------------

    async def invoke_specialist(
        self,
        agent_id: str,
        skill_id: str,
        task: str,
        phase: str = "A",
        cycle_id: str | None = None,
    ) -> str:
        """
        Invoke one specialist agent and return its output.

        Emits phase.entered and sprint.opened events if they aren't already
        in the EventStore for this phase. Returns the agent's text output.
        """
        from src.agents.base import build_agent
        from src.agents.deps import AgentDeps
        from src.agents.tools.universal_tools import register_universal_tools
        from src.agents.tools.write_tools import build_write_tool
        from src.agents.tools.target_repo_tools import register_read_only_target_repo_tools
        from src.models.llm_config import LLMConfig

        # Ensure phase/sprint events exist
        cycle_id = cycle_id or f"CYC-{self.engagement_id}-001"
        self._ensure_phase_events(phase, cycle_id)

        # Build the agent — provider resolved via config cascade
        llm_config = LLMConfig.load(
            self.repo_root / "engagements-config.yaml",
            self.engagement_id,
        )
        agent = build_agent(agent_id, self.agents_root, llm_config=llm_config)
        register_universal_tools(agent)
        register_read_only_target_repo_tools(agent)
        write_fn = build_write_tool(agent_id)
        agent.tool(write_fn)

        # Build deps
        deps = AgentDeps(
            engagement_id=self.engagement_id,
            event_store=self.event_store,
            active_skill_id=skill_id,
            workflow_state=self.workflow_state,
            engagement_path=self.engagement_path,
            framework_path=self.framework_path,
            agent_id=agent_id,
        )

        # Run the agent
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = await agent.run(task, deps=deps)

        # Refresh state after any emitted events
        self.workflow_state = self.event_store.current_state()
        return result.output

    def _ensure_phase_events(self, phase: str, cycle_id: str) -> None:
        """Emit phase.entered and sprint.opened if not already in EventStore."""
        existing = self.event_store.query(event_type="phase.entered", limit=100)
        import json

        def _payload(e: dict) -> dict:
            p = e.get("payload", {})
            return json.loads(p) if isinstance(p, str) else (p or {})

        phase_entered = any(_payload(e).get("phase_id") == phase for e in existing)
        if not phase_entered:
            self.event_store.append(
                PhaseEnteredPayload(
                    phase_id=phase,  # type: ignore[arg-type]
                    iteration_type="context" if phase in ("Prelim", "A") else "definition",
                    iteration_number=1,
                    trigger="initial",
                ),
                actor="system",
                cycle_id=cycle_id,
            )

        existing_sprints = self.event_store.query(event_type="sprint.opened", limit=10)
        if not existing_sprints:
            self.event_store.append(
                SprintOpenedPayload(
                    sprint_id=f"SPR-{self.engagement_id}-{phase}-001",
                    stream="architecture",
                    scope=f"Phase {phase} architecture sprint",
                ),
                actor="system",
                cycle_id=cycle_id,
            )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

async def _main(args: argparse.Namespace) -> None:
    session = EngagementSession(args.engagement)
    print(f"Engagement: {args.engagement}, Phase: {args.phase}, Agent: {args.agent}")
    print(f"Skill: {args.skill}")
    print(f"Task: {args.task}\n")
    print("─" * 60)

    output = await session.invoke_specialist(
        agent_id=args.agent,
        skill_id=args.skill,
        task=args.task,
        phase=args.phase,
    )

    print(output)
    print("─" * 60)
    state = session.workflow_state
    events = session.event_store.query(limit=5)
    print(f"\nEventStore: {len(events)} recent events, snapshot_at={state.snapshot_at}")


def main() -> None:
    parser = argparse.ArgumentParser(description="SDLC Multi-Agent System — MVP session runner")
    parser.add_argument("--engagement", required=True, help="Engagement ID (e.g. ENG-001)")
    parser.add_argument("--phase", default="A", help="ADM phase to enter (default: A)")
    parser.add_argument("--agent", required=True, help="Agent role ID (e.g. SA, PM, SwA)")
    parser.add_argument("--skill", required=True, help="Skill ID to load (e.g. SA-PHASE-A)")
    parser.add_argument("--task", required=True, help="Task description for the agent")
    args = parser.parse_args()
    asyncio.run(_main(args))


if __name__ == "__main__":
    main()

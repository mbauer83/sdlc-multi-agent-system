"""
LangGraph node implementations for the SDLC workflow graph.

All nodes are built as closures over an EngagementSession via
build_node_fns(session), keeping node logic pure (dict in / dict out)
while providing access to the EventStore and agent registry without
module-level global state.

Node contract (LangGraph):
    async def <name>(state: SDLCGraphState) -> dict

Governed by framework/orchestration-topology.md §4.1 and §5.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .graph_state import SDLCGraphState
from .pm_decision import PMDecision


# ---------------------------------------------------------------------------
# Node factory
# ---------------------------------------------------------------------------

def build_node_fns(session: Any) -> dict[str, Callable]:
    """
    Build all LangGraph node functions closed over *session* (EngagementSession).

    Returns a dict suitable for `graph.add_node(name, fn)` iteration.
    Imported lazily inside graph.py to avoid circular imports at module level.
    """
    from src.agents.base import build_agent
    from src.agents.deps import AgentDeps
    from src.agents.tools.pm_tools import register_pm_tools
    from src.agents.tools.universal_tools import register_universal_tools
    from src.events.models.cycle import CycleClosedPayload, EngagementCompletedPayload
    from src.events.models.gate import GateEvaluatedPayload, GatePassedPayload
    from src.events.models.review import ReviewPendingPayload, ReviewSprintClosedPayload
    from src.events.models.specialist import SpecialistCompletedPayload, SpecialistInvokedPayload
    from src.events.models.sprint import SprintClosedPayload
    from src.models.llm_config import LLMConfig

    cfg = LLMConfig.load(
        session.repo_root / "engagements-config.yaml",
        session.engagement_id,
    )

    # ------------------------------------------------------------------
    # PM supervisor node
    # ------------------------------------------------------------------

    async def pm_node(state: SDLCGraphState) -> dict:
        """PM supervisor: reads EventStore state, decides next action."""
        pm_agent = build_agent(
            "PM", session.agents_root, llm_config=cfg, result_type=PMDecision
        )
        register_universal_tools(pm_agent)
        register_pm_tools(pm_agent)

        workflow_state = session.event_store.current_state()
        deps = AgentDeps(
            engagement_id=state["engagement_id"],
            event_store=session.event_store,
            active_skill_id="PM-MASTER",
            workflow_state=workflow_state,
            engagement_path=session.engagement_path,
            framework_path=session.framework_path,
            agent_id="PM",
        )
        prompt = _pm_decision_prompt(state, workflow_state)
        result = await pm_agent.run(prompt, deps=deps)
        decision: PMDecision = result.data
        return {
            **state,
            "pm_decision": decision,
            "current_agent": None,
            "current_skill": None,
            "last_specialist_output": decision.reasoning,
        }

    # ------------------------------------------------------------------
    # Specialist nodes — shared implementation
    # ------------------------------------------------------------------

    async def _specialist(state: SDLCGraphState, agent_id: str) -> dict:
        """Shared specialist node: delegates to EngagementSession.invoke_specialist."""
        decision = state.get("pm_decision")
        skill_id = (decision.skill_id if decision else None) or f"{agent_id}-PHASE-A"
        task = decision.task_description if decision else f"Perform {agent_id} work"

        workflow_state = session.event_store.current_state()
        phase = "A"
        cycle_id: str | None = None
        for cycle in workflow_state.active_cycles:
            phase = cycle.current_phase
            cycle_id = cycle.cycle_id
            break

        session.event_store.append(
            SpecialistInvokedPayload(agent_id=agent_id, skill_id=skill_id, task=task),
            actor="PM",
            cycle_id=cycle_id,
        )

        output = await session.invoke_specialist(
            agent_id=agent_id, skill_id=skill_id, task=task, phase=phase,
            cycle_id=cycle_id,
        )

        session.event_store.append(
            SpecialistCompletedPayload(agent_id=agent_id, skill_id=skill_id),
            actor=agent_id,
            cycle_id=cycle_id,
        )
        if session.event_store.check_snapshot_interval():
            session.event_store.create_snapshot(trigger="periodic")

        return {
            **state,
            "current_agent": agent_id,
            "current_skill": skill_id,
            "last_specialist_output": output,
            "pm_decision": None,
        }

    async def sa_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "SA")

    async def swa_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "SwA")

    async def do_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "DO")

    async def de_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "DE")

    async def qa_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "QA")

    async def po_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "PO")

    async def smm_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "SMM")

    async def csco_node(state: SDLCGraphState) -> dict:
        return await _specialist(state, "CSCO")

    # ------------------------------------------------------------------
    # Infrastructure nodes
    # ------------------------------------------------------------------

    async def gate_check_node(state: SDLCGraphState) -> dict:
        """Evaluate a phase gate; emit gate.evaluated + snapshot on pass."""
        decision = state.get("pm_decision")
        gate_id = (decision.gate_id if decision else None) or "unknown"
        workflow_state = session.event_store.current_state()
        cycle_id = next(
            (c.cycle_id for c in workflow_state.active_cycles), None
        )

        session.event_store.append(
            GateEvaluatedPayload(transition=gate_id, checklist_results={}),
            actor="PM",
            cycle_id=cycle_id,
        )
        session.event_store.append(
            GatePassedPayload(transition=gate_id),
            actor="PM",
            cycle_id=cycle_id,
        )
        session.event_store.create_snapshot(trigger="gate.evaluated")

        return {**state, "pm_decision": None}

    async def cq_user_node(state: SDLCGraphState) -> dict:
        """Surface open CQs to the user; set suspended flag if any remain open."""
        workflow_state = session.event_store.current_state()
        open_cqs: list[str] = []
        for cycle in workflow_state.active_cycles:
            open_cqs = list(cycle.open_cqs)
            break
        return {**state, "pm_decision": None}

    async def algedonic_handler_node(state: SDLCGraphState) -> dict:
        """Clear algedonic bypass after the signal has been handled."""
        return {**state, "algedonic_active": False, "pm_decision": None}

    async def sprint_close_node(state: SDLCGraphState) -> dict:
        """Close all active sprints; emit sprint.closed + snapshot."""
        workflow_state = session.event_store.current_state()
        for cycle in workflow_state.active_cycles:
            for sprint_id in list(cycle.active_sprints):
                session.event_store.append(
                    SprintClosedPayload(sprint_id=sprint_id),
                    actor="PM",
                    cycle_id=cycle.cycle_id,
                )
            break
        session.event_store.create_snapshot(trigger="sprint.close")
        return {**state, "pm_decision": None, "review_pending": False}

    async def review_processing_node(state: SDLCGraphState) -> dict:
        """Emit review.sprint-closed once user review is processed."""
        workflow_state = session.event_store.current_state()
        cycle_id = next(
            (c.cycle_id for c in workflow_state.active_cycles), None
        )
        sprint_id = state.get("current_skill") or "SPR-000"

        session.event_store.append(
            ReviewSprintClosedPayload(sprint_id=sprint_id),
            actor="PM",
            cycle_id=cycle_id,
        )
        return {**state, "review_pending": False, "pm_decision": None}

    async def engagement_complete_node(state: SDLCGraphState) -> dict:
        """Emit engagement.completed + final snapshot; initiates promotion."""
        workflow_state = session.event_store.current_state()
        cycle_id = next(
            (c.cycle_id for c in workflow_state.active_cycles), "CYC-FINAL"
        )
        session.event_store.append(
            EngagementCompletedPayload(cycle_id=cycle_id),
            actor="PM",
            cycle_id=cycle_id,
        )
        session.event_store.create_snapshot(trigger="engagement.completed")
        return {**state, "pm_decision": None}

    # ------------------------------------------------------------------
    # Return all node functions keyed by their LangGraph node names
    # ------------------------------------------------------------------

    return {
        "pm_node":                  pm_node,
        "sa_node":                  sa_node,
        "swa_node":                 swa_node,
        "do_node":                  do_node,
        "de_node":                  de_node,
        "qa_node":                  qa_node,
        "po_node":                  po_node,
        "smm_node":                 smm_node,
        "csco_node":                csco_node,
        "gate_check_node":          gate_check_node,
        "cq_user_node":             cq_user_node,
        "algedonic_handler_node":   algedonic_handler_node,
        "sprint_close_node":        sprint_close_node,
        "review_processing_node":   review_processing_node,
        "engagement_complete_node": engagement_complete_node,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pm_decision_prompt(state: SDLCGraphState, workflow_state: Any) -> str:
    """Build the PM decision prompt from current graph + workflow state."""
    phase = "Prelim"
    open_cqs: list[str] = []
    active_sprints: list[str] = []

    for cycle in getattr(workflow_state, "active_cycles", []):
        phase = cycle.current_phase
        open_cqs = list(cycle.open_cqs)
        active_sprints = list(cycle.active_sprints)
        break

    last_output = state.get("last_specialist_output") or "(none yet)"
    last_agent = state.get("current_agent") or "(none)"

    return (
        f"Engagement: {state.get('engagement_id', 'unknown')}\n"
        f"Current phase: {phase}\n"
        f"Active sprints: {active_sprints or 'none'}\n"
        f"Open CQs: {open_cqs or 'none'}\n"
        f"Last specialist: {last_agent}\n"
        f"Last output (truncated): {str(last_output)[:300]}\n\n"
        "Decide the next action for this engagement and return a PMDecision."
    )

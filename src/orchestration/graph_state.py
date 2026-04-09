"""
SDLCGraphState: the shared state threaded through every LangGraph node.

Governed by framework/orchestration-topology.md §3.

Carries only what routing functions need to select the next node.
Rich engagement state (open CQs, gate history, artifact registry, phase
visit counts) lives in WorkflowState (DOB-009), rebuilt from EventStore
via replay_from_latest_snapshot() and passed to agents via AgentDeps.

All fields are optional (total=False) so nodes only return the keys they
actually mutate — LangGraph merges returned dicts onto the prior state.
"""

from __future__ import annotations

from typing import Annotated, Any

from langgraph.graph import add_messages
from typing_extensions import TypedDict

from .pm_decision import PMDecision


class SDLCGraphState(TypedDict, total=False):
    """
    Mutable state passed through the LangGraph SDLC workflow graph.
    """

    # -----------------------------------------------------------------------
    # Engagement identity (set once at session start; never mutated)
    # -----------------------------------------------------------------------
    engagement_id: str           # e.g. "ENG-001"

    # -----------------------------------------------------------------------
    # Current execution context (set by nodes; read by routing functions)
    # -----------------------------------------------------------------------
    current_agent: str | None    # agent role currently executing, e.g. "SA"
    current_skill: str | None    # skill ID currently loaded, e.g. "SA-PHASE-A"

    # -----------------------------------------------------------------------
    # PM decision — routing functions read next_action from here
    # -----------------------------------------------------------------------
    pm_decision: PMDecision | None

    # -----------------------------------------------------------------------
    # Output from most recent specialist invocation
    # -----------------------------------------------------------------------
    last_specialist_output: str | None

    # -----------------------------------------------------------------------
    # Multi-repo context (populated from engagement config at session start)
    # -----------------------------------------------------------------------
    target_repository_ids: list[str]
    primary_repository_id: str | None

    # -----------------------------------------------------------------------
    # Lifecycle flags (set/cleared by infrastructure nodes; checked by routing)
    # -----------------------------------------------------------------------
    review_pending: bool     # True when sprint review awaits user submission
    algedonic_active: bool   # True when an active S1/S2 algedonic signal exists

    # -----------------------------------------------------------------------
    # Message history (LangGraph managed — append-only via add_messages)
    # -----------------------------------------------------------------------
    messages: Annotated[list[Any], add_messages]


def initial_state(
    engagement_id: str,
    target_repository_ids: list[str] | None = None,
    primary_repository_id: str | None = None,
) -> SDLCGraphState:
    """Return a fresh SDLCGraphState for a new engagement."""
    return SDLCGraphState(
        engagement_id=engagement_id,
        current_agent=None,
        current_skill=None,
        pm_decision=None,
        last_specialist_output=None,
        target_repository_ids=target_repository_ids or [],
        primary_repository_id=primary_repository_id,
        review_pending=False,
        algedonic_active=False,
        messages=[],
    )

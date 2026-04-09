"""
SDLCGraphState: the shared state threaded through every LangGraph node.

Governed by framework/orchestration-topology.md §3.
Extended with multi-repo fields per Stage 5c spec.

All fields are plain Python types (strings, lists, dicts) so they survive
LangGraph's JSON serialization without a custom serializer. Pydantic models
(WorkflowState etc.) are stored separately in the EventStore — only their
IDs or serialized summaries live in graph state.
"""

from __future__ import annotations

from typing import Annotated, Any

from langgraph.graph import add_messages
from typing_extensions import TypedDict


class SDLCGraphState(TypedDict, total=False):
    """
    Mutable state passed through the LangGraph SDLC workflow graph.

    Required fields are declared; optional fields use total=False so nodes
    only need to return the keys they actually mutate.
    """

    # -----------------------------------------------------------------------
    # Engagement identity
    # -----------------------------------------------------------------------
    engagement_id: str          # e.g. "ENG-001"
    entry_point: str            # "EP-0" | "EP-A" | ... | "EP-H"

    # -----------------------------------------------------------------------
    # Phase and sprint tracking
    # -----------------------------------------------------------------------
    current_phase: str          # "Prelim" | "A" | "B" | ... | "H" | "RM"
    current_cycle_id: str       # ID of the active ADM cycle
    current_sprint_id: str | None  # None between sprints

    phase_visit_counts: dict[str, int]  # {"A": 1, "B": 2, ...}

    # -----------------------------------------------------------------------
    # Multi-repo support (Stage 5c)
    # -----------------------------------------------------------------------
    target_repository_ids: list[str]    # all registered repo IDs
    primary_repository_id: str | None   # primary repo ID; None for single-repo

    # -----------------------------------------------------------------------
    # Specialist routing (PM decision output)
    # -----------------------------------------------------------------------
    next_agent_id: str | None       # which specialist to invoke next
    next_skill_id: str | None       # which skill to load for that specialist
    task_description: str           # human-readable task for the specialist
    pm_reasoning: str               # PM's reasoning (audit only)

    # -----------------------------------------------------------------------
    # Specialist output
    # -----------------------------------------------------------------------
    last_specialist_output: str     # raw text output from last specialist
    last_specialist_agent: str      # which agent produced it

    # -----------------------------------------------------------------------
    # Gate tracking
    # -----------------------------------------------------------------------
    pending_gate: str | None        # gate transition string e.g. "A→B"
    gate_votes: dict[str, str]      # agent_id → "pass" | "conditional" | "veto"

    # -----------------------------------------------------------------------
    # CQ / algedonic flags
    # -----------------------------------------------------------------------
    suspended: bool                 # True while waiting for CQ answer
    open_cq_ids: list[str]         # CQ IDs pending user answer
    open_algedonic_ids: list[str]  # active algedonic signal IDs
    review_pending: bool            # True when awaiting sprint review

    # -----------------------------------------------------------------------
    # Message history (LangGraph managed)
    # -----------------------------------------------------------------------
    messages: Annotated[list[Any], add_messages]


def initial_state(
    engagement_id: str,
    entry_point: str = "EP-0",
    target_repository_ids: list[str] | None = None,
    primary_repository_id: str | None = None,
) -> SDLCGraphState:
    """Return a fresh SDLCGraphState for a new engagement."""
    return SDLCGraphState(
        engagement_id=engagement_id,
        entry_point=entry_point,
        current_phase="Prelim",
        current_cycle_id="",
        current_sprint_id=None,
        phase_visit_counts={},
        target_repository_ids=target_repository_ids or [],
        primary_repository_id=primary_repository_id,
        next_agent_id=None,
        next_skill_id=None,
        task_description="",
        pm_reasoning="",
        last_specialist_output="",
        last_specialist_agent="",
        pending_gate=None,
        gate_votes={},
        suspended=False,
        open_cq_ids=[],
        open_algedonic_ids=[],
        review_pending=False,
        messages=[],
    )

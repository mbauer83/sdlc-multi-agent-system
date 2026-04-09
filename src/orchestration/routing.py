"""
LangGraph routing functions for the SDLC workflow graph.

Each function receives SDLCGraphState and returns the name of the next node.
Algedonic bypass is checked before every routing decision — an active S1/S2
signal always wins over the PM's planned next action.

Governed by framework/orchestration-topology.md §4.2.
"""

from __future__ import annotations

from .graph_state import SDLCGraphState


def route_from_pm(state: SDLCGraphState) -> str:
    """Central router: PM has written pm_decision; route to the appropriate node."""
    # Algedonic bypass: checked before acting on PM decision
    if state.get("algedonic_active"):
        return "algedonic_handler_node"

    decision = state.get("pm_decision")
    if decision is None:
        return "pm_node"  # PM re-deliberates (should not occur in normal flow)

    match decision.next_action:
        case "invoke_specialist":
            return _specialist_node(decision.specialist_id)
        case "evaluate_gate":
            return "gate_check_node"
        case "surface_cqs":
            return "cq_user_node"
        case "trigger_review":
            return "review_processing_node"
        case "close_sprint":
            return "sprint_close_node"
        case "complete_engagement":
            return "engagement_complete_node"
    return "pm_node"  # default: PM re-deliberates


def route_after_specialist(state: SDLCGraphState) -> str:
    """After any specialist run: check algedonics, then return to PM."""
    if state.get("algedonic_active"):
        return "algedonic_handler_node"
    if state.get("review_pending"):
        return "review_processing_node"
    return "pm_node"


def route_after_gate(state: SDLCGraphState) -> str:
    """After gate evaluation — return to PM unless a blocking review-gate is pending."""
    if state.get("algedonic_active"):
        return "algedonic_handler_node"
    if state.get("review_pending"):
        return "review_processing_node"
    return "pm_node"


def route_after_cq(state: SDLCGraphState) -> str:
    """After CQ answer received from user — PM resumes or advances."""
    return "pm_node"


def route_after_algedonic(state: SDLCGraphState) -> str:
    """After algedonic signal handled. May halt (END) or resume (pm_node)."""
    decision = state.get("pm_decision")
    if decision and decision.next_action == "complete_engagement":
        return "engagement_complete_node"
    return "pm_node"


def route_after_sprint_close(state: SDLCGraphState) -> str:
    """After sprint closed: trigger review if enabled, else back to PM."""
    if state.get("review_pending"):
        return "review_processing_node"
    return "pm_node"


def route_after_review(state: SDLCGraphState) -> str:
    """After sprint review processed: back to PM for next phase or sprint."""
    return "pm_node"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SPECIALIST_NODES: dict[str, str] = {
    "SA":   "sa_node",
    "SwA":  "swa_node",
    "DO":   "do_node",
    "DE":   "de_node",
    "QA":   "qa_node",
    "PO":   "po_node",
    "SMM":  "smm_node",
    "CSCO": "csco_node",
}


def _specialist_node(agent_id: str | None) -> str:
    """Map agent_id to its LangGraph node name."""
    if agent_id and (node := _SPECIALIST_NODES.get(agent_id)):
        return node
    return "pm_node"  # unknown specialist — re-deliberate

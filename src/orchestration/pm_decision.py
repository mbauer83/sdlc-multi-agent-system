"""
PMDecision: structured output type for the PM supervisor agent.

The PM agent's result_type is PMDecision.  Routing functions in routing.py
consume next_action to select the next LangGraph node.

Governed by framework/orchestration-topology.md §5.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class PMDecision(BaseModel):
    """
    Structured decision emitted by the PM supervisor after each deliberation.

    next_action values are the canonical routing keys consumed by route_from_pm():
      invoke_specialist   — route to a specialist node; specialist_id + skill_id required
      evaluate_gate       — route to gate_check_node; gate_id required
      surface_cqs         — route to cq_user_node
      trigger_review      — route to review_processing_node
      close_sprint        — route to sprint_close_node
      complete_engagement — route to engagement_complete_node
    """

    next_action: Literal[
        "invoke_specialist",
        "evaluate_gate",
        "surface_cqs",
        "trigger_review",
        "close_sprint",
        "complete_engagement",
    ]
    specialist_id: str | None = None   # Required when next_action == "invoke_specialist"
    skill_id: str | None = None        # Required when next_action == "invoke_specialist"
    task_description: str              # Human-readable description of the work unit
    reasoning: str                     # PM's explanation — persisted as audit log
    gate_id: str | None = None         # Required when next_action == "evaluate_gate"

"""
build_sdlc_graph(): assembles the full LangGraph SDLC workflow graph.

The graph encodes:
  - PM supervisor node as deliberation hub
  - 8 specialist nodes (SA, SwA, DO, DE, QA, PO, SMM, CSCO)
  - 6 infrastructure nodes (gate, CQ, algedonic, sprint-close, review, complete)
  - Routing functions that read SDLCGraphState to select the next node

All nodes are built as closures over an EngagementSession so they can
access the EventStore and agent registry without module-level globals.

Governed by framework/orchestration-topology.md §4.3.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langgraph.graph import END, START, StateGraph

from .graph_state import SDLCGraphState
from .routing import (
    route_after_algedonic,
    route_after_cq,
    route_after_gate,
    route_after_review,
    route_after_specialist,
    route_after_sprint_close,
    route_from_pm,
)

if TYPE_CHECKING:
    from src.orchestration.session import EngagementSession


def build_sdlc_graph(session: "EngagementSession") -> Any:
    """
    Build and compile the SDLC LangGraph workflow graph.

    Parameters
    ----------
    session:
        EngagementSession providing EventStore + agents_root + config.
        Nodes are closed over this session — do not share a compiled graph
        across multiple engagement sessions.

    Returns
    -------
    CompiledGraph
        Ready to invoke via `await graph.ainvoke(initial_state)`.
    """
    from .nodes import build_node_fns

    node_fns = build_node_fns(session)
    graph: StateGraph = StateGraph(SDLCGraphState)

    # Register all nodes
    for name, fn in node_fns.items():
        graph.add_node(name, fn)

    # Entry point: always start at PM supervisor
    graph.add_edge(START, "pm_node")

    # PM routes to everything
    graph.add_conditional_edges("pm_node", route_from_pm)

    # All specialist nodes return via route_after_specialist
    specialist_nodes = [
        "sa_node", "swa_node", "do_node", "de_node",
        "qa_node", "po_node", "smm_node", "csco_node",
    ]
    for node in specialist_nodes:
        graph.add_conditional_edges(node, route_after_specialist)

    # Infrastructure nodes
    graph.add_conditional_edges("gate_check_node", route_after_gate)
    graph.add_conditional_edges("cq_user_node", route_after_cq)
    graph.add_conditional_edges("algedonic_handler_node", route_after_algedonic)
    graph.add_conditional_edges("sprint_close_node", route_after_sprint_close)
    graph.add_conditional_edges("review_processing_node", route_after_review)
    graph.add_edge("engagement_complete_node", END)

    return graph.compile()

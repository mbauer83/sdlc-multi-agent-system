"""BDD scenarios for the SDLC LangGraph graph structure.

Verifies that build_sdlc_graph() compiles correctly and registers all nodes
described in framework/orchestration-topology.md §4.3.

Note: We only test *compilation* (structure) here — node *execution* requires
a live LLM and is covered by end-to-end integration tests (Stage 5c).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.events.event_store import EventStore
from src.orchestration.graph_state import SDLCGraphState, initial_state

scenarios("features/graph.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_EXPECTED_NODES = {
    # Specialist nodes
    "pm_node", "sa_node", "swa_node", "do_node", "de_node",
    "qa_node", "po_node", "smm_node", "csco_node",
    # Infrastructure nodes
    "gate_check_node", "cq_user_node", "algedonic_handler_node",
    "sprint_close_node", "review_processing_node", "engagement_complete_node",
}


@pytest.fixture
def stub_session(tmp_path: Path) -> SimpleNamespace:
    """
    Minimal EngagementSession stub providing only the attributes required by
    build_node_fns(). Node closures capture these at graph-build time; the
    attributes are never read during compile() itself.
    """
    engagement_id = "ENG-GRAPH-TEST"
    engagement_path = tmp_path / "engagements" / engagement_id
    engagement_path.mkdir(parents=True)

    event_store = EventStore(
        engagement_id=engagement_id,
        db_path=engagement_path / "workflow.db",
    )
    # Recover state so session.event_store.current_state() is callable
    _ = event_store.current_state()

    return SimpleNamespace(
        engagement_id=engagement_id,
        repo_root=tmp_path,
        engagement_path=engagement_path,
        framework_path=tmp_path / "framework",
        agents_root=tmp_path / "agents",
        event_store=event_store,
    )


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("a stub EngagementSession", target_fixture="session")
def use_stub_session(stub_session: SimpleNamespace) -> SimpleNamespace:
    return stub_session


@given(parsers.parse('engagement id "{eid}"'), target_fixture="eid")
def engagement_id(eid: str) -> str:
    return eid


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("build_sdlc_graph is called", target_fixture="compiled_graph")
def call_build_sdlc_graph(session: SimpleNamespace) -> object:
    from src.orchestration.graph import build_sdlc_graph
    return build_sdlc_graph(session)


@when("initial_state is called", target_fixture="state")
def call_initial_state(eid: str) -> SDLCGraphState:
    return initial_state(eid)


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then("the compiled graph is not None")
def graph_is_not_none(compiled_graph: object) -> None:
    assert compiled_graph is not None


@then(parsers.parse('the graph contains node "{node_name}"'))
def graph_contains_node(compiled_graph: object, node_name: str) -> None:
    # LangGraph compiled graph exposes .nodes as a dict keyed by node name.
    # The __start__ sentinel is also in .nodes but we don't test for it here.
    node_keys = set(compiled_graph.nodes.keys())
    assert node_name in node_keys, (
        f"Node '{node_name}' not found in compiled graph. "
        f"Registered nodes: {sorted(node_keys)}"
    )


@then(parsers.parse('the state has engagement_id "{expected}"'))
def state_has_engagement_id(state: SDLCGraphState, expected: str) -> None:
    assert state["engagement_id"] == expected


@then("the state has algedonic_active False")
def state_algedonic_false(state: SDLCGraphState) -> None:
    assert state.get("algedonic_active") is False


@then("the state has review_pending False")
def state_review_false(state: SDLCGraphState) -> None:
    assert state.get("review_pending") is False


@then("the state has pm_decision None")
def state_pm_decision_none(state: SDLCGraphState) -> None:
    assert state.get("pm_decision") is None

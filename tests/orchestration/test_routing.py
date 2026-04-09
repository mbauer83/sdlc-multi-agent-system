"""BDD scenarios for SDLC LangGraph routing functions.

Each routing function receives an SDLCGraphState dict and returns a node name.
Tests verify the correct node is selected for every state combination, with
special attention to the algedonic bypass invariant.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.orchestration.graph_state import SDLCGraphState, initial_state
from src.orchestration.pm_decision import PMDecision
from src.orchestration.routing import (
    route_after_algedonic,
    route_after_cq,
    route_after_gate,
    route_after_review,
    route_after_specialist,
    route_after_sprint_close,
    route_from_pm,
)

scenarios("features/routing.feature")


# ---------------------------------------------------------------------------
# Shared state fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def state() -> SDLCGraphState:
    return initial_state("ENG-TEST")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("a clean state")
def clean_state(state: SDLCGraphState) -> None:
    pass  # initial_state already sets all flags to False


@given(parsers.parse('a clean state with pm_decision invoke_specialist for "{agent_id}"'))
def state_invoke_specialist(state: SDLCGraphState, agent_id: str) -> None:
    state["pm_decision"] = PMDecision(
        next_action="invoke_specialist",
        specialist_id=agent_id,
        skill_id="SKILL-001",
        task_description="Test task",
        reasoning="Test reasoning",
    )


@given("a clean state with pm_decision evaluate_gate")
def state_evaluate_gate(state: SDLCGraphState) -> None:
    state["pm_decision"] = PMDecision(
        next_action="evaluate_gate",
        gate_id="GATE-A",
        task_description="Evaluate phase gate",
        reasoning="All phase-A deliverables present",
    )


@given("a clean state with pm_decision surface_cqs")
def state_surface_cqs(state: SDLCGraphState) -> None:
    state["pm_decision"] = PMDecision(
        next_action="surface_cqs",
        task_description="Surface pending CQs",
        reasoning="3 open CQs require user input",
    )


@given("a clean state with pm_decision close_sprint")
def state_close_sprint(state: SDLCGraphState) -> None:
    state["pm_decision"] = PMDecision(
        next_action="close_sprint",
        task_description="Close sprint 1",
        reasoning="All sprint tasks complete",
    )


@given("a clean state with pm_decision complete_engagement")
def state_complete_engagement(state: SDLCGraphState) -> None:
    state["pm_decision"] = PMDecision(
        next_action="complete_engagement",
        task_description="Engagement complete",
        reasoning="All phases delivered",
    )


@given("a clean state with pm_decision trigger_review")
def state_trigger_review(state: SDLCGraphState) -> None:
    state["pm_decision"] = PMDecision(
        next_action="trigger_review",
        task_description="Trigger sprint review",
        reasoning="Sprint complete; review gate enabled",
    )


@given("a clean state with no pm_decision")
def state_no_decision(state: SDLCGraphState) -> None:
    state["pm_decision"] = None


@given("algedonic_active is True")
def set_algedonic_active(state: SDLCGraphState) -> None:
    state["algedonic_active"] = True


@given("a clean state with algedonic_active True")
def state_algedonic_only(state: SDLCGraphState) -> None:
    state["algedonic_active"] = True


@given("a clean state with review_pending True")
def state_review_only(state: SDLCGraphState) -> None:
    state["review_pending"] = True


@given("a clean state with review_pending True and algedonic_active True")
def state_review_and_algedonic(state: SDLCGraphState) -> None:
    state["review_pending"] = True
    state["algedonic_active"] = True


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("route_from_pm is called", target_fixture="next_node")
def call_route_from_pm(state: SDLCGraphState) -> str:
    return route_from_pm(state)


@when("route_after_specialist is called", target_fixture="next_node")
def call_route_after_specialist(state: SDLCGraphState) -> str:
    return route_after_specialist(state)


@when("route_after_gate is called", target_fixture="next_node")
def call_route_after_gate(state: SDLCGraphState) -> str:
    return route_after_gate(state)


@when("route_after_cq is called", target_fixture="next_node")
def call_route_after_cq(state: SDLCGraphState) -> str:
    return route_after_cq(state)


@when("route_after_algedonic is called", target_fixture="next_node")
def call_route_after_algedonic(state: SDLCGraphState) -> str:
    return route_after_algedonic(state)


@when("route_after_sprint_close is called", target_fixture="next_node")
def call_route_after_sprint_close(state: SDLCGraphState) -> str:
    return route_after_sprint_close(state)


@when("route_after_review is called", target_fixture="next_node")
def call_route_after_review(state: SDLCGraphState) -> str:
    return route_after_review(state)


# ---------------------------------------------------------------------------
# Then step
# ---------------------------------------------------------------------------


@then(parsers.parse('the next node is "{expected_node}"'))
def check_next_node(next_node: str, expected_node: str) -> None:
    assert next_node == expected_node, (
        f"Expected routing to '{expected_node}', got '{next_node}'"
    )

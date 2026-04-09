"""
BDD tests for universal_tools artifact query functions.

Covers the three serialization bugs found during integration testing:
  - list_artifacts: ArtifactSummary has no to_dict() — must return plain dicts
  - search_artifacts: SearchResult is not iterable — must iterate .hits
  - read_artifact: returns dict from repo — must serialize to JSON string
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, scenario, then, when

from src.agents.tools.universal_tools import (
    list_artifacts,
    read_artifact,
    search_artifacts,
)

# ---------------------------------------------------------------------------
# Minimal entity file content
# ---------------------------------------------------------------------------

_ENTITY_FRONTMATTER = textwrap.dedent("""\
    ---
    artifact-id: STK-001
    artifact-type: stakeholder
    name: "Test Stakeholder"
    version: 0.1.0
    status: draft
    phase-produced: A
    owner-agent: SA
    safety-relevant: false
    produced-by-skill: SA-PHASE-A
    last-updated: 2026-04-09
    engagement: ENG-TEST
    ---

    <!-- §content -->

    ## Test Stakeholder

    A placeholder stakeholder for unit-test purposes.

    <!-- §display -->
""")


# ---------------------------------------------------------------------------
# Fake RunContext (tools only access ctx.deps)
# ---------------------------------------------------------------------------

@dataclass
class _FakeCtx:
    """Minimal stand-in for pydantic_ai.RunContext[AgentDeps]."""
    deps: Any


# ---------------------------------------------------------------------------
# Helpers to build AgentDeps-like objects
# ---------------------------------------------------------------------------

def _make_deps(arch_repo_path: Path, engagement_path: Path | None = None) -> Any:
    """Build a minimal AgentDeps-compatible object pointing to arch_repo_path."""
    from types import SimpleNamespace
    from src.events.event_store import EventStore

    if engagement_path is None:
        engagement_path = arch_repo_path.parent.parent  # work-repos/arch-repo → work-repos → engagement

    db_path = engagement_path / "workflow.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    event_store = EventStore(engagement_id="ENG-TEST", db_path=db_path)
    workflow_state = event_store.current_state()

    work_repos = engagement_path / "work-repositories"

    class _Deps(SimpleNamespace):
        @property
        def work_repos_path(self) -> Path:
            return self._engagement_path / "work-repositories"

        @property
        def architecture_repo_path(self) -> Path:
            return self.work_repos_path / "architecture-repository"

        @property
        def enterprise_repo_path(self) -> Path:
            return self.framework_path.parent / "enterprise-repository"

    return _Deps(
        engagement_id="ENG-TEST",
        agent_id="SA",
        active_skill_id="SA-PHASE-A",
        _engagement_path=engagement_path,
        engagement_path=engagement_path,
        framework_path=engagement_path / "framework",
        event_store=event_store,
        workflow_state=workflow_state,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def arch_repo(tmp_path: Path) -> Path:
    """Create a minimal architecture repo with one stakeholder entity."""
    repo = tmp_path / "work-repositories" / "architecture-repository"
    entity_dir = repo / "model-entities" / "motivation" / "stakeholders"
    entity_dir.mkdir(parents=True)
    (entity_dir / "STK-001.test-stakeholder.md").write_text(_ENTITY_FRONTMATTER)
    return repo


@pytest.fixture
def ctx(arch_repo: Path, tmp_path: Path) -> _FakeCtx:
    """Fake RunContext backed by the real arch_repo fixture."""
    engagement_path = tmp_path
    deps = _make_deps(arch_repo, engagement_path=engagement_path)
    return _FakeCtx(deps=deps)


@pytest.fixture
def result() -> dict:
    return {}


# ---------------------------------------------------------------------------
# Shared step implementations
# ---------------------------------------------------------------------------

@given("a temporary architecture repository with one entity file")
def given_arch_repo(arch_repo: Path) -> None:
    assert (arch_repo / "model-entities" / "motivation" / "stakeholders" / "STK-001.test-stakeholder.md").exists()


@given("a context with a non-existent architecture repository")
def given_missing_repo_ctx(ctx: _FakeCtx) -> None:
    # Override engagement_path to a non-existent subdirectory so arch repo is missing
    ctx.deps.engagement_path = ctx.deps.engagement_path / "nonexistent"
    ctx.deps._engagement_path = ctx.deps.engagement_path


@when("list_artifacts is called with no filters")
def when_list_no_filters(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = list_artifacts(ctx)  # type: ignore[arg-type]


@when("list_artifacts is called with artifact_type \"stakeholder\"")
def when_list_stakeholder(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = list_artifacts(ctx, artifact_type="stakeholder")  # type: ignore[arg-type]


@when("list_artifacts is called with artifact_type \"nonexistent-type\"")
def when_list_nonexistent(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = list_artifacts(ctx, artifact_type="nonexistent-type")  # type: ignore[arg-type]


@when("search_artifacts is called with query \"test stakeholder\"")
def when_search_test_stakeholder(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = search_artifacts(ctx, query="test stakeholder")  # type: ignore[arg-type]


@when("search_artifacts is called with query \"stakeholder\"")
def when_search_stakeholder(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = search_artifacts(ctx, query="stakeholder")  # type: ignore[arg-type]


@when("search_artifacts is called with query \"anything\"")
def when_search_anything(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = search_artifacts(ctx, query="anything")  # type: ignore[arg-type]


@when("read_artifact is called with the entity's artifact_id")
def when_read_existing(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = read_artifact(ctx, artifact_id="STK-001")  # type: ignore[arg-type]


@when("read_artifact is called with artifact_id \"DOES-NOT-EXIST\"")
def when_read_missing(ctx: _FakeCtx, result: dict) -> None:
    result["value"] = read_artifact(ctx, artifact_id="DOES-NOT-EXIST")  # type: ignore[arg-type]


@then("the result is a list")
def then_result_is_list(result: dict) -> None:
    assert isinstance(result["value"], list), f"Expected list, got {type(result['value'])}"


@then("each item in the list is a dict with keys artifact_id, name, status")
def then_items_are_dicts_with_keys(result: dict) -> None:
    for item in result["value"]:
        assert isinstance(item, dict), f"Expected dict, got {type(item)}"
        assert "artifact_id" in item, f"Missing artifact_id in {item}"
        assert "name" in item, f"Missing name in {item}"
        assert "status" in item, f"Missing status in {item}"


@then("the result contains only items where artifact_type is \"stakeholder\"")
def then_only_stakeholder(result: dict) -> None:
    for item in result["value"]:
        assert item["artifact_type"] == "stakeholder", f"Unexpected type: {item}"


@then("the result is an empty list")
def then_empty_list(result: dict) -> None:
    assert result["value"] == [], f"Expected [], got {result['value']}"


@then("each item in the list is JSON-serializable")
def then_json_serializable(result: dict) -> None:
    for item in result["value"]:
        try:
            json.dumps(item)
        except (TypeError, ValueError) as exc:
            pytest.fail(f"Item not JSON-serializable: {item!r} — {exc}")


@then("each item has keys artifact_id, name, score, record_type")
def then_search_item_keys(result: dict) -> None:
    for item in result["value"]:
        for key in ("artifact_id", "name", "score", "record_type"):
            assert key in item, f"Missing key '{key}' in {item}"


@then("the result is a string")
def then_result_is_str(result: dict) -> None:
    assert isinstance(result["value"], str), f"Expected str, got {type(result['value'])}"


@then("the string contains the artifact_id")
def then_contains_artifact_id(result: dict) -> None:
    assert "STK-001" in result["value"], f"artifact_id not in result: {result['value'][:200]}"


@then("the result is a string starting with \"[Artifact\"")
def then_error_string(result: dict) -> None:
    assert isinstance(result["value"], str)
    assert result["value"].startswith("[Artifact"), f"Got: {result['value']}"


# ---------------------------------------------------------------------------
# Scenario bindings
# ---------------------------------------------------------------------------

@scenario("features/universal_tools.feature", "list_artifacts returns list of plain dicts")
def test_list_artifacts_returns_dicts() -> None: ...

@scenario("features/universal_tools.feature", "list_artifacts with artifact_type filter returns matching entities only")
def test_list_artifacts_filter() -> None: ...

@scenario("features/universal_tools.feature", "list_artifacts with unknown filter returns empty list")
def test_list_artifacts_unknown_filter() -> None: ...

@scenario("features/universal_tools.feature", "list_artifacts result dicts have no Path objects")
def test_list_artifacts_json_safe() -> None: ...

@scenario("features/universal_tools.feature", "search_artifacts returns list of dicts with score field")
def test_search_artifacts_returns_dicts() -> None: ...

@scenario("features/universal_tools.feature", "search_artifacts result dicts have no Path objects")
def test_search_artifacts_json_safe() -> None: ...

@scenario("features/universal_tools.feature", "read_artifact returns a JSON string for an existing artifact")
def test_read_artifact_found() -> None: ...

@scenario("features/universal_tools.feature", "read_artifact returns an error string for a missing artifact")
def test_read_artifact_missing() -> None: ...

@scenario("features/universal_tools.feature", "list_artifacts does not raise when the repo root is missing")
def test_list_artifacts_missing_repo() -> None: ...

@scenario("features/universal_tools.feature", "search_artifacts does not raise when the repo root is missing")
def test_search_artifacts_missing_repo() -> None: ...

"""BDD scenarios for the MCP model writer tools.

These tests call the tool functions directly (without starting an MCP server)
so we can validate deterministic content generation and verifier-gated writes.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

from src.common.model_verifier import ModelRegistry, ModelVerifier
from src.tools import mcp_model_server as tools


scenarios("features/model_write_tools.feature")


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    # Minimal ERP repo root skeleton.
    root = tmp_path / "engagements" / "ENG-TEST" / "work-repositories" / "architecture-repository"
    (root / "model-entities").mkdir(parents=True)
    (root / "connections").mkdir(parents=True)
    (root / "diagram-catalog" / "diagrams").mkdir(parents=True)
    return root


@given("an empty engagement architecture repository")
def empty_repo(repo_root: Path) -> Path:
    return repo_root


@when("I dry-run create an entity", target_fixture="dry_run_result")
def dry_run_create_entity(repo_root: Path) -> dict[str, object]:
    return tools.model_create_entity(
        artifact_type="capability",
        name="My Capability",
        phase_produced="A",
        owner_agent="SA",
        produced_by_skill="SA-PHASE-A",
        summary="A short description.",
        dry_run=True,
        repo_root=str(repo_root),
        repo_scope="engagement",
    )


@then("the dry-run result should include a valid entity verification")
def dry_run_result_valid(dry_run_result: dict[str, object]) -> None:
    verification = dry_run_result["verification"]
    assert isinstance(verification, dict)
    assert verification["file_type"] == "entity"
    assert verification["valid"] is True


@when("I attempt to create a connection referencing unknown entities", target_fixture="conn_error")
def create_connection_unknown_entities(repo_root: Path) -> Exception:
    with pytest.raises(Exception) as exc:
        tools.model_create_connection(
            artifact_type="archimate-serving",
            source="APP-001",
            target="APP-002",
            phase_produced="C",
            owner_agent="SwA",
            dry_run=False,
            repo_root=str(repo_root),
            repo_scope="engagement",
        )
    return exc.value


@then("the call should fail with a helpful error")
def connection_error_helpful(conn_error: Exception) -> None:
    msg = str(conn_error)
    assert "unknown" in msg.lower() or "cannot create" in msg.lower()


def _write_min_entity(repo_root: Path, artifact_id: str, artifact_type: str, name: str) -> Path:
    # Use the same tool in non-dry-run mode so the file matches conventions.
    result = tools.model_create_entity(
        artifact_type=artifact_type,
        name=name,
        phase_produced="C",
        owner_agent="SwA",
        produced_by_skill="SWA-TEST",
        artifact_id=artifact_id,
        dry_run=False,
        repo_root=str(repo_root),
        repo_scope="engagement",
    )
    assert result.get("wrote") is True
    return Path(result["path"])  # type: ignore[arg-type]


@given(
    "an engagement architecture repository with two entities and one connection",
    target_fixture="repo_with_entities_and_connection",
)
def repo_with_entities_and_connection(repo_root: Path) -> Path:
    _write_min_entity(repo_root, "APP-001", "application-component", "EventStore")
    _write_min_entity(repo_root, "APP-016", "application-component", "LangGraph Orchestrator")

    conn = tools.model_create_connection(
        artifact_type="archimate-serving",
        source="APP-001",
        target="APP-016",
        phase_produced="C",
        owner_agent="SwA",
        dry_run=False,
        repo_root=str(repo_root),
        repo_scope="engagement",
    )
    assert conn.get("wrote") is True

    # Sanity: verifier should pass across repo.
    verifier = ModelVerifier(ModelRegistry(repo_root))
    results = verifier.verify_all(repo_root)
    assert all(r.valid for r in results), [i for r in results for i in r.errors]
    return repo_root


@when("I create an archimate diagram with serving connection", target_fixture="diagram_result")
def create_archimate_diagram(repo_with_entities_and_connection: Path) -> dict[str, object]:
    puml = """@startuml phase-c-archimate-application-v999
!include ../_macros.puml
!include ../_archimate-stereotypes.puml

DECL_APP_001
DECL_APP_016

APP_001 -[#0078A0]-> APP_016 : <<serving>>
@enduml
"""
    return tools.model_create_diagram(
        diagram_type="archimate-application",
        name="Test Diagram",
        purpose="Test purpose",
        puml=puml,
        phase_produced="C",
        owner_agent="SwA",
        artifact_id="phase-c-archimate-application-v999",
        dry_run=False,
        repo_root=str(repo_with_entities_and_connection),
        repo_scope="engagement",
        connection_inference="strict",
    )


@then("the diagram should verify successfully and reference the inferred ids")
def diagram_inferred_ids(diagram_result: dict[str, object], repo_with_entities_and_connection: Path) -> None:
    assert diagram_result.get("wrote") is True

    # Verify the created file.
    p = Path(diagram_result["path"])  # type: ignore[arg-type]
    verifier = ModelVerifier(ModelRegistry(repo_with_entities_and_connection))
    res = verifier.verify_diagram_file(p)
    assert res.valid is True, res.issues

    # Ensure the frontmatter contains the inferred ids.
    content = p.read_text(encoding="utf-8")
    assert "title Test Diagram" in content
    assert "entity-ids-used" in content
    assert "APP-001" in content
    assert "APP-016" in content
    assert "connection-ids-used" in content
    assert "APP-001---APP-016@@archimate-serving" in content

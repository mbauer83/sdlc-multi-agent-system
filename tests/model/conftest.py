"""
Shared fixtures and pytest-bdd step definitions for model verifier BDD tests.

ALL shared Given/Then steps live here so they are automatically available to
every test module in this package without explicit imports.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, then

from src.common.model_verifier import ModelRegistry, ModelVerifier, VerificationResult


# ---------------------------------------------------------------------------
# Canonical valid file content (shared across test modules)
# ---------------------------------------------------------------------------

VALID_ENTITY = textwrap.dedent("""\
    ---
    artifact-id: APP-001
    artifact-type: application-component
    name: "EventStore"
    version: 0.1.0
    status: draft
    phase-produced: C
    owner-agent: SwA
    safety-relevant: false
    produced-by-skill: SWA-PHASE-C-APP
    last-updated: 2026-04-04
    engagement: ENG-001
    ---

    <!-- §content -->

    ## EventStore

    The EventStore.

    ## Properties

    | Attribute | Value |
    |---|---|
    | Module | src/events/event_store.py |

    <!-- §display -->

    ### archimate

    ```yaml
    layer: Application
    element-type: ApplicationComponent
    label: "EventStore"
    alias: APP_001
    ```
""")

VALID_CONNECTION = textwrap.dedent("""\
    ---
    artifact-id: APP-001---APP-016@@archimate-serving
    artifact-type: archimate-serving
    source: APP-001
    target: APP-016
    version: 0.1.0
    status: draft
    phase-produced: C
    owner-agent: SwA
    engagement: ENG-001
    last-updated: 2026-04-04
    ---

    <!-- §content -->

    EventStore serves LangGraph Orchestrator.

    <!-- §display -->

    ### archimate

    ```yaml
    relationship-type: Serving
    direction: source-to-target
    ```
""")

VALID_ARCHIMATE_DIAGRAM = textwrap.dedent("""\
    ' ---
    ' artifact-id: phase-c-archimate-application-v1
    ' artifact-type: diagram
    ' name: "Application Architecture"
    ' diagram-type: archimate-application
    ' version: 0.1.0
    ' status: draft
    ' phase-produced: C
    ' owner-agent: SwA
    ' engagement: ENG-001
    ' entity-ids-used: [APP-001, APP-016]
    ' connection-ids-used: [APP-001---APP-016@@archimate-serving]
    ' ---
    @startuml
    title Application Architecture
    !include ../_macros.puml
    !include ../_archimate-stereotypes.puml
    APP_001 --> APP_016 : <<serving>>
    @enduml
""")


# ---------------------------------------------------------------------------
# Shared Given steps — verifier construction
# ---------------------------------------------------------------------------


@given("a ModelVerifier with no registry", target_fixture="verifier")
def verifier_no_registry() -> ModelVerifier:
    return ModelVerifier(registry=None)


@given(
    'a ModelVerifier with a registry containing "APP-001" and "APP-016"',
    target_fixture="verifier",
)
def verifier_with_two_entities(tmp_path: Path) -> ModelVerifier:
    registry = _build_registry(
        tmp_path,
        entities={"APP-001": "application-component", "APP-016": "application-component"},
        connections={},
    )
    return ModelVerifier(registry=registry)


@given("a ModelVerifier with a full registry", target_fixture="verifier")
def verifier_full(tmp_path: Path) -> ModelVerifier:
    """Registry with APP-001, APP-016, and connection APP-001---APP-016@@archimate-serving."""
    registry = _build_registry(
        tmp_path,
        entities={"APP-001": "application-component", "APP-016": "application-component"},
        connections={"APP-001---APP-016@@archimate-serving": "archimate-serving"},
    )
    return ModelVerifier(registry=registry)


@given(
    "a ModelVerifier with a unified registry containing enterprise and engagement entities",
    target_fixture="verifier",
)
def verifier_unified_registry(tmp_path: Path) -> ModelVerifier:
    """Registry mounted over engagement + enterprise roots.

    Enterprise root must be named "enterprise-repository" so scope detection works.
    """

    engagement_root = tmp_path / "engagement-architecture-repository"
    enterprise_root = tmp_path / "enterprise-repository"

    # Engagement entity
    _build_registry(
        engagement_root,
        entities={"APP-001": "application-component"},
        connections={},
    )

    # Enterprise entity (omit engagement field; registry derives engagement="enterprise")
    ent_dir = enterprise_root / "model-entities" / "application" / "components"
    ent_dir.mkdir(parents=True, exist_ok=True)
    (ent_dir / "APP-900.md").write_text(
        textwrap.dedent("""\
            ---
            artifact-id: APP-900
            artifact-type: application-component
            name: "APP-900 stub"
            version: 1.0.0
            status: baselined
            phase-produced: A
            owner-agent: SA
            safety-relevant: false
            last-updated: 2026-04-04
            ---

            <!-- §content -->

            ## APP-900 stub

            ## Properties

            | Attribute | Value |
            |---|---|
            | Module | stub |

            <!-- §display -->

            ### archimate

            ```yaml
            layer: Application
            element-type: ApplicationComponent
            label: "APP-900"
            alias: APP_900
            ```
        """),
        encoding="utf-8",
    )

    registry = ModelRegistry([engagement_root, enterprise_root])
    return ModelVerifier(registry=registry)


# ---------------------------------------------------------------------------
# Shared Then steps
# ---------------------------------------------------------------------------


@then("the result is valid")
def result_is_valid(result: VerificationResult) -> None:
    assert result.valid, f"Expected valid but got errors: {result.errors}"


@then("the result is invalid")
def result_is_invalid(result: VerificationResult) -> None:
    assert not result.valid, "Expected invalid result but got no errors"


@then("there are no errors")
def no_errors(result: VerificationResult) -> None:
    assert result.errors == [], f"Unexpected errors: {result.errors}"


@then(parsers.parse('error code "{code}" is reported'))
def error_code_reported(result: VerificationResult, code: str) -> None:
    codes = [i.code for i in result.errors]
    assert code in codes, f"Expected error {code} but got: {codes}"


@then(parsers.parse('warning code "{code}" is reported'))
def warning_code_reported(result: VerificationResult, code: str) -> None:
    codes = [i.code for i in result.warnings]
    assert code in codes, f"Expected warning {code} but got: {codes}"


@then("the invalid connection result has errors")
def invalid_conn_has_errors(all_results: list[VerificationResult]) -> None:
    conn_results = [r for r in all_results if r.file_type == "connection"]
    assert conn_results, "No connection results found"
    assert any(not r.valid for r in conn_results), (
        f"Expected at least one invalid connection result; got: {conn_results}"
    )


@then("the valid entity result has no errors")
def valid_entity_no_errors(all_results: list[VerificationResult]) -> None:
    entity_results = [r for r in all_results if r.file_type == "entity"]
    assert entity_results, "No entity results found"
    valid_entities = [r for r in entity_results if r.valid]
    assert valid_entities, (
        f"Expected at least one valid entity result; errors: "
        f"{[r.errors for r in entity_results]}"
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_registry(
    root: Path,
    entities: dict[str, str],
    connections: dict[str, str],
) -> ModelRegistry:
    """Write minimal stub files and return a ModelRegistry over them."""
    entities_dir = root / "model-entities" / "application" / "components"
    entities_dir.mkdir(parents=True, exist_ok=True)

    for aid, atype in entities.items():
        (entities_dir / f"{aid}.md").write_text(
            textwrap.dedent(f"""\
                ---
                artifact-id: {aid}
                artifact-type: {atype}
                name: "{aid} stub"
                version: 0.1.0
                status: draft
                phase-produced: C
                owner-agent: SwA
                safety-relevant: false
                last-updated: 2026-04-04
                engagement: ENG-001
                ---

                <!-- §content -->

                ## {aid} stub

                ## Properties

                | Attribute | Value |
                |---|---|
                | Module | stub |

                <!-- §display -->

                ### archimate

                ```yaml
                layer: Application
                element-type: ApplicationComponent
                label: "{aid}"
                alias: {aid.replace('-', '_')}
                ```
            """),
            encoding="utf-8",
        )

    if connections:
        conn_dir = root / "connections" / "archimate" / "serving"
        conn_dir.mkdir(parents=True, exist_ok=True)
        for cid, ctype in connections.items():
            endpoint_part = cid.split("@@", 1)[0]
            source_id, target_id = endpoint_part.split("---", 1)
            (conn_dir / f"{cid}.md").write_text(
                textwrap.dedent(f"""\
                    ---
                    artifact-id: {cid}
                    artifact-type: {ctype}
                    source: {source_id}
                    target: {target_id}
                    version: 0.1.0
                    status: draft
                    phase-produced: C
                    owner-agent: SwA
                    engagement: ENG-001
                    last-updated: 2026-04-04
                    ---

                    <!-- §content -->

                    Stub connection.

                    <!-- §display -->

                    ### archimate

                    ```yaml
                    relationship-type: Serving
                    direction: source-to-target
                    ```
                """),
                encoding="utf-8",
            )

    return ModelRegistry(root)


def write_entity(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_connection(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_diagram(path: Path, content: str) -> Path:
    """Write a diagram file and ensure stub includes exist in the catalog root."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    # PlantUML resolves !include paths relative to the diagram file.
    # Stubs must exist at <catalog-root>/_macros.puml and
    # <catalog-root>/_archimate-stereotypes.puml so that -checkonly succeeds.
    catalog_root = path.parent.parent  # diagrams/ → diagram-catalog/
    for stub in ("_macros.puml", "_archimate-stereotypes.puml"):
        stub_path = catalog_root / stub
        if not stub_path.exists():
            stub_path.write_text(f"' stub {stub}\n", encoding="utf-8")
    return path

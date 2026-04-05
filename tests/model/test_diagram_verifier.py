"""
BDD step definitions for diagram_verifier.feature.

Shared Given/Then steps are in conftest.py.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from pytest_bdd import given, scenarios, when

from src.common.model_verifier import ModelVerifier, VerificationResult
from tests.model.conftest import (
    VALID_ARCHIMATE_DIAGRAM,
    VALID_CONNECTION,
    VALID_ENTITY,
    _build_registry,
    write_connection,
    write_diagram,
    write_entity,
)

scenarios("features/diagram_verifier.feature")


# ---------------------------------------------------------------------------
# Given — diagram file creation
# ---------------------------------------------------------------------------


@given(
    "a well-formed ArchiMate diagram referencing known entities and connections",
    target_fixture="diagram_file",
)
def valid_diagram(tmp_path: Path) -> Path:
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(
        diag_dir / "phase-c-archimate-application-v1.puml", VALID_ARCHIMATE_DIAGRAM
    )


@given("a .puml file with no frontmatter comment block", target_fixture="diagram_file")
def diagram_no_frontmatter(tmp_path: Path) -> Path:
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(
        diag_dir / "no-frontmatter.puml",
        textwrap.dedent("""\
            @startuml
            APP-001 --> APP-016
            @enduml
        """),
    )


@given(
    "a .puml file with invalid YAML in its frontmatter comment block",
    target_fixture="diagram_file",
)
def diagram_bad_yaml(tmp_path: Path) -> Path:
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(
        diag_dir / "bad-yaml.puml",
        textwrap.dedent("""\
            ' ---
            ' artifact-id: bad-yaml
            ' name: [unclosed
            ' ---
            @startuml
            @enduml
        """),
    )


@given('a diagram file missing the "diagram-type" field', target_fixture="diagram_file")
def diagram_missing_field(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace("' diagram-type: archimate-application\n", "")
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given(
    'a diagram file whose entity-ids-used includes "APP-999"',
    target_fixture="diagram_file",
)
def diagram_unknown_entity(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace(
        "' entity-ids-used: [APP-001, APP-016]",
        "' entity-ids-used: [APP-001, APP-016, APP-999]",
    )
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given(
    'a diagram file whose connection-ids-used includes "APP-001---APP-999"',
    target_fixture="diagram_file",
)
def diagram_unknown_connection(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace(
        "' connection-ids-used: [APP-001---APP-016]",
        "' connection-ids-used: [APP-001---APP-016, APP-001---APP-999]",
    )
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given(
    'a baselined diagram whose entity-ids-used includes a draft entity "APP-001"',
    target_fixture="diagram_file",
)
def diagram_baselined_draft_entity(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace("' status: draft", "' status: baselined")
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given(
    'a draft diagram whose entity-ids-used includes a draft entity "APP-001"',
    target_fixture="diagram_file",
)
def diagram_draft_draft_entity(tmp_path: Path) -> Path:
    # VALID_ARCHIMATE_DIAGRAM is already draft with APP-001 in entity-ids-used
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", VALID_ARCHIMATE_DIAGRAM)


@given("an ArchiMate diagram that does not include _macros.puml", target_fixture="diagram_file")
def diagram_no_macros(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace(
        "!include ../_macros.puml\n", ""
    ).replace("!include ../_archimate-stereotypes.puml\n", "")
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given(
    "an ArchiMate diagram that includes _macros.puml but not _archimate-stereotypes.puml",
    target_fixture="diagram_file",
)
def diagram_no_stereotypes(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace("!include ../_archimate-stereotypes.puml\n", "")
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given("a diagram file without @startuml", target_fixture="diagram_file")
def diagram_no_startuml(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace("@startuml\n", "")
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given("a diagram file without @enduml", target_fixture="diagram_file")
def diagram_no_enduml(tmp_path: Path) -> Path:
    content = VALID_ARCHIMATE_DIAGRAM.replace("@enduml\n", "")
    diag_dir = tmp_path / "diagram-catalog" / "diagrams"
    return write_diagram(diag_dir / "phase-c-archimate-application-v1.puml", content)


@given(
    "an architecture repository with one valid entity and one invalid connection",
    target_fixture="repo_path",
)
def repo_with_mixed_files(tmp_path: Path) -> Path:
    entity_dir = tmp_path / "model-entities" / "application" / "components"
    write_entity(entity_dir / "APP-001.md", VALID_ENTITY)
    # Invalid: artifact-id does not match filename stem
    bad_conn = VALID_CONNECTION.replace(
        "artifact-id: APP-001---APP-016", "artifact-id: APP-001---APP-999"
    )
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    write_connection(conn_dir / "APP-001---APP-016.md", bad_conn)
    return tmp_path


@given(
    'an enterprise-scope diagram whose entity-ids-used includes engagement entity "APP-001"',
    target_fixture="diagram_file",
)
def enterprise_diagram_refs_engagement(tmp_path: Path) -> Path:
    # Enterprise scope is derived from path containing "enterprise-repository".
    diag_dir = tmp_path / "enterprise-repository" / "diagram-catalog" / "diagrams"
    content = textwrap.dedent("""\
        ' ---
        ' artifact-id: enterprise-archimate-v1
        ' artifact-type: diagram
        ' name: "Enterprise Diagram"
        ' diagram-type: archimate-application
        ' version: 1.0.0
        ' status: baselined
        ' phase-produced: A
        ' owner-agent: SA
        ' entity-ids-used: [APP-001]
        ' connection-ids-used: []
        ' ---
        @startuml
        !include ../_macros.puml
        APP_001()
        @enduml
    """)
    return write_diagram(diag_dir / "enterprise-archimate-v1.puml", content)


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when("I verify the diagram file", target_fixture="result")
def verify_diagram(verifier: ModelVerifier, diagram_file: Path) -> VerificationResult:
    return verifier.verify_diagram_file(diagram_file)


@when("I run verify_all on the repository", target_fixture="all_results")
def run_verify_all(verifier: ModelVerifier, repo_path: Path) -> list[VerificationResult]:
    return verifier.verify_all(repo_path, include_diagrams=False)

"""
BDD step definitions for entity_verifier.feature.

Shared Given/Then steps are in conftest.py. This module contains only entity-specific
file-creation Given steps and the When step.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from pytest_bdd import given, scenarios, when

from src.common.model_verifier import ModelVerifier, VerificationResult
from tests.model.conftest import VALID_ENTITY, write_entity

scenarios("features/entity_verifier.feature")


# ---------------------------------------------------------------------------
# Given — entity file creation
# ---------------------------------------------------------------------------


@given("a well-formed entity file with all required fields", target_fixture="entity_file")
def valid_entity_file(tmp_path: Path) -> Path:
    return write_entity(tmp_path / "APP-001.md", VALID_ENTITY)


@given("an entity file that does not start with ---", target_fixture="entity_file")
def entity_no_frontmatter(tmp_path: Path) -> Path:
    return write_entity(tmp_path / "APP-001.md", "No frontmatter here\n\n## Content\n")


@given("an entity file whose frontmatter --- is never closed", target_fixture="entity_file")
def entity_unclosed_frontmatter(tmp_path: Path) -> Path:
    return write_entity(
        tmp_path / "APP-001.md",
        textwrap.dedent("""\
            ---
            artifact-id: APP-001
            artifact-type: application-component
        """),
    )


@given("an entity file with invalid YAML in the frontmatter", target_fixture="entity_file")
def entity_bad_yaml(tmp_path: Path) -> Path:
    return write_entity(
        tmp_path / "APP-001.md",
        textwrap.dedent("""\
            ---
            artifact-id: APP-001
            name: [unclosed bracket
            ---

            <!-- §content -->

            ## APP-001

            ## Properties

            | A | B |
            |---|---|

            <!-- §display -->
        """),
    )


@given('an entity file that is missing the "safety-relevant" field', target_fixture="entity_file")
def entity_missing_safety_relevant(tmp_path: Path) -> Path:
    return write_entity(tmp_path / "APP-001.md", VALID_ENTITY.replace("safety-relevant: false\n", ""))


@given('an entity file with artifact-id "app-001"', target_fixture="entity_file")
def entity_bad_artifact_id(tmp_path: Path) -> Path:
    return write_entity(
        tmp_path / "app-001.md",
        VALID_ENTITY.replace("artifact-id: APP-001", "artifact-id: app-001"),
    )


@given('an entity file with artifact-type "unknown-widget"', target_fixture="entity_file")
def entity_bad_artifact_type(tmp_path: Path) -> Path:
    return write_entity(
        tmp_path / "APP-001.md",
        VALID_ENTITY.replace("artifact-type: application-component", "artifact-type: unknown-widget"),
    )


@given('an entity file with safety-relevant set to the string "yes"', target_fixture="entity_file")
def entity_bad_safety_relevant(tmp_path: Path) -> Path:
    return write_entity(
        tmp_path / "APP-001.md",
        VALID_ENTITY.replace("safety-relevant: false", "safety-relevant: 'yes'"),
    )


@given('an entity file with status "pending"', target_fixture="entity_file")
def entity_bad_status(tmp_path: Path) -> Path:
    return write_entity(
        tmp_path / "APP-001.md",
        VALID_ENTITY.replace("status: draft", "status: pending"),
    )


@given('an entity file without a "§content" section marker', target_fixture="entity_file")
def entity_no_content_section(tmp_path: Path) -> Path:
    return write_entity(tmp_path / "APP-001.md", VALID_ENTITY.replace("<!-- §content -->", ""))


@given('an entity file without a "§display" section marker', target_fixture="entity_file")
def entity_no_display_section(tmp_path: Path) -> Path:
    return write_entity(tmp_path / "APP-001.md", VALID_ENTITY.replace("<!-- §display -->", ""))


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when("I verify the entity file", target_fixture="result")
def verify_entity(verifier: ModelVerifier, entity_file: Path) -> VerificationResult:
    return verifier.verify_entity_file(entity_file)

"""
BDD step definitions for connection_verifier.feature.

Shared Given/Then steps are in conftest.py.
"""

from __future__ import annotations

from pathlib import Path

from pytest_bdd import given, scenarios, when

from src.common.model_verifier import ModelVerifier, VerificationResult
from tests.model.conftest import VALID_CONNECTION, write_connection

scenarios("features/connection_verifier.feature")


# ---------------------------------------------------------------------------
# Given — connection file creation
# ---------------------------------------------------------------------------


@given("a well-formed connection file referencing known entities", target_fixture="conn_file")
def valid_connection_file(tmp_path: Path) -> Path:
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-016@@archimate-serving.md", VALID_CONNECTION)


@given(
    "a connection file whose artifact-id does not match its filename stem",
    target_fixture="conn_file",
)
def conn_id_mismatch(tmp_path: Path) -> Path:
    content = VALID_CONNECTION.replace(
        "artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: APP-001---APP-017"
    )
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-016@@archimate-serving.md", content)


@given('a connection file with artifact-id "app001---app016"', target_fixture="conn_file")
def conn_bad_format(tmp_path: Path) -> Path:
    content = VALID_CONNECTION.replace(
        "artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: app001---app016"
    )
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "app001---app016.md", content)


@given('a connection file whose source is "APP-999"', target_fixture="conn_file")
def conn_unknown_source(tmp_path: Path) -> Path:
    content = (
        VALID_CONNECTION
        .replace("artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: APP-999---APP-016@@archimate-serving")
        .replace("source: APP-001", "source: APP-999")
        .replace("target: APP-016", "target: APP-016")
    )
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-999---APP-016@@archimate-serving.md", content)


@given('a connection file whose target is "APP-999"', target_fixture="conn_file")
def conn_unknown_target(tmp_path: Path) -> Path:
    content = (
        VALID_CONNECTION
        .replace("artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: APP-001---APP-999@@archimate-serving")
        .replace("target: APP-016", "target: APP-999")
    )
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-999@@archimate-serving.md", content)


@given('a connection file with artifact-type "archimate-unknown"', target_fixture="conn_file")
def conn_bad_type(tmp_path: Path) -> Path:
    content = VALID_CONNECTION.replace(
        "artifact-type: archimate-serving", "artifact-type: archimate-unknown"
    )
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-016@@archimate-serving.md", content)


@given('a connection file without a "§display" section', target_fixture="conn_file")
def conn_no_display(tmp_path: Path) -> Path:
    content = VALID_CONNECTION.replace("<!-- §display -->", "")
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-016@@archimate-serving.md", content)


@given('a connection file without a "§content" section', target_fixture="conn_file")
def conn_no_content(tmp_path: Path) -> Path:
    content = VALID_CONNECTION.replace("<!-- §content -->", "")
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-016@@archimate-serving.md", content)


@given(
    'a connection file referencing "APP-001" and "APP-016"',
    target_fixture="conn_file",
)
def conn_valid_no_registry(tmp_path: Path) -> Path:
    conn_dir = tmp_path / "connections" / "archimate" / "serving"
    return write_connection(conn_dir / "APP-001---APP-016@@archimate-serving.md", VALID_CONNECTION)


@given('an enterprise-scope connection file without an "engagement" field', target_fixture="conn_file")
def enterprise_connection_no_engagement(tmp_path: Path) -> Path:
    root = tmp_path / "enterprise-repository" / "connections" / "archimate" / "serving"
    content = VALID_CONNECTION.replace("engagement: ENG-001\n", "").replace(
        "artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: APP-900---APP-900@@archimate-serving"
    ).replace("source: APP-001", "source: APP-900").replace("target: APP-016", "target: APP-900")
    return write_connection(root / "APP-900---APP-900@@archimate-serving.md", content)


@given("an enterprise-scope connection referencing an engagement entity", target_fixture="conn_file")
def enterprise_connection_refs_engagement(tmp_path: Path) -> Path:
    root = tmp_path / "enterprise-repository" / "connections" / "archimate" / "serving"
    # Enterprise connection references APP-001 (engagement) -> should be rejected (E210)
    content = (
        VALID_CONNECTION.replace("engagement: ENG-001\n", "")
        .replace("artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: APP-900---APP-001@@archimate-serving")
        .replace("source: APP-001", "source: APP-900")
        .replace("target: APP-016", "target: APP-001")
    )
    return write_connection(root / "APP-900---APP-001@@archimate-serving.md", content)


@given("an engagement-scope connection referencing an enterprise entity", target_fixture="conn_file")
def engagement_connection_refs_enterprise(tmp_path: Path) -> Path:
    root = tmp_path / "connections" / "archimate" / "serving"
    # Engagement connection references APP-900 (enterprise) -> allowed
    content = (
        VALID_CONNECTION.replace("artifact-id: APP-001---APP-016@@archimate-serving", "artifact-id: APP-001---APP-900@@archimate-serving")
        .replace("target: APP-016", "target: APP-900")
    )
    return write_connection(root / "APP-001---APP-900@@archimate-serving.md", content)


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when("I verify the connection file", target_fixture="result")
def verify_connection(verifier: ModelVerifier, conn_file: Path) -> VerificationResult:
    return verifier.verify_connection_file(conn_file)

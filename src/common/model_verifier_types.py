from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from src.common.archimate_types import ALL_CONNECTION_TYPES, ALL_ENTITY_TYPES


class Severity:
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    location: str


@dataclass
class VerificationResult:
    path: Path
    file_type: Literal["entity", "connection", "diagram"]
    issues: list[Issue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    def __repr__(self) -> str:
        status = "PASS" if self.valid else "FAIL"
        return f"VerificationResult({status}, {self.path.name}, {len(self.issues)} issues)"


@dataclass(frozen=True)
class VerifierRuntimeConfig:
    mode: Literal["full", "incremental"]
    state_dir: Path
    changed_ratio_threshold: float
    changed_count_threshold: int
    log_mode: bool


@dataclass
class IncrementalState:
    schema_version: int
    engine_signature: str
    include_diagrams: bool
    git_head: str | None
    snapshots: dict[str, dict[str, int | str]]
    results: dict[str, dict]


@dataclass(frozen=True)
class ConnectionRefs:
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]


def entity_id_from_path(path: Path) -> str:
    return path.stem.split(".")[0]


ENTITY_ID_RE = re.compile(r"^[A-Z]+-\d{3}$")
CONN_ID_ALLOWED_CHARS_RE = re.compile(r"^[A-Za-z0-9@-]+$")


def connection_artifact_id_matches_shape(artifact_id: str) -> bool:
    if not CONN_ID_ALLOWED_CHARS_RE.match(artifact_id):
        return False
    source_target, relation_suffix = _split_once(artifact_id, "@@")
    if source_target is None or relation_suffix is None:
        return False
    if not _is_valid_relation_suffix(relation_suffix):
        return False
    source_part, target_part = _split_once(source_target, "---")
    if source_part is None or target_part is None:
        return False
    return _is_valid_connection_side(source_part) and _is_valid_connection_side(target_part)


def _split_once(value: str, separator: str) -> tuple[str | None, str | None]:
    parts = value.split(separator)
    if len(parts) != 2:
        return None, None
    left, right = parts
    if not left or not right:
        return None, None
    return left, right


def _is_valid_connection_side(side: str) -> bool:
    return all(ENTITY_ID_RE.match(token) for token in side.split("--"))


def _is_valid_relation_suffix(value: str) -> bool:
    parts = value.split("-")
    return all(part.isalpha() and part.islower() for part in parts)

ENTITY_TYPES: frozenset[str] = ALL_ENTITY_TYPES
CONNECTION_TYPES: frozenset[str] = ALL_CONNECTION_TYPES

VALID_STATUSES: frozenset[str] = frozenset({"draft", "baselined", "deprecated"})
VALID_PHASES: frozenset[str] = frozenset({"Prelim", "A", "B", "C", "D", "E", "F", "G", "H"})
VALID_AGENTS: frozenset[str] = frozenset({"SA", "SwA", "PM", "PO", "DO", "DE", "QA", "CSCO"})

ENTITY_REQUIRED: frozenset[str] = frozenset(
    {
        "artifact-id",
        "artifact-type",
        "name",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "safety-relevant",
        "last-updated",
        "engagement",
    }
)

CONNECTION_REQUIRED: frozenset[str] = frozenset(
    {
        "artifact-id",
        "artifact-type",
        "source",
        "target",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "last-updated",
        "engagement",
    }
)

DIAGRAM_REQUIRED: frozenset[str] = frozenset(
    {
        "artifact-id",
        "artifact-type",
        "name",
        "diagram-type",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "engagement",
    }
)

DIAGRAM_ARTIFACT_TYPES: frozenset[str] = frozenset({"diagram"})

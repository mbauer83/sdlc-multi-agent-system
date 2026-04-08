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
CONN_ID_RE = re.compile(
    r"^[A-Z]+-\d{3}(--[A-Z]+-\d{3})*---[A-Z]+-\d{3}(--[A-Z]+-\d{3})*@@[a-z]+(?:-[a-z]+)*$"
)

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

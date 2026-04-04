"""
ERP v2.0 Model Verifier — entity, connection, and diagram file validation.

Checks syntactic correctness, frontmatter presence/format, and (when a registry
is provided) referential integrity of source/target artifact-ids in connection files
and entity-ids-used/connection-ids-used in diagram files.

Designed for two usage modes:
  1. Stage 5 integration — called by ``write_artifact`` before committing a file.
  2. Standalone / pre-commit — ``ModelVerifier.verify_all(repo_path)`` batch scan.

No exceptions are raised for validation failures; results are accumulated in
``VerificationResult.issues`` so callers receive a full picture of all errors.

Governed by:
  - framework/artifact-schemas/entity-conventions.md
  - framework/artifact-registry-design.md §3–§5
  - framework/diagram-conventions.md §9
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from src.common.archimate_types import ALL_ENTITY_TYPES, ALL_CONNECTION_TYPES

import yaml


# ---------------------------------------------------------------------------
# Public data model
# ---------------------------------------------------------------------------


class Severity:
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    severity: Literal["error", "warning"]
    code: str  # E/W + three-digit number; see ERROR CODES at module bottom
    message: str
    location: str  # file path (optionally ":line")


@dataclass
class VerificationResult:
    """
    Result of verifying a single file.

    ``valid`` is True when there are no ERROR-severity issues; warnings do not
    invalidate a file.
    """

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

    def __repr__(self) -> str:  # noqa: D105
        status = "PASS" if self.valid else "FAIL"
        return f"VerificationResult({status}, {self.path.name}, {len(self.issues)} issues)"


# ---------------------------------------------------------------------------
# Public utility — formal entity-id extraction from filename
# ---------------------------------------------------------------------------


def entity_id_from_path(path: Path) -> str:
    """Extract the formal artifact-id from an entity filename.

    Entity filenames follow the convention ``TYPEABBR-NNN.friendly-name.md``
    (or the legacy ``TYPEABBR-NNN.md``).  The formal ID is always the portion
    of the stem before the first ``'.'``.  Code must use this function rather
    than ``Path.stem`` directly so that friendly-name suffixes are ignored
    transparently.

    Examples::

        entity_id_from_path(Path("CAP-001.phase-execution.md")) == "CAP-001"
        entity_id_from_path(Path("APP-007.pm-agent.md"))        == "APP-007"
        entity_id_from_path(Path("ACT-001.md"))                 == "ACT-001"
    """
    return path.stem.split(".")[0]


# ---------------------------------------------------------------------------
# Registry — lightweight scan of model-entities/ and connections/
# ---------------------------------------------------------------------------


class ModelRegistry:
    """
    Lightweight in-memory registry of known entity and connection artifact-ids.

    Built by scanning frontmatter of .md files under ``model-entities/`` and
    ``connections/`` directories.  The registry is lazy-loaded on first access
    and cached for the lifetime of the object.

    For Stage 5 integration this will be replaced by the full ModelRegistry
    implementation in ``src/agents/``.  The interface (``entity_ids()``,
    ``connection_ids()``) is kept identical so the verifier can accept either.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        # Single cache per domain — id→status populated together on first bulk access.
        self._entity_meta: dict[str, str] | None = None      # entity artifact-id → status
        self._connection_meta: dict[str, str] | None = None  # connection artifact-id → status

    def _ensure_entity_meta(self) -> dict[str, str]:
        """Lazy-load the full entity id→status map (one scan, cached for lifetime)."""
        if self._entity_meta is None:
            self._entity_meta = {}
            root = self.repo_root / "model-entities"
            if root.exists():
                for f in root.rglob("*.md"):
                    try:
                        fm = _parse_frontmatter_from_path(f)
                        if fm and "artifact-id" in fm:
                            self._entity_meta[str(fm["artifact-id"])] = str(
                                fm.get("status", "")
                            )
                    except Exception:  # noqa: BLE001
                        pass
        return self._entity_meta

    def entity_ids(self) -> set[str]:
        """Return the set of all known entity artifact-ids."""
        return set(self._ensure_entity_meta().keys())

    def entity_status(self, artifact_id: str) -> str | None:
        """Return the status of a single entity without forcing a full scan.

        If the full cache is already warm, uses it (O(1)).  Otherwise locates the
        entity file directly via ``find_file_by_id`` and reads only that file —
        efficient for spot-checks on individual entities.
        """
        if self._entity_meta is not None:
            return self._entity_meta.get(artifact_id)
        # Cache not warm — targeted single-file lookup avoids scanning everything.
        f = self.find_file_by_id(artifact_id)
        if f is None:
            return None
        fm = _parse_frontmatter_from_path(f)
        if fm is None:
            return None
        status = str(fm.get("status", ""))
        return status or None

    def entity_statuses(self) -> dict[str, str]:
        """Return a full artifact-id → status mapping (bulk; triggers full scan)."""
        return dict(self._ensure_entity_meta())

    def connection_ids(self) -> set[str]:
        """Return the set of all known connection artifact-ids."""
        return set(self._ensure_connection_meta().keys())

    def connection_status(self, artifact_id: str) -> str | None:
        """Return the status of a single connection without forcing a full scan.

        If the full cache is already warm, uses it (O(1)).  Otherwise locates the
        connection file directly and reads only that file — efficient for
        spot-checks on individual connections.
        """
        if self._connection_meta is not None:
            return self._connection_meta.get(artifact_id)
        # Cache not warm — targeted single-file lookup.
        root = self.repo_root / "connections"
        if root.exists():
            for f in root.rglob("*.md"):
                if f.stem == artifact_id:
                    fm = _parse_frontmatter_from_path(f)
                    if fm:
                        return str(fm.get("status", "")) or None
        return None

    def _ensure_connection_meta(self) -> dict[str, str]:
        """Lazy-load the full connection id→status map (one scan, cached)."""
        if self._connection_meta is None:
            self._connection_meta = {}
            root = self.repo_root / "connections"
            if root.exists():
                for f in root.rglob("*.md"):
                    try:
                        fm = _parse_frontmatter_from_path(f)
                        if fm and "artifact-id" in fm:
                            self._connection_meta[str(fm["artifact-id"])] = str(
                                fm.get("status", "")
                            )
                    except Exception:  # noqa: BLE001
                        pass
        return self._connection_meta

    @staticmethod
    def _scan(root: Path) -> set[str]:
        ids: set[str] = set()
        if not root.exists():
            return ids
        for f in root.rglob("*.md"):
            try:
                fm = _parse_frontmatter_from_path(f)
                if fm and "artifact-id" in fm:
                    ids.add(str(fm["artifact-id"]))
            except Exception:  # noqa: BLE001
                pass
        return ids

    def find_file_by_id(self, artifact_id: str) -> Path | None:
        """Return the Path of an entity file whose formal artifact-id matches *artifact_id*.

        Supports both the legacy ``TYPEABBR-NNN.md`` format and the new
        ``TYPEABBR-NNN.friendly-name.md`` format.  The formal ID is always the
        portion of the stem before the first ``'.'``.
        """
        root = self.repo_root / "model-entities"
        if not root.exists():
            return None
        for f in root.rglob("*.md"):
            if entity_id_from_path(f) == artifact_id:
                return f
        return None


# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------

_ENTITY_ID_RE = re.compile(r"^[A-Z]+-[0-9]{3}$")
_CONN_ID_RE = re.compile(
    r"^[A-Z]+-[0-9]{3}(--[A-Z]+-[0-9]{3})*---[A-Z]+-[0-9]{3}(--[A-Z]+-[0-9]{3})*$"
)

# Canonical type sets — imported from archimate_types.py (single source of truth).
# Do not add types here; add them to src/common/archimate_types.py instead.
_ENTITY_TYPES: frozenset[str] = ALL_ENTITY_TYPES
_CONNECTION_TYPES: frozenset[str] = ALL_CONNECTION_TYPES

_VALID_STATUSES: frozenset[str] = frozenset({"draft", "baselined", "deprecated"})
_VALID_PHASES: frozenset[str] = frozenset({"Prelim", "A", "B", "C", "D", "E", "F", "G", "H"})
_VALID_AGENTS: frozenset[str] = frozenset({"SA", "SwA", "PM", "PO", "DO", "DE", "QA", "CSCO"})

_ENTITY_REQUIRED: frozenset[str] = frozenset(
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

_CONNECTION_REQUIRED: frozenset[str] = frozenset(
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

_DIAGRAM_REQUIRED: frozenset[str] = frozenset(
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


class ModelVerifier:
    """
    Verifies entity, connection, and diagram files against ERP v2.0 conventions.

    Parameters
    ----------
    registry:
        Optional ``ModelRegistry`` used for referential-integrity checks.  When
        absent, reference checks are skipped (issues noted as warnings).  Pass a
        registry whenever batch-verifying a repository so cross-file checks run.
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify_entity_file(self, path: Path) -> VerificationResult:
        """Verify a model-entity .md file."""
        result = VerificationResult(path=path, file_type="entity")
        loc = str(path)

        content = _read_file(path, result, loc)
        if content is None:
            return result

        fm = _parse_frontmatter(content, result, loc)
        if fm is None:
            return result

        _check_required_fields(fm, _ENTITY_REQUIRED, result, loc)
        _check_artifact_id_entity(fm, result, loc)
        _check_artifact_type(fm, _ENTITY_TYPES, "entity type", result, loc)
        _check_enum(fm, "status", _VALID_STATUSES, result, loc)
        _check_enum(fm, "phase-produced", _VALID_PHASES, result, loc)
        _check_enum(fm, "owner-agent", _VALID_AGENTS, result, loc)
        _check_safety_relevant(fm, result, loc)
        _check_section(content, "§content", required=True, result=result, loc=loc)
        _check_section(content, "§display", required=True, result=result, loc=loc)

        return result

    def verify_connection_file(self, path: Path) -> VerificationResult:
        """Verify a model-connection .md file."""
        result = VerificationResult(path=path, file_type="connection")
        loc = str(path)

        content = _read_file(path, result, loc)
        if content is None:
            return result

        fm = _parse_frontmatter(content, result, loc)
        if fm is None:
            return result

        _check_required_fields(fm, _CONNECTION_REQUIRED, result, loc)
        _check_artifact_id_connection(fm, path, result, loc)
        _check_artifact_type(fm, _CONNECTION_TYPES, "connection type", result, loc)
        _check_enum(fm, "status", _VALID_STATUSES, result, loc)
        _check_enum(fm, "phase-produced", _VALID_PHASES, result, loc)
        _check_enum(fm, "owner-agent", _VALID_AGENTS, result, loc)

        if self.registry is not None:
            _check_reference_resolution(fm, self.registry.entity_ids(), result, loc)
        else:
            result.issues.append(Issue(
                Severity.WARNING,
                "W001",
                "No ModelRegistry provided; source/target reference checks skipped",
                loc,
            ))

        # §content is optional on connections (prose description), warn if absent
        _check_section(content, "§content", required=False, result=result, loc=loc)
        _check_section(content, "§display", required=True, result=result, loc=loc)

        return result

    def verify_diagram_file(self, path: Path) -> VerificationResult:
        """Verify a diagram .puml file."""
        result = VerificationResult(path=path, file_type="diagram")
        loc = str(path)

        content = _read_file(path, result, loc)
        if content is None:
            return result

        fm = _parse_puml_frontmatter(content, result, loc)
        if fm is None:
            return result

        _check_required_fields(fm, _DIAGRAM_REQUIRED, result, loc)
        _check_enum(fm, "status", _VALID_STATUSES, result, loc)
        _check_enum(fm, "phase-produced", _VALID_PHASES, result, loc)
        _check_enum(fm, "owner-agent", _VALID_AGENTS, result, loc)

        if self.registry is not None:
            _check_diagram_references(fm, self.registry, result, loc)
        else:
            result.issues.append(Issue(
                Severity.WARNING,
                "W002",
                "No ModelRegistry provided; entity/connection reference checks skipped",
                loc,
            ))

        _check_puml_structure(content, fm, result, loc)
        _check_puml_syntax(path, result, loc)

        return result

    def verify_all(
        self,
        repo_path: Path,
        *,
        include_diagrams: bool = True,
    ) -> list[VerificationResult]:
        """
        Batch-verify all entity, connection, and (optionally) diagram files under
        ``repo_path``.

        ``repo_path`` should be an architecture-repository root containing
        ``model-entities/``, ``connections/``, and ``diagram-catalog/``.

        Results are ordered: entities first, then connections, then diagrams.
        """
        results: list[VerificationResult] = []

        model_entities = repo_path / "model-entities"
        if model_entities.exists():
            for f in sorted(model_entities.rglob("*.md")):
                results.append(self.verify_entity_file(f))

        connections = repo_path / "connections"
        if connections.exists():
            for f in sorted(connections.rglob("*.md")):
                results.append(self.verify_connection_file(f))

        if include_diagrams:
            diagram_dir = repo_path / "diagram-catalog" / "diagrams"
            if diagram_dir.exists():
                for f in sorted(diagram_dir.rglob("*.puml")):
                    results.append(self.verify_diagram_file(f))

        return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _read_file(path: Path, result: VerificationResult, loc: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        result.issues.append(Issue(Severity.ERROR, "E001", f"Cannot read file: {exc}", loc))
        return None


def _parse_frontmatter_from_path(path: Path) -> dict | None:
    """Best-effort frontmatter parse — returns None on any failure."""
    try:
        content = path.read_text(encoding="utf-8")
        return _extract_yaml_block(content)
    except Exception:  # noqa: BLE001
        return None


def _extract_yaml_block(content: str) -> dict | None:
    """Extract the opening --- ... --- YAML block. Returns None if absent."""
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    return yaml.safe_load(content[3:end].strip()) or {}


def _parse_frontmatter(
    content: str, result: VerificationResult, loc: str
) -> dict | None:
    """Parse markdown frontmatter, recording errors into *result*."""
    if not content.startswith("---"):
        result.issues.append(Issue(
            Severity.ERROR, "E011",
            "File does not begin with YAML frontmatter (--- block)",
            loc,
        ))
        return None

    end = content.find("\n---", 3)
    if end == -1:
        result.issues.append(Issue(
            Severity.ERROR, "E012",
            "Frontmatter opening --- has no closing ---",
            loc,
        ))
        return None

    yaml_block = content[3:end].strip()
    try:
        fm = yaml.safe_load(yaml_block)
    except yaml.YAMLError as exc:
        result.issues.append(Issue(
            Severity.ERROR, "E013", f"Frontmatter YAML parse error: {exc}", loc
        ))
        return None

    if not isinstance(fm, dict):
        result.issues.append(Issue(
            Severity.ERROR, "E014", "Frontmatter is not a YAML mapping", loc
        ))
        return None

    return fm


def _parse_puml_frontmatter(
    content: str, result: VerificationResult, loc: str
) -> dict | None:
    """
    Parse the PUML header comment block.

    Format (per diagram-conventions.md §9)::

        ' ---
        ' artifact-id: some-diagram-v1
        ' artifact-type: diagram
        ' ...
        ' ---
        @startuml

    Lines inside the block are prefixed with ``"' "``.  The ``' ---`` delimiters
    are not included in the YAML body.
    """
    lines = content.splitlines()
    in_block = False
    yaml_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        if not in_block:
            if stripped == "' ---":
                in_block = True
                continue
            if stripped == "":
                continue
            # Hit non-blank, non-start-delimiter before block — no frontmatter
            break
        else:
            if stripped == "' ---":
                break  # end delimiter
            if stripped.startswith("' "):
                yaml_lines.append(stripped[2:])
            elif stripped == "'":
                yaml_lines.append("")
            else:
                result.issues.append(Issue(
                    Severity.WARNING,
                    "W302",
                    f"Unexpected line inside PUML frontmatter block: {line!r}",
                    loc,
                ))

    if not yaml_lines:
        result.issues.append(Issue(
            Severity.ERROR,
            "E311",
            "PUML file has no frontmatter header comment block (expected \"' ---\" ... \"' ---\")",
            loc,
        ))
        return None

    try:
        fm = yaml.safe_load("\n".join(yaml_lines))
    except yaml.YAMLError as exc:
        result.issues.append(Issue(
            Severity.ERROR, "E312", f"PUML frontmatter YAML parse error: {exc}", loc
        ))
        return None

    if not isinstance(fm, dict):
        result.issues.append(Issue(
            Severity.ERROR, "E313", "PUML frontmatter is not a YAML mapping", loc
        ))
        return None

    return fm


def _check_required_fields(
    fm: dict, required: frozenset[str], result: VerificationResult, loc: str
) -> None:
    for f in sorted(required):
        if f not in fm or fm[f] is None:
            result.issues.append(Issue(
                Severity.ERROR, "E021",
                f"Required frontmatter field '{f}' is missing or null",
                loc,
            ))


def _check_artifact_id_entity(fm: dict, result: VerificationResult, loc: str) -> None:
    if "artifact-id" not in fm:
        return
    aid = str(fm["artifact-id"])
    if not _ENTITY_ID_RE.match(aid):
        result.issues.append(Issue(
            Severity.ERROR, "E101",
            f"artifact-id '{aid}' does not match pattern ^[A-Z]+-[0-9]{{3}}$",
            loc,
        ))
        return  # filename check meaningless if ID itself is malformed

    # Filename must start with the formal artifact-id (before the first '.').
    # Both legacy "ACT-001.md" and new "ACT-001.friendly-name.md" are accepted.
    file_id = entity_id_from_path(result.path)
    if file_id != aid:
        result.issues.append(Issue(
            Severity.ERROR, "E104",
            (
                f"entity filename prefix '{file_id}' does not match artifact-id '{aid}'; "
                f"filename must start with '{aid}' (e.g. '{aid}.friendly-name.md')"
            ),
            loc,
        ))


def _check_artifact_id_connection(
    fm: dict, path: Path, result: VerificationResult, loc: str
) -> None:
    if "artifact-id" not in fm:
        return
    aid = str(fm["artifact-id"])

    if not _CONN_ID_RE.match(aid):
        result.issues.append(Issue(
            Severity.ERROR, "E201",
            f"connection artifact-id '{aid}' does not match SOURCE(--SOURCE)*---TARGET(--TARGET)* pattern",
            loc,
        ))

    # artifact-id must match filename stem
    stem = path.stem
    if aid != stem:
        result.issues.append(Issue(
            Severity.ERROR, "E202",
            f"artifact-id '{aid}' does not match filename stem '{stem}'",
            loc,
        ))


def _check_artifact_type(
    fm: dict,
    valid: frozenset[str],
    label: str,
    result: VerificationResult,
    loc: str,
) -> None:
    if "artifact-type" not in fm:
        return
    at = str(fm["artifact-type"])
    if at not in valid:
        result.issues.append(Issue(
            Severity.ERROR, "E102",
            f"artifact-type '{at}' is not a recognised {label}",
            loc,
        ))


def _check_enum(
    fm: dict,
    field_name: str,
    valid: frozenset[str],
    result: VerificationResult,
    loc: str,
) -> None:
    if field_name not in fm or fm[field_name] is None:
        return
    value = str(fm[field_name])
    if value not in valid:
        result.issues.append(Issue(
            Severity.ERROR, "E022",
            f"Field '{field_name}' has invalid value '{value}'; expected one of: {sorted(valid)}",
            loc,
        ))


def _check_safety_relevant(fm: dict, result: VerificationResult, loc: str) -> None:
    if "safety-relevant" not in fm:
        return
    val = fm["safety-relevant"]
    if not isinstance(val, bool):
        result.issues.append(Issue(
            Severity.ERROR, "E103",
            f"'safety-relevant' must be a boolean (true/false), got: {val!r}",
            loc,
        ))


def _check_section(
    content: str,
    section: str,
    *,
    required: bool,
    result: VerificationResult,
    loc: str,
) -> None:
    marker = f"<!-- {section} -->"
    if marker not in content:
        severity = Severity.ERROR if required else Severity.WARNING
        code = "E031" if required else "W031"
        result.issues.append(Issue(
            severity, code,
            f"Section marker '{marker}' is {'absent' if required else 'absent (optional for connections)'}",
            loc,
        ))


def _check_reference_resolution(
    fm: dict, known_ids: set[str], result: VerificationResult, loc: str
) -> None:
    """Verify source and target artifact-ids exist in the entity registry."""
    for field_name in ("source", "target"):
        if field_name not in fm or fm[field_name] is None:
            continue
        val = fm[field_name]
        refs = val if isinstance(val, list) else [val]
        for ref in refs:
            if str(ref) not in known_ids:
                result.issues.append(Issue(
                    Severity.ERROR, "E204",
                    f"'{field_name}' references unknown entity '{ref}' (not in ModelRegistry)",
                    loc,
                ))


def _check_diagram_references(
    fm: dict, registry: ModelRegistry, result: VerificationResult, loc: str
) -> None:
    """Check entity-ids-used and connection-ids-used against the registry.

    Status rules (draft-reference checks):
    - E306: a ``baselined`` diagram references a ``draft`` entity.
    - E307: a ``baselined`` diagram references a ``draft`` connection.

    These checks are only enforced when the diagram itself is ``baselined``.
    A ``draft`` diagram may freely reference ``draft`` entities and connections —
    this is normal in-sprint work.  Connections may also reference draft entities
    (they are created alongside the entities they link).  Once a diagram is
    baselined it represents a frozen snapshot, so all referenced entities and
    connections must themselves be baselined.
    """
    diagram_status = str(fm.get("status", ""))
    diagram_is_baselined = diagram_status == "baselined"

    if "entity-ids-used" in fm:
        entity_ids = fm["entity-ids-used"]
        if isinstance(entity_ids, list):
            known = registry.entity_ids()
            for eid in entity_ids:
                eid_str = str(eid)
                if eid_str not in known:
                    result.issues.append(Issue(
                        Severity.ERROR, "E301",
                        f"entity-ids-used references unknown entity '{eid}'",
                        loc,
                    ))
                elif diagram_is_baselined:
                    status = registry.entity_status(eid_str)
                    if status == "draft":
                        result.issues.append(Issue(
                            Severity.ERROR, "E306",
                            f"baselined diagram references draft entity '{eid}' — "
                            "all entities in a baselined diagram must be baselined",
                            loc,
                        ))
        elif entity_ids is not None:
            result.issues.append(Issue(
                Severity.WARNING, "W303",
                "entity-ids-used should be a YAML list",
                loc,
            ))

    if "connection-ids-used" in fm:
        conn_ids = fm["connection-ids-used"]
        if isinstance(conn_ids, list):
            known = registry.connection_ids()
            for cid in conn_ids:
                cid_str = str(cid)
                if cid_str not in known:
                    result.issues.append(Issue(
                        Severity.ERROR, "E302",
                        f"connection-ids-used references unknown connection '{cid}'",
                        loc,
                    ))
                elif diagram_is_baselined:
                    status = registry.connection_status(cid_str)
                    if status == "draft":
                        result.issues.append(Issue(
                            Severity.ERROR, "E307",
                            f"baselined diagram references draft connection '{cid}' — "
                            "all connections in a baselined diagram must be baselined",
                            loc,
                        ))
        elif conn_ids is not None:
            result.issues.append(Issue(
                Severity.WARNING, "W304",
                "connection-ids-used should be a YAML list",
                loc,
            ))


def _check_puml_structure(
    content: str, fm: dict, result: VerificationResult, loc: str
) -> None:
    """Check @startuml/@enduml markers and required !include statements."""
    if "@startuml" not in content:
        result.issues.append(Issue(
            Severity.ERROR, "E304", "@startuml marker is missing", loc
        ))
    if "@enduml" not in content:
        result.issues.append(Issue(
            Severity.ERROR, "E305", "@enduml marker is missing", loc
        ))

    diagram_type = str(fm.get("diagram-type", ""))
    if "archimate" in diagram_type or "usecase" in diagram_type:
        if "_macros.puml" not in content:
            result.issues.append(Issue(
                Severity.ERROR, "E303",
                "ArchiMate/use-case diagram must include _macros.puml",
                loc,
            ))
        if "_archimate-stereotypes.puml" not in content:
            result.issues.append(Issue(
                Severity.WARNING, "W301",
                "ArchiMate/use-case diagram should include _archimate-stereotypes.puml",
                loc,
            ))


def _find_plantuml_jar() -> Path | None:
    """Locate plantuml.jar relative to the project root (tools/plantuml.jar)."""
    # Walk up from this file to find the project root (contains pyproject.toml)
    candidate = Path(__file__).resolve()
    for _ in range(6):
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists():
            jar = candidate / "tools" / "plantuml.jar"
            return jar if jar.exists() else None
    return None


def _check_puml_syntax(path: Path, result: VerificationResult, loc: str) -> None:
    """Run ``plantuml -checkonly`` against the file and surface any syntax errors.

    Requires Java and ``tools/plantuml.jar`` relative to the project root.
    If the JAR or Java is not found, a warning is appended instead of silently
    skipping — this makes missing tooling visible in CI.

    PlantUML exit code 200 indicates syntax errors; each error line is reported
    as E350. Graphviz-not-found IOExceptions are suppressed (not a diagram error).
    """
    jar = _find_plantuml_jar()
    if jar is None:
        result.issues.append(Issue(
            Severity.WARNING, "W350",
            "tools/plantuml.jar not found; PUML syntax check skipped",
            loc,
        ))
        return

    java = os.environ.get("JAVA_HOME", "")
    java_exe = (Path(java) / "bin" / "java") if java else Path("java")

    # Run with -tsvg to a temp dir + verbose: this gives "Error line N in file: ..."
    # which is far more actionable than -checkonly's minimal output.
    # Graphviz-not-found IOExceptions are expected in CI and suppressed.
    try:
        with tempfile.TemporaryDirectory() as tmp_out:
            proc = subprocess.run(
                [
                    str(java_exe), "-jar", str(jar),
                    "-tsvg", "-verbose",
                    "-o", tmp_out,
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
    except FileNotFoundError:
        result.issues.append(Issue(
            Severity.WARNING, "W351",
            "java not found on PATH; PUML syntax check skipped",
            loc,
        ))
        return
    except subprocess.TimeoutExpired:
        result.issues.append(Issue(
            Severity.WARNING, "W352",
            "plantuml render timed out after 30 s",
            loc,
        ))
        return

    if proc.returncode == 0:
        return  # no errors

    combined = proc.stdout + proc.stderr
    # Extract "Error line N in file: ..." lines — these pinpoint the problem
    error_lines = re.findall(r"^Error line \d+ in file:.*$", combined, re.MULTILINE)
    # Also capture "Syntax Error?" lines from SVG error output embedded in stderr
    syntax_lines = re.findall(r"Syntax Error\?.*", combined)

    reported = error_lines or syntax_lines
    if reported:
        for line in reported:
            result.issues.append(Issue(
                Severity.ERROR, "E350",
                f"PlantUML: {line.strip()}",
                loc,
            ))
    else:
        # Non-zero exit but no parseable error lines — surface the first
        # non-noise line so there is at least some signal.
        signal_lines = [
            ln.strip() for ln in combined.splitlines()
            if ln.strip()
            and "IOException" not in ln
            and "Cannot run program" not in ln
            and "Caused by" not in ln
            and "at java." not in ln
            and "at net." not in ln
            and ln.strip() not in ("Some diagram description contains errors",)
        ]
        msg = signal_lines[0] if signal_lines else f"exit {proc.returncode}"
        result.issues.append(Issue(
            Severity.ERROR, "E350",
            f"PlantUML error (exit {proc.returncode}): {msg[:200]}",
            loc,
        ))


# ---------------------------------------------------------------------------
# Error / Warning Code Reference
# ---------------------------------------------------------------------------
#
# E001  File read error (OS error)
# E011  Missing YAML frontmatter opening ---
# E012  Frontmatter --- block never closed
# E013  Frontmatter YAML parse error
# E014  Frontmatter is not a YAML mapping
# E021  Required frontmatter field is missing
# E022  Enum field has invalid value
# E031  Required §section marker is absent
# E101  Entity artifact-id does not match ^[A-Z]+-[0-9]{3}$
# E102  artifact-type not in recognised type set
# E103  safety-relevant is not a boolean
# E104  Entity filename prefix does not match artifact-id
# E201  Connection artifact-id does not match SOURCE---TARGET pattern
# E202  Connection artifact-id does not match filename stem
# E203  Connection artifact-type not recognised
# E204  source/target references unknown entity
# E301  entity-ids-used references unknown entity
# E302  connection-ids-used references unknown connection
# E303  ArchiMate diagram missing !include _macros.puml
# E304  PUML file missing @startuml
# E305  PUML file missing @enduml
# E311  PUML file has no frontmatter header comment block
# E312  PUML frontmatter YAML parse error
# E313  PUML frontmatter is not a YAML mapping
#
# W001  No registry provided — source/target checks skipped
# W002  No registry provided — diagram reference checks skipped
# W031  Optional §content section absent on connection file
# W301  ArchiMate diagram missing _archimate-stereotypes.puml
# W302  Unexpected line inside PUML frontmatter block
# W303  entity-ids-used is not a list
# W304  connection-ids-used is not a list
# E350  PlantUML syntax error reported by plantuml -checkonly
# W350  tools/plantuml.jar not found; syntax check skipped
# W351  java not found on PATH; syntax check skipped
# W352  plantuml -checkonly timed out

from __future__ import annotations

from pathlib import Path
import re
from typing import Literal

from src.common.model_verifier_registry import ModelRegistry
from src.common.model_verifier_types import (
    CONN_ID_RE,
    DIAGRAM_ARTIFACT_TYPES,
    ENTITY_ID_RE,
    Issue,
    Severity,
    VerificationResult,
    entity_id_from_path,
)


def check_required_fields(fm: dict, required: frozenset[str], result: VerificationResult, loc: str) -> None:
    for field_name in sorted(required):
        if field_name not in fm or fm[field_name] is None:
            result.issues.append(Issue(
                Severity.ERROR,
                "E021",
                f"Required frontmatter field '{field_name}' is missing or null",
                loc,
            ))


def check_artifact_id_entity(fm: dict, result: VerificationResult, loc: str) -> None:
    if "artifact-id" not in fm:
        return
    aid = str(fm["artifact-id"])
    if not ENTITY_ID_RE.match(aid):
        result.issues.append(Issue(
            Severity.ERROR,
            "E101",
            f"artifact-id '{aid}' does not match pattern ^[A-Z]+-\\d{{3}}$",
            loc,
        ))
        return

    file_id = entity_id_from_path(result.path)
    if file_id != aid:
        result.issues.append(Issue(
            Severity.ERROR,
            "E104",
            (
                f"entity filename prefix '{file_id}' does not match artifact-id '{aid}'; "
                f"filename must start with '{aid}' (e.g. '{aid}.friendly-name.md')"
            ),
            loc,
        ))


def check_artifact_id_connection(fm: dict, path: Path, result: VerificationResult, loc: str) -> None:
    if "artifact-id" not in fm:
        return
    aid = str(fm["artifact-id"])

    if not CONN_ID_RE.match(aid):
        result.issues.append(Issue(
            Severity.ERROR,
            "E201",
            "connection artifact-id '"
            f"{aid}' does not match SOURCE(--SOURCE)*---TARGET(--TARGET)*@@artifact-type pattern",
            loc,
        ))

    if "@@" in aid and "artifact-type" in fm and fm["artifact-type"] is not None:
        suffix = aid.rsplit("@@", 1)[1]
        artifact_type = str(fm["artifact-type"])
        if suffix != artifact_type:
            result.issues.append(Issue(
                Severity.ERROR,
                "E203",
                (
                    f"connection artifact-id suffix '@@{suffix}' must match artifact-type "
                    f"'{artifact_type}'"
                ),
                loc,
            ))

    if all(k in fm and fm[k] is not None for k in ("source", "target", "artifact-type")):
        source_val = fm["source"]
        target_val = fm["target"]

        source_ids = tuple(str(x) for x in source_val) if isinstance(source_val, list) else (str(source_val),)
        target_ids = tuple(str(x) for x in target_val) if isinstance(target_val, list) else (str(target_val),)
        expected = (
            f"{'--'.join(source_ids)}---{'--'.join(target_ids)}@@{str(fm['artifact-type'])}"
        )
        if aid != expected:
            result.issues.append(Issue(
                Severity.ERROR,
                "E205",
                (
                    f"artifact-id '{aid}' is inconsistent with source/target/artifact-type; "
                    f"expected '{expected}'"
                ),
                loc,
            ))

    if aid != path.stem:
        result.issues.append(Issue(
            Severity.ERROR,
            "E202",
            f"artifact-id '{aid}' does not match filename stem '{path.stem}'",
            loc,
        ))


def check_artifact_type(
    fm: dict,
    valid: frozenset[str],
    label: str,
    result: VerificationResult,
    loc: str,
) -> None:
    if "artifact-type" not in fm:
        return
    artifact_type = str(fm["artifact-type"])
    if artifact_type not in valid:
        result.issues.append(Issue(
            Severity.ERROR,
            "E102",
            f"artifact-type '{artifact_type}' is not a recognised {label}",
            loc,
        ))


def check_enum(
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
            Severity.ERROR,
            "E022",
            f"Field '{field_name}' has invalid value '{value}'; expected one of: {sorted(valid)}",
            loc,
        ))


def check_safety_relevant(fm: dict, result: VerificationResult, loc: str) -> None:
    if "safety-relevant" not in fm:
        return
    if not isinstance(fm["safety-relevant"], bool):
        result.issues.append(Issue(
            Severity.ERROR,
            "E103",
            f"'safety-relevant' must be a boolean (true/false), got: {fm['safety-relevant']!r}",
            loc,
        ))


def check_section(
    content: str,
    section: str,
    *,
    required: bool,
    result: VerificationResult,
    loc: str,
) -> None:
    marker = f"<!-- {section} -->"
    if marker in content:
        return
    severity = Severity.ERROR if required else Severity.WARNING
    code = "E031" if required else "W031"
    msg = f"Section marker '{marker}' is {'absent' if required else 'absent (optional for connections)'}"
    result.issues.append(Issue(severity, code, msg, loc))


def check_reference_resolution_scoped(
    fm: dict,
    registry: ModelRegistry,
    allowed_ids: set[str],
    file_scope: Literal["enterprise", "engagement", "unknown"],
    result: VerificationResult,
    loc: str,
) -> None:
    all_known = registry.entity_ids()
    for field_name in ("source", "target"):
        if field_name not in fm or fm[field_name] is None:
            continue
        val = fm[field_name]
        refs = val if isinstance(val, list) else [val]
        for ref in refs:
            rid = str(ref)
            if rid in allowed_ids:
                continue
            if rid in all_known:
                if file_scope == "enterprise":
                    msg = (
                        f"'{field_name}' references non-enterprise entity '{rid}' "
                        "— enterprise artifacts may only reference enterprise entities"
                    )
                else:
                    msg = f"'{field_name}' references entity '{rid}' outside the allowed scope"
                result.issues.append(Issue(Severity.ERROR, "E210", msg, loc))
            else:
                result.issues.append(Issue(
                    Severity.ERROR,
                    "E204",
                    f"'{field_name}' references unknown entity '{rid}' (not in ModelRegistry)",
                    loc,
                ))


def check_diagram_references_scoped(
    fm: dict,
    registry: ModelRegistry,
    file_scope: Literal["enterprise", "engagement", "unknown"],
    result: VerificationResult,
    loc: str,
) -> None:
    diagram_is_baselined = str(fm.get("status", "")) == "baselined"

    allowed_entities = registry.enterprise_entity_ids() if file_scope == "enterprise" else registry.entity_ids()
    allowed_connections = (
        registry.enterprise_connection_ids() if file_scope == "enterprise" else registry.connection_ids()
    )
    all_entities = registry.entity_ids()
    all_connections = registry.connection_ids()

    _check_entity_ids_used(
        fm,
        registry,
        file_scope,
        allowed_entities,
        all_entities,
        diagram_is_baselined,
        result,
        loc,
    )
    _check_connection_ids_used(
        fm,
        registry,
        file_scope,
        allowed_connections,
        all_connections,
        diagram_is_baselined,
        result,
        loc,
    )


def _check_entity_ids_used(
    fm: dict,
    registry: ModelRegistry,
    file_scope: Literal["enterprise", "engagement", "unknown"],
    allowed_entities: set[str],
    all_entities: set[str],
    diagram_is_baselined: bool,
    result: VerificationResult,
    loc: str,
) -> None:
    if "entity-ids-used" not in fm:
        return
    entity_ids = fm["entity-ids-used"]
    if not isinstance(entity_ids, list):
        if entity_ids is not None:
            result.issues.append(Issue(Severity.WARNING, "W303", "entity-ids-used should be a YAML list", loc))
        return

    for eid in entity_ids:
        eid_str = str(eid)
        if eid_str not in allowed_entities:
            if eid_str in all_entities and file_scope == "enterprise":
                msg = (
                    f"entity-ids-used references non-enterprise entity '{eid_str}' "
                    "— enterprise diagrams may only reference enterprise entities"
                )
                result.issues.append(Issue(Severity.ERROR, "E310", msg, loc))
            else:
                result.issues.append(Issue(
                    Severity.ERROR,
                    "E301",
                    f"entity-ids-used references unknown entity '{eid_str}'",
                    loc,
                ))
            continue

        if diagram_is_baselined and registry.entity_status(eid_str) == "draft":
            result.issues.append(Issue(
                Severity.ERROR,
                "E306",
                f"baselined diagram references draft entity '{eid_str}' — all entities in a baselined diagram must be baselined",
                loc,
            ))


def _check_connection_ids_used(
    fm: dict,
    registry: ModelRegistry,
    file_scope: Literal["enterprise", "engagement", "unknown"],
    allowed_connections: set[str],
    all_connections: set[str],
    diagram_is_baselined: bool,
    result: VerificationResult,
    loc: str,
) -> None:
    if "connection-ids-used" not in fm:
        return
    conn_ids = fm["connection-ids-used"]
    if not isinstance(conn_ids, list):
        if conn_ids is not None:
            result.issues.append(Issue(Severity.WARNING, "W304", "connection-ids-used should be a YAML list", loc))
        return

    for cid in conn_ids:
        cid_str = str(cid)
        if cid_str not in allowed_connections:
            if cid_str in all_connections and file_scope == "enterprise":
                msg = (
                    f"connection-ids-used references non-enterprise connection '{cid_str}' "
                    "— enterprise diagrams may only reference enterprise connections"
                )
                result.issues.append(Issue(Severity.ERROR, "E320", msg, loc))
            else:
                result.issues.append(Issue(
                    Severity.ERROR,
                    "E302",
                    f"connection-ids-used references unknown connection '{cid_str}'",
                    loc,
                ))
            continue

        if diagram_is_baselined and registry.connection_status(cid_str) == "draft":
            result.issues.append(Issue(
                Severity.ERROR,
                "E307",
                (
                    f"baselined diagram references draft connection '{cid_str}' — "
                    "all connections in a baselined diagram must be baselined"
                ),
                loc,
            ))


def check_puml_structure(content: str, fm: dict, result: VerificationResult, loc: str) -> None:
    if "@startuml" not in content:
        result.issues.append(Issue(Severity.ERROR, "E304", "@startuml marker is missing", loc))
    if "@enduml" not in content:
        result.issues.append(Issue(Severity.ERROR, "E305", "@enduml marker is missing", loc))

    body_lines = [line for line in content.splitlines() if not line.lstrip().startswith("'")]
    has_visible_title = any(re.match(r"^\s*title(\s|$)", line, flags=re.IGNORECASE) for line in body_lines)
    if not has_visible_title:
        result.issues.append(Issue(
            Severity.ERROR,
            "E308",
            "Diagram must include a visible title line (for example: 'title <diagram name>')",
            loc,
        ))

    diagram_type = str(fm.get("diagram-type", ""))
    if "archimate" in diagram_type or "usecase" in diagram_type:
        if "_macros.puml" not in content:
            result.issues.append(Issue(
                Severity.ERROR,
                "E303",
                "ArchiMate/use-case diagram must include _macros.puml",
                loc,
            ))
        if "_archimate-stereotypes.puml" not in content:
            result.issues.append(Issue(
                Severity.WARNING,
                "W301",
                "ArchiMate/use-case diagram should include _archimate-stereotypes.puml",
                loc,
            ))


def check_diagram_artifact_type(fm: dict, result: VerificationResult, loc: str) -> None:
    check_artifact_type(fm, DIAGRAM_ARTIFACT_TYPES, "diagram artifact type", result, loc)

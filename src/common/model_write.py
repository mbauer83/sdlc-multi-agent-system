"""model_write.py — Deterministic ERP v2.0 model artifact generation helpers.

This module is intentionally **non-MCP** and contains the reusable, mostly-pure
logic needed to generate ERP v2.0-compliant model artifacts:
- entity/connection type catalogs (writer-side path mapping)
- deterministic ID allocation helpers
- deterministic formatting of entity/connection markdown and diagram PUML header
- best-effort inference of referenced IDs from PUML

I/O (writing files, cache invalidation, macro regeneration, verifier execution)
belongs in tooling/infrastructure (see src/tools/model_write_ops.py).
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

import yaml  # type: ignore[import-untyped]

from src.common.model_verifier import ModelRegistry


DiagramConnectionInferenceMode = Literal["none", "auto", "strict"]


# ---------------------------------------------------------------------------
# Type catalogs (writer-side deterministic path selection)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntityTypeInfo:
    artifact_type: str
    prefix: str
    layer_dir: str  # model-entities/<layer_dir>/...
    subdir: str
    archimate_layer: str
    archimate_element_type: str


@dataclass(frozen=True)
class ConnectionTypeInfo:
    artifact_type: str
    conn_lang: str
    conn_dir: str
    archimate_relationship_type: str | None = None


# These catalogs are the deterministic “writer” mapping tables.
# They are validated exhaustively by tests against src/common/archimate_types.py.
ENTITY_TYPES: dict[str, EntityTypeInfo] = {
    # Motivation
    "stakeholder": EntityTypeInfo("stakeholder", "STK", "motivation", "stakeholders", "Motivation", "Stakeholder"),
    "driver": EntityTypeInfo("driver", "DRV", "motivation", "drivers", "Motivation", "Driver"),
    "assessment": EntityTypeInfo("assessment", "ASS", "motivation", "assessments", "Motivation", "Assessment"),
    "goal": EntityTypeInfo("goal", "GOL", "motivation", "goals", "Motivation", "Goal"),
    "outcome": EntityTypeInfo("outcome", "OUT", "motivation", "outcomes", "Motivation", "Outcome"),
    "principle": EntityTypeInfo("principle", "PRI", "motivation", "principles", "Motivation", "Principle"),
    "requirement": EntityTypeInfo("requirement", "REQ", "motivation", "requirements", "Motivation", "Requirement"),
    "architecture-constraint": EntityTypeInfo(
        "architecture-constraint", "CST", "motivation", "constraints", "Motivation", "Constraint"
    ),
    "meaning": EntityTypeInfo("meaning", "MEA", "motivation", "meanings", "Motivation", "Meaning"),
    "value": EntityTypeInfo("value", "VAL", "motivation", "values", "Motivation", "Value"),
    # Strategy
    "capability": EntityTypeInfo("capability", "CAP", "strategy", "capabilities", "Strategy", "Capability"),
    "value-stream": EntityTypeInfo("value-stream", "VS", "strategy", "value-streams", "Strategy", "ValueStream"),
    "resource": EntityTypeInfo("resource", "RES", "strategy", "resources", "Strategy", "Resource"),
    "course-of-action": EntityTypeInfo(
        "course-of-action", "COA", "strategy", "courses-of-action", "Strategy", "CourseOfAction"
    ),
    # Business
    "business-actor": EntityTypeInfo("business-actor", "ACT", "business", "actors", "Business", "BusinessActor"),
    "business-role": EntityTypeInfo("business-role", "ROL", "business", "roles", "Business", "BusinessRole"),
    "business-collaboration": EntityTypeInfo(
        "business-collaboration", "BCO", "business", "collaborations", "Business", "BusinessCollaboration"
    ),
    "business-interface": EntityTypeInfo(
        "business-interface", "BIF", "business", "interfaces", "Business", "BusinessInterface"
    ),
    "business-process": EntityTypeInfo("business-process", "BPR", "business", "processes", "Business", "BusinessProcess"),
    "business-function": EntityTypeInfo("business-function", "BFN", "business", "functions", "Business", "BusinessFunction"),
    "business-interaction": EntityTypeInfo(
        "business-interaction", "BIA", "business", "interactions", "Business", "BusinessInteraction"
    ),
    "business-event": EntityTypeInfo("business-event", "BEV", "business", "events", "Business", "BusinessEvent"),
    "business-service": EntityTypeInfo("business-service", "BSV", "business", "services", "Business", "BusinessService"),
    "business-object": EntityTypeInfo("business-object", "BOB", "business", "objects", "Business", "BusinessObject"),
    "contract": EntityTypeInfo("contract", "CTR", "business", "contracts", "Business", "Contract"),
    "representation": EntityTypeInfo("representation", "RPR", "business", "representations", "Business", "Representation"),
    "product": EntityTypeInfo("product", "PRD", "business", "products", "Business", "Product"),
    # Application
    "application-component": EntityTypeInfo(
        "application-component", "APP", "application", "components", "Application", "ApplicationComponent"
    ),
    "application-collaboration": EntityTypeInfo(
        "application-collaboration", "ACO", "application", "collaborations", "Application", "ApplicationCollaboration"
    ),
    "application-interface": EntityTypeInfo(
        "application-interface", "AIF", "application", "interfaces", "Application", "ApplicationInterface"
    ),
    "application-function": EntityTypeInfo(
        "application-function", "AFN", "application", "functions", "Application", "ApplicationFunction"
    ),
    "application-interaction": EntityTypeInfo(
        "application-interaction", "AIA", "application", "interactions", "Application", "ApplicationInteraction"
    ),
    "application-process": EntityTypeInfo(
        "application-process", "APR", "application", "processes", "Application", "ApplicationProcess"
    ),
    "application-event": EntityTypeInfo(
        "application-event", "AEV", "application", "events", "Application", "ApplicationEvent"
    ),
    "application-service": EntityTypeInfo(
        "application-service", "ASV", "application", "services", "Application", "ApplicationService"
    ),
    "data-object": EntityTypeInfo("data-object", "DOB", "application", "data-objects", "Application", "DataObject"),
    # Technology
    "technology-node": EntityTypeInfo("technology-node", "NOD", "technology", "nodes", "Technology", "Node"),
    "device": EntityTypeInfo("device", "DEV", "technology", "devices", "Technology", "Device"),
    "system-software": EntityTypeInfo(
        "system-software", "SSW", "technology", "system-software", "Technology", "SystemSoftware"
    ),
    "technology-collaboration": EntityTypeInfo(
        "technology-collaboration", "TCO", "technology", "collaborations", "Technology", "TechnologyCollaboration"
    ),
    "technology-interface": EntityTypeInfo(
        "technology-interface", "TIF", "technology", "interfaces", "Technology", "TechnologyInterface"
    ),
    "path": EntityTypeInfo("path", "PTH", "technology", "paths", "Technology", "Path"),
    "communication-network": EntityTypeInfo(
        "communication-network", "NET", "technology", "networks", "Technology", "CommunicationNetwork"
    ),
    "technology-function": EntityTypeInfo(
        "technology-function", "TFN", "technology", "functions", "Technology", "TechnologyFunction"
    ),
    "technology-process": EntityTypeInfo(
        "technology-process", "TPR", "technology", "processes", "Technology", "TechnologyProcess"
    ),
    "technology-interaction": EntityTypeInfo(
        "technology-interaction", "TIA", "technology", "interactions", "Technology", "TechnologyInteraction"
    ),
    "technology-event": EntityTypeInfo(
        "technology-event", "TEV", "technology", "events", "Technology", "TechnologyEvent"
    ),
    "technology-service": EntityTypeInfo(
        "technology-service", "TSV", "technology", "services", "Technology", "TechnologyService"
    ),
    "artifact": EntityTypeInfo("artifact", "ART", "technology", "artifacts", "Technology", "Artifact"),
    # Physical
    "equipment": EntityTypeInfo("equipment", "EQP", "physical", "equipment", "Physical", "Equipment"),
    "facility": EntityTypeInfo("facility", "FAC", "physical", "facilities", "Physical", "Facility"),
    "distribution-network": EntityTypeInfo(
        "distribution-network", "DIS", "physical", "distribution-networks", "Physical", "DistributionNetwork"
    ),
    "material": EntityTypeInfo("material", "MAT", "physical", "materials", "Physical", "Material"),
    # Implementation
    "work-package": EntityTypeInfo("work-package", "WP", "implementation", "work-packages", "Implementation", "WorkPackage"),
    "deliverable": EntityTypeInfo("deliverable", "DEL", "implementation", "deliverables", "Implementation", "Deliverable"),
    "implementation-event": EntityTypeInfo(
        "implementation-event", "IEV", "implementation", "events", "Implementation", "ImplementationEvent"
    ),
    "plateau": EntityTypeInfo("plateau", "PLT", "implementation", "plateaus", "Implementation", "Plateau"),
    "gap": EntityTypeInfo("gap", "GAP", "implementation", "gaps", "Implementation", "Gap"),
}


CONNECTION_TYPES: dict[str, ConnectionTypeInfo] = {
    # ArchiMate
    "archimate-composition": ConnectionTypeInfo("archimate-composition", "archimate", "composition", "Composition"),
    "archimate-aggregation": ConnectionTypeInfo("archimate-aggregation", "archimate", "aggregation", "Aggregation"),
    "archimate-assignment": ConnectionTypeInfo("archimate-assignment", "archimate", "assignment", "Assignment"),
    "archimate-realization": ConnectionTypeInfo("archimate-realization", "archimate", "realization", "Realization"),
    "archimate-serving": ConnectionTypeInfo("archimate-serving", "archimate", "serving", "Serving"),
    "archimate-access": ConnectionTypeInfo("archimate-access", "archimate", "access", "Access"),
    "archimate-influence": ConnectionTypeInfo("archimate-influence", "archimate", "influence", "Influence"),
    "archimate-association": ConnectionTypeInfo("archimate-association", "archimate", "association", "Association"),
    "archimate-specialization": ConnectionTypeInfo("archimate-specialization", "archimate", "specialization", "Specialization"),
    "archimate-flow": ConnectionTypeInfo("archimate-flow", "archimate", "flow", "Flow"),
    "archimate-triggering": ConnectionTypeInfo("archimate-triggering", "archimate", "triggering", "Triggering"),
    # ER
    "er-one-to-many": ConnectionTypeInfo("er-one-to-many", "er", "one-to-many"),
    "er-many-to-many": ConnectionTypeInfo("er-many-to-many", "er", "many-to-many"),
    "er-one-to-one": ConnectionTypeInfo("er-one-to-one", "er", "one-to-one"),
    # Sequence
    "sequence-synchronous": ConnectionTypeInfo("sequence-synchronous", "sequence", "synchronous"),
    "sequence-asynchronous": ConnectionTypeInfo("sequence-asynchronous", "sequence", "asynchronous"),
    "sequence-return": ConnectionTypeInfo("sequence-return", "sequence", "return"),
    "sequence-create": ConnectionTypeInfo("sequence-create", "sequence", "create"),
    "sequence-destroy": ConnectionTypeInfo("sequence-destroy", "sequence", "destroy"),
    # Activity
    "activity-sequence-flow": ConnectionTypeInfo("activity-sequence-flow", "activity", "sequence-flow"),
    "activity-decision": ConnectionTypeInfo("activity-decision", "activity", "decision"),
    "activity-message-flow": ConnectionTypeInfo("activity-message-flow", "activity", "message-flow"),
    "activity-data-association": ConnectionTypeInfo("activity-data-association", "activity", "data-association"),
    # Usecase
    "usecase-include": ConnectionTypeInfo("usecase-include", "usecase", "include"),
    "usecase-extend": ConnectionTypeInfo("usecase-extend", "usecase", "extend"),
    "usecase-association": ConnectionTypeInfo("usecase-association", "usecase", "actor-association"),
    "usecase-generalization": ConnectionTypeInfo("usecase-generalization", "usecase", "generalization"),
}


ARCHIMATE_STEREOTYPE_TO_CONNECTION_TYPE: dict[str, str] = {
    "composition": "archimate-composition",
    "aggregation": "archimate-aggregation",
    "assignment": "archimate-assignment",
    "realization": "archimate-realization",
    "serving": "archimate-serving",
    "access": "archimate-access",
    "influence": "archimate-influence",
    "association": "archimate-association",
    "specialization": "archimate-specialization",
    "flow": "archimate-flow",
    "triggering": "archimate-triggering",
}


# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------


def slugify(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "entity"


def prefix_num_from_id(artifact_id: str) -> tuple[str, int] | None:
    m = re.fullmatch(r"([A-Z]+)-(\d{3})", artifact_id.strip())
    if not m:
        return None
    return m.group(1), int(m.group(2))


def allocate_next_entity_id(registry: ModelRegistry, prefix: str) -> str:
    max_num = 0
    for eid in registry.entity_ids():
        parsed = prefix_num_from_id(eid)
        if parsed is None:
            continue
        pref, num = parsed
        if pref == prefix:
            max_num = max(max_num, num)
    return f"{prefix}-{max_num + 1:03d}"


def connection_id_from_endpoints(source: str | list[str], target: str | list[str]) -> str:
    srcs = source if isinstance(source, list) else [source]
    tgts = target if isinstance(target, list) else [target]
    src_part = "--".join(str(s).strip() for s in srcs if str(s).strip())
    tgt_part = "--".join(str(t).strip() for t in tgts if str(t).strip())
    return f"{src_part}---{tgt_part}"


# ---------------------------------------------------------------------------
# PUML inference
# ---------------------------------------------------------------------------


def infer_entity_ids_from_puml(puml: str) -> tuple[set[str], list[str]]:
    """Infer entity IDs from PUML.

    Returns (ids, warnings). IDs are returned in hyphenated artifact-id form.
    """

    warnings: list[str] = []
    ids: set[str] = set()

    # 1) Alias tokens like APP_001 / DOB_009
    for m in re.finditer(r"\b([A-Z]{2,6})_(\d{3})\b", puml):
        ids.add(f"{m.group(1)}-{m.group(2)}")

    # 2) Explicit comments in activity diagrams:  ' artifact-id: ACT-002
    for m in re.finditer(r"^\s*'\s*artifact-id:\s*([A-Z]+-\d{3})\s*$", puml, flags=re.MULTILINE):
        ids.add(m.group(1))

    if not ids:
        warnings.append(
            "No entity IDs inferred from PUML. "
            "For best discoverability, either reference entities using standard aliases like APP_001 "
            "or include explicit comment lines like ' artifact-id: APP-001'."
        )

    return ids, warnings


def infer_archimate_connection_ids_from_puml(
    puml: str,
    *,
    registry: ModelRegistry,
    mode: DiagramConnectionInferenceMode,
) -> tuple[set[str], list[str]]:
    """Infer ArchiMate connection IDs from PUML lines with <<relationship>> stereotypes."""

    warnings: list[str] = []
    conn_ids: set[str] = set()

    # Pattern matches e.g. APP_001 -[#color]-> APP_016 : <<serving>>
    pat = re.compile(
        r"\b(?P<src>[A-Z]{2,6}_\d{3})\b.*?\b(?P<tgt>[A-Z]{2,6}_\d{3})\b\s*:\s*<<(?P<rel>[A-Za-z]+)>>",
        flags=re.IGNORECASE,
    )

    for m in pat.finditer(puml):
        src = m.group("src").replace("_", "-")
        tgt = m.group("tgt").replace("_", "-")
        rel = m.group("rel").strip().lower()
        conn_type = ARCHIMATE_STEREOTYPE_TO_CONNECTION_TYPE.get(rel)
        if conn_type is None:
            msg = f"Unknown ArchiMate relationship stereotype <<{m.group('rel')}>>; cannot infer connection artifact-type"
            if mode == "strict":
                raise ValueError(msg)
            warnings.append(msg)
            continue

        expected_id = connection_id_from_endpoints(src, tgt)
        if expected_id not in registry.connection_ids():
            msg = (
                f"PUML references connection {src} → {tgt} (<<{rel}>>), but no connection artifact '{expected_id}' exists. "
                "Create the connection first, or supply connection_ids_used explicitly."
            )
            if mode == "strict":
                raise ValueError(msg)
            warnings.append(msg)
            continue

        conn_ids.add(expected_id)

    return conn_ids, warnings


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_entity_markdown(
    *,
    engagement: str,
    artifact_id: str,
    artifact_type: str,
    name: str,
    version: str,
    status: str,
    phase_produced: str,
    owner_agent: str,
    produced_by_skill: str,
    last_updated: str,
    safety_relevant: bool,
    domain: str | None,
    summary: str | None,
    properties: dict[str, str] | None,
    notes: str | None,
    display_archimate: dict[str, str],
) -> str:
    fm: dict[str, object] = {
        "artifact-id": artifact_id,
        "artifact-type": artifact_type,
        "name": name,
        "version": version,
        "status": status,
        "phase-produced": phase_produced,
        "owner-agent": owner_agent,
        "safety-relevant": safety_relevant,
        "produced-by-skill": produced_by_skill,
        "last-updated": last_updated,
        "engagement": engagement,
    }
    if domain:
        fm["domain"] = domain

    ordered_keys = [
        "artifact-id",
        "artifact-type",
        "name",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "domain",
        "safety-relevant",
        "produced-by-skill",
        "last-updated",
        "engagement",
    ]
    fm_out = {k: fm[k] for k in ordered_keys if k in fm}

    content_lines: list[str] = []
    content_lines.append("<!-- §content -->")
    content_lines.append("")
    content_lines.append(f"## {name}")
    content_lines.append("")
    if summary:
        content_lines.append(summary.strip())
        content_lines.append("")
    content_lines.append("## Properties")
    content_lines.append("")
    props = properties or {}
    content_lines.append("| Attribute | Value |")
    content_lines.append("|---|---|")
    if props:
        for k in sorted(props.keys()):
            content_lines.append(f"| {k} | {props[k]} |")
    else:
        content_lines.append("| (none) | (none) |")
    content_lines.append("")
    if notes and notes.strip():
        content_lines.append("## Notes")
        content_lines.append("")
        content_lines.append(notes.strip())
        content_lines.append("")

    display_yaml = yaml.safe_dump(display_archimate, sort_keys=False).strip()
    display_lines = [
        "<!-- §display -->",
        "",
        "### archimate",
        "",
        "```yaml",
        display_yaml,
        "```",
    ]

    frontmatter = yaml.safe_dump(fm_out, sort_keys=False).strip()
    return "---\n" + frontmatter + "\n---\n\n" + "\n".join(content_lines) + "\n\n" + "\n".join(display_lines) + "\n"


def format_connection_markdown(
    *,
    engagement: str,
    artifact_id: str,
    artifact_type: str,
    source: str | list[str],
    target: str | list[str],
    version: str,
    status: str,
    phase_produced: str,
    owner_agent: str,
    last_updated: str,
    summary: str | None,
    display_block: dict[str, object] | None,
    display_lang: str,
) -> str:
    fm: dict[str, object] = {
        "artifact-id": artifact_id,
        "artifact-type": artifact_type,
        "source": source,
        "target": target,
        "version": version,
        "status": status,
        "phase-produced": phase_produced,
        "owner-agent": owner_agent,
        "engagement": engagement,
        "last-updated": last_updated,
    }
    frontmatter = yaml.safe_dump(fm, sort_keys=False).strip()

    content_lines: list[str] = ["<!-- §content -->", ""]
    if summary and summary.strip():
        content_lines.append(summary.strip())
        content_lines.append("")

    disp = display_block or {}
    display_yaml = yaml.safe_dump(disp, sort_keys=False).strip() if disp else ""
    display_lines = [
        "<!-- §display -->",
        "",
        f"### {display_lang}",
        "",
        "```yaml",
        display_yaml,
        "```",
    ]

    return "---\n" + frontmatter + "\n---\n\n" + "\n".join(content_lines) + "\n" + "\n".join(display_lines) + "\n"


def format_diagram_puml(
    *,
    engagement: str,
    artifact_id: str,
    diagram_type: str,
    name: str,
    version: str,
    status: str,
    phase_produced: str,
    owner_agent: str,
    domain: str | None,
    purpose: str,
    entity_ids_used: list[str] | None,
    connection_ids_used: list[str] | None,
    puml_body: str,
) -> str:
    fm: dict[str, object] = {
        "artifact-id": artifact_id,
        "artifact-type": "diagram",
        "diagram-type": diagram_type,
        "name": name,
        "version": version,
        "status": status,
        "phase-produced": phase_produced,
        "owner-agent": owner_agent,
        "engagement": engagement,
        "purpose": purpose.strip(),
    }
    if domain:
        fm["domain"] = domain
    if entity_ids_used is not None:
        fm["entity-ids-used"] = entity_ids_used
    if connection_ids_used is not None:
        fm["connection-ids-used"] = connection_ids_used

    ordered = [
        "artifact-id",
        "artifact-type",
        "diagram-type",
        "name",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "engagement",
        "domain",
        "purpose",
        "entity-ids-used",
        "connection-ids-used",
    ]
    fm_out = {k: fm[k] for k in ordered if k in fm}
    yaml_text = yaml.safe_dump(fm_out, sort_keys=False).strip()

    header_lines = ["' ---"]
    for line in yaml_text.splitlines():
        header_lines.append("' " + line)
    header_lines.append("' ---")

    body = puml_body.strip("\n") + "\n"
    return "\n".join(header_lines) + "\n" + body

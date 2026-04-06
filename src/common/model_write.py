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

import re

from src.common.model_verifier import ModelRegistry
from src.common.model_write_catalog import (
    ARCHIMATE_STEREOTYPE_TO_CONNECTION_TYPE,
    CONNECTION_TYPES,
    ENTITY_TYPES,
    ConnectionTypeInfo,
    DiagramConnectionInferenceMode,
    EntityTypeInfo,
)
from src.common.model_write_formatting import (
    format_connection_markdown,
    format_diagram_puml,
    format_entity_markdown,
    format_matrix_markdown,
)


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



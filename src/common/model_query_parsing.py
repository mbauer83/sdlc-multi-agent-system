from __future__ import annotations

import re
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from src.common.model_verifier import entity_id_from_path
from src.common.model_query_types import (
    ConnectionRecord,
    DiagramRecord,
    EntityRecord,
    LAYER_NAMES,
    Layer,
    RepoMount,
    STANDARD_CONNECTION_FIELDS,
    STANDARD_DIAGRAM_FIELDS,
    STANDARD_ENTITY_FIELDS,
)


def extract_yaml_block(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(content[3:end].strip()) or {}
    except yaml.YAMLError:
        return None


def extract_puml_frontmatter(content: str) -> dict | None:
    lines = content.splitlines()
    in_block = False
    yaml_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not in_block:
            if stripped == "' ---":
                in_block = True
            elif stripped:
                break
            continue

        if stripped == "' ---":
            break
        if stripped.startswith("' "):
            yaml_lines.append(stripped[2:])
        elif stripped == "'":
            yaml_lines.append("")

    if not yaml_lines:
        return None

    try:
        return yaml.safe_load("\n".join(yaml_lines)) or {}
    except yaml.YAMLError:
        return None


def extract_section(content: str, marker: str) -> str:
    start_tag = f"<!-- §{marker} -->"
    start = content.find(start_tag)
    if start == -1:
        return ""
    body_start = start + len(start_tag)
    next_tag = re.search(r"<!-- §\w+ -->", content[body_start:])
    if next_tag:
        return content[body_start : body_start + next_tag.start()].strip()
    return content[body_start:].strip()


def extract_display_blocks(content: str) -> dict[str, str]:
    display_body = extract_section(content, "display")
    if not display_body:
        return {}

    blocks: dict[str, str] = {}
    parts = re.split(r"^###\s+(.+)$", display_body, flags=re.MULTILINE)
    iterator = iter(parts[1:])
    for lang, body in zip(iterator, iterator):
        blocks[lang.strip()] = body.strip()
    return blocks


def derive_layer(path: Path, root: Path) -> tuple[Layer, str]:
    try:
        rel = path.relative_to(root)
        parts = rel.parts
        layer_raw = parts[0] if len(parts) > 0 else "unknown"
        sublayer = parts[1] if len(parts) > 1 else ""
        layer: Layer = layer_raw if layer_raw in LAYER_NAMES else "unknown"  # type: ignore[assignment]
        return layer, sublayer
    except ValueError:
        return "unknown", ""


def derive_conn_lang_type(path: Path, root: Path) -> tuple[str, str]:
    try:
        rel = path.relative_to(root)
        parts = rel.parts
        conn_lang = parts[0] if len(parts) > 0 else "unknown"
        conn_type = parts[1] if len(parts) > 1 else "unknown"
        return conn_lang, conn_type
    except ValueError:
        return "unknown", "unknown"


def extract_archimate_label_alias(display_blocks: dict[str, str]) -> tuple[str, str]:
    archimate_block = display_blocks.get("archimate", "")
    if not archimate_block:
        return "", ""
    block = re.sub(r"```\w*\s*|\s*```", " ", archimate_block)
    label_match = re.search(r"label:\s*[\"']?([^\"'\n]+)[\"']?", block)
    alias_match = re.search(r"alias:\s*(\w+)", block)
    label = label_match.group(1).strip() if label_match else ""
    alias = alias_match.group(1).strip() if alias_match else ""
    return label, alias


def parse_entity(path: Path, entities_root: Path, mount: RepoMount) -> EntityRecord | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    frontmatter = extract_yaml_block(content)
    if not frontmatter:
        return None

    if mount.scope == "enterprise":
        engagement = "enterprise"
    else:
        engagement = str(frontmatter.get("engagement", mount.engagement_label))

    layer, sublayer = derive_layer(path, entities_root)
    display_blocks = extract_display_blocks(content)
    display_label, display_alias = extract_archimate_label_alias(display_blocks)

    safety_raw = frontmatter.get("safety-relevant", False)
    safety_relevant = bool(safety_raw) if isinstance(safety_raw, bool) else False

    return EntityRecord(
        artifact_id=str(frontmatter.get("artifact-id", entity_id_from_path(path))),
        artifact_type=str(frontmatter.get("artifact-type", "")),
        name=str(frontmatter.get("name", "")),
        version=str(frontmatter.get("version", "")),
        status=str(frontmatter.get("status", "draft")),
        phase_produced=str(frontmatter.get("phase-produced", "")),
        owner_agent=str(frontmatter.get("owner-agent", "")),
        safety_relevant=safety_relevant,
        engagement=engagement,
        layer=layer,
        sublayer=sublayer,
        path=path,
        extra={key: value for key, value in frontmatter.items() if key not in STANDARD_ENTITY_FIELDS},
        content_text=extract_section(content, "content"),
        display_blocks=display_blocks,
        display_label=display_label,
        display_alias=display_alias,
    )


def parse_connection(path: Path, connections_root: Path, mount: RepoMount) -> ConnectionRecord | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    frontmatter = extract_yaml_block(content)
    if not frontmatter:
        return None

    if mount.scope == "enterprise":
        engagement = "enterprise"
    else:
        engagement = str(frontmatter.get("engagement", mount.engagement_label))

    source_raw = frontmatter.get("source", "")
    target_raw = frontmatter.get("target", "")
    source: str | list[str] = source_raw if isinstance(source_raw, list) else str(source_raw)
    target: str | list[str] = target_raw if isinstance(target_raw, list) else str(target_raw)
    conn_lang, conn_type = derive_conn_lang_type(path, connections_root)

    return ConnectionRecord(
        artifact_id=str(frontmatter.get("artifact-id", path.stem)),
        artifact_type=str(frontmatter.get("artifact-type", "")),
        source=source,
        target=target,
        version=str(frontmatter.get("version", "")),
        status=str(frontmatter.get("status", "draft")),
        phase_produced=str(frontmatter.get("phase-produced", "")),
        owner_agent=str(frontmatter.get("owner-agent", "")),
        engagement=engagement,
        conn_lang=conn_lang,
        conn_type=conn_type,
        path=path,
        extra={key: value for key, value in frontmatter.items() if key not in STANDARD_CONNECTION_FIELDS},
        content_text=extract_section(content, "content"),
    )


def parse_diagram(path: Path, mount: RepoMount) -> DiagramRecord | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    frontmatter = extract_puml_frontmatter(content) if path.suffix == ".puml" else extract_yaml_block(content)
    if not frontmatter:
        return None

    if mount.scope == "enterprise":
        engagement = "enterprise"
    else:
        engagement = str(frontmatter.get("engagement", mount.engagement_label))

    eids_raw = frontmatter.get("entity-ids-used") or []
    cids_raw = frontmatter.get("connection-ids-used") or []

    return DiagramRecord(
        artifact_id=str(frontmatter.get("artifact-id", path.stem)),
        artifact_type=str(frontmatter.get("artifact-type", "diagram")),
        name=str(frontmatter.get("name", "")),
        diagram_type=str(frontmatter.get("diagram-type", "")),
        version=str(frontmatter.get("version", "")),
        status=str(frontmatter.get("status", "draft")),
        phase_produced=str(frontmatter.get("phase-produced", "")),
        owner_agent=str(frontmatter.get("owner-agent", "")),
        engagement=engagement,
        entity_ids_used=[str(x) for x in eids_raw] if isinstance(eids_raw, list) else [],
        connection_ids_used=[str(x) for x in cids_raw] if isinstance(cids_raw, list) else [],
        path=path,
        extra={key: value for key, value in frontmatter.items() if key not in STANDARD_DIAGRAM_FIELDS},
    )

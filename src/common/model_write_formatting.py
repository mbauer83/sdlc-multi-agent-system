from __future__ import annotations

import re

import yaml  # type: ignore[import-untyped]


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
    frontmatter = {
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
        frontmatter["domain"] = domain

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
    fm_out = {key: frontmatter[key] for key in ordered_keys if key in frontmatter}

    content_lines: list[str] = ["<!-- §content -->", "", f"## {name}", ""]
    if summary:
        content_lines.append(summary.strip())
        content_lines.append("")

    content_lines.extend(["## Properties", "", "| Attribute | Value |", "|---|---|"])
    props = properties or {}
    if props:
        for key in sorted(props.keys()):
            content_lines.append(f"| {key} | {props[key]} |")
    else:
        content_lines.append("| (none) | (none) |")
    content_lines.append("")

    if notes and notes.strip():
        content_lines.extend(["## Notes", "", notes.strip(), ""])

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
    frontmatter_text = yaml.safe_dump(fm_out, sort_keys=False).strip()
    return "---\n" + frontmatter_text + "\n---\n\n" + "\n".join(content_lines) + "\n\n" + "\n".join(display_lines) + "\n"


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
    frontmatter = {
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
    frontmatter_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()

    content_lines: list[str] = ["<!-- §content -->", ""]
    if summary and summary.strip():
        content_lines.append(summary.strip())
        content_lines.append("")

    display_yaml = yaml.safe_dump(display_block or {}, sort_keys=False).strip() if display_block else ""
    display_lines = [
        "<!-- §display -->",
        "",
        f"### {display_lang}",
        "",
        "```yaml",
        display_yaml,
        "```",
    ]
    return "---\n" + frontmatter_text + "\n---\n\n" + "\n".join(content_lines) + "\n" + "\n".join(display_lines) + "\n"


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
    frontmatter = {
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
        frontmatter["domain"] = domain
    if entity_ids_used is not None:
        frontmatter["entity-ids-used"] = entity_ids_used
    if connection_ids_used is not None:
        frontmatter["connection-ids-used"] = connection_ids_used

    ordered_keys = [
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
    fm_out = {key: frontmatter[key] for key in ordered_keys if key in frontmatter}
    yaml_text = yaml.safe_dump(fm_out, sort_keys=False).strip()

    header_lines = ["' ---"]
    for line in yaml_text.splitlines():
        header_lines.append("' " + line)
    header_lines.append("' ---")

    body = _ensure_visible_title(puml_body, name)
    return "\n".join(header_lines) + "\n" + body


def _ensure_visible_title(puml_body: str, title_text: str) -> str:
    lines = puml_body.strip("\n").splitlines()
    if not lines:
        return puml_body.strip("\n") + "\n"

    has_title = any(
        (not line.lstrip().startswith("'")) and re.match(r"^\s*title(\s|$)", line, flags=re.IGNORECASE)
        for line in lines
    )
    if has_title:
        return puml_body.strip("\n") + "\n"

    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith("@startuml")), 0)
    insert_idx = start_idx + 1
    for i in range(start_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("'"):
            continue
        if stripped.lower().startswith("!include"):
            insert_idx = i + 1
            continue
        break

    lines.insert(insert_idx, f"title {title_text}")
    return "\n".join(lines) + "\n"


def format_matrix_markdown(
    *,
    engagement: str,
    artifact_id: str,
    name: str,
    version: str,
    status: str,
    phase_produced: str,
    owner_agent: str,
    domain: str | None,
    purpose: str,
    matrix_markdown: str,
    entity_ids_used: list[str] | None,
    connection_ids_used: list[str] | None,
) -> str:
    frontmatter = {
        "artifact-id": artifact_id,
        "artifact-type": "diagram",
        "diagram-type": "matrix",
        "name": name,
        "version": version,
        "status": status,
        "phase-produced": phase_produced,
        "owner-agent": owner_agent,
        "engagement": engagement,
        "purpose": purpose.strip(),
    }
    if domain:
        frontmatter["domain"] = domain
    if entity_ids_used is not None:
        frontmatter["entity-ids-used"] = entity_ids_used
    if connection_ids_used is not None:
        frontmatter["connection-ids-used"] = connection_ids_used

    ordered_keys = [
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
    fm_out = {key: frontmatter[key] for key in ordered_keys if key in frontmatter}
    yaml_text = yaml.safe_dump(fm_out, sort_keys=False).strip()
    body = matrix_markdown.strip("\n") + "\n"
    return f"---\n{yaml_text}\n---\n\n{body}"

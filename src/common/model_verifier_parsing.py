from __future__ import annotations

from pathlib import Path

import yaml

from src.common.model_verifier_types import ConnectionRefs, Issue, Severity, VerificationResult

PUML_FRONTMATTER_DELIMITER = "' ---"


def read_file(path: Path, result: VerificationResult, loc: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        result.issues.append(Issue(Severity.ERROR, "E001", f"Cannot read file: {exc}", loc))
        return None


def parse_frontmatter_from_path(path: Path) -> dict | None:
    try:
        content = path.read_text(encoding="utf-8")
        return extract_yaml_block(content)
    except Exception:
        return None


def extract_yaml_block(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    return yaml.safe_load(content[3:end].strip()) or {}


def parse_frontmatter(content: str, result: VerificationResult, loc: str) -> dict | None:
    if not content.startswith("---"):
        result.issues.append(Issue(Severity.ERROR, "E011", "File does not begin with YAML frontmatter (--- block)", loc))
        return None

    end = content.find("\n---", 3)
    if end == -1:
        result.issues.append(Issue(Severity.ERROR, "E012", "Frontmatter opening --- has no closing ---", loc))
        return None

    yaml_block = content[3:end].strip()
    try:
        fm = yaml.safe_load(yaml_block)
    except yaml.YAMLError as exc:
        result.issues.append(Issue(Severity.ERROR, "E013", f"Frontmatter YAML parse error: {exc}", loc))
        return None

    if not isinstance(fm, dict):
        result.issues.append(Issue(Severity.ERROR, "E014", "Frontmatter is not a YAML mapping", loc))
        return None

    return fm


def parse_puml_frontmatter(content: str, result: VerificationResult, loc: str) -> dict | None:
    lines = content.splitlines()
    in_block = False
    yaml_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not in_block:
            if stripped == PUML_FRONTMATTER_DELIMITER:
                in_block = True
                continue
            if stripped == "":
                continue
            break

        if stripped == PUML_FRONTMATTER_DELIMITER:
            break
        if stripped.startswith("' "):
            yaml_lines.append(stripped[2:])
            continue
        if stripped == "'":
            yaml_lines.append("")
            continue
        result.issues.append(Issue(Severity.WARNING, "W302", f"Unexpected line inside PUML frontmatter block: {line!r}", loc))

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
        result.issues.append(Issue(Severity.ERROR, "E312", f"PUML frontmatter YAML parse error: {exc}", loc))
        return None

    if not isinstance(fm, dict):
        result.issues.append(Issue(Severity.ERROR, "E313", "PUML frontmatter is not a YAML mapping", loc))
        return None

    return fm


def extract_puml_frontmatter_best_effort(content: str) -> dict | None:
    lines = content.splitlines()
    in_block = False
    yaml_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not in_block:
            if stripped == PUML_FRONTMATTER_DELIMITER:
                in_block = True
                continue
            if stripped:
                break
            continue
        if stripped == PUML_FRONTMATTER_DELIMITER:
            break
        if stripped.startswith("' "):
            yaml_lines.append(stripped[2:])
        elif stripped == "'":
            yaml_lines.append("")
        else:
            return None

    if not yaml_lines:
        return None
    try:
        parsed = yaml.safe_load("\n".join(yaml_lines))
    except yaml.YAMLError:
        return None
    return parsed if isinstance(parsed, dict) else None


def parse_connection_refs(path: Path) -> ConnectionRefs | None:
    fm = parse_frontmatter_from_path(path)
    if fm is None:
        return None
    source = fm.get("source")
    target = fm.get("target")

    if isinstance(source, list):
        srcs = source
    elif source:
        srcs = [source]
    else:
        srcs = []

    if isinstance(target, list):
        tgts = target
    elif target:
        tgts = [target]
    else:
        tgts = []

    return ConnectionRefs(
        source_ids=tuple(str(x) for x in srcs if x is not None),
        target_ids=tuple(str(x) for x in tgts if x is not None),
    )


def parse_diagram_refs(path: Path) -> dict[str, list[str]] | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    if path.suffix == ".puml":
        fm = extract_puml_frontmatter_best_effort(content)
    else:
        fm = extract_yaml_block(content)
    if not isinstance(fm, dict):
        return None

    entity_ids_raw = fm.get("entity-ids-used")
    conn_ids_raw = fm.get("connection-ids-used")
    entity_ids = [str(x) for x in entity_ids_raw] if isinstance(entity_ids_raw, list) else []
    connection_ids = [str(x) for x in conn_ids_raw] if isinstance(conn_ids_raw, list) else []
    return {"entity_ids": entity_ids, "connection_ids": connection_ids}

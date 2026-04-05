from __future__ import annotations

from pathlib import Path
import os
import re
from typing import Callable
import yaml

from src.common.model_verifier import ModelRegistry, ModelVerifier
from src.common.model_write import format_matrix_markdown

from .boundary import assert_engagement_write_root, engagement_id_from_repo_root
from .types import WriteResult


_ENTITY_ID_PATTERN = re.compile(r"\b([A-Z]+-\d{3})\b")


def _verification_to_dict(path: Path, res) -> dict[str, object]:
    return {
        "path": str(path),
        "file_type": "diagram",
        "valid": res.valid,
        "issues": [
            {"severity": i.severity, "code": i.code, "message": i.message, "location": i.location}
            for i in res.issues
        ],
    }


def _infer_entity_ids_from_matrix(markdown: str) -> list[str]:
    found = sorted(set(_ENTITY_ID_PATTERN.findall(markdown)))
    return found


def _read_frontmatter(path: Path) -> dict[str, object]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}
    try:
        parsed = yaml.safe_load(content[4:end])
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _display_name_from_entity_file(path: Path, artifact_id: str) -> str:
    fm = _read_frontmatter(path)
    name = str(fm.get("name", "")).strip()
    if not name:
        return artifact_id

    # For skill concept objects, prefer the synchronized "Display Name" property.
    try:
        content = path.read_text(encoding="utf-8")
        m = re.search(r"^\| Display Name \|\s*(.+?)\s*\|\s*$", content, flags=re.MULTILINE)
        if m:
            return m.group(1).strip()
    except OSError:
        pass

    prefixes = (
        "Skill: ",
        "Input Concept: ",
        "Output Concept: ",
        "Input: ",
        "Output: ",
    )
    for pref in prefixes:
        if name.startswith(pref):
            return name[len(pref) :].strip()
    return name


def _linkify_matrix_ids(
    *,
    repo_root: Path,
    registry: ModelRegistry,
    matrix_markdown: str,
    candidate_entity_ids: list[str],
) -> tuple[str, int]:
    """Replace plain entity IDs with relative markdown links in matrix rows."""

    diagrams_dir = repo_root / "diagram-catalog" / "diagrams"
    id_to_relpath: dict[str, str] = {}
    id_to_link_text: dict[str, str] = {}

    for entity_id in candidate_entity_ids:
        p = registry.find_file_by_id(entity_id)
        if p is None:
            continue
        rel = os.path.relpath(str(p), start=str(diagrams_dir)).replace("\\", "/")
        id_to_relpath[entity_id] = rel
        id_to_link_text[entity_id] = _display_name_from_entity_file(p, entity_id)

    if not id_to_relpath:
        return matrix_markdown, 0

    replaced = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal replaced
        artifact_id = match.group(1)
        target = id_to_relpath.get(artifact_id)
        if target is None:
            return artifact_id
        link_text = id_to_link_text.get(artifact_id, artifact_id)
        replaced += 1
        return f"[{link_text}]({target})"

    out_lines: list[str] = []
    for line in matrix_markdown.splitlines():
        # Only rewrite table rows that do not already contain markdown links.
        if line.startswith("| ") and not line.startswith("|---") and "](" not in line:
            out_lines.append(_ENTITY_ID_PATTERN.sub(repl, line))
        else:
            out_lines.append(line)

    return "\n".join(out_lines), replaced


def create_matrix(
    *,
    repo_root: Path,
    registry: ModelRegistry,
    verifier: ModelVerifier,
    clear_repo_caches: Callable[[Path], None],
    name: str,
    purpose: str,
    matrix_markdown: str,
    phase_produced: str,
    owner_agent: str,
    artifact_id: str,
    domain: str | None,
    version: str,
    status: str,
    infer_entity_ids: bool,
    auto_link_entity_ids: bool,
    entity_ids_used: list[str] | None,
    connection_ids_used: list[str] | None,
    dry_run: bool,
) -> WriteResult:
    assert_engagement_write_root(repo_root)

    engagement = engagement_id_from_repo_root(repo_root)

    inferred_entities: list[str] = []
    warnings: list[str] = []
    if infer_entity_ids and entity_ids_used is None:
        inferred_entities = _infer_entity_ids_from_matrix(matrix_markdown)
        if not inferred_entities:
            warnings.append(
                "No entity IDs inferred from matrix markdown. Consider providing entity_ids_used for stronger traceability."
            )

    final_entity_ids = entity_ids_used if entity_ids_used is not None else inferred_entities

    body_markdown = matrix_markdown
    if auto_link_entity_ids:
        ids_for_links = final_entity_ids if final_entity_ids else _infer_entity_ids_from_matrix(matrix_markdown)
        body_markdown, replaced_count = _linkify_matrix_ids(
            repo_root=repo_root,
            registry=registry,
            matrix_markdown=matrix_markdown,
            candidate_entity_ids=ids_for_links,
        )
        if replaced_count == 0 and ids_for_links:
            warnings.append(
                "auto_link_entity_ids enabled, but no entity IDs were converted to links; check ID/path resolution."
            )

    content = format_matrix_markdown(
        engagement=engagement,
        artifact_id=artifact_id,
        name=name,
        version=version,
        status=status,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        domain=domain,
        purpose=purpose,
        matrix_markdown=body_markdown,
        entity_ids_used=final_entity_ids,
        connection_ids_used=connection_ids_used,
    )

    path = repo_root / "diagram-catalog" / "diagrams" / f"{artifact_id}.md"

    if dry_run:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory(prefix="model-write-verify-matrix-") as tmp_dir:
            tmp_path = Path(tmp_dir) / f"{artifact_id}.md"
            tmp_path.write_text(content, encoding="utf-8")
            res = verifier.verify_matrix_diagram_file(tmp_path)
        return WriteResult(
            wrote=False,
            path=path,
            artifact_id=artifact_id,
            content=content,
            warnings=warnings,
            verification=_verification_to_dict(path, res),
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(content, encoding="utf-8")

    res = verifier.verify_matrix_diagram_file(path)
    if not res.valid:
        if prev is None:
            try:
                path.unlink()
            except OSError:
                pass
        else:
            path.write_text(prev, encoding="utf-8")
        return WriteResult(
            wrote=False,
            path=path,
            artifact_id=artifact_id,
            content=content,
            warnings=warnings,
            verification=_verification_to_dict(path, res),
        )

    clear_repo_caches(repo_root)

    return WriteResult(
        wrote=True,
        path=path,
        artifact_id=artifact_id,
        content=None,
        warnings=warnings,
        verification=_verification_to_dict(path, res),
    )

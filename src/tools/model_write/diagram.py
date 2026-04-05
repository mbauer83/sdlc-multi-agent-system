from __future__ import annotations

from pathlib import Path
import re
from typing import Callable

from src.common.model_verifier import ModelRegistry, ModelVerifier
from src.common.model_write import (
    DiagramConnectionInferenceMode,
    format_diagram_puml,
    infer_archimate_connection_ids_from_puml,
    infer_entity_ids_from_puml,
)
from src.tools.generate_macros import generate_macros

from .boundary import assert_engagement_write_root, engagement_id_from_repo_root
from .types import WriteResult
from .verify import verify_content_in_temp_path


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


def create_diagram(
    *,
    repo_root: Path,
    registry: ModelRegistry,
    verifier: ModelVerifier,
    clear_repo_caches: Callable[[Path], None],
    diagram_type: str,
    name: str,
    purpose: str,
    puml: str,
    phase_produced: str,
    owner_agent: str,
    artifact_id: str | None,
    domain: str | None,
    version: str,
    status: str,
    infer_entity_ids: bool,
    connection_inference: DiagramConnectionInferenceMode,
    entity_ids_used: list[str] | None,
    connection_ids_used: list[str] | None,
    auto_include_macros: bool,
    auto_include_stereotypes: bool,
    dry_run: bool,
) -> WriteResult:
    assert_engagement_write_root(repo_root)

    engagement = engagement_id_from_repo_root(repo_root)

    effective_id = artifact_id
    if effective_id is None:
        m = re.search(r"@startuml\s+(\S+)", puml)
        if m:
            effective_id = m.group(1).strip()
    if effective_id is None:
        raise ValueError("artifact_id is required, or puml must contain '@startuml <artifact-id>'")

    puml_body = puml.strip("\n") + "\n"
    warnings: list[str] = []

    macros_path = repo_root / "diagram-catalog" / "_macros.puml"
    if auto_include_macros and not macros_path.exists():
        try:
            generate_macros(repo_root)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"Could not generate _macros.puml: {exc}")

    stereotypes_path = repo_root / "diagram-catalog" / "_archimate-stereotypes.puml"
    if auto_include_stereotypes and ("archimate" in diagram_type.lower()) and not stereotypes_path.exists():
        if "_archimate-stereotypes.puml" in puml_body:
            puml_body = re.sub(
                r"^\s*!include\s+.*_archimate-stereotypes\.puml\s*$\n?",
                "",
                puml_body,
                flags=re.MULTILINE,
            )
            warnings.append(
                "Removed !include of _archimate-stereotypes.puml because the file does not exist under diagram-catalog/."
            )
        warnings.append(
            "_archimate-stereotypes.puml not found under diagram-catalog/. "
            "Skipping auto-include; create the file if you want ArchiMate stereotypes/skinparams."
        )

    needs_macros = ("archimate" in diagram_type.lower()) or ("usecase" in diagram_type.lower())
    if needs_macros and auto_include_macros and "_macros.puml" not in puml_body:
        puml_body = re.sub(
            r"(@startuml\s+\S+\s*)\n",
            r"\1\n!include ../_macros.puml\n",
            puml_body,
            count=1,
        )

    if (
        ("archimate" in diagram_type.lower())
        and auto_include_stereotypes
        and stereotypes_path.exists()
        and "_archimate-stereotypes.puml" not in puml_body
        and "_macros.puml" in puml_body
    ):
        puml_body = re.sub(
            r"(!include\s+\.\./_macros\.puml\s*)\n",
            r"\1\n!include ../_archimate-stereotypes.puml\n",
            puml_body,
            count=1,
        )

    inferred_entities: set[str] = set()
    if infer_entity_ids:
        inferred_entities, w = infer_entity_ids_from_puml(puml_body)
        warnings.extend(w)
    final_entity_ids = entity_ids_used if entity_ids_used is not None else sorted(inferred_entities)

    inferred_conns: set[str] = set()
    if connection_ids_used is None and connection_inference != "none" and "archimate" in diagram_type.lower():
        inferred_conns, w = infer_archimate_connection_ids_from_puml(
            puml_body,
            registry=registry,
            mode=connection_inference,
        )
        warnings.extend(w)

    final_conn_ids = (
        connection_ids_used
        if connection_ids_used is not None
        else (sorted(inferred_conns) if inferred_conns else None)
    )

    content = format_diagram_puml(
        engagement=engagement,
        artifact_id=effective_id,
        diagram_type=diagram_type,
        name=name,
        version=version,
        status=status,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        domain=domain,
        purpose=purpose,
        entity_ids_used=final_entity_ids,
        connection_ids_used=final_conn_ids,
        puml_body=puml_body,
    )

    path = repo_root / "diagram-catalog" / "diagrams" / f"{effective_id}.puml"

    if dry_run:
        res = verify_content_in_temp_path(
            verifier=verifier,
            file_type="diagram",
            desired_name=path.name,
            content=content,
            support_repo_root=repo_root,
        )
        return WriteResult(
            wrote=False,
            path=path,
            artifact_id=effective_id,
            content=content,
            warnings=warnings,
            verification=_verification_to_dict(path, res),
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(content, encoding="utf-8")

    res = verifier.verify_diagram_file(path)
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
            artifact_id=effective_id,
            content=content,
            warnings=warnings,
            verification=_verification_to_dict(path, res),
        )

    clear_repo_caches(repo_root)

    return WriteResult(
        wrote=True,
        path=path,
        artifact_id=effective_id,
        content=None,
        warnings=warnings,
        verification=_verification_to_dict(path, res),
    )

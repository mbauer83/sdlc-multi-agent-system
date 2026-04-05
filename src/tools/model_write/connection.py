from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.common.archimate_types import ALL_CONNECTION_TYPES
from src.common.model_verifier import ModelRegistry, ModelVerifier
from src.common.model_write import CONNECTION_TYPES, connection_id_from_endpoints, format_connection_markdown

from .boundary import assert_engagement_write_root, engagement_id_from_repo_root, today_iso
from .types import WriteResult
from .verify import verify_content_in_temp_path


def _verification_to_dict(path: Path, res) -> dict[str, object]:
    return {
        "path": str(path),
        "file_type": "connection",
        "valid": res.valid,
        "issues": [
            {"severity": i.severity, "code": i.code, "message": i.message, "location": i.location}
            for i in res.issues
        ],
    }


def create_connection(
    *,
    repo_root: Path,
    registry: ModelRegistry,
    verifier: ModelVerifier,
    clear_repo_caches: Callable[[Path], None],
    artifact_type: str,
    source: str | list[str],
    target: str | list[str],
    phase_produced: str,
    owner_agent: str,
    summary: str | None,
    display: dict[str, object] | None,
    version: str,
    status: str,
    last_updated: str | None,
    dry_run: bool,
) -> WriteResult:
    assert_engagement_write_root(repo_root)

    if artifact_type not in ALL_CONNECTION_TYPES:
        raise ValueError(f"Unknown connection artifact_type: {artifact_type!r}")
    info = CONNECTION_TYPES.get(artifact_type)
    if info is None:
        raise ValueError(
            f"Connection artifact_type '{artifact_type}' is supported by the verifier but is missing a writer mapping"
        )

    engagement = engagement_id_from_repo_root(repo_root)
    last = last_updated or today_iso()

    cid = connection_id_from_endpoints(source, target)
    path = repo_root / "connections" / info.conn_lang / info.conn_dir / f"{cid}.md"

    display_lang = info.conn_lang
    disp = dict(display or {})
    if display_lang == "archimate":
        disp.setdefault("relationship-type", info.archimate_relationship_type)
        disp.setdefault("direction", "source-to-target")

    content = format_connection_markdown(
        engagement=engagement,
        artifact_id=cid,
        artifact_type=artifact_type,
        source=source,
        target=target,
        version=version,
        status=status,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        last_updated=last,
        summary=summary,
        display_block=disp,
        display_lang=display_lang,
    )

    if dry_run:
        res = verify_content_in_temp_path(
            verifier=verifier,
            file_type="connection",
            desired_name=path.name,
            content=content,
        )
        return WriteResult(
            wrote=False,
            path=path,
            artifact_id=cid,
            content=content,
            warnings=[],
            verification=_verification_to_dict(path, res),
        )

    missing: set[str] = set()
    for ref in (source if isinstance(source, list) else [source]):
        if str(ref) not in registry.entity_ids():
            missing.add(str(ref))
    for ref in (target if isinstance(target, list) else [target]):
        if str(ref) not in registry.entity_ids():
            missing.add(str(ref))
    if missing:
        raise ValueError(f"Cannot create connection; unknown entity ids: {sorted(missing)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(content, encoding="utf-8")

    res = verifier.verify_connection_file(path)
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
            artifact_id=cid,
            content=content,
            warnings=[],
            verification=_verification_to_dict(path, res),
        )

    clear_repo_caches(repo_root)

    return WriteResult(
        wrote=True,
        path=path,
        artifact_id=cid,
        content=None,
        warnings=[],
        verification=_verification_to_dict(path, res),
    )

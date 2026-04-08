from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from src.common.model_verifier_parsing import parse_connection_refs, parse_diagram_refs
from src.common.model_verifier_types import IncrementalState, VerificationResult, VerifierRuntimeConfig, entity_id_from_path


@dataclass
class FileInventory:
    repo_path: Path
    include_diagrams: bool
    rel_to_path: dict[str, Path]
    path_to_rel: dict[Path, str]
    snapshots: dict[str, dict[str, int | str]]
    ordered_paths: list[str]
    entity_relpaths: list[str]
    connection_relpaths: list[str]
    diagram_puml_relpaths: list[str]
    diagram_matrix_relpaths: list[str]
    file_type_by_relpath: dict[str, Literal["entity", "connection", "diagram"]]
    entity_path_by_id: dict[str, str]
    connection_refs_by_path: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]
    connection_paths_by_entity: dict[str, set[str]]
    neighbor_entities: dict[str, set[str]]
    diagram_paths_by_entity: dict[str, set[str]]
    diagram_paths_by_connection_id: dict[str, set[str]]


def verifier_engine_signature() -> str:
    """
    Return a fingerprint of verifier-engine source modules.

    Incremental verifier state must be invalidated when verifier rules/parsing
    logic changes, even if repository files and git HEAD are unchanged.
    """
    module_files = (
        Path(__file__),
        Path(__file__).with_name("model_verifier.py"),
        Path(__file__).with_name("model_verifier_rules.py"),
        Path(__file__).with_name("model_verifier_types.py"),
        Path(__file__).with_name("model_verifier_parsing.py"),
        Path(__file__).with_name("model_verifier_syntax.py"),
    )
    digest = hashlib.sha256()
    for module_path in module_files:
        try:
            stat = module_path.stat()
            digest.update(str(module_path.resolve()).encode("utf-8"))
            digest.update(str(int(stat.st_mtime_ns)).encode("ascii"))
            digest.update(str(int(stat.st_size)).encode("ascii"))
        except OSError:
            # If a file is not readable, include a stable marker so signature
            # changes deterministically once the file becomes available.
            digest.update(str(module_path.resolve()).encode("utf-8"))
            digest.update(b"missing")
    return digest.hexdigest()[:16]


def load_runtime_config() -> VerifierRuntimeConfig:
    mode_raw = os.getenv("SDLC_MODEL_VERIFY_MODE", "incremental").strip().lower()
    mode: Literal["full", "incremental"] = "incremental" if mode_raw == "incremental" else "full"

    state_root_raw = os.getenv("SDLC_MODEL_VERIFY_STATE_DIR", "").strip()
    if state_root_raw:
        state_dir = Path(state_root_raw).expanduser()
    else:
        xdg_cache = os.getenv("XDG_CACHE_HOME", "").strip()
        cache_root = Path(xdg_cache).expanduser() if xdg_cache else Path.home() / ".cache"
        state_dir = cache_root / "sdlc-agents" / "model-verifier"

    ratio = _read_float_env("SDLC_MODEL_VERIFY_INCREMENTAL_MAX_CHANGED_RATIO", default=0.30)
    count = _read_int_env("SDLC_MODEL_VERIFY_INCREMENTAL_MAX_CHANGED_COUNT", default=200)
    log_mode = _read_bool_env("SDLC_MODEL_VERIFY_LOG_MODE", default=True)

    return VerifierRuntimeConfig(
        mode=mode,
        state_dir=state_dir,
        changed_ratio_threshold=min(max(ratio, 0.01), 1.0),
        changed_count_threshold=max(1, count),
        log_mode=log_mode,
    )


def _read_float_env(name: str, *, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _read_int_env(name: str, *, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _read_bool_env(name: str, *, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw not in {"0", "false", "no", "off"}


def inventory_files(repo_path: Path, *, include_diagrams: bool) -> FileInventory:
    inventory = _new_inventory(repo_path=repo_path, include_diagrams=include_diagrams)
    _index_entity_files(inventory)
    _index_connection_files(inventory)
    if include_diagrams:
        _index_diagram_files(inventory)
    inventory.ordered_paths = (
        inventory.entity_relpaths
        + inventory.connection_relpaths
        + inventory.diagram_puml_relpaths
        + inventory.diagram_matrix_relpaths
    )
    return inventory


def _new_inventory(repo_path: Path, *, include_diagrams: bool) -> FileInventory:
    return FileInventory(
        repo_path=repo_path,
        include_diagrams=include_diagrams,
        rel_to_path={},
        path_to_rel={},
        snapshots={},
        ordered_paths=[],
        entity_relpaths=[],
        connection_relpaths=[],
        diagram_puml_relpaths=[],
        diagram_matrix_relpaths=[],
        file_type_by_relpath={},
        entity_path_by_id={},
        connection_refs_by_path={},
        connection_paths_by_entity={},
        neighbor_entities={},
        diagram_paths_by_entity={},
        diagram_paths_by_connection_id={},
    )


def _index_entity_files(inventory: FileInventory) -> None:
    entity_root = inventory.repo_path / "model-entities"
    if not entity_root.exists():
        return
    for path in sorted(entity_root.rglob("*.md")):
        rel = _add_indexed_file(inventory, path, "entity")
        inventory.entity_relpaths.append(rel)
        inventory.entity_path_by_id[entity_id_from_path(path)] = rel


def _index_connection_files(inventory: FileInventory) -> None:
    connections_root = inventory.repo_path / "connections"
    if not connections_root.exists():
        return
    for path in sorted(connections_root.rglob("*.md")):
        rel = _add_indexed_file(inventory, path, "connection")
        inventory.connection_relpaths.append(rel)
        refs = parse_connection_refs(path)
        if refs is None:
            continue
        source_ids = refs.source_ids
        target_ids = refs.target_ids
        inventory.connection_refs_by_path[rel] = (source_ids, target_ids)
        _index_connection_neighbors(inventory, rel, source_ids, target_ids)


def _index_connection_neighbors(
    inventory: FileInventory,
    rel: str,
    source_ids: tuple[str, ...],
    target_ids: tuple[str, ...],
) -> None:
    for source_id in source_ids:
        inventory.connection_paths_by_entity.setdefault(source_id, set()).add(rel)
        inventory.neighbor_entities.setdefault(source_id, set())
    for target_id in target_ids:
        inventory.connection_paths_by_entity.setdefault(target_id, set()).add(rel)
        inventory.neighbor_entities.setdefault(target_id, set())
    for source_id in source_ids:
        for target_id in target_ids:
            inventory.neighbor_entities.setdefault(source_id, set()).add(target_id)
            inventory.neighbor_entities.setdefault(target_id, set()).add(source_id)


def _index_diagram_files(inventory: FileInventory) -> None:
    diagrams_dir = inventory.repo_path / "diagram-catalog" / "diagrams"
    if not diagrams_dir.exists():
        return
    for path in sorted(diagrams_dir.rglob("*.puml")):
        rel = _add_indexed_file(inventory, path, "diagram")
        inventory.diagram_puml_relpaths.append(rel)
        _add_diagram_refs(path, rel, inventory.diagram_paths_by_entity, inventory.diagram_paths_by_connection_id)
    for path in sorted(diagrams_dir.rglob("*.md")):
        rel = _add_indexed_file(inventory, path, "diagram")
        inventory.diagram_matrix_relpaths.append(rel)
        _add_diagram_refs(path, rel, inventory.diagram_paths_by_entity, inventory.diagram_paths_by_connection_id)


def _add_indexed_file(
    inventory: FileInventory,
    path: Path,
    file_type: Literal["entity", "connection", "diagram"],
) -> str:
    rel = str(path.relative_to(inventory.repo_path))
    stat = path.stat()
    inventory.rel_to_path[rel] = path
    inventory.path_to_rel[path] = rel
    inventory.snapshots[rel] = {
        "mtime_ns": int(stat.st_mtime_ns),
        "size": int(stat.st_size),
        "file_type": file_type,
    }
    inventory.file_type_by_relpath[rel] = file_type
    return rel


def _add_diagram_refs(
    path: Path,
    rel: str,
    diagram_paths_by_entity: dict[str, set[str]],
    diagram_paths_by_connection_id: dict[str, set[str]],
) -> None:
    refs = parse_diagram_refs(path)
    if refs is None:
        return
    for eid in refs["entity_ids"]:
        diagram_paths_by_entity.setdefault(eid, set()).add(rel)
    for cid in refs["connection_ids"]:
        diagram_paths_by_connection_id.setdefault(cid, set()).add(rel)


def state_file_path(repo_path: Path, *, include_diagrams: bool, state_dir: Path) -> Path:
    key = hashlib.sha256(str(repo_path.resolve()).encode("utf-8")).hexdigest()[:16]
    suffix = "with-diagrams" if include_diagrams else "no-diagrams"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{key}.{suffix}.state-v1.json"


def load_incremental_state(path: Path) -> IncrementalState | None:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    if int(raw.get("schema_version", -1)) != 1:
        return None
    snapshots = raw.get("snapshots", {})
    results = raw.get("results", {})
    if not isinstance(snapshots, dict) or not isinstance(results, dict):
        return None
    git_head = raw.get("git_head")
    return IncrementalState(
        schema_version=1,
        engine_signature=str(raw.get("engine_signature", "")),
        include_diagrams=bool(raw.get("include_diagrams", True)),
        git_head=str(git_head) if isinstance(git_head, str) else None,
        snapshots=snapshots,
        results=results,
    )


def save_incremental_state(path: Path, state: IncrementalState) -> None:
    payload = {
        "schema_version": state.schema_version,
        "engine_signature": state.engine_signature,
        "include_diagrams": state.include_diagrams,
        "git_head": state.git_head,
        "snapshots": state.snapshots,
        "results": state.results,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=True), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        return


def detect_changed_paths(inv: FileInventory, prev: IncrementalState) -> tuple[set[str], set[str]]:
    changed: set[str] = set()
    deleted = set(prev.snapshots.keys()) - set(inv.snapshots.keys())
    for rel, curr in inv.snapshots.items():
        prev_item = prev.snapshots.get(rel)
        if prev_item is None:
            changed.add(rel)
            continue
        if prev_item.get("mtime_ns") != curr.get("mtime_ns") or prev_item.get("size") != curr.get("size"):
            changed.add(rel)
    return changed, deleted


def expand_impacted_paths(inv: FileInventory, changed: set[str]) -> set[str]:
    impacted: set[str] = set(changed)
    for rel in changed:
        path = inv.rel_to_path.get(rel)
        if path is None:
            continue
        file_type = inv.file_type_by_relpath.get(rel)
        if file_type == "entity":
            _expand_for_entity(inv, impacted, entity_id_from_path(path))
        elif file_type == "connection":
            _expand_for_connection(inv, impacted, rel, path.stem)
    return impacted


def _expand_for_entity(inv: FileInventory, impacted: set[str], entity_id: str) -> None:
    impacted |= inv.connection_paths_by_entity.get(entity_id, set())
    impacted |= inv.diagram_paths_by_entity.get(entity_id, set())
    for connection_rel in inv.connection_paths_by_entity.get(entity_id, set()):
        impacted |= inv.diagram_paths_by_connection_id.get(Path(connection_rel).stem, set())
    for neighbor_entity in inv.neighbor_entities.get(entity_id, set()):
        neighbor_path = inv.entity_path_by_id.get(neighbor_entity)
        if neighbor_path:
            impacted.add(neighbor_path)


def _expand_for_connection(inv: FileInventory, impacted: set[str], rel: str, connection_id: str) -> None:
    impacted |= inv.diagram_paths_by_connection_id.get(connection_id, set())
    refs = inv.connection_refs_by_path.get(rel)
    if refs is None:
        return
    srcs, tgts = refs
    for entity_id in (*srcs, *tgts):
        entity_rel = inv.entity_path_by_id.get(entity_id)
        if entity_rel:
            impacted.add(entity_rel)
        impacted |= inv.connection_paths_by_entity.get(entity_id, set())
        impacted |= inv.diagram_paths_by_entity.get(entity_id, set())


def serialize_result(result: VerificationResult) -> dict:
    return {
        "file_type": result.file_type,
        "issues": [
            {
                "severity": i.severity,
                "code": i.code,
                "message": i.message,
                "location": i.location,
            }
            for i in result.issues
        ],
    }


def git_head(repo_path: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    head = proc.stdout.strip()
    return head or None

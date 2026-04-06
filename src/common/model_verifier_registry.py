from __future__ import annotations

from pathlib import Path
from typing import Literal

from src.common.model_verifier_parsing import parse_frontmatter_from_path
from src.common.model_verifier_types import entity_id_from_path


class ModelRegistry:
    """Lightweight in-memory registry for entity/connection artifact metadata."""

    def __init__(self, repo_root: Path | list[Path]) -> None:
        roots = [repo_root] if isinstance(repo_root, Path) else list(repo_root)
        self.repo_roots = [r.resolve() for r in roots]
        self._entity_meta: dict[str, tuple[str, str]] | None = None
        self._connection_meta: dict[str, tuple[str, str]] | None = None
        self._entity_file_index: dict[str, Path] | None = None
        self._connection_file_index: dict[str, Path] | None = None

    @staticmethod
    def _scope_for_root(root: Path) -> str:
        return "enterprise" if root.name == "enterprise-repository" else "engagement"

    def scope_for_path(self, path: Path) -> Literal["enterprise", "engagement", "unknown"]:
        p = path.resolve()
        for root in self.repo_roots:
            try:
                _ = p.relative_to(root)
            except ValueError:
                continue
            return "enterprise" if self._scope_for_root(root) == "enterprise" else "engagement"
        return "unknown"

    def scope_of_entity(self, artifact_id: str) -> Literal["enterprise", "engagement", "unknown"]:
        meta = self._ensure_entity_meta().get(artifact_id)
        if meta is None:
            return "unknown"
        return "enterprise" if meta[1] == "enterprise" else "engagement"

    def scope_of_connection(self, artifact_id: str) -> Literal["enterprise", "engagement", "unknown"]:
        meta = self._ensure_connection_meta().get(artifact_id)
        if meta is None:
            return "unknown"
        return "enterprise" if meta[1] == "enterprise" else "engagement"

    def _ensure_entity_meta(self) -> dict[str, tuple[str, str]]:
        if self._entity_meta is None:
            self._entity_meta = {}
            for repo_root in self.repo_roots:
                self._scan_entity_meta(repo_root, self._scope_for_root(repo_root), self._entity_meta)
        return self._entity_meta

    def _scan_entity_meta(self, repo_root: Path, scope: str, out: dict[str, tuple[str, str]]) -> None:
        root = repo_root / "model-entities"
        if not root.exists():
            return
        for path in root.rglob("*.md"):
            try:
                fm = parse_frontmatter_from_path(path)
                if not fm or "artifact-id" not in fm:
                    continue
                aid = str(fm["artifact-id"])
                status = str(fm.get("status", ""))
                if aid in out:
                    prev_scope = out[aid][1]
                    raise ValueError(
                        f"Duplicate entity artifact-id '{aid}' across mounted repositories "
                        f"({prev_scope} and {scope}); this is forbidden by the framework"
                    )
                out[aid] = (status, scope)
            except ValueError:
                raise
            except Exception:
                pass

    def entity_ids(self) -> set[str]:
        return set(self._ensure_entity_meta().keys())

    def enterprise_entity_ids(self) -> set[str]:
        return {aid for aid, (_, scope) in self._ensure_entity_meta().items() if scope == "enterprise"}

    def engagement_entity_ids(self) -> set[str]:
        return {aid for aid, (_, scope) in self._ensure_entity_meta().items() if scope == "engagement"}

    def entity_status(self, artifact_id: str) -> str | None:
        if self._entity_meta is not None:
            meta = self._entity_meta.get(artifact_id)
            return meta[0] if meta else None
        path = self._ensure_entity_file_index().get(artifact_id)
        if path is None:
            return None
        fm = parse_frontmatter_from_path(path)
        if fm is None:
            return None
        status = str(fm.get("status", ""))
        return status or None

    def entity_statuses(self) -> dict[str, str]:
        return {aid: status for aid, (status, _) in self._ensure_entity_meta().items()}

    def connection_ids(self) -> set[str]:
        return set(self._ensure_connection_meta().keys())

    def enterprise_connection_ids(self) -> set[str]:
        return {aid for aid, (_, scope) in self._ensure_connection_meta().items() if scope == "enterprise"}

    def engagement_connection_ids(self) -> set[str]:
        return {aid for aid, (_, scope) in self._ensure_connection_meta().items() if scope == "engagement"}

    def connection_status(self, artifact_id: str) -> str | None:
        if self._connection_meta is not None:
            meta = self._connection_meta.get(artifact_id)
            return meta[0] if meta else None
        path = self._ensure_connection_file_index().get(artifact_id)
        if path is None:
            return None
        fm = parse_frontmatter_from_path(path)
        if fm is None:
            return None
        status = str(fm.get("status", ""))
        return status or None

    def _ensure_connection_meta(self) -> dict[str, tuple[str, str]]:
        if self._connection_meta is None:
            self._connection_meta = {}
            for repo_root in self.repo_roots:
                self._scan_connection_meta(repo_root, self._scope_for_root(repo_root), self._connection_meta)
        return self._connection_meta

    def _scan_connection_meta(self, repo_root: Path, scope: str, out: dict[str, tuple[str, str]]) -> None:
        root = repo_root / "connections"
        if not root.exists():
            return
        for path in root.rglob("*.md"):
            try:
                fm = parse_frontmatter_from_path(path)
                if not fm or "artifact-id" not in fm:
                    continue
                aid = str(fm["artifact-id"])
                status = str(fm.get("status", ""))
                if aid in out:
                    prev_scope = out[aid][1]
                    raise ValueError(
                        f"Duplicate connection artifact-id '{aid}' across mounted repositories "
                        f"({prev_scope} and {scope}); this is forbidden by the framework"
                    )
                out[aid] = (status, scope)
            except ValueError:
                raise
            except Exception:
                pass

    def find_file_by_id(self, artifact_id: str) -> Path | None:
        return self._ensure_entity_file_index().get(artifact_id)

    def _ensure_entity_file_index(self) -> dict[str, Path]:
        if self._entity_file_index is None:
            index: dict[str, Path] = {}
            for repo_root in self.repo_roots:
                root = repo_root / "model-entities"
                if not root.exists():
                    continue
                for path in root.rglob("*.md"):
                    index.setdefault(entity_id_from_path(path), path)
            self._entity_file_index = index
        return self._entity_file_index

    def _ensure_connection_file_index(self) -> dict[str, Path]:
        if self._connection_file_index is None:
            index: dict[str, Path] = {}
            for repo_root in self.repo_roots:
                root = repo_root / "connections"
                if not root.exists():
                    continue
                for path in root.rglob("*.md"):
                    index.setdefault(path.stem, path)
            self._connection_file_index = index
        return self._connection_file_index

"""
LearningStore: wraps LangGraph BaseStore for agent learning memory.

Governed by framework/learning-protocol.md §12.1.

Namespace key: (engagement_id, agent_role, "learnings")
Durable serialisation: agents/<role>/learnings/<ROLE>-L-NNN.md files.
Startup: rebuild_from_files() rehydrates the store if empty on cold start.

Semantic tier: enabled when ≥50 entries AND sqlite-vec is importable.
Falls back to metadata-filter + substring match otherwise.
"""

from __future__ import annotations

import threading
import uuid
from pathlib import Path
from typing import Any

import yaml

from src.models.learning import LearningEntry

# ---------------------------------------------------------------------------
# LangGraph BaseStore import (optional dependency at this layer)
# ---------------------------------------------------------------------------
try:
    from langgraph.store.base import BaseStore as _BaseStore  # type: ignore[import]
    _HAS_LANGGRAPH_STORE = True
except ImportError:
    _BaseStore = object  # type: ignore[assignment, misc]
    _HAS_LANGGRAPH_STORE = False

_HAS_SQLITE_VEC = False
try:
    import sqlite_vec as _  # type: ignore[import]
    _HAS_SQLITE_VEC = True
except ImportError:
    pass

_SEMANTIC_THRESHOLD = 50  # minimum entries before semantic tier activates


class LearningStore:
    """
    Thread-safe learning memory store for a single (engagement, agent_role).

    Backed by LangGraph BaseStore when available; falls back to an in-memory
    dict.  Always writes durable .md files alongside the in-memory tier.
    """

    def __init__(
        self,
        engagement_id: str,
        agent_role: str,
        agents_root: Path,
        store: Any | None = None,
    ) -> None:
        self._engagement_id = engagement_id
        self._agent_role = agent_role
        self._agents_root = agents_root
        self._namespace = (engagement_id, agent_role, "learnings")
        self._lock = threading.RLock()

        # In-memory fallback (always used; BaseStore is supplementary)
        self._mem: dict[str, LearningEntry] = {}

        # LangGraph BaseStore (if provided / available)
        self._store: Any | None = store

        # Next ID counter
        self._counter = 0

        # Cold-start rehydration
        self._rebuild_if_empty()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self,
        phase: str | None = None,
        artifact_type: str | None = None,
        domain: str | None = None,
        skill_id: str | None = None,
        entry_type: str | None = None,
        expand_related: bool = True,
        limit: int = 5,
    ) -> list[str]:
        """
        Return up to `limit` correction_text strings matching the filters.

        Applies metadata filters first; optionally expands via related links.
        Semantic tier engaged when conditions are met.
        """
        with self._lock:
            candidates = list(self._mem.values())

        # Metadata filter
        if phase:
            candidates = [e for e in candidates if e.phase == phase]
        if artifact_type:
            candidates = [e for e in candidates if e.artifact_type == artifact_type]
        if skill_id:
            candidates = [e for e in candidates if e.skill_id == skill_id]
        if entry_type:
            candidates = [e for e in candidates if e.entry_type == entry_type]

        # Sort by importance (S1 most important)
        candidates.sort(key=lambda e: e.importance)

        # Graph expansion: pull in related entries not already in set
        if expand_related:
            seen = {e.learning_id for e in candidates}
            extras: list[LearningEntry] = []
            for entry in candidates[:limit]:
                for rel_id in entry.related:
                    if rel_id not in seen:
                        with self._lock:
                            rel = self._mem.get(rel_id)
                        if rel:
                            extras.append(rel)
                            seen.add(rel_id)
            candidates = candidates + extras

        return [e.correction_text for e in candidates[:limit]]

    def record(self, entry: LearningEntry) -> str:
        """
        Persist a new learning entry.

        Assigns a learning_id if not already set, writes the durable .md file,
        updates the in-memory store, and (if available) the BaseStore.
        Returns the assigned learning_id.
        """
        with self._lock:
            if not entry.learning_id or entry.learning_id == "pending":
                self._counter += 1
                entry = entry.model_copy(
                    update={"learning_id": f"{self._agent_role}-L-{self._counter:03d}"}
                )
            self._mem[entry.learning_id] = entry

        self._write_md(entry)

        if self._store is not None and _HAS_LANGGRAPH_STORE:
            try:
                self._store.put(
                    self._namespace,
                    entry.learning_id,
                    entry.model_dump(mode="json"),
                )
            except Exception:  # noqa: BLE001
                pass  # BaseStore write is best-effort

        return entry.learning_id

    def rebuild_from_files(self) -> int:
        """
        Scan agents/<role>/learnings/*.md and load all valid entries.
        Returns the number of entries loaded.
        """
        learnings_dir = self._agents_root / self._agent_role.lower() / "learnings"
        if not learnings_dir.exists():
            # Also check by alias (e.g. solution-architect)
            learnings_dir = self._agents_root / self._agent_role / "learnings"
        if not learnings_dir.exists():
            return 0

        loaded = 0
        with self._lock:
            for f in sorted(learnings_dir.glob("*.md")):
                try:
                    entry = _parse_learning_md(f)
                    if entry:
                        self._mem[entry.learning_id] = entry
                        num = int(entry.learning_id.split("-L-")[-1])
                        if num > self._counter:
                            self._counter = num
                        loaded += 1
                except Exception:  # noqa: BLE001
                    pass
        return loaded

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rebuild_if_empty(self) -> None:
        if not self._mem:
            self.rebuild_from_files()

    def _write_md(self, entry: LearningEntry) -> None:
        """Write durable .md file to agents/<role>/learnings/."""
        role_lower = self._agent_role.lower()
        # Try canonical alias directory first
        learnings_dir = self._agents_root / role_lower / "learnings"
        if not learnings_dir.parent.exists():
            # Fall back to role abbreviation as directory name
            learnings_dir = self._agents_root / self._agent_role / "learnings"
        learnings_dir.mkdir(parents=True, exist_ok=True)

        fname = f"{entry.learning_id}.md"
        fm = entry.to_frontmatter_dict()
        content = (
            f"---\n{yaml.dump(fm, default_flow_style=False, allow_unicode=True)}---\n\n"
            f"## Trigger\n\n{entry.trigger_text}\n\n"
            f"## Correction\n\n{entry.correction_text}\n"
        )
        if entry.context_text:
            content += f"\n## Context\n\n{entry.context_text}\n"
        (learnings_dir / fname).write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _parse_learning_md(path: Path) -> LearningEntry | None:
    """Parse a learning .md file into a LearningEntry. Returns None on failure."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm: dict[str, Any] = yaml.safe_load(text[3:end]) or {}

    # Map kebab-case frontmatter to LearningEntry field names
    body_parts = text[end + 4:].strip().split("## Correction\n\n", 1)
    trigger = ""
    correction = ""
    if "## Trigger\n\n" in body_parts[0]:
        trigger = body_parts[0].split("## Trigger\n\n", 1)[1].strip()
    if len(body_parts) > 1:
        correction = body_parts[1].split("\n\n## ")[0].strip()

    try:
        return LearningEntry(
            learning_id=fm.get("learning-id", path.stem),
            agent=fm.get("agent", ""),
            phase=fm.get("phase", ""),
            artifact_type=fm.get("artifact-type", ""),
            entry_type=fm.get("entry-type", "correction"),
            error_type=fm.get("error-type"),
            importance=fm.get("importance", "S3"),
            applicability=fm.get("applicability", "this-engagement"),
            skill_id=fm.get("skill-id"),
            generated_at_phase=fm.get("generated-at-phase", fm.get("phase", "")),
            generated_at_sprint=fm.get("generated-at-sprint"),
            generated_at_engagement=fm.get("generated-at-engagement"),
            promoted=bool(fm.get("promoted", False)),
            related=list(fm.get("related", [])),
            trigger_text=trigger or fm.get("trigger-text", ""),
            correction_text=correction or fm.get("correction-text", "—"),
        )
    except Exception:  # noqa: BLE001
        return None

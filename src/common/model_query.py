"""
ERP v2.0 Model Query — rich indexed registry with metadata filtering and text search.

Provides a high-level query API over model-entities/, connections/, and
diagram-catalog/diagrams/ within any architecture-repository root.  Designed for
two uses:

  1. Agent tool layer (Stage 5b) — ``list_artifacts``, ``search_artifacts``,
     ``read_artifact`` tools delegate here for metadata-driven retrieval.
  2. Standalone / AI-assisted work — CLI entry point and direct Python import
     for exploring the ENG-001 reference model during framework development.

Architecture
------------
- ``EntityRecord``, ``ConnectionRecord``, ``DiagramRecord`` — frozen dataclasses
  with all frontmatter fields *plus* path-derived metadata (layer, sublayer,
  conn_lang, conn_type).
- ``ModelRepository`` — lazy-loaded index; call :meth:`refresh` to re-scan.
  Exposes ``list_*``, ``get_*``, ``find_connections_for``, ``find_neighbors``,
  and ``search`` methods.
- ``keyword_score`` — simple TF-IDF-style keyword scorer used by ``search``.
  Pluggable via ``SemanticSearchProvider`` Protocol for future sqlite-vec
  embedding supplement (governed by framework/learning-protocol.md §12).
- CLI — ``python -m src.common.model_query <subcommand>`` for interactive use.

Governed by:
  - framework/artifact-registry-design.md
  - framework/diagram-conventions.md §9
  - framework/discovery-protocol.md §8 (list_artifacts / search_artifacts spec)
"""

from __future__ import annotations

import math
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

import yaml

from src.common.domain_vocabulary import expand_tokens
from src.common.model_verifier import entity_id_from_path

# ---------------------------------------------------------------------------
# Record types
# ---------------------------------------------------------------------------

#: ArchiMate / engagement layer names derived from path component.
Layer = Literal[
    "motivation", "strategy", "business", "application", "technology", "implementation", "unknown"
]


MountScope = Literal["engagement", "enterprise"]


@dataclass(frozen=True)
class RepoMount:
    """One mounted ERP v2.0 repository root.

    The unified registry for an engagement indexes both engagement-scope and
    enterprise-scope repository roots (framework/artifact-registry-design.md §6.1).
    """

    root: Path
    scope: MountScope
    # Engagement label to expose via the record.engagement field.
    # Enterprise mount always uses "enterprise".
    engagement_label: str


class DuplicateArtifactIdError(ValueError):
    pass


def _infer_engagement_label(root: Path, *, scope: MountScope) -> str:
    if scope == "enterprise":
        return "enterprise"
    # Engagement: try to infer from path .../engagements/<ID>/work-repositories/...
    parts = root.resolve().parts
    if "engagements" in parts:
        idx = parts.index("engagements")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def _infer_mount(root: Path) -> RepoMount:
    resolved = root.resolve()
    scope: MountScope = "enterprise" if resolved.name == "enterprise-repository" else "engagement"
    return RepoMount(root=resolved, scope=scope, engagement_label=_infer_engagement_label(resolved, scope=scope))


@dataclass(frozen=True)
class EntityRecord:
    """Full data record for one model-entity file."""

    artifact_id: str
    artifact_type: str
    name: str
    version: str
    status: str
    phase_produced: str
    owner_agent: str
    safety_relevant: bool
    engagement: str
    layer: Layer
    sublayer: str          # second path component, e.g. "capabilities", "processes"
    path: Path
    extra: dict[str, object]   # additional frontmatter fields not in the standard set
    content_text: str          # §content section body (empty string if absent)
    display_blocks: dict[str, str]  # lang → raw YAML/text block inside ### <lang>
    display_label: str         # archimate label= value (or name fallback) — indexed for search
    display_alias: str         # archimate alias= value — indexed for search

    def __str__(self) -> str:
        return (
            f"[{self.artifact_id}] {self.name}  "
            f"({self.artifact_type} · {self.layer}/{self.sublayer} · "
            f"agent={self.owner_agent} · phase={self.phase_produced} · "
            f"status={self.status})"
        )


@dataclass(frozen=True)
class ConnectionRecord:
    """Full data record for one connection file."""

    artifact_id: str
    artifact_type: str
    source: str | list[str]   # single or multi-source (schema allows list)
    target: str | list[str]
    version: str
    status: str
    phase_produced: str
    owner_agent: str
    engagement: str
    conn_lang: str   # archimate | er | sequence | activity | usecase — from path
    conn_type: str   # realization | assignment | serving | … — from path subdir
    path: Path
    extra: dict[str, object]
    content_text: str

    @property
    def source_ids(self) -> list[str]:
        return self.source if isinstance(self.source, list) else [self.source]

    @property
    def target_ids(self) -> list[str]:
        return self.target if isinstance(self.target, list) else [self.target]

    def involves(self, entity_id: str) -> bool:
        return entity_id in self.source_ids or entity_id in self.target_ids

    def __str__(self) -> str:
        src = ", ".join(self.source_ids)
        tgt = ", ".join(self.target_ids)
        return (
            f"[{self.artifact_id}]  {src} --{self.conn_type}--> {tgt}  "
            f"({self.conn_lang} · agent={self.owner_agent} · phase={self.phase_produced})"
        )


@dataclass(frozen=True)
class DiagramRecord:
    """Full data record for one .puml diagram file."""

    artifact_id: str
    artifact_type: str
    name: str
    diagram_type: str
    version: str
    status: str
    phase_produced: str
    owner_agent: str
    engagement: str
    entity_ids_used: list[str]
    connection_ids_used: list[str]
    path: Path
    extra: dict[str, object]

    def __str__(self) -> str:
        return (
            f"[{self.artifact_id}] {self.name}  "
            f"({self.diagram_type} · agent={self.owner_agent} · "
            f"phase={self.phase_produced} · status={self.status})"
        )


# ---------------------------------------------------------------------------
# Search types
# ---------------------------------------------------------------------------


@dataclass
class SearchHit:
    score: float
    record_type: Literal["entity", "connection", "diagram"]
    record: EntityRecord | ConnectionRecord | DiagramRecord

    def __str__(self) -> str:
        return f"  score={self.score:.3f}  {self.record}"


@dataclass
class SearchResult:
    query: str
    hits: list[SearchHit] = field(default_factory=list)

    def __str__(self) -> str:
        if not self.hits:
            return f"No results for '{self.query}'"
        lines = [f"Search results for '{self.query}' ({len(self.hits)} hits):"]
        for h in self.hits:
            lines.append(str(h))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Framework-aligned lightweight summary type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArtifactSummary:
    """
    Metadata-only view returned by :meth:`ModelRepository.list_artifacts`.

    Mirrors the *metadata record* described in framework/discovery-protocol.md §1.2:
    ``artifact-id``, ``artifact-type``, ``version``, ``status``, ``path``,
    ``owner-agent`` — without loading the artifact body.  Callers that need the
    body call :meth:`ModelRepository.read_artifact`.
    """

    artifact_id: str
    artifact_type: str
    name: str          # empty string for connections (no name field)
    version: str
    status: str
    phase_produced: str
    owner_agent: str
    engagement: str
    record_type: Literal["entity", "connection", "diagram"]
    path: Path

    def __str__(self) -> str:
        label = f" {self.name}" if self.name else ""
        return (
            f"[{self.artifact_id}]{label}  "
            f"({self.artifact_type} · {self.record_type} · "
            f"agent={self.owner_agent} · phase={self.phase_produced} · "
            f"status={self.status})"
        )


def _summary_from_entity(rec: EntityRecord) -> ArtifactSummary:
    return ArtifactSummary(
        artifact_id=rec.artifact_id,
        artifact_type=rec.artifact_type,
        name=rec.name,
        version=rec.version,
        status=rec.status,
        phase_produced=rec.phase_produced,
        owner_agent=rec.owner_agent,
        engagement=rec.engagement,
        record_type="entity",
        path=rec.path,
    )


def _summary_from_connection(rec: ConnectionRecord) -> ArtifactSummary:
    return ArtifactSummary(
        artifact_id=rec.artifact_id,
        artifact_type=rec.artifact_type,
        name="",
        version=rec.version,
        status=rec.status,
        phase_produced=rec.phase_produced,
        owner_agent=rec.owner_agent,
        engagement=rec.engagement,
        record_type="connection",
        path=rec.path,
    )


def _summary_from_diagram(rec: DiagramRecord) -> ArtifactSummary:
    return ArtifactSummary(
        artifact_id=rec.artifact_id,
        artifact_type=rec.artifact_type,
        name=rec.name,
        version=rec.version,
        status=rec.status,
        phase_produced=rec.phase_produced,
        owner_agent=rec.owner_agent,
        engagement=rec.engagement,
        record_type="diagram",
        path=rec.path,
    )


# ---------------------------------------------------------------------------
# Semantic search extension point
# ---------------------------------------------------------------------------


@runtime_checkable
class SemanticSearchProvider(Protocol):
    """
    Optional semantic supplement for ``ModelRepository.search``.

    Implement this protocol and pass an instance to ``ModelRepository`` to
    augment keyword results with embedding-based similarity (e.g. sqlite-vec).
    Governed by framework/learning-protocol.md §12.2.
    """

    def top_k(
        self,
        query: str,
        k: int,
        *,
        threshold: float = 0.75,
    ) -> list[tuple[float, str]]:
        """Return up to *k* (score, artifact_id) pairs above *threshold*."""
        ...


# ---------------------------------------------------------------------------
# ModelRepository
# ---------------------------------------------------------------------------

_STANDARD_ENTITY_FIELDS = frozenset({
    "artifact-id", "artifact-type", "name", "version", "status",
    "phase-produced", "owner-agent", "safety-relevant", "last-updated", "engagement",
    "produced-by-skill",
})

_STANDARD_CONNECTION_FIELDS = frozenset({
    "artifact-id", "artifact-type", "source", "target", "version", "status",
    "phase-produced", "owner-agent", "last-updated", "engagement",
    "produced-by-skill",
})

_STANDARD_DIAGRAM_FIELDS = frozenset({
    "artifact-id", "artifact-type", "name", "diagram-type", "version", "status",
    "phase-produced", "owner-agent", "engagement", "entity-ids-used",
    "connection-ids-used", "produced-by-skill",
})

_LAYER_NAMES: frozenset[str] = frozenset({
    "motivation", "strategy", "business", "application", "technology", "implementation"
})


class ModelRepository:
    """
    Full indexed registry for model-entities, connections, and diagrams.

    Lazy-loaded on first query; call :meth:`refresh` to force a re-scan.
    All ``list_*`` and ``get_*`` methods accept ``None`` for any filter
    parameter, which means "no constraint on that field".

    Parameters
    ----------
    repo_root:
        Path to an architecture-repository root containing ``model-entities/``,
        ``connections/``, and ``diagram-catalog/``.
    semantic_provider:
        Optional :class:`SemanticSearchProvider` for embedding-based supplement
        in :meth:`search`.  When absent, only keyword scoring is used.
    """

    def __init__(
        self,
        repo_root: Path | list[Path] | list[RepoMount],
        semantic_provider: SemanticSearchProvider | None = None,
    ) -> None:
        # Back-compat: accept a single Path as before.
        if isinstance(repo_root, Path):
            mounts: list[RepoMount] = [_infer_mount(repo_root)]
        else:
            mounts = [m if isinstance(m, RepoMount) else _infer_mount(m) for m in repo_root]

        # Hard guarantee: within a unified session registry, one artifact-id must
        # not exist in more than one mounted repository.
        roots = [m.root for m in mounts]
        if len(set(map(str, roots))) != len(roots):
            raise ValueError("Duplicate repo root in ModelRepository mounts")

        self.repo_mounts = mounts
        # Preserve old attribute name for callers.
        self.repo_root = mounts[0].root
        self._semantic = semantic_provider
        self._entities: dict[str, EntityRecord] | None = None
        self._connections: dict[str, ConnectionRecord] | None = None
        self._diagrams: dict[str, DiagramRecord] | None = None

    # ------------------------------------------------------------------
    # Loading & refresh
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._entities is None:
            self._load_all()

    def refresh(self) -> None:
        """Discard the cache and re-scan the repository on the next access."""
        self._entities = None
        self._connections = None
        self._diagrams = None

    def _load_all(self) -> None:
        self._entities = {}
        self._connections = {}
        self._diagrams = {}

        for mount in self.repo_mounts:
            entities_root = mount.root / "model-entities"
            if entities_root.exists():
                for f in sorted(entities_root.rglob("*.md")):
                    rec = _parse_entity(f, entities_root, mount)
                    if rec is not None:
                        if rec.artifact_id in self._entities:  # type: ignore[operator]
                            other = self._entities[rec.artifact_id].path  # type: ignore[index]
                            raise DuplicateArtifactIdError(
                                f"Duplicate entity artifact-id '{rec.artifact_id}' in {f} and {other}"
                            )
                        self._entities[rec.artifact_id] = rec  # type: ignore[index]

            connections_root = mount.root / "connections"
            if connections_root.exists():
                for f in sorted(connections_root.rglob("*.md")):
                    rec = _parse_connection(f, connections_root, mount)
                    if rec is not None:
                        if rec.artifact_id in self._connections:  # type: ignore[operator]
                            other = self._connections[rec.artifact_id].path  # type: ignore[index]
                            raise DuplicateArtifactIdError(
                                f"Duplicate connection artifact-id '{rec.artifact_id}' in {f} and {other}"
                            )
                        self._connections[rec.artifact_id] = rec  # type: ignore[index]

            diagrams_root = mount.root / "diagram-catalog" / "diagrams"
            if diagrams_root.exists():
                for f in sorted(diagrams_root.rglob("*.puml")):
                    rec = _parse_diagram(f, mount)
                    if rec is not None:
                        if rec.artifact_id in self._diagrams:  # type: ignore[operator]
                            other = self._diagrams[rec.artifact_id].path  # type: ignore[index]
                            raise DuplicateArtifactIdError(
                                f"Duplicate diagram artifact-id '{rec.artifact_id}' in {f} and {other}"
                            )
                        self._diagrams[rec.artifact_id] = rec  # type: ignore[index]

    # ------------------------------------------------------------------
    # Direct lookup
    # ------------------------------------------------------------------

    def get_entity(self, artifact_id: str) -> EntityRecord | None:
        self._ensure_loaded()
        return self._entities.get(artifact_id)  # type: ignore[union-attr]

    def get_connection(self, artifact_id: str) -> ConnectionRecord | None:
        self._ensure_loaded()
        return self._connections.get(artifact_id)  # type: ignore[union-attr]

    def get_diagram(self, artifact_id: str) -> DiagramRecord | None:
        self._ensure_loaded()
        return self._diagrams.get(artifact_id)  # type: ignore[union-attr]

    # ------------------------------------------------------------------
    # List / filter
    # ------------------------------------------------------------------

    def list_entities(
        self,
        *,
        artifact_type: str | None = None,
        layer: str | None = None,
        sublayer: str | None = None,
        owner_agent: str | None = None,
        phase_produced: str | None = None,
        status: str | None = None,
        safety_relevant: bool | None = None,
        engagement: str | None = None,
    ) -> list[EntityRecord]:
        """Return entities matching all supplied filter criteria (AND semantics)."""
        self._ensure_loaded()
        results: list[EntityRecord] = []
        for rec in self._entities.values():  # type: ignore[union-attr]
            if artifact_type is not None and rec.artifact_type != artifact_type:
                continue
            if layer is not None and rec.layer != layer:
                continue
            if sublayer is not None and rec.sublayer != sublayer:
                continue
            if owner_agent is not None and rec.owner_agent != owner_agent:
                continue
            if phase_produced is not None and rec.phase_produced != phase_produced:
                continue
            if status is not None and rec.status != status:
                continue
            if safety_relevant is not None and rec.safety_relevant != safety_relevant:
                continue
            if engagement is not None and rec.engagement != engagement:
                continue
            results.append(rec)
        return sorted(results, key=lambda r: r.artifact_id)

    def list_connections(
        self,
        *,
        artifact_type: str | None = None,
        conn_lang: str | None = None,
        conn_type: str | None = None,
        source: str | None = None,
        target: str | None = None,
        owner_agent: str | None = None,
        phase_produced: str | None = None,
        engagement: str | None = None,
    ) -> list[ConnectionRecord]:
        """Return connections matching all supplied filter criteria (AND semantics).

        *source* / *target* filters match if the supplied ID appears anywhere in
        the (potentially multi-valued) source / target lists.
        """
        self._ensure_loaded()
        results: list[ConnectionRecord] = []
        for rec in self._connections.values():  # type: ignore[union-attr]
            if artifact_type is not None and rec.artifact_type != artifact_type:
                continue
            if conn_lang is not None and rec.conn_lang != conn_lang:
                continue
            if conn_type is not None and rec.conn_type != conn_type:
                continue
            if source is not None and source not in rec.source_ids:
                continue
            if target is not None and target not in rec.target_ids:
                continue
            if owner_agent is not None and rec.owner_agent != owner_agent:
                continue
            if phase_produced is not None and rec.phase_produced != phase_produced:
                continue
            if engagement is not None and rec.engagement != engagement:
                continue
            results.append(rec)
        return sorted(results, key=lambda r: r.artifact_id)

    def list_diagrams(
        self,
        *,
        diagram_type: str | None = None,
        owner_agent: str | None = None,
        phase_produced: str | None = None,
        status: str | None = None,
        engagement: str | None = None,
    ) -> list[DiagramRecord]:
        """Return diagrams matching all supplied filter criteria (AND semantics)."""
        self._ensure_loaded()
        results: list[DiagramRecord] = []
        for rec in self._diagrams.values():  # type: ignore[union-attr]
            if diagram_type is not None and rec.diagram_type != diagram_type:
                continue
            if owner_agent is not None and rec.owner_agent != owner_agent:
                continue
            if phase_produced is not None and rec.phase_produced != phase_produced:
                continue
            if status is not None and rec.status != status:
                continue
            if engagement is not None and rec.engagement != engagement:
                continue
            results.append(rec)
        return sorted(results, key=lambda r: r.artifact_id)

    # ------------------------------------------------------------------
    # Framework-aligned tool interface
    # ------------------------------------------------------------------

    def list_artifacts(
        self,
        *,
        artifact_type: str | list[str] | None = None,
        layer: str | list[str] | None = None,
        owner_agent: str | list[str] | None = None,
        phase_produced: str | list[str] | None = None,
        status: str | list[str] | None = None,
        safety_relevant: bool | None = None,
        engagement: str | None = None,
        include_connections: bool = False,
        include_diagrams: bool = False,
    ) -> list[ArtifactSummary]:
        """Framework-aligned metadata filter (mirrors ``list_artifacts`` tool spec).

        Governed by ``framework/discovery-protocol.md §1.2``.  Returns lightweight
        :class:`ArtifactSummary` records — no body text.  Callers that need the
        full artifact body call :meth:`read_artifact`.

        Parameters
        ----------
        artifact_type:
            Single type string or list.  ``None`` = any.
        layer:
            ArchiMate layer string or list.  Applies to entities only.
        owner_agent:
            Agent abbreviation string or list.  ``None`` = any.
        phase_produced:
            Phase letter string or list (``"A"``, ``"B"``, …).  ``None`` = any.
        status:
            Status string or list (``"draft"``, ``"baselined"``, …).  ``None`` = any.
        safety_relevant:
            ``True`` / ``False`` / ``None`` (no constraint).
        engagement:
            Engagement id (e.g. ``"ENG-001"``); or ``"enterprise"`` for the
            enterprise repository when indexed. ``None`` = any.
        include_connections:
            Include connection records in the result.  Default ``False`` because
            agents typically filter entities during discovery.
        include_diagrams:
            Include diagram records in the result.  Default ``False``.
        """
        self._ensure_loaded()

        types = _to_set(artifact_type)
        layers = _to_set(layer)
        agents = _to_set(owner_agent)
        phases = _to_set(phase_produced)
        statuses = _to_set(status)

        results: list[ArtifactSummary] = []

        for rec in self._entities.values():  # type: ignore[union-attr]
            if types and rec.artifact_type not in types:
                continue
            if layers and rec.layer not in layers:
                continue
            if agents and rec.owner_agent not in agents:
                continue
            if phases and rec.phase_produced not in phases:
                continue
            if statuses and rec.status not in statuses:
                continue
            if safety_relevant is not None and rec.safety_relevant != safety_relevant:
                continue
            if engagement is not None and rec.engagement != engagement:
                continue
            results.append(_summary_from_entity(rec))

        if include_connections:
            for rec in self._connections.values():  # type: ignore[union-attr]
                if types and rec.artifact_type not in types:
                    continue
                if agents and rec.owner_agent not in agents:
                    continue
                if phases and rec.phase_produced not in phases:
                    continue
                if statuses and rec.status not in statuses:
                    continue
                if engagement is not None and rec.engagement != engagement:
                    continue
                results.append(_summary_from_connection(rec))

        if include_diagrams:
            for rec in self._diagrams.values():  # type: ignore[union-attr]
                if types and rec.artifact_type not in types:
                    continue
                if agents and rec.owner_agent not in agents:
                    continue
                if phases and rec.phase_produced not in phases:
                    continue
                if statuses and rec.status not in statuses:
                    continue
                if engagement is not None and rec.engagement != engagement:
                    continue
                results.append(_summary_from_diagram(rec))

        return sorted(results, key=lambda s: s.artifact_id)

    def read_artifact(
        self,
        artifact_id: str,
        *,
        mode: Literal["summary", "full"] = "summary",
    ) -> dict[str, object] | None:
        """Framework-aligned artifact reader (mirrors ``read_artifact`` tool spec).

        Governed by ``framework/discovery-protocol.md §1.2``.

        Parameters
        ----------
        artifact_id:
            The formal artifact-id (e.g. ``"APP-001"``).
        mode:
            ``"summary"`` — frontmatter fields + first 400 characters of
            ``§content`` body (≈200–400 tokens, per framework spec).
            ``"full"`` — all frontmatter fields + full ``§content`` body +
            raw ``§display`` blocks.

        Returns
        -------
        dict | None
            ``None`` if the artifact-id is not indexed.  Otherwise a dict with:

            ``summary`` mode keys:
              ``artifact_id``, ``artifact_type``, ``name``, ``version``,
              ``status``, ``phase_produced``, ``owner_agent``, ``engagement``,
              ``record_type``, ``path``, ``content_snippet``

            ``full`` mode adds:
              ``content_text``, ``display_blocks``, ``extra``,
              and (entities/connections only) ``safety_relevant``,
              ``layer``, ``sublayer``, ``conn_lang``, ``conn_type``.
        """
        self._ensure_loaded()

        entity = self._entities.get(artifact_id)  # type: ignore[union-attr]
        if entity is not None:
            return _read_entity(entity, mode=mode)

        conn = self._connections.get(artifact_id)  # type: ignore[union-attr]
        if conn is not None:
            return _read_connection(conn, mode=mode)

        diag = self._diagrams.get(artifact_id)  # type: ignore[union-attr]
        if diag is not None:
            return _read_diagram(diag, mode=mode)

        return None

    def search_artifacts(
        self,
        query: str,
        *,
        limit: int = 10,
        layer: str | list[str] | None = None,
        artifact_type: str | list[str] | None = None,
        engagement: str | None = None,
        include_connections: bool = True,
        include_diagrams: bool = True,
    ) -> SearchResult:
        """Framework-aligned concept search (mirrors ``search_artifacts`` tool spec).

        Governed by ``framework/discovery-protocol.md §1.3``.  Keyword-scored
        full-text search over all indexed artifact fields and ``§content`` bodies.
        When a :class:`SemanticSearchProvider` is present, a semantic supplement
        tier is applied for large corpora.

        Returns a :class:`SearchResult` with ranked :class:`SearchHit` entries
        containing a score and the full matching record.  Callers inspect snippets
        then call :meth:`read_artifact` for selected results.
        """
        layers = _to_set(layer)
        types = _to_set(artifact_type)
        return self.search(
            query,
            limit=limit,
            layers=list(layers) if layers else None,
            entity_types=list(types) if types else None,
            include_connections=include_connections,
            include_diagrams=include_diagrams,
            engagement=engagement,
        )

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, object]:
        """Return a summary of what is indexed."""
        self._ensure_loaded()
        entities = list(self._entities.values())  # type: ignore[union-attr]
        connections = list(self._connections.values())  # type: ignore[union-attr]
        diagrams = list(self._diagrams.values())  # type: ignore[union-attr]

        layers: dict[str, int] = {}
        for e in entities:
            layers[e.layer] = layers.get(e.layer, 0) + 1

        conn_langs: dict[str, int] = {}
        for c in connections:
            conn_langs[c.conn_lang] = conn_langs.get(c.conn_lang, 0) + 1

        return {
            "entities": len(entities),
            "connections": len(connections),
            "diagrams": len(diagrams),
            "entities_by_layer": layers,
            "connections_by_lang": conn_langs,
        }

    # ------------------------------------------------------------------
    # Graph traversal
    # ------------------------------------------------------------------

    def find_connections_for(
        self,
        entity_id: str,
        *,
        direction: Literal["any", "outbound", "inbound"] = "any",
        conn_lang: str | None = None,
        conn_type: str | None = None,
    ) -> list[ConnectionRecord]:
        """Return connections that touch *entity_id*.

        Parameters
        ----------
        entity_id:
            The artifact-id to look up (e.g. ``"APP-001"``).
        direction:
            ``"outbound"`` — entity_id appears in *source*;
            ``"inbound"``  — entity_id appears in *target*;
            ``"any"``      — either.
        conn_lang:
            Optionally restrict to a diagram language (``"archimate"``, …).
        conn_type:
            Optionally restrict to a connection type subdirectory (``"realization"``, …).
        """
        self._ensure_loaded()
        results: list[ConnectionRecord] = []
        for rec in self._connections.values():  # type: ignore[union-attr]
            if conn_lang is not None and rec.conn_lang != conn_lang:
                continue
            if conn_type is not None and rec.conn_type != conn_type:
                continue
            in_src = entity_id in rec.source_ids
            in_tgt = entity_id in rec.target_ids
            match direction:
                case "outbound" if not in_src:
                    continue
                case "inbound" if not in_tgt:
                    continue
                case "any" if not (in_src or in_tgt):
                    continue
            results.append(rec)
        return sorted(results, key=lambda r: r.artifact_id)

    def find_neighbors(
        self,
        entity_id: str,
        *,
        max_hops: int = 1,
        conn_lang: str | None = None,
    ) -> dict[str, set[str]]:
        """Return entity-ids reachable from *entity_id* within *max_hops* hops.

        Returns a dict mapping hop distance (as string ``"1"``, ``"2"``, …) to
        the set of neighbor artifact-ids at that distance.  The origin entity is
        not included.
        """
        self._ensure_loaded()
        visited: set[str] = {entity_id}
        frontier: set[str] = {entity_id}
        result: dict[str, set[str]] = {}

        for hop in range(1, max_hops + 1):
            next_frontier: set[str] = set()
            for eid in frontier:
                for conn in self.find_connections_for(eid, conn_lang=conn_lang):
                    for nid in conn.source_ids + conn.target_ids:
                        if nid not in visited and nid != eid:
                            next_frontier.add(nid)
            next_frontier -= visited
            if not next_frontier:
                break
            result[str(hop)] = next_frontier
            visited |= next_frontier
            frontier = next_frontier

        return result

    # ------------------------------------------------------------------
    # Text / semantic search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        entity_types: list[str] | None = None,
        layers: list[str] | None = None,
        include_connections: bool = True,
        include_diagrams: bool = True,
        engagement: str | None = None,
    ) -> SearchResult:
        """Score all indexed records against *query* and return the top *limit* hits.

        Scoring model (keyword):
          - Name match:        weight 4 (exact substring), 3 (token)
          - artifact_type:     weight 2
          - layer/sublayer:    weight 1.5
          - conn_lang/type:    weight 1.5
          - content_text:      weight 1 per occurrence (TF-IDF normalised)
          - diagram_type:      weight 2

        When a :class:`SemanticSearchProvider` is available and the entity corpus
        has ≥ 50 entries, its top-1 embedding match is merged if its cosine score
        exceeds 0.75 (governed by framework/learning-protocol.md §12.2).
        """
        self._ensure_loaded()

        query_lc = query.lower()
        tokens = _tokenize(query_lc)

        hits: list[SearchHit] = []

        # --- entities ---
        for rec in self._entities.values():  # type: ignore[union-attr]
            if entity_types and rec.artifact_type not in entity_types:
                continue
            if layers and rec.layer not in layers:
                continue
            if engagement is not None and rec.engagement != engagement:
                continue
            score = _score_entity(rec, query_lc, tokens)
            if score > 0:
                hits.append(SearchHit(score=score, record_type="entity", record=rec))

        # --- connections ---
        if include_connections:
            for rec in self._connections.values():  # type: ignore[union-attr]
                if engagement is not None and rec.engagement != engagement:
                    continue
                score = _score_connection(rec, query_lc, tokens)
                if score > 0:
                    hits.append(SearchHit(score=score, record_type="connection", record=rec))

        # --- diagrams ---
        if include_diagrams:
            for rec in self._diagrams.values():  # type: ignore[union-attr]
                if engagement is not None and rec.engagement != engagement:
                    continue
                score = _score_diagram(rec, query_lc, tokens)
                if score > 0:
                    hits.append(SearchHit(score=score, record_type="diagram", record=rec))

        # --- semantic supplement ---
        if (
            self._semantic is not None
            and isinstance(self._semantic, SemanticSearchProvider)
            and len(self._entities) >= 50  # type: ignore[union-attr]
        ):
            sem_hits = self._semantic.top_k(query, k=1, threshold=0.75)
            seen_ids = {h.record.artifact_id for h in hits if hasattr(h.record, "artifact_id")}
            for sem_score, aid in sem_hits:
                if aid not in seen_ids:
                    rec = self._entities.get(aid)  # type: ignore[union-attr]
                    if rec is not None:
                        hits.append(SearchHit(
                            score=sem_score * 3.0,  # rescale to keyword range
                            record_type="entity",
                            record=rec,
                        ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return SearchResult(query=query, hits=hits[:limit])


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _extract_yaml_block(content: str) -> dict | None:
    """Extract the opening --- ... --- YAML block from markdown."""
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(content[3:end].strip()) or {}
    except yaml.YAMLError:
        return None


def _extract_puml_frontmatter(content: str) -> dict | None:
    """Extract YAML from the PUML header comment block (``' ---`` delimiters)."""
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
        else:
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


def _extract_section(content: str, marker: str) -> str:
    """Extract body text between ``<!-- §<marker> -->`` and next such tag."""
    start_tag = f"<!-- §{marker} -->"
    start = content.find(start_tag)
    if start == -1:
        return ""
    body_start = start + len(start_tag)
    # Find next <!-- § ... --> tag
    next_tag = re.search(r"<!-- §\w+ -->", content[body_start:])
    if next_tag:
        return content[body_start : body_start + next_tag.start()].strip()
    return content[body_start:].strip()


def _extract_display_blocks(content: str) -> dict[str, str]:
    """Parse the §display section and extract each ### <lang> block."""
    display_body = _extract_section(content, "display")
    if not display_body:
        return {}
    blocks: dict[str, str] = {}
    # Split on ### <lang> headers
    parts = re.split(r"^###\s+(.+)$", display_body, flags=re.MULTILINE)
    # parts = [pre, lang1, body1, lang2, body2, ...]
    it = iter(parts[1:])  # skip pre-text
    for lang, body in zip(it, it):
        blocks[lang.strip()] = body.strip()
    return blocks


def _derive_layer(path: Path, root: Path) -> tuple[Layer, str]:
    """Derive (layer, sublayer) from the path relative to model-entities/."""
    try:
        rel = path.relative_to(root)
        parts = rel.parts  # e.g. ("business", "processes", "BPR-001.md")
        layer_raw = parts[0] if len(parts) > 0 else "unknown"
        sublayer = parts[1] if len(parts) > 1 else ""
        layer: Layer = layer_raw if layer_raw in _LAYER_NAMES else "unknown"  # type: ignore[assignment]
        return layer, sublayer
    except ValueError:
        return "unknown", ""


def _derive_conn_lang_type(path: Path, root: Path) -> tuple[str, str]:
    """Derive (conn_lang, conn_type) from the path relative to connections/."""
    try:
        rel = path.relative_to(root)
        parts = rel.parts  # e.g. ("archimate", "realization", "X---Y.md")
        conn_lang = parts[0] if len(parts) > 0 else "unknown"
        conn_type = parts[1] if len(parts) > 1 else "unknown"
        return conn_lang, conn_type
    except ValueError:
        return "unknown", "unknown"


def _parse_entity(path: Path, entities_root: Path, mount: RepoMount) -> EntityRecord | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = _extract_yaml_block(content)
    if not fm:
        return None

    artifact_id = str(fm.get("artifact-id", entity_id_from_path(path)))
    artifact_type = str(fm.get("artifact-type", ""))
    name = str(fm.get("name", ""))
    version = str(fm.get("version", ""))
    status = str(fm.get("status", "draft"))
    phase_produced = str(fm.get("phase-produced", ""))
    owner_agent = str(fm.get("owner-agent", ""))
    safety_relevant_raw = fm.get("safety-relevant", False)
    safety_relevant = bool(safety_relevant_raw) if isinstance(safety_relevant_raw, bool) else False
    # Enterprise entities commonly omit the engagement field (stripped on promotion).
    # We derive it from the mount so discovery can filter by engagement="enterprise"
    # as specified in framework/discovery-protocol.md §Layer 2.
    if mount.scope == "enterprise":
        engagement = "enterprise"
    else:
        engagement = str(fm.get("engagement", mount.engagement_label))
    layer, sublayer = _derive_layer(path, entities_root)

    extra = {k: v for k, v in fm.items() if k not in _STANDARD_ENTITY_FIELDS}
    content_text = _extract_section(content, "content")
    display_blocks = _extract_display_blocks(content)

    # Extract archimate display label and alias for search indexing
    display_label, display_alias = _extract_archimate_label_alias(display_blocks)

    return EntityRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        name=name,
        version=version,
        status=status,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        safety_relevant=safety_relevant,
        engagement=engagement,
        layer=layer,
        sublayer=sublayer,
        path=path,
        extra=extra,
        content_text=content_text,
        display_blocks=display_blocks,
        display_label=display_label,
        display_alias=display_alias,
    )


def _parse_connection(path: Path, connections_root: Path, mount: RepoMount) -> ConnectionRecord | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = _extract_yaml_block(content)
    if not fm:
        return None

    artifact_id = str(fm.get("artifact-id", path.stem))
    artifact_type = str(fm.get("artifact-type", ""))
    source_raw = fm.get("source", "")
    target_raw = fm.get("target", "")
    source: str | list[str] = source_raw if isinstance(source_raw, list) else str(source_raw)
    target: str | list[str] = target_raw if isinstance(target_raw, list) else str(target_raw)
    version = str(fm.get("version", ""))
    status = str(fm.get("status", "draft"))
    phase_produced = str(fm.get("phase-produced", ""))
    owner_agent = str(fm.get("owner-agent", ""))
    if mount.scope == "enterprise":
        engagement = "enterprise"
    else:
        engagement = str(fm.get("engagement", mount.engagement_label))
    conn_lang, conn_type = _derive_conn_lang_type(path, connections_root)

    extra = {k: v for k, v in fm.items() if k not in _STANDARD_CONNECTION_FIELDS}
    content_text = _extract_section(content, "content")

    return ConnectionRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        source=source,
        target=target,
        version=version,
        status=status,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        engagement=engagement,
        conn_lang=conn_lang,
        conn_type=conn_type,
        path=path,
        extra=extra,
        content_text=content_text,
    )


def _parse_diagram(path: Path, mount: RepoMount) -> DiagramRecord | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = _extract_puml_frontmatter(content)
    if not fm:
        return None

    artifact_id = str(fm.get("artifact-id", path.stem))
    artifact_type = str(fm.get("artifact-type", "diagram"))
    name = str(fm.get("name", ""))
    diagram_type = str(fm.get("diagram-type", ""))
    version = str(fm.get("version", ""))
    status = str(fm.get("status", "draft"))
    phase_produced = str(fm.get("phase-produced", ""))
    owner_agent = str(fm.get("owner-agent", ""))
    if mount.scope == "enterprise":
        engagement = "enterprise"
    else:
        engagement = str(fm.get("engagement", mount.engagement_label))
    eids_raw = fm.get("entity-ids-used") or []
    cids_raw = fm.get("connection-ids-used") or []
    entity_ids_used = [str(x) for x in eids_raw] if isinstance(eids_raw, list) else []
    connection_ids_used = [str(x) for x in cids_raw] if isinstance(cids_raw, list) else []

    extra = {k: v for k, v in fm.items() if k not in _STANDARD_DIAGRAM_FIELDS}

    return DiagramRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        name=name,
        diagram_type=diagram_type,
        version=version,
        status=status,
        phase_produced=phase_produced,
        owner_agent=owner_agent,
        engagement=engagement,
        entity_ids_used=entity_ids_used,
        connection_ids_used=connection_ids_used,
        path=path,
        extra=extra,
    )


# ---------------------------------------------------------------------------
# Display-block extraction helper
# ---------------------------------------------------------------------------


def _extract_archimate_label_alias(display_blocks: dict[str, str]) -> tuple[str, str]:
    """Extract ``label`` and ``alias`` values from the archimate §display block."""
    archimate_block = display_blocks.get("archimate", "")
    if not archimate_block:
        return "", ""
    # Strip code fences if present
    block = re.sub(r"```\w*\s*|\s*```", " ", archimate_block)
    label_match = re.search(r"label:\s*[\"']?([^\"'\n]+)[\"']?", block)
    alias_match = re.search(r"alias:\s*([A-Za-z0-9_]+)", block)
    label = label_match.group(1).strip() if label_match else ""
    alias = alias_match.group(1).strip() if alias_match else ""
    return label, alias


# ---------------------------------------------------------------------------
# Domain synonym expansion
# ---------------------------------------------------------------------------
# Delegated to src.common.domain_vocabulary — the canonical vocabulary module
# for the SDLC Multi-Agent framework.  model_query.py uses expand_tokens() as
# an alias so scoring functions call _expand_tokens() locally.

_expand_tokens = expand_tokens


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _token_match_score(field_text: str, query_lc: str, tokens: list[str], weight: float) -> float:
    """Score a single field's contribution.  Exact substring = weight; each token = weight/2."""
    if not field_text:
        return 0.0
    field_lc = field_text.lower()
    score = 0.0
    if query_lc in field_lc:
        score += weight
    for tok in tokens:
        if tok in field_lc:
            score += weight * 0.5
    return score


def _content_score(content: str, tokens: list[str], weight: float) -> float:
    """TF-normalised score for content body."""
    if not content or not tokens:
        return 0.0
    content_lc = content.lower()
    word_count = max(len(content_lc.split()), 1)
    tf_sum = 0.0
    for tok in tokens:
        count = content_lc.count(tok)
        if count:
            tf = count / word_count
            tf_sum += weight * (1 + math.log(1 + tf))
    return tf_sum


def _score_entity(rec: EntityRecord, query_lc: str, tokens: list[str]) -> float:
    expanded = _expand_tokens(tokens)
    score = 0.0
    # Name / identity fields (high weight)
    score += _token_match_score(rec.name, query_lc, expanded, 4.0)
    score += _token_match_score(rec.display_label, query_lc, expanded, 3.5)
    score += _token_match_score(rec.artifact_id, query_lc, expanded, 2.5)
    score += _token_match_score(rec.display_alias, query_lc, expanded, 2.0)
    # Structural fields (medium weight)
    score += _token_match_score(rec.artifact_type, query_lc, expanded, 2.0)
    score += _token_match_score(rec.layer, query_lc, expanded, 1.5)
    score += _token_match_score(rec.sublayer, query_lc, expanded, 1.5)
    score += _token_match_score(rec.owner_agent, query_lc, expanded, 1.0)
    score += _token_match_score(rec.phase_produced, query_lc, expanded, 1.0)
    # Content body (TF-normalised, lower weight to avoid noise)
    score += _content_score(rec.content_text, expanded, 1.0)
    # Extra frontmatter fields (tags, domain, summary, etc.)
    for v in rec.extra.values():
        score += _token_match_score(str(v), query_lc, expanded, 0.5)
    return score


def _score_connection(rec: ConnectionRecord, query_lc: str, tokens: list[str]) -> float:
    expanded = _expand_tokens(tokens)
    score = 0.0
    score += _token_match_score(rec.artifact_id, query_lc, expanded, 2.5)
    score += _token_match_score(rec.artifact_type, query_lc, expanded, 2.0)
    score += _token_match_score(rec.conn_lang, query_lc, expanded, 1.5)
    score += _token_match_score(rec.conn_type, query_lc, expanded, 1.5)
    for eid in rec.source_ids + rec.target_ids:
        score += _token_match_score(eid, query_lc, expanded, 1.5)
    score += _content_score(rec.content_text, expanded, 1.0)
    return score


def _score_diagram(rec: DiagramRecord, query_lc: str, tokens: list[str]) -> float:
    expanded = _expand_tokens(tokens)
    score = 0.0
    score += _token_match_score(rec.name, query_lc, expanded, 4.0)
    score += _token_match_score(rec.artifact_id, query_lc, expanded, 2.5)
    score += _token_match_score(rec.diagram_type, query_lc, expanded, 2.0)
    score += _token_match_score(rec.owner_agent, query_lc, expanded, 1.0)
    score += _token_match_score(rec.phase_produced, query_lc, expanded, 1.0)
    return score


# ---------------------------------------------------------------------------
# Helpers for list/set coercion and read_artifact formatting
# ---------------------------------------------------------------------------


def _to_set(value: str | list[str] | None) -> set[str]:
    """Coerce a string, list, or None filter value to a set for fast membership tests."""
    if value is None:
        return set()
    return {value} if isinstance(value, str) else set(value)


def _read_entity(rec: EntityRecord, *, mode: Literal["summary", "full"]) -> dict[str, object]:
    base: dict[str, object] = {
        "artifact_id": rec.artifact_id,
        "artifact_type": rec.artifact_type,
        "name": rec.name,
        "version": rec.version,
        "status": rec.status,
        "phase_produced": rec.phase_produced,
        "owner_agent": rec.owner_agent,
        "safety_relevant": rec.safety_relevant,
        "engagement": rec.engagement,
        "layer": rec.layer,
        "sublayer": rec.sublayer,
        "record_type": "entity",
        "path": str(rec.path),
        "content_snippet": rec.content_text[:400] + ("…" if len(rec.content_text) > 400 else ""),
    }
    if mode == "full":
        base["content_text"] = rec.content_text
        base["display_blocks"] = rec.display_blocks
        base["extra"] = rec.extra
    return base


def _read_connection(rec: ConnectionRecord, *, mode: Literal["summary", "full"]) -> dict[str, object]:
    base: dict[str, object] = {
        "artifact_id": rec.artifact_id,
        "artifact_type": rec.artifact_type,
        "name": "",
        "source": rec.source,
        "target": rec.target,
        "version": rec.version,
        "status": rec.status,
        "phase_produced": rec.phase_produced,
        "owner_agent": rec.owner_agent,
        "engagement": rec.engagement,
        "conn_lang": rec.conn_lang,
        "conn_type": rec.conn_type,
        "record_type": "connection",
        "path": str(rec.path),
        "content_snippet": rec.content_text[:400] + ("…" if len(rec.content_text) > 400 else ""),
    }
    if mode == "full":
        base["content_text"] = rec.content_text
        base["extra"] = rec.extra
    return base


def _read_diagram(rec: DiagramRecord, *, mode: Literal["summary", "full"]) -> dict[str, object]:
    base: dict[str, object] = {
        "artifact_id": rec.artifact_id,
        "artifact_type": rec.artifact_type,
        "name": rec.name,
        "diagram_type": rec.diagram_type,
        "version": rec.version,
        "status": rec.status,
        "phase_produced": rec.phase_produced,
        "owner_agent": rec.owner_agent,
        "engagement": rec.engagement,
        "entity_ids_used": rec.entity_ids_used,
        "connection_ids_used": rec.connection_ids_used,
        "record_type": "diagram",
        "path": str(rec.path),
        "content_snippet": "",
    }
    if mode == "full":
        try:
            base["puml_source"] = rec.path.read_text(encoding="utf-8")
        except OSError:
            base["puml_source"] = ""
        base["extra"] = rec.extra
    return base


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_USAGE = """\
Usage: python -m src.common.model_query <subcommand> [options]

Subcommands:
  stats     [--repo PATH]
      Print counts by layer and connection language.

  entities  [--repo PATH] [--layer LAYER] [--type TYPE] [--agent AGENT]
            [--phase PHASE] [--status STATUS] [--safety-relevant]
      List entities matching the given filters.

  connections [--repo PATH] [--lang LANG] [--type TYPE] [--agent AGENT]
              [--source ID] [--target ID]
      List connections matching the given filters.

  diagrams  [--repo PATH] [--type TYPE] [--agent AGENT] [--phase PHASE]
      List diagrams matching the given filters.

  get       [--repo PATH] ID
      Print full details for an entity, connection, or diagram.

  graph     [--repo PATH] [--hops N] [--lang LANG] ID
      Show connections and N-hop neighbors for an entity.

  search    [--repo PATH] [--limit N] [--layer LAYER] [--entities-only]
            [--connections] [--diagrams] QUERY...
      Keyword-score all records against QUERY.

Defaults:
  --repo    engagements/ENG-001/work-repositories/architecture-repository
  --limit   10
  --hops    1
"""


def _repo_from_args(args: list[str]) -> tuple[Path, list[str]]:
    """Extract --repo PATH from args, return (repo_path, remaining_args)."""
    if "--repo" in args:
        idx = args.index("--repo")
        repo = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
    else:
        repo = Path("engagements/ENG-001/work-repositories/architecture-repository")
    return repo, args


def _flag(args: list[str], flag: str) -> tuple[str | None, list[str]]:
    """Extract --flag VALUE pair, returning (value_or_None, remaining)."""
    if flag in args:
        idx = args.index(flag)
        val = args[idx + 1] if idx + 1 < len(args) else None
        return val, args[:idx] + args[idx + 2:]
    return None, args


def _bool_flag(args: list[str], flag: str) -> tuple[bool, list[str]]:
    if flag in args:
        return True, [a for a in args if a != flag]
    return False, args


def _fmt_entity(rec: EntityRecord, *, verbose: bool = False) -> str:
    lines = [str(rec)]
    if verbose:
        if rec.content_text:
            lines.append(textwrap.indent(rec.content_text[:400], "    "))
        if rec.display_blocks:
            for lang, block in rec.display_blocks.items():
                lines.append(f"    [{lang}]: {block[:100].replace(chr(10), ' ')}")
    return "\n".join(lines)


def _fmt_connection(rec: ConnectionRecord, *, verbose: bool = False) -> str:
    lines = [str(rec)]
    if verbose and rec.content_text:
        lines.append(textwrap.indent(rec.content_text[:300], "    "))
    return "\n".join(lines)


def _fmt_diagram(rec: DiagramRecord, *, verbose: bool = False) -> str:
    lines = [str(rec)]
    if verbose:
        if rec.entity_ids_used:
            lines.append(f"    entities used: {', '.join(rec.entity_ids_used)}")
        if rec.connection_ids_used:
            lines.append(f"    connections used: {', '.join(rec.connection_ids_used)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])

    if not args or args[0] in ("-h", "--help"):
        print(_USAGE)
        return 0

    subcommand = args[0]
    args = args[1:]
    repo, args = _repo_from_args(args)

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}", file=sys.stderr)
        return 1

    registry = ModelRepository(repo)

    # ----- stats ------------------------------------------------------------
    if subcommand == "stats":
        s = registry.stats()
        print(f"Repository: {repo}")
        print(f"  Entities:    {s['entities']}")
        print(f"  Connections: {s['connections']}")
        print(f"  Diagrams:    {s['diagrams']}")
        print("  Entities by layer:")
        for layer, count in sorted(s["entities_by_layer"].items()):  # type: ignore[union-attr]
            print(f"    {layer:20s} {count}")
        print("  Connections by language:")
        for lang, count in sorted(s["connections_by_lang"].items()):  # type: ignore[union-attr]
            print(f"    {lang:20s} {count}")
        return 0

    # ----- entities ---------------------------------------------------------
    if subcommand == "entities":
        layer_val, args = _flag(args, "--layer")
        type_val, args = _flag(args, "--type")
        agent_val, args = _flag(args, "--agent")
        phase_val, args = _flag(args, "--phase")
        status_val, args = _flag(args, "--status")
        safe_flag, args = _bool_flag(args, "--safety-relevant")
        verbose_flag, args = _bool_flag(args, "--verbose")

        recs = registry.list_entities(
            artifact_type=type_val,
            layer=layer_val,
            owner_agent=agent_val,
            phase_produced=phase_val,
            status=status_val,
            safety_relevant=True if safe_flag else None,
        )
        print(f"{len(recs)} entities")
        for rec in recs:
            print(_fmt_entity(rec, verbose=verbose_flag))
        return 0

    # ----- connections -------------------------------------------------------
    if subcommand == "connections":
        lang_val, args = _flag(args, "--lang")
        type_val, args = _flag(args, "--type")
        agent_val, args = _flag(args, "--agent")
        src_val, args = _flag(args, "--source")
        tgt_val, args = _flag(args, "--target")
        verbose_flag, args = _bool_flag(args, "--verbose")

        recs = registry.list_connections(
            conn_lang=lang_val,
            conn_type=type_val,
            owner_agent=agent_val,
            source=src_val,
            target=tgt_val,
        )
        print(f"{len(recs)} connections")
        for rec in recs:
            print(_fmt_connection(rec, verbose=verbose_flag))
        return 0

    # ----- diagrams ---------------------------------------------------------
    if subcommand == "diagrams":
        type_val, args = _flag(args, "--type")
        agent_val, args = _flag(args, "--agent")
        phase_val, args = _flag(args, "--phase")
        status_val, args = _flag(args, "--status")
        verbose_flag, args = _bool_flag(args, "--verbose")

        recs = registry.list_diagrams(
            diagram_type=type_val,
            owner_agent=agent_val,
            phase_produced=phase_val,
            status=status_val,
        )
        print(f"{len(recs)} diagrams")
        for rec in recs:
            print(_fmt_diagram(rec, verbose=verbose_flag))
        return 0

    # ----- get --------------------------------------------------------------
    if subcommand == "get":
        if not args:
            print("Usage: get ID", file=sys.stderr)
            return 1
        artifact_id = args[0]
        # Try entity first, then connection, then diagram
        rec: EntityRecord | ConnectionRecord | DiagramRecord | None
        rec = registry.get_entity(artifact_id)
        if rec is None:
            rec = registry.get_connection(artifact_id)
        if rec is None:
            rec = registry.get_diagram(artifact_id)
        if rec is None:
            print(f"Not found: {artifact_id}")
            return 1

        if isinstance(rec, EntityRecord):
            print(_fmt_entity(rec, verbose=True))
        elif isinstance(rec, ConnectionRecord):
            print(_fmt_connection(rec, verbose=True))
        else:
            print(_fmt_diagram(rec, verbose=True))
        return 0

    # ----- graph ------------------------------------------------------------
    if subcommand == "graph":
        hops_str, args = _flag(args, "--hops")
        lang_val, args = _flag(args, "--lang")
        max_hops = int(hops_str) if hops_str else 1
        if not args:
            print("Usage: graph [--hops N] [--lang LANG] ID", file=sys.stderr)
            return 1
        entity_id = args[0]

        entity = registry.get_entity(entity_id)
        if entity is None:
            print(f"Entity not found: {entity_id}")
            return 1

        print(f"Graph for {entity_id}: {entity.name}")
        print()
        print("Direct connections:")
        conns = registry.find_connections_for(entity_id, conn_lang=lang_val)
        if not conns:
            print("  (none)")
        for c in conns:
            direction = "OUT" if entity_id in c.source_ids else "IN "
            other = (
                ", ".join(c.target_ids) if direction == "OUT" else ", ".join(c.source_ids)
            )
            print(f"  [{direction}] {c.conn_type:20s} → {other}  ({c.artifact_type})")

        if max_hops > 1:
            neighbors = registry.find_neighbors(entity_id, max_hops=max_hops, conn_lang=lang_val)
            for hop, nids in sorted(neighbors.items(), key=lambda x: int(x[0])):
                print(f"\nHop {hop} neighbors:")
                for nid in sorted(nids):
                    n = registry.get_entity(nid)
                    label = n.name if n else nid
                    print(f"  {nid}: {label}")
        return 0

    # ----- search -----------------------------------------------------------
    if subcommand == "search":
        limit_str, args = _flag(args, "--limit")
        layer_val, args = _flag(args, "--layer")
        entities_only, args = _bool_flag(args, "--entities-only")
        include_conns, args = _bool_flag(args, "--connections")
        include_diags, args = _bool_flag(args, "--diagrams")
        limit = int(limit_str) if limit_str else 10

        # remaining args = query terms
        query = " ".join(args)
        if not query:
            print("Usage: search [options] QUERY...", file=sys.stderr)
            return 1

        result = registry.search(
            query,
            limit=limit,
            layers=[layer_val] if layer_val else None,
            include_connections=False if entities_only else (include_conns or not entities_only),
            include_diagrams=False if entities_only else (include_diags or not entities_only),
        )
        print(result)
        return 0

    print(f"Unknown subcommand: {subcommand}\n{_USAGE}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

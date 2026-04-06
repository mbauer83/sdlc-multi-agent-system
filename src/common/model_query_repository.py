"""ERP v2.0 Model Query — indexed query API over entities, connections, and diagrams."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast, overload

from src.common.model_query_parsing import parse_connection, parse_diagram, parse_entity
from src.common.model_query_scoring import score_connection, score_diagram, score_entity, tokenize
from src.common.model_query_types import (
    ArtifactSummary,
    ConnectionRecord,
    DiagramRecord,
    DuplicateArtifactIdError,
    EntityRecord,
    RepoMount,
    SearchHit,
    SearchResult,
    SemanticSearchProvider,
    infer_mount,
    summary_from_connection,
    summary_from_diagram,
    summary_from_entity,
)


class ModelRepository:
    def __init__(
        self,
        repo_root: Path | list[Path] | list[RepoMount],
        semantic_provider: SemanticSearchProvider | None = None,
    ) -> None:
        if isinstance(repo_root, Path):
            mounts: list[RepoMount] = [infer_mount(repo_root)]
        else:
            mounts = [m if isinstance(m, RepoMount) else infer_mount(m) for m in repo_root]

        roots = [m.root for m in mounts]
        if len(set(map(str, roots))) != len(roots):
            raise ValueError("Duplicate repo root in ModelRepository mounts")

        self.repo_mounts = mounts
        self.repo_root = mounts[0].root
        self._semantic = semantic_provider
        self._entities: dict[str, EntityRecord] = {}
        self._connections: dict[str, ConnectionRecord] = {}
        self._diagrams: dict[str, DiagramRecord] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load_all()

    def refresh(self) -> None:
        self._entities = {}
        self._connections = {}
        self._diagrams = {}
        self._loaded = False

    def _load_all(self) -> None:
        self._entities = {}
        self._connections = {}
        self._diagrams = {}
        for mount in self.repo_mounts:
            self._load_entities(mount)
            self._load_connections(mount)
            self._load_diagrams(mount)
        self._loaded = True

    def _load_entities(self, mount: RepoMount) -> None:
        entities_root = mount.root / "model-entities"
        if not entities_root.exists():
            return
        for path in sorted(entities_root.rglob("*.md")):
            rec = parse_entity(path, entities_root, mount)
            if rec is not None:
                self._insert_unique(self._entities, rec.artifact_id, rec, "entity")

    def _load_connections(self, mount: RepoMount) -> None:
        connections_root = mount.root / "connections"
        if not connections_root.exists():
            return
        for path in sorted(connections_root.rglob("*.md")):
            rec = parse_connection(path, connections_root, mount)
            if rec is not None:
                self._insert_unique(self._connections, rec.artifact_id, rec, "connection")

    def _load_diagrams(self, mount: RepoMount) -> None:
        diagrams_root = mount.root / "diagram-catalog" / "diagrams"
        if not diagrams_root.exists():
            return
        for suffix in ("*.puml", "*.md"):
            for path in sorted(diagrams_root.rglob(suffix)):
                rec = parse_diagram(path, mount)
                if rec is not None:
                    self._insert_unique(self._diagrams, rec.artifact_id, rec, "diagram")

    @staticmethod
    @overload
    def _insert_unique(
        store: dict[str, EntityRecord],
        artifact_id: str,
        rec: EntityRecord,
        label: str,
    ) -> None: ...

    @staticmethod
    @overload
    def _insert_unique(
        store: dict[str, ConnectionRecord],
        artifact_id: str,
        rec: ConnectionRecord,
        label: str,
    ) -> None: ...

    @staticmethod
    @overload
    def _insert_unique(
        store: dict[str, DiagramRecord],
        artifact_id: str,
        rec: DiagramRecord,
        label: str,
    ) -> None: ...

    @staticmethod
    def _insert_unique(
        store: dict[str, EntityRecord] | dict[str, ConnectionRecord] | dict[str, DiagramRecord],
        artifact_id: str,
        rec: EntityRecord | ConnectionRecord | DiagramRecord,
        label: str,
    ) -> None:
        existing = store.get(artifact_id)
        if existing is not None:
            raise DuplicateArtifactIdError(
                f"Duplicate {label} artifact-id '{artifact_id}' in {rec.path} and {existing.path}"
            )
        if isinstance(rec, EntityRecord):
            cast("dict[str, EntityRecord]", store)[artifact_id] = rec
            return
        if isinstance(rec, ConnectionRecord):
            cast("dict[str, ConnectionRecord]", store)[artifact_id] = rec
            return
        cast("dict[str, DiagramRecord]", store)[artifact_id] = rec

    def get_entity(self, artifact_id: str) -> EntityRecord | None:
        self._ensure_loaded()
        return self._entities.get(artifact_id)

    def get_connection(self, artifact_id: str) -> ConnectionRecord | None:
        self._ensure_loaded()
        return self._connections.get(artifact_id)

    def get_diagram(self, artifact_id: str) -> DiagramRecord | None:
        self._ensure_loaded()
        return self._diagrams.get(artifact_id)

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
        self._ensure_loaded()
        results = [
            rec
            for rec in self._entities.values()
            if _matches_entity(
                rec,
                artifact_type=artifact_type,
                layer=layer,
                sublayer=sublayer,
                owner_agent=owner_agent,
                phase_produced=phase_produced,
                status=status,
                safety_relevant=safety_relevant,
                engagement=engagement,
            )
        ]
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
        self._ensure_loaded()
        results = [
            rec
            for rec in self._connections.values()
            if _matches_connection(
                rec,
                artifact_type=artifact_type,
                conn_lang=conn_lang,
                conn_type=conn_type,
                source=source,
                target=target,
                owner_agent=owner_agent,
                phase_produced=phase_produced,
                engagement=engagement,
            )
        ]
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
        self._ensure_loaded()
        results = [
            rec
            for rec in self._diagrams.values()
            if _matches_diagram(
                rec,
                diagram_type=diagram_type,
                owner_agent=owner_agent,
                phase_produced=phase_produced,
                status=status,
                engagement=engagement,
            )
        ]
        return sorted(results, key=lambda r: r.artifact_id)

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
        self._ensure_loaded()
        types = _to_set(artifact_type)
        layers = _to_set(layer)
        agents = _to_set(owner_agent)
        phases = _to_set(phase_produced)
        statuses = _to_set(status)

        results: list[ArtifactSummary] = []
        results.extend(
            summary_from_entity(rec)
            for rec in self._entities.values()
            if _matches_entity_sets(rec, types, layers, agents, phases, statuses, safety_relevant, engagement)
        )
        if include_connections:
            results.extend(
                summary_from_connection(rec)
                for rec in self._connections.values()
                if _matches_connection_sets(rec, types, agents, phases, statuses, engagement)
            )
        if include_diagrams:
            results.extend(
                summary_from_diagram(rec)
                for rec in self._diagrams.values()
                if _matches_diagram_sets(rec, types, agents, phases, statuses, engagement)
            )
        return sorted(results, key=lambda s: s.artifact_id)

    def read_artifact(
        self,
        artifact_id: str,
        *,
        mode: Literal["summary", "full"] = "summary",
    ) -> dict[str, object] | None:
        self._ensure_loaded()
        entity = self._entities.get(artifact_id)
        if entity is not None:
            return _read_entity(entity, mode=mode)
        connection = self._connections.get(artifact_id)
        if connection is not None:
            return _read_connection(connection, mode=mode)
        diagram = self._diagrams.get(artifact_id)
        if diagram is not None:
            return _read_diagram(diagram, mode=mode)
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

    def stats(self) -> dict[str, object]:
        self._ensure_loaded()
        entities = list(self._entities.values())
        connections = list(self._connections.values())
        diagrams = list(self._diagrams.values())

        entities_by_layer: dict[str, int] = {}
        for entity in entities:
            entities_by_layer[entity.layer] = entities_by_layer.get(entity.layer, 0) + 1

        connections_by_lang: dict[str, int] = {}
        for connection in connections:
            connections_by_lang[connection.conn_lang] = connections_by_lang.get(connection.conn_lang, 0) + 1

        return {
            "entities": len(entities),
            "connections": len(connections),
            "diagrams": len(diagrams),
            "entities_by_layer": entities_by_layer,
            "connections_by_lang": connections_by_lang,
        }

    def find_connections_for(
        self,
        entity_id: str,
        *,
        direction: Literal["any", "outbound", "inbound"] = "any",
        conn_lang: str | None = None,
        conn_type: str | None = None,
    ) -> list[ConnectionRecord]:
        self._ensure_loaded()
        results: list[ConnectionRecord] = []
        for rec in self._connections.values():
            if conn_lang is not None and rec.conn_lang != conn_lang:
                continue
            if conn_type is not None and rec.conn_type != conn_type:
                continue
            if not _matches_direction(rec, entity_id=entity_id, direction=direction):
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
        self._ensure_loaded()
        visited: set[str] = {entity_id}
        frontier: set[str] = {entity_id}
        result: dict[str, set[str]] = {}

        for hop in range(1, max_hops + 1):
            next_frontier = _next_frontier(frontier, visited, self, conn_lang)
            if not next_frontier:
                break
            result[str(hop)] = next_frontier
            visited |= next_frontier
            frontier = next_frontier
        return result

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
        self._ensure_loaded()
        query_lc = query.lower()
        tokens = tokenize(query_lc)
        hits: list[SearchHit] = []

        entity_type_set = set(entity_types) if entity_types else set()
        layer_set = set(layers) if layers else set()

        hits.extend(self._search_entities(query_lc, tokens, entity_type_set, layer_set, engagement))
        if include_connections:
            hits.extend(self._search_connections(query_lc, tokens, engagement))
        if include_diagrams:
            hits.extend(self._search_diagrams(query_lc, tokens, engagement))
        self._apply_semantic_supplement(query, hits)

        hits.sort(key=lambda h: h.score, reverse=True)
        return SearchResult(query=query, hits=hits[:limit])

    def _search_entities(
        self,
        query_lc: str,
        tokens: list[str],
        entity_type_set: set[str],
        layer_set: set[str],
        engagement: str | None,
    ) -> list[SearchHit]:
        hits: list[SearchHit] = []
        for rec in self._entities.values():
            if entity_type_set and rec.artifact_type not in entity_type_set:
                continue
            if layer_set and rec.layer not in layer_set:
                continue
            if engagement is not None and rec.engagement != engagement:
                continue
            score = score_entity(rec, query_lc, tokens)
            if score > 0:
                hits.append(SearchHit(score=score, record_type="entity", record=rec))
        return hits

    def _search_connections(self, query_lc: str, tokens: list[str], engagement: str | None) -> list[SearchHit]:
        hits: list[SearchHit] = []
        for rec in self._connections.values():
            if engagement is not None and rec.engagement != engagement:
                continue
            score = score_connection(rec, query_lc, tokens)
            if score > 0:
                hits.append(SearchHit(score=score, record_type="connection", record=rec))
        return hits

    def _search_diagrams(self, query_lc: str, tokens: list[str], engagement: str | None) -> list[SearchHit]:
        hits: list[SearchHit] = []
        for rec in self._diagrams.values():
            if engagement is not None and rec.engagement != engagement:
                continue
            score = score_diagram(rec, query_lc, tokens)
            if score > 0:
                hits.append(SearchHit(score=score, record_type="diagram", record=rec))
        return hits

    def _apply_semantic_supplement(self, query: str, hits: list[SearchHit]) -> None:
        if self._semantic is None:
            return
        if not isinstance(self._semantic, SemanticSearchProvider):
            return
        if len(self._entities) < 50:
            return

        seen_ids = {
            hit.record.artifact_id
            for hit in hits
            if hasattr(hit.record, "artifact_id")
        }
        for sem_score, artifact_id in self._semantic.top_k(query, k=1, threshold=0.75):
            if artifact_id in seen_ids:
                continue
            rec = self._entities.get(artifact_id)
            if rec is not None:
                hits.append(SearchHit(score=sem_score * 3.0, record_type="entity", record=rec))


def _matches_entity(
    rec: EntityRecord,
    *,
    artifact_type: str | None,
    layer: str | None,
    sublayer: str | None,
    owner_agent: str | None,
    phase_produced: str | None,
    status: str | None,
    safety_relevant: bool | None,
    engagement: str | None,
) -> bool:
    return (
        (artifact_type is None or rec.artifact_type == artifact_type)
        and (layer is None or rec.layer == layer)
        and (sublayer is None or rec.sublayer == sublayer)
        and (owner_agent is None or rec.owner_agent == owner_agent)
        and (phase_produced is None or rec.phase_produced == phase_produced)
        and (status is None or rec.status == status)
        and (safety_relevant is None or rec.safety_relevant == safety_relevant)
        and (engagement is None or rec.engagement == engagement)
    )


def _matches_connection(
    rec: ConnectionRecord,
    *,
    artifact_type: str | None,
    conn_lang: str | None,
    conn_type: str | None,
    source: str | None,
    target: str | None,
    owner_agent: str | None,
    phase_produced: str | None,
    engagement: str | None,
) -> bool:
    return (
        (artifact_type is None or rec.artifact_type == artifact_type)
        and (conn_lang is None or rec.conn_lang == conn_lang)
        and (conn_type is None or rec.conn_type == conn_type)
        and (source is None or source in rec.source_ids)
        and (target is None or target in rec.target_ids)
        and (owner_agent is None or rec.owner_agent == owner_agent)
        and (phase_produced is None or rec.phase_produced == phase_produced)
        and (engagement is None or rec.engagement == engagement)
    )


def _matches_diagram(
    rec: DiagramRecord,
    *,
    diagram_type: str | None,
    owner_agent: str | None,
    phase_produced: str | None,
    status: str | None,
    engagement: str | None,
) -> bool:
    return (
        (diagram_type is None or rec.diagram_type == diagram_type)
        and (owner_agent is None or rec.owner_agent == owner_agent)
        and (phase_produced is None or rec.phase_produced == phase_produced)
        and (status is None or rec.status == status)
        and (engagement is None or rec.engagement == engagement)
    )


def _matches_entity_sets(
    rec: EntityRecord,
    types: set[str],
    layers: set[str],
    agents: set[str],
    phases: set[str],
    statuses: set[str],
    safety_relevant: bool | None,
    engagement: str | None,
) -> bool:
    return (
        (not types or rec.artifact_type in types)
        and (not layers or rec.layer in layers)
        and (not agents or rec.owner_agent in agents)
        and (not phases or rec.phase_produced in phases)
        and (not statuses or rec.status in statuses)
        and (safety_relevant is None or rec.safety_relevant == safety_relevant)
        and (engagement is None or rec.engagement == engagement)
    )


def _matches_connection_sets(
    rec: ConnectionRecord,
    types: set[str],
    agents: set[str],
    phases: set[str],
    statuses: set[str],
    engagement: str | None,
) -> bool:
    return (
        (not types or rec.artifact_type in types)
        and (not agents or rec.owner_agent in agents)
        and (not phases or rec.phase_produced in phases)
        and (not statuses or rec.status in statuses)
        and (engagement is None or rec.engagement == engagement)
    )


def _matches_diagram_sets(
    rec: DiagramRecord,
    types: set[str],
    agents: set[str],
    phases: set[str],
    statuses: set[str],
    engagement: str | None,
) -> bool:
    return (
        (not types or rec.artifact_type in types)
        and (not agents or rec.owner_agent in agents)
        and (not phases or rec.phase_produced in phases)
        and (not statuses or rec.status in statuses)
        and (engagement is None or rec.engagement == engagement)
    )


def _next_frontier(
    frontier: set[str],
    visited: set[str],
    registry: ModelRepository,
    conn_lang: str | None,
) -> set[str]:
    next_frontier: set[str] = set()
    for entity_id in frontier:
        for conn in registry.find_connections_for(entity_id, conn_lang=conn_lang):
            for neighbor_id in conn.source_ids + conn.target_ids:
                if neighbor_id != entity_id and neighbor_id not in visited:
                    next_frontier.add(neighbor_id)
    return next_frontier


def _matches_direction(
    rec: ConnectionRecord,
    *,
    entity_id: str,
    direction: Literal["any", "outbound", "inbound"],
) -> bool:
    in_src = entity_id in rec.source_ids
    in_tgt = entity_id in rec.target_ids
    if direction == "outbound":
        return in_src
    if direction == "inbound":
        return in_tgt
    return in_src or in_tgt


def _to_set(value: str | list[str] | None) -> set[str]:
    if value is None:
        return set()
    return {value} if isinstance(value, str) else set(value)


def _read_entity(rec: EntityRecord, *, mode: Literal["summary", "full"]) -> dict[str, object]:
    data: dict[str, object] = {
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
        data["content_text"] = rec.content_text
        data["display_blocks"] = rec.display_blocks
        data["extra"] = rec.extra
    return data


def _read_connection(rec: ConnectionRecord, *, mode: Literal["summary", "full"]) -> dict[str, object]:
    data: dict[str, object] = {
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
        data["content_text"] = rec.content_text
        data["extra"] = rec.extra
    return data


def _read_diagram(rec: DiagramRecord, *, mode: Literal["summary", "full"]) -> dict[str, object]:
    data: dict[str, object] = {
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
            data["puml_source"] = rec.path.read_text(encoding="utf-8")
        except OSError:
            data["puml_source"] = ""
        data["extra"] = rec.extra
    return data



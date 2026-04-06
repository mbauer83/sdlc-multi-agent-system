from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

Layer = Literal[
    "motivation",
    "strategy",
    "business",
    "application",
    "technology",
    "implementation",
    "unknown",
]

MountScope = Literal["engagement", "enterprise"]


@dataclass(frozen=True)
class RepoMount:
    root: Path
    scope: MountScope
    engagement_label: str


class DuplicateArtifactIdError(ValueError):
    pass


def infer_engagement_label(root: Path, *, scope: MountScope) -> str:
    if scope == "enterprise":
        return "enterprise"
    parts = root.resolve().parts
    if "engagements" in parts:
        idx = parts.index("engagements")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def infer_mount(root: Path) -> RepoMount:
    resolved = root.resolve()
    scope: MountScope = "enterprise" if resolved.name == "enterprise-repository" else "engagement"
    return RepoMount(root=resolved, scope=scope, engagement_label=infer_engagement_label(resolved, scope=scope))


@dataclass(frozen=True)
class EntityRecord:
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
    sublayer: str
    path: Path
    extra: dict[str, object]
    content_text: str
    display_blocks: dict[str, str]
    display_label: str
    display_alias: str

    def __str__(self) -> str:
        return (
            f"[{self.artifact_id}] {self.name}  "
            f"({self.artifact_type} · {self.layer}/{self.sublayer} · "
            f"agent={self.owner_agent} · phase={self.phase_produced} · "
            f"status={self.status})"
        )


@dataclass(frozen=True)
class ConnectionRecord:
    artifact_id: str
    artifact_type: str
    source: str | list[str]
    target: str | list[str]
    version: str
    status: str
    phase_produced: str
    owner_agent: str
    engagement: str
    conn_lang: str
    conn_type: str
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
        for hit in self.hits:
            lines.append(str(hit))
        return "\n".join(lines)


@dataclass(frozen=True)
class ArtifactSummary:
    artifact_id: str
    artifact_type: str
    name: str
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


def summary_from_entity(rec: EntityRecord) -> ArtifactSummary:
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


def summary_from_connection(rec: ConnectionRecord) -> ArtifactSummary:
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


def summary_from_diagram(rec: DiagramRecord) -> ArtifactSummary:
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


@runtime_checkable
class SemanticSearchProvider(Protocol):
    def top_k(self, query: str, k: int, *, threshold: float = 0.75) -> list[tuple[float, str]]:
        ...


STANDARD_ENTITY_FIELDS = frozenset(
    {
        "artifact-id",
        "artifact-type",
        "name",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "safety-relevant",
        "last-updated",
        "engagement",
        "produced-by-skill",
    }
)

STANDARD_CONNECTION_FIELDS = frozenset(
    {
        "artifact-id",
        "artifact-type",
        "source",
        "target",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "last-updated",
        "engagement",
        "produced-by-skill",
    }
)

STANDARD_DIAGRAM_FIELDS = frozenset(
    {
        "artifact-id",
        "artifact-type",
        "name",
        "diagram-type",
        "version",
        "status",
        "phase-produced",
        "owner-agent",
        "engagement",
        "entity-ids-used",
        "connection-ids-used",
        "produced-by-skill",
    }
)

LAYER_NAMES: frozenset[str] = frozenset(
    {"motivation", "strategy", "business", "application", "technology", "implementation"}
)

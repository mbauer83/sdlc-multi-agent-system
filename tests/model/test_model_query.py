"""
BDD step definitions for model_query.feature.

Sets up a minimal fixture repository in a tmp_path so tests are fully
self-contained and do not depend on ENG-001 content.  The fixture contains:

  Entities (4):
    APP-001  application-component  layer=application  sublayer=components  agent=SwA  phase=C  status=draft  safety-relevant=false
    AIF-001  application-interface  layer=application  sublayer=interfaces  agent=SwA  phase=C  status=draft
    BPR-001  business-process       layer=business     sublayer=processes   agent=SA   phase=B  status=draft
    BSV-001  business-service       layer=business     sublayer=services    agent=SA   phase=B  status=baselined  safety-relevant=true

  Connections (3):
    archimate/realization/APP-001---BSV-001  (APP-001 → BSV-001)
    archimate/serving/APP-001---AIF-001     (APP-001 → AIF-001)
    er/one-to-many/AIF-001---DOB-999        (AIF-001 → DOB-999; target not in registry)

  Diagrams (1):
    diagram-catalog/diagrams/phase-b-archimate-business-v1.puml
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.common.model_query import (
    ArtifactSummary,
    ConnectionRecord,
    DiagramRecord,
    EntityRecord,
    ModelRepository,
    SearchResult,
)

scenarios("features/model_query.feature")


# ---------------------------------------------------------------------------
# Fixture templates
# ---------------------------------------------------------------------------

_ENTITY_TMPL = textwrap.dedent("""\
    ---
    artifact-id: {artifact_id}
    artifact-type: {artifact_type}
    name: "{name}"
    version: 0.1.0
    status: {status}
    phase-produced: {phase}
    owner-agent: {agent}
    safety-relevant: {safety}
    produced-by-skill: TEST
    last-updated: 2026-04-04
    engagement: ENG-TEST
    ---

    <!-- §content -->

    ## {name}

    {description}

    <!-- §display -->

    ### archimate

    ```yaml
    layer: Application
    element-type: {element_type}
    label: "{name}"
    alias: {alias}
    ```
""")

_CONNECTION_TMPL = textwrap.dedent("""\
    ---
    artifact-id: {artifact_id}
    artifact-type: {artifact_type}
    source: {source}
    target: {target}
    version: 0.1.0
    status: draft
    phase-produced: C
    owner-agent: SwA
    last-updated: 2026-04-04
    engagement: ENG-TEST
    ---

    <!-- §content -->

    {description}

    <!-- §display -->

    ### archimate

    ```yaml
    connection: {artifact_type}
    ```
""")

_DIAGRAM_TMPL = textwrap.dedent("""\
    ' ---
    ' artifact-id: phase-b-archimate-business-v1
    ' artifact-type: diagram
    ' name: "Business Architecture Overview"
    ' diagram-type: archimate-business
    ' version: 0.1.0
    ' status: draft
    ' phase-produced: B
    ' owner-agent: SA
    ' engagement: ENG-TEST
    ' entity-ids-used:
    '   - BPR-001
    '   - BSV-001
    ' connection-ids-used:
    '   - APP-001---BSV-001
    ' ---
    @startuml
    !include ../_macros.puml
    !include ../_archimate-stereotypes.puml

    BPR_001()
    BSV_001()
    @enduml
""")


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _build_fixture_repo(root: Path) -> ModelRepository:
    """Create a minimal fixture repository and return a ModelRepository for it."""
    ent = root / "model-entities"

    _write(
        ent / "application" / "components" / "APP-001.event-store.md",
        _ENTITY_TMPL.format(
            artifact_id="APP-001",
            artifact_type="application-component",
            name="EventStore",
            status="draft",
            phase="C",
            agent="SwA",
            safety="false",
            description="The canonical append-only event log.",
            element_type="ApplicationComponent",
            alias="APP_001",
        ),
    )
    _write(
        ent / "application" / "interfaces" / "AIF-001.event-store-port.md",
        _ENTITY_TMPL.format(
            artifact_id="AIF-001",
            artifact_type="application-interface",
            name="EventStorePort",
            status="draft",
            phase="C",
            agent="SwA",
            safety="false",
            description="Port interface for the EventStore.",
            element_type="ApplicationInterface",
            alias="AIF_001",
        ),
    )
    _write(
        ent / "business" / "processes" / "BPR-001.sprint-planning.md",
        _ENTITY_TMPL.format(
            artifact_id="BPR-001",
            artifact_type="business-process",
            name="Sprint Planning",
            status="draft",
            phase="B",
            agent="SA",
            safety="false",
            description="The PM agent plans the sprint by assigning specialist agents.",
            element_type="BusinessProcess",
            alias="BPR_001",
        ),
    )
    _write(
        ent / "business" / "services" / "BSV-001.business-architecture-service.md",
        _ENTITY_TMPL.format(
            artifact_id="BSV-001",
            artifact_type="business-service",
            name="Business Architecture Service",
            status="baselined",
            phase="B",
            agent="SA",
            safety="true",
            description="Service that delivers business architecture artifacts.",
            element_type="BusinessService",
            alias="BSV_001",
        ),
    )

    conn = root / "connections"
    _write(
        conn / "archimate" / "realization" / "APP-001---BSV-001.md",
        _CONNECTION_TMPL.format(
            artifact_id="APP-001---BSV-001",
            artifact_type="archimate-realization",
            source="APP-001",
            target="BSV-001",
            description="EventStore realizes Business Architecture Service.",
        ),
    )
    _write(
        conn / "archimate" / "serving" / "APP-001---AIF-001.md",
        _CONNECTION_TMPL.format(
            artifact_id="APP-001---AIF-001",
            artifact_type="archimate-serving",
            source="APP-001",
            target="AIF-001",
            description="EventStore serves EventStorePort.",
        ),
    )
    _write(
        conn / "er" / "one-to-many" / "AIF-001---DOB-999.md",
        _CONNECTION_TMPL.format(
            artifact_id="AIF-001---DOB-999",
            artifact_type="er-one-to-many",
            source="AIF-001",
            target="DOB-999",
            description="Port has many data objects.",
        ),
    )

    diag = root / "diagram-catalog" / "diagrams"
    _write(diag / "phase-b-archimate-business-v1.puml", _DIAGRAM_TMPL)

    return ModelRepository(root)


# ---------------------------------------------------------------------------
# Shared state container
# ---------------------------------------------------------------------------


class _Ctx:
    """Mutable bag of per-scenario state."""
    repo: ModelRepository
    entity_results: list[EntityRecord] = []
    connection_results: list[ConnectionRecord] = []
    diagram_results: list[DiagramRecord] = []
    artifact: Any = None
    artifact_dict: dict[str, Any] | None = None
    search_result: SearchResult | None = None
    summaries: list[ArtifactSummary] = []
    stats: dict[str, Any] = {}
    neighbors: dict[str, set[str]] = {}


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------


@given("a populated model repository with test fixtures", target_fixture="ctx")
def populated_repo(tmp_path: Path) -> _Ctx:
    ctx = _Ctx()
    ctx.repo = _build_fixture_repo(tmp_path)
    return ctx


# ---------------------------------------------------------------------------
# When — entity listing
# ---------------------------------------------------------------------------


@when("I list all entities")
def list_all_entities(ctx: _Ctx) -> None:
    ctx.entity_results = ctx.repo.list_entities()


@when(parsers.parse('I list entities in the "{layer}" layer'))
def list_entities_by_layer(ctx: _Ctx, layer: str) -> None:
    ctx.entity_results = ctx.repo.list_entities(layer=layer)


@when(parsers.parse('I list entities with type "{atype}"'))
def list_entities_by_type(ctx: _Ctx, atype: str) -> None:
    ctx.entity_results = ctx.repo.list_entities(artifact_type=atype)


@when(parsers.parse('I list entities owned by "{agent}"'))
def list_entities_by_agent(ctx: _Ctx, agent: str) -> None:
    ctx.entity_results = ctx.repo.list_entities(owner_agent=agent)


@when(parsers.parse('I list entities produced in phase "{phase}"'))
def list_entities_by_phase(ctx: _Ctx, phase: str) -> None:
    ctx.entity_results = ctx.repo.list_entities(phase_produced=phase)


@when(parsers.parse('I list entities with status "{status}"'))
def list_entities_by_status(ctx: _Ctx, status: str) -> None:
    ctx.entity_results = ctx.repo.list_entities(status=status)


@when("I list entities that are safety relevant")
def list_entities_safety_relevant(ctx: _Ctx) -> None:
    ctx.entity_results = ctx.repo.list_entities(safety_relevant=True)


@when(parsers.parse('I list entities in the "{layer}" layer owned by "{agent}"'))
def list_entities_layer_agent(ctx: _Ctx, layer: str, agent: str) -> None:
    ctx.entity_results = ctx.repo.list_entities(layer=layer, owner_agent=agent)


# ---------------------------------------------------------------------------
# When — connection listing
# ---------------------------------------------------------------------------


@when("I list all connections")
def list_all_connections(ctx: _Ctx) -> None:
    ctx.connection_results = ctx.repo.list_connections()


@when(parsers.parse('I list connections with language "{lang}"'))
def list_connections_by_lang(ctx: _Ctx, lang: str) -> None:
    ctx.connection_results = ctx.repo.list_connections(conn_lang=lang)


@when(parsers.parse('I list connections from source "{source}"'))
def list_connections_by_source(ctx: _Ctx, source: str) -> None:
    ctx.connection_results = ctx.repo.list_connections(source=source)


@when(parsers.parse('I list connections targeting "{target}"'))
def list_connections_by_target(ctx: _Ctx, target: str) -> None:
    ctx.connection_results = ctx.repo.list_connections(target=target)


# ---------------------------------------------------------------------------
# When — diagram listing
# ---------------------------------------------------------------------------


@when("I list all diagrams")
def list_all_diagrams(ctx: _Ctx) -> None:
    ctx.diagram_results = ctx.repo.list_diagrams()


@when(parsers.parse('I list diagrams of type "{dtype}"'))
def list_diagrams_by_type(ctx: _Ctx, dtype: str) -> None:
    ctx.diagram_results = ctx.repo.list_diagrams(diagram_type=dtype)


# ---------------------------------------------------------------------------
# When — direct lookup
# ---------------------------------------------------------------------------


@when(parsers.parse('I get artifact "{artifact_id}"'))
def get_artifact(ctx: _Ctx, artifact_id: str) -> None:
    rec = ctx.repo.get_entity(artifact_id)
    if rec is None:
        rec = ctx.repo.get_connection(artifact_id)
    if rec is None:
        rec = ctx.repo.get_diagram(artifact_id)
    ctx.artifact = rec


# ---------------------------------------------------------------------------
# When — graph traversal
# ---------------------------------------------------------------------------


@when(parsers.parse('I find outbound connections for "{entity_id}"'))
def find_outbound_connections(ctx: _Ctx, entity_id: str) -> None:
    ctx.connection_results = ctx.repo.find_connections_for(entity_id, direction="outbound")


@when(parsers.parse('I find inbound connections for "{entity_id}"'))
def find_inbound_connections(ctx: _Ctx, entity_id: str) -> None:
    ctx.connection_results = ctx.repo.find_connections_for(entity_id, direction="inbound")


@when(parsers.parse('I find all connections for "{entity_id}"'))
def find_all_connections(ctx: _Ctx, entity_id: str) -> None:
    ctx.connection_results = ctx.repo.find_connections_for(entity_id, direction="any")


@when(parsers.parse('I find {n:d}-hop neighbors of "{entity_id}"'))
def find_neighbors(ctx: _Ctx, n: int, entity_id: str) -> None:
    ctx.neighbors = ctx.repo.find_neighbors(entity_id, max_hops=n)


# ---------------------------------------------------------------------------
# When — framework-aligned list_artifacts
# ---------------------------------------------------------------------------


@when(parsers.parse('I call list_artifacts with layer "{layer}"'))
def call_list_artifacts_layer(ctx: _Ctx, layer: str) -> None:
    ctx.summaries = ctx.repo.list_artifacts(layer=layer)


@when(parsers.parse('I call list_artifacts with layers "{l1}" and "{l2}"'))
def call_list_artifacts_multilayer(ctx: _Ctx, l1: str, l2: str) -> None:
    ctx.summaries = ctx.repo.list_artifacts(layer=[l1, l2])


@when("I call list_artifacts with no filters")
def call_list_artifacts_no_filters(ctx: _Ctx) -> None:
    ctx.summaries = ctx.repo.list_artifacts()


@when("I call list_artifacts with include_connections true")
def call_list_artifacts_with_connections(ctx: _Ctx) -> None:
    ctx.summaries = ctx.repo.list_artifacts(include_connections=True)


# ---------------------------------------------------------------------------
# When — read_artifact
# ---------------------------------------------------------------------------


@when(parsers.parse('I read artifact "{artifact_id}" in summary mode'))
def read_artifact_summary(ctx: _Ctx, artifact_id: str) -> None:
    ctx.artifact_dict = ctx.repo.read_artifact(artifact_id, mode="summary")


@when(parsers.parse('I read artifact "{artifact_id}" in full mode'))
def read_artifact_full(ctx: _Ctx, artifact_id: str) -> None:
    ctx.artifact_dict = ctx.repo.read_artifact(artifact_id, mode="full")


# ---------------------------------------------------------------------------
# When — search
# ---------------------------------------------------------------------------


@when(parsers.parse('I search for "{query}"'))
def search_query(ctx: _Ctx, query: str) -> None:
    # Unescape hyphen-joined multi-word queries from feature file
    ctx.search_result = ctx.repo.search(query.replace("-", " "))


@when(parsers.parse('I search for "{query}" with limit {limit:d}'))
def search_query_limited(ctx: _Ctx, query: str, limit: int) -> None:
    ctx.search_result = ctx.repo.search(query, limit=limit)


@when(parsers.parse('I call search_artifacts for "{query}"'))
def search_artifacts_call(ctx: _Ctx, query: str) -> None:
    ctx.search_result = ctx.repo.search_artifacts(query)


# ---------------------------------------------------------------------------
# When — stats
# ---------------------------------------------------------------------------


@when("I get repository stats")
def get_stats(ctx: _Ctx) -> None:
    ctx.stats = ctx.repo.stats()


# ---------------------------------------------------------------------------
# Then — entity result counts
# ---------------------------------------------------------------------------


@then(parsers.parse("I get {n:d} entity results"))
def check_entity_count(ctx: _Ctx, n: int) -> None:
    assert len(ctx.entity_results) == n, (
        f"expected {n} entity results, got {len(ctx.entity_results)}: "
        f"{[r.artifact_id for r in ctx.entity_results]}"
    )


@then("I get 1 entity result")
def check_entity_count_one(ctx: _Ctx) -> None:
    assert len(ctx.entity_results) == 1


# ---------------------------------------------------------------------------
# Then — connection result counts
# ---------------------------------------------------------------------------


@then(parsers.parse("I get {n:d} connection results"))
def check_connection_count(ctx: _Ctx, n: int) -> None:
    assert len(ctx.connection_results) == n, (
        f"expected {n} connection results, got {len(ctx.connection_results)}: "
        f"{[r.artifact_id for r in ctx.connection_results]}"
    )


@then("I get 1 connection result")
def check_connection_count_one(ctx: _Ctx) -> None:
    assert len(ctx.connection_results) == 1


# ---------------------------------------------------------------------------
# Then — diagram result counts
# ---------------------------------------------------------------------------


@then(parsers.parse("I get {n:d} diagram results"))
def check_diagram_count(ctx: _Ctx, n: int) -> None:
    assert len(ctx.diagram_results) == n


@then("I get 1 diagram result")
def check_diagram_count_one(ctx: _Ctx) -> None:
    assert len(ctx.diagram_results) == 1


# ---------------------------------------------------------------------------
# Then — direct lookup
# ---------------------------------------------------------------------------


@then(parsers.parse('the artifact name is "{name}"'))
def check_artifact_name(ctx: _Ctx, name: str) -> None:
    assert ctx.artifact is not None
    assert ctx.artifact.name == name


@then(parsers.parse('the artifact type is "{atype}"'))
def check_artifact_type(ctx: _Ctx, atype: str) -> None:
    assert ctx.artifact is not None
    assert ctx.artifact.artifact_type == atype


@then(parsers.parse('the artifact layer is "{layer}"'))
def check_artifact_layer(ctx: _Ctx, layer: str) -> None:
    assert isinstance(ctx.artifact, EntityRecord)
    assert ctx.artifact.layer == layer


@then("the content text is non-empty")
def check_content_non_empty(ctx: _Ctx) -> None:
    assert isinstance(ctx.artifact, EntityRecord)
    assert ctx.artifact.content_text.strip() != ""


@then("no artifact is found")
def check_no_artifact(ctx: _Ctx) -> None:
    assert ctx.artifact is None


# ---------------------------------------------------------------------------
# Then — graph traversal
# ---------------------------------------------------------------------------


@then(parsers.parse('hop "{hop}" contains "{entity_id}"'))
def check_hop_contains(ctx: _Ctx, hop: str, entity_id: str) -> None:
    assert hop in ctx.neighbors, f"hop {hop!r} not in neighbors: {ctx.neighbors}"
    assert entity_id in ctx.neighbors[hop], (
        f"{entity_id!r} not in hop {hop}: {ctx.neighbors[hop]}"
    )


@then("the neighbor map is empty")
def check_neighbor_map_empty(ctx: _Ctx) -> None:
    assert ctx.neighbors == {}


# ---------------------------------------------------------------------------
# Then — list_artifacts summaries
# ---------------------------------------------------------------------------


@then(parsers.parse("I get {n:d} artifact summaries"))
def check_summary_count(ctx: _Ctx, n: int) -> None:
    assert len(ctx.summaries) == n, (
        f"expected {n} summaries, got {len(ctx.summaries)}: "
        f"{[s.artifact_id for s in ctx.summaries]}"
    )


@then("each summary has an artifact_id")
def check_summaries_have_ids(ctx: _Ctx) -> None:
    for s in ctx.summaries:
        assert s.artifact_id, f"summary missing artifact_id: {s}"


@then("connections are not included in results")
def check_no_connections_in_summaries(ctx: _Ctx) -> None:
    conn_records = [s for s in ctx.summaries if s.record_type == "connection"]
    assert conn_records == [], f"unexpected connections: {[s.artifact_id for s in conn_records]}"


@then("connections are included in results")
def check_connections_in_summaries(ctx: _Ctx) -> None:
    conn_records = [s for s in ctx.summaries if s.record_type == "connection"]
    assert len(conn_records) > 0, "expected connection records in summaries"


# ---------------------------------------------------------------------------
# Then — read_artifact
# ---------------------------------------------------------------------------


@then(parsers.parse('the result contains field "{field}" with value "{value}"'))
def check_result_field_value(ctx: _Ctx, field: str, value: str) -> None:
    assert ctx.artifact_dict is not None
    assert field in ctx.artifact_dict, f"field {field!r} missing from result"
    assert str(ctx.artifact_dict[field]) == value, (
        f"field {field!r}: expected {value!r}, got {ctx.artifact_dict[field]!r}"
    )


@then(parsers.parse('the result contains field "{field}"'))
def check_result_has_field(ctx: _Ctx, field: str) -> None:
    assert ctx.artifact_dict is not None
    assert field in ctx.artifact_dict, f"field {field!r} missing from result: {list(ctx.artifact_dict.keys())}"


@then(parsers.parse('the result does not contain field "{field}"'))
def check_result_lacks_field(ctx: _Ctx, field: str) -> None:
    assert ctx.artifact_dict is not None
    assert field not in ctx.artifact_dict, f"field {field!r} unexpectedly present"


@then("read_artifact returns None")
def check_read_artifact_none(ctx: _Ctx) -> None:
    assert ctx.artifact_dict is None


# ---------------------------------------------------------------------------
# Then — search
# ---------------------------------------------------------------------------


@then(parsers.parse('"{artifact_id}" appears in the search results'))
def check_in_results(ctx: _Ctx, artifact_id: str) -> None:
    assert ctx.search_result is not None
    ids = [h.record.artifact_id for h in ctx.search_result.hits]
    assert artifact_id in ids, f"{artifact_id!r} not found in hits: {ids}"


@then(parsers.parse('"{artifact_id}" is the top result'))
def check_top_result(ctx: _Ctx, artifact_id: str) -> None:
    assert ctx.search_result is not None
    assert ctx.search_result.hits, "search returned no hits"
    top = ctx.search_result.hits[0].record.artifact_id
    assert top == artifact_id, f"expected top={artifact_id!r}, got {top!r}"


@then(parsers.parse("the search result has {n:d} hits"))
def check_search_hit_count(ctx: _Ctx, n: int) -> None:
    assert ctx.search_result is not None
    assert len(ctx.search_result.hits) == n, (
        f"expected {n} hits, got {len(ctx.search_result.hits)}"
    )


@then("the search result has 0 hits")
def check_search_no_hits(ctx: _Ctx) -> None:
    assert ctx.search_result is not None
    assert ctx.search_result.hits == []


# ---------------------------------------------------------------------------
# Then — stats
# ---------------------------------------------------------------------------


@then(parsers.parse("stats entities count is {n:d}"))
def check_stats_entities(ctx: _Ctx, n: int) -> None:
    assert ctx.stats["entities"] == n


@then(parsers.parse("stats connections count is {n:d}"))
def check_stats_connections(ctx: _Ctx, n: int) -> None:
    assert ctx.stats["connections"] == n


@then(parsers.parse('stats layer "{layer}" count is {n:d}'))
def check_stats_layer_count(ctx: _Ctx, layer: str, n: int) -> None:
    layers = ctx.stats.get("entities_by_layer", {})
    assert layers.get(layer, 0) == n, (
        f"expected {n} entities in layer {layer!r}, got {layers.get(layer, 0)}"
    )

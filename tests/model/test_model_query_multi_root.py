"""BDD step definitions for model_query_multi_root.feature."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.common.model_query import DuplicateArtifactIdError, ModelRepository

scenarios("features/model_query_multi_root.feature")


_ENTITY_TMPL = textwrap.dedent("""\
    ---
    artifact-id: {artifact_id}
    artifact-type: principle
    name: "{name}"
    version: 1.0.0
    status: baselined
    phase-produced: A
    owner-agent: SA
    safety-relevant: false
    last-updated: 2026-04-04
    {engagement_line}
    ---

    <!-- §content -->

    ## {name}

    {description}

    <!-- §display -->

    ### archimate

    ```yaml
    layer: Motivation
    element-type: Principle
    label: "{name}"
    alias: {alias}
    ```
""")


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class _Ctx:
    repo: ModelRepository | None = None
    summaries: list[dict] = []
    search: dict | None = None
    err: Exception | None = None


def _build_engagement_root(tmp_path: Path) -> Path:
    root = tmp_path / "engagement-architecture-repository"
    ent = root / "model-entities" / "motivation" / "principles"
    _write(
        ent / "PRI-001.local-principle.md",
        _ENTITY_TMPL.format(
            artifact_id="PRI-001",
            name="Local Principle",
            description="Engagement-local principle.",
            alias="PRI_001",
            engagement_line="engagement: ENG-TEST",
        ),
    )
    return root


def _build_enterprise_root(tmp_path: Path) -> Path:
    root = tmp_path / "enterprise-repository"
    ent = root / "model-entities" / "motivation" / "principles"
    # Enterprise files commonly omit engagement after promotion.
    _write(
        ent / "PRI-900.enterprise-principle.md",
        _ENTITY_TMPL.format(
            artifact_id="PRI-900",
            name="EnterprisePrinciple",
            description="Enterprise-level principle.",
            alias="PRI_900",
            engagement_line="",
        ),
    )
    return root


@given("a unified model repository with engagement and enterprise fixtures", target_fixture="ctx")
def unified_repo(tmp_path: Path) -> _Ctx:
    ctx = _Ctx()
    engagement_root = _build_engagement_root(tmp_path)
    enterprise_root = _build_enterprise_root(tmp_path)
    ctx.repo = ModelRepository([engagement_root, enterprise_root])
    return ctx


@when(parsers.parse('I call list_artifacts with engagement filter "{engagement}"'))
def list_artifacts_engagement(ctx: _Ctx, engagement: str) -> None:
    assert ctx.repo is not None
    summaries = ctx.repo.list_artifacts(engagement=engagement)
    ctx.summaries = [
        {
            "artifact_id": s.artifact_id,
            "engagement": s.engagement,
        }
        for s in summaries
    ]


@then(parsers.parse("I get {n:d} artifact summary"))
def got_n_summaries(ctx: _Ctx, n: int) -> None:
    assert len(ctx.summaries) == n


@then(parsers.parse('the summary engagement is "{engagement}"'))
def summary_engagement(ctx: _Ctx, engagement: str) -> None:
    assert ctx.summaries
    assert all(s["engagement"] == engagement for s in ctx.summaries)


@when(parsers.parse('I call search_artifacts for "{query}" with engagement "{engagement}"'))
def search_scoped(ctx: _Ctx, query: str, engagement: str) -> None:
    assert ctx.repo is not None
    r = ctx.repo.search_artifacts(query, limit=10, engagement=engagement)
    ctx.search = {
        "hits": [getattr(h.record, "artifact_id", "") for h in r.hits],
    }


@then(parsers.parse('"{artifact_id}" appears in the search results'))
def appears(ctx: _Ctx, artifact_id: str) -> None:
    assert ctx.search is not None
    assert artifact_id in ctx.search["hits"]


@given(parsers.parse('two mounted repositories contain entity "{artifact_id}"'), target_fixture="ctx")
def duplicate_ids(tmp_path: Path, artifact_id: str) -> _Ctx:
    ctx = _Ctx()
    engagement_root = _build_engagement_root(tmp_path)
    enterprise_root = _build_enterprise_root(tmp_path)

    ent1 = engagement_root / "model-entities" / "application" / "components"
    ent2 = enterprise_root / "model-entities" / "application" / "components"

    entity = textwrap.dedent(f"""\
        ---
        artifact-id: {artifact_id}
        artifact-type: application-component
        name: "Dup"
        version: 0.1.0
        status: draft
        phase-produced: C
        owner-agent: SwA
        safety-relevant: false
        last-updated: 2026-04-04
        engagement: ENG-TEST
        ---

        <!-- §content -->

        ## Dup

        ## Properties

        | A | B |
        |---|---|

        <!-- §display -->

        ### archimate

        ```yaml
        layer: Application
        element-type: ApplicationComponent
        label: "Dup"
        alias: APP_001
        ```
    """)

    _write(ent1 / f"{artifact_id}.dup.md", entity)
    _write(ent2 / f"{artifact_id}.dup.md", entity.replace("engagement: ENG-TEST", ""))

    # Store roots for build step.
    ctx.summaries = [{"engagement_root": str(engagement_root), "enterprise_root": str(enterprise_root)}]
    return ctx


@when("I build a unified model repository")
def build_unified(ctx: _Ctx) -> None:
    roots = ctx.summaries[0]
    engagement_root = Path(roots["engagement_root"])
    enterprise_root = Path(roots["enterprise_root"])

    try:
        repo = ModelRepository([engagement_root, enterprise_root])
        # Force indexing.
        repo.stats()
    except Exception as exc:  # noqa: BLE001
        ctx.err = exc
    else:
        ctx.err = None


@then("a duplicate artifact-id error is raised")
def dup_error(ctx: _Ctx) -> None:
    assert ctx.err is not None
    assert isinstance(ctx.err, DuplicateArtifactIdError)

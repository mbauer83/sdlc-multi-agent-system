from __future__ import annotations

from pathlib import Path

from src.common.model_query import ModelRepository
from src.tools import mcp_model_server


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_repo(root: Path) -> Path:
    _write(
        root / "model-entities" / "application" / "components" / "APP-001.event-store.md",
        """---
artifact-id: APP-001
artifact-type: application-component
name: "Event Store"
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
safety-relevant: false
engagement: ENG-TEST
---

<!-- §content -->

Stores event streams.

<!-- §display -->

### archimate

```yaml
layer: Application
element-type: ApplicationComponent
label: "Event Store"
alias: APP_001
```
""",
    )
    _write(
        root / "diagram-catalog" / "diagrams" / "dia-001.activity.puml",
        """' ---
' artifact-id: DIA-001
' artifact-type: diagram
' name: "Event Activity Overview"
' diagram-type: activity-bpmn
' version: 0.1.0
' status: draft
' phase-produced: B
' owner-agent: SA
' engagement: ENG-TEST
' entity-ids-used:
'   - APP-001
' ---
@startuml
@enduml
""",
    )
    return root


def test_model_repository_search_priority_and_counts(tmp_path: Path) -> None:
    repo_root = _build_repo(tmp_path / "repo")
    repo = ModelRepository(repo_root)

    strict = repo.search_artifacts(
        "event",
        prefer_record_type="diagram",
        strict_record_type=True,
        include_connections=False,
        include_diagrams=True,
    )
    assert strict.hits
    assert all(hit.record_type == "diagram" for hit in strict.hits)

    preferred = repo.search_artifacts(
        "event",
        prefer_record_type="diagram",
        strict_record_type=False,
        include_connections=False,
        include_diagrams=True,
    )
    assert preferred.hits
    assert preferred.hits[0].record_type == "diagram"

    counts = repo.count_artifacts_by("diagram_type", include_connections=False, include_diagrams=True)
    assert counts["activity-bpmn"] == 1


def test_model_query_mcp_projection_and_aggregate_tool(tmp_path: Path) -> None:
    repo_root = _build_repo(tmp_path / "repo")
    tool_map = mcp_model_server.mcp._tool_manager._tools

    listed = tool_map["model_query_list_artifacts"].fn(
        repo_root=str(repo_root),
        repo_scope="engagement",
        include_connections=False,
        include_diagrams=False,
        fields=["artifact_id", "path"],
    )
    assert listed
    assert set(listed[0].keys()) == {"artifact_id", "path"}

    searched = tool_map["model_query_search_artifacts"].fn(
        "event",
        repo_root=str(repo_root),
        repo_scope="engagement",
        fields=["artifact_id", "record_type", "score"],
        include_connections=False,
        include_diagrams=True,
        prefer_record_type="diagram",
    )
    assert searched["hits"]
    assert set(searched["hits"][0].keys()) <= {"artifact_id", "record_type", "score"}

    grouped = tool_map["model_query_count_artifacts_by"].fn(
        "diagram_type",
        repo_root=str(repo_root),
        repo_scope="engagement",
    )
    assert grouped["counts"]["activity-bpmn"] == 1

from __future__ import annotations

from pathlib import Path

from src.common.model_verifier import ModelRegistry, ModelVerifier
from tests.model.conftest import VALID_CONNECTION, VALID_ENTITY, write_connection, write_entity


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "architecture-repository"
    entity_dir = repo / "model-entities" / "application" / "components"
    conn_dir = repo / "connections" / "archimate" / "serving"

    write_entity(entity_dir / "APP-001.md", VALID_ENTITY)
    write_entity(entity_dir / "APP-016.md", VALID_ENTITY.replace("artifact-id: APP-001", "artifact-id: APP-016"))
    write_connection(conn_dir / "APP-001---APP-016.md", VALID_CONNECTION)
    return repo


def test_incremental_verify_persists_across_restarts_and_detects_manual_changes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = _make_repo(tmp_path)
    state_dir = tmp_path / "verifier-state"

    monkeypatch.setenv("SDLC_MODEL_VERIFY_MODE", "incremental")
    monkeypatch.setenv("SDLC_MODEL_VERIFY_STATE_DIR", str(state_dir))

    verifier_1 = ModelVerifier(ModelRegistry(repo), check_puml_syntax=False)
    first = verifier_1.verify_all(repo, include_diagrams=False)
    assert len(first) == 3
    assert all(r.valid for r in first)

    # Simulate a manual edit between runs.
    entity_path = repo / "model-entities" / "application" / "components" / "APP-001.md"
    entity_path.write_text(
        VALID_ENTITY.replace("status: draft", "status: pending"),
        encoding="utf-8",
    )

    # Simulate restart by building a new verifier instance.
    verifier_2 = ModelVerifier(ModelRegistry(repo), check_puml_syntax=False)
    second = verifier_2.verify_all(repo, include_diagrams=False)
    app_001 = next(r for r in second if r.path.name == "APP-001.md")
    assert not app_001.valid
    assert any(i.code == "E022" for i in app_001.errors)

    state_files = list(state_dir.glob("*.state-v1.json"))
    assert state_files, "incremental mode should persist state for restart-safe runs"

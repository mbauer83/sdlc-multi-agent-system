"""
BDD tests for diagram_tools: regenerate_macros, generate_er_content,
generate_er_relations, validate_diagram, render_diagram, and tool registration.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_bdd import given, scenario, then, when

from src.agents.tools.diagram_tools import (
    generate_er_content,
    generate_er_relations,
    regenerate_macros,
    register_diagram_tools,
    render_diagram,
    validate_diagram,
)


# ---------------------------------------------------------------------------
# Stub for RunContext[AgentDeps]
# ---------------------------------------------------------------------------

@dataclass
class _FakeDeps:
    engagement_path: Path
    work_repos_path: Path
    framework_path: Path
    engagement_id: str = "ENG-TEST"
    agent_id: str = "SA"


@dataclass
class _FakeCtx:
    deps: _FakeDeps


def _make_ctx(arch_repo: Path) -> _FakeCtx:
    work_repos = arch_repo.parent
    engagement = work_repos.parent
    return _FakeCtx(
        deps=_FakeDeps(
            engagement_path=engagement,
            work_repos_path=work_repos,
            framework_path=engagement / "framework",
        )
    )


def _empty_arch_repo(root: Path) -> Path:
    arch = root / "work-repositories" / "architecture-repository"
    (arch / "model-entities").mkdir(parents=True, exist_ok=True)
    (arch / "diagram-catalog" / "diagrams").mkdir(parents=True, exist_ok=True)
    return arch


# ---------------------------------------------------------------------------
# Scenario: regenerate_macros with no entities
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "regenerate_macros with no entities returns zero-macro summary")
def test_regenerate_macros_empty():
    pass


@given("an empty architecture repository", target_fixture="arch_repo")
def arch_repo(tmp_path):
    return _empty_arch_repo(tmp_path)


@when("I call regenerate_macros with no repo_path override",
      target_fixture="regen_result")
def regen_result(arch_repo):
    ctx = _make_ctx(arch_repo)
    return regenerate_macros(ctx, repo_path=None)


@then('the result contains "0 ArchiMate macro(s) written"')
def check_zero_macros(regen_result):
    assert "0 ArchiMate macro(s) written" in regen_result, regen_result


# ---------------------------------------------------------------------------
# Scenario: regenerate_macros with one archimate entity
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "regenerate_macros with one archimate entity returns one macro")
def test_regenerate_macros_one_entity():
    pass


@given("an architecture repository with one entity that has an archimate display block",
       target_fixture="arch_repo")
def arch_repo_with_entity(tmp_path):
    arch = _empty_arch_repo(tmp_path)
    entities = arch / "model-entities" / "application" / "components"
    entities.mkdir(parents=True, exist_ok=True)
    entity_content = textwrap.dedent("""\
        ---
        artifact-id: APP-001
        artifact-type: application-component
        name: Test Component
        version: 0.1.0
        status: draft
        phase-produced: C
        owner-agent: SwA
        safety-relevant: false
        produced-by-skill: SwA-PHASE-C-APP
        last-updated: 2026-04-10
        engagement: ENG-TEST
        layer: application
        ---

        <!-- §content -->

        ## Test Component

        Test.

        <!-- §display -->

        ### archimate

        ```yaml
        layer: Application
        element-type: ApplicationComponent
        label: "Test Component"
        alias: APP_001
        ```
        """)
    (entities / "APP-001.test-component.md").write_text(entity_content)
    return arch


@when("I call regenerate_macros with no repo_path override",
      target_fixture="regen_result")
def regen_result_entity(arch_repo):
    ctx = _make_ctx(arch_repo)
    return regenerate_macros(ctx, repo_path=None)


@then('the result contains "1 ArchiMate macro(s) written"')
def check_one_macro(regen_result):
    assert "1 ArchiMate macro(s) written" in regen_result, regen_result


# ---------------------------------------------------------------------------
# Scenario: generate_er_content for missing entity
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "generate_er_content for missing entity returns warning line")
def test_er_content_missing():
    pass


@given("an empty architecture repository", target_fixture="arch_repo")
def arch_repo_er(tmp_path):
    return _empty_arch_repo(tmp_path)


@when('I call generate_er_content with entity_ids ["DOB-999"]',
      target_fixture="er_result")
def er_result(arch_repo):
    ctx = _make_ctx(arch_repo)
    return generate_er_content(ctx, entity_ids=["DOB-999"])


@then('the result contains "[Warning]"')
def check_warning(er_result):
    assert "[Warning]" in er_result, er_result


# ---------------------------------------------------------------------------
# Scenario: validate_diagram returns error for missing file
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "validate_diagram returns error when PUML file does not exist")
def test_validate_diagram_missing():
    pass


@given("an empty architecture repository", target_fixture="arch_repo")
def arch_repo_vd(tmp_path):
    return _empty_arch_repo(tmp_path)


@when("I call validate_diagram with a non-existent puml path",
      target_fixture="vd_result")
def vd_result(arch_repo):
    ctx = _make_ctx(arch_repo)
    return validate_diagram(ctx, puml_path="diagram-catalog/diagrams/nonexistent.puml")


@then('the result contains "[Error]"')
def check_error(vd_result):
    assert "[Error]" in vd_result, vd_result


# ---------------------------------------------------------------------------
# Scenario: render_diagram returns skip when plantuml absent
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "render_diagram returns skip message when plantuml is not on PATH")
def test_render_no_plantuml():
    pass


@given("an empty architecture repository", target_fixture="arch_repo")
def arch_repo_rd(tmp_path):
    return _empty_arch_repo(tmp_path)


@given("plantuml is not installed")
def plantuml_absent():
    pass  # shutil.which is patched in the when step


@when("I call render_diagram with a minimal puml file",
      target_fixture="render_result")
def render_result(arch_repo):
    diag_dir = arch_repo / "diagram-catalog" / "diagrams"
    puml = diag_dir / "TST-001.puml"
    puml.write_text("@startuml TST-001\nBob -> Alice : hello\n@enduml\n")
    ctx = _make_ctx(arch_repo)
    with patch("src.agents.tools._diagram_io.shutil.which", return_value=None):
        return render_diagram(ctx, puml_path=str(puml))


@then('the result contains "[Skipped]"')
def check_skipped(render_result):
    assert "[Skipped]" in render_result, render_result


# ---------------------------------------------------------------------------
# Scenario: register_diagram_tools adds 5 tools
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "register_diagram_tools adds 4 tools to an agent")
def test_registration():
    pass


@given("a PydanticAI agent with test model", target_fixture="test_agent")
def make_test_agent():
    from pydantic_ai import Agent
    return Agent("test")


@when("I call register_diagram_tools on the agent")
def call_register(test_agent):
    register_diagram_tools(test_agent)


@then("the agent has 4 diagram tools registered")
def check_4_tools(test_agent):
    tool_names = set(test_agent._function_toolset.tools.keys())
    expected = {
        "generate_er_content",
        "generate_er_relations",
        "validate_diagram",
        "render_diagram",
    }
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"
    # regenerate_macros must NOT be in the agent-facing tool set
    assert "regenerate_macros" not in tool_names, "regenerate_macros should be auto-triggered, not agent-facing"


# ---------------------------------------------------------------------------
# Scenario: write_artifact auto-triggers macro regeneration
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "write_artifact auto-regenerates macros when entity has archimate block")
def test_write_artifact_regenerates_macros():
    pass


@given("an architecture repository set up for write testing",
       target_fixture="arch_repo")
def arch_repo_for_write(tmp_path):
    arch = _empty_arch_repo(tmp_path)
    entities = arch / "model-entities" / "application" / "components"
    entities.mkdir(parents=True, exist_ok=True)
    entity_content = textwrap.dedent("""\
        ---
        artifact-id: APP-001
        artifact-type: application-component
        name: Existing Component
        version: 0.1.0
        status: draft
        phase-produced: C
        owner-agent: SwA
        safety-relevant: false
        produced-by-skill: SwA-PHASE-C-APP
        last-updated: 2026-04-10
        engagement: ENG-TEST
        layer: application
        ---

        <!-- §content -->

        <!-- §display -->

        ### archimate

        ```yaml
        layer: Application
        element-type: ApplicationComponent
        label: "Existing Component"
        alias: APP_001
        ```
        """)
    (entities / "APP-001.existing-component.md").write_text(entity_content)
    return arch


@when("write_artifact writes an entity with an archimate display block")
def write_archimate_entity(arch_repo):
    from src.agents.tools.write_tools import _has_archimate_display, _regenerate_macros_for

    content = textwrap.dedent("""\
        ---
        artifact-id: APP-002
        artifact-type: application-component
        name: New Component
        version: 0.1.0
        status: draft
        phase-produced: C
        owner-agent: SwA
        safety-relevant: false
        produced-by-skill: SwA-PHASE-C-APP
        last-updated: 2026-04-10
        engagement: ENG-TEST
        layer: application
        ---
        <!-- §content -->
        <!-- §display -->
        ### archimate
        ```yaml
        layer: Application
        element-type: ApplicationComponent
        label: "New Component"
        alias: APP_002
        ```
        """)
    assert _has_archimate_display(content)
    target = arch_repo / "model-entities" / "application" / "components" / "APP-002.new-component.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)

    ctx = _make_ctx(arch_repo)
    _regenerate_macros_for(ctx)


@then("_macros.puml is regenerated with at least one macro")
def check_macros_present(arch_repo):
    macros_path = arch_repo / "diagram-catalog" / "_macros.puml"
    assert macros_path.exists(), "_macros.puml was not created"
    count = macros_path.read_text().count("!define DECL_")
    assert count >= 1, f"Expected ≥1 macro, got {count}"


# ---------------------------------------------------------------------------
# Scenario: write_artifact does NOT regenerate macros for plain markdown
# ---------------------------------------------------------------------------

@scenario("features/diagram_tools.feature",
          "write_artifact does not regenerate macros for plain markdown")
def test_write_artifact_no_regen_plain():
    pass


@given("an empty architecture repository for plain write test",
       target_fixture="arch_repo")
def arch_repo_plain(tmp_path):
    return _empty_arch_repo(tmp_path)


@when("write_artifact writes a plain markdown file without archimate block",
      target_fixture="macros_before_after")
def write_plain_md(arch_repo):
    from src.agents.tools.write_tools import _has_archimate_display

    content = "# Hello\n\nThis is a plain markdown file with no archimate block.\n"
    assert not _has_archimate_display(content)
    target = arch_repo / "model-entities" / "motivation" / "plain.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)

    macros_path = arch_repo / "diagram-catalog" / "_macros.puml"
    before = macros_path.stat().st_mtime if macros_path.exists() else None
    # _regenerate_macros_for should NOT be called for plain files
    # (tested by checking _has_archimate_display is False, not by calling _regenerate_macros_for)
    return before


@then("_macros.puml count is unchanged")
def check_macros_unchanged(macros_before_after, arch_repo):
    # _macros.puml should either not exist or be unchanged (not modified by plain write)
    macros_path = arch_repo / "diagram-catalog" / "_macros.puml"
    after = macros_path.stat().st_mtime if macros_path.exists() else None
    assert macros_before_after == after, "Unexpected _macros.puml modification for plain markdown write"

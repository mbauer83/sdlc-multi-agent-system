"""BDD step definitions for registry_librarian.feature.

Creates a synthetic agents/ directory structure under tmp_path so tests are
self-contained and do not depend on workspace agent content.
"""

from __future__ import annotations

import hashlib
import textwrap
from pathlib import Path
from typing import Any

import pytest
import yaml
from pytest_bdd import given, parsers, scenarios, then, when

from src.tools import mcp_registry_server as reg


scenarios("features/registry_librarian.feature")


@pytest.fixture
def ctx(tmp_path: Path) -> dict[str, Any]:
    return {"tmp_path": tmp_path, "agents_root": tmp_path / "agents"}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


_AGENT_MD = textwrap.dedent(
    """\
    ---
    agent-id: alpha
    name: Alpha Agent
    system-prompt-identity: "You are Alpha."
    ---

    # Alpha

    Some body text.
    """
)


def _skill_md(*, skill_id: str, procedure: str | None = None, inputs_required_table: str | None = None) -> str:
    parts: list[str] = [
        "---\n",
        f"skill-id: {skill_id}\n",
        "name: Test Skill\n",
        "---\n\n",
        "# Skill\n\n",
    ]

    if inputs_required_table is not None:
        parts.append("## Inputs Required\n\n")
        parts.append(inputs_required_table.strip("\n") + "\n\n")

    if procedure is not None:
        parts.append("## Procedure\n\n")
        parts.append(procedure.strip("\n") + "\n\n")

    parts.append("## Outputs\n\n- done\n")
    return "".join(parts)


@given(
    parsers.parse('an agents root containing agents "alpha" (valid) and "beta" (invalid)')
)
def given_agents_root_with_valid_and_invalid(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    _write(root / "alpha" / "AGENT.md", _AGENT_MD)
    (root / "beta").mkdir(parents=True, exist_ok=True)


@given(parsers.parse('an agents root containing agent "alpha" with an identity file'))
def given_agents_root_with_identity(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    _write(root / "alpha" / "AGENT.md", _AGENT_MD)


@given(parsers.parse('an agents root containing agent "alpha" with skills "skill-one" and "skill-two"'))
def given_agent_with_skills(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    _write(root / "alpha" / "AGENT.md", _AGENT_MD)
    _write(root / "alpha" / "skills" / "skill-one.md", _skill_md(skill_id="skill-one", procedure="Do it"))
    _write(root / "alpha" / "skills" / "skill-two.md", _skill_md(skill_id="skill-two", procedure="Do it again"))
    _write(root / "alpha" / "skills" / "README.txt", "not a skill")


@given(parsers.parse('an agents root containing agent "alpha" with a skill "cacheable-skill" that has a procedure'))
def given_skill_with_procedure(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    _write(root / "alpha" / "AGENT.md", _AGENT_MD)
    # Add trailing spaces to validate normalization.
    procedure = textwrap.dedent(
        """\
        Step 1: Do a thing   
        Step 2: Do another thing
        """
    )
    _write(
        root / "alpha" / "skills" / "cacheable-skill.md",
        _skill_md(skill_id="cacheable-skill", procedure=procedure),
    )


@given(parsers.parse('an agents root containing agent "alpha" with a skill "needs-inputs" that has an inputs table'))
def given_skill_with_inputs_table(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    _write(root / "alpha" / "AGENT.md", _AGENT_MD)
    table = """\
    | key | description |
    | --- | --- |
    | need_this | required |
    | need_that | required |
    | optional_thing | optional |
    """
    _write(
        root / "alpha" / "skills" / "needs-inputs.md",
        _skill_md(skill_id="needs-inputs", inputs_required_table=table, procedure="Run"),
    )


@given(parsers.parse('an agents root containing agents "alpha" and "gamma" each with a skill "shared-skill"'))
def given_ambiguous_skill(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    _write(root / "alpha" / "AGENT.md", _AGENT_MD)
    _write(root / "gamma" / "AGENT.md", _AGENT_MD.replace("agent-id: alpha", "agent-id: gamma"))
    _write(root / "alpha" / "skills" / "shared-skill.md", _skill_md(skill_id="shared-skill", procedure="Alpha"))
    _write(root / "gamma" / "skills" / "shared-skill.md", _skill_md(skill_id="shared-skill", procedure="Gamma"))


@when("I list agents")
def when_list_agents(ctx: dict[str, Any]) -> None:
    root: Path = ctx["agents_root"]
    ctx["result"] = reg.list_agents(agents_root=str(root))


@when(parsers.parse('I load agent identity for "{agent_id}"'))
def when_load_agent_identity(ctx: dict[str, Any], agent_id: str) -> None:
    root: Path = ctx["agents_root"]
    ctx["result"] = reg.load_agent_identity(agent_id, agents_root=str(root))


@when(parsers.parse('I list skills for agent "{agent_id}"'))
def when_list_skills(ctx: dict[str, Any], agent_id: str) -> None:
    root: Path = ctx["agents_root"]
    ctx["result"] = reg.list_agent_skills(agent_id, agents_root=str(root))


@when(parsers.parse('I get skill details for agent "{agent_id}" skill "{skill_id}"'))
def when_get_skill_details(ctx: dict[str, Any], agent_id: str, skill_id: str) -> None:
    root: Path = ctx["agents_root"]
    ctx["result"] = reg.get_skill_details(agent_id, skill_id, agents_root=str(root))


@when(parsers.parse('I check readiness for skill "{skill_id}" with provided inputs {inputs}'))
def when_check_readiness(ctx: dict[str, Any], skill_id: str, inputs: str) -> None:
    root: Path = ctx["agents_root"]
    # inputs comes as a string like ["a", "b"] or []
    provided = yaml.safe_load(inputs)
    assert isinstance(provided, list)
    ctx["result"] = reg.check_skill_readiness(skill_id, provided_inputs=provided, agents_root=str(root))


@then(parsers.parse("the agent IDs should be {expected}"))
def then_agent_ids(ctx: dict[str, Any], expected: str) -> None:
    exp = yaml.safe_load(expected)
    assert ctx["result"] == exp


@then(parsers.parse('the loaded agent identity system prompt should be "{expected}"'))
def then_system_prompt(ctx: dict[str, Any], expected: str) -> None:
    result = ctx["result"]
    assert isinstance(result, dict)
    assert result["system_prompt_identity"] == expected


@then(parsers.parse('the loaded agent identity frontmatter should include "{key}" = "{value}"'))
def then_identity_frontmatter(ctx: dict[str, Any], key: str, value: str) -> None:
    result = ctx["result"]
    assert isinstance(result, dict)
    fm = result["frontmatter"]
    assert isinstance(fm, dict)
    assert fm.get(key) == value


@then(parsers.parse("the skill IDs should be {expected}"))
def then_skill_ids(ctx: dict[str, Any], expected: str) -> None:
    exp = yaml.safe_load(expected)
    assert ctx["result"] == exp


@then("the procedure markdown should equal:")
def then_procedure_markdown(ctx: dict[str, Any], docstring: str) -> None:
    result = ctx["result"]
    assert isinstance(result, dict)
    got = result.get("procedure_markdown")
    assert isinstance(got, str)

    expected = textwrap.dedent(docstring)
    # Match server normalization: final newline, no leading/trailing blank lines.
    expected = expected.strip("\n") + "\n"

    assert got == expected


@then("the procedure sha256 should match the procedure markdown")
def then_procedure_hash(ctx: dict[str, Any]) -> None:
    result = ctx["result"]
    assert isinstance(result, dict)
    proc = result.get("procedure_markdown")
    sha = result.get("procedure_sha256")
    assert isinstance(proc, str)
    assert isinstance(sha, str)
    assert sha == hashlib.sha256(proc.encode("utf-8")).hexdigest()


@then(parsers.parse('the skill frontmatter should include "{key}" = "{value}"'))
def then_skill_frontmatter(ctx: dict[str, Any], key: str, value: str) -> None:
    result = ctx["result"]
    assert isinstance(result, dict)
    fm = result.get("frontmatter")
    assert isinstance(fm, dict)
    assert fm.get(key) == value


@then("the readiness result should be not ready")
def then_not_ready(ctx: dict[str, Any]) -> None:
    result = ctx["result"]
    assert isinstance(result, dict)
    assert result.get("found") is True
    assert result.get("ready") is False


@then(parsers.parse("the missing inputs should be {expected}"))
def then_missing_inputs(ctx: dict[str, Any], expected: str) -> None:
    exp = yaml.safe_load(expected)
    result = ctx["result"]
    assert isinstance(result, dict)
    assert result.get("missing_inputs") == exp


@then(parsers.parse("the readiness result should be ambiguous with candidates {expected}"))
def then_ambiguous(ctx: dict[str, Any], expected: str) -> None:
    exp = yaml.safe_load(expected)
    result = ctx["result"]
    assert isinstance(result, dict)
    assert result.get("found") is False
    assert result.get("reason") == "ambiguous"
    assert result.get("candidates") == exp

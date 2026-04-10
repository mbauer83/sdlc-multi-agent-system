"""
BDD tests for SkillLoader SectionSpec registry, mode-aware filtering,
unknown-section warnings, stub detection, budget constants, and public API.
"""

from __future__ import annotations

import textwrap
import warnings
from pathlib import Path

import pytest
from pytest_bdd import given, scenario, then, when

from src.agents._skill_sections import (
    BUDGETS,
    SECTION_REGISTRY,
    SectionEntry,
    _ALIAS_MAP,
    budget_tokens,
    filter_by_mode,
    parse_sections,
)
from src.agents.skill_loader import SkillLoader, SkillNotFoundError, SkillSpec


# ---------------------------------------------------------------------------
# Fixtures / shared state
# ---------------------------------------------------------------------------

class _State:
    entries: list[SectionEntry] = []
    filtered: list[SectionEntry] = []
    warnings_list: list[warnings.WarningMessage] = []
    skill_spec: SkillSpec | None = None
    error: Exception | None = None


@pytest.fixture()
def state() -> _State:
    return _State()


# ---------------------------------------------------------------------------
# Registry scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "SectionSpec registry has all 9 expected canonical keys")
def test_registry_all_keys() -> None: ...

@given("the SectionSpec registry", target_fixture="state")
def _given_registry(state: _State) -> _State:
    return state

@then('the registry contains "procedure"')
def _then_procedure(state: _State) -> None:
    assert "procedure" in SECTION_REGISTRY

@then('the registry contains "inputs required"')
def _then_inputs(state: _State) -> None:
    assert "inputs required" in SECTION_REGISTRY

@then('the registry contains "feedback loop"')
def _then_feedback(state: _State) -> None:
    assert "feedback loop" in SECTION_REGISTRY

@then('the registry contains "algedonic triggers"')
def _then_algedonic(state: _State) -> None:
    assert "algedonic triggers" in SECTION_REGISTRY

@then('the registry contains "outputs"')
def _then_outputs(state: _State) -> None:
    assert "outputs" in SECTION_REGISTRY

@then('the registry contains "end-of-skill memory close"')
def _then_eosmc(state: _State) -> None:
    assert "end-of-skill memory close" in SECTION_REGISTRY

@then('the registry contains "common rationalizations (rejected)"')
def _then_rationalizations(state: _State) -> None:
    assert "common rationalizations (rejected)" in SECTION_REGISTRY

@then('the registry contains "red flags"')
def _then_red_flags(state: _State) -> None:
    assert "red flags" in SECTION_REGISTRY

@then('the registry contains "verification"')
def _then_verification(state: _State) -> None:
    assert "verification" in SECTION_REGISTRY


@scenario("features/skill_loader.feature",
          '"steps" alias resolves to procedure canonical key')
def test_steps_alias() -> None: ...

@when('I look up alias "steps"', target_fixture="state")
def _when_lookup_alias(state: _State) -> _State:
    return state

@then('the canonical key is "procedure"')
def _then_canonical_procedure(state: _State) -> None:
    assert _ALIAS_MAP["steps"] == "procedure"


@scenario("features/skill_loader.feature",
          "procedure section has truncation_priority -1 (never truncated)")
def test_procedure_never_truncated() -> None: ...

@then('"procedure" has truncation_priority -1')
def _then_proc_prio(state: _State) -> None:
    assert SECTION_REGISTRY["procedure"].truncation_priority == -1


# ---------------------------------------------------------------------------
# Mode filtering helpers
# ---------------------------------------------------------------------------

def _md_with(*headers: str) -> str:
    parts = []
    for h in headers:
        parts.append(f"## {h}\n\nsome content here\n")
    return "\n".join(parts)


def _has_key(entries: list[SectionEntry], key: str) -> bool:
    return any(e.canonical_key == key for e in entries)


# ---------------------------------------------------------------------------
# Mode filtering scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "workflow mode includes algedonic triggers")
def test_workflow_includes_algedonic() -> None: ...

@scenario("features/skill_loader.feature",
          "express mode excludes algedonic triggers")
def test_express_excludes_algedonic() -> None: ...

@given("a skill markdown with an algedonic triggers section", target_fixture="state")
def _given_algedonic_md(state: _State) -> _State:
    state.entries = parse_sections(
        _md_with("Inputs Required", "Procedure", "Algedonic Triggers")
    )
    return state

@when('I parse and filter for mode "workflow"', target_fixture="state")
def _when_filter_workflow(state: _State) -> _State:
    state.filtered = filter_by_mode(state.entries, "workflow")
    return state

@when('I parse and filter for mode "express"', target_fixture="state")
def _when_filter_express(state: _State) -> _State:
    state.filtered = filter_by_mode(state.entries, "express")
    return state

@then('the filtered entries include "algedonic triggers"')
def _then_has_algedonic(state: _State) -> None:
    assert _has_key(state.filtered, "algedonic triggers")

@then('the filtered entries do not include "algedonic triggers"')
def _then_no_algedonic(state: _State) -> None:
    assert not _has_key(state.filtered, "algedonic triggers")


@scenario("features/skill_loader.feature",
          "express mode excludes end-of-skill memory close")
def test_express_excludes_eosmc() -> None: ...

@given("a skill markdown with an end-of-skill memory close section", target_fixture="state")
def _given_eosmc_md(state: _State) -> _State:
    state.entries = parse_sections(
        _md_with("Inputs Required", "Procedure", "End-of-Skill Memory Close")
    )
    return state

@then('the filtered entries do not include "end-of-skill memory close"')
def _then_no_eosmc(state: _State) -> None:
    assert not _has_key(state.filtered, "end-of-skill memory close")


@scenario("features/skill_loader.feature",
          "per-instance workflow tag forces inclusion even for unknown sections")
def test_instance_tag_workflow() -> None: ...

@given("a skill markdown with an unknown section tagged workflow", target_fixture="state")
def _given_custom_workflow(state: _State) -> _State:
    md = "## Custom Section <!-- workflow -->\n\nsome body\n"
    state.entries = parse_sections(md)
    return state

@then('the filtered entries include "custom section"')
def _then_has_custom(state: _State) -> None:
    assert _has_key(state.filtered, "custom section")


@scenario("features/skill_loader.feature",
          "per-instance express tag forces express-only inclusion")
def test_instance_tag_express() -> None: ...

@given("a skill markdown with a section tagged express", target_fixture="state")
def _given_express_tagged(state: _State) -> _State:
    md = "## Express Mode <!-- express -->\n\nsome express content\n"
    state.entries = parse_sections(md)
    return state

@then('the filtered entries do not include "express mode"')
def _then_no_express_in_workflow(state: _State) -> None:
    assert not _has_key(state.filtered, "express mode")

@then('the filtered entries include "express mode"')
def _then_has_express(state: _State) -> None:
    assert _has_key(state.filtered, "express mode")


# ---------------------------------------------------------------------------
# Assembly position scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "common rationalizations section is assembled before inputs required")
def test_rationalizations_before_inputs() -> None: ...

@given("a skill markdown with rationalizations and inputs required sections",
       target_fixture="state")
def _given_rat_inputs(state: _State) -> _State:
    state.entries = parse_sections(
        _md_with("Inputs Required", "Common Rationalizations (Rejected)")
    )
    return state

@then('"common rationalizations (rejected)" assembly_position is less than '
     '"inputs required" assembly_position')
def _then_rat_before_inputs(state: _State) -> None:
    rat = SECTION_REGISTRY["common rationalizations (rejected)"]
    inp = SECTION_REGISTRY["inputs required"]
    assert rat.assembly_position < inp.assembly_position


@scenario("features/skill_loader.feature",
          "red flags section is assembled after feedback loop")
def test_red_flags_after_feedback() -> None: ...

@given("a skill markdown with red flags and feedback loop sections", target_fixture="state")
def _given_rf_fb(state: _State) -> _State:
    state.entries = parse_sections(_md_with("Feedback Loop", "Red Flags"))
    return state

@then('"red flags" assembly_position is greater than "feedback loop" assembly_position')
def _then_rf_after_fb(state: _State) -> None:
    assert (
        SECTION_REGISTRY["red flags"].assembly_position
        > SECTION_REGISTRY["feedback loop"].assembly_position
    )


@scenario("features/skill_loader.feature",
          "verification section is assembled after algedonic triggers")
def test_verification_after_algedonic() -> None: ...

@given("a skill markdown with verification and algedonic triggers sections",
       target_fixture="state")
def _given_ver_alg(state: _State) -> _State:
    state.entries = parse_sections(
        _md_with("Verification", "Algedonic Triggers")
    )
    return state

@then('"verification" assembly_position is greater than '
     '"algedonic triggers" assembly_position')
def _then_ver_after_alg(state: _State) -> None:
    assert (
        SECTION_REGISTRY["verification"].assembly_position
        > SECTION_REGISTRY["algedonic triggers"].assembly_position
    )


# ---------------------------------------------------------------------------
# Unknown section warning scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "unknown section without mode tag emits a warning")
def test_unknown_section_warning() -> None: ...

@given("a skill markdown with an unknown untagged section", target_fixture="state")
def _given_unknown_untagged(state: _State) -> _State:
    md = "## Some Completely Unknown Section\n\nbody\n"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        state.entries = parse_sections(md, skill_id="TEST-SKILL")
        state.warnings_list = list(w)
    return state

@when("I parse the sections", target_fixture="state")
def _when_parse(state: _State) -> _State:
    return state  # parsing already done in given step

@then("a UserWarning is emitted about the unknown section")
def _then_warning_emitted(state: _State) -> None:
    assert any(issubclass(w.category, UserWarning) for w in state.warnings_list)


@scenario("features/skill_loader.feature",
          "unknown section with mode tag does not emit a warning")
def test_unknown_section_no_warning() -> None: ...

@given("a skill markdown with an unknown section tagged workflow", target_fixture="state")
def _given_tagged_no_warn(state: _State) -> _State:
    md = "## Custom Section <!-- workflow -->\n\nsome body\n"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        state.entries = parse_sections(md, skill_id="TEST-SKILL")
        state.warnings_list = list(w)
    return state

@then("no UserWarning is emitted")
def _then_no_warning(state: _State) -> None:
    assert not any(issubclass(w.category, UserWarning) for w in state.warnings_list)


# ---------------------------------------------------------------------------
# Stub detection scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "stub body is detected and excluded from budget count")
def test_stub_budget() -> None: ...

@given("a skill markdown with a stub end-of-skill memory close section",
       target_fixture="state")
def _given_stub_eosmc(state: _State) -> _State:
    stub_body = "*Step 0.L — Injected at Layer 2.*"
    md = f"## End-of-Skill Memory Close\n\n{stub_body}\n"
    state.entries = parse_sections(md)
    return state

@when("I compute the budget token count", target_fixture="state")
def _when_compute_budget(state: _State) -> _State:
    return state

@then("the stub contributes at most 15 tokens to the budget")
def _then_stub_cheap(state: _State) -> None:
    eosmc_entries = [e for e in state.entries
                     if e.canonical_key == "end-of-skill memory close"]
    assert eosmc_entries, "end-of-skill memory close entry not found"
    assert eosmc_entries[0].is_stub
    cost = budget_tokens(eosmc_entries)
    # Stub contributes heading tokens (~7) + 5 = ~12; far less than full body (~50)
    assert cost <= 15, f"Expected ≤15 tokens (stub cost) but got {cost}"


# ---------------------------------------------------------------------------
# Budget constant scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "complex skill budget is 2350 soft / 2820 hard")
def test_complex_budget() -> None: ...

@scenario("features/skill_loader.feature",
          "standard skill budget is 1400 soft / 1680 hard")
def test_standard_budget() -> None: ...

@scenario("features/skill_loader.feature",
          "simple skill budget is 700 soft / 840 hard")
def test_simple_budget() -> None: ...

@given("the BUDGETS dict", target_fixture="state")
def _given_budgets(state: _State) -> _State:
    return state

@then('"complex" soft cap is 2350')
def _then_complex_soft(state: _State) -> None:
    assert BUDGETS["complex"][0] == 2350

@then('"complex" hard cap is 2820')
def _then_complex_hard(state: _State) -> None:
    assert BUDGETS["complex"][1] == 2820

@then('"standard" soft cap is 1400')
def _then_standard_soft(state: _State) -> None:
    assert BUDGETS["standard"][0] == 1400

@then('"standard" hard cap is 1680')
def _then_standard_hard(state: _State) -> None:
    assert BUDGETS["standard"][1] == 1680

@then('"simple" soft cap is 700')
def _then_simple_soft(state: _State) -> None:
    assert BUDGETS["simple"][0] == 700

@then('"simple" hard cap is 840')
def _then_simple_hard(state: _State) -> None:
    assert BUDGETS["simple"][1] == 840


# ---------------------------------------------------------------------------
# SkillLoader public API scenarios
# ---------------------------------------------------------------------------

@scenario("features/skill_loader.feature",
          "load_instructions returns empty string for empty skill_id")
def test_load_empty_skill_id() -> None: ...

@scenario("features/skill_loader.feature",
          "load_instructions raises SkillNotFoundError for unknown skill")
def test_load_unknown_skill() -> None: ...

@scenario("features/skill_loader.feature",
          "SkillSpec includes invoke_when and invoke_never_when fields")
def test_skill_spec_routing_fields() -> None: ...

@given("a SkillLoader over an agents directory", target_fixture="state")
def _given_skill_loader(tmp_path: Path, state: _State) -> _State:
    # Create a minimal agents directory structure for unknown-skill tests
    (tmp_path / "test-agent" / "skills").mkdir(parents=True)
    state._loader = SkillLoader(tmp_path)  # type: ignore[attr-defined]
    return state

@when("I call load_instructions with an empty skill_id", target_fixture="state")
def _when_load_empty(state: _State) -> _State:
    state._result = state._loader.load_instructions("")  # type: ignore[attr-defined]
    return state

@then("the result is an empty string")
def _then_empty_result(state: _State) -> None:
    assert state._result == ""  # type: ignore[attr-defined]

@when('I call load_instructions with skill_id "NONEXISTENT-SKILL"', target_fixture="state")
def _when_load_nonexistent(state: _State) -> _State:
    try:
        state._loader.load_instructions("NONEXISTENT-SKILL")  # type: ignore[attr-defined]
    except SkillNotFoundError as exc:
        state.error = exc
    return state

@then("a SkillNotFoundError is raised")
def _then_not_found(state: _State) -> None:
    assert isinstance(state.error, SkillNotFoundError)


@given("a skill file with invoke-when and invoke-never-when frontmatter",
       target_fixture="state")
def _given_skill_file_routing(tmp_path: Path, state: _State) -> _State:
    skills_dir = tmp_path / "test-role" / "skills"
    skills_dir.mkdir(parents=True)
    skill_md = textwrap.dedent("""\
        ---
        skill-id: TEST-ROUTING
        agent: test-role
        complexity-class: standard
        trigger-phases: [A]
        primary-outputs: [some-artifact]
        invoke-when: >
          A Phase A Architecture Sprint starts and an Architecture Vision does not exist.
        invoke-never-when: >
          An Architecture Vision already exists at version 1.0.0.
        ---

        ## Inputs Required

        - Architecture brief

        ## Procedure

        Step 1. Do the thing.
        Step 2. Check it.

        ## Outputs

        - `architecture-repository/overview/architecture-vision.md`
        """)
    (skills_dir / "test-routing.md").write_text(skill_md)
    state._loader = SkillLoader(tmp_path)  # type: ignore[attr-defined]
    return state

@when("I load the skill", target_fixture="state")
def _when_load_skill(state: _State) -> _State:
    state.skill_spec = state._loader.load("TEST-ROUTING")  # type: ignore[attr-defined]
    return state

@then("the SkillSpec has a non-empty invoke_when")
def _then_invoke_when(state: _State) -> None:
    assert state.skill_spec is not None
    assert state.skill_spec.invoke_when != ""

@then("the SkillSpec has a non-empty invoke_never_when")
def _then_invoke_never_when(state: _State) -> None:
    assert state.skill_spec is not None
    assert state.skill_spec.invoke_never_when != ""

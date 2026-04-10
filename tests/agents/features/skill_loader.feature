Feature: SkillLoader SectionSpec registry and mode-aware filtering

  # --- Registry ---

  Scenario: SectionSpec registry has all 9 expected canonical keys
    Given the SectionSpec registry
    Then the registry contains "procedure"
    And the registry contains "inputs required"
    And the registry contains "feedback loop"
    And the registry contains "algedonic triggers"
    And the registry contains "outputs"
    And the registry contains "end-of-skill memory close"
    And the registry contains "common rationalizations (rejected)"
    And the registry contains "red flags"
    And the registry contains "verification"

  Scenario: "steps" alias resolves to procedure canonical key
    Given the SectionSpec registry
    When I look up alias "steps"
    Then the canonical key is "procedure"

  Scenario: procedure section has truncation_priority -1 (never truncated)
    Given the SectionSpec registry
    Then "procedure" has truncation_priority -1

  # --- Mode filtering ---

  Scenario: workflow mode includes algedonic triggers
    Given a skill markdown with an algedonic triggers section
    When I parse and filter for mode "workflow"
    Then the filtered entries include "algedonic triggers"

  Scenario: express mode excludes algedonic triggers
    Given a skill markdown with an algedonic triggers section
    When I parse and filter for mode "express"
    Then the filtered entries do not include "algedonic triggers"

  Scenario: express mode excludes end-of-skill memory close
    Given a skill markdown with an end-of-skill memory close section
    When I parse and filter for mode "express"
    Then the filtered entries do not include "end-of-skill memory close"

  Scenario: per-instance workflow tag forces inclusion even for unknown sections
    Given a skill markdown with an unknown section tagged workflow
    When I parse and filter for mode "workflow"
    Then the filtered entries include "custom section"

  Scenario: per-instance express tag forces express-only inclusion
    Given a skill markdown with a section tagged express
    When I parse and filter for mode "workflow"
    Then the filtered entries do not include "express mode"
    When I parse and filter for mode "express"
    Then the filtered entries include "express mode"

  # --- New sections included ---

  Scenario: common rationalizations section is assembled before inputs required
    Given a skill markdown with rationalizations and inputs required sections
    When I parse and filter for mode "workflow"
    Then "common rationalizations (rejected)" assembly_position is less than "inputs required" assembly_position

  Scenario: red flags section is assembled after feedback loop
    Given a skill markdown with red flags and feedback loop sections
    When I parse and filter for mode "workflow"
    Then "red flags" assembly_position is greater than "feedback loop" assembly_position

  Scenario: verification section is assembled after algedonic triggers
    Given a skill markdown with verification and algedonic triggers sections
    When I parse and filter for mode "workflow"
    Then "verification" assembly_position is greater than "algedonic triggers" assembly_position

  # --- Unknown section warning ---

  Scenario: unknown section without mode tag emits a warning
    Given a skill markdown with an unknown untagged section
    When I parse the sections
    Then a UserWarning is emitted about the unknown section

  Scenario: unknown section with mode tag does not emit a warning
    Given a skill markdown with an unknown section tagged workflow
    When I parse the sections
    Then no UserWarning is emitted

  # --- Stub detection ---

  Scenario: stub body is detected and excluded from budget count
    Given a skill markdown with a stub end-of-skill memory close section
    When I compute the budget token count
    Then the stub contributes at most 15 tokens to the budget

  # --- Budget constants ---

  Scenario: complex skill budget is 2350 soft / 2820 hard
    Given the BUDGETS dict
    Then "complex" soft cap is 2350
    And "complex" hard cap is 2820

  Scenario: standard skill budget is 1400 soft / 1680 hard
    Given the BUDGETS dict
    Then "standard" soft cap is 1400
    And "standard" hard cap is 1680

  Scenario: simple skill budget is 700 soft / 840 hard
    Given the BUDGETS dict
    Then "simple" soft cap is 700
    And "simple" hard cap is 840

  # --- SkillLoader public API ---

  Scenario: load_instructions returns empty string for empty skill_id
    Given a SkillLoader over an agents directory
    When I call load_instructions with an empty skill_id
    Then the result is an empty string

  Scenario: load_instructions raises SkillNotFoundError for unknown skill
    Given a SkillLoader over an agents directory
    When I call load_instructions with skill_id "NONEXISTENT-SKILL"
    Then a SkillNotFoundError is raised

  Scenario: SkillSpec includes invoke_when and invoke_never_when fields
    Given a skill file with invoke-when and invoke-never-when frontmatter
    When I load the skill
    Then the SkillSpec has a non-empty invoke_when
    And the SkillSpec has a non-empty invoke_never_when

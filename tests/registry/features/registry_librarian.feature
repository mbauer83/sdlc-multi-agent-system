Feature: Registry librarian tools
  The registry MCP server provides filesystem-backed discovery of agents and skills.

  Scenario: List valid agents
    Given an agents root containing agents "alpha" (valid) and "beta" (invalid)
    When I list agents
    Then the agent IDs should be ["alpha"]

  Scenario: Load agent identity from AGENT.md
    Given an agents root containing agent "alpha" with an identity file
    When I load agent identity for "alpha"
    Then the loaded agent identity system prompt should be "You are Alpha."
    And the loaded agent identity frontmatter should include "agent-id" = "alpha"

  Scenario: List agent skills
    Given an agents root containing agent "alpha" with skills "skill-one" and "skill-two"
    When I list skills for agent "alpha"
    Then the skill IDs should be ["skill-one", "skill-two"]

  Scenario: Get skill details returns cacheable procedure
    Given an agents root containing agent "alpha" with a skill "cacheable-skill" that has a procedure
    When I get skill details for agent "alpha" skill "cacheable-skill"
    Then the procedure markdown should equal:
      """
      Step 1: Do a thing
      Step 2: Do another thing
      """
    And the procedure sha256 should match the procedure markdown
    And the skill frontmatter should include "skill-id" = "cacheable-skill"

  Scenario: Check skill readiness detects missing inputs
    Given an agents root containing agent "alpha" with a skill "needs-inputs" that has an inputs table
    When I check readiness for skill "needs-inputs" with provided inputs ["have_this"]
    Then the readiness result should be not ready
    And the missing inputs should be ["need_this", "need_that"]

  Scenario: Check skill readiness is ambiguous across agents
    Given an agents root containing agents "alpha" and "gamma" each with a skill "shared-skill"
    When I check readiness for skill "shared-skill" with provided inputs []
    Then the readiness result should be ambiguous with candidates ["alpha", "gamma"]

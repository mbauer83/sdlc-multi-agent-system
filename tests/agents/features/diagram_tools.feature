Feature: Diagram tools for SA and SwA agents

  Scenario: regenerate_macros with no entities returns zero-macro summary
    Given an empty architecture repository
    When I call regenerate_macros with no repo_path override
    Then the result contains "0 ArchiMate macro(s) written"

  Scenario: regenerate_macros with one archimate entity returns one macro
    Given an architecture repository with one entity that has an archimate display block
    When I call regenerate_macros with no repo_path override
    Then the result contains "1 ArchiMate macro(s) written"

  Scenario: generate_er_content for missing entity returns warning line
    Given an empty architecture repository
    When I call generate_er_content with entity_ids ["DOB-999"]
    Then the result contains "[Warning]"

  Scenario: validate_diagram returns error when PUML file does not exist
    Given an empty architecture repository
    When I call validate_diagram with a non-existent puml path
    Then the result contains "[Error]"

  Scenario: render_diagram returns skip message when plantuml is not on PATH
    Given an empty architecture repository
    And plantuml is not installed
    When I call render_diagram with a minimal puml file
    Then the result contains "[Skipped]"

  Scenario: register_diagram_tools adds 4 tools to an agent
    Given a PydanticAI agent with test model
    When I call register_diagram_tools on the agent
    Then the agent has 4 diagram tools registered

  Scenario: write_artifact auto-regenerates macros when entity has archimate block
    Given an architecture repository set up for write testing
    When write_artifact writes an entity with an archimate display block
    Then _macros.puml is regenerated with at least one macro

  Scenario: write_artifact does not regenerate macros for plain markdown
    Given an empty architecture repository for plain write test
    When write_artifact writes a plain markdown file without archimate block
    Then _macros.puml count is unchanged

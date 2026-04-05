Feature: Unified model repository (engagement + enterprise)
  As a Stage 5 discovery tool
  I want the model registry to index both engagement and enterprise repositories
  So that engagement work can build on enterprise architecture without copying

  Scenario: Engagement and enterprise are indexed and filterable
    Given a unified model repository with engagement and enterprise fixtures
    When I call list_artifacts with engagement filter "enterprise"
    Then I get 1 artifact summary
    And the summary engagement is "enterprise"

  Scenario: search_artifacts can be scoped to enterprise
    Given a unified model repository with engagement and enterprise fixtures
    When I call search_artifacts for "EnterprisePrinciple" with engagement "enterprise"
    Then "PRI-900" appears in the search results

  Scenario: Duplicate artifact-id across mounted roots is rejected
    Given two mounted repositories contain entity "APP-001"
    When I build a unified model repository
    Then a duplicate artifact-id error is raised

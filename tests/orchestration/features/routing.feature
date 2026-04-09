Feature: SDLC LangGraph routing functions
  Routing functions read SDLCGraphState and return the name of the next node.
  Algedonic bypass takes priority over every other routing decision.

  # ---------------------------------------------------------------------------
  # route_from_pm — central PM dispatcher
  # ---------------------------------------------------------------------------

  Scenario: PM routes to the correct specialist node for each agent role
    Given a clean state with pm_decision invoke_specialist for "<agent_id>"
    When route_from_pm is called
    Then the next node is "<expected_node>"

    Examples:
      | agent_id | expected_node |
      | SA       | sa_node       |
      | SwA      | swa_node      |
      | DO       | do_node       |
      | DE       | de_node       |
      | QA       | qa_node       |
      | PO       | po_node       |
      | SMM      | smm_node      |
      | CSCO     | csco_node     |

  Scenario: PM routes to gate_check_node when next_action is evaluate_gate
    Given a clean state with pm_decision evaluate_gate
    When route_from_pm is called
    Then the next node is "gate_check_node"

  Scenario: PM routes to cq_user_node when next_action is surface_cqs
    Given a clean state with pm_decision surface_cqs
    When route_from_pm is called
    Then the next node is "cq_user_node"

  Scenario: PM routes to sprint_close_node when next_action is close_sprint
    Given a clean state with pm_decision close_sprint
    When route_from_pm is called
    Then the next node is "sprint_close_node"

  Scenario: PM routes to engagement_complete_node when next_action is complete_engagement
    Given a clean state with pm_decision complete_engagement
    When route_from_pm is called
    Then the next node is "engagement_complete_node"

  Scenario: PM routes to review_processing_node when next_action is trigger_review
    Given a clean state with pm_decision trigger_review
    When route_from_pm is called
    Then the next node is "review_processing_node"

  Scenario: Algedonic bypass wins over any PM specialist decision
    Given a clean state with pm_decision invoke_specialist for "SA"
    And algedonic_active is True
    When route_from_pm is called
    Then the next node is "algedonic_handler_node"

  Scenario: Algedonic bypass wins over gate evaluation
    Given a clean state with pm_decision evaluate_gate
    And algedonic_active is True
    When route_from_pm is called
    Then the next node is "algedonic_handler_node"

  Scenario: PM re-deliberates when pm_decision is None
    Given a clean state with no pm_decision
    When route_from_pm is called
    Then the next node is "pm_node"

  Scenario: PM re-deliberates when specialist_id is unknown
    Given a clean state with pm_decision invoke_specialist for "UNKNOWN"
    When route_from_pm is called
    Then the next node is "pm_node"

  # ---------------------------------------------------------------------------
  # route_after_specialist
  # ---------------------------------------------------------------------------

  Scenario: After specialist, return to PM in the normal case
    Given a clean state
    When route_after_specialist is called
    Then the next node is "pm_node"

  Scenario: After specialist, algedonic bypass takes priority
    Given a clean state with algedonic_active True
    When route_after_specialist is called
    Then the next node is "algedonic_handler_node"

  Scenario: After specialist, route to review when review is pending
    Given a clean state with review_pending True
    When route_after_specialist is called
    Then the next node is "review_processing_node"

  Scenario: Algedonic bypass wins over review_pending after specialist
    Given a clean state with review_pending True and algedonic_active True
    When route_after_specialist is called
    Then the next node is "algedonic_handler_node"

  # ---------------------------------------------------------------------------
  # route_after_gate
  # ---------------------------------------------------------------------------

  Scenario: After gate, return to PM in the normal case
    Given a clean state
    When route_after_gate is called
    Then the next node is "pm_node"

  Scenario: After gate, algedonic bypass takes priority
    Given a clean state with algedonic_active True
    When route_after_gate is called
    Then the next node is "algedonic_handler_node"

  Scenario: After gate, route to review when review is pending
    Given a clean state with review_pending True
    When route_after_gate is called
    Then the next node is "review_processing_node"

  # ---------------------------------------------------------------------------
  # route_after_cq
  # ---------------------------------------------------------------------------

  Scenario: After CQ answer, always return to PM
    Given a clean state
    When route_after_cq is called
    Then the next node is "pm_node"

  Scenario: After CQ answer with algedonic active, still return to PM
    Given a clean state with algedonic_active True
    When route_after_cq is called
    Then the next node is "pm_node"

  # ---------------------------------------------------------------------------
  # route_after_algedonic
  # ---------------------------------------------------------------------------

  Scenario: After algedonic handled, return to PM by default
    Given a clean state
    When route_after_algedonic is called
    Then the next node is "pm_node"

  Scenario: After algedonic, route to engagement_complete when PM says so
    Given a clean state with pm_decision complete_engagement
    When route_after_algedonic is called
    Then the next node is "engagement_complete_node"

  # ---------------------------------------------------------------------------
  # route_after_sprint_close
  # ---------------------------------------------------------------------------

  Scenario: After sprint close, return to PM in the normal case
    Given a clean state
    When route_after_sprint_close is called
    Then the next node is "pm_node"

  Scenario: After sprint close, route to review when review is pending
    Given a clean state with review_pending True
    When route_after_sprint_close is called
    Then the next node is "review_processing_node"

  # ---------------------------------------------------------------------------
  # route_after_review
  # ---------------------------------------------------------------------------

  Scenario: After review processed, always return to PM
    Given a clean state
    When route_after_review is called
    Then the next node is "pm_node"

Feature: SDLC LangGraph graph structure
  build_sdlc_graph() must compile without error and register every node and
  edge described in framework/orchestration-topology.md §4.3.

  Scenario: Graph compiles without error given a valid EngagementSession
    Given a stub EngagementSession
    When build_sdlc_graph is called
    Then the compiled graph is not None

  Scenario: All specialist nodes are registered in the graph
    Given a stub EngagementSession
    When build_sdlc_graph is called
    Then the graph contains node "<node_name>"

    Examples:
      | node_name              |
      | pm_node                |
      | sa_node                |
      | swa_node               |
      | do_node                |
      | de_node                |
      | qa_node                |
      | po_node                |
      | smm_node               |
      | csco_node              |

  Scenario: All infrastructure nodes are registered in the graph
    Given a stub EngagementSession
    When build_sdlc_graph is called
    Then the graph contains node "<node_name>"

    Examples:
      | node_name                  |
      | gate_check_node            |
      | cq_user_node               |
      | algedonic_handler_node     |
      | sprint_close_node          |
      | review_processing_node     |
      | engagement_complete_node   |

  Scenario: initial_state produces a valid SDLCGraphState
    Given engagement id "ENG-TEST"
    When initial_state is called
    Then the state has engagement_id "ENG-TEST"
    And the state has algedonic_active False
    And the state has review_pending False
    And the state has pm_decision None

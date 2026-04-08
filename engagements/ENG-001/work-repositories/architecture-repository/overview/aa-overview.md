---
artifact-type: aa-overview
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
safety-relevant: true
csco-sign-off: pending
references:
  - APP-001
  - APP-002
  - APP-003
  - APP-004
  - APP-005
  - APP-006
  - APP-007
  - APP-008
  - APP-009
  - APP-010
  - APP-011
  - APP-012
  - APP-013
  - APP-014
  - APP-015
  - APP-016
  - APP-017
  - APP-018
  - APP-019
  - APP-020
  - APP-021
  - APP-022
  - AIF-001
  - AIF-002
  - AIF-003
  - AIF-004
  - AIF-005
  - AIF-006
  - DOB-001
  - DOB-002
  - DOB-003
  - DOB-004
  - DOB-005
  - DOB-006
  - DOB-007
  - DOB-008
  - DOB-009
  - DOB-010
  - DOB-011
  - DOB-012
  - DOB-013
---

# Application Architecture Overview — ENG-001

## Summary
This overview maps the ENG-001 application-layer model to intended implementation structure for Stage 5 delivery. Application entities remain technology-independent; concrete framework/runtime selection is captured in ADRs and technology artifacts.

## Layering Rule
All implementation follows the dependency rule:
Common -> Domain -> Application -> Infrastructure

## Application Components (APP)
| APP ID | Model entity | Target implementation path | One-line function |
|---|---|---|---|
| APP-001 | [@APP-001 v0.1.0](../model-entities/application/components/APP-001.event-store.md) | `src/events/` | Canonical event persistence and replay boundary. |
| APP-002 | [@APP-002 v0.1.0](../model-entities/application/components/APP-002.model-registry.md) | `src/common/model_query.py` | Model index/query facade over ERP v2.0 files. |
| APP-003 | [@APP-003 v0.1.0](../model-entities/application/components/APP-003.learning-store.md) | `src/agents/learning_store.py` | Learning retrieval/record gateway for agents. |
| APP-004 | [@APP-004 v0.1.0](../model-entities/application/components/APP-004.skill-loader.md) | `src/agents/skill_loader.py` | Runtime skill selection and bounded instruction loading. |
| APP-005 | [@APP-005 v0.1.0](../model-entities/application/components/APP-005.agent-factory.md) | `src/agents/base.py` | Layered PydanticAI agent construction. |
| APP-006 | [@APP-006 v0.1.0](../model-entities/application/components/APP-006.agent-registry.md) | `src/agents/__init__.py` | Role-to-agent registration and lookup. |
| APP-007 | [@APP-007 v0.1.0](../model-entities/application/components/APP-007.pm-agent.md) | `src/agents/project_manager.py` | PM supervision and decision orchestration intent. |
| APP-008 | [@APP-008 v0.1.0](../model-entities/application/components/APP-008.sa-agent.md) | `src/agents/solution_architect.py` | SA specialist execution intent. |
| APP-009 | [@APP-009 v0.1.0](../model-entities/application/components/APP-009.swa-agent.md) | `src/agents/software_architect.py` | SwA specialist execution intent. |
| APP-010 | [@APP-010 v0.1.0](../model-entities/application/components/APP-010.do-agent.md) | `src/agents/devops_platform.py` | DevOps specialist execution intent. |
| APP-011 | [@APP-011 v0.1.0](../model-entities/application/components/APP-011.de-agent.md) | `src/agents/implementing_developer.py` | Developer specialist execution intent. |
| APP-012 | [@APP-012 v0.1.0](../model-entities/application/components/APP-012.qa-agent.md) | `src/agents/qa_engineer.py` | QA specialist execution intent. |
| APP-013 | [@APP-013 v0.1.0](../model-entities/application/components/APP-013.po-agent.md) | `src/agents/product_owner.py` | PO specialist execution intent. |
| APP-014 | [@APP-014 v0.1.0](../model-entities/application/components/APP-014.sm-agent.md) | `src/agents/sales_marketing.py` | Sales/marketing specialist execution intent. |
| APP-015 | [@APP-015 v0.1.0](../model-entities/application/components/APP-015.csco-agent.md) | `src/agents/csco.py` | Safety/compliance specialist execution intent. |
| APP-016 | [@APP-016 v0.1.0](../model-entities/application/components/APP-016.langgraph-orchestrator.md) | `src/orchestration/graph_builder.py` | Nested graph topology and routing control. |
| APP-017 | [@APP-017 v0.1.0](../model-entities/application/components/APP-017.engagement-session.md) | `src/orchestration/engagement_session.py` | Session lifecycle and state bootstrap/resume. |
| APP-018 | [@APP-018 v0.1.0](../model-entities/application/components/APP-018.user-interaction-orchestrator.md) | `src/orchestration/user_interaction.py` | CQ/review interaction processing loop. |
| APP-019 | [@APP-019 v0.1.0](../model-entities/application/components/APP-019.promotion-orchestrator.md) | `src/orchestration/promotion.py` | Enterprise-promotion coordination boundary. |
| APP-020 | [@APP-020 v0.1.0](../model-entities/application/components/APP-020.dashboard-server.md) | `src/dashboard/server.py` | Local dashboard HTTP surface. |
| APP-021 | [@APP-021 v0.1.0](../model-entities/application/components/APP-021.user-input-gateway.md) | `src/dashboard/interaction.py` | User answers/uploads/review ingestion. |
| APP-022 | [@APP-022 v0.1.0](../model-entities/application/components/APP-022.target-repo-manager.md) | `src/sources/target_repo_manager.py` | Multi-target-repository management boundary. |

## Data Objects (DOB)
| DOB ID | Model entity | Target src/models path |
|---|---|---|
| DOB-001 | [@DOB-001 v0.1.0](../model-entities/application/data-objects/DOB-001.workflow-event.md) | `src/models/workflow_event.py` |
| DOB-002 | [@DOB-002 v0.1.0](../model-entities/application/data-objects/DOB-002.engagement.md) | `src/models/engagement.py` |
| DOB-003 | [@DOB-003 v0.1.0](../model-entities/application/data-objects/DOB-003.learning-entry.md) | `src/models/learning_entry.py` |
| DOB-004 | [@DOB-004 v0.1.0](../model-entities/application/data-objects/DOB-004.clarification-request.md) | `src/models/clarification_request.py` |
| DOB-005 | [@DOB-005 v0.1.0](../model-entities/application/data-objects/DOB-005.algedonic-signal.md) | `src/models/algedonic_signal.py` |
| DOB-006 | [@DOB-006 v0.1.0](../model-entities/application/data-objects/DOB-006.handoff-record.md) | `src/models/handoff_record.py` |
| DOB-007 | [@DOB-007 v0.1.0](../model-entities/application/data-objects/DOB-007.gate-outcome.md) | `src/models/gate_outcome.py` |
| DOB-008 | [@DOB-008 v0.1.0](../model-entities/application/data-objects/DOB-008.review-item.md) | `src/models/review_item.py` |
| DOB-009 | [@DOB-009 v0.1.0](../model-entities/application/data-objects/DOB-009.workflow-state.md) | `src/models/workflow_state.py` |
| DOB-010 | [@DOB-010 v0.1.0](../model-entities/application/data-objects/DOB-010.agent-deps.md) | `src/models/agent_deps.py` |
| DOB-011 | [@DOB-011 v0.1.0](../model-entities/application/data-objects/DOB-011.pm-decision.md) | `src/models/pm_decision.py` |
| DOB-012 | [@DOB-012 v0.1.0](../model-entities/application/data-objects/DOB-012.sdlc-graph-state.md) | `src/models/sdlc_graph_state.py` |
| DOB-013 | [@DOB-013 v0.1.0](../model-entities/application/data-objects/DOB-013.artifact-record.md) | `src/models/artifact_record.py` |

## Application Interfaces (AIF)
| AIF ID | Model entity | Protocol location (intended) |
|---|---|---|
| AIF-001 | [@AIF-001 v0.1.0](../model-entities/application/interfaces/AIF-001.event-store-port.md) | `src/events/ports.py` |
| AIF-002 | [@AIF-002 v0.1.0](../model-entities/application/interfaces/AIF-002.llm-client-port.md) | `src/agents/ports.py` |
| AIF-003 | [@AIF-003 v0.1.0](../model-entities/application/interfaces/AIF-003.source-adapter-port.md) | `src/sources/base.py` |
| AIF-004 | [@AIF-004 v0.1.0](../model-entities/application/interfaces/AIF-004.artifact-read-writer-port.md) | `src/common/ports.py` |
| AIF-005 | [@AIF-005 v0.1.0](../model-entities/application/interfaces/AIF-005.diagram-tools-port.md) | `src/common/ports.py` |
| AIF-006 | [@AIF-006 v0.1.0](../model-entities/application/interfaces/AIF-006.learning-store-port.md) | `src/agents/learning_store.py` |

## Notes
- This file is the narrative handoff companion for Phase C application architecture.
- Model entities and connections remain the normative source of truth.

---
artifact-id: runtime-matrix-business-to-application-traceability-v1
artifact-type: diagram
diagram-type: matrix
name: "Cross-Layer Traceability Matrix \u2014 Business Workflow to Application Runtime"
version: 0.2.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
domain: core-platform
purpose: 'Phase C cross-layer conformance slice: map business workflow-net behaviors
  to application services/components, runtime boundary view, and sequence realizations
  used as Stage 5 implementation baseline.'
entity-ids-used:
- ACT-001
- BPR-002
- BPR-003
- BPR-004
- BPR-005
- BIA-001
- BEV-005
- BSV-003
- BSV-004
- AIA-001
- ASV-001
- ASV-003
- ASV-004
- APP-001
- APP-004
- APP-006
- APP-007
- APP-008
- APP-015
- APP-016
- APP-017
- APP-018
- APP-020
- APP-021
connection-ids-used:
- AIA-001---BPR-002@@archimate-realization
- ASV-004---BPR-003@@archimate-realization
- ASV-003---BIA-001@@archimate-realization
- BPR-004---BSV-003@@archimate-realization
- BPR-005---BSV-004@@archimate-realization
- ASV-001---BSV-003@@archimate-realization
- APP-020---ACT-001@@archimate-serving
- APP-020---APP-021@@archimate-serving
---

| Business workflow net | Realization relation(s) | Application service(s) | Runtime component path | Runtime boundary view | Sequence realization | Key events | Conformance check |
|---|---|---|---|---|---|---|---|
| [BPR-002 Skill Execution](../../model-entities/business/processes/BPR-002.skill-execution.md) | [AIA-001 -> BPR-002](../../connections/archimate/realization/AIA-001---BPR-002@@archimate-realization.md), [ASV-001 -> BSV-003](../../connections/archimate/realization/ASV-001---BSV-003@@archimate-realization.md) | [ASV-001 Agent Invocation Service](../../model-entities/application/services/ASV-001.agent-invocation-service.md) | [APP-016](../../model-entities/application/components/APP-016.langgraph-orchestrator.md) -> [APP-007](../../model-entities/application/components/APP-007.pm-agent.md)/[APP-008](../../model-entities/application/components/APP-008.sa-agent.md) + [APP-004](../../model-entities/application/components/APP-004.skill-loader.md) + [APP-006](../../model-entities/application/components/APP-006.agent-registry.md) | [runtime-archimate-application-interaction-boundaries-v1](./runtime-archimate-application-interaction-boundaries-v1.puml) | [runtime-sequence-specialist-invocation-cycle-v1](./runtime-sequence-specialist-invocation-cycle-v1.puml) | specialist.invoked, artifact.created/updated, specialist.completed | Service and sequence are aligned with model-backed APP/AIA realizations and invocation_id correlation for replay-safe causality tracing. |
| [BPR-003 CQ Lifecycle](../../model-entities/business/processes/BPR-003.cq-lifecycle.md) | [ASV-004 -> BPR-003](../../connections/archimate/realization/ASV-004---BPR-003@@archimate-realization.md), [APP-020 -> ACT-001](../../connections/archimate/serving/APP-020---ACT-001@@archimate-serving.md) | [ASV-004 CQ Management Service](../../model-entities/application/services/ASV-004.cq-management-service.md) | [APP-018](../../model-entities/application/components/APP-018.user-interaction-orchestrator.md) + [APP-020](../../model-entities/application/components/APP-020.dashboard-server.md) + [APP-021](../../model-entities/application/components/APP-021.user-input-gateway.md) + [APP-016](../../model-entities/application/components/APP-016.langgraph-orchestrator.md) | [runtime-archimate-application-interaction-boundaries-v1](./runtime-archimate-application-interaction-boundaries-v1.puml) | [runtime-sequence-cq-routing-resume-v1](./runtime-sequence-cq-routing-resume-v1.puml) | cq.raised, cq.batched, phase.suspended, cq.answered, cq.routed, phase.resumed | Suspend/resume semantics are explicit and delegated across PM, orchestration, and interaction runtime; canonical event_id dedup provides idempotent answer routing under retries/replay. |
| [BPR-004 Gate Evaluation](../../model-entities/business/processes/BPR-004.gate-evaluation.md) | [BPR-004 -> BSV-003](../../connections/archimate/realization/BPR-004---BSV-003@@archimate-realization.md), [ASV-001 -> BSV-003](../../connections/archimate/realization/ASV-001---BSV-003@@archimate-realization.md) | PM orchestration decision path (via [ASV-001](../../model-entities/application/services/ASV-001.agent-invocation-service.md)) | [APP-007](../../model-entities/application/components/APP-007.pm-agent.md) + [APP-008](../../model-entities/application/components/APP-008.sa-agent.md) + [APP-015](../../model-entities/application/components/APP-015.csco-agent.md) + [APP-016](../../model-entities/application/components/APP-016.langgraph-orchestrator.md) + [APP-001](../../model-entities/application/components/APP-001.event-store.md) + [APP-017](../../model-entities/application/components/APP-017.engagement-session.md) | [runtime-archimate-application-interaction-boundaries-v1](./runtime-archimate-application-interaction-boundaries-v1.puml) | [runtime-sequence-gate-evaluation-decision-path-v1](./runtime-sequence-gate-evaluation-decision-path-v1.puml) | gate.evaluated, decision.recorded, phase.transitioned, sprint.started | Reviewer collection includes producing/dependent specialists and CSCO safety vote before transition/rework routing; missing/timeout safety vote follows fail-closed escalation branch. |
| [BPR-005 Algedonic Escalation](../../model-entities/business/processes/BPR-005.algedonic-escalation.md) | [BPR-005 -> BSV-004](../../connections/archimate/realization/BPR-005---BSV-004@@archimate-realization.md), [APP-015 -> BPR-005](../../connections/archimate/realization/APP-015---BPR-005@@archimate-realization.md) | Safety-governance escalation decision path (orchestration fast-path) | [APP-008](../../model-entities/application/components/APP-008.sa-agent.md) + [APP-016](../../model-entities/application/components/APP-016.langgraph-orchestrator.md) + [APP-007](../../model-entities/application/components/APP-007.pm-agent.md) + [APP-015](../../model-entities/application/components/APP-015.csco-agent.md) + [APP-001](../../model-entities/application/components/APP-001.event-store.md) | [runtime-archimate-application-interaction-boundaries-v1](./runtime-archimate-application-interaction-boundaries-v1.puml) | [runtime-sequence-algedonic-escalation-fastpath-v1](./runtime-sequence-algedonic-escalation-fastpath-v1.puml) | algedonic.raised, decision.recorded, phase.suspended, review.pending | Fast-path escalation now has explicit app-layer control-loop traceability from signal capture to CSCO-backed orchestration action, with timeout-to-containment fail-safe default and correlation_id audit chain. |
| [BIA-001 Sprint Review Interaction](../../model-entities/business/interactions/BIA-001.sprint-review-interaction.md) | [ASV-003 -> BIA-001](../../connections/archimate/realization/ASV-003---BIA-001@@archimate-realization.md), [APP-020 -> ACT-001](../../connections/archimate/serving/APP-020---ACT-001@@archimate-serving.md) | [ASV-003 Sprint Review Service](../../model-entities/application/services/ASV-003.sprint-review-service.md) | [APP-020](../../model-entities/application/components/APP-020.dashboard-server.md) + [APP-021](../../model-entities/application/components/APP-021.user-input-gateway.md) + [APP-018](../../model-entities/application/components/APP-018.user-interaction-orchestrator.md) + [APP-007](../../model-entities/application/components/APP-007.pm-agent.md) + [APP-016](../../model-entities/application/components/APP-016.langgraph-orchestrator.md) + [APP-008](../../model-entities/application/components/APP-008.sa-agent.md) | [runtime-archimate-application-interaction-boundaries-v1](./runtime-archimate-application-interaction-boundaries-v1.puml) | [runtime-sequence-sprint-review-correction-loop-v1](./runtime-sequence-sprint-review-correction-loop-v1.puml) | review.pending, review.submitted, review.correction-routed, artifact.updated, review.sprint-closed, sprint.close | PM remains in the loop for post-review decisioning and correction routing before closure. |

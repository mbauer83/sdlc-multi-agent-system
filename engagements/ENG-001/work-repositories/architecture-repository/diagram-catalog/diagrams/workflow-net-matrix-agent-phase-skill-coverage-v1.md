---
artifact-id: workflow-net-matrix-agent-phase-skill-coverage-v1
artifact-type: diagram
diagram-type: matrix
name: Workflow-Net Coverage Matrix (Agent-Phase-Skill)
version: 0.1.0
status: draft
phase-produced: G
owner-agent: PM
engagement: ENG-001
domain: core-platform
purpose: Classify agent-phase-skill workflow units by complexity and model coverage
  to drive BPMN/activity diagram authoring decisions.
entity-ids-used: []
---

| Agent | Phase | Skill ID | Workflow Class | Existing Diagram Coverage | Gap Action |
|---|---|---|---|---|---|
| [SA](../../../../../../agents/solution-architect/AGENT.md) | B | [SA-PHASE-B](../../../../../../agents/solution-architect/skills/phase-b.md) | non-trivial (CQ + safety + multi-artifact) | partial (generic execution/governance views) | Added [b-activity-sa-phase-b-workflow-v1](b-activity-sa-phase-b-workflow-v1.puml) |
| [SA](../../../../../../agents/solution-architect/AGENT.md) | C | [SA-PHASE-C-APP-REVIEW](../../../../../../agents/solution-architect/skills/phase-c-application.md) | moderate | generic CQ/review views only | covered by [c-activity-swa-phase-c-application-workflow-v1](c-activity-swa-phase-c-application-workflow-v1.puml) + [cq-activity-lifecycle-v1](cq-activity-lifecycle-v1.puml) |
| [SA](../../../../../../agents/solution-architect/AGENT.md) | H | [SA-PHASE-H](../../../../../../agents/solution-architect/skills/phase-h.md) | non-trivial parallel-track | governance-level only | defer (next slice: H-specific net) |
| [SwA](../../../../../../agents/software-architect/AGENT.md) | C | [SwA-PHASE-C-APP](../../../../../../agents/software-architect/skills/phase-c-application.md) | non-trivial (cross-layer traceability) | partial | Added [c-activity-swa-phase-c-application-workflow-v1](c-activity-swa-phase-c-application-workflow-v1.puml) |
| [SwA](../../../../../../agents/software-architect/AGENT.md) | D/E/F | [SwA-PHASE-D](../../../../../../agents/software-architect/skills/phase-d.md) / [SwA-PHASE-E](../../../../../../agents/software-architect/skills/phase-e.md) / [SwA-PHASE-F](../../../../../../agents/software-architect/skills/phase-f.md) | moderate | generic sprint/governance | defer unless branch complexity increases |
| [SwA](../../../../../../agents/software-architect/AGENT.md) | G | [SwA-PHASE-G](../../../../../../agents/software-architect/skills/phase-g-governance.md) | moderate | [specialist-invocation-activity-workflow-v1](specialist-invocation-activity-workflow-v1.puml) + [g-activity-pm-phase-g-governance-workflow-v1](g-activity-pm-phase-g-governance-workflow-v1.puml) | covered |
| [PM](../../../../../../agents/project-manager/AGENT.md) | G | [PM-PHASE-G](../../../../../../agents/project-manager/skills/phase-g.md) | non-trivial (gates + review + CQ/algedonic + review-gate loopback) | partial | Added [g-activity-pm-phase-g-governance-workflow-v1](g-activity-pm-phase-g-governance-workflow-v1.puml) |
| [PM](../../../../../../agents/project-manager/AGENT.md) | A/B/C | [PM-PHASE-A](../../../../../../agents/project-manager/skills/phase-a.md) / [PM-MASTER](../../../../../../agents/project-manager/skills/master-agile-adm.md) | non-trivial orchestration | [lifecycle-activity-sprint-v1](lifecycle-activity-sprint-v1.puml) + [business-archimate-operational-governance-v1](business-archimate-operational-governance-v1.puml) | covered for current stage |
| [QA](../../../../../../agents/qa-engineer/AGENT.md) | G | [QA-PHASE-G](../../../../../../agents/qa-engineer/skills/phase-g-execution.md) | moderate | [specialist-invocation-activity-workflow-v1](specialist-invocation-activity-workflow-v1.puml) + [sprint-review-activity-workflow-v1](sprint-review-activity-workflow-v1.puml) | covered |
| [DE](../../../../../../agents/implementing-developer/AGENT.md) | G | [DE-PHASE-G](../../../../../../agents/implementing-developer/skills/phase-g.md) | moderate | [specialist-invocation-activity-workflow-v1](specialist-invocation-activity-workflow-v1.puml) + [sprint-review-activity-workflow-v1](sprint-review-activity-workflow-v1.puml) | covered |
| [DO](../../../../../../agents/devops-platform/AGENT.md) | G | [DO-PHASE-G](../../../../../../agents/devops-platform/skills/phase-g.md) | moderate | [specialist-invocation-activity-workflow-v1](specialist-invocation-activity-workflow-v1.puml) + [sprint-review-activity-workflow-v1](sprint-review-activity-workflow-v1.puml) | covered |
| [CSCO](../../../../../../agents/csco/AGENT.md) | G/H | [CSCO-GATE-G](../../../../../../agents/csco/skills/gate-phase-g.md) / [CSCO-GATE-H](../../../../../../agents/csco/skills/gate-phase-h.md) / [CSCO-INCIDENT](../../../../../../agents/csco/skills/incident-response.md) | non-trivial veto/escalation | [business-archimate-operational-governance-v1](business-archimate-operational-governance-v1.puml) + [g-activity-pm-phase-g-governance-workflow-v1](g-activity-pm-phase-g-governance-workflow-v1.puml) | covered (H-specific detail deferred) |

Notes:
- Step 0.L (learning lookup) and Discovery Scan are mandatory in all non-trivial units.
- External source lookup remains situative (EP-G/user-cited/PM-directed), not unconditional.
- Add dedicated Phase H parallel-track workflow nets in a follow-up slice if change-volume increases.

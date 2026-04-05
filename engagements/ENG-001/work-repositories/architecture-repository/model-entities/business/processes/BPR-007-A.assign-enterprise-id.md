---
artifact-id: BPR-007-A
artifact-type: business-process
name: "Assign Enterprise ID"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-007
stage-order: 1
---

<!-- §content -->

## Assign Enterprise ID

The PromotionOrchestrator reads `enterprise-repository/id-counters.yaml`, allocates the next globally unique enterprise ID for the entity type being promoted, and records the mapping from engagement-local ID to enterprise ID. The ID counter is incremented and the mapping is written atomically.

## Properties

| Attribute | Value |
|---|---|
| Input | Engagement-local entity ID; entity type; `id-counters.yaml` from enterprise repository |
| Output | Enterprise ID assigned; ID counter incremented; local→enterprise ID mapping recorded |
| Flow-to | BPR-007-B (Reference Sweep) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Assign Enterprise ID"
alias: BPR_007_A
```

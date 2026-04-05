---
artifact-id: BPR-008-C
artifact-type: business-process
name: "Confirm and Populate Model"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-008
stage-order: 3
---

<!-- §content -->

## Confirm and Populate Model

The confirmation CQs from BPR-008-B are routed to the user (via BPR-003). Confirmed entities are promoted from `[inferred]` to draft status and written to the model-entities corpus. Rejected inferences are discarded with a rationale note. The resulting populated model is the baseline for ongoing Phase G governance.

## Properties

| Attribute | Value |
|---|---|
| Input | Batched confirmation CQs (from BPR-008-B); user confirmations via BPR-003 |
| Output | Populated model-entities corpus (draft status); `entity.confirmed` events; gap assessment document |
| Sub-triggers | BPR-003 (CQ Lifecycle) for batched entity confirmations |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Confirm and Populate Model"
alias: BPR_008_C
```

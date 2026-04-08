---
artifact-id: DOB-009---DOB-004@@er-one-to-many
artifact-type: er-one-to-many
source: DOB-009
target: DOB-004
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

WorkflowState (DOB-009) contains many open ClarificationRequests (DOB-004). The `open_cqs` field in WorkflowState holds all CQs that have been raised but not yet answered; this list shrinks as `cq.answered` events are replayed.

<!-- §display -->

### er

```yaml
source-cardinality: "1"
target-cardinality: "0..*"
label: "has open"
```

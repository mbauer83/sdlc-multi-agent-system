---
artifact-id: DOB-009---DOB-001@@er-one-to-many
artifact-type: er-one-to-many
source: DOB-009
target: DOB-001
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

WorkflowState (DOB-009) is derived from many WorkflowEvents (DOB-001). WorkflowState is a computed projection — `EventStore.replay()` folds the full ordered event sequence into a single state object. There is no direct DB relationship; the derivation is via the replay function.

<!-- §display -->

### er

```yaml
source-cardinality: "1"
target-cardinality: "1..*"
label: "derived from"
```

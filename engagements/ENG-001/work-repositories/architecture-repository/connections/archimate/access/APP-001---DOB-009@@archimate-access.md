---
artifact-id: APP-001---DOB-009@@archimate-access
artifact-type: archimate-access
source: APP-001
target: DOB-009
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

EventStore (APP-001) produces WorkflowState (DOB-009) via event replay. `replay()` and `replay_from_latest_snapshot()` reduce the event log into a current WorkflowState object. WorkflowState is a derived, in-memory projection — it is never directly stored; the EventStore is the authoritative source.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-type: write
```

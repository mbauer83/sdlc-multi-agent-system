---
artifact-id: APP-001---APP-017@@archimate-serving
artifact-type: archimate-serving
source: APP-001
target: APP-017
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

EventStore (APP-001) serves EngagementSession (APP-017). On startup, EngagementSession calls `replay_from_latest_snapshot()` to restore WorkflowState; on shutdown it calls `create_snapshot()`. The engagement's full history is accessible through EventStore for integrity checks and disaster recovery.

<!-- §display -->

### archimate

```yaml
relationship-type: Serving
direction: source-to-target
```

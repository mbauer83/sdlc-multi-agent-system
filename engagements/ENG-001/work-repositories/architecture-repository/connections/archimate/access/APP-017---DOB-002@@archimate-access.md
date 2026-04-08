---
artifact-id: APP-017---DOB-002@@archimate-access
artifact-type: archimate-access
source: APP-017
target: DOB-002
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

EngagementSession (APP-017) reads the Engagement config object (DOB-002). On startup, EngagementSession reads `engagements-config.yaml` and `engagement-profile.md` to construct the Engagement domain object that seeds the initial WorkflowState.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-type: read
```

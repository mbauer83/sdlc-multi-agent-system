---
artifact-id: APP-021---DOB-004@@archimate-access
artifact-type: archimate-access
source: APP-021
target: DOB-004
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

UserInputGateway (APP-021) writes ClarificationRequest answers (DOB-004). When a user submits a CQ answer via the Dashboard, UserInputGateway validates the payload and calls `EventStore.record_event(cq.answered)` with the answer embedded in the DOB-004 payload.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-type: write
```

---
artifact-id: APP-001---APP-021@@archimate-serving
artifact-type: archimate-serving
source: APP-001
target: APP-021
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

EventStore (APP-001) serves UserInputGateway (APP-021). UserInputGateway writes `cq.answered`, `upload.registered`, and `review.submitted` events to the EventStore after validating user-submitted inputs through the Dashboard API endpoints.

<!-- §display -->

### archimate

```yaml
relationship-type: Serving
direction: source-to-target
```

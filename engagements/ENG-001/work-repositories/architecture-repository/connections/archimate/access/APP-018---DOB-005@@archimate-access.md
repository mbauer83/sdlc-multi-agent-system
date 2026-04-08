---
artifact-id: APP-018---DOB-005@@archimate-access
artifact-type: archimate-access
source: APP-018
target: DOB-005
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

UserInteractionOrchestrator (APP-018) reads AlgedonicSignal records (DOB-005) from EventStore as part of its monitoring loop. When an `algedonic.raised` event is detected, APP-018 extracts the AlgedonicSignal payload and routes it to the designated escalation target (CSCO or User) via a LangGraph graph signal, bypassing the normal phase-sequenced topology.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-mode: read
```

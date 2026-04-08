---
artifact-id: APP-005---DOB-010@@archimate-access
artifact-type: archimate-access
source: APP-005
target: DOB-010
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

AgentFactory (APP-005) constructs AgentDeps instances (DOB-010) for each LangGraph node invocation. At node entry, AgentFactory assembles the `AgentDeps` dataclass by injecting the current EventStore handle, ModelRegistry reference, LearningStore handle, active skill context, and tool set. The AgentDeps instance is discarded after the agent returns — it is never persisted.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-mode: read-write
```

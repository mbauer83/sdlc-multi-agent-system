---
artifact-id: APP-006---APP-007@@archimate-composition
artifact-type: archimate-composition
source: APP-006
target: APP-007
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

AgentRegistry (APP-006) contains PM Agent instance (APP-007). The registry maintains the live PydanticAI agent object for each role, keyed by agent-id, allowing LangGraph nodes to retrieve the pre-built agent without reconstructing it on every invocation.

<!-- §display -->

### archimate

```yaml
relationship-type: Composition
direction: source-to-target
```

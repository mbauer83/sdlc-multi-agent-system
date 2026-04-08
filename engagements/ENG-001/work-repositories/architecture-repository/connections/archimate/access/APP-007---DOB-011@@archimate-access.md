---
artifact-id: APP-007---DOB-011@@archimate-access
artifact-type: archimate-access
source: APP-007
target: DOB-011
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

PM Agent (APP-007) writes PMDecision (DOB-011). The PM Agent's PydanticAI `result_type` is PMDecision; every invocation returns a structured decision object specifying `next_action`, target skill, and optional CQ batch — which the routing function reads to select the next LangGraph node.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-type: write
```

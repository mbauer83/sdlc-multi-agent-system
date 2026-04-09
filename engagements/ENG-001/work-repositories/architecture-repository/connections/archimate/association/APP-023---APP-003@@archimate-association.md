---
artifact-id: APP-023---APP-003@@archimate-association
artifact-type: archimate-association
source: APP-023
target: APP-003
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: '2026-04-09'
---

<!-- §content -->

MementoStore (APP-023) and LearningStore (APP-003) share the same LangGraph SQLiteStore backend (workflow.db) but use distinct namespaces and semantics. APP-023 uses namespace (engagement_id, agent_role, "memento") with overwrite semantics; APP-003 uses (engagement_id, agent_role, "learnings") with accumulate semantics. This association records the shared-infrastructure relationship.

<!-- §display -->

### archimate

```yaml
relationship-type: Association
direction: source-to-target
```

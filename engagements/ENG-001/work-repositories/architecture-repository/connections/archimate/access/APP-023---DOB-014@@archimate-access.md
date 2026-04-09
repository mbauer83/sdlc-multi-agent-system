---
artifact-id: APP-023---DOB-014@@archimate-access
artifact-type: archimate-access
source: APP-023
target: DOB-014
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: '2026-04-09'
---

<!-- §content -->

MementoStore (APP-023) reads and writes MementoState (DOB-014). save_memento_state() overwrites the single slot for (agent, phase); get_memento_state() retrieves it. Overwrite semantics — not accumulated.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
```

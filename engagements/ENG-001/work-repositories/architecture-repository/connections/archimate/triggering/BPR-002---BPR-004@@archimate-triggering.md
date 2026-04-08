---
artifact-id: BPR-002---BPR-004@@archimate-triggering
artifact-type: archimate-triggering
source: BPR-002
target: BPR-004
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
engagement: ENG-001
last-updated: 2026-04-05
---

<!-- §content -->

Skill Execution (BPR-002) directly triggers Gate Evaluation (BPR-004). After all specialist invocations for the sprint complete (BPR-203 emits specialist.completed for the last invocation), the PM immediately evaluates whether a phase gate is due.

<!-- §display -->

### archimate

```yaml
relationship-type: Triggering
direction: source-to-target
```

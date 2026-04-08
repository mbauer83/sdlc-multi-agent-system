---
artifact-id: BPR-002---BOB-006@@archimate-access
artifact-type: archimate-access
source: BPR-002
target: BOB-006
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
engagement: ENG-001
last-updated: 2026-04-05
---

<!-- §content -->

Skill Execution (BPR-002) accesses Learning Entry (BOB-006) with read-write access. At the start of each skill invocation, BPR-002 queries relevant learning entries (read); at the end of an invocation that triggers learning generation, BPR-002 writes a new entry.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-type: read-write
```

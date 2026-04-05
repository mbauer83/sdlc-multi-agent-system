---
artifact-id: BPR-002-C
artifact-type: business-process
name: "Emit Artifacts"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-002
stage-order: 3
---

<!-- §content -->

## Emit Artifacts

The specialist agent writes completed output artifacts to the work-repository, emits `artifact.created` / `artifact.updated` EventStore events, records any learning entries triggered by feedback or gate-veto conditions, and emits `specialist.completed` to signal the PM. This stage closes the skill execution cycle.

## Properties

| Attribute | Value |
|---|---|
| Input | Completed skill outputs (from BPR-002-B) |
| Output | Written artifact files; `artifact.created`/`updated` events; optional learning entry; `specialist.completed` event |
| Triggers | BPR-004 (Gate Evaluation) — PM receives specialist.completed and decides whether gate evaluation is due |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Emit Artifacts"
alias: BPR_002_C
```

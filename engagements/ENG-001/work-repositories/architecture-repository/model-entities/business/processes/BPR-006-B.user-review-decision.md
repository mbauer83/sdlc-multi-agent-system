---
artifact-id: BPR-006-B
artifact-type: business-process
name: "User Review Decision"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-006
stage-order: 2
---

<!-- §content -->

## User Review Decision

The user evaluates each artifact and marks it: approved / needs-revision (with optional agent tag and comment) / rejected. The user submits the review via the Dashboard, raising `review.submitted` (BEV-006). This is the collaborative stage within BIA-001 — neither PM nor User can close this stage alone.

## Properties

| Attribute | Value |
|---|---|
| Input | Dashboard Review tab with artifact list (from BPR-006-A); user evaluation |
| Output | `review.submitted` event (BEV-006); per-artifact decisions recorded |
| Flow-to | BPR-006-C (Process Review Decisions) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "User Review Decision"
alias: BPR_006_B
```

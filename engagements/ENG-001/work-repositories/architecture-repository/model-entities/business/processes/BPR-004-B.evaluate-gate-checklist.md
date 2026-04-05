---
artifact-id: BPR-004-B
artifact-type: business-process
name: "Evaluate Gate Checklist"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-004
stage-order: 2
---

<!-- §content -->

## Evaluate Gate Checklist

The PM applies the phase-specific gate checklist: verifies mandatory artifact presence, version states, CSCO sign-off, and that no veto has been cast. A single CSCO veto blocks the gate regardless of other votes. Deferred items are noted for the next sprint. The checklist result (pass / fail / defer) is determined here.

## Properties

| Attribute | Value |
|---|---|
| Input | Vote tally (from BPR-004-A); gate checklist for current phase; artifact status from model registry |
| Output | Gate evaluation result: pass / fail / defer; list of blocking items if not passing |
| Flow-to | BPR-004-C (Record Gate Outcome) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Evaluate Gate Checklist"
alias: BPR_004_B
```

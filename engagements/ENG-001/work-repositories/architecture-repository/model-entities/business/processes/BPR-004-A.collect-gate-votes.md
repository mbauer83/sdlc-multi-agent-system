---
artifact-id: BPR-004-A
artifact-type: business-process
name: "Collect Gate Votes"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-004
stage-order: 1
---

<!-- §content -->

## Collect Gate Votes

The PM agent solicits `gate.vote_cast` events from all required gate voters for the current phase transition. A CSCO vote is mandatory on every gate. Specialist agents cast votes as part of their skill completion steps. The PM waits until all required votes are received before proceeding.

## Properties

| Attribute | Value |
|---|---|
| Input | List of required voters for this phase gate; existing `gate.vote_cast` events in EventStore |
| Output | Complete set of `gate.vote_cast` events; vote tally (approved / veto / deferred) |
| Flow-to | BPR-004-B (Evaluate Checklist) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Collect Gate Votes"
alias: BPR_004_A
```

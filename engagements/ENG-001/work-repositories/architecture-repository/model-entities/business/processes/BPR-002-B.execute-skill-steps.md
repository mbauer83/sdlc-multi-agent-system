---
artifact-id: BPR-002-B
artifact-type: business-process
name: "Execute Skill Steps"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-002
stage-order: 2
---

<!-- §content -->

## Execute Skill Steps

The specialist agent iterates through the procedure steps defined in the skill file, calling tools, querying artifacts, and producing outputs. If a knowledge gap is found, the agent raises a CQ (sub-triggering BPR-003) and suspends until answered. If a safety condition is detected, an algedonic signal is raised (sub-triggering BPR-005). Control returns here after CQ resolution.

## Properties

| Attribute | Value |
|---|---|
| Input | Assembled execution context (from BPR-002-A) |
| Output | Intermediate artifacts; tool-call results; optional CQ raised (→ BPR-003); optional algedonic signal (→ BPR-005) |
| Flow-to | BPR-002-C (Emit Artifacts) |
| Sub-triggers | BPR-003 (CQ Lifecycle) when gap detected; BPR-005 (Algedonic Escalation) when safety condition detected |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Execute Skill Steps"
alias: BPR_002_B
```

---
artifact-id: BPR-003-A
artifact-type: business-process
name: "Route CQ to User"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-003
stage-order: 1
---

<!-- §content -->

## Route CQ to User

The PM agent receives the `cq.raised` event from the specialist, writes the ClarificationRequest (BOB-003) to the work-repository, batches it with any other open CQs, and surfaces the set on the Dashboard for the user. Blocking CQs suspend the invoking skill node; non-blocking CQs are flagged as assumptions and the skill continues.

## Properties

| Attribute | Value |
|---|---|
| Input | `cq.raised` event; CQ payload from raising specialist |
| Output | ClarificationRequest (BOB-003) written; Dashboard notification; skill node suspended (if blocking) |
| Flow-to | BPR-003-B (Await User Answer) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Route CQ to User"
alias: BPR_003_A
```

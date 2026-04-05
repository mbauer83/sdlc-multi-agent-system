---
artifact-id: BPR-008-B
artifact-type: business-process
name: "Infer Entities"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-008
stage-order: 2
---

<!-- §content -->

## Infer Entities

From the evidence corpus (BPR-008-A), the SA and SwA agents draft entity files for all identifiable business, application, and technology-layer elements. Each entity is annotated `[inferred: <source>]` rather than `[confirmed]`. Gap annotations are added where evidence is missing. Batched confirmation CQs are composed for the user.

## Properties

| Attribute | Value |
|---|---|
| Input | Annotated evidence corpus (from BPR-008-A) |
| Output | Draft entity files with `[inferred]` annotations; gap assessment; batched confirmation CQs |
| Flow-to | BPR-008-C (Confirm and Populate Model) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Infer Entities"
alias: BPR_008_B
```

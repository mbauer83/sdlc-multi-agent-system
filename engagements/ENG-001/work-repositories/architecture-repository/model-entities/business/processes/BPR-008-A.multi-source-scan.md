---
artifact-id: BPR-008-A
artifact-type: business-process
name: "Multi-Source Scan"
version: 0.1.0
status: draft
phase-produced: B
owner-agent: SA
safety-relevant: false
produced-by-skill: SA-PHASE-B
last-updated: 2026-04-05
engagement: ENG-001
parent-process: BPR-008
stage-order: 1
---

<!-- §content -->

## Multi-Source Scan

The SA and SwA agents scan all available evidence sources for the target system: source code structure, IaC manifests, CI/CD pipeline configurations, package dependency files, and any user-uploaded documents. Each scanned item is annotated with `[source: <source-id>]`. The scan produces a raw evidence corpus for entity inference.

## Properties

| Attribute | Value |
|---|---|
| Input | Target repository paths; user-uploaded documents; external source configs |
| Output | Annotated evidence corpus: technology fingerprint, structural observations, user-document extracts |
| Flow-to | BPR-008-B (Infer Entities) |

<!-- §display -->

### archimate

```yaml
layer: Business
element-type: BusinessProcess
label: "Multi-Source Scan"
alias: BPR_008_A
```

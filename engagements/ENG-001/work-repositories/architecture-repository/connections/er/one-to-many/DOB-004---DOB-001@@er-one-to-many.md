---
artifact-id: DOB-004---DOB-001@@er-one-to-many
artifact-type: er-one-to-many
source: DOB-004
target: DOB-001
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

One ClarificationRequest (DOB-004) produces many WorkflowEvents (DOB-001). A single CQ lifecycle generates at minimum two events: `cq.raised` (when the agent raises it) and `cq.answered` (when the user responds). Additional intermediate events may be emitted if the CQ is batched or re-routed.

<!-- §display -->

### er

```yaml
source-cardinality: "1"
target-cardinality: "1..*"
label: "produces"
```

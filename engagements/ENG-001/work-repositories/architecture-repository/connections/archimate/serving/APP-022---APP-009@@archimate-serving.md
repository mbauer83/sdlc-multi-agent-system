---
artifact-id: APP-022---APP-009@@archimate-serving
artifact-type: archimate-serving
source: APP-022
target: APP-009
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

TargetRepoManager (APP-022) serves SwA Agent (APP-009). SwA Agent calls `scan_target_repo` during SWA-REV-TA Discovery Scan Layer 4 to read technology stack evidence (package files, infrastructure configs, CI pipelines). Access is read-only.

<!-- §display -->

### archimate

```yaml
relationship-type: Serving
direction: source-to-target
```

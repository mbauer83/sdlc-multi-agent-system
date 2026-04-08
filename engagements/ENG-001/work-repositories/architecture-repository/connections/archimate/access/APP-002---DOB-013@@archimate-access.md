---
artifact-id: APP-002---DOB-013@@archimate-access
artifact-type: archimate-access
source: APP-002
target: DOB-013
version: 0.1.0
status: draft
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

ModelRegistry (APP-002) builds and maintains ArtifactRecord instances (DOB-013) as its in-memory index. At cold start, APP-002 scans all entity files in both engagement and enterprise repository paths and constructs one ArtifactRecord per file from frontmatter. At runtime, `list_artifacts()`, `get_entity()`, and `search_artifacts()` all operate on the ArtifactRecord collection without re-reading disk.

<!-- §display -->

### archimate

```yaml
relationship-type: Access
direction: source-to-target
access-mode: read-write
```

# Framework Knowledge Index and Retrieval

**Version:** 1.2.0  
**Status:** Implemented (Stage 5 partial)  
**Owner:** PM + SwA  
**Last Updated:** 2026-04-09

---

## 1. Problem Statement

Current guidance in several places implies broad pre-reading of framework documents. This is inefficient, increases context noise, and weakens runtime reliability.

Required shift:
- From: "read all framework docs first"
- To: "query-first, section-targeted retrieval with traceable evidence"

---

## 2. Goals and Non-Goals

### Goals

1. Focused agent context: retrieve only framework sections needed for the current task.
2. Strong discoverability: metadata + keyword + optional semantic search across framework docs.
3. Multi-surface access:
- Python API for orchestration/agent code.
- CLI for humans and debugging.
- MCP tools for runtime tool invocation.
4. Deterministic behavior: retrieval sequence is auditable and reproducible.
5. Backward compatibility: existing `read_framework_doc` usage remains valid while migrating to query-first tools.

### Non-Goals

1. Replacing skill files as primary runtime procedure payloads.
2. Replacing model/entity registries.
3. Creating a second source of truth for framework content.

---

## 3. Retrieval Model (Query-First)

Default retrieval sequence:

1. `list_framework_docs` with role/phase/topic filters.
2. `search_framework_docs` for specific rule lookup.
3. `read_framework_doc` for only the selected section(s), summary-first.
4. Escalate to full-document read only when summary evidence is insufficient.

Hard rule: no unconditional full-framework preload at skill start.

---

## 4. Index Architecture

### 4.1 Indexed Unit

Primary unit is a **section record**, not a whole file.

Each record:
- `doc_id`
- `path`
- `section_id` (heading-derived)
- `heading`
- `heading_path`
- `content_snippet`
- `tags`
- `owner`
- `phase_scope`
- `agent_scope`
- `updated_at`

### 4.2 Storage Tiers

1. In-memory metadata index (fast filter/list).
2. SQLite FTS5 section index (keyword + snippet ranking).
3. Optional semantic tier (`sqlite-vec`) for large corpora and fuzzy intent queries.

### 4.3 Freshness

1. Startup full scan of `framework/` and key planning specs (`specs/IMPLEMENTATION_PLAN.md`, `CLAUDE.md`, `README.md`).
2. Transparent auto-refresh via mtime polling watcher with bounded-latency stale detection.
3. TTL-triggered refresh guard as a safety net for missed file-change observations.
4. Optional caller-forced refresh (`refresh=True`) and CLI `refresh` for deterministic CI/debug runs.

### 4.4 Cross-Reference Graph Model

Framework retrieval index must also maintain a directed document graph:

- Node: document section (`doc_id`, `section_id`).
- Edge: explicit formal cross-reference from source section to target section/doc.
- Edge attributes: `ref_type`, `label`, `created_at`, `source_path`, `target_path`.

Graph queries should support:
- outbound refs (`neighbors_out`)
- inbound refs (`neighbors_in`)
- shortest path between sections
- impact set (reverse dependency traversal)
- orphan section detection (no inbound and no outbound refs)

Purpose: improve discoverability/navigation and let agents query dependency context instead of broad reading.

---

## 5. Tool Surfaces

### 5.1 Python API

Implemented module: `src/common/framework_query/`

Core interface:
- `list_docs(**filters) -> list[FrameworkDocRecord]`
- `search_docs(query: str, **filters) -> list[FrameworkSearchHit]`
- `read_doc(doc_id_or_path: str, section: str | None = None, section_id: str | None = None, mode: Literal["summary","full"] = "summary") -> str`
- `list_sections(doc_id_or_path: str) -> list[FrameworkSectionRecord]`
- `suggest_sections(doc_id_or_path: str, query: str, limit: int = 5) -> list[dict]`
- `related_docs(doc_id_or_path: str, limit: int = 5) -> list[FrameworkDocRecord]`
- `neighbors(doc_id_or_path: str, section: str | None = None, direction: Literal["out","in","both"] = "both") -> list[FrameworkRefEdge]`
- `trace_path(source_ref: str, target_ref: str, max_hops: int = 6) -> list[FrameworkRefEdge]`

### 5.2 CLI

Implemented command:
- `uv run python -m src.common.framework_query <stats|list|search|read|related|neighbors|path|refresh>`

### 5.3 MCP Tools

Implemented server and tools:
- Server: `sdlc-mcp-framework` (`src/tools/mcp_framework_server.py`)
- `framework_query_stats`
- `framework_query_list_docs`
- `framework_query_list_sections`
- `framework_query_search_docs`
- `framework_query_read_doc`
- `framework_query_resolve_ref`
- `framework_query_related_docs`
- `framework_query_neighbors`
- `framework_query_path`
- `framework_query_path_batch`
- `framework_query_missing_links`
- `framework_query_validate_refs`

MCP behavior mirrors Python API and uses the same index backend. Framework responses include freshness metadata for traceability and silent auto-refresh behavior. Canonical runtime inventory is tracked in `framework/tool-catalog.md`.

---

## 6. Runtime Guardrails

1. Query-first policy is mandatory for framework retrieval in phase-start and gate-evaluation workflows.
2. Full document reads require reason logging in tool call context.
3. Skill prose should reference framework docs by precise section when possible.
4. Retrieval should prefer role-scoped and phase-scoped filters to minimize token load.

---

## 7. Migration Plan

### Phase 1 (docs + planning)

1. Remove broad-read directives from AGENT and skill files.
2. Update discovery and runtime specs to query-first framework retrieval.
3. Add Stage 5 implementation tasks for framework index and tools.

### Phase 2 (implementation)

1. Build framework index backend and query API.
2. Add CLI.
3. Expose MCP tools.
4. Keep `read_framework_doc` as compatibility alias, internally routed through indexed resolver.
5. Parse formal cross-document references and build graph index.

### Phase 3 (adoption)

1. Update high-traffic skills to explicit section-based retrieval.
2. Add telemetry for retrieval patterns (summary vs full reads).
3. Tighten policy checks in lint/tests to prevent reintroduction of "read all framework docs" guidance.

---

## 8. Acceptance Criteria

1. No AGENT/skill file requires reading all framework docs at task start.
2. Framework retrieval tools support metadata list, search, and section read.
3. Python API, CLI, and MCP surfaces are all available.
4. Query-first retrieval path is documented in runtime and discovery specs.
5. Framework-doc access is auditable in event logs/tool traces.
6. Formal cross-reference graph is queryable (neighbors/path/impact queries).

---

## 9. Formal Cross-Reference Format

Framework/spec document references should use this canonical markdown pattern:

```
[@DOC:<doc-id>#<section-id>](<relative-path>#<anchor>)
```

Examples:
- `[@DOC:discovery-protocol#2-discovery-scan-procedure](framework/discovery-protocol.md#2-discovery-scan-procedure)`
- `[@DOC:agent-runtime-spec#6-1-universal-tools-all-agents](framework/agent-runtime-spec.md#6-1-universal-tools-all-agents)`

Conventions:
1. `doc-id` should match frontmatter `doc-id` where present; otherwise derived from filename stem.
2. `section-id` is heading-derived slug.
3. Prefer section-specific references over file-only references when guidance is normative.
4. Keep human-readable link text concise; structured `@DOC` token is for machine parsing.

This format enables deterministic graph extraction during indexing.

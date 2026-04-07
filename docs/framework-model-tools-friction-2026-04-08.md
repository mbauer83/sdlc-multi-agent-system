# Framework/Model MCP Tool-Surface Refinement (2026-04-08)

## Purpose

Refine friction observations into a concrete, best-practice target design for framework/model tool surfaces with three goals:
1. Usable: low-ambiguity behavior and predictable recovery paths.
2. Effective: correct answers without manual retries and ad-hoc fallbacks.
3. Efficient: minimal tool calls and bounded payload overhead.

## What Was Evaluated

Implementation and tests reviewed:
- `src/common/framework_query/index.py`
- `src/tools/framework_mcp/*`
- `src/tools/model_mcp/watch_tools.py`
- `tests/model/test_framework_query.py`
- `tests/tools/test_registry_asyncio_and_mcp_servers.py`

Validation run:
- `uv run pytest tests/model/test_framework_query.py tests/tools/test_registry_asyncio_and_mcp_servers.py`

## Key Findings

1. Framework query tools were query-capable but freshness-poor at evaluation time.
- Previous behavior was cache + manual refresh (`framework_query_stats(refresh=True)` or CLI refresh).
- Current implementation now provides transparent freshness via background mtime polling + TTL stale detection, without requiring agent-managed watch/start/stop calls.

2. Path traversal has weak diagnostics.
- Empty path results and unknown refs are hard to distinguish from stale index or disconnected graph.

3. Section-id ergonomics are functional but not resilient under active edits.
- Deterministic `section_id` exists, but path calls remain brittle for newly edited headings unless index freshness is guaranteed.

4. Test coverage confirms current behavior, not requirement parity.
- Existing tests cover indexing/search/read/path basics and manual refresh paths.
- No tests enforce automatic framework index updates via watch/scheduled mechanisms.

## Best-Practice Design Principles

1. Freshness should be transparent by default across query surfaces.
2. Diagnostics should explain failure class, not just fail/empty.
3. Keep APIs lean: minimal knobs, strong defaults, deterministic outputs.
4. Test behavior contracts, not only happy-path function outputs.

## Refined Recommendations (Optimized Surface)

### P1 - Freshness Parity with Model Tools

1. Implement transparent freshness in the framework index context (no agent action required):
- mtime fingerprint + TTL invalidation in framework index context.
- Auto-refresh on first stale hit, then continue with cached mode.

2. Wire silent background freshness updates:
- Use internal watcher/scheduled checks managed by server lifecycle, not caller-invoked tooling.
- Agent-facing query calls remain unchanged and do not require extra freshness flags.

### P1 - Path/Graph Explainability Without API Bloat

3. Extend `framework_query_path` response with optional diagnostics block (default off):
- `include_diagnostics: bool = False`
- when true: `source_exists`, `target_exists`, `reason_code`, `suggested_source_refs`, `suggested_target_refs`, `index_age_ms`.

4. Standardize empty-path reason codes:
- `DISCONNECTED_GRAPH`
- `UNKNOWN_SOURCE_REF`
- `UNKNOWN_TARGET_REF`
- `INDEX_STALE_OR_UNREFRESHED`

### P1 - Section-ID Usability and Recovery

5. Add deterministic ref resolution helper:
- `framework_query_resolve_ref(doc_id_or_path, ref_hint)` -> canonical `doc#section` + confidence + alternatives.

6. Keep `read_doc` error payload structured and consistent across all unknown-section/ref failures.

### P2 - Efficiency and Operator UX

7. Add batch path endpoint for planning workflows:
- `framework_query_path_batch(pairs=[...])` returns per-pair status and optional diagnostics.

8. Add compact response mode for large searches:
- Minimal fields by default for search/list in tool-agent contexts.

### P2 - Graph Hygiene Support

9. Add link-quality helpers:
- `framework_query_missing_links(doc_id)` for low-connectivity sections.
- `framework_query_validate_refs(doc_id_or_path=None)` for unresolved `@DOC` targets.

## Implementation Plan (Small Safe Increments)

### Slice A (highest value)

1. Implement server-managed auto-refresh (TTL + mtime invalidation + background watcher/poller).
2. Expose freshness metadata in existing framework query responses (for traceability), not control burden.
3. Update `framework/tool-catalog.md` to reflect transparent freshness guarantees and diagnostics behavior.

### Slice B

4. Add `framework_query_resolve_ref`.
5. Add `framework_query_path(include_diagnostics)` with reason codes.

### Slice C

6. Add batch path and link-hygiene helpers.

## Test Plan (Required for Requirement Compliance)

1. Transparent freshness tests:
- file changes become discoverable without explicit refresh calls
- cache invalidation/refresh occurs automatically within bounded latency

2. Auto-refresh integration tests:
- modify framework doc without manual refresh
- verify section discoverability and path behavior updates automatically

3. Freshness observability tests:
- response metadata exposes index age/version/last-refresh for debugging
- diagnostics distinguish stale-index class from unknown/disconnected refs

4. Diagnostics contract tests:
- unknown source/target refs return stable reason codes and suggestions

5. Compatibility tests:
- existing non-diagnostics callers receive unchanged response shape by default

## Current Operational Guidance

1. Use `framework_query_search_docs` + `framework_query_read_doc(section_id=...)` as primary discovery path.
2. Use explicit `refresh=True` only for deterministic debugging/CI or when investigating freshness edge cases.
3. Continue adding reciprocal formal `@DOC` references for cross-contract sections.

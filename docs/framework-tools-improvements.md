# Framework MCP Tooling Improvements (Discovery Feedback)

Date: 2026-04-08
Scope: Query-first discovery for framework/spec and model repositories

## Evaluation Outcome (2026-04-08)

Status: implemented and validated with targeted tests + BDD updates.

Implemented tool/API changes:

1. Stable section addressing in framework reads
- `framework_query_read_doc` now accepts `section_id` (preferred deterministic selector).
- `framework_query_list_sections(doc_id_or_path)` added, returning `section_id`, heading, line range, and level.

2. Type-prioritized model search controls
- `model_query_search_artifacts` now supports `prefer_record_type` and `strict_record_type`.
- Prioritization uses deterministic type-first ordering when `prefer_record_type` is set.

3. Compact projection mode for list/search
- `model_query_list_artifacts` and `model_query_search_artifacts` now support `fields=[...]` projection.
- This reduces large payload overhead for inventory-style tasks.

4. Direct aggregate endpoint
- `model_query_count_artifacts_by(group_by=artifact_type|diagram_type|phase_produced|owner_agent)` added.

5. Unknown-section helper behavior
- On unknown section, `framework_query_read_doc` now returns an error payload with `suggested_sections` (nearest section-id candidates).

Validation run:
- `uv run pytest tests/model/test_framework_query.py tests/model/test_model_query.py tests/tools/test_registry_asyncio_and_mcp_servers.py tests/tools/test_model_query_mcp_improvements.py`
- Result: all tests passing.

## Additional Outcome (2026-04-09)

Status: implemented and validated for framework MCP path/ref/freshness improvements.

Implemented additions:

1. Transparent framework-index freshness
- Framework MCP context now performs silent auto-refresh using mtime polling + TTL stale detection.
- Freshness metadata now returned with framework read/graph responses (`index_version`, `last_refresh_at`, `index_age_ms`, `stale_detected`, `auto_refreshed`).

2. Ref/path usability and diagnostics
- Added `framework_query_resolve_ref(doc_id_or_path, ref_hint)` to resolve canonical `doc#section_id` refs.
- Added `framework_query_path(include_diagnostics=true)` with reason codes and suggestion hints.
- Added `framework_query_path_batch(pairs=[...])` for batched traversal.

3. Graph hygiene helpers
- Added `framework_query_missing_links(...)` for low-connectivity section discovery.
- Added `framework_query_validate_refs(...)` for unresolved `@DOC` target checks.

Validation run:
- `uv run pytest tests/tools/test_framework_mcp_tool_improvements.py tests/tools/test_registry_asyncio_and_mcp_servers.py`
- Result: all tests passing.

## Observed Friction

1. Section addressing is brittle when headings are long or contain punctuation.
- `framework_query_read_doc(section=...)` often fails if the exact heading text is not matched.
- Practical impact: extra `search_docs` round-trips just to recover section IDs.

2. Search ranking can be noisy for metadata-like queries.
- Queries such as `diagram-type: activity-bpmn` returned many entity hits before the diagram hit.
- Practical impact: harder to quickly answer inventory questions (for example, how many activity diagrams exist).

3. Large responses are redirected to generated temp JSON files.
- This is workable but introduces extra manual file reads for routine usage.
- Practical impact: more tool calls for common exploratory tasks.

4. Some summary reads return only headings with no section body when structure is sparse.
- Example pattern: section summary with just heading text required fallback to filesystem read.
- Practical impact: summary-first workflow sometimes degrades into direct file read.

## Suggested Improvements

1. Add stable section addressing by `section_id` as a first-class `read_doc` input.
- Keep text-heading addressing as convenience, but make `section_id` preferred and deterministic.

2. Add type-prioritized search controls for model queries.
- Example options: `prefer_record_type=diagram`, `strict_record_type=true`, or weighted ranking by record type.

3. Add compact projection mode for large list/search results.
- Example: `fields=[artifact_id,path,diagram_type,phase_produced]` with no snippets.
- Goal: avoid temp-file detours for inventory tasks.

4. Add direct aggregate endpoints for common discovery questions.
- Examples:
  - `model_query_count_artifacts_by(artifact_type, diagram_type, phase_produced, owner_agent)`
  - `framework_query_list_sections(doc_id)` returning `{section_id, heading, line_start}`.

5. Add a quick-reference error helper in framework tools.
- On unknown section, return nearest section IDs by similarity (not only a hard failure).

## Priority Recommendation

1. `read_doc` by `section_id` and section listing endpoint.
2. Model search record-type prioritization/strict filtering.
3. Compact field projection mode for list/search.
4. Aggregate count endpoints.

## Amendments From Initial Proposal

- For search ranking, the implemented behavior is deterministic type-priority ordering under `prefer_record_type` (rather than only score-weighting). This better matches discovery workflows where record-type intent is explicit.
- For unknown sections, the MCP read tool returns structured error + suggestions without throwing, to avoid extra recovery calls in agent/tool loops.

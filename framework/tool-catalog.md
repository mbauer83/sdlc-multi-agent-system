# Tool Catalog (Authoritative)

**Version:** 1.2.0
**Status:** Approved
**Owner:** PM + SwA
**Last Updated:** 2026-04-08

---

## 1. Purpose

This file is the central, authoritative catalog of runtime tools provided by this repository.

Scope:
1. MCP tool surfaces implemented in code under `src/tools/`.
2. Canonical tool names and behavior intent.
3. Where each tool family is registered.

If this catalog conflicts with narrative docs, this catalog and code registration are authoritative.

---

## 2. Servers

| Server Script | Python Entry | Transport Defaults | Purpose |
|---|---|---|---|
| `sdlc-mcp-model` | `src.tools.mcp_model_server:main` | streamable-http / stdio | ERP v2.0 model query, graph traversal, verifier, deterministic writers |
| `sdlc-mcp-registry` | `src.tools.mcp_registry_server:main` | streamable-http / stdio | Agent/skill registry discovery and runtime metadata retrieval |
| `sdlc-mcp-framework` | `src.tools.mcp_framework_server:main` | streamable-http / stdio | Query-first framework/spec lookup and formal reference graph traversal |

---

## 3. Model MCP Tools

Registration: `src/tools/model_mcp/`

### 3.1 Query

- `model_query_stats`: repository index stats (entities/connections/diagrams)
- `model_query_list_artifacts`: metadata list with filters + optional compact projection via `fields`
- `model_query_search_artifacts`: ranked text search with record-type controls (`prefer_record_type`, `strict_record_type`) + optional compact projection via `fields`
- `model_query_count_artifacts_by`: aggregate counts grouped by `artifact_type | diagram_type | phase_produced | owner_agent`
- `model_query_read_artifact`: summary/full artifact read
- `model_query_find_connections_for`: inbound/outbound connection records for entity
- `model_query_find_neighbors`: hop-bounded graph traversal

### 3.2 Verification

- `model_verify_file`: verify one entity/connection/diagram file
- `model_verify_all`: verify all model files under selected scope

### 3.3 Writer

- `model_write_help`: authoritative type conventions and write guidance
- `model_create_entity`: deterministic entity file create/update
- `model_create_connection`: deterministic connection file create/update
- `model_create_diagram`: deterministic PUML diagram file create/update
- `model_create_matrix`: deterministic matrix diagram markdown create/update

### 3.4 Watch/Refresh

- `model_tools_refresh`
- `model_tools_watch_start`
- `model_tools_watch_status`
- `model_tools_watch_stop`

---

## 4. Registry MCP Tools

Registration: `src/tools/mcp_registry_server.py` + `src/tools/mcp_registry/service.py`

- `list_agents`: discover valid agent IDs (dirs with `AGENT.md`)
- `load_agent_identity`: parse runtime identity payload from `AGENT.md`
- `list_agent_skills`: list skill IDs for one agent
- `list_skill_triggers`: trigger metadata scan over skills
- `get_skill_details`: runtime frontmatter + runtime sections from skill file
- `check_skill_readiness`: compare provided input keys against skill Inputs Required table

---

## 5. Framework MCP Tools

Registration: `src/tools/framework_mcp/`

### 5.1 Discovery and Read

- `framework_query_stats`: framework/spec index counts
- `framework_query_list_docs`: metadata list by owner/tag/path-prefix
- `framework_query_list_sections`: section inventory by doc (`section_id`, heading, line range)
- `framework_query_search_docs`: ranked section-level search with snippets
- `framework_query_read_doc`: summary/full read by doc + optional `section` or deterministic `section_id`; unknown section returns nearest section-id suggestions
- `framework_query_resolve_ref`: resolve a reference hint to canonical `doc#section_id` with confidence and alternatives
- `framework_query_related_docs`: document affinity from formal references

### 5.2 Graph Exploration (analogous to model graph tools)

- `framework_query_neighbors`: inbound/outbound `@DOC` edges for doc/section
- `framework_query_path`: shortest path between section refs (`doc#section`) with optional diagnostics
- `framework_query_path_batch`: batched shortest-path traversal with per-pair status/diagnostics
- `framework_query_missing_links`: sections with low/no formal graph connectivity
- `framework_query_validate_refs`: unresolved `@DOC` target validator

### 5.3 Freshness Behavior

- Framework index freshness is managed transparently by the server context (mtime + TTL invalidation plus background polling).
- Query tools may expose `freshness` metadata (`index_version`, `last_refresh_at`, `index_age_ms`, `stale_detected`, `auto_refreshed`) for observability.
- Manual refresh controls remain compatibility behavior (for example stats `refresh=true`) and are not required in normal agent query flow.

Graph model:
- Node: framework/spec section
- Edge: formal cross-reference `[@DOC:<doc-id>#<section-id>](<relative-path>#<anchor>)`

---

## 6. Naming and Compatibility

1. Canonical runtime names are exactly the names listed in this catalog.
2. Incoming names may be normalized by separator suffix extraction (`-`, `:`, `.`, `/`) when bridges namespace tools.
3. AGENT/skill markdown tool mentions are intent guidance; runtime callable surface is code-owned.

---

## 7. Change Control

When adding/removing/changing tools:
1. Update code registration and tests first.
2. Update this catalog in the same change.
3. Update relevant MCP config files (`.mcp.json`, `.vscode/mcp.json`) if server inventory changes.

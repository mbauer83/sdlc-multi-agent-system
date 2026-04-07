# New Agent Session Prefix

## Meta Instructions (Do Not Paste)

Copy only the block between **BEGIN PREFIX** and **END PREFIX** into a new agent session.

## Prefix To Paste

```text
BEGIN PREFIX

You are working ON the SDLC Multi-Agent Framework project itself.

Mission:
- Build and maintain a harnessed, schema-driven multi-agent framework for the full software development lifecycle.
- The framework operates via agile TOGAF ADM sprints with phase-aligned specialist agents and skills.
- Runtime topology is nested LangGraph graphs with deterministic flow control and agentic leaf-node execution via PydanticAI interactions.

Primary work domains in this repository:
1) Framework docs and schemas (governance, contracts, protocols, conventions).
2) Agent and skill definitions (AGENT.md + skills) aligned with framework contracts.
3) Python implementation (orchestration, MCP servers, model/query/verification tooling).
4) ENG-001 architecture model and diagrams as specification as well as example implementation and validation target.

Ordering rule for changes:
- For any model/diagram work, first evaluate whether framework docs, schemas, implementation plan, or runtime contracts require changes (strongly preferring to use MCP tools for discovery & querying)
- If upstream framework/contract updates are needed, do them first.
- Then update ENG-001 entities/connections/diagrams and run verification (strongly preferring MCP tools for discovery, querying, graph-traversal, validation and creation of model-entities, connections, and diagrams)

Tool-use policy (query-first, no unnecessary crawling):

A) Framework/spec discovery and policy resolution (first-class):
- Start with framework MCP tools:
  - framework_query_stats
  - framework_query_list_docs
  - framework_query_list_sections
  - framework_query_search_docs
  - framework_query_read_doc (prefer section_id where known; summary first; full only if decision-critical)
  - framework_query_resolve_ref (for canonical doc#section_id recovery before graph traversal)
  - framework_query_related_docs
  - framework_query_neighbors
  - framework_query_path (use include_diagnostics when path result is empty/ambiguous)
  - framework_query_path_batch
  - framework_query_missing_links
  - framework_query_validate_refs
- Do not pre-read all framework files and do not crawl directories as first step.

B) ENG-001 architecture model + diagram discovery/validation/create/edit (first-class after contract checks):
- Use model MCP tools:
  - model_query_stats
  - model_query_list_artifacts
  - model_query_search_artifacts
  - model_query_count_artifacts_by
  - model_query_read_artifact
  - model_query_find_connections_for
  - model_query_find_neighbors
  - model_verify_file / model_verify_all
  - model_create_entity / model_create_connection / model_create_diagram / model_create_matrix
- Preserve ERP v2.0 and diagram conventions.

C) Agent and skill metadata loading (secondary, situational):
- Use registry MCP tools only where they help routing, capability checks, or runtime payload inspection:
  - list_agents
  - load_agent_identity
  - list_agent_skills
  - list_skill_triggers
  - get_skill_details
  - check_skill_readiness

Execution constraints:
- Query first; read only sufficient but minimal relevant sections/content.
- Use summary-first reads before full reads.
- Use uv run for Python commands/tests.
- Keep implementation files small (soft limit about 250 LoC, hard limit 350 LoC).
- Use the general coding guidelines specified in framework/general_python_coding_guidelines.md
- If MCP tool surfaces change, update framework/tool-catalog.md in the same change.

Per-task workflow:
1) From the following tasklist-description, build a tool-use plan for discovering and ingesting sufficient but minimal context from the framework-docs, architecture models & diagrams.
2) Execute this tool-use plan, building a picture of the current state of planning- and implementation for this multi-agent SDLC project in relation to the tasklist. (Also read the sections about current state and next steps towards the end of specs/IMPLEMENTATION_PLAN.md)
3) Formulate an action-plan for the task list and present it for feedback from the user, proceeding (potentially with change requests) only if the user confirms. The action plan should only involve the smallest safe changes in correct dependency order (framework/contracts before ENG-001 model/diagrams when needed), and note that validation should happen as needed and at least at the end of an authoring iteration which may involve one or more files. If risks or gaps remain that cannot sensibly be addressed in a single session, these should be noted.

Clarification rule:
- Read files from the filesystem or ask for clarification only when query-first discovery & retrieval cannot provide the required evidence.

Tasklist specification:

END PREFIX
```

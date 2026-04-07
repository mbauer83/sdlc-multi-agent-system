# Wave Continuation Plan (Post-Wave-2)

Date: 2026-04-08

## 1. Purpose

Continue from the now-completed contract waves with two immediate priorities:
1. framework MCP freshness/usability parity with model MCP tooling,
2. completion of remaining ENG-001 Stage 4.9f workflow sequence diagrams.

## 2. Current Status Snapshot

Completed:
- Wave 0: baseline contract alignment.
- Wave 1: clarification/coordination taxonomy and routing semantics.
- Wave 2: nested subgraph decomposition and implementation-oriented checklists.

Active remaining work:
- Framework MCP tooling parity for automatic index updates and path-query usability.
- Wave 3 ENG-001 workflow model/diagram completion.

## 3. Scope Boundaries

1. Keep object-level architecture representation rules in diagram conventions only:
- `framework/diagram-conventions.md` governs governed-project architecture artifacts.

2. Keep meta-level SDLC workflow semantics in runtime-contract docs only:
- `framework/orchestration-topology.md`
- `framework/clarification-protocol.md`
- `specs/IMPLEMENTATION_PLAN.md`

3. Keep query-first discovery discipline for policy resolution and model authoring.

## 4. Remaining Work Slices

### Slice A: Framework MCP Freshness and Path-Usability Parity

Goal:
- Ensure framework tools auto-refresh indexes (watchers/scheduled fallback) and provide usable path diagnostics.

Primary targets:
- `src/tools/framework_mcp/`
- `src/common/framework_query/`
- `tests/model/test_framework_query.py`
- `tests/tools/test_registry_asyncio_and_mcp_servers.py` (and/or new framework MCP watch tests)
- `framework/tool-catalog.md`
- `docs/framework-model-tools-friction-2026-04-08.md`

Planned outputs:
1. Framework watch/refresh surface aligned with model tool ergonomics.
2. Deterministic freshness behavior for framework query endpoints.
3. Path diagnostics (reason codes + suggestions) for unknown/disconnected refs.
4. Tests validating automatic index update behavior after file changes.

Acceptance criteria:
- Framework index freshness can be maintained without manual stats-refresh steps.
- Newly edited framework sections become queryable in the same authoring session.
- Path failures are diagnosable (unknown ref vs disconnected graph vs stale index).
- Tool catalog reflects any surface changes.

### Slice B: Wave 3 ENG-001 Workflow Model/Diagram Completion

Goal:
- Complete remaining Stage 4.9f sequence diagrams aligned with the updated runtime contracts.

Primary targets:
- `engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/`
- `engagements/ENG-001/work-repositories/architecture-repository/connections/`
- `engagements/ENG-001/work-repositories/architecture-repository/model-entities/` (only if missing backing entities are found)
- `specs/IMPLEMENTATION_PLAN.md`

Planned outputs:
1. Complete missing business workflow activity/BPMN diagrams:
- `phase-g-activity-skill-invocation-v1.puml`
- `phase-c-activity-cq-lifecycle-v1.puml`
- `phase-c-activity-sprint-review-v1.puml`
2. Validate event/routing alignment against Wave 2 contracts.
3. Add/update matrix artifact(s) only if edge density requires traceability support.

Acceptance criteria:
- `model_verify_all` returns 0 errors and 0 warnings.
- Diagram sources and rendered outputs are synchronized in canonical locations.
- Stage 4.9f status in implementation plan is updated with concrete completion evidence.

## 5. Dependency Order (From Here)

Execute in this order:
1. Slice A framework-tooling parity (if any runtime/tool surface changes are needed).
2. Slice B ENG-001 model/diagram completion.
3. Verification and rendering sync.
4. Implementation plan and orientation docs update.

## 6. Restart Procedure

1. Confirm next target slice (`A` or `B`).
2. Query current state first with MCP tools:
- framework stats/list/search/read/path tools,
- model stats/list/search/read/verify tools.
3. Apply smallest safe change batch for that slice.
4. Validate at slice boundary:
- diagnostics for touched files,
- `model_verify_all` for ENG-001 model work,
- targeted tests for tooling surface changes.
5. Record completion evidence in `specs/IMPLEMENTATION_PLAN.md` current-state section.

## 7. Immediate Next Pickup

Recommended next slice: `Slice A` (framework MCP freshness/path usability parity), then `Slice B`.

Reason:
- It removes remaining tooling friction before heavy Wave 3 authoring,
- It reduces failed/ambiguous tool calls during ENG-001 completion work.

## 8. High-Value Formal References

- [@DOC:orchestration-topology#2-8-subgraph-decomposition-matrix-wave-2](../framework/orchestration-topology.md#28-subgraph-decomposition-matrix-wave-2)
- [@DOC:orchestration-topology#2-9-deterministic-vs-agentic-checklist-per-workflow-unit-wave-2](../framework/orchestration-topology.md#29-deterministic-vs-agentic-checklist-per-workflow-unit-wave-2)
- [@DOC:orchestration-topology#2-10-minimal-stage-5-node-and-routing-implementation-checklist-wave-2](../framework/orchestration-topology.md#210-minimal-stage-5-node-and-routing-implementation-checklist-wave-2)
- [@DOC:IMPLEMENTATION_PLAN#5c-orchestration-layer](../specs/IMPLEMENTATION_PLAN.md#5c--orchestration-layer)

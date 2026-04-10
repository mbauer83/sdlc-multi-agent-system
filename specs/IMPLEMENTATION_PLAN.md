# SDLC Multi-Agent System — Implementation Plan

## Vision & Overall Goal

This project builds a **multi-agent AI system** that operationalises the full Software Development Lifecycle (SDLC) through a suite of specialised Claude-based agents, each embodying a distinct professional role, each equipped with role-specific skills scoped to the TOGAF ADM phases relevant to that role.

The system is designed to assist (and partially automate) the end-to-end journey from market analysis and product ideation through architecture, implementation, deployment, and operational change management — with safety and compliance woven in at every phase as a first-class concern.

---

## Ontology & Conceptual Framework

### Agents as Role-Bounded Control Systems

Each agent is modelled as a **cybernetic control unit** in the sense of Stafford Beer's Viable System Model: it has a defined purpose, defined inputs and outputs, and defined channels of communication upward (reporting, escalation), downward (direction, feedback), and laterally (peer collaboration). No agent has unbounded authority — every agent operates within a mandate defined by its AGENT.md and enforced by the interaction protocols in its skill files.

The **algedonic channel** — a concept taken directly from VSM — is the fast-path escalation signal that bypasses normal hierarchical processing when time-criticality or risk severity demands immediate response. This is formalised in `framework/algedonic-protocol.md` and referenced in every skill file's `## Algedonic Triggers` section.

### The TOGAF ADM as Workflow Backbone

The **TOGAF Architecture Development Method (ADM)** provides the phase structure:

| Phase | Focus |
|---|---|
| Preliminary | Framework setup, principles, repository initialisation |
| A — Architecture Vision | Scope, stakeholders, high-level solution concept, safety envelope |
| B — Business Architecture | Business processes, capabilities, motivation, value streams |
| C — Information Systems Architecture | Application + Data architecture (logical) |
| D — Technology Architecture | Concrete technology stack, infrastructure, platform |
| E — Opportunities & Solutions | Implementation candidates, gap analysis, build vs buy |
| F — Migration Planning | Roadmap, sequencing, dependency resolution |
| G — Implementation Governance | Development, testing, deployment oversight |
| H — Architecture Change Management | Change impact assessment, continuous improvement |
| Requirements Management | Cross-phase, continuous — feeds all other phases |

These phases are run in **Agile ADM** cadence: time-boxed Architecture Sprints producing phase artifacts, feeding Delivery Sprints for implementation, with explicit iteration and phase-transition gates. This cadence is fully specified in `framework/agile-adm-cadence.md`.

### Agent Roles and Phase Coverage

Nine agent roles are defined. No agent covers all phases — each has a primary set of phases and a consulting set. The full RACI matrix is in `framework/raci-matrix.md`. Summary:

| Agent | Primary Phases | Consulting Phases |
|---|---|---|
| Sales & Marketing Manager | A | Req-Mgmt |
| Product Owner | Prelim, A, B, H | C, E, Req-Mgmt |
| Solution Architect | A, B, H | C (traceability review), D, E, Req-Mgmt |
| Software Architect / Principal Engineer | C, D, E, F, G, H (app/tech) | A |
| DevOps / Platform Engineer | D, E, F, G | — |
| Implementing Developer | G | E, F, Req-Mgmt feedback |
| QA Engineer | E/F (test planning), G | H |
| Project Manager | Prelim, A, E, F, G, H | All (coordination) |
| Chief Safety & Compliance Officer | A, B, C, D, G, H | All (gate reviews) |

### Repository Ownership

Work-repositories are role-owned, version-controlled, and path-governed. No agent writes outside its designated paths. Cross-role artifact transfer occurs through defined handoff events, not ad-hoc file sharing.

| Repository | Owner | Contents |
|---|---|---|
| `architecture-repository/` | SA (motivation/strategy/business layers) + SwA (application layer — Phase C) | Architecture Vision, Business Architecture, App/Data Architecture entities (SwA-primary), principles, ADRs |
| `technology-repository/` | Software Architect/PE | Technology Architecture, implementation plans, coding standards, ADRs, solutions inventory |
| `project-repository/` | Project Manager | Sprint plans, schedules, decision log, lessons learned, knowledge base |
| `safety-repository/` | CSCO | STAMP/STPA analyses, safety constraints, compliance checklists, incident records |
| `delivery-repository/` | Implementing Developer | Feature branches, PRs (draft and final), unit test reports |
| `qa-repository/` | QA Engineer | Test strategies, test cases, execution reports, defect records |
| `devops-repository/` | DevOps/Platform Engineer | IaC, pipeline definitions, environment configs, deployment records |

### Artifact Retrieval Protocol (Confidence-Threshold)

Every skill that consumes an artifact from another role's repository must apply the following rule:

- **High confidence** that the artifact summary is sufficient to fulfil the current task → use the summary header only (≈200–400 tokens)
- **Confidence below threshold** (detail is needed for correctness, the task involves producing a binding output, or an inconsistency is detected) → retrieve and read the full artifact, log the retrieval reason

This protocol is formalised in `framework/repository-conventions.md`.

### Knowledge Self-Assessment and Clarification Protocol

Every agent must continuously monitor whether it has sufficient knowledge to produce correct outputs. When domain-specific facts about the user's situation are absent from all available artifacts and cannot safely be assumed, the agent raises a **Clarification Request (CQ)** rather than proceeding silently. CQs are:
- Structured, specific, and actionable (not open-ended)
- Routed to the appropriate party (user, PM, or producing agent)
- Tracked as sprint blockers by the PM when `blocking: true`
- Batched by the PM for efficient user interaction

The work suspension and resumption rules, CQ format, routing logic, and skill file requirements are fully specified in `framework/clarification-protocol.md`.

### SDLC Entry Points

The system supports seven engagement entry points, from cold-start (EP-0) to change management (EP-H). Users may bring existing documents, designs, codebases, or change requests, and the system will ingest, validate, and warm-start from that material rather than re-doing work already done. Entry procedures, warm-start artifact production, gap assessment, and the Entry Assessment Report format are specified in `framework/sdlc-entry-points.md`.

### Algedonic Protocol

Certain conditions require bypassing normal communication topology and escalating immediately. The algedonic protocol defines:
- Trigger classification (safety-critical, regulatory breach, timeline collapse, unresolvable inter-agent conflict)
- Escalation targets per trigger class
- Simplified "failsafe" decision structures for short time-horizon situations
- Re-integration into normal topology after algedonic event resolution

### Feedback Loops

Every inter-agent handoff supports a bounded feedback cycle:
- **Maximum two iterations** (initial output + one revision) before escalation to PM
- Feedback is structured (template-based), not free-form prose
- Retrospective feedback (all roles → PM knowledge base → skill/process updates) is a separate, lower-frequency loop triggered at sprint boundaries

---

## Technology Stack

### Python Coding Standards

All Python implementation (`src/`) must follow the canonical guidelines in `framework/general_python_coding_guidelines.md`.

This includes type-system rules, style constraints, error-handling policy, domain-centred layering, and ports-and-adapters requirements.

- **Runtime:** Python 3.12+ (required for PEP 695 inline type parameter syntax — `def f[T](...)`), Pydantic v2 for all data models, artifact schemas, and event payloads
- **Orchestration:** LangGraph (primary control plane) with nested subgraphs for lifecycle, engagement-type, and phase flows; deterministic routing and resumable state transitions
- **LLM backend:** Configurable LLM provider via `LLMConfig` (`src/models/llm_config.py`); uses PydanticAI `provider:model-id` string convention (e.g. `anthropic:claude-sonnet-4-6`, `openai:gpt-4o`, `ollama:llama3.1`); default primary `anthropic:claude-sonnet-4-6`, routing `anthropic:claude-haiku-4-5`; provider SDKs are optional extras in `pyproject.toml`
- **Leaf reasoning engine:** PydanticAI at leaf nodes only (schema-constrained specialist execution and tool use)
- **Version control:** Git (all agent definitions, skill files, framework documents, and work-repository schemas are tracked)
- **Artifact persistence:** File-based work-repositories (git-tracked) per engagement under `engagements/<id>/work-repositories/`
- **Workflow state persistence:** SQLite event store (`engagements/<id>/workflow.db`) — **canonical, git-tracked**; Pydantic-validated, append-only, managed by the `EventStore` class in `src/events/`; YAML projection in `engagements/<id>/workflow-events/` also git-tracked for human readability and PR review; schema managed by Alembic migrations
- **Enterprise architecture persistence:** `enterprise-repository/` (embedded) or external EA system via source adapter; configurable via `enterprise-repository-config.yaml`
- **External source adapters:** Read-only, configured in `external-sources/<source-id>.config.yaml`; supports Confluence, Jira, external Git, SharePoint, and generic REST APIs
- **Target project repositories (multi-repo support):** Engagements may register one or more target repositories in `engagements-config.yaml`. The `target-repositories` list (or backward-compatible singular `target-repository`) associates each repo with an `id`, `label`, `role` (microservice | microfrontend | bff | event-store | shared-lib | infrastructure | api-gateway | data-platform | shared-schema | monolith), and `domain` (bounded context). Local clones live at `engagements/<id>/target-repos/<repo-id>/` (.gitignored). Multi-repo engagements require a `repository-map.md` artifact; see `framework/artifact-schemas/repository-map.schema.md`. The `delivery-repository/` holds delivery metadata (PR records, branch refs, test reports) per repo, not code.

---

## Planning & Implementation Stages

### Stage 1 — Foundation Artifacts (Complete)

- [x] **Scaffold repository directory structure**

---

### Stage 2 — Project Manager Master Skill (Complete)

Every AGENT.md must include: role mandate, phase coverage, repository ownership, entry point behaviour (per EP-0 through EP-H), and cross-references to all skill files.  
Every skill file must include: `## Inputs Required`, `## Knowledge Adequacy Check`, `## Algedonic Triggers`, `## Feedback Loop`, and `## Outputs`.

---

### Stage 3 — Primary Implementation Chain (in phase order)

---

### Stage 4 — Framing Layer Agents (Mostly planning & documentation)

### Stage 4.5 — Cross-Cutting Framework Extensions (Complete)
#### 4.5a — Diagram Conventions Framework (Complete)
#### 4.5b — Artifact Reference Format Extension (Complete)
#### 4.5c — Diagram-Aware Discovery Protocol Extension (Complete)
#### 4.5d — Coding Guidelines and Standards Discovery Protocol (Complete)
#### 4.5e — Agent Profile Condensation: Layer 1 / Layer 2 Design (Complete)
#### 4.5f — Retroactive Diagram and Reference Updates to Existing Skill Files (Complete)

---

### Stage 4.6 — Learning Protocol (Reflexion-Inspired Agent Memory) (Complete)
#### 4.6a — Framework Documents (Complete)
#### 4.6b — Retroactive Skill File Patches (Complete)
#### 4.6c — Python Tooling (deferred to Stage 5b)

Implemented alongside other `universal_tools.py` additions in Stage 5b:

- [ ] `src/tools/universal_tools.py` — add `query_learnings()` and `record_learning()` (spec below; see also Stage 5b tool list)
- [x] `src/models/learning.py` — `LearningEntry` Pydantic model (fields: `learning_id`, `agent`, `phase`, `artifact_type`, `trigger_event`, `error_type`, `importance`, `applicability`, `generated_at_phase`, `generated_at_sprint`, `generated_at_engagement`, `promoted`, `synthesis_superseded`, `synthesised_from`, `related: list[str]`, `trigger_text`, `correction_text`, `context_text`)
- [ ] EventStore event models — add `learning.created`, `learning.synthesised`, `learning.promoted` to `src/events/`

**`query_learnings` spec:** See `framework/learning-protocol.md §9` and §12.1–12.2. Reads from LangGraph `BaseStore` (runtime) and falls back to file-based index on cold start. Applies metadata filter, graph expansion (`related` links), and optional semantic supplement tier (enterprise corpus ≥ 50 entries + `sqlite-vec` available). Returns top 5 `## Correction` texts.

**`record_learning` spec:** validates entry against schema (9 rules); assigns next `<ROLE>-L-NNN` id; writes to LangGraph `BaseStore` AND writes `agents/<agent>/learnings/<ROLE>-L-NNN.md` + updates `index.yaml` (durable serialisation); emits `learning.created` EventStore event; raises `LearningSchemaError` on validation failure.

**`src/agents/learning_store.py`:** `LearningStore` wraps LangGraph `BaseStore`. Namespace: `(engagement_id, agent_role, "learnings")`. Startup: calls `rebuild_from_files()` if store is empty to rehydrate from `learnings/index.yaml`. Implements `query(phase, artifact_type, domain, expand_related=True) → list[str]` and `record(entry: LearningEntry) → str`. Optional semantic tier gated on `sqlite-vec` availability check at init time. Optional `memory_20250818` backend: if configured, the store uses Anthropic's official memory tool type (client-side) instead of direct SQLiteStore — enables the same memory patterns Claude Code uses internally; governed by `framework/learning-protocol.md §12.1`.


#### 4.6d — Learning Protocol 2026 Alignment + Harness Research (Complete — same session)

---

### Stage 4.7 — Multi-Target-Repository Support (Complete — same session)
---

### Stage 4.8 — Entity Registry Pattern (ERP) Framework (Complete)
#### 4.8a — Framework Specification (Complete)
#### 4.8b — Entity Conventions Schema (Complete)
#### 4.8c — Diagram Conventions Update (Complete)
#### 4.8d — Artifact Schema and Framework Doc Updates (Complete — 2026-04-03)
#### 4.8e — CLAUDE.md Authoring Rules (Complete)
#### 4.8f — Reverse Architecture Skills (Complete — 2026-04-03)
### Stage 4.8h — SA/SwA Role Boundary Refactoring (Complete — 2026-04-04)
---
### Stage 4.9 — ENG-001 Architecture Model (Complete — 4.9i delivered)
#### 4.9a — ERP Directory Bootstrap (Complete)
#### 4.9b — Motivation and Strategy Entities (Phase A) (Complete)
#### 4.9c — Business Layer Entities (Phase B) (Complete)
#### 4.9d — Application Layer Entities (Phase C) — Primary Stage 5 Implementation Specification (Complete)
#### 4.9e — Connection Files (Complete)
#### 4.9f — Diagrams (Phase C outputs — binding implementation views) (Complete)
#### 4.9g — Overview Documents and Decisions (Complete)
#### 4.9h — Event-Sourcing of Repository Mutations and User Inputs (Complete)
#### 4.9i — Application and Infrastructure Architecture Elaboration (Complete)
---

### Stage 5 — Python Implementation Layer

> Implements the specs defined in `framework/agent-runtime-spec.md` and `framework/orchestration-topology.md`. **Read those documents before authoring any src/ file.** Architecture: LangGraph outer loop (ADM phase workflow) + PydanticAI inner loop (per-agent invocations) + EventStore (canonical state persistence).

#### 5a — EventStore completion

- [x] **`src/events/replay.py`** + **`src/events/replay_builder.py`**: full state machine implemented — all 20 event types handled via mutable `StateBuilder`; audit-only events pass through; unknown types skipped (forward-compatible)
- [x] **`src/events/export.py`**: implement `write_event_yaml()` with full PyYAML serialisation; implement `import_from_yaml()` for disaster recovery round-trip
- [x] **`src/events/migrations/`**: Alembic migration baseline — `alembic.ini` + `src/events/migrations/env.py` (configurable URL via `SDLC_DB_URL` or `alembic.ini`) + `src/events/migrations/versions/001_baseline.py` (idempotent `CREATE TABLE IF NOT EXISTS` for events + snapshots; documented two-path startup order); `src/events/migrations/script.py.mako` (new-migration template). BDD tests in `tests/events/test_event_store_migration.py` (5 scenarios: empty DB, pre-initialised DB, round-trip, downgrade, column contract).
- [ ] **`EventStore.check_integrity()`**: validate JSON payloads, sequence gaps, YAML vs SQLite consistency check
- [ ] **Snapshot implementation** — `snapshots` SQLite table: `snapshot_id TEXT PK, trigger_event_type TEXT, trigger_sequence INTEGER, state_json TEXT NOT NULL, created_at DATETIME NOT NULL`; Alembic migration adds this table alongside `events`. Implement:
  - `create_snapshot(trigger: str) → str` — serialises current `WorkflowState` to JSON (all fields; `Path` → `str`); `INSERT INTO snapshots`; returns `snapshot_id`
  - `replay_from_latest_snapshot() → tuple[WorkflowState, int]` — `SELECT ... ORDER BY trigger_sequence DESC LIMIT 1`; deserialises `state_json` → `WorkflowState`; returns `(state, trigger_sequence)` so caller replays only events with `sequence > trigger_sequence`; falls back to full `replay()` if no snapshot exists
  - `check_snapshot_interval() → bool` — counts events since `MAX(trigger_sequence)` in snapshots; returns True if count ≥ `snapshot_interval` (read from `engagements-config.yaml`, default 100)
  - **Situative snapshot triggers** — called by the relevant nodes/handlers immediately after emitting the trigger event:
    - `engagement.started` — baseline snapshot after bootstrap (before any agent work)
    - `gate.evaluated` where `result == "passed"` — phase boundary; clean stable state
    - `sprint.close` — end of every sprint; most frequent durable checkpoint
    - `review.sprint-closed` — after sprint review corrections resolved
    - `artifact.promoted` — after enterprise promotion (major structural change)
  - **Periodic trigger** — `record_event()` calls `check_snapshot_interval()` after every write; if True, calls `create_snapshot("periodic")`; prevents unbounded replay cost between situative events
  - `EngagementSession` startup sequence: call `replay_from_latest_snapshot()` first; if snapshot found, rebuild `SDLCGraphState` from returned `WorkflowState`; call `replay_from_latest_snapshot()` only for events after `trigger_sequence`; fall back to full `replay()` only if no snapshot (first run or corrupted snapshot)
- [ ] **Event taxonomy — repository mutations and user inputs** (per §4.9h prescription): define the following event types in `src/events/models.py` and implement handlers in `src/events/replay.py` (each updates `WorkflowState` as noted):

  | Event type | Produced by | `WorkflowState` update |
  |---|---|---|
  | `artifact.created` | `ArtifactReadWriterPort.write()` — new file (status=draft) | track in draft set; not yet in `baselined_artifacts` |
  | `artifact.updated` | `ArtifactReadWriterPort.write()` — content change, no status transition | update version in `baselined_artifacts` if already baselined |
  | `artifact.baselined` | `ArtifactReadWriterPort.write()` — `draft → baselined` | add/update `baselined_artifacts[artifact_id] = version` |
  | `artifact.deprecated` | `ArtifactReadWriterPort.write()` — status → `deprecated` | remove from `baselined_artifacts`; add to `deprecated_artifacts` set |
  | `artifact.deleted` | `ArtifactReadWriterPort.delete()` | remove from `deprecated_artifacts`; audit only |
  | `source.scanned` | Reverse-arch skill Step 0 | no state change; audit only |
  | `entity.confirmed` | Reverse-arch skill Step 3 | flag entity as user-confirmed in artifact metadata |
  | `upload.registered` | `UserInputGateway` POST /uploads | append to `registered_uploads: list[str]` |
  | `file.referenced` | `ArtifactReadWriterPort.write()` when `upload_refs` present | append to `upload_reference_map: dict[str, list[str]]` (upload_id → artifact_ids) |

  Key payload contracts:
  - `artifact.created` / `artifact.updated`: `{path, artifact_id, version, produced_by_skill, source_evidence: list[str], changed_fields: list[str] | None}`; `source_evidence` is mandatory for reverse-arch writes — populated from the agent's active inference context at call time; not reconstructable after the fact.
  - `upload.registered`: `{upload_id, file_path, mime_type, original_filename, referenced_by_cq: str | None}`; file content lives at `engagements/<id>/user-uploads/<upload_id>/`; event is the reference.
  - `source.scanned`: `{scan_scope: list[str], target_repo_id: str | None, external_source_ids: list[str], triggered_by_skill: str, file_count: int}`.
  - `entity.confirmed`: `{artifact_id, confirmation_method: "user" | "inferred", confirmed_fields: list[str], user_note: str | None, upload_refs: list[str]}`.

- [ ] **Workflow lifecycle event taxonomy** — emitted by orchestration layer and PM tools (see Key decisions: three-layer emitter hierarchy). Define event types and implement `WorkflowState` handlers in `src/events/replay.py`:

  | Event type | Emitted by | `WorkflowState` update |
  |---|---|---|
  | `engagement.started` | `EngagementSession` after bootstrap | set `current_phase = "Preliminary"` |
  | `sprint.started` | `EngagementSession` (first specialist of new sprint) | set `current_sprint` |
  | `sprint.close` | `sprint_close_node` | clear `current_sprint`; increment sprint counter |
  | `phase.entered` | `EngagementSession` on phase change | set `current_phase`; increment `phase_visit_counts` |
  | `phase.transitioned` | `gate_check_node` on gate pass | same as `phase.entered` |
  | `phase.suspended` | `cq_user_node` on entry | set `suspended: True` in state |
  | `phase.resumed` | `cq_user_node` when unblocked | clear `suspended` |
  | `algedonic.escalated` | `algedonic_handler_node` | set `last_algedonic` |
  | `specialist.invoked` | `invoke_specialist()` PM tool | no state change; audit only |
  | `specialist.completed` | specialist node after agent returns | no state change; audit only |
  | `gate.evaluated` | `evaluate_gate()` PM tool | append to `gate_outcomes` |
  | `cq.batched` | `batch_cqs()` PM tool | no state change; audit only |
  | `decision.recorded` | `record_decision()` PM tool | no state change; audit only |
  | `review.pending` | `trigger_review()` PM tool | set `review_pending: True` |
  | `review.sprint-closed` | `review_processing_node` | clear `review_pending` |
  | `engagement.completed` | `engagement_complete_node` | set terminal flag |

#### 5b — Agent implementation layer

> Governed by `framework/agent-runtime-spec.md`. Each agent is a PydanticAI `Agent[AgentDeps, str | PMDecision]` built via `build_agent()`.

- [~] **`src/common/model_registry.py`**: `ModelRegistry` — two-tier index: **(1) in-memory tier: DONE** — implemented as `ModelRepository` in `src/common/model_query.py`; supports unified engagement+enterprise indexing (mount multiple roots) per `framework/artifact-registry-design.md §6.1`, enforces **no duplicate artifact-id across mounted roots**, derives `engagement="enterprise"` for enterprise-scope artifacts, and applies `engagement=` filtering in `search_artifacts` per `framework/discovery-protocol.md`. APIs: `list_artifacts(**filter)`, `list_connections(**filter)`, `search_artifacts(query)`, `read_artifact(id, mode)`; **(2) SQLite FTS5 tier: PENDING** — add `artifact_fts(artifact_id UNINDEXED, content)` table in `model_registry.db`; populate at startup and on every `write_artifact` call; `search()` queries FTS5 with `MATCH`, applies metadata filters, returns ranked `(ArtifactRecord, snippet)` pairs; optional sqlite-vec embedding tier (≥50 artifacts + library available); `watchdog` filesystem listener for incremental refresh; thread-safe (`threading.RLock`); Stage 5b should rename/promote `ModelRepository` into the production `ModelRegistry` or wrap it.
- [x] **`src/agents/deps.py`**: `AgentDeps` dataclass complete (engagement_id, event_store, active_skill_id, workflow_state, engagement_path, framework_path, agent_id + path shortcuts)
- [x] **`src/agents/base.py`**: `build_agent(agent_id, agents_root, model)` factory — layered system prompt assembly:
  - Layer 1: `AgentSpec.load(agent_id)` parses YAML frontmatter, extracts `system-prompt-identity` verbatim (hard cap ≤150 tokens; raises `AgentSpecError` if exceeded)
  - Layer 2: `AgentSpec.load_personality(agent_id)` extracts `### Runtime Behavioral Stance` subsection from §11 only (hard cap ≤350 tokens; full §11 is **not** loaded at runtime — the rest of §11 is authoring documentation, not a runtime injection target)
  - Layer 3: active skill via `@agent.instructions` calling `SkillLoader.load_instructions(ctx.deps.active_skill_id)`
- [x] **`src/agents/skill_loader.py`**: `SkillLoader.load_instructions(skill_id)` complete — parses skill Markdown, extracts included sections, enforces complexity-class token budgets (simple ≤600/720, standard ≤1200/1440, complex ≤2000/2400); truncation priority respected; hard cap exceeded → `UserWarning` (not exception) since existing skills exceed budget; Steps never truncated. `End-of-Skill Memory Close` section now included in extraction.
- [x] **`src/agents/tools/`**: MVP tool implementations (all tools described in `framework/agent-runtime-spec.md §6`):
  - `universal_tools.py` — `read_artifact(id_or_path, mode)` (resolves artifact-id → path via ModelRegistry; modes: `summary`=frontmatter+first two §content sections, `full`=entire file); `list_artifacts(**filter)` (queries ModelRegistry in-memory frontmatter cache; returns metadata list without loading bodies; filters: artifact-type, status, domain, safety-relevant, phase-produced, engagement); `search_artifacts(query: str, **filter)` (**primary discovery tool for content-based lookup** — delegates to ModelRegistry FTS5 index; optional semantic tier when available; returns ranked `(ArtifactRecord, snippet)` pairs; agent then selects which to read in full; use when artifact type is uncertain or discovery is by concept rather than metadata); `list_connections(source, target, artifact_type)` (ModelRegistry query scoped to `connections/`; all params optional); `query_event_store`, `emit_event`, `raise_cq`, `raise_algedonic`, `list_framework_docs(**filter)`, `search_framework_docs(query, **filter)`, `read_framework_doc(doc_id_or_path, section=None, mode="summary")` (query-first framework retrieval per `framework/framework-knowledge-index.md`; `mode="full"` escalation only), `discover_standards` (reads `technology-repository/coding-standards/` and `enterprise-repository/standards/`; SA/SwA/DE/DO only), `list_target_repositories()` (reads `engagements-config.yaml`; returns all registered repos with id/label/role/domain/primary/clone-path; available to all agents), `query_learnings(phase, artifact_type, domain, expand_related=True)` (per `framework/learning-protocol.md §9` + §12.1–12.2), `record_learning(entry: LearningEntry)` (per §9 + §12.1)
  - `write_tools.py` — per-agent path-constrained write tools (RepositoryBoundaryError on violation → ALG-007)
  - `target_repo_tools.py` — **multi-repo aware**: `read_target_repo(path, repo_id=None)` (repo_id=None → primary repo; raises TargetRepoNotFoundError if id not registered); `write_target_repo(path, content, repo_id=None)` (DE and DO only, per their respective access grants); `execute_pipeline(repo_id=None)` (DO only); `scan_target_repo(repo_id=None)` (Discovery Layer 4 single-repo scan — called once per repo by Layer 4 procedure); `list_target_repos()` (alias for `list_target_repositories()` — convenience import in this module). **Backward compatibility:** when `target-repository` (singular) is configured, `repo_id=None` and `repo_id="default"` both refer to it.
  - `pm_tools.py` — PM decision events (all emitted inside the tool call, before returning to the agent): `invoke_specialist(agent_id, skill_id, task)` → emits `specialist.invoked`; `evaluate_gate(gate_id, votes)` → emits `gate.evaluated` + `create_snapshot("gate.evaluated")` on pass; `batch_cqs(cq_ids)` → emits `cq.batched`; `record_decision(rationale)` → emits `decision.recorded`; `trigger_review()` → emits `review.pending`
  - `diagram_tools.py` — Model-driven diagram production per `framework/diagram-conventions.md §5` (D1–D5 protocol): `regenerate_macros(repo_path)` (scans all entity `§display ###archimate` blocks via ModelRegistry; rewrites `_macros.puml`; called automatically by `write_artifact` when an entity's archimate display spec changes — ALG-C04 if count drift detected); `generate_er_content(entity_ids)` (reads each DOB entity's `§display ###er` block; returns PUML class declarations with attribute lists for direct paste into ER diagram); `generate_er_relations(connection_ids)` (reads each er-connection's `§display ###er` block; returns cardinality lines); `validate_diagram(puml_file_path)` (extracts all PUML aliases; checks each against ModelRegistry; verifies each resolved entity has the appropriate `§display ###<language>` section; confirms `!include _macros.puml` present for ArchiMate/use-case diagrams; returns list of validation errors; ALG-C03 on alias with no backing entity — model must be extended, alias must not be removed); `render_diagram(puml_file_path)` (invokes local `plantuml` CLI; writes SVG to the sibling `diagram-catalog/rendered/` directory for files in `diagram-catalog/diagrams/`; never writes to `diagrams/rendered/`; sprint-boundary render only unless on-demand requested by PM). Non-SA agents call `diagram.display-spec-request` handoff when a needed `§display ###<language>` subsection is missing from an entity. **Agents author PUML source text directly via `write_artifact`, following templates from `framework/diagram-conventions.md §7`.**
- [x] **`src/agents/learning_store.py`**: `LearningStore` wrapper around LangGraph `BaseStore` (per `framework/learning-protocol.md §12.1`); implements `query()` and `record()` with graph-expansion and optional semantic tier; handles store rebuild from files on startup
- [x] **`src/common/framework_query/`**: queryable framework/spec index implemented (section-level metadata index + search scoring; optional semantic tier pending). API delivered: `list_docs`, `search_docs`, `read_doc`, `related_docs`; startup scan scope includes `framework/` plus orientation specs (`specs/IMPLEMENTATION_PLAN.md`, `README.md`, `CLAUDE.md`); CLI entrypoint at `python -m src.common.framework_query`.
- [x] **Framework doc graph extraction**: formal framework/spec references (`[@DOC:<doc-id>#<section-id>](...)`) parsed into directed section graph. APIs delivered: `neighbors()`, `trace_path()`.
- [~] **Framework index freshness model**: transparent freshness implemented in MCP context with background mtime polling watcher + TTL stale detection + optional caller-forced/manual refresh (`refresh=True` / CLI `refresh`). Remaining parity task: migrate to first-class evented filesystem watcher lifecycle when introduced.
- [ ] **`src/agents/tools/universal_tools.py`**: implement framework retrieval tools: `list_framework_docs`, `search_framework_docs`, and upgraded `read_framework_doc(section, mode)` with summary-first policy and full-read reason logging.
- [x] **CLI**: `uv run python -m src.common.framework_query <stats|list|search|read|related>` for deterministic local navigation/debug.
- [x] **CLI extension**: graph and maintenance commands implemented (`neighbors`, `path`, `refresh`).
- [x] **MCP surface** (framework-doc discovery): implemented in `src/tools/mcp_framework_server.py` and `src/tools/framework_mcp/` with tools `framework_query_stats`, `framework_query_list_docs`, `framework_query_list_sections`, `framework_query_search_docs`, `framework_query_read_doc` (supports `section_id` + unknown-section suggestions), `framework_query_resolve_ref`, `framework_query_related_docs`, `framework_query_neighbors`, `framework_query_path` (optional diagnostics), `framework_query_path_batch`, `framework_query_missing_links`, `framework_query_validate_refs` backed by the same index as Python/CLI.
- [x] **`src/agents/roles.py`**: per-role builder functions `build_pm_agent`, `build_sa_agent`, `build_swa_agent`, `build_de_agent`, `build_do_agent`, `build_qa_agent`, `build_po_agent`, `build_smm_agent`, `build_csco_agent` — each calls `build_agent()`, registers universal tools + role-appropriate write tool + PM decision tools (PM only). SA and SwA additionally call `register_diagram_tools()`. Replaces individual per-role `.py` modules (unified pattern).
- [x] **`src/agents/__init__.py`**: `AGENT_IDS`, `get_agent(agent_id, root, llm_config)` lazy singleton cache, `_build_for_id()` dispatcher. `AGENT_REGISTRY` populated on demand.
- [x] **`src/agents/tools/target_repo_tools.py`**: multi-repo aware target-repo tools — `list_target_repos`, `read_target_repo`, `scan_target_repo` (all roles), `write_target_repo` (DE/DO only, writes to worktree); `register_read_only_target_repo_tools` + `register_readwrite_target_repo_tools` registration helpers; TargetRepoManager unblocked (Stage 5d done)
- [x] **`src/agents/tools/diagram_tools.py`** + **`src/agents/tools/_diagram_io.py`**: 4 agent-facing tools registered via `register_diagram_tools()` for SA and SwA: `generate_er_content`, `generate_er_relations`, `validate_diagram`, `render_diagram`. `regenerate_macros` is NOT agent-exposed — it is triggered transparently by `write_artifact` (when content has `§display ###archimate`) and by the MCP watcher/refresh. `_diagram_io.py` holds internal helpers (≤130 LoC) to keep `diagram_tools.py` within the 350-LoC hard limit. Uses `ModelRepository` (same registry as universal_tools + MCP) for artifact lookup. BDD tests: 8 scenarios in `tests/agents/test_diagram_tools.py`.

#### 5c — Orchestration layer

> Governed by `framework/orchestration-topology.md`. Nested LangGraph topology with deterministic control at graph levels and PydanticAI only at specialist leaf nodes.

**Wave 2 contract deepening (completed 2026-04-08):**
- Added subgraph decomposition matrix (outer lifecycle, engagement-type, phase, specialist leaf) with explicit ownership for branching, suspension/resume, and fan-out/fan-in.
- Added deterministic-vs-agentic workflow-unit checklist with preconditions, event emission expectations, branch criteria, merge criteria, and suspend/resume invariants.
- Added minimal Stage 5 node/routing implementation checklist: required state fields consumed/produced, event taxonomy touchpoints, gate ownership, and escalation ownership.
- Source of truth: `framework/orchestration-topology.md` §2.8, §2.9, §2.10.
- Formal references:
  - [@DOC:orchestration-topology#2-8-subgraph-decomposition-matrix-wave-2](../framework/orchestration-topology.md#28-subgraph-decomposition-matrix-wave-2)
  - [@DOC:orchestration-topology#2-9-deterministic-vs-agentic-checklist-per-workflow-unit-wave-2](../framework/orchestration-topology.md#29-deterministic-vs-agentic-checklist-per-workflow-unit-wave-2)
  - [@DOC:orchestration-topology#2-10-minimal-stage-5-node-and-routing-implementation-checklist-wave-2](../framework/orchestration-topology.md#210-minimal-stage-5-node-and-routing-implementation-checklist-wave-2)

- [x] **`src/orchestration/graph_state.py`**: `SDLCGraphState` TypedDict complete with multi-repo fields (`target_repository_ids`, `primary_repository_id`), phase/sprint tracking, PM decision routing, gate votes, CQ/algedonic flags, and LangGraph `add_messages` annotation. `initial_state()` factory included.
- [ ] **`src/orchestration/subgraphs/outer_lifecycle.py`**: outer graph entry/resume classification (`new_engagement` vs `resume_engagement`), suspend/resume routing, and engagement completion routing
- [ ] **`src/orchestration/subgraphs/engagement_types.py`**: engagement-type subgraphs (`ep0_greenfield_subgraph`, `warm_start_subgraph`, `reverse_architecture_subgraph`) with deterministic entry conditions and output contracts
- [ ] **`src/orchestration/subgraphs/phases.py`**: phase subgraphs with deterministic specialist ordering and optional fan-out/fan-in segments where independence exists
- [ ] **`src/orchestration/pm_decision.py`**: `PMDecision` Pydantic model — PM's structured output (next_action, specialist_id, skill_id, task_description, reasoning, gate_id)
- [ ] **`src/orchestration/routing.py`**: all routing functions — `route_from_pm`, `route_after_specialist`, `route_after_gate`, `route_after_cq`, `route_after_algedonic`, `route_after_sprint_close`; algedonic bypass check in every routing function
- [ ] **`src/orchestration/nodes.py`**: all node implementations; each node function signature includes `event_store: EventStorePort` alongside `state: SDLCGraphState`; lifecycle event responsibilities:
  - `pm_node` — PM deliberative reasoning; no lifecycle events (PM emits via pm_tools)
  - `sa_node` … `csco_node` — each specialist node calls `invoke_specialist` via pm_tools, which emits `specialist.invoked`; emits `specialist.completed` after agent returns
  - `gate_check_node` — reads gate votes from state; calls PM `evaluate_gate` tool; on pass emits `phase.transitioned`
  - `cq_user_node` — emits `phase.suspended` on entry; emits `phase.resumed` when unblocked by `cq.answered`
  - `algedonic_handler_node` — emits `algedonic.escalated`; does NOT emit resolution (that is a separate agent decision)
  - `sprint_close_node` — emits `sprint.close`; calls `event_store.create_snapshot("sprint.close")`
  - `review_processing_node` — emits `review.sprint-closed` after correction routing completes
  - `engagement_complete_node` — emits `engagement.completed`; calls `event_store.create_snapshot("engagement.completed")`
- [ ] **`src/orchestration/graph.py`**: `build_sdlc_graph()` — exactly as specified in orchestration-topology.md §4.3; passes `event_store` into every node via `functools.partial` or LangGraph `config` injection
- [x] **`src/orchestration/session.py`**: `EngagementSession` MVP complete — boots engagement, loads config, initialises EventStore, provides `invoke_specialist(agent_id, skill_id, task, phase)` single-agent execution. CLI: `python -m src.orchestration.session --engagement ENG-001 --agent SA --skill SA-PHASE-A --task "..."`. Model overrideable via `SDLC_MODEL` env var. Full LangGraph routing (PM loop, phase subgraphs) deferred to Stage 5c.
- [ ] **`src/orchestration/promotion.py`**: Enterprise Promotion workflow — implements `repository-conventions.md §12`
- [ ] **`src/orchestration/user_interaction.py`**: CQ surface and answer ingestion — batches CQs, presents to user, routes answers back to raising agents via EventStore `cq.answered` events

#### 5d — Source adapters

- [x] **`src/sources/base.py`**: `SourceAdapter` Protocol — `query(query: str) → str` + `source_id: str`; read-only; event emission is caller's responsibility
- [ ] **`src/sources/confluence.py`**, **`src/sources/jira.py`**, **`src/sources/git_source.py`**: external source implementations; wired to `external-sources/<id>.config.yaml`
- [x] **`src/sources/target_repo.py`**: `TargetRepoManager` — multi-repo aware clone manager; reads `engagements-config.yaml` (`target-repositories` list or backward-compat `target-repository` singular); `clone_or_update(repo_id)`, `get_clone_path(repo_id) → Path`, `check_access(repo_id, agent_role) → AccessLevel`, `get_primary_id() → str | None`, `create_worktree(repo_id, branch_name) → Path` (isolated git worktree at `<base>/<repo-id>-wt-<branch>/`), `remove_worktree(repo_id, branch_name)`. BDD tests in `tests/sources/test_target_repo.py` (12 scenarios: config parsing, path resolution, access control, worktree isolation).

#### 5e — Cross-cutting skill docs and retroactive updates

- [ ] Stakeholder communication sub-skills for PM, PO, SA
- [ ] Feedback loop protocol documents (per role-pair)
- [ ] Phase H change management sub-skills retroactive update (SA, SwA/PE, CSCO)
- [x] Retroactive: add Step 0.M (Memento Recall) to all 48 skill files — complete; migration script at `scripts/add_step0m_and_memory_close.py`; End-of-Skill Memory Close appended to all files
- [ ] Retroactive: add Discovery Scan Layers 1-5 envelope to all Stage 3 skill files — Step 0.L + Step 0.M now in all files; Layer 1-5 still missing from ~37 regular phase skills (deferred: only ~11 files have the full envelope)
- [x] Retroactive: add `### Runtime Behavioral Stance` subsection to all AGENT.md §11 sections — complete (Stage 4.5e)
- [x] Retroactive: add `## Artifact Discovery Priority` section to all AGENT.md files — complete (Stage 4.5e)
- [x] Retroactive: add Step 0.D (Diagram Catalog Lookup) + D1–D6 diagram authoring sequence to SA `phase-b.md`, `phase-c-application.md`, `phase-c-data.md` and SwA `phase-d.md`, `phase-e.md` — complete (Stage 4.5f)
- [x] Retroactive: add Step 0.S (Standards and Coding Guidelines Discovery) to SwA `phase-g-governance.md`, DE `phase-g.md`, DO `phase-g.md` — complete (Stage 4.5f)

- [ ] Commit as `stage-5-python-implementation`

---

### Stage 5.5 — Engagement Dashboard (Local Web Server + User Interaction Surface)

> Local web server providing a readable, explorable view of engagement state, SDLC progress, produced artifacts, and agent activity — **and** the primary surface through which users interact with the running engagement: answering agent queries, uploading reference documents, reviewing and approving sprint output, and inspecting the full audit trail of agent work.

**Core requirements:**
1. Users can view and explore: current phase, produced artifacts, agent activity, event history.
2. Users can see and respond to pending queries (CQs) from agents without leaving the browser.
3. Users can upload files (documents, diagrams, specs) and reference them from query answers — essential for reverse architecture engagements.
4. (Configurable) Before sprint close or entity/diagram promotion, users review output and mark items as approved, needing revision, or rejected; can tag specific agents for corrections; PM handles routing of untagged items.
5. Audit logs make it unambiguous: **which agent, using which skill, in which sprint, produced which artifact**.

---

#### 5.5a — Core Dashboard (Read-Only Views + Audit Trail)

**Architecture:**

- **Server:** Python `FastAPI`. Single entry point: `python -m src.dashboard.server --engagement <id> [--port 8000]`.
- **Data sources (read-only):**
  - `engagements/<id>/workflow.db` — EventStore (via `EventStore.replay()` → `WorkflowState`)
  - `engagements/<id>/work-repositories/*/` — ERP entity files, overview docs, decisions, diagrams
  - `engagements/<id>/clarification-log/`, `handoff-log/`, `algedonic-log/`
  - `framework/agent-index.md` — agent/skill display metadata
- **Rendering:** Server-side Jinja2 templates; markdown rendered via `markdown-it-py`. No JavaScript framework.
- **No auth:** `127.0.0.1` only; local-only process.
- **Filesystem monitoring:** `watchdog` observer on `engagements/<id>/`; changes pushed via SSE (`/events/stream`); single `<script>` block in `base.html` listens and shows a "N artifact(s) updated — click to refresh" banner. No polling, no WebSocket, no framework.
- **PUML rendering:** `src/dashboard/puml_renderer.py` calls local `plantuml` binary; renders to `.svg`; cached in `render_cache/` (.gitignored); falls back to `<code>` block with install notice. No external network calls.

**Views (read-only):**

| View | URL | Content |
|---|---|---|
| Engagement Overview | `/` | Engagement ID, entry point, current phase, sprint, gate status summary; pending query count badge linking to `/queries` |
| SDLC Progress | `/progress` | ADM phase timeline; completed/active/pending phases; gate outcomes; current sprint plan |
| Artifact Browser | `/artifacts` | Tree view by work-repository and ArchiMate layer; each entity file shows: type, version, status, owner-agent, produced-by-skill; inline SVG for diagram files |
| Artifact Detail | `/artifacts/<path>` | Full rendered markdown; frontmatter as metadata table; provenance badge (agent → skill → sprint → phase); `[@artifact-id]` references as hyperlinks; associated diagrams rendered inline |
| Diagram Browser | `/diagrams` | All `.puml` diagrams from diagram-catalog; rendered SVG inline; element stats; link to producing artifact |
| Model Explorer | `/model` | Multi-mode architecture model exploration (see §5.5d below) |
| Handoff Log | `/handoffs` | Inter-agent handoffs: from, to, artifact, version, acknowledged status |
| Algedonic Log | `/algedonic` | Algedonic signals: trigger ID, severity, status (active/resolved), escalation target |
| Agent Status | `/agents` | Per-agent: active phase, last event, open CQs, pending handoffs, skills active this sprint |
| Audit Trail | `/audit` | Per-agent, per-skill, per-sprint work chain: each entry shows agent → skill invoked → artifact(s) produced → EventStore events emitted. Filterable by agent, skill, phase, sprint. Primary visibility surface for understanding who did what. |
| Event Log | `/events` | Raw EventStore event stream (paginated); each event shows: timestamp, type, agent, phase, sprint, skill-id (extracted from payload), artifact reference. Filter by event type / agent / phase / sprint. |

**Audit Trail detail (`/audit`):** Each row = one skill invocation. Columns: sprint, phase, agent, skill-id, skill-display-name, start-event timestamp, artifacts produced (linked), CQs raised, handoffs created, duration. Derived by joining `skill.started` / `skill.completed` EventStore events with `artifact.created` / `artifact.baselined` / `handoff.created` / `cq.raised` events in the same sprint window. Makes it unambiguous which agent used which skill to produce which work.

**Provenance badge** on Artifact Detail: derived from `produced-by-skill` frontmatter field and EventStore `artifact.created` event. Displayed as: `[SA] · [SA-PHASE-B] · Sprint 2 · Phase B · 2026-04-03`.

**Implementation tasks (5.5a):**

- [ ] `src/dashboard/__init__.py`
- [ ] `src/dashboard/server.py` — FastAPI app; all read-only routes; SSE endpoint `/events/stream`; startup
- [ ] `src/dashboard/state.py` — `EngagementSnapshot` dataclass: hydrated from `EventStore.replay()` + ModelRegistry filesystem scan; refreshed per-request; `AuditEntry` list built from event join
- [ ] `src/dashboard/watcher.py` — `watchdog` observer; pushes SSE events; one observer per server lifetime
- [ ] `src/dashboard/puml_renderer.py` — detects `plantuml` CLI; renders `.puml` → `.svg`; caches; fallback to source
- [ ] `src/dashboard/file_server.py` — serves `.svg`, `.png` inline; `.pdf` as embed; `.docx`/`.xlsx` as download; path-restricted to engagement directory
- [ ] `src/dashboard/markdown_renderer.py` — renders `.md` → safe HTML; frontmatter table; `[@artifact-id]` as hyperlinks; `[inferred:]` and `[UNKNOWN]` annotations highlighted
- [ ] `src/dashboard/audit.py` — `build_audit_trail(events: list[WorkflowEvent]) → list[AuditEntry]`: joins skill/artifact/handoff/cq events; returns per-skill-invocation records
- [ ] `src/dashboard/templates/` — Jinja2 templates: `base.html` (SSE `<script>`), `overview.html`, `progress.html`, `artifacts.html`, `artifact_detail.html`, `diagrams.html`, `events.html`, `handoffs.html`, `algedonic.html`, `agents.html`, `audit.html`
- [ ] `src/dashboard/static/style.css` — minimal; readable; print-friendly; no build step
- [ ] `src/dashboard/render_cache/` — `.gitignore` entry

---

#### 5.5b — User Interaction Layer (Queries, Uploads, Sprint Review)

**Purpose:** The dashboard becomes the primary surface for user input into the SDLC workflow. All user interactions write to the EventStore via the same `EventStore.record_event()` path used by agents — no special write channel.

**Architecture additions:**

- **Interaction routes** (`POST` endpoints on `server.py`): CQ answer submission, file upload, sprint review submission. All writes go through `src/dashboard/interaction.py` which calls `EventStore.record_event()`.
- **User-uploads store:** Uploaded files written to `engagements/<id>/user-uploads/` (git-tracked; committed at sprint boundaries). Each upload registered as an EventStore `upload.registered` event with `filename`, `content-type`, `sha256`, `uploaded-at`, `referenced-by-cq` (optional). Agents access uploads via `UserUploadAdapter` (see Stage 5d).
- **Sprint review config:** Read from `engagements-config.yaml` under `sprint-review:`. When enabled, PM emits `review.pending` event (instead of `sprint.close`) at sprint end; dashboard surfaces `/review`; user submits → `review.submitted` event → PM processes corrections.
- **JavaScript budget:** Two vanilla `<script>` blocks permitted — (1) SSE change-alert listener (5.5a), (2) review-toolbar state management: counts selected items, enables/disables submit button, shows per-item comment toggle. No framework, no npm, no build step.

**New EventStore event types (add to `src/events/` models):**

| Event type | Emitted by | Payload |
|---|---|---|
| `cq.answered` (user) | Dashboard interaction | `cq_id`, `answer_text`, `upload_refs: list[str]` |
| `upload.registered` | Dashboard interaction | `upload_id`, `filename`, `content-type`, `sha256`, `size_bytes`, `referenced-by-cq` |
| `review.pending` | PM (sprint close trigger) | `sprint_id`, `phase`, `artifact_ids: list[str]`, `connection_ids: list[str]`, `diagram_ids: list[str]` |
| `review.submitted` | Dashboard interaction | `sprint_id`, `reviewer: "user"`, `items: list[ReviewItem]`, `submitted-at` |
| `review.correction-routed` | PM (post-review processing) | `sprint_id`, `item_id`, `target-agent`, `comment`, `artifact_id` |
| `review.sprint-closed` | PM (post-review processing) | `sprint_id`, `approved_count`, `revision_count`, `rejected_count` |

`ReviewItem` schema: `{ artifact_id: str, decision: "approved" | "needs-revision" | "rejected", agent_tag: str | null, comment: str | null }`.

**Sprint Review Configuration** (`engagements-config.yaml`):

```yaml
sprint-review:
  enabled: true                        # false by default (automated engagements skip review)
  trigger:                             # when review is required
    - sprint-close                     # before PM closes any sprint
    - entity-promotion                 # before entities are promoted to enterprise repo
  scope:                               # what artifact types appear in the review list
    - entities                         # ERP model entity files
    - connections                      # ERP connection files
    - diagrams                         # PUML diagram files
    - decisions                        # ADR files
    - overview-docs                    # architecture-vision.md, ba-overview.md, ta-overview.md
  default-agent-for-untagged: PM       # PM routes corrections when reviewer didn't tag an agent
  auto-approve-after-hours: 48         # auto-approve all pending items after timeout (0 = never)
```

**Stage/Agent review-gate policy (required):**

```yaml
review-gates:
  default:
    blocking: false
  by-stage:
    phase-a:
      blocking: true
      agents: [SA, PO, CSCO]
    phase-b:
      blocking: true
      agents: [SA, PO, CSCO]
    phase-c:
      blocking: true
      agents: [SwA, SA, CSCO]
    phase-g:
      blocking: true
      agents: [DE, DO, QA]
  overrides:
    - stage: phase-e
      agent: PM
      blocking: true
```

When `blocking: true`, dependent downstream stage transitions are held until the corresponding review item is approved by the user.

#### 5.5c — Dashboard Review-Control Model (Findability Anchor)

This subsection is the canonical review-control model for dashboard-driven human approval.

1. Policy source: `review-gates` in `engagements-config.yaml`.
2. Decision unit: `(stage, agent)` with optional per-item override.
3. Behavior:
  - `blocking: true` -> downstream dependent workflow nodes must wait for user approval.
  - `blocking: false` -> workflow may proceed while review remains advisory.
  - For blocking phase-stage gates, any `needs-revision` or non-approved item routes back into the existing specialist phase-work control loop (same CQ/algedonic paths), not into a separate ad-hoc rework branch.
  - In workflow-net diagrams, this loopback must terminate on the explicit specialist-lane rework merge node immediately before phase skill execution.
4. Enforcement point: orchestration layer (`review_processing_node` + stage-transition routing guards), not skill prose.
5. Required events: `review.pending`, `review.submitted`, `review.correction-routed`, `review.sprint-closed`.
6. UI contract: dashboard Review view must display per-item decision state and blocking status before submit.

**New / updated views (5.5b):**

| View | URL | Mode | Content |
|---|---|---|---|
| Queries | `/queries` | Read + Write | All pending CQs requiring user input; count badge in nav header (e.g. "Queries (3)"); per-CQ: description, raising agent, skill, blocking status, related artifact; text area to compose answer; file-attach button (uploads file, inserts reference into answer); submit button |
| Uploads | `/uploads` | Read + Write | All user-uploaded files: filename, size, upload date, SHA256, referenced-by CQ/review; upload form (drag-and-drop or file picker); download links |
| Sprint Review | `/review` | Read + Write | Active only when `review.pending` event exists for current sprint (otherwise shows "No review pending" with last review outcome); artifact list grouped by type (entities, connections, diagrams, decisions); per-item: rendered preview, provenance badge, decision radio (approved / needs-revision / rejected), agent-tag dropdown, comment textarea; sticky review toolbar showing: total items, N approved / N flagged / N rejected, Submit Review button (enabled when all items have a decision); submission POST → `review.submitted` event |
| Engagement Overview (updated) | `/` | Read | Adds: pending query count badge ("Queries (N)") linking to `/queries`; sprint review status badge if review is pending ("Review needed") |

**Query response workflow (`/queries`):**

1. Dashboard reads all `cq.raised` events; filters to status `open` (no matching `cq.answered` event).
2. Displays each open CQ: agent identity, skill-id, blocking status, the question text, any prior partial answers.
3. User types answer in textarea. Optionally clicks "Attach file" → file picker → file uploaded to `engagements/<id>/user-uploads/`; `upload.registered` event emitted; upload reference ID auto-inserted into answer textarea.
4. User submits → `POST /queries/<cq_id>/answer` → `interaction.py` validates non-empty, emits `cq.answered` event with answer text and any upload_refs; records to EventStore.
5. PM's `user_interaction.py` (`src/orchestration/user_interaction.py`) monitors for `cq.answered` events and routes answers back to raising agents per `clarification-protocol.md §4`.

**Sprint review workflow (`/review`):**

1. PM emits `review.pending` at sprint close trigger (if `sprint-review.enabled: true`). Sprint does NOT close until review is submitted.
2. Dashboard detects `review.pending`; surfaces `/review` with the full artifact list for the sprint (from `review.pending` event payload).
3. User marks each item: approved / needs-revision / rejected. For `needs-revision` or `rejected`: agent-tag dropdown (SA, SwA, PM, DO, DE, QA, CSCO) and comment textarea.
4. Review toolbar shows live count. Submit enabled when all items decided. User submits → `POST /review/submit` → `review.submitted` event emitted.
5. PM processes `review.submitted`:
   - `rejected` items: excluded from sprint artifact set; artifact set back to `status: draft`; `artifact.rejected` event emitted.
   - `needs-revision` items: if `agent_tag` present → `handoff.created` to tagged agent with comment as revision instruction; if no tag → PM classifies and routes to accountable agent per RACI matrix.
   - `approved` items: sprint proceeds; `review.sprint-closed` event emitted; `sprint.close` follows.
6. Revision items re-enter the normal skill invocation cycle. PM may trigger another sprint review if significant revisions were made (determined by PM based on revision scope).
7. Gate ownership remains PM/CSCO-governed: `BPR-004` gate evaluation is executed by PM orchestration with CSCO vote authority where applicable, never by the user.

**File upload detail (`/uploads` and `/queries` attach):**

- Files stored at `engagements/<id>/user-uploads/<upload_id>-<sanitised-filename>`. `upload_id` is UUID4.
- No executable files accepted (MIME-type allow-list: PDF, images, Office docs, Markdown, plain text, JSON, YAML, XML, CSV).
- Max file size: 50 MB (configurable in `engagements-config.yaml` under `uploads.max-file-size-mb`).
- `UserUploadAdapter` (Stage 5d addition): implements `SourceAdapter` protocol; `query()` returns upload metadata list; agents call `read_artifact(upload_id)` to retrieve content as text (PDF → extracted text via `pdfminer`; images → path reference; others → decoded text).
- Upload manifest: `engagements/<id>/user-uploads/manifest.yaml` (git-tracked); one entry per upload with id, filename, content-type, sha256, uploaded-at, referenced-by.

**Implementation tasks (5.5b):**

- [ ] `src/dashboard/interaction.py` — `UserInputGateway`: validates and writes CQ answers, uploads, review submissions to EventStore; enforces content rules (non-empty answers, MIME allow-list for uploads); path-restricted writes
- [ ] `src/dashboard/uploads.py` — `UploadManager`: saves file to `user-uploads/`, computes SHA256, writes manifest entry, emits `upload.registered`; `get_upload(upload_id)` for retrieval; MIME-type validation
- [ ] `src/dashboard/review.py` — `ReviewManager`: loads `review.pending` event; builds per-artifact review items; validates `ReviewItem` submission; emits `review.submitted`; computes review summary
- [ ] `src/sources/user_upload.py` — `UserUploadAdapter`: `SourceAdapter` implementation; reads `user-uploads/manifest.yaml`; `query()` returns upload list; integrates with existing source adapter registry in `src/sources/base.py`
- [ ] `src/events/` — add event models: `CQAnsweredEvent`, `UploadRegisteredEvent`, `ReviewPendingEvent`, `ReviewSubmittedEvent`, `ReviewCorrectionRoutedEvent`, `ReviewSprintClosedEvent`
- [ ] `src/orchestration/user_interaction.py` — update: monitor `cq.answered` events from dashboard (not just CLI); route answers to raising agents; monitor `review.submitted` and trigger PM review-processing node
- [ ] `src/orchestration/nodes.py` — update `sprint_close_node`: check `sprint-review.enabled` config; if true, emit `review.pending` and wait (do not close) until `review.submitted` received; `review_processing_node`: process ReviewItems, emit correction handoffs or `review.sprint-closed`
- [ ] `src/dashboard/server.py` — add interaction routes: `POST /queries/<cq_id>/answer`, `POST /uploads`, `POST /review/submit`; update existing routes to render new views
- [ ] `src/dashboard/templates/` — add: `queries.html`, `uploads.html`, `review.html`; update `base.html` nav: add Queries count badge (`<span class="badge">{{pending_cq_count}}</span>`); update `overview.html` for review-pending status
- [ ] `src/dashboard/static/style.css` — add: badge styles, review toolbar (sticky bottom bar), file-attach inline widget, decision radio styling, comment toggle
- [ ] `src/dashboard/static/review.js` — review toolbar state: counts decisions per category, enables submit when all items decided, toggles comment visibility; second and final JS block
- [ ] `engagements-config.yaml` — add `sprint-review:` and `uploads:` sections with documented defaults
- [ ] `docs/dashboard.md` — update usage guide: queries workflow, file upload, sprint review configuration, audit trail interpretation

**Constraints (updated for 5.5b):**

- Read-only views (5.5a) never write to any file. Interaction routes (5.5b) write only through `EventStore.record_event()` and `UploadManager` — never directly to work-repositories or agent-owned directories.
- Dashboard never invokes agents, calls the LLM, or triggers workflow actions directly. User interaction events are consumed by the orchestration layer's monitoring loop, which triggers agent work.
- Must work with a partially-complete engagement. Absent artifacts display as "not yet produced"; review view with no pending review shows last review outcome.
- Startup under 5 seconds for engagements with ≤500 events, ≤100 artifacts.
- No external network calls. PUML rendering uses local binary only.
- JavaScript budget: two `<script>` blocks maximum — (1) SSE change-alert listener, (2) `review.js` review toolbar. No framework, no npm.
- Upload MIME allow-list enforced at server level. No executable files stored. Path traversal prevention enforced in `UploadManager` and `file_server.py`.
- `auto-approve-after-hours: 0` (never auto-approve) is the only safe default for safety-relevant engagements. Timeout auto-approve is opt-in.

**Commit as `stage-5.5-dashboard`**

---

#### 5.5d — Model Explorer (Architecture Model Navigation)

**Purpose:** Let users efficiently explore the full architecture model — entities, connections, and documents — without relying solely on diagrams. Diagrams are good for narrative context; the Model Explorer is for density, traceability, and discovery.

**Four navigation modes (all read-only, backed by ModelRegistry):**

| Mode | UI pattern | Description |
|---|---|---|
| Tree | Collapsible sidebar tree | Grouped by layer (motivation → strategy → business → application → technology → implementation); each node = one entity; click → detail panel. Filter by: layer, artifact-type, status, owner-agent. |
| Table / Strict search | Filterable sortable table | All entities and connections as rows; columns: artifact-id, name, type, layer, status, owner-agent, version; sort by any column; strict keyword filter on name/type/id; multi-select rows to open graph view centred on selection. |
| Semantic search | Search box + ranked results | Free-text query delegated to `ModelRepository.search_artifacts()`; returns ranked hits with snippet; click result → detail panel; optionally restrict to layer or type. |
| Graph explorer | Interactive force-directed graph | D3.js (single `<script src="d3.min.js">` from a local vendor copy — not a CDN); nodes = entities; edges = connections coloured by type (serving/composition/flow etc.); click node → detail panel; double-click → expand neighbours; filter panel (layer, connection-type). Strict JS budget: one vendor file (`static/d3.v7.min.js`, vendored at setup) + one app file (`static/graph.js`, <300 LoC). No npm, no build step. |

**Detail panel** (shared by all modes): renders entity or connection as formatted HTML; frontmatter table; `§content` markdown; `[@artifact-id]` links navigate to that entity in-panel; inline diagram SVG if entity appears in a diagram; "connections" tab listing in/out connections with neighbour previews.

**Implementation tasks (5.5d):**

- [ ] `src/dashboard/model_explorer.py` — `ModelExplorerData`: builds tree, table, and graph data structures from `ModelRepository`; `graph_data()` returns `{nodes, edges}` JSON for D3; `search(query, filters)` delegates to ModelRepository; all computed once per request (no long-lived cache needed at this scale)
- [ ] `src/dashboard/server.py` — add routes: `GET /model` (tree/table default), `GET /model/search`, `GET /model/graph`, `GET /model/<artifact_id>` (detail panel fragment for HTMX-style inline load or full page)
- [ ] `src/dashboard/templates/model_explorer.html` — three-panel layout: left sidebar (tree), centre (table or graph canvas), right (detail panel); tab bar switching table/graph
- [ ] `src/dashboard/templates/model_detail.html` — entity/connection detail fragment; reused in all modes
- [ ] `src/dashboard/static/graph.js` — D3 force-directed graph: load `/model/graph` JSON; render nodes+edges; click/double-click handlers; filter panel wired to DOM checkboxes; pan+zoom via `d3.zoom()`
- [ ] `src/dashboard/static/d3.v7.min.js` — vendored D3 v7 (download at setup time via `scripts/vendor_assets.py`; never fetched at runtime)
- [ ] `scripts/vendor_assets.py` — one-time script: downloads `d3.v7.min.js` from official release archive into `src/dashboard/static/`; checksums verified; no network calls at server startup

**Constraints:**

- All data served from ModelRepository (same index used by MCP model server). No separate database.
- Graph view: nodes capped at 200 for render performance; excess nodes shown in table with "Load more in graph" affordance.
- No CDN calls. D3 is vendored locally. No npm, no build step.
- Graph JS budget: one vendor file + one app file, app file ≤300 LoC.
- Semantic search falls back gracefully when FTS5 tier is not yet populated (returns empty with "index not ready" notice).
- The detail panel must work for both entities and connections; connection detail shows source/target entity summaries inline.

---

### Stage 5.6 — LLM Provider Configuration System

Replace scattered hardcoded model strings with a structured configuration layer so the LLM provider can be changed via config. PydanticAI's own `provider:model-id` string convention (`anthropic:claude-sonnet-4-6`, `openai:gpt-4o`, `ollama:llama3.1`, etc.) is the portability mechanism — no additional abstraction layer is needed. Provider SDKs move to optional extras; PydanticAI itself and LangGraph remain core dependencies. Use PydanticAI's built-in `TestModel` for API-free tests.

#### 5.6-A — LLMConfig and Provider Extras ✅

- [x] **`src/models/llm_config.py`** — `LLMConfig` Pydantic model with `from_env()` (reads `SDLC_PRIMARY_MODEL`/`SDLC_ROUTING_MODEL`) and `load(config_path, engagement_id)` (cascade: per-engagement YAML → global YAML → env vars)
- [x] **`src/models/__init__.py`** — package init
- [x] **`engagements-config.yaml`** — top-level `llm:` block with `primary-model` / `routing-model`; per-engagement override supported via engagement-level `llm:` block
- [x] **`src/agents/base.py`** — `build_agent(... llm_config: LLMConfig | None = None)` replaces `model: str`; passes `cfg.primary_model` and `cfg.extra_params` to `Agent()`
- [x] **`src/orchestration/session.py`** — replaced `os.getenv("SDLC_MODEL", ...)` with `LLMConfig.load(config_path, engagement_id)`; `SDLC_MODEL` env var removed
- [x] **`pyproject.toml`** — `anthropic>=0.40` moved to `[anthropic]` optional extra; `[openai]` and `[ollama]` extras added; PydanticAI stays core
- [x] **`scripts/demo_setup.py`** — `--model` flag sets `SDLC_PRIMARY_MODEL` env var before invoking session

**Committed as `stage-5.6a-llm-config`**

---

#### 5.6-B — Architecture Model and Documentation Corrections

- [x] **`AIF-002.llm-client-port.md`** — update `§content`: the provider boundary is provided by PydanticAI's model string convention; `LLMConfig` configures provider selection; no separate port protocol is implemented. Update Properties table: `Implemented by: PydanticAI Agent`, `Provider config: LLMConfig (DOB-015)`. Remove references to `src/agents/protocols.py` and "swappable test double".

- [x] **`CST-001.no-framework-lock-in.md`** — update scope: LLM provider is swappable via `LLMConfig`; PydanticAI (agent execution) and LangGraph (orchestration) are deliberate framework choices used for their respective capabilities.

- [x] **`APP-005.agent-factory.md`** — `| LLM backend | claude-sonnet-4-6 ... |` → `| LLM backend | LLMConfig (default: anthropic:claude-sonnet-4-6 primary, anthropic:claude-haiku-4-5 routing) |`

- [x] **`APP-007.pm-agent.md`**, **`APP-008.sa-agent.md`**, **`APP-009.swa-agent.md`** — `| LLM | claude-sonnet-4-6 |` → `| LLM | LLMConfig.primary_model |`

- [x] **New entity `DOB-015.llm-config.md`** — `artifact-type: data-object`; `owner-agent: SwA`; fields: `primary_model`, `routing_model`, `extra_params`; references `AIF-002`

- [x] **`specs/IMPLEMENTATION_PLAN.md` technology stack** — replace "Anthropic Claude API (claude-sonnet-4-6 ...)" with "Configurable LLM provider via `LLMConfig` (PydanticAI `provider:model-id` format; default `anthropic:claude-sonnet-4-6` / `anthropic:claude-haiku-4-5`)"

- [x] **`CLAUDE.md` technology stack** — same generalisation; `src/agents/` is adapter-layer code where PydanticAI imports are correct

- [x] **`general_python_coding_guidelines.md`** — add: "`src/agents/` is adapter-layer code; PydanticAI imports (`Agent`, `RunContext`) are permitted throughout `src/agents/` and prohibited in `src/models/`, `src/events/`, and `src/orchestration/` business logic."

- [x] **Run `ModelVerifier.verify_all()`** on updated entities — 0 errors (2050 files); DOB-015 added to component map (v0.3.0) + serving connection DOB-015→APP-005 created

**Commit as `stage-5.6b-model-and-docs`**

---

### Stage 5.7 — Skill Quality Hardening

Informed by structural analysis of `addyosmani/agent-skills` (10.9k-star engineering-skills library for coding agents). Four patterns from that library are directly valuable in our context; two additional internal improvements are appended. The rationalization table is the highest-priority addition because it defends against the most dangerous class of agent failure: procedural shortcuts that are silently justified rather than escalated.

**Critical implementation pre-condition:** Before adding new sections to skill files, `SkillLoader._INCLUDED_H2` must be updated to include them, and the token budget must be validated. Sections written but not in `_INCLUDED_H2` are silently dropped and never reach the agent. The three new sections (Rationalizations, Red Flags, Verification) are currently NOT in `_INCLUDED_H2`.

**Placement convention for new sections** (applies to all complex skills; standard skills get Red Flags + Verification only):

```
... Procedure steps ...
## Common Rationalizations (Rejected)     ← new; injected at top of assembled content (pre-procedure guard)
## Feedback Loop                          ← existing
## Red Flags                              ← new; after Feedback Loop
## Algedonic Triggers <!-- workflow -->   ← existing; mode-tagged workflow-only
## Verification                           ← new; before Outputs
## Outputs                                ← existing
## End-of-Skill Memory Close <!-- workflow --> ← existing; mode-tagged workflow-only
```

**SkillLoader injection contract for new sections:**
- `## Common Rationalizations (Rejected)` → assembled first (before Inputs Required), so the agent reads guards before procedure
- `## Red Flags` → assembled after Feedback Loop
- `## Verification` → assembled after Algedonic Triggers (or after Red Flags in express mode)
- Truncation priority (lowest = first to drop when budget tight): End-of-Skill Memory Close → Outputs → Algedonic Triggers → Red Flags → Verification → Feedback Loop → Rationalizations → Inputs Required. Procedure (Steps) is never truncated.

**Token budget:**
- Stage 5.7-E (boilerplate extraction) reclaims ~150 tokens per skill. Implement first.
- After extraction: raise complex soft cap 2000 → 2350, hard cap 2400 → 2820.
- Rationalizations (3 rows) ≈ 200 tokens; Red Flags (6 items) ≈ 150 tokens; Verification (10 items) ≈ 200 tokens. Net addition: ~550 tokens, covered by boilerplate savings + budget increase.

**Abbreviation definitions in Layer 1:**
Most abbreviations in body sections are defined inline on first use or appear in Layer 1+2. Genuine gaps: `S1/S2/S3` severity classification and `EP-0..EP-H` entry point codes — not defined anywhere in injected content. Fix: add one definitions sentence to each AGENT.md `system-prompt-identity` field:
> `Severity: S1=immediate-halt, S2=requires-revision, S3=advisory. EP-0=cold-start, EP-A..H=mid-lifecycle entries. CQ=Clarification Request. APR=Architecture Principles Register.`
~50 tokens, always in context.

**Frontmatter routing fields (`invoke-when`, `invoke-never-when`) must be plain English — no unexplained abbreviations.** These fields are read by LLMs for autonomous skill selection (PM agent via registry tool calls, express mode without a `--skill` flag, any external use). SkillLoader also parses them as guard metadata, but the primary consumer is an LLM that has no guaranteed pre-injected glossary. Write them as self-contained sentences a new reader can understand without any context. See Stage 5.7-D for the authoring rule and audit checklist. (`trigger-conditions` and `trigger-phases` are documentation/code-only and are not injected to any LLM.)

#### 5.7-A — Rationalization Tables + Shortcut-Catch Mechanism

**Design rationale:** Rationalization tables can only be built meaningfully from experience — a fully pre-populated table before any real agent runs would be speculative. The implementation therefore has two parts: (1) seed each complex skill with 2–3 of the *most predictable* shortcuts (derivable from the governance structure alone, not from LLM observation); (2) add a lightweight catch-and-append mechanism that grows the table from live runs.

**Catch-and-append mechanism — honest design:**

Only a human reviewer can reliably classify a quality failure as a *rationalization pattern* rather than a legitimate knowledge gap or a correctly-raised ALG situation. Automated detection would be circular: if the agent could consistently self-report the shortcuts it took, it would not take them. Two complementary mechanisms are used instead:

**1. Artifact-level heuristic checks (automated, structural violations only):**
`scripts/check_artifact_heuristics.py` inspects produced artifacts for known shortcut signatures — these are structural violations detectable from the output without inferring intent:
- SA artifacts: gap-analysis rows where all four domain rows contain only "Not yet characterised" or "TBD"; safety envelope section shorter than 50 words; stakeholder register containing only agent role IDs (STK-001..009) with no external entries
- DE artifacts: PR description missing the AC reference or coverage percentage; implementation notes file empty after PR creation
- CSCO artifacts: gate vote cast with `csco-sign-off` field missing or `pending`

These are violation flags surfaced in the engagement dashboard and EventStore — not rationalization classifications.

**2. Human-triage script (semi-automated, human decides):**
`scripts/triage_learning_candidates.py` reads `learnings/*.md` across all engagement directories, filters for `error-type: protocol-skip` and gate-veto entries, groups by `skill-id`, and formats them as a triage list for a human reviewer to examine. The human decides which entries represent a rationalization pattern worth adding to the table. Threshold suggestion (not enforcement): 2+ occurrences of structurally similar corrections in the same skill → candidate for table entry.

**3. Sprint review annotation (Stage 5.5):**
The sprint review UI includes a "flag as rationalization pattern" action on learning entries. When a reviewer flags an entry, the entry gains a `rationalization-candidate: true` field. The triage script filters these first.

**4. Quarterly maintenance task:**
Documented in `retrospective-knowledge-capture.md`: run `triage_learning_candidates.py`, review flagged entries, and update skill rationalization tables with confirmed patterns.

The Learning Generation subsection of each complex skill gains a `shortcut-observed` row as a reminder that the existing §3.1 `protocol-skip` error-type is the correct classification when a procedural step was bypassed — no new entry type is needed.

**Seed rationalizations — SA-PHASE-A:**

| Rationalization | Rejection |
|---|---|
| "The Safety Envelope can be left as TBD pending CSCO availability — I'll fill it in after the gate" | `csco-sign-off` must be `true` before an `approved` gate vote; if CSCO is unavailable, raise ALG-002 — casting a gate vote with a pending safety envelope is a governance violation |
| "The Stakeholder Register only needs agent roles — external stakeholders can be added in Phase B" | Phase A gate requires ≥1 named external stakeholder beyond agent roles, or a CQ documenting why none have been identified; an agent-roles-only register is an incomplete AV |
| "Gap analysis can be left as 'Not yet characterised' for all four domains — that's honest about the current state" | At least one domain gap must describe a substantive delta between a known baseline and the target; all-placeholder gap tables signal missing discovery work; raise a CQ for the missing baseline rather than filing the table with uniform placeholders |

**Seed rationalizations — DE-PHASE-G:**

| Rationalization | Rejection |
|---|---|
| "I can start implementing while waiting for the AC to be baselined — I'll adjust if it changes" | An AC at v0.x.x triggers ALG-008 immediately; implementation against a draft AC is invalid regardless of time pressure; raise ALG-008 and halt |
| "I'll write unit tests after the implementation is working and the logic is confirmed" | Unit tests are written in Step 6 before the PR in Step 9; CI must pass before the PR is created; this sequence is the acceptance criterion order, not a preference |
| "Compliance gaps can be noted informally in a code comment rather than in the PR description" | Compliance gaps must be documented in the PR description per Step 9 item 4; comment-form or verbal documentation is not a governance record and will not pass SwA review |

**Seed rationalizations — PM-MASTER-AGILE-ADM:**

| Rationalization | Rejection |
|---|---|
| "A CQ with a reasonable assumed answer is equivalent to waiting for user response — I'll proceed with the assumption" | Assumed answers must be explicitly recorded in the artifact's `assumptions` field with a risk flag and PM acceptance; they never silently replace CQ answers; the PM must record the assumption and notify the affected agent before proceeding |
| "Phase transition can proceed if no algedonic signal has been raised and no agent has vetoed" | Absence of an algedonic signal is necessary but not sufficient; the phase gate checklist must be evaluated explicitly; missing required artifacts trigger a PM veto even without an agent signal |
| "I can batch multiple specialist invocations to save latency" | Each specialist invocation is a separate EventStore event and LangGraph node transition; batching bypasses gate evaluation between specialists and violates the event-sourcing invariant |

**Checklist:**
- [ ] `scripts/check_artifact_heuristics.py` — structural violation checks on produced artifacts (placeholder detection, missing required fields, etc.); outputs violation list to stdout and emits `artifact.heuristic-violation` advisory events to EventStore
- [x] `scripts/triage_learning_candidates.py` — reads `learnings/*.md`, filters `error-type: protocol-skip` and gate-veto entries, groups by `skill-id`, formats triage list for human review; respects `rationalization-candidate: true` flag added by sprint review annotation
- [ ] `framework/learning-protocol.md §3` — add note under `protocol-skip` error-type: when a procedural step was bypassed, document the bypassed step and the governance rule it violated; this is the source material for future rationalization table entries
- [x] `agents/solution-architect/skills/phase-a.md` — add `## Common Rationalizations (Rejected)` (3 rows seeded); `## Red Flags` (7 items); `## Verification` (12-item checklist); `invoke-never-when` frontmatter
- [x] `agents/implementing-developer/skills/phase-g.md` — same (3 rows / 6 items / 12-item checklist / frontmatter)
- [x] `agents/project-manager/skills/master-agile-adm.md` — same (3 rows / 6 items / split sprint-closeout + gate-evaluation checklist / frontmatter)
- [ ] All other 15 complex skills — add `## Common Rationalizations (Rejected)` with 2–3 rows each. Priority order: SA-PHASE-B, SA-PHASE-H, SwA-PHASE-C-APP, SwA-PHASE-C-DATA, SwA-PHASE-D, CSCO-GATE-A, CSCO-STAMP-STPA, QA-PHASE-EF, QA-PHASE-G, QA-PHASE-H, DevOps skills, SA/SwA reverse-arch skills
- [ ] `agents/project-manager/skills/retrospective-knowledge-capture.md` — add quarterly rationalization-table maintenance step (run `triage_learning_candidates.py`, review, update tables)

---

#### 5.7-B — Red Flags Sections

Pre-escalation observable indicators placed after `## Feedback Loop` and before `## Algedonic Triggers` in all complex skills. Algedonic triggers are reactive (thresholds already crossed); Red Flags are proactive (observable signs the skill is going off-track before the algedonic threshold).

**Examples for SA-PHASE-A:**
- AV document contains no DRV-nnn IDs — capability overview has no traceability anchor
- §3.3 Stakeholder Register lists only agent roles (STK-001..009) with no external stakeholders and no CQ record
- §3.7 Safety Envelope section is blank, contains "TBD", or contains generic boilerplate not specific to the engagement domain
- Architecture Vision Statement contains technology product names or architecture acronyms without explanation
- Phase A gate vote is being prepared while any AV section contains `[UNKNOWN]` without a corresponding CQ-id

**Examples for DE-PHASE-G:**
- Feature branch contains imports from the framework repository path (not target-repo)
- PR description omits any reference to the AC constraint ID or test coverage percentage
- Implementation notes document is empty after Step 5 completes
- Unit test file contains `import os` or `os.environ` (real credential access in test suite)
- Step 8 compliance self-check has been skipped (no checkbox records in PR description)

**Checklist:**
- [ ] `agents/solution-architect/skills/phase-a.md` — add `## Red Flags` (5–7 items)
- [ ] `agents/implementing-developer/skills/phase-g.md` — same
- [ ] `agents/project-manager/skills/master-agile-adm.md` — same
- [ ] All other 15 complex skills — add `## Red Flags`
- [ ] All 30 standard-class skills — add `## Red Flags` (3–5 items each)

---

#### 5.7-C — Standalone Verification Sections

Replace embedded gate-vote checklists (currently inside individual steps, e.g. SA-PHASE-A Step 10) with a standalone `## Verification` section that is the invariant skill-completion gate — it applies regardless of which execution path through the skill was taken. Placed after `## Algedonic Triggers`, before `## Outputs`.

The gate-vote checklist in the final step is kept as the *vote criterion* (the agent must be able to cast `approved`); the `## Verification` section is the *skill-completion criterion* (the skill is not done until all boxes are ticked, whether or not a gate vote was cast in this invocation).

**Template:**
```markdown
## Verification

Before emitting the completion event for this skill, confirm:

- [ ] All blocking CQs resolved or documented as PM-accepted assumptions
- [ ] Primary output artifact exists at the required minimum version
- [ ] CSCO sign-off recorded where required (`csco-sign-off: true`)
- [ ] All required EventStore events emitted in this invocation
- [ ] Handoffs to downstream agents created
- [ ] Learning entries recorded if a §3.1 trigger was met this invocation
- [ ] Memento state saved (End-of-Skill Memory Close)
```

Each skill's `## Verification` has its own concrete checklist items drawn from the skill's outputs and gate criteria. The generic template above is a minimum floor.

**Checklist:**
- [ ] `agents/solution-architect/skills/phase-a.md` — add `## Verification`; merge gate checklist from Step 10
- [ ] `agents/implementing-developer/skills/phase-g.md` — same
- [ ] `agents/project-manager/skills/master-agile-adm.md` — same
- [ ] All other 15 complex skills — add `## Verification`

---

#### 5.7-D — `invoke-never-when` Frontmatter Field + Plain-English Routing Field Authoring Rule

Add `invoke-never-when` as a new optional frontmatter field complementing `invoke-when`. Prevents misrouting for the most common wrong-context invocation. SkillLoader surfaces this in a pre-invocation guard log line; PM routing policy can enforce it as a hard block.

**Authoring rule (applies to `invoke-when` AND `invoke-never-when`):** Write these fields as plain English sentences with no unexplained abbreviations. These fields are read by LLMs for autonomous skill selection (PM agent via registry tool calls, express mode, external use) and have no guaranteed glossary pre-injected. Short enough that plain English costs nothing.

**Corrected examples (plain English — abbreviation-free):**

SA-PHASE-A:
```yaml
invoke-when: >
  A Phase A Architecture Sprint starts, or one of the project-initiation entry points
  (greenfield, architecture-requirement, or warm-start revisit) is active and an Architecture
  Vision document does not yet exist at version 1.0.0.
invoke-never-when: >
  An Architecture Vision document already exists at version 1.0.0 and no active Change Record
  references it. Use SA-PHASE-H for change management. Do not re-run Phase A to update an
  existing Architecture Vision.
```

DE-PHASE-G:
```yaml
invoke-when: >
  A Solution Sprint starts and the Implementing Developer has received and acknowledged a
  baselined Architecture Contract; implements each assigned Work Package and submits pull
  requests to the target repository.
invoke-never-when: >
  No baselined Architecture Contract (version 1.0.0 or later) exists for the current sprint.
  Raise an algedonic escalation signal to the Project Manager and await a baselined Architecture
  Contract before starting implementation.
```

**Done (2026-04-10):** SA-PHASE-A, DE-PHASE-G, PM-MASTER — `invoke-when` and `invoke-never-when` rewritten to plain English.

**Checklist:**
- [x] SA-PHASE-A — `invoke-when` + `invoke-never-when` plain English ✓
- [x] DE-PHASE-G — `invoke-when` + `invoke-never-when` plain English ✓
- [x] PM-MASTER — `invoke-when` + `invoke-never-when` plain English ✓
- [ ] `framework/agent-runtime-spec.md §5` — document `invoke-never-when` as a pre-invocation guard field; SkillLoader logs it when present; **update the description of `invoke-when` and `invoke-never-when` to state that both are LLM-readable and must be plain English** (remove any language saying they are "routing metadata only" or "not injected to LLM")
- [ ] `framework/agent-index.md` — confirm any skill routing table rows that reference `invoke-when` text are also plain English; update if needed
- [ ] Any other framework docs (`orchestration-topology.md`, `clarification-protocol.md`) that describe skill routing fields — audit for incorrect claims about frontmatter visibility and correct as needed
- [ ] `src/agents/skill_loader.py` — extract and return `invoke-never-when` field alongside existing fields; add `guard_condition` to loaded skill metadata; `EngagementSession.invoke_specialist()` logs a WARNING when `guard_condition` is non-empty (enforcement is PM routing logic, not SkillLoader hard-block)
- [ ] All remaining 15 complex skills — add `invoke-never-when` in plain English; audit `invoke-when` for abbreviations
- [ ] All 30 standard skills — add `invoke-never-when` in plain English; audit `invoke-when` for abbreviations

---

#### 5.7-E — SkillLoader: Mode-Aware Section Filtering + Boilerplate Extraction + Budget Update

This stage covers three tightly coupled SkillLoader concerns that must be done together:

**E.1 — Mode-aware section filtering (prerequisite for Express Mode content in Stage 5.8)**

Section headers carry an optional HTML comment mode tag: `<!-- workflow -->`, `<!-- express -->`, or no tag (= both modes). SkillLoader strips the comment suffix before using the heading as a key. `AgentDeps` gets `invocation_mode: Literal["workflow", "express"] = "workflow"`. `build_agent()` injects a Layer 1 express override sentence when `invocation_mode == "express"`: *"Express Mode: produce domain output directly from user input; skip all EventStore event emissions, gate voting, and handoff creation."*

Default section mode assignments:
- `## Algedonic Triggers` → workflow-only (add `<!-- workflow -->` to all skill files)
- `## End-of-Skill Memory Close` → workflow-only (add `<!-- workflow -->`)
- All other existing sections → no tag (both modes)
- `## Express Mode` (future, Stage 5.8) → express-only

This is the infrastructure gate for Stage 5.8. Do NOT write Express Mode sections into skill files until this is implemented.

**Why `_INCLUDED_H2: frozenset` is not the right architecture:**

The frozenset splits logically-unified section behaviour across three places: `_INCLUDED_H2` (inclusion), `_assemble()` (order), `_truncate()` (truncation). Adding one new section requires changes in all three. Sections omitted from the frozenset are silently dropped with no warning (this is why the Rationalizations/Red Flags/Verification sections we authored never reach the agent). Mode-awareness would require a parallel frozenset or scattered conditionals.

**E.2 + E.1 combined — Replace `_INCLUDED_H2` with a `SectionSpec` registry**

Define a `SectionSpec` dataclass and a `_SECTION_REGISTRY` dict that encodes all section behaviour in one place:

```python
@dataclass(frozen=True)
class SectionSpec:
    key: str                    # canonical normalised name (used as dict key)
    aliases: frozenset[str]     # alternative headings that resolve to this spec
    modes: frozenset[str]       # {"workflow", "express"} = both; singleton = mode-gated
    assembly_position: int      # output ordering (lower = earlier)
    truncation_priority: int    # lower = first to drop under budget; -1 = never truncate
    truncation_strategy: str    # "omit" | "compact"

_SECTION_REGISTRY: dict[str, SectionSpec] = {
    spec.key: spec for spec in [
        SectionSpec("common rationalizations (rejected)", frozenset(), {"workflow","express"},  0, 7, "compact"),
        SectionSpec("inputs required",                    frozenset(), {"workflow","express"},  1, 8, "compact"),
        SectionSpec("procedure",      frozenset({"steps"}),{"workflow","express"},              2,-1, "omit"),
        SectionSpec("feedback loop",                      frozenset(), {"workflow","express"},  3, 6, "compact"),
        SectionSpec("red flags",                          frozenset(), {"workflow","express"},  4, 4, "compact"),
        SectionSpec("algedonic triggers",                 frozenset(), {"workflow"},            5, 3, "compact"),
        SectionSpec("verification",                       frozenset(), {"workflow","express"},  6, 5, "compact"),
        SectionSpec("outputs",                            frozenset(), {"workflow","express"},  7, 2, "compact"),
        SectionSpec("end-of-skill memory close",          frozenset(), {"workflow"},            8, 1, "omit"),
        # Express-mode-only sections (authored in skill files with <!-- express --> tag):
        # "express mode" is not in the registry — handled via per-instance heading tag (see below)
    ]
}
```

**Truncation priority column** (lower = first to drop): 1=End-of-Skill Memory Close, 2=Outputs, 3=Algedonic Triggers, 4=Red Flags, 5=Verification, 6=Feedback Loop, 7=Rationalizations, 8=Inputs Required, -1=Procedure (never).

**Per-instance heading tags** (`<!-- workflow -->` / `<!-- express -->`) serve as overrides for sections NOT in the global registry — specifically future skill-specific sections like `## Express Mode` that will appear in only 4–5 skills. The heading tag declares the mode for that instance; SkillLoader resolves unknown-registry sections via the tag (and emits a WARNING if neither a registry entry nor a tag is present — no more silent drops).

**`_assemble()` and `_truncate()` become fully data-driven:** both functions iterate `_SECTION_REGISTRY` sorted by `assembly_position` / `truncation_priority` rather than having hardcoded section-name logic. Adding a new section type requires one new `SectionSpec` entry; no other code changes.

**E.3 — Boilerplate extraction + budget increase**

Step 0.L, Step 0.M, and `## End-of-Skill Memory Close` body text are identical across all 48 skill files (~150 tokens each). Move canonical text to AGENT.md `## Skill Preamble` / `## Skill Close` sections; `build_agent()` injects them as Layer 2 prefix/suffix. Skill files retain a one-line stub (`*Step 0.L — Injected at Layer 2.*`) for authoring context; SkillLoader recognises the stub pattern and excludes it from budget-counted content. End-of-Skill Memory Close remains in `_SECTION_REGISTRY` as `workflow`-mode with `assembly_position=8` — but its body is a stub, so it costs ~5 tokens rather than ~50.

After extraction: raise budgets — complex: 2000→2350 soft / 2400→2820 hard; standard: 1200→1400 soft / 1440→1680 hard; simple: 600→700 soft / 720→840 hard. Net effect: ~550 tokens of new content (Rationalizations + Red Flags + Verification) − ~150 tokens boilerplate savings = +400 tokens needed; budget increase covers it.

**E.4 — Abbreviation definitions in Layer 1**

Add one sentence to each AGENT.md `system-prompt-identity` covering genuinely undefined system terms: `S1/S2/S3` (severity levels), `EP-0..H` (entry points), `CQ` (Clarification Request), `APR` (Architecture Principles Register). ~50 tokens; always in context. This covers H2 skill body sections. Frontmatter routing fields (`invoke-when`, `invoke-never-when`) must be plain English without unexplained abbreviations — they are read by LLMs for skill selection and have no guaranteed pre-injected definitions; see Stage 5.7-D authoring rule.

**Checklist:**
- [ ] `src/agents/skill_loader.py` — replace `_INCLUDED_H2: frozenset` with `SectionSpec` dataclass + `_SECTION_REGISTRY: dict[str, SectionSpec]`; make `_assemble()` and `_truncate()` fully data-driven; parse optional `<!-- workflow -->` / `<!-- express -->` heading comments for per-instance mode override; emit WARNING on sections that are neither in registry nor tagged; add `invocation_mode` parameter to `load()` / `load_instructions()`; detect and exclude `*Injected at Layer 2.*` stubs from budget-counted content; raise budget constants
- [ ] `src/agents/deps.py` — add `invocation_mode: Literal["workflow", "express"] = "workflow"` to `AgentDeps`
- [ ] `src/agents/base.py` — `build_agent()`: inject Step 0.L/0.M/Memory Close boilerplate as Layer 2 prefix/suffix from AGENT.md `## Skill Preamble` / `## Skill Close`; inject express override sentence when `invocation_mode == "express"`; pass `invocation_mode` through to `SkillLoader.load_instructions()`
- [ ] `framework/agent-runtime-spec.md §4–5` — document `SectionSpec` registry pattern, per-instance heading tag convention, mode-aware filtering, assembly order, truncation priority, budget constants, boilerplate injection contract, express override sentence
- [ ] All 9 `AGENT.md` files — add `## Skill Preamble` and `## Skill Close` sections; add abbreviation definitions sentence to `system-prompt-identity`
- [ ] `scripts/collapse_boilerplate.py` — bulk-collapse Step 0.L, Step 0.M, and End-of-Skill Memory Close body in all 48 skill files to single-line stubs
- [ ] BDD tests for `skill_loader.py` — add scenarios: SectionSpec registry lookup, mode filtering (workflow/express), unknown-section warning, stub detection, budget enforcement with new caps
- [ ] CLAUDE.md Rule 14 — replace `_INCLUDED_H2` reference with `SectionSpec` registry pattern + `invocation_mode` field

**Note:** This is the highest-priority implementation item for Stage 5.7. Until the registry is in place and the new section keys are registered, the Rationalizations/Red Flags/Verification sections authored in SA-PHASE-A, DE-PHASE-G, and PM-MASTER are silently excluded from agent context.

---

#### 5.7-F — Measurable Thresholds + Intent→Skill-Chain Map

Two lower-effort improvements:

**Measurable thresholds (audit and patch):** Audit all procedure steps in complex skills for qualitative-only criteria ("sufficient", "adequate", "meaningful") and add numeric floors/ceilings where a specific threshold has architectural significance. Do not add arbitrary numbers — only where there is a defensible rationale.

Targets identified:
- SA-PHASE-A §3.5 capability overview: add floor of 3, ceiling of 7 capability clusters (already stated in Step 4 — confirm it is enforced in Verification checklist)
- SA-PHASE-A §3.3 stakeholder register: add floor of 1 external stakeholder or explicit CQ justification
- SA-PHASE-A §3.8 gap analysis: add minimum 1 substantive row per domain (no all-placeholder tables)
- DE-PHASE-G Step 6: add "≥1 test case per public function/method" as floor complement to ≥80% coverage
- DE-PHASE-G Step 9: "PR description rejected if any of the 6 required items is absent"

**Intent→Skill-Chain Map:** Add an `## Intent → Skill Chain` section to `framework/agent-index.md` mapping common engagement intents to the canonical skill invocation sequence. This gives the PM routing logic a concise, scannable reference for which skills to chain together.

- [ ] `framework/agent-index.md` — add `## Intent → Skill Chain` section (5–8 rows covering: EP-0 greenfield, EP-G reverse-arch, mid-engagement change request, Phase A warm-start, Phase C cold-start)
- [ ] Complex skill procedure steps — audit and patch qualitative-only criteria with numeric floors where justified

---

### Stage 5.8 — Express Mode: Standalone Skill Invocation

**Depends on:** Stage 5.7-E (SectionSpec registry + mode-aware loading must be in place first)

Express Mode allows a single skill to be invoked against any target directory without creating an engagement, without the LangGraph orchestration graph, and without the full EventStore lifecycle. The primary use cases are:

- **Reverse architecture against an existing codebase** (`SA-REV-A`, `SWA-REV-C`) — a user points the agent at a repository and gets architecture documentation out, no ADM workflow required.
- **Point-in-time safety stamp** (`CSCO-STAMP-STPA`) — a user wants a safety analysis of a specific component without running a full sprint.
- **Architecture vision draft** (`SA-PHASE-A`) — a user wants a first-pass architecture vision from a brief and a target directory, without a PM coordination layer.
- **Developer code review** (`DE-PHASE-G`) — a user wants a compliance/quality assessment of a PR without a full engagement context.

#### 5.8-A — What Express Mode Is (and Is Not)

Express Mode **is:**
- A thin wrapper around a single PydanticAI agent invocation (`agent.run(prompt)`)
- Mode-aware: `invocation_mode="express"` passed in `AgentDeps`, which triggers filtered skill loading via the SectionSpec registry
- Output-to-stdout or output-to-directory (caller's choice): no handoff events, no `workflow.db`, no `EngagementProfile`
- A legitimate, first-class supported path — not a testing shortcut

Express Mode **is not:**
- A replacement for full engagements (no PM routing, no cross-phase continuity, no ALG signaling to other agents)
- A simplified agent (same LLM, same skill procedure, same quality checks — just governance scaffolding removed)
- Batch processing (one skill invocation per `express` call; chaining multiple skills is a caller responsibility)

#### 5.8-B — Integration Mechanism: CLI Entry Point

The integration surface is a `src/cli.py` module providing an `express` subcommand, callable as:

```
uv run python -m src.cli express \
    --role solution-architect \
    --skill SA-REV-A \
    --target-dir ./my-existing-project \
    [--output-dir ./architecture-output] \
    [--model anthropic:claude-sonnet-4-6] \
    [--context "key=value ..."]
```

**Flags:**
- `--role` — agent role (`solution-architect`, `implementing-developer`, etc.); maps to `AgentRole` enum
- `--skill` — skill ID (`SA-REV-A`, `DE-PHASE-G`, etc.); validated against SkillLoader
- `--target-dir` — path to the target repository or codebase; passed to agent as Layer 4 context; mounted as a read-only target repo
- `--output-dir` — optional directory for file outputs; defaults to current directory; agents that produce files write here
- `--model` — optional LLM override; same PydanticAI `provider:model-id` format as full engagements; falls back to `llm:` block in `engagements-config.yaml` then to system default
- `--context` — optional `key=value` pairs (repeatable) injected into the Layer 4 user prompt as YAML block

**Interaction model:** The CLI produces a rich prompt from the `--context` args and `--target-dir` contents (file tree summary), invokes the agent, streams the response to stdout, and writes any produced files to `--output-dir`. The invocation is synchronous — no background processes, no event loop visible to the user.

**Python API (for programmatic callers):**

```python
from src.express import run_express_skill, ExpressResult

result: ExpressResult = await run_express_skill(
    role="solution-architect",
    skill_id="SA-REV-A",
    target_dir=Path("./my-project"),
    output_dir=Path("./architecture-output"),
    extra_context={"project_name": "TaskFlow API"},
    llm_model="anthropic:claude-sonnet-4-6",
)
# result.text — agent's prose response
# result.files_written — list of Path objects written to output_dir
# result.messages — full message history for inspection
```

`src/express.py` is a thin module (≤120 lines):
- `ExpressResult` dataclass with `text`, `files_written`, `messages`, `skill_id`, `role`
- `run_express_skill()` — constructs `AgentDeps(invocation_mode="express", ...)`, calls `get_agent(role)`, builds Layer 4 prompt from context, calls `agent.run()`
- No EventStore, no `EngagementSession`, no LangGraph graph

#### 5.8-C — What Changes in Agent Behavior (Mode Filtering)

With `invocation_mode="express"` set in `AgentDeps`, the SectionSpec registry (Stage 5.7-E) applies the following changes to the loaded skill:

**Excluded in express mode** (workflow-only sections, per registry `modes={"workflow"}`):
- `## Algedonic Triggers` — signaling other agents is meaningless without an ALG bus
- `## End-of-Skill Memory Close` — no MementoStore in express mode; no engagement session to close

**Layer 1 behavioral override** — one sentence is appended to `system-prompt-identity` when `invocation_mode == "express"`:
> "You are operating in Express Mode: there is no engagement session, no handoff lifecycle, and no ADM gate gating. Produce your best-effort output directly; document any critical uncertainties in your response."

This single sentence is sufficient to prevent the agent from stalling on missing engagement context or waiting for governance gate signals that will never arrive.

**Procedure steps receive no structural modification.** Steps that reference engagement artifacts (e.g., "check `engagement-profile.md`") become best-effort in express mode: the agent is smart enough to skip them if context is absent when its Layer 1 explicitly says to do so. Express Mode procedure variants are NOT written as separate duplicate steps — that would double the maintenance burden.

**`## Express Mode` H2 section** (optional, express-only per registry): A skill file may include an `## Express Mode` section. When present, it is injected in express mode (excluded in workflow mode). It should contain only:
1. **Minimum viable context** — what the agent absolutely needs that it cannot infer (e.g., "A populated `--target-dir` is required; invocation without one produces a speculative draft only")
2. **Output format relaxation** — deviations from the full artifact schema that are acceptable in express output (e.g., "Entity files may omit `§display ###archimate` blocks; diagram generation is optional")
3. **Stopping criteria** — when to stop and report rather than recurse (e.g., "If no source files are found in `--target-dir`, report as gap and exit; do not raise a CQ")

NOT included in `## Express Mode` sections: duplicated procedure steps, shadow verification checklists, or alternative feedback loops. Keep it under 150 tokens.

#### 5.8-D — Skill Candidates for Express Mode Sections

Not all skills need an `## Express Mode` section — only those where express behavior meaningfully differs from the default. Candidates (in priority order):

| Skill | Rationale |
|---|---|
| `SA-REV-A` | Primary express use case; target-dir is the only required input; outputs are entity files + vision doc |
| `SWA-REV-C` | Same; outputs are application-layer entity files |
| `SA-PHASE-A` | Vision draft from a brief; minimum viable context is a project name + domain description |
| `CSCO-STAMP-STPA` | Safety analysis on a specific component; no prior HAZOP required for express run |
| `DE-PHASE-G` | PR review mode: target-dir = repo, context = branch name; no AC baseline required in express |

Skills that do NOT need an `## Express Mode` section (their procedure works as-is in express, with the Layer 1 override sufficient):
- All standard/simple skills (Red Flags, Verification, Outputs are all generic enough)
- QA-PHASE-EF/G (requires a running test suite — no structural difference in express)
- PM-MASTER-AGILE-ADM (PM has no meaningful express mode; routing is its entire purpose)

#### 5.8-E — Implementation Checklist

- [ ] **`src/express.py`** — `ExpressResult` dataclass; `run_express_skill()` async function; no EventStore, no LangGraph, no EngagementSession; mounts `--target-dir` as read-only target repo via `TargetRepoManager`; uses `get_agent(role)` from `src/agents/__init__.py`
- [ ] **`src/cli.py`** — `express` subcommand; argparse integration; streams agent output to stdout; writes files to `--output-dir`; `--model` flag cascades to `LLMConfig`; entry point: `python -m src.cli`
- [ ] **`src/agents/deps.py`** — `invocation_mode: Literal["workflow", "express"] = "workflow"` field (prerequisite; needed by Stage 5.7-E first)
- [ ] **`src/agents/base.py`** — Layer 1 express override sentence injected when `deps.invocation_mode == "express"`
- [ ] **`src/agents/skill_loader.py`** — mode filtering applied via SectionSpec registry (this is the Stage 5.7-E change; 5.8 depends on it)
- [ ] **`## Express Mode` sections** — add to the 5 candidate skills listed in 5.8-D; keep each under 150 tokens
- [ ] **BDD tests** — `tests/agents/features/express_mode.feature`: scenarios: (1) skill loads without engagement context, (2) algedonic-triggers excluded in express, (3) end-of-skill-memory-close excluded in express, (4) express section included in express / excluded in workflow, (5) CLI invocation parses args correctly, (6) run_express_skill returns ExpressResult with text and files_written
- [ ] **CLAUDE.md** — Stage 5.8 row added to implementation stages table

**Integration constraint:** Stage 5.8 has a hard dependency on Stage 5.7-E completing first. The SectionSpec registry must be in place before any express-mode section filtering will work. Do not author `## Express Mode` sections in skill files until Stage 5.7-E is done (the sections will be silently dropped, same as Rationalizations/Red Flags/Verification today).

---

### Stage 6 — Integration Testing

- [ ] Define synthetic project in `tests/synthetic-project/` (small but non-trivial: a web service with a clear business requirement, a safety-relevant component, and at least one mid-project requirement change)
- [ ] Run full chain from Phase A through Phase G
- [ ] Validate: all handoff artifacts produced, all schemas satisfied, no orphaned outputs
- [ ] Identify token budget actuals vs estimates, calibrate summary-vs-full retrieval thresholds
- [ ] Document lessons learned → feed into skill file revisions
- [ ] Commit as `stage-6-integration-validated`

---

## Immediate Next Actions

**Completed this session (2026-04-09):**
- Step 0.M (Memento Recall) + End-of-Skill Memory Close added to all 48 skill files via `scripts/add_step0m_and_memory_close.py`.
- `src/events/replay.py` + `replay_builder.py`: full event state machine (20 event types, mutable builder pattern).
- `src/agents/`: `deps.py`, `base.py` (build_agent factory with Layer 1+2+3 assembly), `skill_loader.py` (budget enforcement with warnings).
- `src/agents/tools/`: `universal_tools.py`, `escalation_tools.py`, `learning_tools.py`, `write_tools.py` (path-boundary enforcement + ALG-007 signalling).
- `src/orchestration/`: `graph_state.py` (SDLCGraphState TypedDict), `session.py` (EngagementSession MVP — boot + single-agent invoke). CLI: `python -m src.orchestration.session`.
- Full stack smoke test: EngagementSession + EventStore + AgentSpec + SkillLoader + tool registration all wire correctly.
- `scripts/demo_setup.py` + `scripts/demo_teardown.py`: scenario-based integration test CLI (TaskFlow API Phase A); scaffold + agent run + automated verification.
- Stage 5.6-A: `src/models/llm_config.py` (LLMConfig with cascade load), `src/models/__init__.py`; `build_agent()` now accepts `llm_config: LLMConfig`; provider extras in pyproject.toml; `engagements-config.yaml` `llm:` block; `--model` flag in demo_setup.py.

**Completed this session (2026-04-09, continued):**
- Stage 5.6-B: AIF-002, CST-001, APP-005/007/008/009 entity corrections; DOB-015 (LLMConfig) created via MCP; DOB-015→APP-005 serving connection; component map updated (v0.3.0); general_python_coding_guidelines.md + CLAUDE.md + IMPLEMENTATION_PLAN.md tech stacks updated; ModelVerifier 0 errors (2050 files).
- Stage 5b: `src/models/learning.py` (LearningEntry Pydantic model); `src/agents/learning_store.py` (LearningStore wrapping LangGraph BaseStore with file-durable tier + graph expansion); `src/agents/tools/pm_tools.py` (5 PM decision tools + register_pm_tools); `src/events/models/specialist.py`, `decision.py`, `review.py` (missing event payload models); `src/events/models/cq.py` + CQBatchedPayload; `src/agents/roles.py` (per-role build_*_agent factory functions for all 9 roles); `src/agents/__init__.py` (AGENT_REGISTRY + get_agent() lazy cache). All 119 tests pass.
- Stage 5.5d added: Model Explorer requirement (tree/table/semantic-search/graph-explorer modes; D3 graph vendored; detail panel) added to dashboard spec.
- Stage 5a: `src/events/event_store.py` — public snapshot API (`create_snapshot`, `replay_from_latest_snapshot`, `check_snapshot_interval`) fully implemented; `src/events/export.py` — `write_event_yaml` uses PyYAML serialisation; `import_from_yaml()` implemented (disaster-recovery YAML→SQLite rebuild). `src/events/replay_builder.py` — data-driven dispatch (`_HANDLERS` dict replaces match/case; `StateBuilder.from_state()` + `_CycleBuilder.from_state()` enable O(delta) incremental replay); `src/events/replay.py` — thin loop architecture (`_run_events` + two initialisation strategies, no duplicated dispatch). APP-001 entity updated to match actual public API.
- Stage 5c: `src/orchestration/pm_decision.py` (PMDecision structured output model); `src/orchestration/graph_state.py` aligned with spec (`pm_decision: PMDecision | None`, `algedonic_active: bool`, `current_agent`, `current_skill`; flat fields removed); `src/orchestration/routing.py` (all 7 routing functions per spec); `src/orchestration/nodes.py` (`build_node_fns(session)` factory — all 15 nodes as closures over EngagementSession); `src/orchestration/graph.py` (`build_sdlc_graph(session)` — full compiled graph). `src/agents/base.py` — added `result_type` param to `build_agent()` for typed PM structured output. `src/events/models/cycle.py` — added `EngagementCompletedPayload`. Demo updated: 4-step flow with framework infrastructure check (5/5 checks: EventStore, agent registry, LearningStore, SDLCGraphState, PMDecision) that runs without an LLM key. All 119 tests pass; ModelVerifier 0 errors (2050 files).

**Completed this session (2026-04-10):**
- Stage 5a: Alembic migration baseline — `alembic.ini`, `src/events/migrations/env.py` (SDLC_DB_URL override), `src/events/migrations/versions/001_baseline.py` (idempotent CREATE TABLE IF NOT EXISTS), `script.py.mako`. BDD tests: 5 scenarios (empty DB, pre-init DB, round-trip, downgrade, column contract) all pass.
- Stage 5b: `src/models/memento.py` (MementoState Pydantic model, field validators, summary()); `src/agents/memento_store.py` (SQLite-backed MementoStore with upsert semantics, mementos table in workflow.db); `get_memento_state`/`save_memento_state` added to `universal_tools.py` and registered in `register_universal_tools`.
- Stage 5b: `src/agents/tools/target_repo_tools.py` — `list_target_repos`, `read_target_repo`, `scan_target_repo` (all roles), `write_target_repo` (DE/DO only, worktree-enforced); `register_read_only_target_repo_tools` + `register_readwrite_target_repo_tools` registration helpers.
- Stage 5c: BDD tests — `tests/orchestration/test_routing.py` (31 scenarios covering all 7 routing functions + algedonic bypass invariant) + `tests/orchestration/test_graph.py` (17 scenarios: graph compile, all 15 nodes registered, initial_state contract). 48 new tests.
- Stage 5d: `src/sources/__init__.py`, `src/sources/base.py` (SourceAdapter Protocol), `src/sources/target_repo.py` (TargetRepoManager: config parsing, path resolution, access control, clone_or_update, create_worktree/remove_worktree). BDD tests: 12 scenarios all pass.
- Total test count: 184 (was 119).

**Completed this session (2026-04-10, continued — diagram tools + macro regeneration consistency):**
- Stage 5b: `src/agents/tools/diagram_tools.py` (4 agent-facing tools: `generate_er_content`, `generate_er_relations`, `validate_diagram`, `render_diagram`) + `src/agents/tools/_diagram_io.py` (internal helpers, split for LoC compliance). `regenerate_macros` is internal-only (auto-triggered, not agent-facing). `register_diagram_tools()` added; called for SA and SwA in `roles.py`.
- Macro regeneration consistency: all four write paths now trigger `generate_macros()` — `write_artifact` (conditional on `§display ###archimate` block), `model_create_entity` MCP tool (already present), `model_tools_refresh` MCP tool (new call), `_watcher_loop` (new call after file-change detection). `_regenerate_macros_for_roots()` helper added to `watch_tools.py`.
- Demo parity: `scripts/demo_setup.py` task prompts simplified to PM-style briefs (no re-injection of skill content); added `--phase-a-only` flag; `scripts/demo_verify.py` updated with multi-path fallback checks.
- BDD tests: `tests/agents/features/diagram_tools.feature` + `tests/agents/test_diagram_tools.py` — 8 scenarios covering regenerate_macros (0 and 1 entity), generate_er_content warning, validate_diagram error, render_diagram skip, register (4 tools, not regenerate_macros), write_artifact auto-regen, write_artifact no-regen for plain markdown. All pass.
- Total test count: 202 (8 new diagram_tools BDD tests).

**Completed this session (2026-04-10, continued — integration test drive):**
- Fixed three silent bugs in `src/agents/tools/universal_tools.py` found via live LLM run:
  (1) `search_artifacts` tried `for r, snippet in results` — `ModelRepository.search_artifacts()` returns `SearchResult(hits: list[SearchHit])`, not a list of tuples. Fixed to iterate `results.hits`.
  (2) `list_artifacts` called `r.to_dict()` on `ArtifactSummary` (a plain dataclass). Fixed to build dict manually from dataclass fields.
  (3) `read_artifact` returned `dict[str,object]` with return annotation `-> str`. Fixed to JSON-serialize with `json.dumps(result, default=str)`.
  All three tools now have `try/except` guards returning empty-list / error-string on failure (no propagating exceptions, no retry loops).
- BDD tests: `tests/agents/features/universal_tools.feature` + `tests/agents/test_universal_tools.py` — 10 scenarios covering correct return types, JSON-serializability, missing-repo graceful degradation. All pass.
- `src/agents/tools/write_tools.py`: boundary violations now return an error string (not raise) so the model can self-correct; `_derive_artifact_id()` auto-emits artifact events from filename pattern `TYPE-NNN.*.md`; improved docstring explicitly stating both `relative_path` and `content` are required.
- `src/agents/base.py`: `retries=3`, `model_settings={"max_tokens": 8192}` — Haiku was hitting the 4096-token ceiling mid-tool-call with large markdown content.
- `src/orchestration/session.py`: `register_read_only_target_repo_tools` added to `invoke_specialist` so agents can read from target repos during discovery.
- `scripts/demo_setup.py`: always tears down before scaffold (clean state per run); task prompt includes concrete YAML frontmatter format example and valid `artifact-type` values; observability: clean error message with exception type, no raw traceback.
- `.gitignore`: `engagements/ENG-DEMO/` excluded (ephemeral demo engagement, rebuilt each run).
- **Demo result (final run with `anthropic:claude-haiku-4-5-20251001`):** 6/7 checks pass — vision doc ✓, stakeholders ✓, drivers ✓, principles ✓, no boundary violations ✓, 20 artifact events ✓. Remaining: ModelVerifier [E102] `artifact-type: architecture-principle` → should be `principle`. Fix applied in prompt (task template updated); not re-run per session close constraint.
- Total test count: 194 (10 new universal_tools BDD tests).

**Completed this session (2026-04-10, continued — Stage 5.7 skill quality hardening):**
- Stage 5.7 spec written in IMPLEMENTATION_PLAN.md; CLAUDE.md and README.md updated.
- Catch-and-append mechanism redesigned (human-triage model, not automated classifier): `triage_learning_candidates.py` created.
- SA-PHASE-A, DE-PHASE-G, PM-MASTER-AGILE-ADM: `invoke-never-when` frontmatter + `## Common Rationalizations (Rejected)` + `## Red Flags` + `## Verification` added.
- Design correction: new sections (Rationalizations, Red Flags, Verification) are not yet in `_INCLUDED_H2` — they are in skill files but not injected to the agent until Stage 5.7-E is implemented.
- Stage 5.7-E expanded: mode-aware section filtering (prerequisite for Express Mode), new section injection, boilerplate extraction, budget update, abbreviation definitions in Layer 1 — all four concerns bundled as one coordinated SkillLoader change.
- Stage 5.8 Express Mode spec written: `src/express.py` API + `src/cli.py` `express` subcommand + mode-filtered loading design (5 skill candidates, BDD test list, dependency on Stage 5.7-E).
- Design correction (2026-04-10): `invoke-when` / `invoke-never-when` frontmatter fields MUST be plain English — they are read by LLMs for skill selection (PM via registry tools, express mode, external use) and have no guaranteed pre-injected glossary. Previous claim ("SkillLoader parses them, LLM never sees them") was wrong. Corrected SA-PHASE-A, DE-PHASE-G, PM-MASTER; remaining 45 skills pending as part of Stage 5.7-D audit.

**Immediate next items (priority order):**
1. **Stage 5.7-E (SkillLoader rewrite)** — prerequisite for everything else in 5.7 and 5.8: new sections don't reach the agent until `_INCLUDED_H2` is replaced with SectionSpec registry; Express Mode can't be wired until mode filtering is implemented; boilerplate savings needed before remaining complex skills fit budget. Implement all four E-concerns together. Run BDD tests after.
2. **Demo: 7/7 pass** — confirm `artifact-type: principle` prompt fix resolves the ModelVerifier [E102] error on next run.
3. **Stage 5.7-A/B/C/D (remaining 15 complex skills)** — after Stage 5.7-E: SA-PHASE-B, SA-PHASE-H, SwA-PHASE-C-APP, SwA-PHASE-C-DATA, SwA-PHASE-D, CSCO-GATE-A/STAMP-STPA, QA-PHASE-EF/G, SwA reverse-arch, DevOps, SA reverse-arch. Standard skills get Red Flags + Verification + `invoke-never-when` only.
4. **Stage 5.7-A pending:** `check_artifact_heuristics.py`; `learning-protocol.md §3` `protocol-skip` note; `retrospective-knowledge-capture.md` quarterly maintenance step; PR→APR rename across SA/SM/PO skill files.
5. **Stage 5.8 Express Mode** — after Stage 5.7-E and ≥5 complex skills updated: author `## Express Mode` sections for the 5 candidate skills; implement `src/express.py` + `src/cli.py express` subcommand; BDD tests.
6. **Demo: extend to SwA Phase C** — add a second agent step (SwA, `SwA-PHASE-C-APP` skill) after SA Phase A, producing application-layer entities; exposes handoff event flow between agents.
7. **Stage 5c**: PM agent `result_type=PMDecision` end-to-end validation with a live LLM (PM routing loop without a human).
8. **Stage 5d**: external source adapters (Confluence, Jira, git_source) + `UserUploadAdapter`.
9. **Stage 5e**: Discovery Scan Step 0 full envelope for Stage 3 skill files.
10. **Stage 5.5**: Dashboard (FastAPI + Jinja2 + SSE + Model Explorer).

**Stage 5** — Python implementation. Read `framework/agent-runtime-spec.md` and `framework/orchestration-topology.md` before authoring any `src/` file. Begin with Stage 5a (EventStore completion), then 5b (agent layer). Key implementation dependencies:
- `src/sources/target_repo.py` implements `TargetRepoManager` (multi-repo aware; see Stage 5d)
- `src/agents/learning_store.py` wraps LangGraph `BaseStore` for the learning system (see Stage 4.6c + `framework/learning-protocol.md §12`)
- `src/orchestration/graph_state.py` includes `target_repository_ids` and `primary_repository_id` (see Stage 5c)

**Outstanding retroactive item (complete before or alongside Stage 5e):**
- Discovery Scan Step 0 (five-layer scan per `framework/discovery-protocol.md §2`) not yet added to Stage 3 skill files. Step 0.L is present in all 43 files; the broader Step 0 envelope (engagement profile read, enterprise repo, external sources, target-repo, EventStore state) is missing from Stage 3 skills. See Stage 5e checklist.

### Key decisions already made (do not re-litigate)
- `workflow.db` is **git-tracked** (canonical EventStore). YAML in `workflow-events/` is a projection. See `framework/architecture-repository-design.md §4.2`.
- Framework deploys **one clone per software project**. Target project repos are separate git repos at `engagements/<id>/target-repos/<repo-id>/` (.gitignored). Framework files never enter any target project repo.
- `delivery-repository/` holds **delivery metadata only** (PR records, test reports, branch refs), per target repo in `delivery-repository/repos/<repo-id>/`. Source code lives in target repos.
- **Multi-repo: `target-repository` (singular) is backward-compatible.** Tools treat it as `target-repositories: [{id: "default", primary: true, ...}]`. All `target_repo_tools` functions accept `repo_id=None` (→ primary repo). See `engagements-config.yaml` for multi-repo example.
- **Repository Map (`REPO-MAP`) artifact is required for multi-repo engagements.** PM bootstraps registry section; SA completes dependency map + bounded-context allocation. Schema: `framework/artifact-schemas/repository-map.schema.md`.
- **Git worktrees are non-negotiable for DE and DO when writing to target repos.** Each agent (DE/DO) gets its own git worktree per sprint (created via `TargetRepoManager.create_worktree()`), preventing cross-contamination between concurrent agents. Sprint close merges worktrees back to the branch tracked by the engagement. This is the 2026 standard for safe multi-agent code modification.
- **Learning store uses LangGraph `BaseStore` at runtime** with file-based `learnings/` as durable serialisation. Semantic retrieval tier is optional (enterprise corpus ≥ 50 entries + `sqlite-vec` available). Cross-agent learnings flow through enterprise promotion and PM's `cross-role-learnings/` index.
- Change Record (Phase H) is produced by **SA** (not PM). PM produces intake record only.
- Algedonic triggers in `algedonic-protocol.md` are the canonical list. Skill files reference them by ID (e.g., ALG-001); they do not redefine them.
- **`regenerate_macros` is NOT an agent-facing tool.** It is auto-triggered transparently by all four write paths: (1) `write_artifact` in `write_tools.py` — when content contains a `§display ###archimate` block; (2) `model_create_entity` MCP tool in `entity.py` — always after successful write; (3) `model_tools_refresh` MCP tool — always on explicit refresh; (4) `_watcher_loop` in `watch_tools.py` — after detecting any file change in monitored paths. `register_diagram_tools()` intentionally omits it. Agents never need to call it; they just write entity files and the macro library stays in sync.
- **Diagram authoring:** agents write PUML source text directly; runtime wiring (LangGraph + PydanticAI + MCP) binds concrete write/query/verify tool functions. For model MCP this is `model_create_diagram` (+ `model_query_*`, `model_verify_*`, and `model_create_entity`/`model_create_connection` where required). Diagram/skill docs describe intent and constraints; code owns callable signatures.
- **Model MCP tool surface is now explicit and grouped by intent.** Discovery/search/filter/query: `model_query_stats`, `model_query_list_artifacts` (supports `fields` projection), `model_query_search_artifacts` (supports `prefer_record_type`, `strict_record_type`, and `fields` projection), `model_query_count_artifacts_by`, `model_query_read_artifact`, `model_query_find_connections_for`, `model_query_find_neighbors`; validation: `model_verify_file`, `model_verify_all`; deterministic model writing: `model_write_help`, `model_create_entity`, `model_create_connection`, `model_create_diagram` (dry-run first by default).
- **Runtime search-space constraints are now explicit and non-optional.** Per-role skill inventories are kept small (target <=12) and runtime injects one skill at a time (`active_skill_id`) rather than a role's full skill corpus. Tool exposure is role-scoped and budgeted (<=30 per agent, preferred 12-26). Complexity classes remain the Layer 3 control: `simple <=600`, `standard <=1200`, `complex <=2000` with hard-stop handling when exceeded.
- **Reusable skill-core plus code-bound workflow control is now explicit policy.** Skill files are treated as reusable procedural/output contracts; orchestration/routing code is treated as the executable state machine and gate authority. This allows reuse across entry points/profiles without weakening governance.
- **Stage 4.9 entities/connections/diagrams are living specifications, not a frozen design.** They will and should change during Stage 5 implementation as design decisions are refined. The model-first discipline applies in both directions: (a) forward — Stage 5 code divergences update the entity files first; (b) reverse — reverse-architecture skill output populates entity files which then drive Stage 5 implementation. Requirements (REQ, CST, PRI) are also subject to revision as implementation reveals constraints. The architecture repository always leads the code.
- **Every engagement repository mutation must be event-sourced.** `ArtifactReadWriterPort.write()` emits `artifact.created` or `artifact.updated` (with `source_evidence` for reverse-arch inferred entities). User file uploads emit `upload.registered`. Reverse-architecture scan evidence emits `source.scanned`. User confirmation of inferred entities emits `entity.confirmed`. Events reference file paths; files hold content. This is the invariant that makes engagement state fully replayable from the EventStore alone. See §4.9h for full event taxonomy and payload contracts.
- **Workflow events have a three-layer emitter hierarchy.** (1) **Orchestration layer** (LangGraph nodes + EngagementSession) emits lifecycle events: `engagement.started`, `sprint.started`, `sprint.close`, `phase.entered`, `phase.transitioned`, `phase.suspended`, `phase.resumed`, `algedonic.escalated`, `specialist.completed`, `review.sprint-closed`, `engagement.completed`. These are graph state transitions — no agent reasoning is involved. (2) **PM agent tools** (`pm_tools.py`) emit decision events: `specialist.invoked`, `gate.evaluated`, `cq.batched`, `decision.recorded`, `review.pending`. These are PM-reasoned decisions materialised as events. (3) **Specialist agent tools** emit artifact/interaction events: `artifact.created/updated`, `handoff.created`, `cq.raised`, `algedonic.raised`, `source.scanned`, `entity.confirmed`, `file.referenced`. Each node function receives `event_store: EventStorePort` directly alongside `SDLCGraphState` — it does not go through an agent to emit its lifecycle events.
- **EventStore snapshots are mandatory.** Two `snapshots` table in SQLite; full replay is for integrity checks and disaster recovery only. Normal startup uses `replay_from_latest_snapshot()`. Situative triggers: `engagement.started`, `gate.evaluated` (passed), `sprint.close`, `review.sprint-closed`, `artifact.promoted`. Periodic trigger: every 100 events (configurable). This keeps startup time bounded regardless of engagement length.

---

## Guiding Principles for Authoring Agent & Skill Files

1. **Every directive in a skill file is a prompt engineering decision.** Write it as you would write a system prompt: precise, unambiguous, testable.
2. **Schemas before skills.** Never author a skill that produces or consumes an artifact whose schema doesn't yet exist.
3. **Artifacts are tailored TOGAF.** Artifact selection and design is a streamlined version of the full TOGAF artifact set and must be well-researched and grounded in the ADM specification.
4. **One accountable agent per artifact per phase.** If two agents could plausibly claim ownership, resolve it in the RACI matrix before proceeding.
5. **Feedback loops must have termination conditions.** Every `## Feedback Loop` section must specify a maximum iteration count and an escalation path.
6. **Algedonic triggers are not optional.** Every skill file must have a `## Algedonic Triggers` section, even if the content is "none identified for this skill" — the explicit absence is itself a design decision.
7. **The summary header is a contract.** The artifact summary format defined in `repository-conventions.md` must be produced faithfully by every skill that generates an artifact. It is the unit of inter-agent communication at normal operating tempo.
8. **Knowledge self-assessment is mandatory before every binding output.** Every skill file must have a `## Knowledge Adequacy Check` section specifying: the domain knowledge required, predictable knowledge gaps for that skill, and the conditions under which a Clarification Request (`CQ`) must be raised rather than an assumption made. Agents must never silently assume facts about the user's specific domain, organisation, or system. Every assumption must be documented in the artifact's `assumptions` field. This is governed by `framework/clarification-protocol.md`.
9. **Engagements may start at any ADM phase.** The system must support users who bring existing artifacts, designs, requirements, or codebases. Every AGENT.md must describe how the agent behaves at each of the seven entry points defined in `framework/sdlc-entry-points.md`. The Project Manager skill `master-agile-adm.md` must implement the full entry assessment procedure including the Engagement Profile and Entry Assessment Report.
10. **Discovery before CQs.** Every skill that begins phase work must execute the Discovery Scan per `framework/discovery-protocol.md §2` as its first step. The five-layer scan covers: engagement work-repositories, enterprise repository, configured external sources (Confluence, Jira, etc.), target project repository, and EventStore state. CQs are raised only for information that cannot be obtained or inferred from available sources. Every sourced or inferred artifact field must be annotated. The system must be able to start with very little explicit input — it discovers what is available, maps it to ADM schema fields, and asks specifically for what is genuinely missing. This makes the system useful from any starting state, not only from a clean-slate EP-0.

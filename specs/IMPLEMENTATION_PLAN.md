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
- [ ] **`src/events/export.py`**: implement `write_event_yaml()` with full PyYAML serialisation; implement `import_from_yaml()` for disaster recovery round-trip
- [ ] **`src/events/migrations/`**: Alembic migration baseline — `alembic.ini` and initial migration script for the events + snapshots tables
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
- [x] **`src/agents/roles.py`**: per-role builder functions `build_pm_agent`, `build_sa_agent`, `build_swa_agent`, `build_de_agent`, `build_do_agent`, `build_qa_agent`, `build_po_agent`, `build_smm_agent`, `build_csco_agent` — each calls `build_agent()`, registers universal tools + role-appropriate write tool + PM decision tools (PM only). Replaces individual per-role `.py` modules (unified pattern).
- [x] **`src/agents/__init__.py`**: `AGENT_IDS`, `get_agent(agent_id, root, llm_config)` lazy singleton cache, `_build_for_id()` dispatcher. `AGENT_REGISTRY` populated on demand.
- [ ] **`src/agents/tools/target_repo_tools.py`**: multi-repo aware target-repo tools (blocked on `TargetRepoManager` from Stage 5d)
- [ ] **`src/agents/tools/diagram_tools.py`**: `regenerate_macros`, `validate_diagram`, `render_diagram` (blocked on diagram production sprint)

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

- [ ] **`src/sources/base.py`**: adapter base class — `SourceAdapter.query(query: str) → str`; all queries emit `source.queried` EventStore event; adapter is read-only
- [ ] **`src/sources/confluence.py`**, **`src/sources/jira.py`**, **`src/sources/git_source.py`**: external source implementations; wired to `external-sources/<id>.config.yaml`
- [ ] **`src/sources/target_repo.py`**: `TargetRepoManager` — multi-repo aware clone manager; reads `engagements-config.yaml` to build repo registry; `clone_or_update(repo_id)` clones/fetches to `engagements/<id>/target-repos/<repo-id>/`; `get_clone_path(repo_id) → Path`; `check_access(repo_id, agent_role) → Literal["read-write","read-only","none"]`; `get_primary_id() → str | None`; **`create_worktree(repo_id, branch_name) → Path`** (creates a git worktree at `engagements/<id>/target-repos/<repo-id>-wt-<branch>/` for agent-isolated code changes — non-negotiable for safe concurrent agent writes; DE and DO each get their own worktree per sprint; merged back by PM on sprint close); backward-compatible: `target-repository` (singular) registered as `id="default"`. Never commits framework files into any target repo.

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

**Immediate next items:**
- Stage 5a remaining: Alembic migration baseline.
- Stage 5b remaining: `get_memento_state()`/`save_memento_state()` tools in `universal_tools.py` (MementoStore integration); `src/agents/tools/target_repo_tools.py` stub (multi-repo scan + worktree, blocked on TargetRepoManager from 5d).
- Stage 5c remaining: PM agent `result_type=PMDecision` wiring needs end-to-end validation with a live LLM; `build_sdlc_graph` integration test (graph compile + single PM→SA→gate cycle).
- Stage 5d: `src/sources/target_repo.py` (TargetRepoManager with worktree support), external source adapters.
- Stage 5e: Add Layer 1-5 envelope to remaining ~37 skill files that only have Step 0.L + Step 0.M.

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

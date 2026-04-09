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
- **LLM backend:** Anthropic Claude API (claude-sonnet-4-6 for primary agents; claude-haiku-4-5 for lightweight routing/summarisation tasks)
- **Leaf reasoning engine:** PydanticAI at leaf nodes only (schema-constrained specialist execution and tool use)
- **Version control:** Git (all agent definitions, skill files, framework documents, and work-repository schemas are tracked)
- **Artifact persistence:** File-based work-repositories (git-tracked) per engagement under `engagements/<id>/work-repositories/`
- **Workflow state persistence:** SQLite event store (`engagements/<id>/workflow.db`) — **canonical, git-tracked**; Pydantic-validated, append-only, managed by the `EventStore` class in `src/events/`; YAML projection in `engagements/<id>/workflow-events/` also git-tracked for human readability and PR review; schema managed by Alembic migrations
- **Enterprise architecture persistence:** `enterprise-repository/` (embedded) or external EA system via source adapter; configurable via `enterprise-repository-config.yaml`
- **External source adapters:** Read-only, configured in `external-sources/<source-id>.config.yaml`; supports Confluence, Jira, external Git, SharePoint, and generic REST APIs
- **Target project repositories (multi-repo support):** Engagements may register one or more target repositories in `engagements-config.yaml`. The `target-repositories` list (or backward-compatible singular `target-repository`) associates each repo with an `id`, `label`, `role` (microservice | microfrontend | bff | event-store | shared-lib | infrastructure | api-gateway | data-platform | shared-schema | monolith), and `domain` (bounded context). Local clones live at `engagements/<id>/target-repos/<repo-id>/` (.gitignored). Multi-repo engagements require a `repository-map.md` artifact; see `framework/artifact-schemas/repository-map.schema.md`. The `delivery-repository/` holds delivery metadata (PR records, branch refs, test reports) per repo, not code.

---

## Implementation Stages

### Stage 1 — Foundation Artifacts (Complete)
> Everything else references these. Complete before authoring any agent or skill files.

- [x] **Scaffold repository directory structure**
  - `enterprise-repository/` (embedded mode, configurable via `enterprise-repository-config.yaml`)
  - `engagements/<id>/` per-engagement directories with work-repositories, event log, and log subdirectories
  - `engagements/<id>/target-repos/<repo-id>/` entry in `.gitignore` (local clones of target projects; separate repos); backward-compat `target-repo/` also gitignored
  - `external-sources/` source adapter configuration
  - `src/events/` EventStore Python module skeleton
  - `enterprise-repository-config.yaml` and `engagements-config.yaml` (includes target-repository per engagement)
- [x] Author `framework/agile-adm-cadence.md`
  - Phase → iteration mapping (four iteration types: context, definition, transition, governance)
  - Sprint types (Architecture Sprint, Business Sprint, Solution Sprint)
  - Phase transition triggers and gates
  - Artifact readiness criteria
  - **ADM iteration model: non-linear, iterative phase re-entry** (§5.3–5.4)
  - Phase revisitation triggers and visit count tracking
  - Architecture Repository structure (enterprise, engagement, external) (§12)
- [x] Author `framework/raci-matrix.md`
  - Per-artifact, per-phase responsibility table
  - Definitions of ● (accountable/owns), ○ (consulted/contributes), — (not involved)
- [x] Author `framework/repository-conventions.md`
  - Directory ownership and path governance rules (engagement-scoped work-repositories)
  - Artifact versioning convention (semver for architecture artifacts)
  - Artifact summary header format (required fields, including `pending-clarifications` and `assumptions`)
  - Confidence-threshold retrieval protocol (full spec)
  - Cross-role handoff event format
  - **External source query protocol** (§10)
  - **Enterprise vs. engagement artifact lookup rules** (§11)
  - **Enterprise promotion procedure** (§12)
- [x] Author `framework/algedonic-protocol.md`
  - Trigger taxonomy and severity classification (6 categories, 18 triggers)
  - Escalation target map per trigger class (includes User as target for KG category)
  - Failsafe control topology for high-urgency situations
  - Re-integration procedure
- [x] Author `framework/artifact-schemas/` — one schema file per major handoff artifact:
  - `architecture-vision.schema.md`
  - `business-architecture.schema.md`
  - `application-architecture.schema.md`
  - `data-architecture.schema.md`
  - `technology-architecture.schema.md`
  - `implementation-plan.schema.md`
  - `test-strategy.schema.md`
  - `safety-constraint-overlay.schema.md`
  - `architecture-contract.schema.md` (added — required by Phase G governance)
  - `change-record.schema.md` (added — required by Phase H)
  - `requirements-register.schema.md` (added — required by Requirements Management)
- [x] Author `framework/clarification-protocol.md`
  - Knowledge adequacy self-assessment decision rule
  - Clarification Request (CQ) format and routing rules
  - Work suspension and partial-progress rules
  - Answer integration procedure
  - Skill file `## Knowledge Adequacy Check` section requirement
- [x] Author `framework/sdlc-entry-points.md`
  - Seven entry point classifications (EP-0 through EP-H)
  - Engagement Profile artifact format
  - Warm-start artifact ingestion and validation procedure
  - Entry Assessment Report format (batched CQ delivery to user)
  - Reverse architecture reconstruction procedure (EP-G)
  - Mid-engagement re-entry procedure
- [x] Author `framework/architecture-repository-design.md`
  - Three-scope architecture data model (Enterprise, Engagement, External)
  - Git repository layout options (embedded, submodule, external enterprise; single vs. multi-repo engagements)
  - **SQLite-canonical EventStore** — Pydantic-validated, ACID-protected, the sole write path agents cannot bypass; `.gitignored`
  - **YAML audit export** — derived git-tracked record committed at sprint boundaries; serves as disaster-recovery backup; agents cannot corrupt it (only EventStore writes to `workflow-events/`)
  - EventStore API (`src/events/`) with Alembic migration management (all engagements share same schema; each bootstrapped on creation)
  - Engagement bootstrap procedure (§4.8)
  - Log directory record vs SQLite event distinction (§4.7): markdown records in `clarification-log/`, `handoff-log/`, `algedonic-log/` are detailed prose content; SQLite events are minimal workflow signals
  - Event taxonomy (cycle, phase, gate, sprint, artifact, handoff, CQ, algedonic, source events)
  - ADM multi-cycle and multi-level architecture model (Strategic/Segment/Capability)
  - Enterprise Promotion Protocol
- [x] Create `.gitignore` (excludes `target-repos/` and `target-repo/`, SQLite WAL/journal temporaries, credentials, Python artifacts; `workflow.db` is NOT excluded — it is git-tracked as the canonical event store)
- [x] Commit as `stage-1-foundation`

---

### Stage 2 — Project Manager Master Skill (Complete)
> The orchestration layer. Must exist before any other agent can be run end-to-end.

Every AGENT.md must include: role mandate, phase coverage, repository ownership, entry point behaviour (per EP-0 through EP-H), and cross-references to all skill files.  
Every skill file must include: `## Inputs Required`, `## Knowledge Adequacy Check`, `## Algedonic Triggers`, `## Feedback Loop`, and `## Outputs`.

- [x] Author `agents/project-manager/AGENT.md`
  - Role mandate (System 3 / VSM), phase coverage, repository ownership
  - Entry-point behaviour for all 7 EPs (EP-0 through EP-H)
  - Authority constraints (cannot override CSCO, cannot make architecture decisions)
  - Communication topology (user ↔ PM ↔ all agents)
  - EventStore contract (events emitted and consumed)
  - Downstream agent governance constraints
- [x] Author `agents/project-manager/skills/master-agile-adm.md`
  - Full Agile ADM cadence operationalisation (7-phase engagement procedure)
  - Engagement bootstrap procedure (directory structure, EventStore init, git commit)
  - Sprint planning, in-sprint coordination, sprint closeout with EventStore commit
  - Phase gate evaluation procedure (checklist, G-holder vote collection, gate records)
  - CQ lifecycle management (batching, routing, tracking, resumption, ALG-016 trigger)
  - Algedonic signal handling (routing, halts, resolution)
  - Phase revisit detection and scope constraint
  - Engagement close and enterprise promotion initiation
- [x] Author remaining PM skills:
  - `phase-a.md` — Scoping Interview (EP-0), Entry Assessment Report, Phase A gate coordination, SoAW
  - `phase-e-f.md` — Work Package Catalog, Risk Register, Architecture Roadmap, Implementation Plan, Solution Sprint Plan
  - `phase-g.md` — Solution Sprint governance, Architecture Contract oversight, Governance Checkpoint Records, Phase G exit
  - `phase-h.md` — Change Record intake, change classification, phase return coordination, emergency change procedure
  - `retrospective-knowledge-capture.md` — Sprint retros, Engagement Retrospective, Enterprise Promotion Review, Knowledge Base stewardship
- [x] Commit as `stage-2-pm-master`

---

### Stage 3 — Primary Implementation Chain (in phase order)

> Author in dependency order. Each role's skills reference the framework and the previous role's output schemas.

**Additional framework document authored as part of Stage 3:**
- [x] `framework/discovery-protocol.md` — Discovery-first protocol: five-layer scan (engagement state, enterprise repo, external sources, target-repo, EventStore); gap assessment format; CQ generation rules; annotation conventions; phase-revisit discovery; skill file requirements

**Branch: `agent/solution-architect`**
- [x] `agents/solution-architect/AGENT.md`
- [x] Skills: `phase-a.md`, `phase-b.md`, `phase-c-application.md`, `phase-c-data.md`, `phase-h.md`, `requirements-management.md`

**Branch: `agent/software-architect`**
- [x] `agents/software-architect/AGENT.md`
- [x] Skills: `phase-d.md`, `phase-e.md`, `phase-f.md`, `phase-g-governance.md`, `phase-h.md`

**SA → SwA handoff contract validated:** AA schema (§3.2–3.9) maps to TA inputs required table (§2) — all APP-nnn identifiers, IFC-nnn interfaces, and safety-relevance flags flow through. DA DE-nnn entities and classification levels drive TA ADR requirements for data store selection. No schema updates required.

**Branch: `agent/devops-platform`**
- [x] `agents/devops-platform/AGENT.md`
- [x] Skills: `phase-d.md`, `phase-e.md`, `phase-f.md`, `phase-g.md`

**Branch: `agent/implementing-developer`**
- [x] `agents/implementing-developer/AGENT.md`
- [x] Skills: `phase-g.md`, `phase-e-feedback.md`, `phase-f-feedback.md`

**Branch: `agent/qa-engineer`**
- [x] `agents/qa-engineer/AGENT.md`
- [x] Skills: `phase-ef-test-planning.md`, `phase-g-execution.md`, `phase-h-regression.md`

**Merge all stage-3 branches to `stage-3-implementation-chain`** — complete

**Post-authoring review findings addressed:**
- Added `framework/discovery-protocol.md` — the discovery-first, ask-last protocol for all agents
- Added Authoring Rule #12 to `CLAUDE.md` — discovery before CQs
- Added phase-revisit handling to SA AGENT.md §10 (consistent with SwA §5.3)
- Fixed ALG-014 misuse: SwA phase-h.md Step 3b.3 and DE phase-g.md now use ALG-006 for general mid-sprint change conflicts; ALG-014 reserved for Safety-Critical change + CSCO unavailable
- All Stage 3 skill files require retroactive addition of discovery scan Step 0 (per discovery-protocol.md §6) — tracked as first item of Stage 5 clean-up

**Personality layer added (pre-Stage 4, 2026-04-02):**
- `framework/agent-personalities.md` — master framework: L&L + VSM theoretical basis, role taxonomy, 9 personality profiles (7 from specs + PM and QA derived), productive tension protocol, inter-role tension map, skill file requirements
- Added Authoring Rule #13 to `CLAUDE.md` — §11 personality section required in every AGENT.md
- Added `## 11. Personality & Behavioral Stance` to all 6 Stage-3 AGENT.md files (SA, SwA, DevOps, Dev, QA, PM)
- Added `### Personality-Aware Conflict Engagement` subsections to 3 high-tension skill feedback loops: `implementing-developer/skills/phase-g.md`, `software-architect/skills/phase-g-governance.md`, `devops-platform/skills/phase-d.md`
- Stage 4 agents (PO, Sales, CSCO) must also receive §11 sections when authored (personality specs already exist in `specs/agent-personalities/` for all three)

---

### Stage 4 — Framing Layer Agents

**Branch: `agent/product-owner`** — Complete (2026-04-02)
- [x] `agents/product-owner/AGENT.md`
- [x] Skills: `phase-a.md`, `phase-b.md`, `phase-h.md`, `requirements-management.md`, `stakeholder-communication.md`

**Branch: `agent/sales-marketing`** — Complete (2026-04-02)
- [x] `agents/sales-marketing/AGENT.md`
- [x] Skills: `phase-a-market-research.md`, `phase-a-swot.md`, `requirements-management-feedback.md`

**Branch: `agent/csco`** — Complete (2026-04-03)
- [x] `agents/csco/AGENT.md`
- [x] Skill: `stamp-stpa-methodology.md` (master methodology reference)
- [x] `gate-phase-a.md` — Phase A gate review (Prelim→A and A→B votes; SCO Phase A baseline; STAMP Level 1)
- [x] `gate-phase-b.md` — Phase B gate review (B→C vote; SCO Phase B update; STAMP Level 1 process analysis)
- [x] `gate-phase-c.md` — Phase C gate review (C→D vote; SCO Phase C update; STAMP Level 2 application/data)
- [x] `gate-phase-d.md` — Phase D gate review (D→E vote; SCO Phase D update; STAMP Level 3 technology)
- [x] `gate-phase-g.md` — Phase G spot-checks (Mode 1: PM-requested; Mode 2: QA CA review) + G-exit gate vote
- [x] `gate-phase-h.md` — Phase H change safety impact classification (Safety-Neutral / Safety-Relevant / Safety-Critical) + H gate vote + SCO update
- [x] Skill: `incident-response.md` — safety incident and algedonic response; S1/S2 containment directive; SCO gap analysis; regulatory notification assessment; post-incident safety finding

**Merge all stage-4 branches to `stage-4-framing-layer`** — Complete (2026-04-03)

---

### Stage 4.5 — Cross-Cutting Framework Extensions (Complete)

> Framework documents underpinning diagram consistency, artifact traceability, agent-profile condensation, and coding-standards enforcement. No Python code — framework specs, schemas, and retroactive skill-file patches only.

#### 4.5a — Diagram Conventions Framework
- [x] `framework/diagram-conventions.md` — authored (§1 authoring model; §2–§4 ontological catalog structure and lifecycle; §5 D1–D6 reuse + authoring protocol; §6 write authority; §7 PUML templates × 6 diagram types; §8 `_macros.puml`; §9 element record format; §10 ID namespace reference table)
- [x] `framework/artifact-schemas/diagram-catalog.schema.md` — updated to ERP v2.0 frontmatter model (no `diagrams/index.yaml`; diagram artifacts are file-first `.puml` / `.md` records discovered via ModelRegistry)
- [x] `framework/algedonic-protocol.md` — ALG-C01–ALG-C04 added (catalog duplicate ID, unauthorised catalog write, broken cross-ontology link, `_macros.puml` out of sync)

#### 4.5b — Artifact Reference Format Extension
- [x] `framework/repository-conventions.md` §13 authored — Canonical Artifact Reference Format (in-text Markdown reference, `references:` frontmatter list, handoff `artifact_refs:` field, `## Inputs Required` table format, artifact-id assignment convention)

#### 4.5c — Diagram-Aware Discovery Protocol Extension
- [x] `framework/discovery-protocol.md` §8 authored — Step 0.D (Diagram Catalog Lookup): sub-step inserted after Step 0 source scan; specifies ontological-layer identification, sub-catalog reads, annotation, and D1–D6 trigger conditions

#### 4.5d — Coding Guidelines and Standards Discovery Protocol
- [x] `framework/discovery-protocol.md` §9 authored — Step 0.S (Standards and Coding Guidelines Discovery): mandatory for SwA / DE / DO; scans `technology-repository/coding-standards/` and `enterprise-repository/standards/`; gap record COD-GAP-001 + CQ if no standards found

#### 4.5e — Agent Profile Condensation: Layer 1 / Layer 2 Design
- [x] `framework/agent-runtime-spec.md` §2 updated — Layer 2 extraction now targets `### Runtime Behavioral Stance` subsection only (not full §11); required form (default bias + conflict posture + cross-cutting rule); token budgets: L1 ≤150 tokens, L2 ≤350 tokens, L3 by complexity class (simple ≤600, standard ≤1200, complex ≤2000)
- [x] `### Runtime Behavioral Stance` subsection authored and added to all 9 AGENT.md §11 sections (SA, SwA, DO, DE, QA, PM, PO, SM, CSCO)
- [x] `complexity-class:` field added to all skill file YAML frontmatter
- [x] `## Artifact Discovery Priority` section added to all 9 AGENT.md files
- [x] `framework/agent-index.md` updated v1.0.0 → v1.1.0: PO / SM / CSCO skill routing tables added; Stage 4 "pending" annotations removed; SM skill ID bugs fixed (`SM-MARKET-RESEARCH` → `SM-PHASE-A-MR`, `SM-SWOT` → `SM-PHASE-A-SWOT`)

#### 4.5f — Retroactive Diagram and Reference Updates to Existing Skill Files
- [x] Diagram production steps D1–D6 added to SA `phase-b.md` (3 diagram steps: capability map, process catalog, value stream), `phase-c-application.md` (2 steps: component model, interaction flows), `phase-c-data.md` (1 step: canonical data model)
- [x] Diagram production steps D1–D6 added to SwA `phase-d.md` (Step 0.D + 2 diagram steps: domain model, technology-layer), `phase-e.md` (1 diagram step: API contract sequence)
- [x] Step 0.S (Standards and Coding Guidelines Discovery) added to SwA `phase-g-governance.md`, DE `phase-g.md`, DO `phase-g.md`

**Committed as `stage-4.5-framework-extensions`** (batched with Stage 4.6b, 2026-04-03)

---

### Stage 4.6 — Learning Protocol (Reflexion-Inspired Agent Memory) (Complete)

> Structured per-role learning repositories so agents record mistakes and retrieve relevant corrections at the start of each skill invocation. Framework documents in 4.6a; retroactive skill-file patches in 4.6b; Python tooling deferred to Stage 5b.

#### 4.6a — Framework Documents
- [x] `framework/learning-protocol.md` — authored (11 sections: trigger conditions §3; entry format §4; Step 0.L retrieval §5; sprint-level synthesis §6; enterprise promotion §7; tool spec §8; EventStore events §9; anti-patterns §10)
- [x] `framework/artifact-schemas/learning-entry.schema.md` — authored (frontmatter schema, body section rules, 9 `record_learning()` validation rules, example entry)

#### 4.6b — Retroactive Skill File Patches
- [x] **Step 0.L** (Learnings Lookup via `query_learnings`) added as first sub-step of Step 0 in all 43 skill files
- [x] **`### Learning Generation`** subsection added to `## Feedback Loop` in all 43 skill files (trigger table + `record_learning()` call spec with `artifact-type`, `error-type`, and correction format)
- [x] PM `master-agile-adm.md` — sprint retrospective updated with cross-role synthesis step (invokes `record_learning(trigger_event="synthesis")` per `framework/learning-protocol.md §6`)

**Committed as `stage-4.6-learning-protocol`** (batched with Stage 4.5f, 2026-04-03)

#### 4.6d — Learning Protocol 2026 Alignment + Harness Research (Complete — same session)

Research conducted on: Anthropic memory_20250818 tool, MIRIX 6-component memory, Mem0 multi-level structure, LangGraph BaseStore namespacing, OpenHarness `skills` subsystem, 30-tool accuracy limit, git worktree isolation, AutoDream consolidation mapping. Key validated findings incorporated into §12; design gaps documented as future considerations.

Conceptual basis updated and new framework sections authored:

- [x] `framework/learning-protocol.md` updated v1.0.0 → v1.1.0:
  - **§1 Conceptual Basis** extended with 2026 research and production patterns: Claude Code file-based memory system (validates our approach), LangGraph BaseStore (Stage 5 implementation guidance), A-MEM graph connectivity (`related` links in index), memory consolidation as first-class operation
  - **§2.3 Index format** extended with `related: []` field (A-MEM graph traversal pointers; set at synthesis and promotion time, not automatically) and explicit `synthesis-superseded: null` field
  - **§9 `query_learnings` spec** updated: graph expansion via `related` links (up to 2 extra results when primary filter < 3); semantic supplement tier (enterprise corpus ≥ 50 entries + sqlite-vec available → top-1 embedding match above 0.75 cosine threshold)
  - **§12 Stage 5 Implementation Guidance** authored (new section): LangGraph `SQLiteStore` backend with `(engagement_id, agent_role, "learnings")` namespace tuples; Anthropic `memory_20250818` tool as optional alternative backend; durable file serialisation contract; AutoDream→PM-synthesis mapping; semantic retrieval tier (sqlite-vec, sentence-transformers/all-MiniLM-L6-v2); graph expansion procedure; cross-agent visibility via PM cross-role synthesis index; consolidation growth trigger; MIRIX 6-component gap analysis (current protocol covers procedural memory only)

#### 4.6c — Python Tooling (deferred to Stage 5b)

Implemented alongside other `universal_tools.py` additions in Stage 5b:

- [ ] `src/tools/universal_tools.py` — add `query_learnings()` and `record_learning()` (spec below; see also Stage 5b tool list)
- [ ] `src/models/learning.py` — `LearningEntry` Pydantic model (fields: `learning_id`, `agent`, `phase`, `artifact_type`, `trigger_event`, `error_type`, `importance`, `applicability`, `generated_at_phase`, `generated_at_sprint`, `generated_at_engagement`, `promoted`, `synthesis_superseded`, `synthesised_from`, `related: list[str]`, `trigger_text`, `correction_text`, `context_text`)
- [ ] EventStore event models — add `learning.created`, `learning.synthesised`, `learning.promoted` to `src/events/`

**`query_learnings` spec:** See `framework/learning-protocol.md §9` and §12.1–12.2. Reads from LangGraph `BaseStore` (runtime) and falls back to file-based index on cold start. Applies metadata filter, graph expansion (`related` links), and optional semantic supplement tier (enterprise corpus ≥ 50 entries + `sqlite-vec` available). Returns top 5 `## Correction` texts.

**`record_learning` spec:** validates entry against schema (9 rules); assigns next `<ROLE>-L-NNN` id; writes to LangGraph `BaseStore` AND writes `agents/<agent>/learnings/<ROLE>-L-NNN.md` + updates `index.yaml` (durable serialisation); emits `learning.created` EventStore event; raises `LearningSchemaError` on validation failure.

**`src/agents/learning_store.py`:** `LearningStore` wraps LangGraph `BaseStore`. Namespace: `(engagement_id, agent_role, "learnings")`. Startup: calls `rebuild_from_files()` if store is empty to rehydrate from `learnings/index.yaml`. Implements `query(phase, artifact_type, domain, expand_related=True) → list[str]` and `record(entry: LearningEntry) → str`. Optional semantic tier gated on `sqlite-vec` availability check at init time. Optional `memory_20250818` backend: if configured, the store uses Anthropic's official memory tool type (client-side) instead of direct SQLiteStore — enables the same memory patterns Claude Code uses internally; governed by `framework/learning-protocol.md §12.1`.

---

### Stage 4.7 — Multi-Target-Repository Support (Complete — same session)

> Cross-cutting framework extension enabling engagements that span multiple target repositories (microservices, CQRS, microfrontends, multi-product change requests).

- [x] `framework/artifact-schemas/repository-map.schema.md` — authored: Repository Map (`REPO-MAP`) artifact schema; §3.2 repository registry with role taxonomy (10 roles); §3.3 inter-repo dependency map with 7 dependency types; §3.4 bounded-context allocation table; §3.5 change-impact matrix (for Phase H multi-repo CRs); §3.6 access control summary; §4 validation rules (exactly-one-primary, no duplicate IDs, all config repos represented); §5 discovery annotations; §6 file path and ownership
- [x] `engagements-config.yaml` — updated: `target-repositories` (plural list) format added alongside backward-compatible `target-repository` (singular); role taxonomy documented; multi-repo example (microservices + shared-schema engagement) added as inline comment; `local-clone-path` updated to `target-repos/<id>/` pattern
- [x] `framework/discovery-protocol.md §2 Layer 4` — updated: multi-repo procedure (load Repository Map first; `list_target_repositories()` call; per-repo discovery steps 4–10; cross-repo synthesis for shared-dependency divergence, undocumented integration contracts, circular dependencies); annotation updated to `[inferred: target-repo:<id> scan]`

**Framework design decisions recorded:**
- `target-repository` (singular) is treated by all tools as `target-repositories: [{id: default, primary: true, ...}]` — fully backward-compatible.
- All `target_repo_tools` functions require explicit `repo_id` parameter in multi-repo engagements; default to primary repo only when exactly one repo is registered.
- Repository Map is produced at engagement bootstrap by PM (registry section) and completed by SA during Phase A/B (dependency map + bounded-context allocation).
- Delivery-repository metadata is per-repo: `delivery-repository/repos/<repo-id>/` subdirectory tracks PRs, branch refs, test reports for each target repo independently.

---

### Stage 4.8 — Entity Registry Pattern (ERP) Framework

> One file per entity or connection instance, organised by ArchiMate layer/aspect (all diagram language types are subsumable under ArchiMate taxonomy). No `_index.yaml` files — frontmatter is the single source of truth; the ephemeral `ModelRegistry` is built at startup by scanning frontmatter. All relational information lives in typed connection files (sibling `connections/<diagram-language>/<connection-type>/` directories). Entity files contain no cross-references. `§content` and `§display` sections (delimited by `<!-- §<name> -->` markers) separate semantic content from per-diagram-language rendering specs (`### <language-id>` H3 subsections within `§display`).

**Diagram rendering strategy:** Diagrams are views over the model. `_macros.puml` is generated by scanning entity `§display ###archimate` blocks — each entity's artifact-id becomes its PUML alias. For ER diagrams, `generate_er_content(entity_ids)` and `generate_er_relations(connection_ids)` read entity/connection `§display ###er` blocks and return PUML class declarations and cardinality lines respectively. For sequence, activity, and use-case diagrams, participant labels and flow lines are derived from corresponding `§display ###sequence/activity/usecase` blocks. `validate_diagram` confirms all PUML aliases resolve to existing entities in ModelRegistry. The model-first rule (ERP-2/§9 of artifact-registry-design.md) prohibits diagram elements with no backing entity; entities may freely exist without being in any diagram.

#### 4.8a — Framework Specification (Complete)

- [x] `framework/artifact-registry-design.md` v2.0.0 — ERP master spec: ArchiMate-organised directory structure (motivation/strategy/business/application/implementation + technology-repository); full entity type registry covering all 40+ ArchiMate elements across all layers/aspects (§4); connection type registry for archimate/er/sequence/activity/usecase diagram languages (§5); unified file format with `§content` + `§display ###language` sections (§3); ModelRegistry design replacing `_index.yaml` (§6); ID assignment rules (§7); cache-first discovery protocol (§8); model-first rule (§9); tool contracts for `write_artifact`, `read_artifact`, `list_artifacts`, `list_connections` (§10); authoring rules ERP-1 through ERP-6 (§11); migration procedure (§12)
- [x] **Two-scope ID space and promotion design** (§6.1, §7): engagement artifact-IDs are engagement-local only (no cross-engagement uniqueness); enterprise IDs are globally unique, assigned at promotion from `enterprise-repository/governance-log/id-counters.yaml`; `promote_entity` performs deterministic reference sweep (old engagement-ID → new enterprise-ID across all connection files, diagram PUML aliases, inline references) then moves the entity file; Architecture Board members are the only writers to the enterprise repository

#### 4.8b — Entity Conventions Schema (Complete)

- [x] `framework/artifact-schemas/entity-conventions.md` v2.0.0 — unified entity and connection file format: mandatory frontmatter (no `references`, no `diagram-element-id`); `§content` + `§display` section structure with `### language` H3 subsections; properties tables per ArchiMate entity type across all layers; five exemplar files (capability, app-component, data-object, archimate connection, er connection)

#### 4.8c — Diagram Conventions Update (Complete)

- [x] `framework/diagram-conventions.md` v2.0.0 — model-driven diagram production: no separate `elements/` catalog directory; `_macros.puml` generated from entity `§display ###archimate` blocks; artifact-ids as PUML aliases; D1–D5 production protocol (query ModelRegistry → verify §display coverage → author PUML → validate → render); `generate_er_content`/`generate_er_relations` tools for ER diagrams; diagram index format (§9); PUML templates updated for all diagram types
- [x] **Diagram referencing design** (§4.1, §9): existing enterprise and prior-engagement diagrams are referenced in-place via `entry_type: reference` entries in `diagrams/index.yaml` — never copied; `render_diagram` on a reference entry renders the source `.puml` at its original path; engagement bootstrap creates catalog structure + runs `regenerate_macros()` only, no entity import; `promote_diagram` moves (not copies) promoted diagrams to enterprise path

#### 4.8d — Artifact Schema and Framework Doc Updates (Complete — 2026-04-03)

The domain artifact schemas and cross-cutting framework docs updated to align with the ERP v2.0 design.

- [x] `framework/artifact-schemas/business-architecture.schema.md` — v2.0.0: refactored to ERP entity-file output; entity paths under `model-entities/` grouping; §display requirements; connections table; ba-overview.md spec
- [x] `framework/artifact-schemas/application-architecture.schema.md` — v2.0.0: refactored; entity paths under `application/`; technology-independence constraint; connections table
- [x] `framework/artifact-schemas/data-architecture.schema.md` — v2.0.0: refactored; DOB entities in `application/data-objects/`; `§display ###er` requirement; ER connections in `connections/er/`
- [x] `framework/artifact-schemas/technology-architecture.schema.md` — v2.0.0: refactored; paths to `model-entities/technology/`; connections in `technology-repository/connections/`
- [x] `framework/repository-conventions.md` — v1.3.0: §2.2 rewritten with `model-entities/` grouping, `diagram-catalog/diagrams/` + `templates/`, no `index.yaml`; §14 ERP Conventions Summary (10 rules)
- [x] `framework/discovery-protocol.md` — Layer 5 updated to `deps.workflow_state`/`WorkflowState`; §8 Step 0.D rewritten to use `list_artifacts`, `list_connections`, `search_artifacts`; D1–D6 → D1–D5; multi-layer ArchiMate examples added
- [x] `framework/agent-runtime-spec.md §6` — v1.1.0: §6.1–6.5 rewritten; discovery/read/learning/interaction/framework tool groups; `write_artifact` with ERP validation; §6.4 new diagram tools (`regenerate_macros`, `generate_er_content`, `generate_er_relations`, `validate_diagram`, `render_diagram`)
- [x] `framework/diagram-conventions.md` — v2.1.0: `index.yaml` removed; `diagrams/` + `templates/` structure; PUML header comment frontmatter spec (§9); D3d updated; D5 "user-facing output only"; "Reading vs. rendering" section
- [x] `framework/artifact-registry-design.md` — v2.1.0: `model-entities/` + `connections/` + `diagram-catalog/` sibling layout; `templates/`; §2.3 technology repo note; §2.4 diagram frontmatter; `learning-entry` path fix
- [x] Retroactive skill file diagram step updates: SA `phase-b.md` (3 steps), `phase-c-application.md` (2 steps), `phase-c-data.md` (1 step); SwA `phase-d.md` (Step 0.D + 2 steps), `phase-e.md` (1 step) — all updated to D1–D4 protocol with `list_artifacts`/`search_artifacts`, no `index.yaml`, `diagram-catalog/diagrams/` paths
- [x] SwA `AGENT.md` §1, §3, §12, `system-prompt-identity` updated: cross-layer diagram scope clarified; ERP v2.0 repository paths; Stage 4.8h forward-reference added
- [x] `CLAUDE.md` repository layout updated: `model-entities/` grouping, `templates/`, no `index.yaml` in enterprise and engagement repos; rule 16 updated

#### 4.8e — CLAUDE.md Authoring Rules (Complete)

- [x] CLAUDE.md updated: ERP authoring rules ERP-1 through ERP-6; stage table updated

#### 4.8f — Reverse Architecture Skills (Complete — 2026-04-03)

> SA and SwA skills for reverse architecture / repository-building engagements (EP-G): Raising a query to the user to provide any textual context, document references, diagrams etc, discovering and structuring the info from the response and its referenced content, scanning existing codebases/systems, and populating the model repository with discovered entities and connections after confirmation, before any diagrams are drawn. This is the primary use case where model-first matters most — the model is built up incrementally from discovered artefacts, and diagrams are produced only after the model achieves sufficient coverage.

- [x] `agents/solution-architect/skills/reverse-architecture-bprelim-a.md` (SA-REV-PRELIM-A) — Phase A and Prelim reverse: discover stakeholders, product-areas / bounded contexts, capabilities, drivers, motivations, constraints, requirements, maturity-levels, meta-information from external sources, user queries, document/diagram references; produce ERP entity files in `motivation/` + `strategy/` directories; generate ArchiMate connections; validate with user max 2 iterations; produce Architecture Vision overview document; raise CQs for gaps.
- [x] `agents/solution-architect/skills/reverse-architecture-ba.md` (SA-REV-BA) — Phase B reverse: discover business entities (actors, roles, processes, functions, services, objects, events) from codebase domain decomposition, ADRs, docs, and user input; produce ERP entity files in `business/` directory; generate ArchiMate connections (assignment, triggering, realization, access); validate with user max 2 iterations; produce BA overview document; flag safety-relevant processes for CSCO.
- [x] `agents/software-architect/skills/reverse-architecture-ta.md` (SWA-REV-TA) — Phase D/E reverse: discover technology layer (nodes, system-software, services, artifacts, networks, interfaces) from IaC, Dockerfiles, CI/CD configs, package manifests; produce ERP entity files in `technology-repository/technology/`; author ADR stubs; generate technology connections; perform Gap & Risk Assessment (lifecycle, security, SIB deviation, ADR coverage); produce TA overview; handoff to SA and CSCO.

---

### Stage 4.8h — SA/SwA Role Boundary Refactoring (Complete — 2026-04-04)

> **Trigger:** During Stage 4.8d diagram-step alignment, it became clear that the current SA/SwA boundary places Phase C (Application + Data Architecture) under SA primary, while SwA also inevitably produces application-layer and data-layer diagrams (sequence, ER, activity) as part of Phase D/E. The two roles produce the same diagram types in adjacent phases, with no clean boundary — a structural conflict, not a convention gap.

#### Problem Statement

The current model:

| Agent | Primary Phases | Consulting |
|---|---|---|
| SA (Solution Architect) | A, B, **C**, H | D, E |
| SwA (Software Architect / PE) | D, E, F, G | **C** |

Phase C produces Application Architecture (APP, IFC, ASV entities; interaction diagrams; sequence diagrams) and Data Architecture (DOB entities; ER/class diagrams). Both artifact types are system-design artifacts, not business-design artifacts. Yet they are owned by the SA — whose primary collaborators are PO (requirements) and SM (market/business drivers) and whose primary domain is the business layer (Phases A/B).

Consequences of the current boundary:
1. **Diagram type collision**: SA produces sequence and ER diagrams in Phase C; SwA produces sequence and ER diagrams in Phase D/E. The same diagram types appear in both roles with overlapping subjects (application components, interfaces, data objects). There is no principled reason to split them across two agents.
2. **SwA is a consumer of artifacts it has no authoring authority over**: SwA must make AA and DA technically feasible (Phase D), yet cannot revise them — only return feedback to SA. This creates a feedback loop that should be a single integrated design process.
3. **SA does two cognitively distinct jobs**: Phases A/B require stakeholder engagement, business-domain reasoning, and collaboration with PO/SM. Phase C requires system-design reasoning and close iteration with SwA on implementation feasibility. These are different disciplines that pull the SA in opposite directions.
4. **`technology-repository` scope is ambiguous**: SwA's work-repository is named for the ArchiMate technology layer but already holds cross-layer implementation artifacts. The naming creates false constraints on SwA's diagram scope.

#### Proposed Model

Architecture work splits into three collaboration zones, not two:

| Zone | ArchiMate Layers | Primary | Active Collaborators |
|---|---|---|---|
| Business-layer architecture (Phases A, B) | Motivation, Strategy, Business | SA | PO, SM, CSCO |
| Application + data architecture (Phase C) | Application, Data | **SwA** | SA (business traceability) |
| Technology / infrastructure (Phase D) | Technology | **SwA** | DO (operational feasibility) |

**SA (Solution Architect)** — owns the full ArchiMate **Motivation, Strategy, and Business layers**. This is not limited to strategic overviews: SA produces the complete business-layer architecture including business objects and their relations, business processes, business functions, business events, business services, business interfaces, business collaborations, business actors, business roles, and representations — in addition to motivation entities (stakeholders, drivers, goals, requirements, constraints, principles) and strategy entities (capabilities, value streams). SA works with PO (requirements) and SM (market/business drivers) as primary collaborators. SA provides business-layer context and traceability validation during Phase C as an active collaborating partner. SA owns Phase H from the business-layer impact perspective.

**SwA (Software Architect / Principal Engineer)** — owns the full ArchiMate **Application and Technology layers**. Covers two adjacent collaboration zones: (1) *application and data architecture* (Phase C) — worked out with SA, who supplies the business-layer model that the application layer must realise; (2) *technology and infrastructure* (Phase D) — worked out with DO, who validates operational feasibility and implementation constraints. SwA governs the full implementation stream (Phases E–G) and provides technical feasibility input during Phase B as a consulting partner.

**The ArchiMate layer boundary is the role boundary:** SA is accountable for every ArchiMate entity at or above the Business layer; SwA is accountable for every ArchiMate entity at or below the Application layer. Phase C is the handoff point — SA's business-layer model (BPR-nnn, BOB-nnn, BSV-nnn, ACT-nnn, etc.) is the primary input SwA uses to derive application components, interfaces, and data objects.

The current model's error is placing Phase C under SA primary. SA's expertise and collaborator network are business-layer-focused; Phase C requires system-design reasoning. Phase C should be SwA primary, with SA as an active partner ensuring application/data architecture correctly realises the business layer.

#### Open Design Decisions (resolve before implementation)

These must be decided before any file changes are made — they have wide-ranging impact on repository layout and agent permissions:

1. **Repository ownership for Phase C entities** (most consequential decision): APP-nnn, IFC-nnn, ASV-nnn, DOB-nnn currently live in `architecture-repository/` (SA-owned). Under the new model they are primary-authored by SwA. Options:
   - **Option A — Co-authorship**: `architecture-repository/` stays SA-owned; SwA is granted write access to `architecture-repository/model-entities/application/` and `architecture-repository/model-entities/data/` subdirectories under a defined tenant model. SA approves Phase C work via review handoff, not direct write prevention.
   - **Option B — Repository split**: SA owns `architecture-repository/` (motivation, strategy, business layers only). SwA owns a new `solution-repository/` (application and data layers). Technology-layer entities stay in `technology-repository/`.
   - **Option C — Repository rename**: Rename `technology-repository/` to `solution-repository/` or `design-repository/`. SwA owns application + data + technology layers in one repo.
   - **Option D — Unified architecture repo, SwA primary**: `architecture-repository/` becomes co-owned; SA is custodian for motivation/strategy/business; SwA is custodian for application/data. Technology-repository stays unchanged.
   - **Recommendation**: Option D preserves the single-repo structure for all ArchiMate model entities (motivation through application/data), avoids a renaming cascade, and makes the handoff model explicit. Ownership governance changes; file layout does not.

2. **Phase H split**: Should SA handle the full Change Record (as currently), or should the Phase H skill be split so SA covers business-layer impact and SwA covers application/data/technology impact? This is a significant skill authoring change.

3. **SwA display-name and invoke-when**: Current "Software Architect / Principal Engineer" is compatible with expanded Phase C scope. No rename needed. `invoke-when` needs updating to include Phase C trigger conditions.

4. **CSCO Phase C gate**: Currently coordinates with SA for Phase C review. Under new model, coordinates with SwA instead. Minor adjustment to `gate-phase-c.md`.

#### Affected Files (complete rework list)

Every file in this list requires review and likely modification. Do not attempt partial updates — the change is load-bearing.

**Framework:**
- `framework/raci-matrix.md` — Phase C ownership (SA → SwA primary; SA → consulting); Phase B (add SwA consulting)
- `framework/agile-adm-cadence.md` — Phase C primary agent; Phase D "inputs" (no longer from SA); Phase B consulting updated
- `framework/agent-index.md` — SA and SwA routing entries, phase lists, invoke-when descriptions
- `framework/repository-conventions.md §2.2` — Phase C entity paths and ownership (depends on Option A–D decision)
- `framework/artifact-registry-design.md §4.x` — owner annotations on application/data-layer entity type tables
- `framework/discovery-protocol.md` — SA and SwA Layer 1 scan priorities
- `framework/sdlc-entry-points.md` — EP-C entry point (currently SA-primary)

**Artifact Schemas:**
- `framework/artifact-schemas/application-architecture.schema.md` — **Owner** field: SA → SwA; consumed-by updated
- `framework/artifact-schemas/data-architecture.schema.md` — **Owner** field: SA → SwA; consumed-by updated
- `framework/artifact-schemas/business-architecture.schema.md` — consumed-by updated (SwA replaces SA for Phase C handoff receipt)

**Agent files — SA:**
- `agents/solution-architect/AGENT.md` — mandate clarified as full Business-layer architect (Motivation + Strategy + Business ArchiMate layers: actors, roles, collaborations, interfaces, processes, functions, events, services, objects, representations — not just strategic overviews); phase coverage updated; entry-point behaviour EP-C removed or changed to consulting; §11 tensions updated
- `agents/solution-architect/skills/phase-c-application.md` — RETIRE (or convert to a narrow SA-consulting skill: verify AA traces to BA — business objects realised by application components, business services realised by application services, etc.)
- `agents/solution-architect/skills/phase-c-data.md` — RETIRE (or convert to a narrow SA-consulting skill: verify DA traces to BA — business objects → data objects)
- `agents/solution-architect/skills/phase-a.md` — update scope reference; minor
- `agents/solution-architect/skills/phase-b.md` — update handoff target (Phase B Business Architecture now hands off to SwA for Phase C, not loops to SA Phase C); confirm that Phase B already covers the full Business Layer (currently it does: ACT, ROL, BPR, BSV, BOB — verify completeness against ArchiMate Business Layer element catalogue)
- `agents/solution-architect/skills/phase-h.md` — scope to business/motivation/strategy impact only; SwA handles application/technology impact assessment (Phase H split)

**Agent files — SwA:**
- `agents/software-architect/AGENT.md` — mandate (add Phase C primary), phase coverage table, repository ownership, system-prompt-identity, entry-point behaviour EP-C added, §11 tensions updated
- NEW: `agents/software-architect/skills/phase-c-application.md` — primary skill; full AA production (app components, interfaces, services, interaction diagrams, sequence diagrams)
- NEW: `agents/software-architect/skills/phase-c-data.md` — primary skill; full DA production (data entities, ER diagrams, data flow diagrams, classification register)
- `agents/software-architect/skills/phase-d.md` — update inputs section (AA and DA are now own-produced, not SA handoffs; validate for consistency not feasibility); Step 0 updated
- `agents/software-architect/skills/phase-e.md` — minor update
- `agents/software-architect/skills/reverse-architecture-ta.md` — may need expansion to cover Phase C reverse (application layer reconstruction)

**Agent files — CSCO:**
- `agents/csco/skills/gate-phase-c.md` — coordination partner changes from SA to SwA

**Root files:**
- `CLAUDE.md` — repository layout, agent phase tables, authoring rules referencing Phase C ownership
- `specs/IMPLEMENTATION_PLAN.md` — agent roles table (line 46–47), repository ownership table (line 60–61), stage table in CLAUDE.md

#### Dependencies and Sequencing

- **Must complete before Stage 4.9**: Stage 4.9 produces ENG-001 entity files using current SA Phase C entities authored by SA. These would be wrong under the new model.
- **Must complete before Stage 5**: Python agent construction (`src/agents/`) hard-codes phase trigger routing based on AGENT.md frontmatter. Getting the phase assignments wrong here means the orchestration graph routes phases to the wrong agents.
- **Design decisions (§Open Design Decisions) must be resolved in a focused review session before any file changes begin.** The repository ownership decision (Option A–D) in particular has cascading effects on `repository-conventions.md`, all agent write-path constraints, and the Python `RegistryReadOnlyError` path enforcement.

#### Design Decisions Resolved (2026-04-04)

1. **Repository ownership:** Option D adopted — `architecture-repository/` co-owned; SA has write authority over `model-entities/motivation/`, `strategy/`, `business/`, `implementation/`; SwA has write authority over `model-entities/application/`. Technology-repository stays unchanged as SwA-owned for technology-layer entities and implementation artifacts.
2. **Phase H split:** SA produces business/motivation/strategy layer Change Record; SwA produces parallel application/technology layer Change Record. Both coordinated via PM.
3. **SwA display-name:** unchanged ("Software Architect / Principal Engineer").
4. **CSCO Phase C gate:** coordinates with SwA (not SA) for AA and DA review.
5. **Stage 4.9 entity assignments (ACT-003/004):** SA scope = "phases A/B/H + EP-G Prelim/A and BA reconstruction"; SwA scope = "phases C/D/E/F/G + EP-G TA and application-layer reconstruction" — update when Stage 4.9 authoring resumes.

#### Checklist

- [x] Resolve Open Design Decisions (2026-04-04)
- [x] Update `framework/raci-matrix.md` — Phase B/C/D ownership
- [ ] Update `framework/agile-adm-cadence.md` — Phase C primary agent (minor; deferred)
- [x] Update artifact schemas (AA, DA owner field → SwA; BA consumed-by note added via RACI)
- [x] Rewrite `agents/solution-architect/AGENT.md` v1.0.0 → v1.1.0
- [x] Convert `agents/solution-architect/skills/phase-c-application.md` → SA-PHASE-C-APP-REVIEW (consulting traceability)
- [x] Convert `agents/solution-architect/skills/phase-c-data.md` → SA-PHASE-C-DATA-REVIEW (consulting traceability)
- [x] Update SA `skills/phase-h.md` v1.0.0 → v1.1.0 — scoped to business/motivation/strategy layer only; always routes Phase H handoff to SwA for parallel application/technology CR track
- [x] Rewrite `agents/software-architect/AGENT.md` v1.0.0 → v1.1.0
- [x] Author NEW `agents/software-architect/skills/phase-c-application.md` (SwA-PHASE-C-APP)
- [x] Author NEW `agents/software-architect/skills/phase-c-data.md` (SwA-PHASE-C-DATA)
- [x] Update SwA `skills/phase-d.md` — inputs section (AA/DA self-produced; no SA handoff)
- [x] Update SwA `skills/phase-h.md` v1.0.0 → v1.1.0 — SwA is now co-primary; produces own application/technology-layer CR; adds Step 3c (CR production), Step 4a (AA/DA entity updates)
- [x] Update `agents/csco/skills/gate-phase-c.md` — coordination partner SA → SwA
- [x] Update `framework/agent-index.md` v1.1.0 → v1.2.0 — SA/SwA routing tables; Phase C primary=SwA; Phase H co-primary; Phase-to-Agent Activation Map
- [x] Update `framework/repository-conventions.md §2.2` — Phase C entity paths and co-ownership (write-authority by layer annotation added)
- [ ] Update `framework/artifact-registry-design.md` — owner annotations on application-layer entity types (deferred)
- [ ] Update `framework/discovery-protocol.md` — SA/SwA Layer 1 scan priority order (deferred)
- [x] Update `CLAUDE.md` — agent phase table; architecture-repository ownership note
- [x] Update `specs/IMPLEMENTATION_PLAN.md` — agent roles table, repository ownership table
- [ ] Commit as `stage-4-sa-swa-role-refactor`

**All deferred items now complete (2026-04-04):**
- [x] Phase H skill split (SA phase-h.md v1.1.0, SwA phase-h.md v1.1.0)
- [x] `framework/agile-adm-cadence.md` — Phase C primary agent updated SA→SwA; §4.1 primary owners updated
- [x] `framework/agent-index.md` v1.2.0 — SA/SwA routing tables, Phase C/H activation maps
- [x] `framework/repository-conventions.md §2.2` — write-authority by layer annotations
- [x] `framework/artifact-registry-design.md §4.4` — application-layer entity owner updated SA→SwA; DOB-001 and APP-001---BSV-001 exemplar `owner-agent` fields corrected
- [x] `framework/discovery-protocol.md` — role-specific scan priority note in Step 1.2; diagram write-authority note updated for SwA Phase C diagrams
- framework/artifact-registry-design.md owner annotations
- framework/discovery-protocol.md scan priority

---

### Stage 4.9 — ENG-001 Architecture Model (Complete — 4.9i delivered)

> **Primary purpose: the implementation specification for Stage 5.** The SDLC multi-agent system is modelled as a first-class ERP v2.0 architecture engagement. Entity files, connection files, and diagrams produced here are the definitive architectural plans for all Stage 5 `src/` work. Developers implement one APP entity at a time; Pydantic models in `src/models/` are derived from DOB attribute tables; the LangGraph topology follows the activity diagram. When Stage 5 diverges from these artifacts, the artifacts are updated first. Secondary purpose: integration test fixture for Stage 6.
>
> **Model evolution is expected and normal.** The entities, connections, and diagrams in Stage 4.9 are *living* specifications — not a frozen snapshot. Every Stage 5 implementation decision that contradicts, extends, or refines the model (e.g. a new interface discovered, a data object field renamed, a component split into two) must be reflected by updating the relevant entity/connection files *before* changing the code. Requirements and constraints (REQ, CST, PRI) are likewise updated when implementation reveals that a stated requirement or constraint needs revision. Diagrams are regenerated from the updated model after each such update. Connection files are added or removed as actual component relationships are established. This is the model-first discipline applied to forward implementation: the architecture repository always leads the code, not the reverse.

#### 4.9a — ERP Directory Bootstrap

- [x] Create under `engagements/ENG-001/work-repositories/architecture-repository/`: `model-entities/motivation/{stakeholders,drivers,goals,requirements,constraints,principles}/`, `model-entities/strategy/{capabilities,value-streams}/`, `model-entities/business/{actors,processes,services}/`, `model-entities/application/{components,interfaces,services,data-objects}/`, `model-entities/implementation/`, `connections/archimate/{realization,serving,assignment,composition,access}/`, `connections/er/one-to-many/`, `connections/sequence/synchronous/`, `connections/activity/sequence-flow/`, `diagram-catalog/{diagrams,rendered,templates}/`, `decisions/`, `overview/`
- [x] Create `diagram-catalog/_archimate-stereotypes.puml` stub with official ArchiMate 3 layer colors (Motivation: `#EDD6F0`; Strategy: `#F5DEB3`; Business: `#FFFAC8`; Application: `#CCF2FF`; Technology: `#CCFFCC`; Physical: `#FFE0B2`; Implementation: `#FFE4C4`). No `diagrams/index.yaml` — ERP v2.0 uses frontmatter only; ModelRegistry and DiagramCatalog are built from file scans at startup.

#### 4.9b — Motivation and Strategy Entities (Phase A)

- [x] **Motivation** in `model-entities/motivation/`:
  - `STK-001.md` — `User / Engagement Owner` — directs the engagement; answers CQs; approves sprint output; primary consumer of all agent-produced artifacts
  - `STK-002.md` — `Architecture Board` — governs enterprise promotion; approves cross-engagement standards; only writers to `enterprise-repository/`
  - `DRV-001.md` — `SDLC Execution Cost` — manual execution of TOGAF ADM phases is expensive, error-prone, and rarely completed end-to-end
  - `DRV-002.md` — `Architecture Documentation Debt` — brownfield systems lack architecture models; decisions are undocumented; onboarding is slow
  - `GOL-001.md` — `Full ADM Phase Coverage` — every TOGAF phase (Prelim through H) executable by a specialist agent
  - `GOL-002.md` — `End-to-End Traceability` — every artifact traceable to a requirement, a producing agent, a skill, and a sprint
  - `GOL-003.md` — `Safety-by-Default` — CSCO gate woven into every phase transition; safety cannot be bypassed
  - `REQ-001.md` — `Multi-Agent Coordination` — agents hand off artifacts through structured events; no ad-hoc coupling
  - `REQ-002.md` — `Human-in-the-Loop` — user can inspect, question, and approve any agent output before it is promoted
  - `REQ-003.md` — `Brownfield Support` — system reconstructs architecture models from existing codebases (EP-G)
  - `REQ-004.md` — `Resumable State` — workflow survives process restarts; EventStore is the sole durable state
  - `REQ-005.md` — `Agent Learning` — agents record corrections; accuracy improves within and across engagements
  - `CST-001.md` — `No Framework Lock-In` — orchestration and LLM layers are swappable; domain logic has zero framework imports
  - `CST-002.md` — `Local-Only Runtime` — no required external services; only outbound call is the LLM API
  - `PRI-001.md` — `Domain-Centric Layering` — strict inward dependency rule: Infrastructure → Application → Domain → Common; never reversed
  - `PRI-002.md` — `EventStore Primacy` — `workflow.db` is the sole canonical state; no agent holds private mutable state between invocations
  - `PRI-003.md` — `Model-First` — entity files exist before any diagram; diagram aliases must resolve to ModelRegistry entries

- [x] **Strategy** in `model-entities/strategy/`:
  - `CAP-001.md` — `Phase Execution` — execute any TOGAF ADM phase via a specialist agent invoked by PM
  - `CAP-002.md` — `Artifact Production` — produce schema-valid, versioned, ERP-compliant architecture artifacts
  - `CAP-003.md` — `Multi-Agent Orchestration` — coordinate specialist agents under PM supervision via LangGraph
  - `CAP-004.md` — `Knowledge Retention` — record, retrieve, and synthesise learnings across skills, sprints, and engagements
  - `CAP-005.md` — `User Interaction` — surface CQs, accept answers and file uploads, present sprint reviews via dashboard
  - `CAP-006.md` — `Reverse Architecture` — reconstruct ERP model from existing codebase, IaC, and user-provided documents
  - `VS-001.md` — `Forward SDLC` — EP-0 cold start → Phase A–G sequential execution → enterprise promotion
  - `VS-002.md` — `Brownfield Onboarding` — EP-G entry → codebase scan → model reconstruction → gap assessment → Phase G governance

#### 4.9c — Business Layer Entities (Phase B)

Agent roles, core SDLC processes, and business services — the "what the system does" view, independent of Python.

- [x] **Actors** in `model-entities/business/actors/` — `safety-relevant: false` on all; `phase-produced: B`:
  - `ACT-001.md` — `User` — human; initiates phases; answers CQs; uploads files; reviews and approves sprint output
  - `ACT-002.md` — `PM Agent` — VSM System 3; orchestrates all agents; sprint lifecycle; gate coordination; CQ batching; review trigger
  - `ACT-003.md` — `SA Agent` — VSM System 4; phases A/B/H + Phase C traceability review + EP-G Prelim/A and BA reconstruction; business-layer architecture authority
  - `ACT-004.md` — `SwA Agent` — phases C (primary AA/DA)/D/E/F/G/H (app/tech) + EP-G TA and application-layer reconstruction; application and technology architecture authority
  - `ACT-005.md` — `DevOps Agent` — phases D/E/F/G; IaC, pipelines, deployments
  - `ACT-006.md` — `DE Agent` — phase G; code delivery; git worktree per sprint
  - `ACT-007.md` — `QA Agent` — phases E/F (test planning) + G (execution); compliance assessment co-production
  - `ACT-008.md` — `PO Agent` — phases Prelim/A/B/H; requirements register; stakeholder communication
  - `ACT-009.md` — `SM Agent` — phase A; market analysis; SWOT; requirements-management feedback
  - `ACT-010.md` — `CSCO Agent` — all phases (gate reviews); safety constraints; STAMP/STPA; incident response
  - `ACT-011.md` — `Architecture Board` — enterprise promotion reviews; enterprise-repository write authority

- [x] **Processes** in `model-entities/business/processes/` — each `safety-relevant: false` except BPR-005:
  - `BPR-001.md` — `Sprint Planning` — PM assigns work-packages to agents; emits `sprint.started`
  - `BPR-002.md` — `Skill Execution` — agent invoked with skill; reads artifacts; calls tools; produces output; emits events
  - `BPR-003.md` — `CQ Lifecycle` — agent raises CQ → PM batches → dashboard surfaces → user answers → agent resumes
  - `BPR-004.md` — `Gate Evaluation` — PM collects votes; evaluates checklist; records `gate.evaluated` event
  - `BPR-005.md` — `Algedonic Escalation` — `alg.raised` bypasses topology; reaches escalation target immediately — `safety-relevant: true`
  - `BIA-001.md` — `Sprint Review Interaction` — PM+User collaborative review sequence; user decisions drive continue/pause/end; PM routes corrections
  - `BPR-007.md` — `Enterprise Promotion` — entity promoted from engagement to enterprise repo; ID reference sweep; Architecture Board review
  - `BPR-008.md` — `Reverse Architecture` — EP-G entry; multi-source scan; entity inference; user confirmation; ERP model population

- [x] **Services** in `model-entities/business/services/` — what each role offers to the system, consumed by other actors or processes:
  - `BSV-001.md` — `Business Architecture` (SA) — produces AV, BA, Change Records (business layer); owns architecture-repository motivation/strategy/business layers; traceability review of SwA's Phase C output
  - `BSV-002.md` — `Application & Technology Architecture` (SwA) — produces AA, DA (Phase C), TA, ADRs, Architecture Contract; primary author of architecture-repository/application layer; owns technology-repository
  - `BSV-003.md` — `Project Coordination` (PM) — sprint lifecycle management; gate evaluation; CQ routing; review coordination
  - `BSV-004.md` — `Safety Governance` (CSCO) — gate vote authority on all phases; SCO updates; incident response
  - `BSV-005.md` — `Requirements Management` (PO) — maintains RR; stakeholder communication; phase A/B consulting
  - `BSV-006.md` — `Code Delivery` (DE) — implements work packages; submits PRs; contributes test reports
  - `BSV-007.md` — `Quality Assurance` (QA) — test strategy; test execution; compliance assessment
  - `BSV-008.md` — `Platform Engineering` (DO) — IaC; CI/CD pipelines; environment provisioning; deployment records
  - `BSV-009.md` — `User Decisions` (User) — CQ answers; file uploads; sprint review decisions — consumed by BPR-003 and BIA-001, including pause/resume intent

#### 4.9d — Application Layer Entities (Phase C) — Primary Stage 5 Implementation Specification

Every APP-nnn maps to a distinct `src/` Python module. Every DOB-nnn maps to a Pydantic model (or TypedDict for LangGraph state). These are the binding specifications Stage 5 developers work from.

- [x] **Components** in `application/components/`:

  *State & Storage (src/events/, src/common/, src/sources/):*
  - `APP-001.md` — `EventStore` — `src/events/event_store.py`; ACID SQLite; two tables: `events` (append-only; never mutated) and `snapshots` (point-in-time `WorkflowState` serialisations); public API: `record_event(event) → None`, `replay() → WorkflowState` (full replay from event 0; used for integrity check and disaster recovery), `replay_from_latest_snapshot() → tuple[WorkflowState, int]` (fast path: deserialises latest snapshot + replays delta events since snapshot; returns `(state, resume_sequence)`), `create_snapshot(trigger: str) → str` (serialises current `WorkflowState` to JSON; inserts into `snapshots` table; returns `snapshot_id`), `check_snapshot_interval() → bool` (returns True if events since last snapshot ≥ `snapshot_interval`, default 100), `check_integrity()`, `query_events(**filter)`; canonical workflow state; never accessed directly via sqlite3
  - `APP-002.md` — `ModelRegistry` — `src/common/model_registry.py`; two-tier artifact index: (1) **in-memory frontmatter cache** (`dict[str, ArtifactRecord]`) for structured metadata filtering — `list_artifacts(**filter)`, `list_connections(**filter)`, `get_by_id(id)`, `upsert(record)`; (2) **SQLite FTS5 full-text index** over artifact `§content` blocks for keyword and semantic search — `search(query: str, **filter) → list[tuple[ArtifactRecord, str]]` (returns ranked records + matched snippet; filters applied as post-FTS metadata constraints); optional **sqlite-vec semantic tier** enabled when corpus ≥ 50 artifacts and `sqlite-vec` available (same pattern as LearningStore — embeddings stored in `model_registry.db` alongside FTS5 table, cosine similarity replaces BM25 ranking); both tiers updated synchronously on every `write_artifact` call; thread-safe (RLock); FTS5 index persisted to `engagements/<id>/model_registry.db` (git-tracked); rebuilt from files on cold start or integrity mismatch
  - `APP-003.md` — `LearningStore` — `src/agents/learning_store.py`; LangGraph `BaseStore` wrapper; `(engagement_id, agent_role, "learnings")` namespace; `query(phase, artifact_type, domain, expand_related) → list[str]`; `record(entry: LearningEntry) → str`; optional sqlite-vec semantic tier; cold-start rebuild from `learnings/index.yaml`

  *Agent Runtime (src/agents/ infrastructure):*
  - `APP-004.md` — `SkillLoader` — `src/agents/skill_loader.py`; parses skill `.md` frontmatter + body; extracts Inputs/Steps/Algedonic/FeedbackLoop/Outputs sections; enforces token budget by `complexity-class` (600/1200/2000); truncation priority order; `load_instructions(skill_id) → str`
  - `APP-005.md` — `AgentFactory` — `src/agents/base.py`; `build_agent(agent_id) → Agent[AgentDeps, str | PMDecision]`; Layer 1 = `system-prompt-identity` (≤150 tok); Layer 2 = `### Runtime Behavioral Stance` (≤350 tok); Layer 3 = `SkillLoader.load_instructions()` via `@agent.instructions`; Layer 4 = tool results at runtime; registers tool sets per agent role
  - `APP-006.md` — `AgentRegistry` — `src/agents/__init__.py`; `AGENT_REGISTRY: dict[str, Agent]` of pre-built instances for all 9 roles; populated at module import; used by LangGraph nodes to invoke agents without re-constructing

  *Agent Instances (src/agents/*.py — one module each):*
  - `APP-007.md` — `PM Agent` — `src/agents/project_manager.py`; `result_type=PMDecision`; `pm_tools` (invoke_specialist, batch_cqs, evaluate_gate, record_decision); all PM skills loadable
  - `APP-008.md` — `SA Agent` — `src/agents/solution_architect.py`; `universal_tools` + `write_tools` (architecture-repository bound to motivation/strategy/business/implementation layers) + `target_repo_tools` (read-only); all SA skills including SA-REV-PRELIM-A, SA-REV-BA, SA-PHASE-C-APP-REVIEW, SA-PHASE-C-DATA-REVIEW
  - `APP-009.md` — `SwA Agent` — `src/agents/software_architect.py`; `universal_tools` + `write_tools` (architecture-repository/model-entities/application/ for Phase C; technology-repository for Phase D+) + `target_repo_tools` (read-only); all SwA skills including SwA-PHASE-C-APP, SwA-PHASE-C-DATA, SWA-REV-TA
  - `APP-010.md` — `DO Agent` — `src/agents/devops_platform.py`; `universal_tools` + `write_tools` (devops-repository bound) + `target_repo_tools` (read-write for DO) + `execute_pipeline()`
  - `APP-011.md` — `DE Agent` — `src/agents/implementing_developer.py`; `universal_tools` + `write_tools` (delivery-repository metadata bound) + `target_repo_tools` (read-write for DE; git worktree per sprint)
  - `APP-012.md` — `QA Agent` — `src/agents/qa_engineer.py`; `universal_tools` + `write_tools` (qa-repository bound) + `target_repo_tools` (read-only)
  - `APP-013.md` — `PO Agent` — `src/agents/product_owner.py`; `universal_tools` + `write_tools` (project-repository RR bound)
  - `APP-014.md` — `SM Agent` — `src/agents/sales_marketing.py`; `universal_tools` + read-only external source access
  - `APP-015.md` — `CSCO Agent` — `src/agents/csco.py`; `universal_tools` + `write_tools` (safety-repository bound); gate vote authority on all phases

  *Orchestration (src/orchestration/):*
  - `APP-016.md` — `LangGraph Orchestrator` — `src/orchestration/graph.py`; `build_sdlc_graph() → CompiledGraph`; nodes: pm_node, sa_node … csco_node, gate_check_node, cq_user_node, algedonic_handler_node, sprint_close_node, review_processing_node, engagement_complete_node; `SDLCGraphState` as shared state; **each node receives `event_store: EventStorePort` directly** (not only via AgentDeps) so it can emit lifecycle events without delegating to an agent; lifecycle events emitted by specific nodes: `sprint_close_node` → `sprint.close` + `create_snapshot("sprint.close")`; `gate_check_node` → `phase.transitioned` (on pass); `cq_user_node` → `phase.suspended`/`phase.resumed`; `algedonic_handler_node` → `algedonic.escalated`; `review_processing_node` → `review.sprint-closed`; `engagement_complete_node` → `engagement.completed` + `create_snapshot("engagement.completed")`
  - `APP-017.md` — `EngagementSession` — `src/orchestration/session.py`; top-level entry point; loads `engagements-config.yaml`; bootstraps EventStore; calls `replay_from_latest_snapshot()` (falls back to full `replay()`) to reconstruct `SDLCGraphState`; invokes `graph.stream()`; manages the outer user interaction loop; emits `engagement.started` + `create_snapshot("engagement.started")` after bootstrap, before graph execution; emits `sprint.started` at the start of each sprint iteration (detected when PM returns `next_action == "invoke_specialist"` for the first skill in a new sprint)
  - `APP-018.md` — `UserInteractionOrchestrator` — `src/orchestration/user_interaction.py`; runs as async monitor alongside the graph; watches for `cq.answered` and `review.submitted` EventStore events (emitted by Dashboard); routes CQ answers to the raising agent node; emits `cq.routed` event; signals PM review-processing node on review submission
  - `APP-019.md` — `PromotionOrchestrator` — `src/orchestration/promotion.py`; implements `repository-conventions.md §12` enterprise promotion procedure; `promote_entity(entity_id, engagement_id)`: reads entity file, assigns enterprise ID from `id-counters.yaml`, performs reference sweep across all connection/diagram files, moves entity file to enterprise path, emits `artifact.promoted` event

  *Dashboard & User Interaction (src/dashboard/):*
  - `APP-020.md` — `DashboardServer` — `src/dashboard/server.py`; FastAPI; all read-only view routes + POST interaction routes; SSE endpoint `/events/stream`; starts `watchdog` observer; mounts static files; single process; 127.0.0.1 only
  - `APP-021.md` — `UserInputGateway` — `src/dashboard/interaction.py`; handles POST /queries/<cq_id>/answer, POST /uploads, POST /review/submit; validates inputs; calls `EventStore.record_event()` for all writes; enforces MIME allow-list; path-restricted; never touches work-repositories directly
  - `APP-022.md` — `TargetRepoManager` — `src/sources/target_repo.py`; reads `engagements-config.yaml`; `clone_or_update(repo_id)`; `get_clone_path(repo_id) → Path`; `check_access(repo_id, agent_role)`; `create_worktree(repo_id, branch) → Path`; `get_primary_id()`; backward-compatible with singular `target-repository`

- [x] **Interfaces** in `application/interfaces/` — ports in the ports-and-adapters model; each is a `typing.Protocol` defined in `src/agents/protocols.py` or `src/sources/base.py`:
  - `AIF-001.md` — `EventStorePort` — `record_event(event: WorkflowEvent) → None`; `replay() → WorkflowState`; `replay_from_latest_snapshot() → tuple[WorkflowState, int]`; `create_snapshot(trigger: str) → str`; `check_snapshot_interval() → bool`; `query_events(**filter) → list[WorkflowEvent]`; implemented by APP-001; injected into all agents via AgentDeps
  - `AIF-002.md` — `LLMClientPort` — `complete(messages, tools, result_type) → Result`; implemented by PydanticAI `Agent` backed by Anthropic API; swappable for test doubles without LLM calls; defined in `src/agents/protocols.py`; this port is what CST-001 (No Framework Lock-In) depends on
  - `AIF-003.md` — `SourceAdapterPort` — `query(query: str) → str`; `source_id: str`; implemented by Confluence, Jira, Git, UserUpload adapters in `src/sources/`; registered in source adapter registry at session startup
  - `AIF-004.md` — `ArtifactReadWriterPort` — `read(id_or_path, mode) → str`; `write(path, content, *, upload_refs: list[str] | None = None) → ArtifactRecord`; `list(**filter) → list[ArtifactRecord]`; `search(query: str, **filter) → list[tuple[ArtifactRecord, str]]` (delegates to ModelRegistry FTS5/semantic tier; returns ranked records + snippet); path-constrained per agent role; validates ERP frontmatter + §content/§display structure; updates ModelRegistry synchronously on write; **tool-transparent event emission** (no skill instruction required): (1) emits `artifact.created` or `artifact.updated` — auto-detects new vs existing file; (2) auto-extracts `source_evidence` by scanning written content for `[inferred: <source>]` annotation pattern — no agent parameter needed; (3) emits `entity.confirmed` when `active_skill_id` in AgentDeps matches a reverse-arch skill ID (SA-REV-*, SWA-REV-*) — `confirmation_method` derived from whether a user CQ round occurred (EventStore `cq.answered` event exists for this skill invocation); (4) emits `file.referenced` events for each entry in `upload_refs` when provided. All four emissions happen inside the port implementation; agents call `write(path, content)` exactly as before — no new parameters required for the common case.
  - `AIF-005.md` — `DiagramToolsPort` — `regenerate_macros(repo_path)`; `generate_er_content(entity_ids) → str`; `generate_er_relations(connection_ids) → str`; `validate_diagram(puml_path) → list[str]`; `render_diagram(puml_path) → Path`; invokes local `plantuml` CLI
  - `AIF-006.md` — `LearningStorePort` — `query(phase, artifact_type, domain, expand_related) → list[str]`; `record(entry: LearningEntry) → str`; implemented by APP-003 (`LearningStore`); swappable for in-memory fake in tests

- [x] **Data objects** in `application/data-objects/` — authoritative field-level specification for all Pydantic models and TypedDicts in `src/models/` and `src/orchestration/`:

  *Persisted domain objects (EventStore-recorded or file-stored):*
  - `DOB-001.md` — `WorkflowEvent` — `src/events/models.py`; base model; fields: `event_id: str`, `event_type: str`, `agent: str | None`, `phase: str | None`, `sprint_id: str | None`, `skill_id: str | None`, `payload: dict`, `sequence: int`, `timestamp: datetime`; all EventStore-specific models inherit from this
  - `DOB-002.md` — `Engagement` — `src/models/engagement.py`; root domain entity; fields: `engagement_id: str`, `entry_point: str`, `target_repositories: list[TargetRepo]`, `primary_repo_id: str | None`, `sprint_review: SprintReviewConfig`, `uploads: UploadConfig`; loaded from `engagements-config.yaml` at session start; passed into `AgentDeps`
  - `DOB-003.md` — `LearningEntry` — `src/models/learning.py`; fields: `learning_id: str`, `agent: str`, `phase: str`, `artifact_type: str`, `trigger_event: str`, `error_type: str`, `importance: Literal["S1","S2","S3"]`, `applicability: str`, `correction_text: str`, `context_text: str | None`, `related: list[str]`, `synthesis_superseded: str | None`, `promoted: bool`, `generated_at_sprint: str`, `generated_at_engagement: str`
  - `DOB-004.md` — `ClarificationRequest` — `src/models/cq.py`; fields: `cq_id: str`, `raising_agent: str`, `skill_id: str`, `phase: str`, `question_text: str`, `blocking: bool`, `blocks_task: str | None`, `status: Literal["open","answered","withdrawn"]`, `answer_text: str | None`, `upload_refs: list[str]`, `raised_at: datetime`, `answered_at: datetime | None`
  - `DOB-005.md` — `AlgedonicSignal` — `src/models/algedonic.py`; fields: `alg_id: str`, `trigger_id: str`, `category: str`, `severity: Literal["S1","S2","S3"]`, `escalation_target: str`, `raised_by: str`, `raised_at: datetime`, `status: Literal["active","resolved","superseded"]`, `resolution_notes: str | None`
  - `DOB-006.md` — `HandoffRecord` — `src/models/handoff.py`; fields: `handoff_id: str`, `from_agent: str`, `to_agent: str`, `artifact_id: str`, `artifact_type: str`, `version: str`, `handoff_type: str`, `payload: dict`, `acknowledged: bool`, `acknowledged_at: datetime | None`; stored in `handoff-log/` and as EventStore `handoff.created` event
  - `DOB-007.md` — `GateOutcome` — `src/models/gate.py`; fields: `gate_id: str`, `phase_from: str`, `phase_to: str`, `votes: list[GateVote]`, `result: Literal["passed","failed","deferred"]`, `evaluated_at: datetime`, `rationale: str`; `GateVote` sub-model: `agent: str`, `result: Literal["approved","veto","abstain"]`, `rationale: str | None`
  - `DOB-008.md` — `ReviewItem` — `src/models/review.py`; fields: `item_id: str`, `artifact_id: str`, `artifact_type: str`, `decision: Literal["approved","needs-revision","rejected"]`, `agent_tag: str | None`, `comment: str | None`; list of these is the payload of `review.submitted` event

  *Runtime state objects (not persisted independently):*
  - `DOB-009.md` — `WorkflowState` — `src/events/replay.py`; rebuilt by `EventStore.replay()` (full) or `EventStore.replay_from_latest_snapshot()` (fast path); **snapshot payload** — this is exactly what is serialised to `snapshots.state_json`; must be fully JSON-serialisable (no `Path` objects; use `str`); fields: `current_phase: str`, `current_sprint: str | None`, `phase_visit_counts: dict[str, int]`, `open_cqs: list[ClarificationRequest]`, `pending_handoffs: list[HandoffRecord]`, `baselined_artifacts: dict[str, str]` (id → version), `gate_outcomes: dict[str, GateOutcome]`, `last_algedonic: AlgedonicSignal | None`, `registered_uploads: list[str]`, `upload_reference_map: dict[str, list[str]]`, `snapshot_sequence: int | None` (sequence of the event that triggered the latest snapshot loaded; None if state was built by full replay)
  - `DOB-010.md` — `AgentDeps` — `src/agents/deps.py`; dataclass; fields: `engagement: Engagement`, `event_store: EventStorePort`, `active_skill_id: str`, `workflow_state: WorkflowState`, `engagement_base_path: Path`, `framework_path: Path`; injected by LangGraph node into each agent invocation
  - `DOB-011.md` — `PMDecision` — `src/orchestration/pm_decision.py`; Pydantic model; `result_type` for PM Agent; fields: `next_action: Literal["invoke_specialist","evaluate_gate","surface_cqs","trigger_review","close_sprint","complete_engagement"]`, `specialist_id: str | None`, `skill_id: str | None`, `task_description: str`, `reasoning: str`, `gate_id: str | None`
  - `DOB-012.md` — `SDLCGraphState` — `src/orchestration/graph_state.py`; LangGraph `TypedDict` (not Pydantic); fields: `engagement_id: str`, `current_agent: str | None`, `current_skill: str | None`, `pm_decision: PMDecision | None`, `last_specialist_output: str | None`, `target_repository_ids: list[str]`, `primary_repository_id: str | None`, `review_pending: bool`, `algedonic_active: bool`
  - `DOB-013.md` — `ArtifactRecord` — `src/common/model_registry.py`; ModelRegistry's in-process representation of a scanned entity file; fields: `artifact_id: str`, `artifact_type: str`, `path: Path`, `version: str`, `status: str`, `owner_agent: str`, `safety_relevant: bool`, `produced_by_skill: str | None`, `domain: str | None`, `engagement: str`, `name: str`; never persisted; rebuilt at startup

- [x] **Application services** in `application/services/` — named service groupings that span multiple components; useful for the business diagram and for tracing capability-to-implementation:
  - `ASV-001.md` — `Agent Invocation Service` — APP-005 + APP-004 + APP-006; accepts `(agent_id, skill_id, deps)` → 4-layer prompt assembly → PydanticAI execution → structured result; governed by `framework/agent-runtime-spec.md`
  - `ASV-002.md` — `Artifact I/O Service` — APP-002 + AIF-004; read/write/list on ERP entity files; path constraints enforced; ModelRegistry kept in sync; ERP format validated on every write
  - `ASV-003.md` — `Sprint Review Service` — APP-018 + APP-021 + APP-016 review_processing_node; full lifecycle: `review.pending` → dashboard surfaces artifacts → user marks items → correction handoffs to agents → agents revise → **loop: user re-reviews until all approved** → `review.sprint-closed` → `sprint.close`. User has final say; rework cycles are unbounded.
  - `ASV-004.md` — `CQ Management Service` — APP-007 (PM batching) + APP-018 (event monitoring) + APP-020 (dashboard surfacing) + APP-021 (answer submission); full CQ lifecycle from `cq.raised` → user answer → agent resumption
  - `ASV-005.md` — `Learning Service` — APP-003 + AIF-006; implements `learning-protocol.md §9` full query logic (metadata filter → graph expansion via `related` → optional semantic tier) and `record()` with schema validation, ID assignment, durable file write, and EventStore event

#### 4.9e — Connection Files

Enumerate specific connection files. Each is an `.md` file with frontmatter and brief `§content`. `§display ###archimate` block where applicable.

- [x] **`connections/archimate/realization/`** ✅ 15 files. Note: filenames corrected to source=realizing element per artifact-registry-design.md §3.3 (plan had reversed convention with realized element first):
  - `APP-016---CAP-001.md` (was CAP-001---APP-016 in plan) — LangGraph Orchestrator realises Phase Execution
  - `ASV-002---CAP-002.md`, `ASV-001---CAP-003.md`, `ASV-005---CAP-004.md` — services realise capabilities
  - `ASV-004---CAP-005.md`, `ASV-003---CAP-005.md` — CQ and Sprint Review services realise User Interaction
  - `APP-008---CAP-006.md`, `APP-009---CAP-006.md` — SA/SwA agents realise Reverse Architecture
  - `ASV-001---BPR-002.md`, `ASV-004---BPR-003.md`, `ASV-003---BIA-001.md` — services realise core execution/review behaviors
  - `APP-008---BSV-001.md`, `APP-009---BSV-002.md`, `APP-007---BSV-003.md`, `APP-020---BSV-009.md` — agents realise BSV services

- [x] **`connections/archimate/serving/`** ✅ 24 files. Corrections: `APP-006---APP-016.md` (plan erroneously listed APP-005---APP-006); 6 additional SkillLoader→agent connections for DO/DE/QA/PO/SM/CSCO (plan said "four more" but 6 agents remain):
  - APP-001→{APP-016, APP-017, APP-018, APP-021}; APP-002→{APP-004, APP-005}; APP-003→{APP-007..009}
  - APP-004→{APP-007..015} (all 9 agents); APP-006→APP-016; APP-016→APP-017; APP-020→ACT-001
  - APP-022→{APP-008, APP-009, APP-011}

- [x] **`connections/archimate/assignment/`** ✅ 17 files: original 8 (ACT-001/002/003/004 + BCO-001 → BPR-001/002/003/004/006/007) + 9 new: ACT-005..010 → BPR-002; ACT-010 → BPR-004/005; ACT-002 → BPR-005. ACT-011 renamed BCO-001 throughout.

- [x] **`connections/archimate/composition/`** ✅ 13 files: APP-016→{APP-007..009, APP-018}; APP-006→{APP-007..015} (all 9 agents)

- [x] **`connections/archimate/access/`** ✅ 8 files: APP-001→{DOB-001, DOB-009}; APP-003→DOB-003; APP-016→DOB-012; APP-017→DOB-002; APP-007→DOB-011; APP-021→{DOB-004, DOB-008}

- [x] **`connections/er/one-to-many/`** ✅ 7 files. Corrections: DOB-009---DOB-004 and DOB-009---DOB-006 (plan had reversed direction):
  - `DOB-002---DOB-001.md`, `DOB-009---DOB-001.md`, `DOB-004---DOB-001.md`, `DOB-007---DOB-007.md`
  - `DOB-009---DOB-007.md`, `DOB-009---DOB-004.md`, `DOB-009---DOB-006.md`

#### 4.9f — Diagrams (Phase C outputs — binding implementation views)

Seven diagrams. Each has a stated **implementation purpose** — what Stage 5 decision or module it specifies. Diagrams are prescribed at the level of content and grouping; the SA authors the actual PUML.

- [x] **`business-archimate-combined-v1.puml`** ✅ v0.3.0 — fully connected. Owner: SA. 35 entity IDs, 39 connection IDs (17 assignment + 14 BPR→BSV realization + 7 BPR→CAP realization + 1 BCO-001→BPR-007). Six groups with `<<Grouping>>` stereotypes.
  *Purpose:* Defines agent role taxonomy and SDLC process model used in all Stage 5 agent module naming and EventStore event routing.
  *Semantic corrections applied:* ACT-002..ACT-010 → `BusinessRole`; ACT-011 → `BusinessCollaboration` renamed BCO-001 (correct prefix per §4 of artifact-registry-design.md); ACT-001 stays `BusinessActor`. BCO-001 alias corrected to `BCO_001` in `_macros.puml`.
  *Connection additions:* All 6 unconnected specialist roles (ACT-005..010) now assigned to BPR-002; ACT-010 additionally assigned to BPR-004 (gate authority) and BPR-005 (algedonic authority); ACT-002 assigned to BPR-005 (algedonic handler); all 5 orphan BSVs (BSV-004..008) now realized by BPR-002; BPR-008 also realizes BSV-001; all 6 CAPs now realized by appropriate BPRs (cross-layer, rendered in steel blue). No entity remains unconnected.
  *User is head/final authority of Architecture Board* (BCO-001 entity content updated).

- [x] **`application-archimate-component-map-v1.puml`** ✅ v0.2.0 — layer-boundary and grouping corrections. Owner: SwA. 27+5 entity IDs (27 application-layer + 4 BSV + 1 ACT cross-layer boundary), 32 connection IDs. `skinparam rankdir LR`.
  *Purpose:* Primary implementation map for Stage 5b — every box is a Python module; every serving connection is a function call boundary.
  *Corrections applied:* `<<Grouping>>` added to all 5 outer containers; cross-layer boundary elements (BSV_001/002/003/009, ACT_001) declared outside groups; 4 APP→BSV cross-layer realization arrows added; APP_020→ACT_001 serving connection added.
  *Grouping — five `<<Grouping>>` rectangles:*
  - **State & Storage** (APP-001 EventStore, APP-002 ModelRegistry, APP-003 LearningStore) — `src/events/ + src/common/`
  - **Agent Runtime** (APP-004 SkillLoader, APP-005 AgentFactory, APP-006 AgentRegistry; AIF-002/004/005/006) — `src/agents/` infrastructure
  - **Agent Roster** (APP-007 PM through APP-015 CSCO — 9 agents) — `src/agents/*.py`
  - **Orchestration** (APP-016 LangGraph, APP-017 Session, APP-018 UIO, APP-019 Promotion; AIF-001) — `src/orchestration/`
  - **Dashboard & Interaction** (APP-020 DashboardServer, APP-021 UserInputGateway; AIF-003, APP-022 TargetRepoManager) — `src/dashboard/ + src/sources/`

- [x] **`application-class-er-domain-model-v1.puml`** ✅ present and semantically aligned to persisted DOB scope.
  *Purpose:* Pydantic model specification for `src/models/` — field names in this diagram are the authoritative attribute names used in Stage 5 code.
  *Scope:* The eight persisted domain objects that flow through EventStore and define workflow state: DOB-001 (WorkflowEvent), DOB-002 (Engagement), DOB-003 (LearningEntry), DOB-004 (ClarificationRequest), DOB-005 (AlgedonicSignal), DOB-006 (HandoffRecord), DOB-007 (GateOutcome), DOB-008 (ReviewItem). Runtime-only objects (DOB-009 WorkflowState, DOB-010 AgentDeps, DOB-011 PMDecision, DOB-012 SDLCGraphState, DOB-013 ArtifactRecord) are in the model but excluded from this diagram — they have no ER relationships to show.
  *Contents:* Each DOB as a PlantUML class with attribute list (name: type). ER connections with cardinalities per `connections/er/` entries. `DOB-002 Engagement` at top-left as aggregate root; `DOB-001 WorkflowEvent` as the central hub entity.

- [x] **`lifecycle-activity-sprint-v1.puml`** ✅ present and aligned to sprint lifecycle + review loop.
  *Purpose:* LangGraph graph topology specification for Stage 5c — every decision diamond maps to a routing function; every action box maps to a node implementation.
  *Contents:* Full ADM sprint lifecycle as UML activity diagram. Start fork: entry point selection (EP-0 through EP-H). Main path: Sprint Planning (BPR-001) → Phase Execution (BPR-002, loop per agent per phase) → Gate Evaluation (BPR-004) → decision: gate passed? → next phase or return. Branches: (1) CQ suspension fork from any phase execution node → await `cq.answered` → resume; (2) Algedonic bypass from any node → ALG handler → resolution → resume or halt; (3) Sprint review branch after each sprint close: decision `sprint-review.enabled?` → if true: `review.pending` → await `review.submitted` → corrections loop → sprint close; if false: direct close. End: Engagement Complete.
  *Swim-lanes:* PM (planning/gating/review), Agent (execution), User (CQ answers/review), EventStore (state writes at each transition).

- [x] **`specialist-invocation-activity-workflow-v1.puml`** ✅ added (session 15).
  *Purpose:* Business-process activity/BPMN view of Phase G specialist invocation and sub-process execution boundaries.
  *Contents:* Swimlanes for PM, Specialist, and CSCO roles; progression through BPR-001 → BPR-201 → BPR-202 → BPR-203 → BPR-004 with CQ and algedonic branches.

- [x] **`cq-activity-lifecycle-v1.puml`** ✅ added (session 15).
  *Purpose:* Business-process activity/BPMN view of BPR-003 CQ lifecycle (route, await, integrate, resume).
  *Contents:* Swimlanes for Specialist, PM, and User; explicit BPR-301 → BPR-302 → BPR-303 flow with resume handoff back to specialist execution.

- [x] **`sprint-review-activity-workflow-v1.puml`** ✅ added (session 15).
  *Purpose:* Business-interaction activity/BPMN view of BIA-001 sprint review loop.
  *Contents:* Swimlanes for PM, User, Specialist; staged interaction BIA-101 → BIA-102 → BIA-103 and correction loop until approval closure.

- [ ] Each diagram `.puml` file carries frontmatter in its header comment block per `framework/diagram-conventions.md`; no `diagrams/index.yaml` — ERP v2.0 uses frontmatter only (DiagramCatalog built from file scans at startup).

#### 4.9g — Overview Documents and Decisions

- [x] `overview/architecture-vision.md` — AV for ENG-001: engagement context (modelling the SDLC system itself); capability clusters (CAP-001 through CAP-006); STK-001 and STK-002; safety classification: Safety-Neutral (no physical actuation, no regulated user data, no financial transactions)
- [x] `overview/aa-overview.md` — Application Architecture summary: lists all APP-nnn with `src/` path and one-line function; states the four-layer dependency rule (Common → Domain → Application → Infrastructure); lists all DOB-nnn Pydantic models with their `src/models/` path; lists all AIF-nnn ports with their `Protocol` location
- [x] `decisions/ADR-001.md` — `PydanticAI for agent definition` — context: evaluated LangChain, Autogen, raw API; decision: PydanticAI; rationale: structured output via `result_type`, native tool use, minimal magic, first-class Anthropic support; consequences: tighter Pydantic v2 dependency, simpler than alternatives
- [x] `decisions/ADR-002.md` — `LangGraph for orchestration graph` — context: PM-as-supervisor pattern requires stateful multi-step routing with conditional branches and interrupt support; decision: LangGraph; rationale: built-in state persistence, interrupt/resume for CQ handling, conditional edge routing, compatible with PydanticAI; consequences: LangGraph version pinning, graph must be rebuilt if topology changes
- [x] `decisions/ADR-003.md` — `SQLite EventStore as canonical state` — context: need durable, auditable, ACID workflow state; decision: SQLite via EventStore class; rationale: local-only (CST-002), git-trackable binary, zero-infrastructure, ACID guarantees, replay from scratch gives WorkflowState; consequences: single-process only (no concurrent writer), binary in git (acceptable at engagement scale)
- [x] `decisions/ADR-004.md` — `FastAPI + Jinja2 + SSE for dashboard` — context: user interaction surface needed; decision: FastAPI server-side rendering; rationale: no build step, no frontend framework, works with Python-only stack, SSE is standard HTTP (no WebSocket needed for change notifications), POST forms sufficient for CQ/review interaction; consequences: minimal JS budget (two blocks only)
- [x] `decisions/ADR-005.md` — `File-based ERP entity storage` — context: need to store architecture model; decision: one `.md` file per entity, organised by ArchiMate layer; rationale: git-native diff and blame, human-readable, no DB schema migration for model changes, ModelRegistry is ephemeral (rebuilt at startup); consequences: startup scan time proportional to entity count; mitigated by watchdog incremental updates

#### 4.9h — Event-Sourcing of Repository Mutations and User Inputs

**Every mutation to an engagement work-repository and every user-contributed input must produce an EventStore event.** This is the event-sourcing invariant: the engagement event-stream is the authoritative record of *what happened and when*, while the file system is the *current state projection* of that stream. Events reference file paths; files hold content. On replay, the system reconstructs full workflow state including which entities were inferred from which evidence, which files were uploaded by the user, and which entities the user confirmed.

**All events in this taxonomy are emitted by tool implementations, not by skill instructions — no agent or skill file changes are required.** `ArtifactReadWriterPort.write()`, `scan_target_repo()`, and `UserInputGateway` each emit their respective events autonomously using context from `AgentDeps` (`active_skill_id`, `event_store`). Skill files call the same tool signatures they always have.

The following events govern reverse-architecture and user-input persistence. They must be added to `src/events/models.py` in Stage 5a alongside the existing base event types:

| Event type | Emitted by (tool layer) | Key payload fields | Purpose |
|---|---|---|---|
**Artifact status lifecycle.** Every entity, connection, and diagram file has a `status` field whose valid values are `draft | baselined | deprecated`. Status semantics are enforced by the port layer:
- **`draft`**: under active construction in the current sprint. Cannot be referenced in connections by agents outside the producing sprint context. Cannot appear in any diagram file (draft or otherwise). Transitions to `baselined` at sprint close (gate-pass or PM explicit baseline call). Emits `artifact.created` on first write.
- **`baselined`**: approved and stable. May appear in diagrams and be cross-referenced freely by all agents. Subsequent content edits emit `artifact.updated`; status change to `deprecated` emits `artifact.deprecated`.
- **`deprecated`**: no longer current; excluded from new diagrams and new connections; all existing diagrams and connections referencing it must be updated or deprecated in turn. Remains in the model for audit and rollback. Physical deletion requires explicit `delete_artifact` call; emits `artifact.deleted`.

| Event type | Emitted by (tool layer) | Key payload fields | Purpose |
|---|---|---|---|
| `artifact.created` | `ArtifactReadWriterPort.write()` — new file (status=draft) | `path`, `artifact_id`, `version`, `produced_by_skill`, `source_evidence: list[str]` | Creation of any ERP entity/connection/diagram file. `source_evidence` **auto-extracted** from `[inferred: <source>]` annotations. |
| `artifact.updated` | `ArtifactReadWriterPort.write()` — existing file; no status transition | `path`, `artifact_id`, `version`, `previous_version`, `produced_by_skill`, `changed_fields: list[str]` | Content or version change within a stable status. `changed_fields` derived by diffing new frontmatter against previous file on disk. |
| `artifact.baselined` | `ArtifactReadWriterPort.write()` — `status` transitions `draft` → `baselined` | `path`, `artifact_id`, `version`, `sprint_id`, `produced_by_skill` | Sprint-close or explicit PM baseline call. Auto-emitted in place of `artifact.updated` when the port detects this transition. Updates `WorkflowState.baselined_artifacts[artifact_id] = version`. |
| `artifact.deprecated` | `ArtifactReadWriterPort.write()` — `status` transitions to `deprecated` | `path`, `artifact_id`, `previous_status`, `rationale: str`, `produced_by_skill` | First-class lifecycle event. `rationale` required — port raises `MissingDeprecationRationale` if absent. |
| `artifact.deleted` | `ArtifactReadWriterPort.delete()` — physical file removal | `path`, `artifact_id`, `previously_deprecated_at: str`, `rationale: str`, `produced_by_skill` | Emitted on physical removal. Port enforces `status == deprecated` precondition (`PrematureDeleteError` otherwise). |
| `source.scanned` | `scan_target_repo()` tool, end of scan | `scan_scope: list[str]`, `target_repo_id: str \| None`, `external_source_ids: list[str]`, `triggered_by_skill: str`, `file_count: int` | Audit record of EP-G discovery scan. Emitted by the tool; skill files call `scan_target_repo()` as before. |
| `entity.confirmed` | `ArtifactReadWriterPort.write()` when `active_skill_id` ∈ `{SA-REV-*, SWA-REV-*}` | `artifact_id`, `confirmation_method: "user" \| "auto"` | Post-confirmation entity write in a reverse-arch context. `confirmation_method` = `"user"` if a `cq.answered` event exists for this skill invocation; `"auto"` otherwise. Minimal payload — fully derivable from tool context. |
| `upload.registered` | `UserInputGateway` POST /uploads | `upload_id`, `file_path: str`, `mime_type: str`, `original_filename: str`, `referenced_by_cq: str \| None` | User file upload. File content at `engagements/<id>/user-uploads/<upload_id>/`; event is the reference. |
| `file.referenced` | `ArtifactReadWriterPort.write()` when `upload_refs` kwarg provided | `upload_id`, `artifact_id` | Links uploaded file to entity. Agent passes `upload_refs=[...]` explicitly when a CQ answer cited a file — the one optional kwarg on `write()`; omitted in all non-upload contexts. |

**`source_evidence` auto-extraction:** The port implementation scans the `§content` block of every written entity file for the `[inferred: <source>]` annotation pattern already mandated by the reverse-arch skill steps. No new skill instruction is needed — the annotation is already there per existing requirements; the tool harvests it.

**Model-update contract (Stage 5 forward):** Every Stage 5 implementation change that updates an entity or connection file emits `artifact.updated` with `changed_fields` derived by diff. Diagrams regenerated as a consequence emit `artifact.updated` with `changed_fields: ["§display"]`. Happens inside `write_artifact`; no new developer action required.

**Contingency — if future skill additions become necessary (Stage 4.8g):** The three reverse-arch skills are `complexity-class: complex` (2000-token soft budget). Any additions to Steps 3 or 4 (e.g. explicit `upload_refs` guidance) are estimated at ≤60 tokens per skill. Truncation priority (`Algedonic Triggers → Feedback Loop → Outputs`; Steps never truncated) provides ~400 tokens of headroom before content loss. All such changes are designed in Stage 4.8g before execution — see below.

#### 4.9i — Application and Infrastructure Architecture Elaboration (Complete)

Purpose: extend the Stage 5 implementation specification with deeper, execution-grade architectural detail for application and technology/infrastructure layers, using paired ArchiMate + sequence views.

- [x] **Application layer refinement package (ArchiMate):**
  - Refine component/service/interface boundaries for APP/AIF/ASV entities and their realization/serving/access relations.
  - Add explicit runtime interaction boundaries for PM orchestration, specialist invocation, CQ routing, and review processing.
  - Validate APP-to-BSV realization and APP-to-DOB access coverage against current entity/connection files.
  - 2026-04-08 remediation: explicit DashboardServer -> UserInputGateway serving boundary modeled (`APP-020---APP-021@@archimate-serving`) and propagated to component map/runtime-boundary views.
  - 2026-04-08 remediation: explicit EventStore -> DashboardServer read-side serving boundary modeled (`APP-001---APP-020@@archimate-serving`) for local developer-machine runtime query paths (open CQ/review scope + event stream reads).

- [x] **Application runtime behavior package (Sequence):**
  - Author or refine sequence diagrams for core flows: specialist invocation cycle, CQ answer routing/resume, gate evaluation decision path, sprint review correction loop.
  - Ensure each sequence flow has backing entities/connections and traceable relation to lifecycle/activity workflow nets.
  - 2026-04-08 remediation: CQ and sprint-review runtime sequences now explicitly show APP-020 -> APP-021 delegation path; runtime traceability matrix frontmatter corrected for APP-017 + connection completeness.
  - 2026-04-08 adequacy review: added `runtime-sequence-algedonic-escalation-fastpath-v1.puml` and updated gate-evaluation/runtime-boundary views to explicitly model safety fast-path escalation and CSCO decisioning control flow.
  - 2026-04-08 prioritization pass (best-practice aligned): added explicit idempotency/dedup semantics (canonical `event_id`), correlation continuity (`invocation_id`/`correlation_id`), and fail-safe timeout branches for safety-critical decision points in CQ/gate/algedonic runtime sequences.

- [x] **Technology/infrastructure layer refinement package (ArchiMate):**
  - Model deployment/runtime topology (nodes, system software, environments, data stores, external boundaries) for the actual Stage 5 execution model.
  - Specify EventStore deployment context, dashboard/runtime hosting boundary, and target-repo/tooling execution context.
  - Add technology-layer relations required for operational readiness (serving, deployment, communication-path, access where applicable).
  - 2026-04-08 baseline slice: added local runtime topology entities [@NOD-001 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/model-entities/technology/nodes/NOD-001.local-runtime-host.md), [@SSW-001 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/model-entities/technology/system-software/SSW-001.python-runtime-and-uv-toolchain.md), and [@TSV-001 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/model-entities/technology/services/TSV-001.local-file-and-process-service.md).
  - 2026-04-08 baseline slice: added infrastructure-to-application serving/composition connections [@NOD-001---SSW-001@@archimate-composition v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/connections/archimate/composition/NOD-001---SSW-001@@archimate-composition.md), [@SSW-001---TSV-001@@archimate-serving v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/connections/archimate/serving/SSW-001---TSV-001@@archimate-serving.md), [@TSV-001---APP-001@@archimate-serving v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/connections/archimate/serving/TSV-001---APP-001@@archimate-serving.md), [@TSV-001---APP-016@@archimate-serving v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/connections/archimate/serving/TSV-001---APP-016@@archimate-serving.md), and [@TSV-001---APP-020@@archimate-serving v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/connections/archimate/serving/TSV-001---APP-020@@archimate-serving.md).
  - 2026-04-08 baseline slice: added companion views [@technology-archimate-local-runtime-hosting-v1 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/technology-archimate-local-runtime-hosting-v1.puml) and [@technology-matrix-runtime-hosting-traceability-v1 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/technology-matrix-runtime-hosting-traceability-v1.md).

- [x] **Operational behavior package (Sequence):**
  - Author or refine sequence diagrams for deployment/provisioning, event persistence/snapshot/replay lifecycle, and operational observability/escalation paths.
  - Confirm sequence participants map to defined application/technology entities (no diagram-only participants).
  - 2026-04-08 completion slice: added [@technology-sequence-runtime-bootstrap-provisioning-v1 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/technology-sequence-runtime-bootstrap-provisioning-v1.puml) for local host/runtime bootstrap and provisioning flow.
  - 2026-04-08 refinement slice: replaced mixed sequence with decomposed operational scenarios [@technology-sequence-event-persistence-snapshot-policy-v1 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/technology-sequence-event-persistence-snapshot-policy-v1.puml), [@technology-sequence-replay-hydration-on-resume-v1 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/technology-sequence-replay-hydration-on-resume-v1.puml), and [@technology-sequence-observability-query-path-v1 v0.1.0](../engagements/ENG-001/work-repositories/architecture-repository/diagram-catalog/diagrams/technology-sequence-observability-query-path-v1.puml) to avoid false linear causality between independent triggers.

- [x] **Cross-layer conformance and verification:**
  - Run model-first conformance check: business workflow nets -> application services -> technology/infrastructure realization path.
  - Re-render modified diagrams to canonical `diagram-catalog/rendered/` and run `ModelVerifier.verify_all(...)` after each slice.
  - 2026-04-08 completion slice: conformance evidence consolidated across `runtime-matrix-business-to-application-traceability-v1.md` + `technology-matrix-runtime-hosting-traceability-v1.md` and paired application/technology sequences.
  - 2026-04-08 completion slice: rendered new technology operational sequences and re-ran full repository verification with zero errors/warnings.

---

### Stage 5 — Python Implementation Layer

> Implements the specs defined in `framework/agent-runtime-spec.md` and `framework/orchestration-topology.md`. **Read those documents before authoring any src/ file.** Architecture: LangGraph outer loop (ADM phase workflow) + PydanticAI inner loop (per-agent invocations) + EventStore (canonical state persistence).

#### 5a — EventStore completion

- [ ] **`src/events/replay.py`**: implement full state machine — process each event type → update `WorkflowState`; handle all 10+ event types (phase, cycle, gate, sprint, artifact, handoff, cq, algedonic, source)
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
- [ ] **`src/agents/deps.py`**: `AgentDeps` dataclass (engagement_id, event_store, active_skill_id, workflow_state, engagement_base_path, framework_path)
- [ ] **`src/agents/base.py`**: `build_agent(agent_id)` factory — layered system prompt assembly:
  - Layer 1: `AgentSpec.load(agent_id)` parses YAML frontmatter, extracts `system-prompt-identity` verbatim (hard cap ≤150 tokens; raises `AgentSpecError` if exceeded)
  - Layer 2: `AgentSpec.load_personality(agent_id)` extracts `### Runtime Behavioral Stance` subsection from §11 only (hard cap ≤350 tokens; full §11 is **not** loaded at runtime — the rest of §11 is authoring documentation, not a runtime injection target)
  - Layer 3: active skill via `@agent.instructions` calling `SkillLoader.load_instructions(ctx.deps.active_skill_id)`
- [ ] **`src/agents/skill_loader.py`**: `SkillLoader.load_instructions(skill_id)` — parses skill Markdown file, extracts included sections (Inputs Required, Steps, Algedonic Triggers, Feedback Loop, Outputs); excludes Knowledge Adequacy Check; reads `complexity-class` from frontmatter to select token threshold (simple ≤600, standard ≤1200, complex ≤2000); counts tokens via `tiktoken`; truncation priority if soft cap exceeded: Algedonic Triggers → compact ALG-IDs only; Feedback Loop → termination conditions + iteration count only; Outputs → artifact paths only; **Steps are never truncated**; raises `SkillBudgetExceededError` only above hard cap (complex=2000, standard=1440, simple=720 — 20% over soft cap; indicates a skill that needs splitting, not compressing)
- [ ] **`src/agents/tools/`**: tool implementations (all tools described in `framework/agent-runtime-spec.md §6`):
  - `universal_tools.py` — `read_artifact(id_or_path, mode)` (resolves artifact-id → path via ModelRegistry; modes: `summary`=frontmatter+first two §content sections, `full`=entire file); `list_artifacts(**filter)` (queries ModelRegistry in-memory frontmatter cache; returns metadata list without loading bodies; filters: artifact-type, status, domain, safety-relevant, phase-produced, engagement); `search_artifacts(query: str, **filter)` (**primary discovery tool for content-based lookup** — delegates to ModelRegistry FTS5 index; optional semantic tier when available; returns ranked `(ArtifactRecord, snippet)` pairs; agent then selects which to read in full; use when artifact type is uncertain or discovery is by concept rather than metadata); `list_connections(source, target, artifact_type)` (ModelRegistry query scoped to `connections/`; all params optional); `query_event_store`, `emit_event`, `raise_cq`, `raise_algedonic`, `list_framework_docs(**filter)`, `search_framework_docs(query, **filter)`, `read_framework_doc(doc_id_or_path, section=None, mode="summary")` (query-first framework retrieval per `framework/framework-knowledge-index.md`; `mode="full"` escalation only), `discover_standards` (reads `technology-repository/coding-standards/` and `enterprise-repository/standards/`; SA/SwA/DE/DO only), `list_target_repositories()` (reads `engagements-config.yaml`; returns all registered repos with id/label/role/domain/primary/clone-path; available to all agents), `query_learnings(phase, artifact_type, domain, expand_related=True)` (per `framework/learning-protocol.md §9` + §12.1–12.2), `record_learning(entry: LearningEntry)` (per §9 + §12.1)
  - `write_tools.py` — per-agent path-constrained write tools (RepositoryBoundaryError on violation → ALG-007)
  - `target_repo_tools.py` — **multi-repo aware**: `read_target_repo(path, repo_id=None)` (repo_id=None → primary repo; raises TargetRepoNotFoundError if id not registered); `write_target_repo(path, content, repo_id=None)` (DE and DO only, per their respective access grants); `execute_pipeline(repo_id=None)` (DO only); `scan_target_repo(repo_id=None)` (Discovery Layer 4 single-repo scan — called once per repo by Layer 4 procedure); `list_target_repos()` (alias for `list_target_repositories()` — convenience import in this module). **Backward compatibility:** when `target-repository` (singular) is configured, `repo_id=None` and `repo_id="default"` both refer to it.
  - `pm_tools.py` — PM decision events (all emitted inside the tool call, before returning to the agent): `invoke_specialist(agent_id, skill_id, task)` → emits `specialist.invoked`; `evaluate_gate(gate_id, votes)` → emits `gate.evaluated` + `create_snapshot("gate.evaluated")` on pass; `batch_cqs(cq_ids)` → emits `cq.batched`; `record_decision(rationale)` → emits `decision.recorded`; `trigger_review()` → emits `review.pending`
  - `diagram_tools.py` — Model-driven diagram production per `framework/diagram-conventions.md §5` (D1–D5 protocol): `regenerate_macros(repo_path)` (scans all entity `§display ###archimate` blocks via ModelRegistry; rewrites `_macros.puml`; called automatically by `write_artifact` when an entity's archimate display spec changes — ALG-C04 if count drift detected); `generate_er_content(entity_ids)` (reads each DOB entity's `§display ###er` block; returns PUML class declarations with attribute lists for direct paste into ER diagram); `generate_er_relations(connection_ids)` (reads each er-connection's `§display ###er` block; returns cardinality lines); `validate_diagram(puml_file_path)` (extracts all PUML aliases; checks each against ModelRegistry; verifies each resolved entity has the appropriate `§display ###<language>` section; confirms `!include _macros.puml` present for ArchiMate/use-case diagrams; returns list of validation errors; ALG-C03 on alias with no backing entity — model must be extended, alias must not be removed); `render_diagram(puml_file_path)` (invokes local `plantuml` CLI; writes SVG to the sibling `diagram-catalog/rendered/` directory for files in `diagram-catalog/diagrams/`; never writes to `diagrams/rendered/`; sprint-boundary render only unless on-demand requested by PM). Non-SA agents call `diagram.display-spec-request` handoff when a needed `§display ###<language>` subsection is missing from an entity. **Agents author PUML source text directly via `write_artifact`, following templates from `framework/diagram-conventions.md §7`.**
- [ ] **`src/agents/learning_store.py`**: `LearningStore` wrapper around LangGraph `BaseStore` (per `framework/learning-protocol.md §12.1`); implements `query()` and `record()` with graph-expansion and optional semantic tier; handles store rebuild from files on startup
- [x] **`src/common/framework_query/`**: queryable framework/spec index implemented (section-level metadata index + search scoring; optional semantic tier pending). API delivered: `list_docs`, `search_docs`, `read_doc`, `related_docs`; startup scan scope includes `framework/` plus orientation specs (`specs/IMPLEMENTATION_PLAN.md`, `README.md`, `CLAUDE.md`); CLI entrypoint at `python -m src.common.framework_query`.
- [x] **Framework doc graph extraction**: formal framework/spec references (`[@DOC:<doc-id>#<section-id>](...)`) parsed into directed section graph. APIs delivered: `neighbors()`, `trace_path()`.
- [~] **Framework index freshness model**: transparent freshness implemented in MCP context with background mtime polling watcher + TTL stale detection + optional caller-forced/manual refresh (`refresh=True` / CLI `refresh`). Remaining parity task: migrate to first-class evented filesystem watcher lifecycle when introduced.
- [ ] **`src/agents/tools/universal_tools.py`**: implement framework retrieval tools: `list_framework_docs`, `search_framework_docs`, and upgraded `read_framework_doc(section, mode)` with summary-first policy and full-read reason logging.
- [x] **CLI**: `uv run python -m src.common.framework_query <stats|list|search|read|related>` for deterministic local navigation/debug.
- [x] **CLI extension**: graph and maintenance commands implemented (`neighbors`, `path`, `refresh`).
- [x] **MCP surface** (framework-doc discovery): implemented in `src/tools/mcp_framework_server.py` and `src/tools/framework_mcp/` with tools `framework_query_stats`, `framework_query_list_docs`, `framework_query_list_sections`, `framework_query_search_docs`, `framework_query_read_doc` (supports `section_id` + unknown-section suggestions), `framework_query_resolve_ref`, `framework_query_related_docs`, `framework_query_neighbors`, `framework_query_path` (optional diagnostics), `framework_query_path_batch`, `framework_query_missing_links`, `framework_query_validate_refs` backed by the same index as Python/CLI.
- [ ] **`src/agents/project_manager.py`**: PM agent with `result_type=PMDecision`; all PM skills loaded via SkillLoader
- [ ] **`src/agents/solution_architect.py`**: SA agent; Discovery Scan tool registered; all SA skills loadable
- [ ] **`src/agents/software_architect.py`**: SwA agent; Reverse Architecture Reconstruction support for EP-G
- [ ] **`src/agents/devops_platform.py`**: DO agent; pipeline execution tools
- [ ] **`src/agents/implementing_developer.py`**: DE agent; target-repo write tools
- [ ] **`src/agents/qa_engineer.py`**: QA agent; Compliance Assessment co-production tools
- [ ] **`src/agents/__init__.py`**: `AGENT_REGISTRY: dict[str, Agent]` — pre-built agent instances for all roles

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

- [ ] **`src/orchestration/graph_state.py`**: `SDLCGraphState` TypedDict — as specified in orchestration-topology.md §3, extended with: `target_repository_ids: list[str]` (all registered repo IDs for this engagement; populated at `EngagementSession` startup from `engagements-config.yaml`); `primary_repository_id: str | None` (id of the primary repo, or None for single-repo backward compat)
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
- [ ] **`src/orchestration/session.py`**: `EngagementSession` — top-level entry point; loads engagements-config.yaml; calls `event_store.replay_from_latest_snapshot()` (fallback: full `replay()`); emits `engagement.started` + `event_store.create_snapshot("engagement.started")` after bootstrap; emits `sprint.started` when first specialist invocation of a new sprint is detected; resumes `graph.stream()`; handles CQ user interaction loop
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
- [ ] Retroactive: add Discovery Scan Step 0 (five-layer scan per `framework/discovery-protocol.md §2`) to all Stage 3 skill files — Step 0.L is present in all files; the broader Step 0 envelope is not (tracked since Stage 3 review)
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

### Stage 6 — Integration Testing

- [ ] Define synthetic project in `tests/synthetic-project/` (small but non-trivial: a web service with a clear business requirement, a safety-relevant component, and at least one mid-project requirement change)
- [ ] Run full chain from Phase A through Phase G
- [ ] Validate: all handoff artifacts produced, all schemas satisfied, no orphaned outputs
- [ ] Identify token budget actuals vs estimates, calibrate summary-vs-full retrieval thresholds
- [ ] Document lessons learned → feed into skill file revisions
- [ ] Commit as `stage-6-integration-validated`

---

### Stage 4.8g — Skill/Agent Alignment Audit (Complete — 2026-04-08; commit pending)

> **Purpose:** Verify that existing agent and skill files are fully consistent with the revised information-discovery and work-repository interaction plans added in Stage 4.9h and the snapshotting spec. Do not assume alignment — read the files.

#### Audit scope

1. **Reverse-architecture skills** — read `agents/solution-architect/skills/reverse-architecture-bprelim-a.md`, `agents/solution-architect/skills/reverse-architecture-ba.md`, `agents/software-architect/skills/reverse-architecture-ta.md` in full. Check:
   - Does Step 0 call `scan_target_repo()`? (Required to emit `source.scanned` via the tool)
   - Does Step 3 (confirmation loop) produce any output that the tool cannot derive? If so, is `upload_refs` kwarg needed, and must the skill instruct the agent to pass it?
   - Does Step 4 call `write_artifact`? Does current wording imply the agent must supply `source_evidence` as a parameter, or is auto-extraction from `[inferred: <source>]` annotations sufficient?
   - Any instruction that contradicts the tool-transparent emission design (§4.9h)?

2. **All `write_artifact`-using skills** — grep all skill files for `write_artifact` calls. For each: does the skill instruct the agent to pass any evidence, version, or metadata that the §4.9h port spec now handles automatically? Flag contradictions.

3. **Discovery Scan step wording (all skill files)** — the existing Step 0 wording references a 5-layer scan. Verify it is consistent with `framework/discovery-protocol.md §2` as currently written. Flag any gaps vs. the EventStore-state layer (Layer 5) — this overlaps with the outstanding retroactive item in §"Current State".

4. **`framework/agent-runtime-spec.md §6` (tool set spec)** — read the tool set section. Verify `ArtifactReadWriterPort.write()` signature matches the updated `write(path, content, *, upload_refs=None)` spec. Flag if `scan_target_repo` is documented as emitting `source.scanned`.

5. **`framework/discovery-protocol.md`** — verify Step 0 scan coverage includes `source.scanned` event emission as a side-effect of the discovery scan, not a separate agent action.

#### Outcome options per finding

- **No gap:** note it; no file change.
- **Skill wording contradicts tool-transparent design:** update the skill step to remove the contradiction (e.g., remove instruction to pass `source_evidence` explicitly if auto-extraction is sufficient).
- **Skill wording is silent where explicit guidance adds value:** add a brief ≤2-line note to the relevant step (budget: `complexity-class: complex` = 2000 tokens; headroom is sufficient for small additions).
- **Framework doc gap:** update the relevant framework doc section; no skill change needed.
- **Any change that would push a skill over its `complexity-class` soft cap:** split the skill into two (e.g., `reverse-architecture-bprelim-a-steps1-3.md` + `reverse-architecture-bprelim-a-steps4-7.md`) before making the addition.

#### Checklist

- [x] Read and audit 3 reverse-arch skill files (Step 0, 3, 4 focus)
- [x] Grep all skill files for `write_artifact`; check for conflicting instructions
- [x] Verify Step 0 wording across at least a representative sample of Stage 3 skills
- [x] Read `framework/agent-runtime-spec.md §6` tool set spec
- [x] Read `framework/discovery-protocol.md §2` and §4 (Layer 4 target-repo scan)
- [x] Execute any confirmed changes; update IMPLEMENTATION_PLAN.md findings table when done
- [ ] Commit as part of `stage-4-pre5-alignment`

---

## Current State & Immediate Next Actions

**Stages 1–4.9g complete. ModelVerifier complete (71 BDD tests). Stage 4.9f core diagrams remain 7/7 complete; diagram naming is now scope-based and workflow-net activity coverage is expanded (core set + additional workflow-net views), rendered, and verified (`model_verify_all`: 0 errors, 0 warnings). Stage 4.8g alignment audit is complete with reverse-architecture skill wording adjusted to query-first/model-writer intent. Stage 4.9g overview/ADR documentation is now present in ENG-001 architecture-repository. Slice A framework MCP freshness/path parity is validated by targeted `uv run pytest` tests. `src/common/model_query.py` complete.**

**Blocker update (2026-04-08, session 20):** the session-19 `E201` surge was a stale incremental verifier-state artifact, not an active regex/rule defect. Forced full verification confirms ENG-001 baseline at **2022 files, 0 errors, 0 warnings**. Incremental state now includes verifier-engine signature invalidation, so rule-engine changes force a full recompute instead of replaying stale cached issues.

**Validation update (2026-04-08, session 22):** `model_verify_all` now returns **2024 files, 0 errors, 0 warnings** after the application-layer runtime-boundary remediation slice.

**Validation update (2026-04-08, session 23):** after application-architecture adequacy improvements (algedonic fast-path sequence, orchestrator->CSCO composition mapping, APP-015->BPR-005 realization, and runtime matrix escalation row), `model_verify_all` returns **2027 files, 0 errors, 0 warnings**.

**Validation update (2026-04-08, session 26):** after Stage 4.9i technology baseline additions (NOD-001/SSW-001/TSV-001 entities, serving/composition relations, and hosting diagram+matrix views), `model_verify_all` returns **2037 files, 0 errors, 0 warnings**.

**Validation update (2026-04-09, session 28):** after holistic memory architecture additions (DOB-014/APP-023/AIF-007 entities + 4 connections + AIF-006 orphan fix + specialist invocation sequence update), `model_verify_all` returns **2048 files, 0 errors, 0 warnings**.

### Immediate next actions

- Stage 4.9 memory architecture extension complete (session 28). Memory design decisions resolved:
  - Official agent-phase skills stay as static markdown with deterministic routing — NOT converted to memento-skills.
  - Five-tier memory architecture defined (Tier 0 conversation buffer through Tier 4 enterprise knowledge).
  - `query_learnings()` extended with `skill_id` + `entry_type` params (unified tool — no separate skill-amendment tool).
  - `entry-type: episodic` and `entry-type: skill-amendment` added to LearningEntry schema.
  - `MementoState` (DOB-014), `MementoStore` (APP-023), `MementoPort` (AIF-007) added to model.
  - Discovery protocol updated: Step 0.M added; end-of-skill close template added to §6.
- Continue Stage 5 integration focus items: EventStore/orchestration/tooling completion and integration-test readiness.
- Stage 5 implementation now includes `src/agents/memento_store.py` (MementoStore wrapper around LangGraph BaseStore).
- Outstanding retroactive: add Step 0.M + end-of-skill close to Stage 3 skill files (alongside the existing Step 0 envelope item, deferred to 5e).
- Implement modeled control-loop reliability semantics in code: event_id-based idempotent dedup, correlation-id propagation, fail-safe timeout branches.

### Completed this session (2026-04-08 — session 25)

- **Priority-filtered best-practice propagation (solution-architecture quality):**
  - Applied runtime-sequence refinements only where risk impact is high:
    - event_id-based dedup path (CQ flow exemplar) in `runtime-sequence-cq-routing-resume-v1.puml`
    - invocation correlation continuity (`invocation_id`) in `runtime-sequence-specialist-invocation-cycle-v1.puml`
    - fail-closed timeout behavior for safety vote absence in `runtime-sequence-gate-evaluation-decision-path-v1.puml`
    - fail-safe timeout-to-containment branch + `correlation_id` in `runtime-sequence-algedonic-escalation-fastpath-v1.puml`
  - Propagated the same controls into architecture narrative and traceability matrix:
    - `overview/aa-overview.md`
    - `runtime-matrix-business-to-application-traceability-v1.md`
  - Codified these controls in framework guidance:
    - `framework/diagram-conventions.md` (`§7.sequence` runtime quality controls)

### Completed this session (2026-04-08 — session 26)

- **Stage 4.9i infrastructure baseline elaboration (technology layer):**
  - Added technology entities for local runtime substrate:
    - `NOD-001.local-runtime-host.md`
    - `SSW-001.python-runtime-and-uv-toolchain.md`
    - `TSV-001.local-file-and-process-service.md`
  - Added technology/application relation set:
    - `NOD-001---SSW-001@@archimate-composition.md`
    - `SSW-001---TSV-001@@archimate-serving.md`
    - `TSV-001---APP-001@@archimate-serving.md`
    - `TSV-001---APP-016@@archimate-serving.md`
    - `TSV-001---APP-020@@archimate-serving.md`
  - Added companion infrastructure views:
    - `technology-archimate-local-runtime-hosting-v1.puml`
    - `technology-matrix-runtime-hosting-traceability-v1.md`
  - Updated `overview/aa-overview.md` with explicit technology baseline mapping.
  - Validation checkpoint:
    - `model_verify_all` (ENG-001 scope) -> **2037 files, 0 errors, 0 warnings**.

### Completed this session (2026-04-08 — session 27)

- **Stage 4.9i operational behavior + conformance closure:**
  - Added technology operational sequence views:
    - `technology-sequence-runtime-bootstrap-provisioning-v1.puml`
    - `technology-sequence-event-persistence-snapshot-policy-v1.puml`
    - `technology-sequence-replay-hydration-on-resume-v1.puml`
    - `technology-sequence-observability-query-path-v1.puml`
  - Completed 4.9i checklist closure:
    - operational behavior package marked complete
    - cross-layer conformance + verification package marked complete
  - Re-rendered new sequence diagrams to canonical `diagram-catalog/rendered/`.
  - Validation checkpoint:
    - full `ModelVerifier.verify_all(...)` (ENG-001 scope) -> **0 errors, 0 warnings**.

### Completed this session (2026-04-08 — session 22)

- **Application-layer adequacy remediation (local developer-machine runtime):**
  - Added explicit read-side serving relation `APP-001---APP-020@@archimate-serving` to model EventStore-backed dashboard query paths.
  - Propagated runtime boundary semantics across:
    - `application-archimate-component-map-v1.puml`
    - `runtime-archimate-application-interaction-boundaries-v1.puml`
    - `runtime-sequence-cq-routing-resume-v1.puml`
    - `runtime-sequence-sprint-review-correction-loop-v1.puml`
    - `runtime-matrix-business-to-application-traceability-v1.md`
  - Re-rendered modified PUML diagrams to `diagram-catalog/rendered/`.
- **Validation checkpoint:**
  - `model_verify_all` (ENG-001 scope) -> **2024 files, 0 errors, 0 warnings**.

### Completed this session (2026-04-08 — session 23)

- **Application-architecture adequacy review and remediation (problem/solution-space):**
  - Added explicit safety fast-path control-loop coverage in application runtime:
    - new diagram `runtime-sequence-algedonic-escalation-fastpath-v1.puml`
    - updated `runtime-sequence-gate-evaluation-decision-path-v1.puml` for orchestrator-led CSCO safety vote invocation
  - Added model relations to remove traceability blind spots:
    - `APP-016---APP-015@@archimate-composition`
    - `APP-015---BPR-005@@archimate-realization`
  - Updated cross-layer matrix `runtime-matrix-business-to-application-traceability-v1.md` with a dedicated BPR-005 escalation row and links to realization + runtime-sequence evidence.
  - Updated runtime/application boundary diagrams to include CSCO composition in runtime topology.
- **Validation checkpoint:**
  - `model_verify_all` (ENG-001 scope) -> **2027 files, 0 errors, 0 warnings**.

### Completed this session (2026-04-08 — session 24)

- **Solution-architecture propagation audit completed:**
  - Framework guidance updated in `framework/diagram-conventions.md` to require a conditional algedonic fast-path runtime sequence whenever safety escalation behavior is modeled.
  - ENG-001 application architecture narrative updated in `overview/aa-overview.md` with explicit runtime control-path table including algedonic escalation traceability.
  - Stage 4.9i artifacts, overview docs, and rendered diagrams now reflect a consistent application-layer control architecture across CQ/review/gate/algedonic paths.

### Completed this session (2026-04-08 — session 20)

- **Incremental verifier cache invalidation hardened:**
  - `src/common/model_verifier_incremental.py`: added `verifier_engine_signature()` and persisted signature in state payload.
  - `src/common/model_verifier.py`: incremental-mode fallback now forces full verify when cached `engine_signature` differs.
  - `src/common/model_verifier_types.py`: `IncrementalState` now carries `engine_signature`.
  - `tests/model/test_model_verifier_incremental.py`: added regression case proving stale cache invalidation on engine-signature mismatch.

- **Verifier baseline revalidated:**
  - `uv run pytest tests/model/test_connection_verifier.py` -> **14 passed**.
  - `SDLC_MODEL_VERIFY_MODE=full ... ModelVerifier.verify_all(...)` (ENG-001 scope) -> **2022 files, 0 errors, 0 warnings**.

### Completed this session (2026-04-08 — session 19)

- **Connection `@@` contract hardening delivered in verifier + tests + docs:**
  - `src/common/model_verifier_rules.py`: added `E203` (`@@suffix` must equal frontmatter `artifact-type`) and `E205` (artifact-id source/target composition must match frontmatter `source`/`target`).
  - `tests/model/test_connection_verifier.py` + `tests/model/features/connection_verifier.feature`: added scenario coverage for `E203` and `E205`.
  - Contract docs aligned in:
    - `framework/artifact-registry-design.md`
    - `framework/artifact-schemas/entity-conventions.md`
    - `framework/repository-conventions.md`

- **Runtime application interaction boundary clarification completed:**
  - Kept `APP-008` as SA-specific entity (no generic conversion).
  - Annotated `runtime-archimate-application-interaction-boundaries-v1.puml` to explicitly mark SA as exemplar for this slice and note role-polymorphic invocation behavior.
  - Re-rendered `runtime-archimate-application-interaction-boundaries-v1.svg` after annotation.

- **Evidence captured:**
  - `uv run pytest tests/model/test_connection_verifier.py` -> **14 passed**.
  - `model_verify_all` (ENG-001 architecture-repository scope) -> **2022 files, 1369 errors, 0 warnings** (known `E201` over-strictness blocker).

### Completed this session (2026-04-08 — session 18)

- **Stage 4.8g alignment audit closed with targeted edits:**
  - Audited all three reverse-architecture skills (`SA-REV-PRELIM-A`, `SA-REV-BA`, `SWA-REV-TA`) for Step 0 and model-write wording drift.
  - Updated legacy `list_artifacts(directory=...)` references in core procedural steps to query-first `model_query_list_artifacts(...)` intent.
  - Updated Step 4/5 wording in all three skills from direct `write_artifact` signature emphasis to deterministic model writer intent (`model_create_entity` / `model_create_connection`, `dry_run` first) while preserving runtime compatibility guidance.

- **Stage 4.9g documentation deliverables completed:**
  - Added ENG-001 overview documents:
    - `overview/architecture-vision.md`
    - `overview/aa-overview.md`
  - Added ENG-001 decision records:
    - `decisions/ADR-001.md` (PydanticAI)
    - `decisions/ADR-002.md` (LangGraph)
    - `decisions/ADR-003.md` (SQLite EventStore)
    - `decisions/ADR-004.md` (FastAPI + Jinja2 + SSE)
    - `decisions/ADR-005.md` (File-based ERP storage)

### Completed this session (2026-04-08 — session 17)

- **PM-G workflow cleanup completed (control-flow + labeling):**
  - Removed duplicate/superfluous decision-node pattern around targeted rework.
  - Removed redundant intermediate targeted-rework handoff/wait activities in the lower loop.
  - Preserved semantically correct loop behavior; explicit `no` exit label retained to BPR-004 evaluation path.

- **Diagram naming normalization completed across broader non-phase sets:**
  - Renamed non-phase-prefixed artifacts in motivation/business/application/usecase families to scope/purpose-based IDs.
  - Updated frontmatter `artifact-id`, `@startuml` identifiers, in-repo references, and rendered SVG filenames.
  - Re-rendered canonical outputs to sibling `diagram-catalog/rendered/` only.

- **Validation:**
  - `ModelVerifier.verify_all(...)` run after renames and PM-G updates: **2016 files, 0 errors**.

### Completed this session (2026-04-08 — session 16)

- **Framework-first naming-contract update completed:**
  - Updated diagram filename policy from phase-forced to scope-based across framework contracts.
  - `framework/diagram-conventions.md`: `<scope>-...` pattern with explicit rule: use phase token only when phase-scoped.
  - Aligned examples in `framework/artifact-registry-design.md`, `framework/repository-conventions.md`, and `framework/artifact-schemas/diagram-catalog.schema.md`.

- **ENG-001 diagram normalization completed (rename + reference sweep):**
  - Renamed phase-prefixed diagrams to scope-appropriate IDs where needed:
    - `phase-b-archimate-business-v1` -> `business-archimate-combined-v1`
    - `phase-application-archimate-component-map-v1` -> `application-archimate-component-map-v1`
    - `phase-application-class-er-domain-model-v1` -> `application-class-er-domain-model-v1`
    - `phase-b-activity-sprint-v1` -> `lifecycle-activity-sprint-v1`
    - `phase-c-activity-cq-lifecycle-v1` -> `cq-activity-lifecycle-v1`
    - `phase-c-activity-sprint-review-v1` -> `sprint-review-activity-workflow-v1`
    - `phase-g-activity-skill-invocation-v1` -> `specialist-invocation-activity-workflow-v1`
  - Updated frontmatter `artifact-id`, `@startuml` identifiers, and in-repo references.
  - Removed non-canonical rendered leftovers from `diagram-catalog/diagrams/`.

- **Workflow-net modeling expansion (agent-phase focused):**
  - Added new activity/BPMN workflow nets:
    - `b-activity-sa-phase-b-workflow-v1.puml`
    - `c-activity-swa-phase-c-application-workflow-v1.puml`
    - `g-activity-pm-phase-g-governance-workflow-v1.puml`
  - Added coverage matrix artifact:
    - `workflow-net-matrix-agent-phase-skill-coverage-v1.md`
  - Aligned runtime/authoring guidance in:
    - `framework/orchestration-topology.md`
    - `agents/solution-architect/skills/phase-b.md`
    - `agents/software-architect/skills/phase-c-application.md`
    - `agents/project-manager/skills/phase-g.md`

- **Validation and rendering:**
  - Re-rendered modified/new PUML files to canonical sibling `diagram-catalog/rendered/`.
  - Ran verifier: `uv run ... ModelVerifier.verify_all(...)` -> **2016 files, 0 errors, 0 warnings**.

### Completed this session (2026-04-08 — session 15)

- **Slice A closure validated:**
  - Ran targeted framework MCP parity tests with `uv run pytest tests/tools/test_framework_mcp_tool_improvements.py tests/model/test_framework_query.py tests/tools/test_registry_asyncio_and_mcp_servers.py`.
  - Result: all tests passed.

- **Slice B completed (Wave 3 Stage 4.9f):**
  - Added business workflow activity/BPMN diagrams:
    - `specialist-invocation-activity-workflow-v1.puml`
    - `cq-activity-lifecycle-v1.puml`
    - `sprint-review-activity-workflow-v1.puml`
  - Added supporting business-flow model artifacts under `connections/activity/sequence-flow/`.
  - Rendered canonical SVG outputs in sibling `diagram-catalog/rendered/`.
  - Ran `model_verify_all` for engagement scope: 0 errors, 0 warnings.

### Completed this session (2026-04-08 — session 14)

- **Wave 2 nested-subgraph contract deepening completed (framework-first):**
  - Added documentation-level subgraph decomposition matrix to `framework/orchestration-topology.md` with explicit runtime ownership per tier.
  - Added deterministic-vs-agentic checklist per workflow unit with explicit precondition, event, merge, and suspend/resume invariants.
  - Added minimal Stage 5 node/routing implementation checklist (state fields, event touchpoints, gate ownership, escalation points) sufficient to author and verify orchestration code without policy ambiguity.
  - Added implementation-plan traceability note in Stage 5c linking Wave 2 completion to topology sections.

### Completed this session (2026-04-08 — session 13)

- **Wave 1 clarification/coordination semantics completed (contract-first):**
  - Added shared two-class interaction taxonomy across framework contracts: (1) User-facing Clarification Interaction (CQ) and (2) Agent-directed Coordination Interaction.
  - Added explicit non-goal boundary: retrieval tool behavior (`list/search/read/count/find`) is not an interaction class and is not CQ-routed.
  - Added routing contract mapping (initiator, responder, PM routing ownership, required events, suspension behavior) in:
    - `framework/clarification-protocol.md`
    - `framework/orchestration-topology.md`
    - `framework/agent-runtime-spec.md`

### Completed this session (2026-04-08 — session 11)

- **Wave 0 contract alignment completed (framework-first, no diagram-conventions meta-level edits):**
  - `framework/artifact-schemas/diagram-catalog.schema.md` rewritten from legacy catalog-index model to ERP v2.0 file-first diagram schema.
  - Explicitly removed legacy assumptions from the schema contract: no `elements/*.yaml`, `connections/*.yaml`, `diagrams/index.yaml`, or `catalog_register()` runtime path.
  - Added deterministic required frontmatter contract for diagram artifacts and verifier/tooling contract references (`model_create_diagram`, `model_create_matrix`, `model_verify_*`).
  - `framework/orchestration-topology.md` updated with an agent-phase workflow decomposition contract defining deterministic vs agentic step mapping, decision/suspension handling, and fan-out constraints.
  - `framework/clarification-protocol.md` updated with explicit inter-agent clarification boundary: no separate agent-to-agent CQ channel; use feedback/handoff + PM arbitration.

### Completed this session (2026-04-08 — session 12)

- **Framework/model query improvement wave implemented and validated:**
  - Framework query engine now supports deterministic section targeting via `section_id` and exposes `list_sections()` + `suggest_sections()` helpers.
  - Framework MCP surface extended with `framework_query_list_sections`; `framework_query_read_doc` now accepts `section_id` and returns nearest section suggestions on unknown-section errors.
  - Framework MCP graph/discovery surface deepened with `framework_query_resolve_ref`, `framework_query_path(include_diagnostics)`, `framework_query_path_batch`, `framework_query_missing_links`, and `framework_query_validate_refs`.
  - Transparent framework-index freshness implemented in MCP context (background mtime poller + TTL stale guard + freshness metadata in responses).
  - Model query engine now supports record-type prioritization controls for search (`prefer_record_type`, `strict_record_type`) and aggregate grouping via `count_artifacts_by(...)`.
  - Model MCP surface extended with `model_query_count_artifacts_by`; `model_query_list_artifacts` and `model_query_search_artifacts` now support compact field projection (`fields=[...]`) to reduce large payload friction.
  - Validation complete with targeted tests and BDD additions: `uv run pytest tests/model/test_framework_query.py tests/model/test_model_query.py tests/tools/test_registry_asyncio_and_mcp_servers.py tests/tools/test_model_query_mcp_improvements.py`.

### Completed this session (2026-04-07 — session 10)

- **Framework-doc tooling implemented end-to-end (query + graph + MCP):**
  - Refactored monolithic `src/common/framework_query.py` into a small-module package `src/common/framework_query/` (`types.py`, `parsing.py`, `index.py`, `cli.py`, `__init__.py`, `__main__.py`) to satisfy maintainability and file-size limits.
  - Implemented framework/spec query APIs: `list_docs`, `search_docs`, `read_doc`, `related_docs`, plus graph traversal APIs `neighbors` and `trace_path` over formal `@DOC` references.
  - Added CLI support: `python -m src.common.framework_query <stats|list|search|read|related|neighbors|path|refresh>`.
  - Implemented dedicated MCP server `src/tools/mcp_framework_server.py` with tool family `framework_query_*` and graph exploration parity with model-query style traversal.

- **Registry asyncio failure resolved + regression coverage added:**
  - Fixed nested-event-loop risk in registry service by removing `anyio.run` from sync path reads (`src/tools/mcp_registry/service.py`).
  - Added regression test that executes registry service calls from inside an active asyncio loop.

- **MCP coverage and config updates completed:**
  - Added test coverage for tool-surface contracts across model/registry/framework MCP servers and behavior tests for framework MCP tools.
  - Registered framework MCP server in `.mcp.json` and `.vscode/mcp.json`.
  - Added script entrypoint `sdlc-mcp-framework` in `pyproject.toml`.

- **Central authoritative tool catalog established:**
  - Added `framework/tool-catalog.md` as canonical runtime inventory for all MCP servers and tool families.
  - Linked runtime spec and README status/readme sections to the centralized catalog.

### Completed this session (2026-04-07 — session 9)

- **Documentation remediation started for orchestration + skill clarity:**
  - Normalized diagramming hints in skill files: removed from non-diagram skills; retained only where skills produce/update diagram artifacts.
  - Added explicit authoring rule in `CLAUDE.md` requiring diagram hints to be scoped, well-positioned, and minimal.
  - Clarified `framework/discovery-protocol.md` execution order: core Step 0.L + Layers 1-5 first, then optional Step 0.D/0.S/0.F, then Gap Assessment/CQs.
  - Updated orchestration target architecture in `framework/orchestration-topology.md` and Stage 5 planning notes to nested LangGraph subgraphs with PydanticAI at specialist leaf nodes.
  - Added stage/agent review-gate policy model in Stage 5.5 docs so blocking human review can gate downstream dependent stages.
  - Added query-first framework retrieval architecture doc: `framework/framework-knowledge-index.md` (section-level index model, Python API, CLI, MCP tool surfaces, migration plan).
  - Updated `framework/agent-runtime-spec.md` and Stage 5b tool planning from broad framework reads to indexed `list/search/read` framework-doc tooling.
  - Removed broad "read all framework docs" instructions from PM/SA/DE/QA docs; replaced with focused section-scoped retrieval guidance.

### Completed this session (2026-04-06 — session 8)

- **Rendering-path invariant enforced end-to-end:**
  - Removed non-canonical rendered artifacts under `diagram-catalog/diagrams/rendered/`.
  - Updated framework/docs/spec text to require rendering from `diagram-catalog/diagrams/` into sibling `diagram-catalog/rendered/` only.
  - Regenerated modified SVGs in canonical `diagram-catalog/rendered/`.

- **SA traceability logic upgraded from intent-to-value with verifiable outcomes:**
  - Prescribed mandatory chain across SA agent-definition and skills: `STK -> DRV -> GOL -> OUT -> COA -> CAP -> (BPR/BSV) -> VS-stage value`.
  - Updated schema guidance (`architecture-vision`, `business-architecture`, `requirements-register`) to include measurable outcomes (`OUT`) and courses of action (`COA`) with value-evidence linkage.
  - Updated process governance (`agile-adm-cadence` universal gate checklist) to require outcome-evidence chain integrity at gates.

- **ENG-001 model implemented for outcome-evidence traceability:**
  - Added entity sets: `OUT-001..002`, `COA-001..002`, `VAL-001..002` with ERP-compliant files and display specs.
  - Added motivation/strategy/business cross-layer connections linking stakeholder intent to operational evidence and value-stream value.
  - Added new diagram: `motivation-archimate-outcome-course-value-traceability-v1.puml` and rendered SVG.
  - Repaired stale BPR-006 aliases in `business-archimate-concept-v1.puml` and `business-archimate-combined-v1.puml`.
  - Full verifier run via `uv run`: **2001 files, 0 errors**.

### Completed this session (2026-04-06 — session 7)

- **Dense-diagram decomposition policy codified across framework + skills:**
  - `framework/diagram-conventions.md` updated to v2.3.0 with mandatory dense-edge decomposition rule (§0.2.1): after one layout pass, split monolithic diagrams into thematic slices and add matrix companion artifacts for full coverage.
  - `framework/diagram-conventions.md §5.D0` now explicitly instructs agents to stop layout tuning when lane overlap persists and switch to split-diagram + matrix strategy.
  - `framework/artifact-registry-design.md` updated to v2.2.0 with the dense-association modeling pattern (§2.6): focused `.puml` slices plus full-coverage `.md` matrix as a paired output.
  - SA runtime guidance updated in `agents/solution-architect/skills/phase-a.md` and `agents/solution-architect/skills/phase-b.md` so active skills explicitly direct this strategy at execution time.
  - Orientation docs updated (`README.md`, `CLAUDE.md` rule 29) so the policy is visible both to implementers and to agent authors.

- **Diagram-vs-matrix representation policy is now explicit, balanced, and uniform across framework + skills:**
  - `framework/agent-runtime-spec.md` now documents matrix creation alongside diagram creation in the runtime tool-capability map.
  - `framework/diagram-conventions.md` now includes an explicit representation-choice step: use diagrams for topology/flow/context and matrices for high-cardinality mapping/coverage views.
  - A coverage guardrail now explicitly prevents matrix-only replacement of contextual diagrams when structural or behavioral understanding would be lost.
  - `framework/artifact-registry-design.md` now treats `diagram-catalog/diagrams/*.md` matrix artifacts as first-class, discoverable architecture-view artifacts alongside `.puml`.
  - Runtime tooling hints were aligned across all role skill files (48 updates) with the same mandatory balanced-selection guidance.

### Completed this session (2026-04-06 — session 6)

- **Nested operational decomposition convention standardized across framework + SA skills:**
  - `framework/diagram-conventions.md` now explicitly mandates that decomposed `BPR-NNN` / `BIA-NNN` are diagrammed as nested parent containers (parent element is the container itself), not as outer groupings with duplicate parent nodes.
  - `§7.archimate-business-operational` template updated to show nested process/interaction containers with internal stage `flow` links.
  - `§11.9.1a` clarified that parent→stage `archimate-composition` files remain required model truth even when operational diagrams omit external composition arrows.
  - SA skill alignment completed in `agents/solution-architect/skills/phase-b.md` and `agents/solution-architect/skills/reverse-architecture-ba.md` so both greenfield and reverse-architecture BA outputs follow the same nested rendering policy.

### Completed this session (2026-04-05 — session 5)

- **Runtime search-space governance validated and documented**:
  - Skill inventory audit: 48 total skills; per-agent counts are bounded (`csco: 8`, `devops-platform: 4`, `implementing-developer: 3`, `product-owner: 5`, `project-manager: 6`, `qa-engineer: 3`, `sales-marketing: 3`, `software-architect: 8`, `solution-architect: 8`) — all within the <=12 target.
  - Complexity-class audit: all 48 skill files include valid `complexity-class` values (`simple: 6`, `standard: 24`, `complex: 18`); no missing or invalid frontmatter values.
  - Runtime loading scope made explicit in framework docs: Layer 1 (`system-prompt-identity`), Layer 2 (`### Runtime Behavioral Stance` only), Layer 3 (single `active_skill_id` skill sections only), Layer 4 (tool-returned artifact context on demand).
  - Tool surface budgeting documented in runtime spec: role-scoped tool families, target <=30 callable tools per agent, preferred 12-26 range.

- **Skill portability boundary clarified (hybrid model)**:
  - Skills remain strict on outputs, validation, and domain procedure.
  - Executable workflow logic (phase transitions, dependency gating, retries, suspend/resume) is explicitly assigned to orchestration harness and PM routing policy code.
  - `invoke-when` / `trigger-conditions` are retained as intent-level hints and documentation, not sole executable workflow contracts.

- **`framework/diagram-conventions.md` v2.3.0** — Major additions:
  - `§0.1` Phase B canonical diagram set updated: "Business architecture overview" split into **structural viewpoint** (BFN-centric: functions, roles, services, capabilities) and **operational viewpoint** (BPR-centric: processes, events, roles, services). Both are minima for greenfield Phase B; a single combined diagram is acceptable for small systems.
  - `§7.archimate-business` template updated: now shows the structural viewpoint (BFN groups with role/actor assignments, services outside groupings, capabilities in strategy layer). Includes single-vs-dual diagram guidance.
  - `§7.archimate-business-operational` template added: operational viewpoint (processes, business events, collaborations/interactions, services — no functions).
  - `§11.9 Business Layer Architecture Modeling Pattern` added — the authoritative specification for business-layer modeling across all engagements:
    - §11.9.1 Outside-In Principle (mandatory progression): VS stages → services/objects/interfaces → processes/interactions/events → functions → roles → BPMN sub-behavior
    - §11.9.2 Value Stream Stage Requirements (not ADM phases; 3–7 stakeholder-facing stages; each links to ≥1 BSV)
    - §11.9.3 Business Concept Map (BOB + BIF coherent graph; BEV as structural glue; BOB↔DOB mapping)
    - §11.9.4 Diagram Count and Scope (multiple diagrams normal; structural always includes roles; operational always includes roles/actors; distinguishing principle is organizing concept)
    - §11.9.5 Application-to-Business-Layer Connection Patterns (priority table: ASV→serving→BPR primary; full pattern options)
    - §11.9.6 Sprint Coverage Completeness Check (per-element-type minimum connection requirements)
    - §11.9.7 Cross-Layer Traceability and Mutual Validation (upward + downward traceability; completeness check in D1 step via list_connections; diagram cross-validation)

- **`agents/solution-architect/skills/phase-b.md`** — Restructured procedure around outside-in principle:
  - `Step 0.VS` added before Step 1: Value Stream Stage Definition — create/verify VS-nnn entities with stakeholder-facing stages; CQ trigger if no VS identifiable
  - `Step 1` replaced: now "Identify and Scope Business Services per VS Stage" — BSV-first, not capability-first; every BSV links to a VS stage
  - `Step 1.1` added: Capability Cross-Reference — demoted to a supporting EA step performed after BSV modeling, not the entry point
  - `Step 1.5` added: Business Concept Map — BOB (objects), BIF (interfaces), BEV (events) authored before processes; triggering connections required
  - `Step 2.5` added: Business Function Decomposition — BFN entities; assignment + realization connections; coverage rule; dual-viewpoint diagram steps using prescribed `list_artifacts`/`list_connections`/`validate_diagram` tools
  - Gate checklist updated: VS stages, BSV/BPR/BFN coverage, cross-layer traceability checks, dual-viewpoint diagram requirement

- **`agents/solution-architect/skills/phase-a.md`** — Step 4 updated: Value Stream sketch (VS-nnn stubs) now precedes capability overview; VS↔CAP traceability added.

- **`agents/software-architect/skills/phase-c-application.md`** — Step 1 cross-layer guidance corrected:
  - Entry point corrected to BSV/BPR/BFN (not CAP-first)
  - `ASV --serving--> BPR` established as primary cross-layer pattern (was incorrectly described as prohibited)
  - Full priority table added per §11.9.5
  - Collaborative behavior rule clarified: ACO+AIA is for structured multi-service sequences; single-service `ASV→serving→BPR` is correct and standard

- **`agents/product-owner/skills/phase-b.md`** — Minor corrections: BPR-nnn prefix fixed (was PRO-nnn); value stream stage requirement noted; BSV as primary requirement anchor (CAP as supporting cross-reference).

### Completed this session (2026-04-04, continued — session 4)

- **`src/common/model_query.py`** — `ModelRepository`: full in-memory indexed registry for model-entities, connections, and diagrams. Provides `list_entities/connections/diagrams(**filter)`, `get_entity/connection/diagram(id)`, `find_connections_for(entity_id, direction)`, `find_neighbors(entity_id, max_hops)`, `search(query)` (keyword TF-IDF + synonym expansion), and the framework-aligned `list_artifacts(**filter)` / `read_artifact(id, mode)` / `search_artifacts(query)` API from `framework/discovery-protocol.md §1.2–§1.3`. `ArtifactSummary` lightweight record type. `SemanticSearchProvider` Protocol for future sqlite-vec integration. CLI: `python -m src.common.model_query <stats|entities|connections|diagrams|get|graph|search>`. 36 BDD tests passing.
- **`src/common/domain_vocabulary.py`** — canonical SDLC domain vocabulary: bidirectional synonym map covering agent abbreviations (PM ↔ project manager), protocol/concept abbreviations (CQ ↔ clarification, ALG ↔ algedonic), ArchiMate artifact-id prefixes (BPR ↔ business process), and common domain concepts. `expand_tokens()` public API. `agent_abbreviations()` and `archimate_prefix_to_type()` lookup tables. `AIA` prefix added for ApplicationInteraction. Imported by `model_query.py`.

- **`src/common/model_verifier.py` — E306/E307 draft-reference checks**: `ModelRegistry` now provides `entity_status(id)` and `connection_status(id)` — each uses a targeted single-file lookup when the full cache is cold (O(1) cache hit; O(n) walk only on cold miss), avoiding full scans for individual status checks. Bulk access via `entity_statuses()` / `connection_statuses()` triggers one lazy scan and caches results. E306 (baselined diagram references draft entity) and E307 (baselined diagram references draft connection) added to `_check_diagram_references`; both are suppressed for draft diagrams (draft→draft-element is allowed during in-sprint authoring). 2 new BDD scenarios; 71 tests passing.

- **PlantUML alias hyphen-vs-underscore fix**: `application-class-er-domain-model-v1.puml` corrected: all PUML element aliases changed from `DOB-NNN` (hyphen) to `DOB_NNN` (underscore); PlantUML treats `-` as arithmetic in identifier contexts. `framework/diagram-conventions.md §7.er` template and rule updated to match (was incorrectly specifying hyphenated aliases).

- **Entity filename convention** — New format `[TYPEABBR-###].[friendly-name].md` adopted. All 98 entity files renamed; BCO-001 (formerly ACT-011) renamed with correct prefix. `src/common/model_verifier.py` updated: `entity_id_from_path()` public utility added (single point for formal-ID extraction from filename, ignoring friendly-name suffix); `_check_artifact_id_entity()` now validates filename prefix (E104); `ModelRegistry.find_file_by_id()` added. `framework/artifact-registry-design.md §3.0` documents the convention. BDD test suite updated: 33 tests passing.
- **BCO-001 (Architecture Board) correction** — BusinessCollaboration prefix corrected from `ACT` → `BCO` per artifact-registry-design.md §4. Entity file renamed, frontmatter `artifact-id` updated, alias `BCO_001` in `§display`. Connection `ACT-011---BPR-007.md` renamed to `BCO-001---BPR-007.md`. `_macros.puml` regenerated (`DECL_BCO_001` now correct). BCO-001 entity content updated: User is explicitly head/final authority of the Architecture Board; SA and SwA are participating members.
- **Phase-B diagram — complete connectivity** — `business-archimate-combined-v1.puml` updated to v0.3.0: 9 new assignment connections (all specialist roles now assigned to BPR-002; CSCO additionally to BPR-004/005; PM to BPR-005); all 5 orphan BSVs realised by BPR-002; BPR-008 realises BSV-001; 7 new BPR→CAP realization connections (cross-layer, steel blue). 9 new assignment + 7 new BPR→CAP realization connection files created. Total: 17 assignment + 22 realization connection files. No entity in phase-b is now unconnected. ModelVerifier: 204 files, 0 errors.
- **README + diagram-conventions.md** — Activity diagram description corrected to cover three scopes: (1) external business processes of the client organisation (Phase B), (2) process logic within the software being built (Phase C), (3) ENG-001 meta-level (framework orchestration, binding spec for `src/orchestration/`). `diagram-conventions.md §7.activity-bpmn` updated with separate business-layer and application-layer templates and rules. Version bumped to 2.2.0.

### Resume at: Stage 5 implementation

**Stage 4.9f is complete (2026-04-08, session 15).**

Completion evidence:
1. Added remaining activity/BPMN workflow diagrams:
  - `specialist-invocation-activity-workflow-v1.puml`
  - `cq-activity-lifecycle-v1.puml`
  - `sprint-review-activity-workflow-v1.puml`
2. Added supporting activity sequence-flow connection artifacts:
  - `BPR-001---BPR-002`, `BPR-201---BPR-202`, `BPR-202---BPR-203`, `BPR-002---BPR-004`
  - `BPR-301---BPR-302`, `BPR-302---BPR-303`
  - `BIA-101---BIA-102`, `BIA-102---BIA-103`
3. Rendered all three to canonical sibling `diagram-catalog/rendered/` outputs.
4. `model_verify_all` (engagement scope) returned 0 errors and 0 warnings.

**`src/common/model_query.py` pre-empts Stage 5b `src/common/model_registry.py` (in-memory tier only).** The production Stage 5b model registry adds: SQLite FTS5 full-text index, `watchdog` filesystem listener for incremental refresh, sqlite-vec embedding tier, and thread-safety (`threading.RLock`). `model_query.py`'s `ModelRepository` provides the in-memory query API that the Stage 5b tools delegate to; the interface (`list_artifacts`, `search_artifacts`, `read_artifact`) is already production-ready and will not change.

**Stage 4.9e** — ✅ Complete: 115 connection files (original 89 + 9 new assignment + 7 new BPR→CAP realization).
**Stage 4.9f** — ✅ Complete: core 7/7 diagrams done, semantically corrected, rendered to SVG, verifier clean (0 errors, 0 warnings); additional workflow-net activity views added in session 16.
**`_macros.puml`** — ✅ Regenerated: 99 macros, BCO_001 alias correct.

**Stage 4.9** — ENG-001 reference model: entity files, connection files, `_macros.puml`, and seven PUML diagrams. Documents the SDLC system itself. Serves as integration test fixture. Entity ownership reflects Stage 4.8h model (SwA owns APP/DOB entities; SA owns motivation/strategy/business entities).

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

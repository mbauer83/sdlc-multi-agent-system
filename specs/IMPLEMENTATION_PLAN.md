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
| Solution Architect | A, B, C, H | D, E, Req-Mgmt |
| Software Architect / Principal Engineer | D, E, F, G, H | C, Req-Mgmt |
| DevOps / Platform Engineer | D, E, F, G | — |
| Implementing Developer | G | E, F, Req-Mgmt feedback |
| QA Engineer | E/F (test planning), G | H |
| Project Manager | Prelim, A, E, F, G, H | All (coordination) |
| Chief Safety & Compliance Officer | A, B, C, D, G, H | All (gate reviews) |

### Repository Ownership

Work-repositories are role-owned, version-controlled, and path-governed. No agent writes outside its designated paths. Cross-role artifact transfer occurs through defined handoff events, not ad-hoc file sharing.

| Repository | Owner | Contents |
|---|---|---|
| `architecture-repository/` | Solution Architect | Architecture Vision, Business Architecture, App/Data Architecture, principles, ADRs |
| `technology-repository/` | Software Architect/PE | Technology Architecture, implementation plans, coding standards, solutions inventory |
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

All Python implementation (`src/`) must follow these conventions. They apply to every file authored in Stage 5 onward and are enforced during code review.

**Type system — expressive and mandatory:**
- Type annotations are **required on all function and method signatures** (parameters and return types). No bare `def f(x)` without annotations.
- **Modern syntax for built-in collection types (PEP 585/604):** Write `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `set[T]`, `type[X]` directly — never the capitalised `typing` aliases `List`, `Dict`, `Tuple`, `Set`, `FrozenSet`, `Type`. Use `X | Y` instead of `Union[X, Y]`, and `X | None` instead of `Optional[X]`.
- **Parametric polymorphism — prefer inline type parameter syntax (PEP 695, Python 3.12+):** Write `def f[T](x: T) -> T` and `class Stack[T]: ...` instead of declaring `T = TypeVar('T')` separately. Bounds and constraints are written inline — `[T: SomeBase]` for an upper bound, `[T: (int, float)]` for constraints. Use `[**P]` for a `ParamSpec` parameter and `[*Ts]` for a `TypeVarTuple`. Explicit `TypeVar` declarations are still required only when variance must be stated explicitly (covariant/contravariant) and cannot be inferred by the type checker — this is an edge case; prefer letting inference handle it. Use the `type` statement (PEP 695) for named type aliases: `type Vector = list[float]` — not `TypeAlias` from `typing`.
- `Protocol` (from `typing`) is still required for structural subtyping — preferred over `ABC` for interface definitions. `overload` (from `typing`) is still required for multi-dispatch signatures. These have no PEP 695 equivalents.
- Use `TypedDict` or Pydantic `BaseModel` for structured data; never `dict[str, Any]` at a boundary.

**Pythonic style — current best practices:**
- Prefer **compositional, functional style** over imperative mutation: use comprehensions, `map`/`filter` where readable, generator expressions, and `functools` where appropriate.
- Use **`dataclasses`** (with `slots=True` where applicable) for lightweight value objects that don't need Pydantic validation.
- Use **`match`/`case`** (structural pattern matching, PEP 634) for multi-branch dispatch on tagged unions or event types — preferred over long `if/elif` chains.
- Use `pathlib.Path` throughout; never `os.path` string concatenation.
- **f-strings** for all string formatting; never `%`-formatting or `.format()`.

**Error handling — monadic, no exceptions for control flow:**
- Use **`Result`-style returns** via a lightweight `Result[T, E]` type (either a project-local definition or `returns` library) for operations that can fail in expected ways. Do not raise exceptions for expected failure paths (missing artifact, validation failure, CQ not found).
- Raise exceptions only for **truly unexpected states** (programming errors, unrecoverable I/O failures). Use `assert` only for internal invariants, never for user-facing validation.
- Avoid bare `except Exception` clauses. If catching broadly, re-raise or log with full context.
- Pydantic `ValidationError` is acceptable at system boundaries (external input validation); never swallow it silently.

**No magic:**
- No monkey-patching, no `__getattr__` tricks, no dynamic `setattr` unless implementing a clearly-bounded, well-documented protocol (e.g., Pydantic internals).
- No `globals()` / `locals()` manipulation.
- Dependency injection over module-level singletons; pass configuration and dependencies explicitly.

**Domain-centred architecture — layered dependency rule:**

The codebase follows a domain-centred layered architecture (hexagonal / ports-and-adapters style). The dependency rule is strict: **outer layers depend inward; the domain depends on nothing outside itself.**

```
┌─────────────────────────────────────────────┐
│  Infrastructure  (src/events/, src/sources/) │  ← depends on Application + Domain + Common
├─────────────────────────────────────────────┤
│  Application     (src/agents/, src/orch.)   │  ← depends on Domain + Common
├─────────────────────────────────────────────┤
│  Domain          (src/models/, src/domain/) │  ← depends on Common only
├─────────────────────────────────────────────┤
│  Common          (src/common/)              │  ← no business or framework dependencies;
│  logging, validation, parsing, normalisation│    usable by all layers
└─────────────────────────────────────────────┘
```

**Cross-cutting concerns** that are genuinely needed at every layer — logging, structured validation helpers, text parsing utilities, normalisation functions — live in `src/common/`. This module has no business-domain knowledge and no infrastructure dependencies; it is pure utility. All layers may import from `src/common/` without violating the dependency rule. What is prohibited is importing *inward* across the business layers (infrastructure importing application logic, application importing infrastructure implementations) or importing framework-specific types into the domain.

- **Domain layer** (`src/models/`, `src/domain/`): Pydantic models, value objects, domain events, aggregate roots, domain services. May import from `src/common/` (e.g., logging, shared validators). No imports from PydanticAI, SQLAlchemy, LangGraph, Anthropic SDK, `pathlib` I/O, or any framework. Domain logic (validation rules, state transitions, constraint checks) lives here and is fully unit-testable without mocking.
- **Application layer** (`src/agents/`, `src/orchestration/`): orchestrates domain objects; invokes infrastructure via **ports** (abstract `Protocol` interfaces defined in the domain or application layer). Depends on the domain; never directly on infrastructure implementations. Agent skill execution, handoff routing, and CQ lifecycle management live here.
- **Infrastructure layer** (`src/events/`, `src/sources/`, future `src/dashboard/`): implements the ports — EventStore (SQLite), source adapters (Confluence, Jira, Git), file-system artifact I/O, plantuml CLI subprocess. Infrastructure knows about domain types (it uses them as data shapes) but domain types never know about infrastructure.

**Ports and adapters pattern for all I/O:**
- Define a `Protocol` (port) in the application or domain layer for every infrastructure capability needed: `ArtifactReader`, `ArtifactWriter`, `EventStore`, `LLMClient`, `SourceAdapter`.
- Concrete implementations (adapters) live in the infrastructure layer and are injected at composition root (startup / agent factory).
- This means the entire application and domain can be tested with in-memory fakes implementing the same protocols — no SQLite, no file system, no LLM API calls required.

**Domain representations are the single source of truth:**
- Pydantic models in `src/models/` are the canonical representation of SDLC artifacts (ArchitectureVision, BusinessArchitecture, LearningEntry, etc.). No parallel dict-based or ORM-mapped representations of the same concepts.
- EventStore events are also Pydantic models; the SQLite schema is derived from them (via Alembic), not defined independently.
- If a framework (PydanticAI, LangGraph) requires its own data shape, adapt at the boundary — wrap or map from the domain model; do not let framework types leak into domain or application code.

- **Runtime:** Python 3.12+ (required for PEP 695 inline type parameter syntax — `def f[T](...)`), Pydantic v2 for all data models, artifact schemas, and event payloads
- **Orchestration:** PydanticAI (primary) — provides agent definition, tool use, and structured output natively; avoids heavy framework lock-in while enabling clean composition
- **LLM backend:** Anthropic Claude API (claude-sonnet-4-6 for primary agents; claude-haiku-4-5 for lightweight routing/summarisation tasks)
- **Workflow graph (if needed for complex multi-agent flows):** LangGraph as an optional layer on top of PydanticAI for stateful multi-step orchestration — to be introduced only when the simpler PydanticAI patterns prove insufficient
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
- [x] `framework/artifact-schemas/diagram-catalog.schema.md` — authored (element records per ontological layer, connections records, diagram index, `_macros.puml` validation rules, `catalog_register()` validation rules, examples)
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

#### 4.8d — Artifact Schema and Framework Doc Updates (Pending — pre-Stage-5)

The domain artifact schemas and cross-cutting framework docs need updating to align with the new ERP design.

- [ ] `framework/artifact-schemas/business-architecture.schema.md` — refactor to ArchiMate-layer entity-type registry; remove `_index.yaml` references; update output paths to `motivation/`, `strategy/`, `business/`
- [ ] `framework/artifact-schemas/application-architecture.schema.md` — refactor; update paths to `application/`
- [ ] `framework/artifact-schemas/data-architecture.schema.md` — refactor; `data-object` entities in `application/data-objects/`; ER connections in `connections/er/`
- [ ] `framework/artifact-schemas/technology-architecture.schema.md` — refactor; paths to `technology/`; connections in `technology-repository/connections/`
- [ ] `framework/repository-conventions.md` — update §2.2 directory layout; add §14 ERP conventions summary
- [ ] `framework/discovery-protocol.md` — update Layer 1 to `list_artifacts` ModelRegistry scan; update diagram discovery to D1–D5 protocol
- [ ] `framework/agent-runtime-spec.md §6` — update all tool specs: `write_artifact` (§content/§display validation, ModelRegistry update, reference resolution for connections); `list_artifacts`/`list_connections` (ModelRegistry queries); `regenerate_macros`; `generate_er_content`; `generate_er_relations`; `validate_diagram` (alias→ModelRegistry check)
- [ ] Retroactive skill file update: skills producing entity artifacts must use new ERP paths and file format. **Script-based** (grep/sed, not parallel agents).

#### 4.8e — CLAUDE.md Authoring Rules (Complete)

- [x] CLAUDE.md updated: ERP authoring rules ERP-1 through ERP-6; stage table updated

#### 4.8f — Reverse Architecture Skills (Complete — 2026-04-03)

> SA and SwA skills for reverse architecture / repository-building engagements (EP-G): Raising a query to the user to provide any textual context, document references, diagrams etc, discovering and structuring the info from the response and its referenced content, scanning existing codebases/systems, and populating the model repository with discovered entities and connections after confirmation, before any diagrams are drawn. This is the primary use case where model-first matters most — the model is built up incrementally from discovered artefacts, and diagrams are produced only after the model achieves sufficient coverage.

- [x] `agents/solution-architect/skills/reverse-architecture-bprelim-a.md` (SA-REV-PRELIM-A) — Phase A and Prelim reverse: discover stakeholders, product-areas / bounded contexts, capabilities, drivers, motivations, constraints, requirements, maturity-levels, meta-information from external sources, user queries, document/diagram references; produce ERP entity files in `motivation/` + `strategy/` directories; generate ArchiMate connections; validate with user max 2 iterations; produce Architecture Vision overview document; raise CQs for gaps.
- [x] `agents/solution-architect/skills/reverse-architecture-ba.md` (SA-REV-BA) — Phase B reverse: discover business entities (actors, roles, processes, functions, services, objects, events) from codebase domain decomposition, ADRs, docs, and user input; produce ERP entity files in `business/` directory; generate ArchiMate connections (assignment, triggering, realization, access); validate with user max 2 iterations; produce BA overview document; flag safety-relevant processes for CSCO.
- [x] `agents/software-architect/skills/reverse-architecture-ta.md` (SWA-REV-TA) — Phase D/E reverse: discover technology layer (nodes, system-software, services, artifacts, networks, interfaces) from IaC, Dockerfiles, CI/CD configs, package manifests; produce ERP entity files in `technology-repository/technology/`; author ADR stubs; generate technology connections; perform Gap & Risk Assessment (lifecycle, security, SIB deviation, ADR coverage); produce TA overview; handoff to SA and CSCO.

---

### Stage 4.9 — ENG-001 Architecture Model (Pending — pre-Stage-5)

> **Primary purpose: the implementation specification for Stage 5.** The SDLC multi-agent system is modelled as a first-class ERP v2.0 architecture engagement. Entity files, connection files, and diagrams produced here are the definitive architectural plans for all Stage 5 `src/` work. Developers implement one APP entity at a time; Pydantic models in `src/models/` are derived from DOB attribute tables; the LangGraph topology follows the activity diagram. When Stage 5 diverges from these artifacts, the artifacts are updated first. Secondary purpose: integration test fixture for Stage 6.
>
> **Model evolution is expected and normal.** The entities, connections, and diagrams in Stage 4.9 are *living* specifications — not a frozen snapshot. Every Stage 5 implementation decision that contradicts, extends, or refines the model (e.g. a new interface discovered, a data object field renamed, a component split into two) must be reflected by updating the relevant entity/connection files *before* changing the code. Requirements and constraints (REQ, CST, PRI) are likewise updated when implementation reveals that a stated requirement or constraint needs revision. Diagrams are regenerated from the updated model after each such update. Connection files are added or removed as actual component relationships are established. This is the model-first discipline applied to forward implementation: the architecture repository always leads the code, not the reverse.

#### 4.9a — ERP Directory Bootstrap

- [ ] Create under `engagements/ENG-001/work-repositories/architecture-repository/`: `motivation/`, `strategy/`, `business/actors/`, `business/processes/`, `business/services/`, `application/components/`, `application/interfaces/`, `application/services/`, `application/data-objects/`, `implementation/`, `connections/archimate/realization/`, `connections/archimate/serving/`, `connections/archimate/assignment/`, `connections/archimate/composition/`, `connections/archimate/access/`, `connections/er/one-to-many/`, `connections/sequence/synchronous/`, `connections/activity/sequence-flow/`, `diagram-catalog/diagrams/`, `diagram-catalog/rendered/`, `decisions/`, `overview/`
- [ ] Create `diagram-catalog/_archimate-stereotypes.puml` stub; `diagram-catalog/diagrams/index.yaml` empty list

#### 4.9b — Motivation and Strategy Entities (Phase A)

- [ ] **Motivation** in `motivation/`:
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

- [ ] **Strategy** in `strategy/`:
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

- [ ] **Actors** in `business/actors/` — `safety-relevant: false` on all; `phase-produced: B`:
  - `ACT-001.md` — `User` — human; initiates phases; answers CQs; uploads files; reviews and approves sprint output
  - `ACT-002.md` — `PM Agent` — VSM System 3; orchestrates all agents; sprint lifecycle; gate coordination; CQ batching; review trigger
  - `ACT-003.md` — `SA Agent` — VSM System 4; phases A/B/C/H + EP-G Prelim/A and BA reconstruction
  - `ACT-004.md` — `SwA Agent` — phases D/E/F/G + EP-G TA reconstruction; technology authority
  - `ACT-005.md` — `DevOps Agent` — phases D/E/F/G; IaC, pipelines, deployments
  - `ACT-006.md` — `DE Agent` — phase G; code delivery; git worktree per sprint
  - `ACT-007.md` — `QA Agent` — phases E/F (test planning) + G (execution); compliance assessment co-production
  - `ACT-008.md` — `PO Agent` — phases Prelim/A/B/H; requirements register; stakeholder communication
  - `ACT-009.md` — `SM Agent` — phase A; market analysis; SWOT; requirements-management feedback
  - `ACT-010.md` — `CSCO Agent` — all phases (gate reviews); safety constraints; STAMP/STPA; incident response
  - `ACT-011.md` — `Architecture Board` — enterprise promotion reviews; enterprise-repository write authority

- [ ] **Processes** in `business/processes/` — each `safety-relevant: false` except BPR-005:
  - `BPR-001.md` — `Sprint Planning` — PM assigns work-packages to agents; emits `sprint.started`
  - `BPR-002.md` — `Skill Execution` — agent invoked with skill; reads artifacts; calls tools; produces output; emits events
  - `BPR-003.md` — `CQ Lifecycle` — agent raises CQ → PM batches → dashboard surfaces → user answers → agent resumes
  - `BPR-004.md` — `Gate Evaluation` — PM collects votes; evaluates checklist; records `gate.evaluated` event
  - `BPR-005.md` — `Algedonic Escalation` — `alg.raised` bypasses topology; reaches escalation target immediately — `safety-relevant: true`
  - `BPR-006.md` — `Sprint Review` — PM emits `review.pending`; dashboard surfaces review; user marks items; PM routes corrections; sprint closes
  - `BPR-007.md` — `Enterprise Promotion` — entity promoted from engagement to enterprise repo; ID reference sweep; Architecture Board review
  - `BPR-008.md` — `Reverse Architecture` — EP-G entry; multi-source scan; entity inference; user confirmation; ERP model population

- [ ] **Services** in `business/services/` — what each role offers to the system, consumed by other actors or processes:
  - `BSV-001.md` — `Architecture Modelling` (SA) — produces AV, BA, AA, DA, Change Records; owns architecture-repository
  - `BSV-002.md` — `Technology Architecture` (SwA) — produces TA, ADRs, Architecture Contract; owns technology-repository
  - `BSV-003.md` — `Project Coordination` (PM) — sprint lifecycle management; gate evaluation; CQ routing; review coordination
  - `BSV-004.md` — `Safety Governance` (CSCO) — gate vote authority on all phases; SCO updates; incident response
  - `BSV-005.md` — `Requirements Management` (PO) — maintains RR; stakeholder communication; phase A/B consulting
  - `BSV-006.md` — `Code Delivery` (DE) — implements work packages; submits PRs; contributes test reports
  - `BSV-007.md` — `Quality Assurance` (QA) — test strategy; test execution; compliance assessment
  - `BSV-008.md` — `Platform Engineering` (DO) — IaC; CI/CD pipelines; environment provisioning; deployment records
  - `BSV-009.md` — `User Decisions` (User) — CQ answers; file uploads; sprint review approvals — the user's contribution as a bounded service consumed by BPR-003 and BPR-006

#### 4.9d — Application Layer Entities (Phase C) — Primary Stage 5 Implementation Specification

Every APP-nnn maps to a distinct `src/` Python module. Every DOB-nnn maps to a Pydantic model (or TypedDict for LangGraph state). These are the binding specifications Stage 5 developers work from.

- [ ] **Components** in `application/components/`:

  *State & Storage (src/events/, src/common/, src/sources/):*
  - `APP-001.md` — `EventStore` — `src/events/event_store.py`; ACID SQLite; two tables: `events` (append-only; never mutated) and `snapshots` (point-in-time `WorkflowState` serialisations); public API: `record_event(event) → None`, `replay() → WorkflowState` (full replay from event 0; used for integrity check and disaster recovery), `replay_from_latest_snapshot() → tuple[WorkflowState, int]` (fast path: deserialises latest snapshot + replays delta events since snapshot; returns `(state, resume_sequence)`), `create_snapshot(trigger: str) → str` (serialises current `WorkflowState` to JSON; inserts into `snapshots` table; returns `snapshot_id`), `check_snapshot_interval() → bool` (returns True if events since last snapshot ≥ `snapshot_interval`, default 100), `check_integrity()`, `query_events(**filter)`; canonical workflow state; never accessed directly via sqlite3
  - `APP-002.md` — `ModelRegistry` — `src/common/model_registry.py`; in-process frontmatter cache; built at startup by scanning all `*.md` ERP files; `list_artifacts(**filter)`, `list_connections(**filter)`, `get_by_id(id)`, `upsert(record)`; thread-safe (RLock); never persisted to disk; rebuilt on cold start
  - `APP-003.md` — `LearningStore` — `src/agents/learning_store.py`; LangGraph `BaseStore` wrapper; `(engagement_id, agent_role, "learnings")` namespace; `query(phase, artifact_type, domain, expand_related) → list[str]`; `record(entry: LearningEntry) → str`; optional sqlite-vec semantic tier; cold-start rebuild from `learnings/index.yaml`

  *Agent Runtime (src/agents/ infrastructure):*
  - `APP-004.md` — `SkillLoader` — `src/agents/skill_loader.py`; parses skill `.md` frontmatter + body; extracts Inputs/Steps/Algedonic/FeedbackLoop/Outputs sections; enforces token budget by `complexity-class` (600/1200/2000); truncation priority order; `load_instructions(skill_id) → str`
  - `APP-005.md` — `AgentFactory` — `src/agents/base.py`; `build_agent(agent_id) → Agent[AgentDeps, str | PMDecision]`; Layer 1 = `system-prompt-identity` (≤150 tok); Layer 2 = `### Runtime Behavioral Stance` (≤350 tok); Layer 3 = `SkillLoader.load_instructions()` via `@agent.instructions`; Layer 4 = tool results at runtime; registers tool sets per agent role
  - `APP-006.md` — `AgentRegistry` — `src/agents/__init__.py`; `AGENT_REGISTRY: dict[str, Agent]` of pre-built instances for all 9 roles; populated at module import; used by LangGraph nodes to invoke agents without re-constructing

  *Agent Instances (src/agents/*.py — one module each):*
  - `APP-007.md` — `PM Agent` — `src/agents/project_manager.py`; `result_type=PMDecision`; `pm_tools` (invoke_specialist, batch_cqs, evaluate_gate, record_decision); all PM skills loadable
  - `APP-008.md` — `SA Agent` — `src/agents/solution_architect.py`; `universal_tools` + `write_tools` (architecture-repository bound) + `target_repo_tools` (read-only); all SA skills including SA-REV-PRELIM-A and SA-REV-BA
  - `APP-009.md` — `SwA Agent` — `src/agents/software_architect.py`; `universal_tools` + `write_tools` (technology-repository bound) + `target_repo_tools` (read-only); all SwA skills including SWA-REV-TA
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
  - `APP-021.md` — `InteractionHandler` — `src/dashboard/interaction.py`; handles POST /queries/<cq_id>/answer, POST /uploads, POST /review/submit; validates inputs; calls `EventStore.record_event()` for all writes; enforces MIME allow-list; path-restricted; never touches work-repositories directly
  - `APP-022.md` — `TargetRepoManager` — `src/sources/target_repo.py`; reads `engagements-config.yaml`; `clone_or_update(repo_id)`; `get_clone_path(repo_id) → Path`; `check_access(repo_id, agent_role)`; `create_worktree(repo_id, branch) → Path`; `get_primary_id()`; backward-compatible with singular `target-repository`

- [ ] **Interfaces** in `application/interfaces/` — ports in the ports-and-adapters model; each is a `typing.Protocol` defined in `src/agents/protocols.py` or `src/sources/base.py`:
  - `AIF-001.md` — `EventStorePort` — `record_event(event: WorkflowEvent) → None`; `replay() → WorkflowState`; `replay_from_latest_snapshot() → tuple[WorkflowState, int]`; `create_snapshot(trigger: str) → str`; `check_snapshot_interval() → bool`; `query_events(**filter) → list[WorkflowEvent]`; implemented by APP-001; injected into all agents via AgentDeps
  - `AIF-002.md` — `LLMClientPort` — `complete(messages, tools, result_type) → Result`; implemented by PydanticAI `Agent` backed by Anthropic API; swappable for test doubles without LLM calls; defined in `src/agents/protocols.py`; this port is what CST-001 (No Framework Lock-In) depends on
  - `AIF-003.md` — `SourceAdapterPort` — `query(query: str) → str`; `source_id: str`; implemented by Confluence, Jira, Git, UserUpload adapters in `src/sources/`; registered in source adapter registry at session startup
  - `AIF-004.md` — `ArtifactReadWriterPort` — `read(id_or_path, mode) → str`; `write(path, content, *, upload_refs: list[str] | None = None) → ArtifactRecord`; `list(**filter) → list[ArtifactRecord]`; path-constrained per agent role; validates ERP frontmatter + §content/§display structure; updates ModelRegistry synchronously on write; **tool-transparent event emission** (no skill instruction required): (1) emits `artifact.created` or `artifact.updated` — auto-detects new vs existing file; (2) auto-extracts `source_evidence` by scanning written content for `[inferred: <source>]` annotation pattern — no agent parameter needed; (3) emits `entity.confirmed` when `active_skill_id` in AgentDeps matches a reverse-arch skill ID (SA-REV-*, SWA-REV-*) — `confirmation_method` derived from whether a user CQ round occurred (EventStore `cq.answered` event exists for this skill invocation); (4) emits `file.referenced` events for each entry in `upload_refs` when provided. All four emissions happen inside the port implementation; agents call `write(path, content)` exactly as before — no new parameters required for the common case.
  - `AIF-005.md` — `DiagramToolsPort` — `regenerate_macros(repo_path)`; `generate_er_content(entity_ids) → str`; `generate_er_relations(connection_ids) → str`; `validate_diagram(puml_path) → list[str]`; `render_diagram(puml_path) → Path`; invokes local `plantuml` CLI
  - `AIF-006.md` — `LearningStorePort` — `query(phase, artifact_type, domain, expand_related) → list[str]`; `record(entry: LearningEntry) → str`; implemented by APP-003 (`LearningStore`); swappable for in-memory fake in tests

- [ ] **Data objects** in `application/data-objects/` — authoritative field-level specification for all Pydantic models and TypedDicts in `src/models/` and `src/orchestration/`:

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

- [ ] **Application services** in `application/services/` — named service groupings that span multiple components; useful for the business diagram and for tracing capability-to-implementation:
  - `ASV-001.md` — `Agent Invocation Service` — APP-005 + APP-004 + APP-006; accepts `(agent_id, skill_id, deps)` → 4-layer prompt assembly → PydanticAI execution → structured result; governed by `framework/agent-runtime-spec.md`
  - `ASV-002.md` — `Artifact I/O Service` — APP-002 + AIF-004; read/write/list on ERP entity files; path constraints enforced; ModelRegistry kept in sync; ERP format validated on every write
  - `ASV-003.md` — `Sprint Review Service` — APP-018 + APP-021 + APP-016 review_processing_node; full lifecycle from `review.pending` → dashboard presentation → user submission → correction routing → `sprint.close`
  - `ASV-004.md` — `CQ Management Service` — APP-007 (PM batching) + APP-018 (event monitoring) + APP-020 (dashboard surfacing) + APP-021 (answer submission); full CQ lifecycle from `cq.raised` → user answer → agent resumption
  - `ASV-005.md` — `Learning Service` — APP-003 + AIF-006; implements `learning-protocol.md §9` full query logic (metadata filter → graph expansion via `related` → optional semantic tier) and `record()` with schema validation, ID assignment, durable file write, and EventStore event

#### 4.9e — Connection Files

Enumerate specific connection files. Each is an `.md` file with frontmatter and brief `§content`. `§display ###archimate` block where applicable.

- [ ] **`connections/archimate/realization/`** (capability/process/service realized by component):
  - `CAP-001---APP-016.md` — LangGraph Orchestrator realises Phase Execution capability
  - `CAP-002---ASV-002.md` — Artifact I/O Service realises Artifact Production capability
  - `CAP-003---ASV-001.md` — Agent Invocation Service realises Multi-Agent Orchestration
  - `CAP-004---ASV-005.md` — Learning Service realises Knowledge Retention
  - `CAP-005---ASV-004.md` — CQ Management Service realises User Interaction (query half)
  - `CAP-005---ASV-003.md` — Sprint Review Service realises User Interaction (review half)
  - `CAP-006---APP-008.md` — SA Agent realises Reverse Architecture (SA-REV-PRELIM-A, SA-REV-BA)
  - `CAP-006---APP-009.md` — SwA Agent realises Reverse Architecture (SWA-REV-TA)
  - `BPR-002---ASV-001.md` — Agent Invocation Service realises Skill Execution process
  - `BPR-003---ASV-004.md` — CQ Management Service realises CQ Lifecycle process
  - `BPR-006---ASV-003.md` — Sprint Review Service realises Sprint Review process
  - `BSV-001---APP-008.md` — SA Agent realises Architecture Modelling service
  - `BSV-002---APP-009.md` — SwA Agent realises Technology Architecture service
  - `BSV-003---APP-007.md` — PM Agent realises Project Coordination service
  - `BSV-009---APP-020.md` — DashboardServer realises User Decisions service

- [ ] **`connections/archimate/serving/`** (component serves another component or actor):
  - `APP-001---APP-016.md` — EventStore serves LangGraph Orchestrator (state reads/writes in all nodes)
  - `APP-001---APP-017.md` — EventStore serves EngagementSession (replay on startup)
  - `APP-001---APP-018.md` — EventStore serves UserInteractionOrchestrator (event monitoring)
  - `APP-001---APP-021.md` — EventStore serves InteractionHandler (writes CQ answers, uploads, reviews)
  - `APP-002---APP-004.md` — ModelRegistry serves SkillLoader (artifact lookup for skill routing)
  - `APP-002---APP-005.md` — ModelRegistry serves AgentFactory (AgentSpec frontmatter load)
  - `APP-003---APP-007.md` — LearningStore serves PM Agent (via `query_learnings` tool)
  - `APP-003---APP-008.md` — LearningStore serves SA Agent
  - `APP-003---APP-009.md` — LearningStore serves SwA Agent
  - `APP-004---APP-007.md` — SkillLoader serves PM Agent (Layer 3 injection)
  - `APP-004---APP-008.md` — SkillLoader serves SA Agent
  - `APP-004---APP-009.md` — SkillLoader serves SwA Agent (and DO, DE, QA, PO, SM, CSCO — four more serving connections; one per remaining agent)
  - `APP-005---APP-006.md` — AgentRegistry serves LangGraph Orchestrator (agent instance lookup in nodes)
  - `APP-016---APP-017.md` — LangGraph Orchestrator serves EngagementSession (graph execution)
  - `APP-020---ACT-001.md` — DashboardServer serves User (all views + interaction endpoints)
  - `APP-022---APP-008.md` — TargetRepoManager serves SA Agent (read-only target-repo access)
  - `APP-022---APP-009.md` — TargetRepoManager serves SwA Agent (read-only; SWA-REV-TA uses scan_target_repo)
  - `APP-022---APP-011.md` — TargetRepoManager serves DE Agent (read-write; git worktree per sprint)

- [ ] **`connections/archimate/assignment/`** (actor assigned to process):
  - `ACT-002---BPR-001.md` — PM assigned to Sprint Planning
  - `ACT-002---BPR-004.md` — PM assigned to Gate Evaluation
  - `ACT-002---BPR-006.md` — PM assigned to Sprint Review
  - `ACT-003---BPR-002.md` — SA assigned to Skill Execution (phases A/B/C/H)
  - `ACT-004---BPR-002.md` — SwA assigned to Skill Execution (phases D/E/F/G)
  - `ACT-001---BPR-003.md` — User assigned to CQ Lifecycle (answer step)
  - `ACT-001---BPR-006.md` — User assigned to Sprint Review (marking step)
  - `ACT-011---BPR-007.md` — Architecture Board assigned to Enterprise Promotion

- [ ] **`connections/archimate/composition/`** (structural containment):
  - `APP-016---APP-007.md` — LangGraph Orchestrator composes PM Agent node
  - `APP-016---APP-008.md` — composes SA Agent node
  - `APP-016---APP-009.md` — composes SwA Agent node
  - `APP-016---APP-018.md` — composes UserInteractionOrchestrator node
  - `APP-006---APP-007.md` — AgentRegistry contains PM Agent instance
  - `APP-006---APP-008.md` — contains SA Agent instance (and one entry per remaining agent)

- [ ] **`connections/archimate/access/`** (component reads/writes data object):
  - `APP-001---DOB-001.md` — EventStore reads/writes WorkflowEvent
  - `APP-001---DOB-009.md` — EventStore produces WorkflowState (via replay)
  - `APP-003---DOB-003.md` — LearningStore reads/writes LearningEntry
  - `APP-016---DOB-012.md` — LangGraph Orchestrator reads/writes SDLCGraphState
  - `APP-017---DOB-002.md` — EngagementSession accesses Engagement (config)
  - `APP-007---DOB-011.md` — PM Agent writes PMDecision
  - `APP-021---DOB-004.md` — InteractionHandler writes ClarificationRequest answers
  - `APP-021---DOB-008.md` — InteractionHandler writes ReviewItems

- [ ] **`connections/er/one-to-many/`** (entity relationships for ER diagram):
  - `DOB-002---DOB-001.md` — Engagement has many WorkflowEvents (`engagement_id` FK)
  - `DOB-009---DOB-001.md` — WorkflowState is derived from many WorkflowEvents
  - `DOB-004---DOB-001.md` — ClarificationRequest produces WorkflowEvents (cq.raised, cq.answered)
  - `DOB-007---DOB-007.md` — GateOutcome contains many GateVotes (self-referential sub-model)
  - `DOB-009---DOB-007.md` — WorkflowState contains many GateOutcomes (one per evaluated gate)
  - `DOB-004---DOB-009.md` — WorkflowState contains many open ClarificationRequests
  - `DOB-006---DOB-009.md` — WorkflowState contains many pending HandoffRecords

#### 4.9f — Diagrams (Phase C outputs — binding implementation views)

Seven diagrams. Each has a stated **implementation purpose** — what Stage 5 decision or module it specifies. Diagrams are prescribed at the level of content and grouping; the SA authors the actual PUML.

- [ ] **`phase-b-archimate-business-v1.puml`**
  *Purpose:* Defines agent role taxonomy and SDLC process model used in all Stage 5 agent module naming and EventStore event routing.
  *Contents:* All ACT-nnn actors (two columns: human actors left, agent actors right); BPR-001 through BPR-008 processes (centre); BSV-001 through BSV-009 services (right column, aligned to their providing actor); assignment connections ACT→BPR; realization connections BSV→BPR; CAP-001 through CAP-006 capabilities shown as an aggregation grouping above the process column.
  *Grouping:* Two swim-lanes — "Human" (ACT-001, ACT-011) and "Agents" (ACT-002 through ACT-010).

- [ ] **`phase-c-archimate-application-v1.puml`**
  *Purpose:* Primary implementation map for Stage 5b — every box is a Python module; every serving connection is a function call boundary.
  *Contents:* All APP-nnn and AIF-nnn entities. Serving, composition, and access connections.
  *Grouping — five ArchiMate grouping rectangles:*
  - **State & Storage** (APP-001 EventStore, APP-002 ModelRegistry, APP-003 LearningStore) — `src/events/ + src/common/`
  - **Agent Runtime** (APP-004 SkillLoader, APP-005 AgentFactory, APP-006 AgentRegistry; AIF-002 LLMClientPort, AIF-004 ArtifactReadWriterPort, AIF-005 DiagramToolsPort) — `src/agents/` infrastructure
  - **Agent Roster** (APP-007 PM through APP-015 CSCO — 9 agents) — `src/agents/*.py`; served by Agent Runtime group
  - **Orchestration** (APP-016 LangGraph, APP-017 Session, APP-018 UIO, APP-019 Promotion; AIF-001 EventStorePort) — `src/orchestration/`
  - **Dashboard & Interaction** (APP-020 DashboardServer, APP-021 InteractionHandler; AIF-003 SourceAdapterPort, APP-022 TargetRepoManager) — `src/dashboard/ + src/sources/`
  *Key connections shown:* State & Storage → Agent Runtime (serving); Agent Runtime → Agent Roster (serving); Orchestration ↔ Agent Roster (composition + serving); Dashboard ↔ Orchestration (via EventStore serving both); External Access → Agent Roster (serving).

- [ ] **`phase-c-class-er-v1.puml`**
  *Purpose:* Pydantic model specification for `src/models/` — field names in this diagram are the authoritative attribute names used in Stage 5 code.
  *Scope:* The eight persisted domain objects that flow through EventStore and define workflow state: DOB-001 (WorkflowEvent), DOB-002 (Engagement), DOB-003 (LearningEntry), DOB-004 (ClarificationRequest), DOB-005 (AlgedonicSignal), DOB-006 (HandoffRecord), DOB-007 (GateOutcome), DOB-008 (ReviewItem). Runtime-only objects (DOB-009 WorkflowState, DOB-010 AgentDeps, DOB-011 PMDecision, DOB-012 SDLCGraphState, DOB-013 ArtifactRecord) are in the model but excluded from this diagram — they have no ER relationships to show.
  *Contents:* Each DOB as a PlantUML class with attribute list (name: type). ER connections with cardinalities per `connections/er/` entries. `DOB-002 Engagement` at top-left as aggregate root; `DOB-001 WorkflowEvent` as the central hub entity.

- [ ] **`phase-b-activity-sprint-v1.puml`**
  *Purpose:* LangGraph graph topology specification for Stage 5c — every decision diamond maps to a routing function; every action box maps to a node implementation.
  *Contents:* Full ADM sprint lifecycle as UML activity diagram. Start fork: entry point selection (EP-0 through EP-H). Main path: Sprint Planning (BPR-001) → Phase Execution (BPR-002, loop per agent per phase) → Gate Evaluation (BPR-004) → decision: gate passed? → next phase or return. Branches: (1) CQ suspension fork from any phase execution node → await `cq.answered` → resume; (2) Algedonic bypass from any node → ALG handler → resolution → resume or halt; (3) Sprint review branch after each sprint close: decision `sprint-review.enabled?` → if true: `review.pending` → await `review.submitted` → corrections loop → sprint close; if false: direct close. End: Engagement Complete.
  *Swim-lanes:* PM (planning/gating/review), Agent (execution), User (CQ answers/review), EventStore (state writes at each transition).

- [ ] **`phase-g-sequence-skill-invocation-v1.puml`**
  *Purpose:* Specifies the Stage 5b core runtime loop — the sequence every Stage 5 developer must internalise before implementing a single agent or node.
  *Contents:* Participants: EngagementSession, LangGraph, pm_node, routing_function, specialist_node, AgentFactory, SkillLoader, PydanticAI_Agent, UniversalTools, EventStore. Sequence: Session invokes graph.stream() → PM node runs (PM Agent via AgentFactory, Layer 1+2 prompt) → PMDecision returned → routing function reads next_action → specialist node selected → specialist_node calls AgentFactory.build_agent() → build_agent calls SkillLoader.load_instructions(skill_id) (Layer 3) → PydanticAI.run_sync(deps) → agent calls tool (e.g. read_artifact via AIF-004, query_learnings via AIF-006) → agent calls write_artifact → ModelRegistry.upsert() + file written → agent calls EventStore.record_event(artifact.created) → agent returns → specialist_node emits handoff.created if needed → returns to LangGraph → next iteration.
  *Note at bottom:* "Layer 4 = tool results appended to context by PydanticAI between tool calls — not shown separately."

- [ ] **`phase-c-sequence-cq-lifecycle-v1.puml`**
  *Purpose:* Specifies `src/orchestration/user_interaction.py` and Dashboard `/queries` interaction for Stage 5b + 5.5b.
  *Participants:* Agent (any specialist), EventStore, UserInteractionOrchestrator, DashboardServer, User.
  *Sequence:* Agent raises CQ → `EventStore.record_event(cq.raised)` → PM batches open CQs → UserInteractionOrchestrator detects `cq.raised` → DashboardServer serves `/queries` page (open CQs visible with count badge) → User types answer + optional file attach → POST /queries/<id>/answer → InteractionHandler validates → `EventStore.record_event(cq.answered)` → UserInteractionOrchestrator detects `cq.answered` → emits `cq.routed` to raising agent's node → agent resumes with answer in context.

- [ ] **`phase-c-sequence-sprint-review-v1.puml`**
  *Purpose:* Specifies Stage 5.5b `ReviewManager`, `sprint_close_node`, and `review_processing_node` for Stage 5c + 5.5b.
  *Participants:* PM_node, EventStore, UserInteractionOrchestrator, DashboardServer, User, review_processing_node.
  *Sequence:* PM node decides close_sprint → checks `sprint-review.enabled` → `EventStore.record_event(review.pending)` (sprint NOT closed yet) → DashboardServer surfaces `/review` with artifact list → User marks each item (approved/needs-revision/rejected + agent_tag + comment) → POST /review/submit → InteractionHandler validates all items decided → `EventStore.record_event(review.submitted)` → UserInteractionOrchestrator signals `review_processing_node` → review_processing_node processes: rejected items → `artifact.rejected` events; needs-revision items → `handoff.created` to tagged agent (or PM routes if no tag); approved items → proceed → `review.sprint-closed` → `sprint.close`.

- [ ] **`diagrams/index.yaml`** — entry per diagram; `entry_type: local`; `entity_ids_used` and `connection_ids_used` lists populated from above

#### 4.9g — Overview Documents and Decisions

- [ ] `overview/architecture-vision.md` — AV for ENG-001: engagement context (modelling the SDLC system itself); capability clusters (CAP-001 through CAP-006); STK-001 and STK-002; safety classification: Safety-Neutral (no physical actuation, no regulated user data, no financial transactions)
- [ ] `overview/aa-overview.md` — Application Architecture summary: lists all APP-nnn with `src/` path and one-line function; states the four-layer dependency rule (Common → Domain → Application → Infrastructure); lists all DOB-nnn Pydantic models with their `src/models/` path; lists all AIF-nnn ports with their `Protocol` location
- [ ] `decisions/ADR-001.md` — `PydanticAI for agent definition` — context: evaluated LangChain, Autogen, raw API; decision: PydanticAI; rationale: structured output via `result_type`, native tool use, minimal magic, first-class Anthropic support; consequences: tighter Pydantic v2 dependency, simpler than alternatives
- [ ] `decisions/ADR-002.md` — `LangGraph for orchestration graph` — context: PM-as-supervisor pattern requires stateful multi-step routing with conditional branches and interrupt support; decision: LangGraph; rationale: built-in state persistence, interrupt/resume for CQ handling, conditional edge routing, compatible with PydanticAI; consequences: LangGraph version pinning, graph must be rebuilt if topology changes
- [ ] `decisions/ADR-003.md` — `SQLite EventStore as canonical state` — context: need durable, auditable, ACID workflow state; decision: SQLite via EventStore class; rationale: local-only (CST-002), git-trackable binary, zero-infrastructure, ACID guarantees, replay from scratch gives WorkflowState; consequences: single-process only (no concurrent writer), binary in git (acceptable at engagement scale)
- [ ] `decisions/ADR-004.md` — `FastAPI + Jinja2 + SSE for dashboard` — context: user interaction surface needed; decision: FastAPI server-side rendering; rationale: no build step, no frontend framework, works with Python-only stack, SSE is standard HTTP (no WebSocket needed for change notifications), POST forms sufficient for CQ/review interaction; consequences: minimal JS budget (two blocks only)
- [ ] `decisions/ADR-005.md` — `File-based ERP entity storage` — context: need to store architecture model; decision: one `.md` file per entity, organised by ArchiMate layer; rationale: git-native diff and blame, human-readable, no DB schema migration for model changes, ModelRegistry is ephemeral (rebuilt at startup); consequences: startup scan time proportional to entity count; mitigated by watchdog incremental updates

#### 4.9h — Event-Sourcing of Repository Mutations and User Inputs

**Every mutation to an engagement work-repository and every user-contributed input must produce an EventStore event.** This is the event-sourcing invariant: the engagement event-stream is the authoritative record of *what happened and when*, while the file system is the *current state projection* of that stream. Events reference file paths; files hold content. On replay, the system reconstructs full workflow state including which entities were inferred from which evidence, which files were uploaded by the user, and which entities the user confirmed.

**All events in this taxonomy are emitted by tool implementations, not by skill instructions — no agent or skill file changes are required.** `ArtifactReadWriterPort.write()`, `scan_target_repo()`, and `InteractionHandler` each emit their respective events autonomously using context from `AgentDeps` (`active_skill_id`, `event_store`). Skill files call the same tool signatures they always have.

The following events govern reverse-architecture and user-input persistence. They must be added to `src/events/models.py` in Stage 5a alongside the existing base event types:

| Event type | Emitted by (tool layer) | Key payload fields | Purpose |
|---|---|---|---|
| `artifact.created` | `ArtifactReadWriterPort.write()` — new file | `path`, `artifact_id`, `version`, `produced_by_skill`, `source_evidence: list[str]` | Creation of any ERP entity/connection/diagram file. `source_evidence` **auto-extracted** from `[inferred: <source>]` annotations in written content — no agent parameter needed. |
| `artifact.updated` | `ArtifactReadWriterPort.write()` — existing file | `path`, `artifact_id`, `version`, `previous_version`, `produced_by_skill`, `changed_fields: list[str]` | Every version increment. `changed_fields` derived by diffing new frontmatter against previous file on disk. |
| `source.scanned` | `scan_target_repo()` tool, end of scan | `scan_scope: list[str]`, `target_repo_id: str \| None`, `external_source_ids: list[str]`, `triggered_by_skill: str`, `file_count: int` | Audit record of EP-G discovery scan. Emitted by the tool; skill files call `scan_target_repo()` as before. |
| `entity.confirmed` | `ArtifactReadWriterPort.write()` when `active_skill_id` ∈ `{SA-REV-*, SWA-REV-*}` | `artifact_id`, `confirmation_method: "user" \| "auto"` | Post-confirmation entity write in a reverse-arch context. `confirmation_method` = `"user"` if a `cq.answered` event exists for this skill invocation; `"auto"` otherwise. Minimal payload — fully derivable from tool context. |
| `upload.registered` | `InteractionHandler` POST /uploads | `upload_id`, `file_path: str`, `mime_type: str`, `original_filename: str`, `referenced_by_cq: str \| None` | User file upload. File content at `engagements/<id>/user-uploads/<upload_id>/`; event is the reference. |
| `file.referenced` | `ArtifactReadWriterPort.write()` when `upload_refs` kwarg provided | `upload_id`, `artifact_id` | Links uploaded file to entity. Agent passes `upload_refs=[...]` explicitly when a CQ answer cited a file — the one optional kwarg on `write()`; omitted in all non-upload contexts. |

**`source_evidence` auto-extraction:** The port implementation scans the `§content` block of every written entity file for the `[inferred: <source>]` annotation pattern already mandated by the reverse-arch skill steps. No new skill instruction is needed — the annotation is already there per existing requirements; the tool harvests it.

**Model-update contract (Stage 5 forward):** Every Stage 5 implementation change that updates an entity or connection file emits `artifact.updated` with `changed_fields` derived by diff. Diagrams regenerated as a consequence emit `artifact.updated` with `changed_fields: ["§display"]`. Happens inside `write_artifact`; no new developer action required.

**Contingency — if future skill additions become necessary (Stage 4.8g):** The three reverse-arch skills are `complexity-class: complex` (2000-token soft budget). Any additions to Steps 3 or 4 (e.g. explicit `upload_refs` guidance) are estimated at ≤60 tokens per skill. Truncation priority (`Algedonic Triggers → Feedback Loop → Outputs`; Steps never truncated) provides ~400 tokens of headroom before content loss. All such changes are designed in Stage 4.8g before execution — see below.

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
  | `artifact.created` | `ArtifactReadWriterPort.write()` — new file | append to `baselined_artifacts` |
  | `artifact.updated` | `ArtifactReadWriterPort.write()` — existing file | update version in `baselined_artifacts` |
  | `source.scanned` | Reverse-arch skill Step 0 | no state change; audit only |
  | `entity.confirmed` | Reverse-arch skill Step 3 | flag entity as user-confirmed in artifact metadata |
  | `upload.registered` | `InteractionHandler` POST /uploads | append to `registered_uploads: list[str]` |
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

- [ ] **`src/common/model_registry.py`**: `ModelRegistry` — `dict[Path, dict]` built at startup by scanning all `.md` entity/connection files for YAML frontmatter; `watchdog` filesystem listener keeps it fresh; used by all `list_artifacts`/`list_connections` calls; `write_artifact` updates it synchronously on write; thread-safe (read-heavy, write-rare — `threading.RLock`); never persisted
- [ ] **`src/agents/deps.py`**: `AgentDeps` dataclass (engagement_id, event_store, active_skill_id, workflow_state, engagement_base_path, framework_path)
- [ ] **`src/agents/base.py`**: `build_agent(agent_id)` factory — layered system prompt assembly:
  - Layer 1: `AgentSpec.load(agent_id)` parses YAML frontmatter, extracts `system-prompt-identity` verbatim (hard cap ≤150 tokens; raises `AgentSpecError` if exceeded)
  - Layer 2: `AgentSpec.load_personality(agent_id)` extracts `### Runtime Behavioral Stance` subsection from §11 only (hard cap ≤350 tokens; full §11 is **not** loaded at runtime — the rest of §11 is authoring documentation, not a runtime injection target)
  - Layer 3: active skill via `@agent.instructions` calling `SkillLoader.load_instructions(ctx.deps.active_skill_id)`
- [ ] **`src/agents/skill_loader.py`**: `SkillLoader.load_instructions(skill_id)` — parses skill Markdown file, extracts included sections (Inputs Required, Steps, Algedonic Triggers, Feedback Loop, Outputs); excludes Knowledge Adequacy Check; reads `complexity-class` from frontmatter to select token threshold (simple ≤600, standard ≤1200, complex ≤2000); counts tokens via `tiktoken`; truncation priority if soft cap exceeded: Algedonic Triggers → compact ALG-IDs only; Feedback Loop → termination conditions + iteration count only; Outputs → artifact paths only; **Steps are never truncated**; raises `SkillBudgetExceededError` only above hard cap (complex=2000, standard=1440, simple=720 — 20% over soft cap; indicates a skill that needs splitting, not compressing)
- [ ] **`src/agents/tools/`**: tool implementations (all tools described in `framework/agent-runtime-spec.md §6`):
  - `universal_tools.py` — `read_artifact(id_or_path, mode)` (resolves artifact-id → path via ModelRegistry; modes: `summary`=frontmatter+first two §content sections, `full`=entire file); `list_artifacts(directory, **filter)` (queries ModelRegistry; returns metadata list without loading bodies; filters: artifact-type, status, domain, safety-relevant, phase-produced); `list_connections(source, target, artifact_type)` (ModelRegistry query scoped to `connections/`; all params optional); `query_event_store`, `emit_event`, `raise_cq`, `raise_algedonic`, `read_framework_doc`, `discover_standards` (reads `technology-repository/coding-standards/` and `enterprise-repository/standards/`; SA/SwA/DE/DO only), `list_target_repositories()` (reads `engagements-config.yaml`; returns all registered repos with id/label/role/domain/primary/clone-path; available to all agents), `query_learnings(phase, artifact_type, domain, expand_related=True)` (per `framework/learning-protocol.md §9` + §12.1–12.2), `record_learning(entry: LearningEntry)` (per §9 + §12.1)
  - `write_tools.py` — per-agent path-constrained write tools (RepositoryBoundaryError on violation → ALG-007)
  - `target_repo_tools.py` — **multi-repo aware**: `read_target_repo(path, repo_id=None)` (repo_id=None → primary repo; raises TargetRepoNotFoundError if id not registered); `write_target_repo(path, content, repo_id=None)` (DE and DO only, per their respective access grants); `execute_pipeline(repo_id=None)` (DO only); `scan_target_repo(repo_id=None)` (Discovery Layer 4 single-repo scan — called once per repo by Layer 4 procedure); `list_target_repos()` (alias for `list_target_repositories()` — convenience import in this module). **Backward compatibility:** when `target-repository` (singular) is configured, `repo_id=None` and `repo_id="default"` both refer to it.
  - `pm_tools.py` — PM decision events (all emitted inside the tool call, before returning to the agent): `invoke_specialist(agent_id, skill_id, task)` → emits `specialist.invoked`; `evaluate_gate(gate_id, votes)` → emits `gate.evaluated` + `create_snapshot("gate.evaluated")` on pass; `batch_cqs(cq_ids)` → emits `cq.batched`; `record_decision(rationale)` → emits `decision.recorded`; `trigger_review()` → emits `review.pending`
  - `diagram_tools.py` — Model-driven diagram production per `framework/diagram-conventions.md §5` (D1–D5 protocol): `regenerate_macros(repo_path)` (scans all entity `§display ###archimate` blocks via ModelRegistry; rewrites `_macros.puml`; called automatically by `write_artifact` when an entity's archimate display spec changes — ALG-C04 if count drift detected); `generate_er_content(entity_ids)` (reads each DOB entity's `§display ###er` block; returns PUML class declarations with attribute lists for direct paste into ER diagram); `generate_er_relations(connection_ids)` (reads each er-connection's `§display ###er` block; returns cardinality lines); `validate_diagram(puml_file_path)` (extracts all PUML aliases; checks each against ModelRegistry; verifies each resolved entity has the appropriate `§display ###<language>` section; confirms `!include _macros.puml` present for ArchiMate/use-case diagrams; returns list of validation errors; ALG-C03 on alias with no backing entity — model must be extended, alias must not be removed); `render_diagram(puml_file_path)` (invokes local `plantuml` CLI; writes SVG to `rendered/`; sprint-boundary render only unless on-demand requested by PM). Non-SA agents call `diagram.display-spec-request` handoff when a needed `§display ###<language>` subsection is missing from an entity. **Agents author PUML source text directly via `write_artifact`, following templates from `framework/diagram-conventions.md §7`.**
- [ ] **`src/agents/learning_store.py`**: `LearningStore` wrapper around LangGraph `BaseStore` (per `framework/learning-protocol.md §12.1`); implements `query()` and `record()` with graph-expansion and optional semantic tier; handles store rebuild from files on startup
- [ ] **`src/agents/project_manager.py`**: PM agent with `result_type=PMDecision`; all PM skills loaded via SkillLoader
- [ ] **`src/agents/solution_architect.py`**: SA agent; Discovery Scan tool registered; all SA skills loadable
- [ ] **`src/agents/software_architect.py`**: SwA agent; Reverse Architecture Reconstruction support for EP-G
- [ ] **`src/agents/devops_platform.py`**: DO agent; pipeline execution tools
- [ ] **`src/agents/implementing_developer.py`**: DE agent; target-repo write tools
- [ ] **`src/agents/qa_engineer.py`**: QA agent; Compliance Assessment co-production tools
- [ ] **`src/agents/__init__.py`**: `AGENT_REGISTRY: dict[str, Agent]` — pre-built agent instances for all roles

#### 5c — Orchestration layer

> Governed by `framework/orchestration-topology.md`. LangGraph graph with PM supervisor + specialist nodes.

- [ ] **`src/orchestration/graph_state.py`**: `SDLCGraphState` TypedDict — as specified in orchestration-topology.md §3, extended with: `target_repository_ids: list[str]` (all registered repo IDs for this engagement; populated at `EngagementSession` startup from `engagements-config.yaml`); `primary_repository_id: str | None` (id of the primary repo, or None for single-repo backward compat)
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

**File upload detail (`/uploads` and `/queries` attach):**

- Files stored at `engagements/<id>/user-uploads/<upload_id>-<sanitised-filename>`. `upload_id` is UUID4.
- No executable files accepted (MIME-type allow-list: PDF, images, Office docs, Markdown, plain text, JSON, YAML, XML, CSV).
- Max file size: 50 MB (configurable in `engagements-config.yaml` under `uploads.max-file-size-mb`).
- `UserUploadAdapter` (Stage 5d addition): implements `SourceAdapter` protocol; `query()` returns upload metadata list; agents call `read_artifact(upload_id)` to retrieve content as text (PDF → extracted text via `pdfminer`; images → path reference; others → decoded text).
- Upload manifest: `engagements/<id>/user-uploads/manifest.yaml` (git-tracked); one entry per upload with id, filename, content-type, sha256, uploaded-at, referenced-by.

**Implementation tasks (5.5b):**

- [ ] `src/dashboard/interaction.py` — `InteractionHandler`: validates and writes CQ answers, uploads, review submissions to EventStore; enforces content rules (non-empty answers, MIME allow-list for uploads); path-restricted writes
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

### Stage 4.8g — Skill/Agent Alignment Audit (Pending — pre-Stage-5)

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

- [ ] Read and audit 3 reverse-arch skill files (Step 0, 3, 4 focus)
- [ ] Grep all skill files for `write_artifact`; check for conflicting instructions
- [ ] Verify Step 0 wording across at least a representative sample of Stage 3 skills
- [ ] Read `framework/agent-runtime-spec.md §6` tool set spec
- [ ] Read `framework/discovery-protocol.md §2` and §4 (Layer 4 target-repo scan)
- [ ] Execute any confirmed changes; update IMPLEMENTATION_PLAN.md findings table when done
- [ ] Commit as part of `stage-4-pre5-alignment`

---

## Current State & Immediate Next Actions

**Stages 1–4.8f complete.** Remaining pre-Stage-5 work: Stage 4.8d (schema/framework ERP alignment), Stage 4.8g (skill/agent alignment audit), Stage 4.9 (ENG-001 reference model). Stage 5 is the main target.

### Resume at: Stage 4.8d → Stage 4.8g → Stage 4.9 → Stage 5

**Stage 4.8d** — ERP v2.0 alignment for domain artifact schemas and framework cross-cutting docs. Updates four artifact schemas (BA, AA, DA, TA) and three framework docs (repository-conventions.md, discovery-protocol.md, agent-runtime-spec.md §6). Retroactive skill file patches are script-based.

**Stage 4.9** — ENG-001 reference model: entity files, connection files, `_macros.puml`, four PUML diagrams, `diagrams/index.yaml`. Documents the SDLC system itself. Serves as integration test fixture.

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
- **Diagram authoring:** agents write PUML source text directly via `write_artifact` — no intermediate spec format. Tools handle catalog I/O (`catalog_lookup`, `catalog_register`, `catalog_propose`, `validate_diagram`, `render_diagram`) and CLI invocation only. See `framework/diagram-conventions.md §1`.
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

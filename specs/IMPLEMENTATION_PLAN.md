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
- **Target project repository:** Per-engagement pointer to the software project being built; separate git repo; configured in `engagements-config.yaml`; local clone at `engagements/<id>/target-repo/` (.gitignored); delivery-repository/ holds metadata only, not code

---

## Implementation Stages

### Stage 1 — Foundation Artifacts (Complete)
> Everything else references these. Complete before authoring any agent or skill files.

- [x] **Scaffold repository directory structure**
  - `enterprise-repository/` (embedded mode, configurable via `enterprise-repository-config.yaml`)
  - `engagements/<id>/` per-engagement directories with work-repositories, event log, and log subdirectories
  - `engagements/<id>/target-repo/` entry in `.gitignore` (local clone of target project; separate repo)
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
- [x] Create `.gitignore` (excludes `target-repo/`, SQLite WAL/journal temporaries, credentials, Python artifacts; `workflow.db` is NOT excluded — it is git-tracked as the canonical event store)
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

**Stage 4 review findings (2026-04-03):**
- Fixed YAML frontmatter bug in all 4 pre-existing gate skills (gate-a through gate-d): `complexity-class:` field was incorrectly placed inside the `primary-outputs:` list block
- Upgraded all 4 gate skill `complexity-class` values from `simple` to `standard` (gate-a has 9 steps + full STAMP Level 1 analysis — well above 600-token simple budget)
- Updated `framework/agent-index.md` v1.0.0 → v1.1.0: added PO, SM, CSCO skill routing tables; removed Stage 4 "pending" annotations from Agent Routing Table

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

#### 4.6c — Python Tooling (deferred to Stage 5b)

Implemented alongside other `universal_tools.py` additions in Stage 5b:

- [ ] `src/tools/universal_tools.py` — add `query_learnings()` and `record_learning()` (spec below; see also Stage 5b tool list)
- [ ] `src/models/learning.py` — `LearningEntry` Pydantic model (fields: `learning_id`, `agent`, `phase`, `artifact_type`, `trigger_event`, `error_type`, `importance`, `applicability`, `generated_at_phase`, `generated_at_sprint`, `generated_at_engagement`, `promoted`, `synthesis_superseded`, `synthesised_from`, `trigger_text`, `correction_text`, `context_text`)
- [ ] EventStore event models — add `learning.created`, `learning.synthesised`, `learning.promoted` to `src/events/`

**`query_learnings` spec:** reads `agents/<agent>/learnings/index.yaml`; filters by phase + artifact_type + applicability; skips `synthesis-superseded` entries; sorts S1 → S2 → S3; returns top 5 `## Correction` texts.

**`record_learning` spec:** validates entry against schema (9 rules); assigns next `<ROLE>-L-NNN` id; writes `agents/<agent>/learnings/<ROLE>-L-NNN.md`; appends `index.yaml`; emits `learning.created` EventStore event; raises `LearningSchemaError` on validation failure.

---

### Stage 5 — Python Implementation Layer

> Implements the specs defined in `framework/agent-runtime-spec.md` and `framework/orchestration-topology.md`. **Read those documents before authoring any src/ file.** Architecture: LangGraph outer loop (ADM phase workflow) + PydanticAI inner loop (per-agent invocations) + EventStore (canonical state persistence).

#### 5a — EventStore completion

- [ ] **`src/events/replay.py`**: implement full state machine — process each event type → update `WorkflowState`; handle all 10+ event types (phase, cycle, gate, sprint, artifact, handoff, cq, algedonic, source)
- [ ] **`src/events/export.py`**: implement `write_event_yaml()` with full PyYAML serialisation; implement `import_from_yaml()` for disaster recovery round-trip
- [ ] **`src/events/migrations/`**: Alembic migration baseline — `alembic.ini` and initial migration script for the events + snapshots tables
- [ ] **`EventStore.check_integrity()`**: validate JSON payloads, sequence gaps, YAML vs SQLite consistency check

#### 5b — Agent implementation layer

> Governed by `framework/agent-runtime-spec.md`. Each agent is a PydanticAI `Agent[AgentDeps, str | PMDecision]` built via `build_agent()`.

- [ ] **`src/agents/deps.py`**: `AgentDeps` dataclass (engagement_id, event_store, active_skill_id, workflow_state, engagement_base_path, framework_path)
- [ ] **`src/agents/base.py`**: `build_agent(agent_id)` factory — layered system prompt assembly:
  - Layer 1: `AgentSpec.load(agent_id)` parses YAML frontmatter, extracts `system-prompt-identity` verbatim (hard cap ≤150 tokens; raises `AgentSpecError` if exceeded)
  - Layer 2: `AgentSpec.load_personality(agent_id)` extracts `### Runtime Behavioral Stance` subsection from §11 only (hard cap ≤350 tokens; full §11 is **not** loaded at runtime — the rest of §11 is authoring documentation, not a runtime injection target)
  - Layer 3: active skill via `@agent.instructions` calling `SkillLoader.load_instructions(ctx.deps.active_skill_id)`
- [ ] **`src/agents/skill_loader.py`**: `SkillLoader.load_instructions(skill_id)` — parses skill Markdown file, extracts included sections (Inputs Required, Steps, Algedonic Triggers, Feedback Loop, Outputs); excludes Knowledge Adequacy Check; reads `complexity-class` from frontmatter to select token threshold (simple ≤600, standard ≤1200, complex ≤2000); counts tokens via `tiktoken`; truncation priority if soft cap exceeded: Algedonic Triggers → compact ALG-IDs only; Feedback Loop → termination conditions + iteration count only; Outputs → artifact paths only; **Steps are never truncated**; raises `SkillBudgetExceededError` only above hard cap (complex=2000, standard=1440, simple=720 — 20% over soft cap; indicates a skill that needs splitting, not compressing)
- [ ] **`src/agents/tools/`**: tool implementations (all tools described in `framework/agent-runtime-spec.md §6`):
  - `universal_tools.py` — read_artifact, query_event_store, emit_event, raise_cq, raise_algedonic, read_framework_doc, discover_standards (reads `technology-repository/coding-standards/` and `enterprise-repository/standards/`; SA/SwA/DE/DO only)
  - `write_tools.py` — per-agent path-constrained write tools (RepositoryBoundaryError on violation → ALG-007)
  - `target_repo_tools.py` — read_target_repo (DE, DO, SwA EP-G), write_target_repo (DE), execute_pipeline (DO)
  - `pm_tools.py` — invoke_specialist (agent-as-tool pattern), batch_cqs, evaluate_gate, record_decision
  - `diagram_tools.py` — `catalog_lookup(query, ontological_layer)` (semantic search across `elements/<layer>/`; returns matching element IDs + names); `catalog_propose(element_spec)` (submits new element via `diagram.catalog-proposal` handoff; non-SA only); `catalog_register(element_spec)` (SA only; writes to correct sub-catalog YAML; regenerates `_macros.puml`; validates no duplicate IDs); `validate_diagram(puml_file_path)` (post-authoring validation: reads .puml file, extracts all element aliases, checks each against catalog YAML sub-catalogs; verifies `!include _macros.puml` is present; returns list of validation errors — missing catalog IDs, broken cross-references, missing required header; SA calls before rendering); `render_diagram(puml_file_path)` (invokes local `plantuml` CLI; on success writes SVG to `rendered/` and returns SVG path; on failure returns error output for agent to diagnose; sprint-boundary render only unless on-demand render is requested by PM). **Note: agents author PUML source text directly using `write_artifact` — no intermediate spec format is generated by a tool. The LLM follows per-diagram-type templates from `framework/diagram-conventions.md §7` (PUML syntax conventions). Text generation is the model's task; tools handle catalog I/O and CLI invocation only.**
- [ ] **`src/agents/project_manager.py`**: PM agent with `result_type=PMDecision`; all PM skills loaded via SkillLoader
- [ ] **`src/agents/solution_architect.py`**: SA agent; Discovery Scan tool registered; all SA skills loadable
- [ ] **`src/agents/software_architect.py`**: SwA agent; Reverse Architecture Reconstruction support for EP-G
- [ ] **`src/agents/devops_platform.py`**: DO agent; pipeline execution tools
- [ ] **`src/agents/implementing_developer.py`**: DE agent; target-repo write tools
- [ ] **`src/agents/qa_engineer.py`**: QA agent; Compliance Assessment co-production tools
- [ ] **`src/agents/__init__.py`**: `AGENT_REGISTRY: dict[str, Agent]` — pre-built agent instances for all roles

#### 5c — Orchestration layer

> Governed by `framework/orchestration-topology.md`. LangGraph graph with PM supervisor + specialist nodes.

- [ ] **`src/orchestration/graph_state.py`**: `SDLCGraphState` TypedDict — exactly as specified in orchestration-topology.md §3
- [ ] **`src/orchestration/pm_decision.py`**: `PMDecision` Pydantic model — PM's structured output (next_action, specialist_id, skill_id, task_description, reasoning, gate_id)
- [ ] **`src/orchestration/routing.py`**: all routing functions — `route_from_pm`, `route_after_specialist`, `route_after_gate`, `route_after_cq`, `route_after_algedonic`, `route_after_sprint_close`; algedonic bypass check in every routing function
- [ ] **`src/orchestration/nodes.py`**: all node implementations — `pm_node` (PM deliberative reasoning); `sa_node`, `swa_node`, `do_node`, `de_node`, `qa_node` (each calls `invoke_specialist` via PM tools); `gate_check_node`, `cq_user_node`, `algedonic_handler_node`, `sprint_close_node`, `engagement_complete_node`
- [ ] **`src/orchestration/graph.py`**: `build_sdlc_graph()` — exactly as specified in orchestration-topology.md §4.3
- [ ] **`src/orchestration/session.py`**: `EngagementSession` — top-level entry point; loads engagements-config.yaml; reconstructs `SDLCGraphState` from EventStore on startup; resumes graph execution; handles CQ user interaction loop
- [ ] **`src/orchestration/promotion.py`**: Enterprise Promotion workflow — implements `repository-conventions.md §12`
- [ ] **`src/orchestration/user_interaction.py`**: CQ surface and answer ingestion — batches CQs, presents to user, routes answers back to raising agents via EventStore `cq.answered` events

#### 5d — Source adapters

- [ ] **`src/sources/base.py`**: adapter base class — `SourceAdapter.query(query: str) → str`; all queries emit `source.queried` EventStore event; adapter is read-only
- [ ] **`src/sources/confluence.py`**, **`src/sources/jira.py`**, **`src/sources/git_source.py`**: external source implementations; wired to `external-sources/<id>.config.yaml`
- [ ] **`src/sources/target_repo.py`**: local clone manager for target project repository; read path for all agents; write path for DE only; never commits framework files into target repo

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

### Stage 5.5 — Engagement Dashboard (Local Web Server)

> Lightweight local web server providing users with a readable, explorable view of engagement state, SDLC progress, produced artifacts, and agent activity. Runs alongside the Python multi-agent system; reads EventStore and work-repositories; no write access.

**Requirement:** Users need to efficiently and intelligibly view and explore: what has been produced, where the project is in the SDLC, what is available to review, and the current state of all artifacts and agent activity.

**Architecture:**

- **Server:** Python `FastAPI` (already in the Python ecosystem; zero additional dependencies beyond what Stage 5 introduces). Single file: `src/dashboard/server.py`. Started with `python -m src.dashboard.server --engagement <id>`.
- **Data sources (read-only):**
  - `engagements/<id>/workflow.db` — EventStore (via `EventStore.replay()` to get `WorkflowState`)
  - `engagements/<id>/work-repositories/*/` — markdown artifact files
  - `engagements/<id>/clarification-log/`, `handoff-log/`, `algedonic-log/`
  - `framework/agent-index.md` — for agent/skill display metadata
- **Rendering:** Server-side HTML with Jinja2 templates; no JavaScript framework required. Markdown rendered to HTML via `markdown-it-py` (lightweight, no build step).
- **No auth:** Local-only server (`127.0.0.1`); not exposed to network. No authentication needed.

**Views:**

| View | URL | Content |
|---|---|---|
| Engagement Overview | `/` | Engagement ID, entry point, current phase, sprint number, gate status summary |
| SDLC Progress | `/progress` | ADM phase timeline; completed/active/pending phases with gate outcomes; current sprint plan |
| Artifact Browser | `/artifacts` | Tree view by work-repository; each artifact shows: status (draft/baselined), version, agent owner, last updated; click to view rendered markdown |
| Artifact Detail | `/artifacts/<path>` | Full rendered markdown content of any artifact; shows frontmatter metadata, version history links |
| Event Log | `/events` | Chronological event stream from EventStore (paginated); filter by event type, agent, phase |
| CQ Log | `/cqs` | Open and resolved Clarification Requests; shows routing target, blocking status, answer |
| Algedonic Log | `/algedonic` | Algedonic signals: trigger ID, severity, status (active/resolved), escalation target |
| Handoff Log | `/handoffs` | Inter-agent handoffs: from, to, artifact, version, acknowledged status |
| Agent Status | `/agents` | Per-agent status: active phase, last event, open CQs, pending handoffs |

**Extended architecture (additions beyond original spec):**

- **PUML rendering:** Local PlantUML CLI integration. `src/dashboard/puml_renderer.py` detects a local `plantuml` executable (JAR or system install); if found, renders `.puml` to `.svg` on-demand and caches in `src/dashboard/render_cache/` (.gitignored); if not found, displays the PUML source in a `<code>` block with an installation notice. No external network calls to plantuml.com.
- **Static file and document display:** `src/dashboard/file_server.py` serves `.svg` and `.png` files inline (via `<img>` tag); `.pdf` files as browser-native embed or download link; `.docx`/`.xlsx` as download links with file metadata. Images from `diagram-catalog/rendered/` are served directly.
- **Filesystem monitoring + change alerts:** `src/dashboard/watcher.py` uses `watchdog` to monitor `engagements/<id>/work-repositories/` for file creation/modification events. Changed file events are pushed via Server-Sent Events (SSE) on `/events/stream`. A minimal `<script>` block in `base.html` (the only JavaScript in the entire dashboard) listens on the SSE endpoint and displays a non-intrusive "N artifact(s) updated — click to refresh" banner at the top of any page; clicking refreshes. No polling, no WebSocket, no JavaScript framework.
- **Diagram browser view** (`/diagrams`): lists all `.puml` files in `architecture-repository/diagram-catalog/diagrams/`; renders each inline as SVG (via `puml_renderer.py`); shows element count from the sub-catalog files; links each diagram to the artifact that produced it (via `diagrams/index.yaml`).
- **Updated views table:**

| View | URL | Content |
|---|---|---|
| Engagement Overview | `/` | Engagement ID, entry point, current phase, sprint number, gate status summary |
| SDLC Progress | `/progress` | ADM phase timeline; completed/active/pending phases with gate outcomes; current sprint plan |
| Artifact Browser | `/artifacts` | Tree view by work-repository; each artifact shows: status (draft/baselined), version, agent owner, last updated; click to view rendered markdown; inline SVGs for artifacts with associated diagrams |
| Artifact Detail | `/artifacts/<path>` | Full rendered markdown; frontmatter as metadata table; `[@artifact-id]` references resolved as hyperlinks; associated diagrams rendered inline |
| Diagram Browser | `/diagrams` | All `.puml` diagrams from diagram-catalog; rendered SVG inline; element stats; link to producing artifact |
| Event Log | `/events` | Chronological event stream from EventStore (paginated); filter by event type, agent, phase |
| CQ Log | `/cqs` | Open and resolved Clarification Requests; routing target, blocking status, answer |
| Algedonic Log | `/algedonic` | Algedonic signals: trigger ID, severity, status (active/resolved), escalation target |
| Handoff Log | `/handoffs` | Inter-agent handoffs: from, to, artifact, version, acknowledged status |
| Agent Status | `/agents` | Per-agent status: active phase, last event, open CQs, pending handoffs |

**Implementation tasks:**

- [ ] `src/dashboard/__init__.py`
- [ ] `src/dashboard/server.py` — FastAPI app, route definitions, startup; SSE endpoint `/events/stream` for filesystem change notifications
- [ ] `src/dashboard/state.py` — `EngagementSnapshot` dataclass: hydrated from `EventStore.replay()` + filesystem scan of work-repositories; refreshed on each page request
- [ ] `src/dashboard/watcher.py` — `watchdog` observer on `engagements/<id>/work-repositories/`; pushes SSE events; one observer instance per server lifetime
- [ ] `src/dashboard/puml_renderer.py` — detects `plantuml` CLI; renders `.puml` → `.svg`; caches renders; returns SVG content or source fallback
- [ ] `src/dashboard/file_server.py` — serves image files, documents; MIME-type dispatch; no path traversal (restricted to engagement directory)
- [ ] `src/dashboard/markdown_renderer.py` — renders `.md` to safe HTML via `markdown-it-py`; strips embedded HTML; renders frontmatter as metadata table; resolves `[@artifact-id vN.N](path)` references to hyperlinks
- [ ] `src/dashboard/templates/` — Jinja2 templates: `base.html` (includes SSE listener `<script>`), `overview.html`, `progress.html`, `artifacts.html`, `artifact_detail.html`, `diagrams.html`, `events.html`, `cqs.html`, `algedonic.html`, `handoffs.html`, `agents.html`
- [ ] `src/dashboard/static/style.css` — minimal CSS; readable, print-friendly; no build step
- [ ] `src/dashboard/render_cache/` — `.gitignore` entry for cached SVG renders
- [ ] `docs/dashboard.md` — usage guide: starting the server, PlantUML install, SSE change alerts, engagement ID configuration

**Constraints:**

- Dashboard is strictly read-only. It never writes to EventStore, work-repositories, or any engagement file.
- It does not invoke agents, emit events, or trigger any workflow action.
- It must work with a partially-complete engagement (some phases not yet run, some artifacts missing) — absent artifacts display as "not yet produced."
- Startup must complete in under 5 seconds for engagements with up to 500 events and 100 artifacts.
- No external network calls. All data comes from the local filesystem and SQLite. PUML rendering uses the local `plantuml` binary only.
- The SSE listener `<script>` in `base.html` is the only JavaScript permitted. No JavaScript framework, no npm, no build step.

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

## Current State & Immediate Next Actions

**Stages 1 through 4.6b are complete.** All framework documents, AGENT.md files, and skill files have been authored. Stage 5 (Python implementation) is next.

### Resume at: Stage 5 — Python Implementation Layer

Read `framework/agent-runtime-spec.md` and `framework/orchestration-topology.md` before authoring any `src/` file. Begin with Stage 5a (EventStore completion), then 5b (agent layer).

**Outstanding retroactive item (complete before or alongside Stage 5e):**
- Discovery Scan Step 0 (five-layer scan per `framework/discovery-protocol.md §2`) not yet added to Stage 3 skill files. Step 0.L is present in all 43 files; the broader Step 0 envelope (engagement profile read, enterprise repo, external sources, target-repo, EventStore state) is missing from Stage 3 skills. See Stage 5e checklist.

### Key decisions already made (do not re-litigate)
- `workflow.db` is **git-tracked** (canonical EventStore). YAML in `workflow-events/` is a projection. See `framework/architecture-repository-design.md §4.2`.
- Framework deploys **one clone per software project**. Target project is a separate git repo in `engagements/<id>/target-repo/` (.gitignored). Framework files never enter target project.
- `delivery-repository/` holds **delivery metadata only** (PR records, test reports, branch refs). Source code lives in target project repo.
- Change Record (Phase H) is produced by **SA** (not PM). PM produces intake record only.
- Algedonic triggers in `algedonic-protocol.md` are the canonical list. Skill files reference them by ID (e.g., ALG-001); they do not redefine them.
- **Diagram authoring:** agents write PUML source text directly via `write_artifact` — no intermediate spec format. Tools handle catalog I/O (`catalog_lookup`, `catalog_register`, `catalog_propose`, `validate_diagram`, `render_diagram`) and CLI invocation only. See `framework/diagram-conventions.md §1`.

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

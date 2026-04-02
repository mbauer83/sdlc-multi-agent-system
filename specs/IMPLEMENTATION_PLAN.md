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

- **Runtime:** Python 3.11+, Pydantic v2 for all data models, artifact schemas, and event payloads
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

**Branch: `agent/csco`** — Partially complete (2026-04-02)
- [x] `agents/csco/AGENT.md`
- [x] Skill: `stamp-stpa-methodology.md` (master methodology reference)
- [x] `gate-phase-a.md` — Phase A gate review (Prelim→A and A→B votes; SCO Phase A baseline; STAMP Level 1)
- [x] `gate-phase-b.md` — Phase B gate review (B→C vote; SCO Phase B update; STAMP Level 1 process analysis)
- [x] `gate-phase-c.md` — Phase C gate review (C→D vote; SCO Phase C update; STAMP Level 2 application/data)
- [x] `gate-phase-d.md` — Phase D gate review (D→E vote; SCO Phase D update; STAMP Level 3 technology)
- [ ] `gate-phase-g.md` — Phase G spot-checks and G-exit gate (Compliance Assessment review)
- [ ] `gate-phase-h.md` — Phase H gate review (change safety impact classification; SCO update)
- [ ] Skill: `incident-response.md` — safety incident and algedonic response procedure

**Remaining Stage 4 work (next session — pick up here):**

> **Warning:** A background agent was running unsupervised at session end. It may have
> written `gate-phase-g.md`, `gate-phase-h.md`, and/or `incident-response.md` to disk
> after the last commit. If these files exist, treat them as **unreviewed drafts** —
> do not mark them complete without reading and verifying against the framework.
> If they do not exist, author them fresh.

1. Check for untracked files in `agents/csco/skills/` — review any that exist for correctness
2. Also review `gate-phase-b.md`, `gate-phase-c.md`, `gate-phase-d.md` — written by background
   agents and committed without manual review; verify against framework cross-references
3. Author or complete (as needed): `gate-phase-g.md`, `gate-phase-h.md`, `incident-response.md`
4. Update `framework/agent-index.md` — add PO, SM, CSCO rows to Agent Routing Table and skill tables
5. Full coherence review of all Stage 4 files against framework specs
6. Commit as `stage-4-framing-layer`

**Merge all stage-4 branches to `stage-4-framing-layer`** — Pending

---

### Stage 4.5 — Cross-Cutting Framework Extensions

> These framework documents underpin diagram consistency, artifact traceability, agent-profile condensation, and coding-standards enforcement. Author all items before Stage 5 Python work begins. No Python code is produced here — only framework specs, schemas, and retroactive skill file patches.

#### 4.5a — Diagram Conventions Framework

**New document: `framework/diagram-conventions.md`**

Purpose: formalize the production, registration, and reuse of PlantUML diagrams across all agent roles. Drift risk in a multi-agent architecture repository is acute — without a strict catalog-and-reuse protocol, the same actor or system will be drawn differently in every diagram. This document is the canonical specification for all diagram work.

Sections required:

1. **Diagram type catalogue** — when each diagram type is mandatory vs. optional, per agent and per phase:
   - *ArchiMate overlay* (SA): Architecture Vision motivation overlay, Business Architecture capability map, Application Architecture component/interaction overview, Phase H change impact; use `!include` from a shared `archimate-stereotypes.puml` library covering all three ArchiMate layers (Motivation, Business, Application, Technology)
   - *Use Case* (SA, PO): business capability/actor interaction (SA Phase B), requirements scope (PO Phase B); actors must reference catalog `ACT-nnn` IDs
   - *Class/ER with cardinalities* (SA, SwA): data entity model with PK/FK and cardinalities (SA Phase C-Data), domain model (SwA Phase D); entity IDs must map to DA `DE-nnn` identifiers in the Data Architecture artifact, which are in turn linked to ArchiMate Data Objects in the catalog
   - *Sequence* (SA, SwA): key interaction flows in Application Architecture (SA Phase C-App), API contract flows (SwA Phase E); lifeline participants must reference catalog `CMP-nnn` or `ACT-nnn` IDs
   - *Activity/BPMN-overlay* (SA, SwA): business process flows (SA Phase B), solution-level process specs (SA/SwA Phase C/E); swimlane pools must map to `ACT-nnn` (organization) or `SYS-nnn` (system) catalog IDs; tasks and gateways follow BPMN semantics using PlantUML activity diagram syntax restricted to BPMN-compatible constructs (no free-form branching syntax)

2. **Why ontological organization, not vertical slicing, governs the catalog**:

   The catalog's purpose is element reuse across diagrams. The central risk is ontological drift — the same real-world concept (e.g., "Customer") appearing as an ArchiMate Business Actor, a Use Case actor, a BPMN pool, a Sequence lifeline, and a Class entity without any explicit cross-reference, producing five inconsistent representations. The solution is a single canonical element ID that each diagram type references in its own syntactic form.

   Vertical slicing by business domain (e.g., "Order Management", "Customer Management") is appropriate at the **architecture artifact level** — separate subdirectories per domain within each ADM phase output (Phase B, C, D) — because different architects or phases may own different domain slices. However, it is **not** the right top-level organiser for the element catalog, because cross-domain reuse (a Customer actor appearing in both the Order and Shipping domains) requires that the element exist in a single place, not duplicated in two domain directories.

   The catalog therefore uses **ontological layer as the primary organiser** (matching the ArchiMate layer structure, extended for non-ArchiMate diagram types), with `domain:` as a field on each element for filtering. Diagrams are organized by phase and diagram-type, not domain. Domain subdirectories appear in the phase artifact directories (e.g., `application-architecture/order-management/`, `application-architecture/payment/`) but not in the shared catalog.

3. **Enterprise catalog vs. engagement catalog — two-catalog architecture**:

   **Decision: two separate catalogs, each with identical internal package structure. Scope is structural, not a naming convention.**

   The three-scope model established in `framework/architecture-repository-design.md` (§2) already provides the separation: Scope 1 is `enterprise-repository/` (org-wide, Architecture Board owned, indefinite lifetime); Scope 2 is `engagements/<id>/work-repositories/` (project-scoped, SA owned, engagement lifetime). The diagram catalog is a component of both scopes and inherits the same structural divide:

   - **`enterprise-repository/diagram-catalog/`** — org-wide, long-lived elements: enterprise actors, major enterprise systems, canonical enterprise data entities, shared technology nodes. Writes require Architecture Board approval. Maintained by the EA team across all engagements.
   - **`engagements/<id>/work-repositories/architecture-repository/diagram-catalog/`** — self-contained, per-engagement catalog. Created and maintained by SA. Holds all elements used in this engagement's diagrams, including imported enterprise elements.

   Packages (the ontological layers: `motivation/`, `business/`, etc.) are the type organizer *within* each catalog. The ontological packages are the right tool for "what type is this element?" The structural separation between catalogs is the right tool for "which scope does this element belong to?" These two organizing principles serve different purposes and must not be conflated by attempting to encode scope within the package structure.

   **The import-not-include pattern:**

   Enterprise elements that are relevant to an engagement are *imported* into the engagement catalog at bootstrap time — not referenced in-place. SA reads the enterprise catalog, selects applicable elements, and creates engagement-catalog entries for them with locally-assigned IDs and an `extends:` field pointing back to the enterprise source. Diagrams include only the engagement catalog's `_macros.puml` — single include, self-contained, no PUML macro-name collision between the two catalogs.

   This approach is consistent with how the rest of the architecture treats the enterprise/engagement boundary: engagement artifacts are produced independently and promoted back to the enterprise on close, not maintained as live references into the enterprise store.

   **Lifecycle:**
   - At engagement bootstrap (during Preliminary / Phase A): SA scans `enterprise-repository/diagram-catalog/` for elements relevant to the engagement scope; imports relevant entries into the engagement catalog, assigning new engagement-local IDs with `extends: <source-catalog-path>/<element_id>`
   - During the engagement: SA maintains the engagement catalog as the single authoritative source for diagram production; all PUML diagrams reference engagement-catalog IDs only
   - At engagement close: Enterprise Promotion Protocol (§12 of `repository-conventions.md`) covers catalog elements — SA nominates sufficiently general engagement elements for promotion; Architecture Board approves and adds to enterprise catalog

   **Discovery rule (Step 0.D and Step D1):** SA first queries the enterprise catalog to check for existing enterprise-level elements matching the concept; if found, imports; if not, creates a new engagement-local element. This ensures enterprise elements are always used as the basis, with project-specific detail added by specialisation rather than duplication.

   **Enterprise catalog baseline:** `enterprise-repository/diagram-catalog/` is seeded (by the EA team, outside any specific engagement) with: primary stakeholder roles, major enterprise-wide systems, enterprise canonical data entities corresponding to the organisation's core data concepts, shared infrastructure nodes, and key enterprise processes. This baseline is the starting point every engagement imports from.

4. **Common architecture model — ontological structure**:

   Both catalogs use this identical internal package structure. Each ontological sub-catalog feeds one or more diagram types:

   ```
   [enterprise-repository OR engagements/<id>/work-repositories/architecture-repository]/diagram-catalog/
     _macros.puml                       # Auto-generated !define macros for all elements in this catalog
                                        # Engagement version contains imported enterprise elements + engagement elements
     _archimate-stereotypes.puml        # Shared ArchiMate PUML skinparam + stereotype library
                                        # (enterprise-repository version is canonical; engagement copies on import)
     elements/
       motivation/                      # ArchiMate Motivation layer
         stakeholders.yaml              # STK-nnn: stakeholders (map to ArchiMate Stakeholder)
         goals.yaml                     # GOA-nnn: business goals and outcomes
         drivers.yaml                   # DRV-nnn: internal/external change drivers
         principles.yaml                # PRI-nnn: architecture principles
         requirements.yaml              # REQ-nnn: high-level motivational requirements
       business/                        # ArchiMate Business layer
         actors.yaml                    # ACT-nnn: business actors and roles
                                        #   → also: Use Case actors, BPMN pool owners, Sequence human lifelines
         processes.yaml                 # PRO-nnn: business processes
                                        #   → also: BPMN Process element, Activity swimlane subjects
         functions.yaml                 # FUN-nnn: business functions
         services.yaml                  # BSV-nnn: business services
         objects.yaml                   # BOB-nnn: business objects (conceptual data concepts)
                                        #   → linked to DE-nnn data entities in data/ below
       application/                     # ArchiMate Application layer
         components.yaml                # CMP-nnn: application components and microservices
                                        #   → also: Sequence lifelines (system/service participants)
                                        #   → also: Class diagram subject (when modelling component structure)
         interfaces.yaml                # IFC-nnn: interfaces and APIs (shared with AA artifact IFC identifiers)
                                        #   → also: Sequence message boundaries
         data-objects.yaml              # DAO-nnn: application data objects
                                        #   → linked to DE-nnn canonical data entities in data/
         services.yaml                  # ASV-nnn: application services (exposed capabilities)
       technology/                      # ArchiMate Technology layer
         nodes.yaml                     # NOD-nnn: infrastructure nodes (servers, containers, cloud regions)
         artifacts.yaml                 # ART-nnn: deployment artifacts (images, packages, configs)
         services.yaml                  # TSV-nnn: technology services (DBs, message brokers, etc.)
         networks.yaml                  # NET-nnn: networks and communication paths
       data/                            # Canonical data model — shared across diagram types
         entities.yaml                  # DE-nnn: canonical data entities (same IDs as DA artifact)
                                        #   → Class/ER: primary subject (with attributes + cardinalities)
                                        #   → ArchiMate: linked to DAO-nnn data objects
                                        #   → Sequence: data payloads in messages reference DE-nnn
         attributes.yaml                # Per-entity attribute definitions (name, type, PK/FK flag)
       sequences/                       # Sequence diagram participants — not a new ontology layer,
                                        # but a rendering-hint index: maps catalog IDs → PUML lifeline syntax
         participant-map.yaml           # Maps CMP-nnn / ACT-nnn / SYS-nnn → lifeline alias + display name
         message-types.yaml             # Defined operation/message types reusable across sequence diagrams
       processes/                       # Activity/BPMN elements — not a new ontology layer,
                                        # but BPMN-specific rendering constructs keyed to catalog IDs
         pool-map.yaml                  # Maps ACT-nnn / SYS-nnn → BPMN pool definition
         gateway-types.yaml             # Controlled vocabulary: XOR | AND | OR | Event-Based
         event-types.yaml               # Start | End | Intermediate (Message | Timer | Error)
     connections/
       archimate.yaml                   # ArchiMate relationships (CON-A-nnn): association, realization,
                                        #   composition, aggregation, assignment, serving, flow, triggering
       er-relationships.yaml            # ER associations (CON-E-nnn): cardinality, FK references
       sequence-flows.yaml              # Sequence message flows (CON-S-nnn): synchronous, async, return
       process-flows.yaml               # BPMN flows (CON-P-nnn): sequence flow, message flow, default flow
     diagrams/
       <phase>-<diagram-type>-<subject>[-<domain>]-v<N>.puml
                                        # domain suffix optional; used when diagram scope is one domain slice
     rendered/
       <phase>-<diagram-type>-<subject>[-<domain>]-v<N>.svg
   ```

   **Cross-ontology identity links**: Elements in different sub-catalogs that represent the same real-world concept must carry explicit cross-reference fields:
   - `business/actors.yaml[ACT-001]` → `sequences/participant-map.yaml` references `ACT-001`
   - `business/objects.yaml[BOB-001]` → `data/entities.yaml[DE-001]` via `linked_data_entity: DE-001`
   - `application/data-objects.yaml[DAO-001]` → `data/entities.yaml[DE-001]` via `canonical_entity: DE-001`
   - `application/components.yaml[CMP-001]` → `sequences/participant-map.yaml` references `CMP-001`
   - `business/processes.yaml[PRO-001]` → `processes/pool-map.yaml` references `PRO-001`

   This ensures that a Class diagram entity, its ArchiMate data object counterpart, and its appearance as a Sequence message payload all trace to the same `DE-nnn` root, preventing silent drift across diagram types.

   **ID namespaces summary** (for quick reference when authoring skill files):

   IDs are locally unique within each catalog (enterprise or engagement). There is no naming convention that encodes scope into the ID — scope is determined by which catalog file the element lives in. The `extends:` field on an element provides the explicit cross-catalog linkage (e.g., `extends: enterprise-repository/diagram-catalog/elements/business/actors.yaml#ACT-001`). Agents and tools use the catalog file path to determine scope; PUML diagrams use only the engagement catalog's macros (enterprise elements imported at bootstrap have engagement-local IDs).

   | Prefix | Ontological layer | Primary diagram type | Secondary uses |
   |--------|-------------------|---------------------|----------------|
   | `STK` | Motivation | ArchiMate motivation | — |
   | `GOA` | Motivation | ArchiMate motivation | — |
   | `DRV` | Motivation | ArchiMate motivation | — |
   | `PRI` | Motivation | ArchiMate motivation | — |
   | `ACT` | Business | ArchiMate business, Use Case | Sequence (human), BPMN pool |
   | `PRO` | Business | ArchiMate business, Activity/BPMN | BPMN process |
   | `BSV` | Business | ArchiMate business | — |
   | `BOB` | Business | ArchiMate business | links to `DE-nnn` |
   | `CMP` | Application | ArchiMate application | Sequence lifeline, Class |
   | `IFC` | Application | ArchiMate application | Sequence boundary |
   | `DAO` | Application | ArchiMate application | links to `DE-nnn` |
   | `ASV` | Application | ArchiMate application | — |
   | `NOD` | Technology | ArchiMate technology | — |
   | `ART` | Technology | ArchiMate technology | — |
   | `TSV` | Technology | ArchiMate technology | — |
   | `DE`  | Data | Class/ER (primary) | Sequence payload, DAO link |
   | `CON-A` | — | ArchiMate relationship | — |
   | `CON-E` | — | ER association | — |
   | `CON-S` | — | Sequence message flow | — |
   | `CON-P` | — | BPMN flow | — |

5. **Architecture artifact directories and vertical slicing**:

   Vertical slicing by business domain IS appropriate at the **artifact level** within each ADM phase directory. When the engagement scope includes multiple bounded contexts (e.g., Order Management, Customer, Payment), each context gets its own subdirectory within the relevant phase artifact directories. This keeps domain-specific artifacts navigable and independently version-able:

   ```
   architecture-repository/
     diagram-catalog/             # Ontologically organized — shared across all domains (as above)
     architecture-vision/         # No domain subdirs — single engagement-wide vision
     business-architecture/
       _common/                   # Cross-domain: value streams, enterprise capability map
       <domain-a>/                # e.g., order-management/ — domain-specific process/capability artifacts
       <domain-b>/
     application-architecture/
       _common/                   # Shared components, APIs used by multiple domains
       <domain-a>/                # Domain-specific component model, sequence diagrams, API contracts
       <domain-b>/
     data-architecture/
       _common/                   # Canonical data model (master DE-nnn entities); linked to diagram-catalog
       <domain-a>/                # Domain-specific entity extensions, bounded context data model
       <domain-b>/
     technology-architecture/     # No domain subdirs — technology stack is engagement-wide
     principles/
     decisions/                   # ADRs, numbered and domain-tagged but stored flat
     requirements/                # Requirements traceability matrix
   ```

   For **small engagements** (one bounded context, no domain decomposition): the `_common/` directory serves as the single domain; no per-domain subdirectories are created. SA assesses domain boundaries at Phase A/B and creates domain subdirectories only if two or more structurally distinct bounded contexts exist.

5. **Reuse-first protocol** (enforced in every diagram-producing skill step):
   - Step D1: Query the relevant ontological sub-catalog (e.g., `elements/business/actors.yaml` for an actor, `elements/data/entities.yaml` for a data concept) for semantically matching elements (name match, type match, or ID cross-reference to artifact identifiers)
   - Step D2: For each required concept — if found (semantic match ≥ 90%) → use existing ID; if not found → draft new element registration record in the correct sub-catalog
   - Step D3: Submit new elements to SA for catalog integration via handoff event `diagram.catalog-proposal`; SA writes directly; non-SA agents must not write to `diagram-catalog/`
   - Step D4: When adding a new element, SA validates: no duplicate ID within the namespace, no name collision within the sub-catalog, cross-reference fields populated if the element links to another ontological layer

6. **Write authority**:
   - SA: sole writer to all files under `diagram-catalog/`; runs `plantuml` to regenerate `_macros.puml` after any catalog update
   - SwA, PO, and other agents: may draft `.puml` files in their own work-repositories (e.g., `technology-repository/diagrams/` for SwA), referencing catalog IDs; SA integrates these via `diagram.catalog-proposal` handoff on phase transition
   - No agent may create a new element ID without SA catalog registration

7. **PUML syntax conventions** per diagram type: every `.puml` file must begin with a standard header block (title, scale, skinparam), followed by `!include <relative-path>/_macros.puml` and (for ArchiMate diagrams) `!include <relative-path>/_archimate-stereotypes.puml`; elements are declared using their catalog ID as the PUML alias; free-floating labels not connected to catalogued elements are prohibited

8. **Rendering**: Diagrams must be renderable by the local `plantuml` CLI (JAR or system install). At sprint close, SA runs `plantuml -tsvg diagrams/*.puml -o rendered/`. SVGs are committed to git at sprint boundary.

9. **Algedonic triggers** (new IDs to be assigned in `framework/algedonic-protocol.md`):
   - `ALG-C01` — Catalog inconsistency: duplicate element ID or name detected within a sub-catalog
   - `ALG-C02` — Diagram element created without catalog registration (non-SA agent writes directly to `diagram-catalog/`)
   - `ALG-C03` — Cross-ontology link broken: `DAO-nnn.canonical_entity` references non-existent `DE-nnn`; or `BOB-nnn.linked_data_entity` references non-existent `DE-nnn`
   - `ALG-C04` — `_macros.puml` out of sync with `elements/` sub-catalogs (detected at render time by ID mismatch)

**New schema: `framework/artifact-schemas/diagram-catalog.schema.md`**

Specifies required fields and validation rules for each sub-catalog file type:

- **`elements/<layer>/*.yaml` entries**: `element_id` (immutable, namespace-prefixed, `[A-Z]+-\d{3}`), `name`, `archimate_type` (for ArchiMate-layer elements; controlled vocabulary per layer), `description`, `domain` (optional; for filtering within diagrams), `source_agent`, `phase_created`, `phase_last_modified`, `extends` (optional; cross-catalog back-reference to the enterprise element this was imported from, as `<relative-path-to-enterprise-catalog-file>#<enterprise-element-id>`), plus layer-specific cross-reference fields (`linked_data_entity`, `canonical_entity`, `pool_owner`, etc.)
- **`connections/<type>.yaml` entries**: `connection_id` (namespaced: `CON-A-nnn`, `CON-E-nnn`, `CON-S-nnn`, `CON-P-nnn`), `from_element_id`, `to_element_id`, `relationship_type` (controlled vocabulary per connection type), `label` (optional), `created_by_agent`, `phase_created`
- **`sequences/participant-map.yaml` entries**: `catalog_id` (must exist in `elements/`), `lifeline_alias` (PUML alias), `display_name`, `participant_type` (actor | boundary | control | entity | database | participant)
- **`processes/pool-map.yaml` entries**: `catalog_id` (must exist in `elements/business/actors.yaml` or `elements/application/components.yaml`), `pool_label`, `lane_definitions[]` (optional; each lane references a child `ACT-nnn`)
- **Diagram index entries** (maintained in `diagrams/index.yaml`): `diagram_id`, `title`, `diagram_type` (archimate-motivation | archimate-business | archimate-application | archimate-technology | use-case | class-er | sequence | activity-bpmn), `puml_file_path`, `domain` (optional), `agent_owner`, `phase`, `elements_used[]`, `connections_used[]`, `rendered_svg_path`

#### 4.5b — Artifact Reference Format Extension

**Update `framework/repository-conventions.md` — add §13: Canonical Artifact Reference Format**

Every handoff, work-spec, or skill output that cites another artifact must use one of the following forms:

- **In-text Markdown reference:** `[@<artifact-id> v<major>.<minor>](<relative-path-from-engagement-root>)` — e.g., `[@ARCH-VIS-001 v1.2](work-repositories/architecture-repository/architecture-vision/arch-vis-001-v1.2.md)`
- **Frontmatter `references:` list:** YAML list of artifact-ids cited by this artifact; used by the orchestration layer and dashboard for cross-artifact dependency resolution
- **Handoff event payload `artifact_refs:` field:** list of artifact-ids explicitly included in the handoff; the receiving agent uses these to prime its Discovery Scan
- **Work-spec `## Inputs Required` table:** each row that names a prior artifact must include its artifact-id and the owning work-repository path

Agents must never reference artifacts by filename alone — the artifact-id plus version is the stable identifier.

#### 4.5c — Diagram-Aware Discovery Protocol Extension

**Update `framework/discovery-protocol.md` — add §8: Diagram Catalog Lookup**

For any skill step that produces or updates a diagram, the standard Discovery Scan (§2) must include an additional sub-step:

> **Step 0.D — Diagram Catalog Lookup** (insert after Step 0 source scan, before CQ assessment)
> 1. Identify the relevant ontological layers for the current task (e.g., a business process diagram needs `elements/business/` and `processes/`; a data model diagram needs `elements/data/` and `connections/er-relationships.yaml`)
> 2. Read the relevant sub-catalog files from `architecture-repository/diagram-catalog/elements/<layer>/` — extract all entries whose name, type, or cross-reference fields match the current artifact domain
> 3. Read the relevant `connections/` file(s) for known relationships between extracted elements
> 4. Annotate the working context: "Diagram catalog: N elements found relevant; IDs: [...]"
> 5. Proceed to diagram production using Steps D1–D4 from `framework/diagram-conventions.md §5`

If the engagement catalog does not yet exist (Preliminary / Phase A bootstrap): SA creates the empty directory structure and, if an enterprise catalog is configured, runs the enterprise catalog import scan to seed the engagement catalog with relevant elements before any diagram work begins.

#### 4.5d — Coding Guidelines and Standards Discovery Protocol

**Update `framework/discovery-protocol.md` — add §9: Mandatory Standards and Guidelines Discovery**

For SwA (Phase D, E, F, G), DE (Phase G), and DO (Phase D, E, F, G), the Discovery Scan Step 0 must include:

> **Step 0.S — Standards and Coding Guidelines Discovery** (mandatory for SwA, DE, DO)
> 1. Scan `technology-repository/coding-standards/` — if present, read all files; record findings as "Coding Standards: [list of docs found]"
> 2. Scan `enterprise-repository/standards/` — read applicable technology standards (language, framework, security)
> 3. If no coding guidelines found in either location: record as discovery gap "COD-GAP-001: No coding standards document found"; DO NOT proceed silently; raise CQ to PM/SwA requesting standards authorship if gap is blocking the current task
> 4. All Phase G skill outputs (implementation specs, PR reviews, deployment configs) must cite the governing standard by its document path

This ensures coding conventions, security standards, and platform standards are never silently skipped by implementing agents.

#### 4.5e — Agent Profile Condensation: Layer 1 / Layer 2 Design

**Design rationale (do not skip):**

The runtime system prompt has two identity-related layers. Their purposes are distinct and must not overlap:

- **Layer 1 (`system-prompt-identity`)** answers: *who am I, what do I own, what is my hard constraint?* — factual identity, authority scope, one non-negotiable rule. No behavioral content.
- **Layer 2 (`### Runtime Behavioral Stance`)** answers: *how do I think and act when the task doesn't resolve the situation?* — default disposition across all skills and phases. No identity restatement.

Layer 3 (skill instructions) already handles task-specific conflict engagement (`### Personality-Aware Conflict Engagement`). Layer 2 provides the *cross-cutting default disposition* that underlies every skill invocation. Without it, the agent's behavioral defaults are undefined and will vary unpredictably across invocations.

A subsection named "Condensed Behavioral Directives" would signal to authors that they should compress §11 documentation into fewer words — producing abstract prose ("I value coherence") that does not reliably shape behavior. The correct approach is a separately-authored, runtime-first block.

**Required change to `framework/agent-runtime-spec.md` §2 (Layer 2 spec):**

Replace the current Layer 2 description with the following:

> **Layer 2 — Runtime Behavioral Stance** (`### Runtime Behavioral Stance` subsection within §11; ≤200 tokens)
>
> Source: a dedicated subsection `### Runtime Behavioral Stance` within `agents/<role>/AGENT.md §11`. This subsection is **independently authored for the runtime** — it is not a summary or compression of the rest of §11.
>
> Required form: imperative first-person voice, same discipline as a system prompt. Exactly three elements, in this order:
> 1. **Default bias** (1–2 sentences): what the agent defaults to when a trade-off is not resolved by skill instructions
> 2. **Conflict posture** (1 sentence): how the agent responds when another agent disputes its output or decision
> 3. **Cross-cutting rule** (1 sentence): one behavioral rule that applies across all skills and phases, beyond the Layer 1 hard constraint
>
> The subsection must NOT: restate identity facts from Layer 1; reference role-type taxonomy (Integrator/Specialist/etc.); include inter-role tension maps; exceed 200 tokens.
>
> Example (SA):
> *"Default to architecture coherence over delivery velocity when PM has not flagged a sprint risk. Request evidence before revising any baselined architecture decision under peer pressure — do not revise under time pressure alone. Never bypass a CSCO gate vote even when all other stakeholders have approved."*

**Token budget design rationale:**

The investment in carefully-designed skill procedures and behavioral stances justifies adequate token budgets. The goal is not minimal token use — it is the right amount of specification that the agent can act on correctly and immediately, reducing iteration cycles. Over-compressing skill instructions defeats the purpose of the careful procedure design: the agent will miss validation steps, produce schema-non-compliant artifacts, or make wrong trade-offs. The budget decision is: does this token pay for itself in improved first-pass quality?

**Token budget constraints (add to `framework/agent-runtime-spec.md` §2):**

- **Layer 1 (`system-prompt-identity`):** hard cap ≤150 tokens. Identity and authority are terse by design — 3–5 sentences covers who, what, where, one constraint. Authors verify at writing time (word-count × 1.3).
- **Layer 2 (`### Runtime Behavioral Stance`):** soft target ≤250 tokens; hard cap ≤350 tokens. The three required elements (default bias, conflict posture, cross-cutting rule) can be expressed in 150–250 tokens with appropriate nuance. More than 350 tokens means the section has exceeded its behavioral-directive purpose and drifted into documentation.
- **Layer 3 (skill instructions):** calibrated by skill complexity class:
  - *Simple skills* (intake, routing, gate vote, single-step feedback): ≤600 tokens; `WARNING` if exceeded
  - *Standard phase skills* (phase work with 4–7 steps, moderate cross-role interaction): ≤1200 tokens; `WARNING` if exceeded
  - *Complex skills* (multi-step analysis, multi-phase coordination, STAMP/STPA methodology, master ADM cadence): ≤2000 tokens; `WARNING` at 1500; `SkillBudgetExceededError` only above 2000 (indicates a skill that should be split or redesigned, not compressed)
  - Each skill file's YAML frontmatter should carry `complexity-class: simple | standard | complex` — used by SkillLoader to apply the right threshold
  - Truncation priority if soft target exceeded: Algedonic Triggers → compact ALG-IDs only; Feedback Loop → termination conditions + iteration count only; Outputs → artifact paths only; **Steps are never truncated**

**Implementation impact in Stage 5b:**
- `src/agents/base.py` `AgentSpec.load_personality(agent_id)` extracts the `### Runtime Behavioral Stance` subsection only — not the full §11
- `src/agents/skill_loader.py` reads `complexity-class` from frontmatter to select the token threshold; counts tokens via `tiktoken`; applies truncation priority at soft cap; raises `SkillBudgetExceededError` only if content exceeds the hard cap (2000 for complex, scaled down for other classes)

**Retroactive authoring requirement:** Add `### Runtime Behavioral Stance` subsection to all existing AGENT.md §11 sections (all 9 roles); add `complexity-class:` field to all existing skill file frontmatter. **Both COMPLETE** — all 9 AGENT.md files and all 40 skill files updated.

#### 4.5f — Retroactive Diagram and Reference Updates to Existing Skill Files

Tracked for Stage 5 retroactive pass (do not block Stage 4.5 authoring on these):

| File | Update Required |
|---|---|
| `agents/solution-architect/skills/phase-b.md` | Add Step D: ArchiMate capability map + Use Case diagram production (Steps D1–D4 from diagram-conventions.md) |
| `agents/solution-architect/skills/phase-c-application.md` | Add Step D: Sequence diagram for key interactions; Class/ER for conceptual application model |
| `agents/solution-architect/skills/phase-c-data.md` | Add Step D: Class/ER diagram with DE-nnn IDs; register all DE-nnn entities in diagram catalog |
| `agents/software-architect/skills/phase-d.md` | Add Step D: Class diagram (domain model); component diagram; reference SA diagram catalog |
| `agents/software-architect/skills/phase-e.md` | Add Step D: Sequence diagram for API flows referencing IFC-nnn catalog IDs |
| `agents/software-architect/skills/phase-g-governance.md` | Add Step 0.S: Mandatory coding-guidelines pre-read |
| `agents/implementing-developer/skills/phase-g.md` | Add Step 0.S: Mandatory coding-guidelines pre-read |
| `agents/devops-platform/skills/phase-g.md` | Add Step 0.S: Advisory coding-guidelines and platform-standards pre-read |
| All AGENT.md files (SA, SwA, DO, DE, PM, QA, PO, SM, CSCO) | Add `### Runtime Behavioral Stance` subsection to §11 + `## Artifact Discovery Priority` section — **COMPLETE** |
| All AGENT.md files (all roles) | Add `## Artifact Discovery Priority` subsection: defines ordered list of repositories to scan, by role; architects prioritize `architecture-repository/` then `technology-repository/`; DE and DO must always check `technology-repository/coding-standards/` first |

**New AGENT.md section requirement — `## Artifact Discovery Priority`:**
Every AGENT.md must include a section specifying, in priority order, which repositories and document types the agent must scan during Discovery Scan Step 0. This section feeds the `read_artifact` tool's default search scope. Required for all roles; particularly critical for integrators and implementation roles. Content is role-specific:
- SA: architecture-repository (own), enterprise-repository, external-sources
- SwA: technology-repository (own), architecture-repository (SA), enterprise-repository/standards
- DE: technology-repository (coding-standards, FIRST), architecture-repository (implementation plan, contracts), delivery-repository (own)
- DO: technology-repository (platform specs), enterprise-repository/standards, devops-repository (own)
- PM: project-repository (own), all other repositories (read-only, coordination)
- QA: qa-repository (own), architecture-repository (contracts), technology-repository (implementation plan)
- PO: project-repository, architecture-repository (requirements traceability)
- CSCO: safety-repository (own), all other repositories (gate review read)

**Commit as `stage-4.5-framework-extensions`**

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
  - `diagram_tools.py` — `catalog_lookup(query, ontological_layer)` (semantic search across `elements/<layer>/`; returns matching element IDs + names); `catalog_propose(element_spec)` (submits new element via `diagram.catalog-proposal` handoff; non-SA only); `catalog_register(element_spec)` (SA only; writes to correct sub-catalog YAML; regenerates `_macros.puml`; validates no duplicate IDs); `produce_diagram(diagram_spec)` (generates PUML source from a structured spec following diagram-conventions.md syntax rules; writes to agent's own work-repository or to `diagram-catalog/diagrams/` for SA)
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
- [ ] Retroactive: add discovery scan Step 0 to all Stage 3 skill files (tracked since Stage 3 review)
- [x] Retroactive: add `### Runtime Behavioral Stance` subsection to all AGENT.md §11 sections (all 9 roles) — **COMPLETE**
- [x] Retroactive: add `## Artifact Discovery Priority` section to all AGENT.md files (all 9 roles) — **COMPLETE**
- [ ] Retroactive: add diagram production Steps D1–D4 to SA `phase-b.md`, `phase-c-application.md`, `phase-c-data.md` and SwA `phase-d.md`, `phase-e.md` per Stage 4.5f table
- [x] Retroactive: add Step 0.S (Standards and Coding Guidelines Discovery) to SwA `phase-g-governance.md`, DE `phase-g.md`, DO `phase-g.md` — **COMPLETE**
- [ ] Retroactive: add Step 0.D (Diagram Catalog Lookup) to SA `phase-b.md`, `phase-c-application.md`, `phase-c-data.md` and SwA `phase-d.md`, `phase-e.md` — **blocked on `framework/diagram-conventions.md`**

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

**Stages 1, 2, and 3 are complete.** Pre-Stage-4 additions are complete (personality layer + discoverability layer). Stage 4 is partially complete (PO and SM authored; CSCO foundation in progress). Stage 4.5 framework extensions have been specified (diagram conventions, artifact references, standards discovery, agent profile condensation, enterprise/engagement catalog separation) but not yet authored. Do not re-scaffold directories or re-author any existing file without first reading it.

**Stage 3 completion state:**
- `framework/discovery-protocol.md` — authored (discovery-first protocol for all agents)
- `agents/solution-architect/` — AGENT.md + 6 skills complete
- `agents/software-architect/` — AGENT.md + 5 skills complete
- `agents/devops-platform/` — AGENT.md + 4 skills complete
- `agents/implementing-developer/` — AGENT.md + 3 skills complete
- `agents/qa-engineer/` — AGENT.md + 3 skills complete

### Resume at: Stage 4 — Framing Layer Agents

Three agents remain before Stage 4 is complete. Author in this order:

**1. Product Owner (`agents/product-owner/`)**
- Primary phases: Prelim, A, B, H; consulting C, E, Requirements Management
- Owns Requirements Register, Business Scenarios, Requirements Traceability Matrix
- Collaborates with SA (requirements → architecture traceability); SM (market input); PM (sprint planning input)
- Skills: `phase-a.md`, `phase-b.md`, `phase-h.md`, `requirements-management.md`, `stakeholder-communication.md`
- **Personality:** Framing (Value) — spec at `specs/agent-personalities/product-owner.md`; key tensions with SA (value-now vs coherence), CSCO (market opportunity vs risk control); §11 required

**2. Sales & Marketing Manager (`agents/sales-marketing/`)**
- Primary phases: A (market research input)
- Owns Market Analysis, Business Scenarios
- Collaborates with PO (requirements validation); SA (business drivers)
- Skills: `phase-a-market-research.md`, `phase-a-swot.md`, `requirements-management-feedback.md`
- **Personality:** Framing (Market) — spec at `specs/agent-personalities/sales-marketing-manager.md`; key tensions with SA/SwA (market ambition vs feasibility constraints); §11 required

**3. Chief Safety & Compliance Officer (`agents/csco/`)**
- Most complex Stage 4 agent — gate authority on every phase
- Owns Safety Constraint Overlay (all phase updates), Safety Retrospective Assessment, CSCO Spot-check Record
- Skills: `stamp-stpa-methodology.md`, `gate-phase-a.md`, `gate-phase-b.md`, `gate-phase-c.md`, `gate-phase-d.md`, `gate-phase-g.md`, `gate-phase-h.md`, `incident-response.md`
- **Personality:** Integrator (Safety) — spec at `specs/agent-personalities/safety-engineer--chief-compliance-officer.md`; key tensions with PO/Sales (risk control vs velocity), Dev/SwA (safety requirements vs implementation expedience); §11 required; gate skills must include `### Personality-Aware Conflict Engagement` subsections

### Key decisions already made (do not re-litigate)
- `workflow.db` is **git-tracked** (canonical EventStore). YAML in `workflow-events/` is a projection. See `framework/architecture-repository-design.md §4.2`.
- Framework deploys **one clone per software project**. Target project is a separate git repo in `engagements/<id>/target-repo/` (.gitignored). Framework files never enter target project.
- `delivery-repository/` holds **delivery metadata only** (PR records, test reports, branch refs). Source code lives in target project repo.
- Change Record (Phase H) is produced by **SA** (not PM). PM produces intake record only.
- Algedonic triggers in `algedonic-protocol.md` are the canonical list. Skill files reference them by ID (e.g., ALG-001); they do not redefine them.

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

# SDLC Multi-Agent System

A multi-agent AI framework that operationalises the full Software Development Lifecycle through a suite of specialised Claude-based agents. Each agent embodies a distinct professional role, carries role-specific skills scoped to the [TOGAF ADM](https://en.wikipedia.org/wiki/The_Open_Group_Architecture_Framework) phases it owns, and participates in a structured workflow governed by architecture principles drawn from organisational theory, systems safety, and cybernetics.

---

## Goals

- Make TOGAF ADM phases executable end-to-end, not just documented
- Produce consistent, schema-valid architecture artifacts across every phase, tracked in work-repositories — from Architecture Vision through Implementation Governance to Change Management
- Support brownfield engagements as a first-class use case: the system can reconstruct an architecture model from an existing codebase and then govern it forward
- Keep humans in the loop at every meaningful decision point through a structured query, review, and approval surface
- Treat safety and compliance as a woven-in concern at every phase transition, not a final gate

---

## Conceptual Foundations

### TOGAF ADM

The framework uses the [TOGAF Architecture Development Method](https://en.wikipedia.org/wiki/The_Open_Group_Architecture_Framework) as its workflow backbone. Phases run in an **Agile ADM** cadence: time-boxed Architecture Sprints feed Delivery Sprints, with explicit phase-transition gates and support for non-linear iteration. Phases are not one-shot — any phase can be revisited when a change, a new requirement, or a corrective signal demands it. The full cadence, sprint structure, and gate model are specified in `framework/agile-adm-cadence.md`.

### Viable System Model (Beer)

Each agent is modelled as a cybernetic control unit with some conceptual similarities to [Stafford Beer's Viable System Model](https://en.wikipedia.org/wiki/Viable_system_model) and other applications of control-theoretical and systems theoretical insights: a defined purpose, defined input/output contracts, and distinct upward (reporting, escalation, feedback-giving), downward (direction, feedback-integration), and lateral (peer handoff) communication channels. No agent has unbounded authority. The Project Manager occupies VSM System 3 — the coordinator that balances operational demands and allocates work. The Solution Architect occupies VSM System 4 — the outward-facing intelligence that monitors the environment and shapes the architecture accordingly.

The **algedonic channel** — Beer's fast-path signal that bypasses the hierarchy when severity demands — is formalised in `framework/algedonic-protocol.md` and referenced in every skill file.

### Contingency Theory (Lawrence & Lorsch; Galbraith)

The agent roster is designed around the principle of differentiated specialisation and integration: each role owns a bounded domain of knowledge, a distinct set of phases, and a separate work repository. Integration is achieved not through shared state but through integrator-roles (architects, CSCO), structured handoff events and explicit gate evaluations — the same pattern Lawrence and Lorsch identified as the mechanism by which differentiated organisations maintain coherence under environmental uncertainty. ([[1](https://www.researchgate.net/profile/Jay-Lorsch/publication/234021677_Differentiation_and_Integration_in_Complex_Organizations/links/569908e008ae6169e55162b5/Differentiation-and-Integration-in-Complex-Organizations.pdf)],[[2](https://armyoe.com/wp-content/uploads/2018/03/1984_vol8_number11.pdf#page=29)])

[Galbraith's information processing theory](https://isscholar.com/wp-content/uploads/2024/10/Galbraith.pdf) informs the discovery-before-CQ protocol: agents are expected to scan all available sources first, infer what they can, and raise clarification requests only for information that is genuinely absent. The system is designed to function usefully from an incomplete starting state rather than demanding a full brief upfront.

### STAMP / STPA Safety Engineering

Safety is represented as a first-class architectural concern, not a checklist. A dedicated Chief Safety and Compliance Officer agent-role applies STAMP (Systems-Theoretic Accident Model and Processes) and STPA (Systems-Theoretic Process Analysis) to identify hazardous control actions, inadequate feedback loops, and missing safety constraints at each phase.([[1](http://sunnyday.mit.edu/accidents/safetyscience-single.pdf)], [[2](https://functionalsafetyengineer.com/introduction-to-stamp/)], [[3](https://www.flighttestsafety.org/images/Engineering_a_Safer_World.pdf)], [[4](https://www.flighttestsafety.org/images/STPA_Handbook.pdf)]) CSCO holds gate veto authority on every phase transition. Safety-relevant processes, actors, and components are explicitly flagged in architecture artifacts. The safety repository (`engagements/<id>/work-repositories/safety-repository/`) is the sole write target for CSCO and is never modified by other agents.

---

## Agent Roles

Nine specialist agents cover the full SDLC:

| Agent | VSM Position | Primary ADM Phases |
|---|---|---|
| Sales & Marketing Manager | System 4 (external intelligence) | Phase A |
| Product Owner | System 3* (requirements authority) | Prelim, A, B, H |
| Solution Architect | System 4 | A, B, H (Phase C: traceability review, consulting) |
| Software Architect / Principal Engineer | System 3 | C, D, E, F, G, H (application/technology layer) |
| DevOps / Platform Engineer | System 1 | D, E, F, G |
| Implementing Developer | System 1 | G |
| QA Engineer | System 1 | E/F (planning), G (execution) |
| Project Manager | System 3 (coordinator/supervisor) | All (coordination) |
| Chief Safety & Compliance Officer | System 2 (regulator) | All phases (gate reviews) |

The Project Manager acts as the LangGraph supervisor node: it deliberates on what to do next, routes work to specialists, batches clarification requests for the user, evaluates phase-transition gates, and manages the sprint review workflow. It does not produce architecture artifacts — it coordinates their production.

Each agent's mandate, input/output contracts, entry-point behaviour, personality stance, and skill index are specified in `agents/<role>/AGENT.md`.

---

## Skills and ADM Phase Alignment

Each agent owns a set of skill files (`agents/<role>/skills/*.md`). A skill corresponds to a specific ADM phase or major capability. The **ArchiMate layer boundary is the role boundary**: the Solution Architect owns motivation, strategy, and business-layer artifacts (Phases A, B, and the business-layer track of Phase H); the Software Architect / PE owns application and technology-layer artifacts (Phase C application + data architecture, Phases D–G, and the application/technology track of Phase H). For example: the SA has skills for Phase A (Architecture Vision), Phase B (Business Architecture), Phase C traceability review (consulting — verifying that SwA's application entities correctly realise business-layer entities), reverse architecture reconstruction (EP-G), and business-layer change management (Phase H). The SwA has primary skills for Phase C (Application and Data Architecture production), Phase D (Technology Architecture), Phases E–G, and the application/technology Phase H track.

Skills are the primary runtime delivery vehicle: when an agent is invoked, the orchestrator loads the relevant skill file and injects its instructions (steps, inputs, outputs, feedback loop, algedonic triggers) as the Layer 3 system prompt. Skills are authored at three complexity levels (`simple`, `standard`, `complex`) which govern their token budget. The skill loading and prompt assembly protocol is specified in `framework/agent-runtime-spec.md`.

A compact routing index of all agents and their skills is maintained in `framework/agent-index.md`.

---

## Workflows

### Forward SDLC (EP-0 cold start)

The standard greenfield flow: the user initiates a new engagement, the Project Manager runs the entry assessment, and the system executes ADM phases sequentially from Preliminary through Phase G, with gate evaluations at each transition. Sprints are time-boxed; artifacts are versioned and handed off through the event stream.

### Brownfield Onboarding (EP-G)

For existing codebases, the system enters at Phase G via a reverse architecture reconstruction workflow. Specialist agents scan the target repository (IaC, source structure, package manifests, configuration) and user-provided documents to infer and populate an architecture model (registering entities and connections). The user confirms inferred entities before they are committed. The result is a populated architecture repository that the system can then govern forward. The reverse architecture skills are in `agents/solution-architect/skills/` and `agents/software-architect/skills/`.

### Other Entry Points

Six additional entry points (EP-A through EP-H, excluding EP-0 and EP-G) handle mid-lifecycle starts — where the user arrives with existing artifacts, a requirements register, a completed design, or an in-flight change. Entry-point handling is specified in `framework/sdlc-entry-points.md` and in every `AGENT.md`.

### Change Management (Phase H)

Phase H runs two parallel tracks coordinated by the Project Manager. The Solution Architect produces the business/motivation/strategy-layer Change Record and always routes a handoff to the Software Architect / PE to assess application and technology impact. The Software Architect / PE produces a separate application/technology-layer Change Record covering APP/DOB entity updates, TA revisions, and AC amendments. Both CRs cross-reference each other; the PM waits for both gate votes before closing Phase H. Phase H can trigger a return to any earlier phase. The algedonic channel provides an immediate escalation path when a change has safety implications.

### Enterprise Promotion

Architecture entities developed within an engagement can be promoted to the enterprise repository for cross-engagement reuse, subject to Architecture Board review. The promotion procedure, ID assignment, and reference sweep are specified in `framework/repository-conventions.md §12`.

---

## Deployment Model

**Create a new repository per project from this template.** This repository is a framework template. For each software project or programme being governed, clone it and immediately push the result as a new, standalone git repository — the per-project architecture repository. All per-project and per-engagement work then accumulates in that new repository under version control, with its own git history, remote, and branch strategy. Framework files themselves are never committed into any target project's code repository.

```bash
# Bootstrap a new project architecture repository
git clone https://github.com/your-org/sdlc-multi-agent-system my-project-architecture
cd my-project-architecture
git remote set-url origin git@github.com:your-org/my-project-architecture.git
git push -u origin main
```

```
my-project-architecture/       ← your clone of this repo
  engagements/
    ENG-001/                    ← one directory per engagement
      work-repositories/        ← role-owned artifact stores (git-tracked)
      target-repos/             ← local clones of the target codebase (.gitignored)
      workflow.db               ← event store (git-tracked)
      user-uploads/             ← files uploaded via dashboard (.gitignored)
  enterprise-repository/        ← shared architecture knowledge (see below)
  external-sources/             ← source adapter configs (credentials in env vars)
  engagements-config.yaml       ← engagement and target-repo configuration
  enterprise-repository-config.yaml
```

**Per-engagement work-repositories** (`engagements/<id>/work-repositories/`) are git-tracked inside the clone. Each role-owned repository (architecture, technology, project, safety, delivery, QA, devops) accumulates artifacts, entity files, diagrams, and decisions for that engagement. The event store (`workflow.db`) is also git-tracked as the canonical workflow state record.

**The enterprise repository** (`enterprise-repository/`) is the persistent, cross-engagement store for promoted architecture content. It holds organisation-wide standards, approved technology patterns, promoted model-entities, connections & diagrams, cross-engagement governance records, and synthesised learnings. It is read by agents in every engagement and written to exclusively by Architecture Board members. Its content accumulates across engagements and projects — it is the long-lived institutional memory of the architecture practice.

The enterprise repository can be configured in three modes via `enterprise-repository-config.yaml`:

| Mode | Description |
|---|---|
| `embedded` | Lives inside this clone (default; simplest for single-team use) |
| `submodule` | Separate git repository included as a submodule; enables sharing across multiple project clones |
| `external` | Path or URL to an externally managed repository; read-only to this clone unless Architecture Board credentials are configured |

**Promotion** is the mechanism by which engagement-local artifacts graduate to the enterprise repository. When an entity file, ADR, or learning entry has proven its value in one engagement, the PM or Architecture Board initiates promotion: the entity is assigned a globally unique enterprise ID, all references in connection and diagram files are swept, the file moves to the enterprise path, and an `artifact.promoted` event is recorded. The full procedure is in `framework/repository-conventions.md §12`.

**External information sources** (Confluence, Jira, read-only git repositories) are configured separately in `external-sources/` and queried situatively — not on every skill invocation. See the Configuration section for details.

---

## Configuration

### `engagements-config.yaml`

Defines the active engagement: entry point, target repositories (single-repo or multi-repo), sprint review settings, and upload configuration. Multi-repo engagements (microservices, CQRS, microfrontends) are first-class: each registered repository has a role, domain, and primary flag.

```yaml
engagement-id: my-project
entry-point: EP-0
target-repositories:
  - id: api
    label: API Service
    role: backend
    primary: true
    url: https://github.com/org/api
  - id: frontend
    label: Web Frontend
    role: frontend
    url: https://github.com/org/web
sprint-review:
  enabled: true
  auto-approve-after-hours: 0
```

### External Information Sources

Agents can query external systems during their discovery scans — Confluence wikis, Jira projects, read-only git repositories, and other sources. Each external source is configured as a separate file in `external-sources/<source-id>.config.yaml`. Credentials are never committed; all authentication references environment variables.

```yaml
# external-sources/my-confluence.config.yaml
source-id: company-confluence
source-type: confluence        # confluence | jira | git | sharepoint | api
base-url: https://company.atlassian.net/wiki
auth-method: env-var
auth-config:
  env-var: CONFLUENCE_API_TOKEN
  user-env-var: CONFLUENCE_USER_EMAIL
engagement-scope: all          # or list specific engagement IDs: [ENG-001]
index-scope:
  spaces: [ARCH, ENG, PRODUCT]
access-pattern: search-only
purpose: |
  Source for existing ADRs, runbooks, and product documentation.
```

Example configs for Confluence, Jira, and read-only git repositories are provided in `external-sources/EXAMPLE-*.config.yaml`.

**How agents use external sources:**

The discovery scan (`framework/discovery-protocol.md §2`) makes a deliberate distinction between *structured, system-controlled repositories* and *unstructured external sources*:

- **Always queried on every skill invocation:** the engagement work-repositories, the enterprise repository, and the target project repositories. These are structured, versioned, and owned by this system. Agents never walk directory trees — they query via `list_artifacts(**filter)` for metadata-driven lookup and `search_artifacts(query)` for content-based and semantic search, both backed by the `ModelRegistry` (in-memory frontmatter cache + SQLite FTS5 index + optional sqlite-vec semantic tier). Only artifact bodies confirmed as relevant are loaded.
- **Queried situatively only:** external sources such as Confluence, Jira, and read-only reference repositories. These are not under the system's control, have no guaranteed structure relative to the architecture model, and may contain large volumes of irrelevant content.

External sources are queried in three specific situations: (1) during reverse architecture (EP-G entry, SA-REV-* and SWA-REV-* skills), where all available evidence is gathered to reconstruct an architecture model from scratch; (2) when a user explicitly references an external source in a CQ answer — the agent resolves only the cited item, not a broad search; (3) when the Project Manager explicitly instructs an agent to consult a specific source because the relevant phase context is known to be thin. Retrieved content is annotated with `[source: <source-id>]`.

**User-referenced sources in CQ answers:**

When an agent raises a clarification request, users can point to external source content rather than typing it out — for example, citing a Jira epic key (`PROJ-123`) or a Confluence page URL. The `SourceAdapterPort` implementation resolves these references to full content and includes them in the agent's answer context. Users can also upload files directly via the dashboard (see User Interaction Surface below), which are stored at `engagements/<id>/user-uploads/` and available to agents as an additional source for the remainder of the engagement.

### `enterprise-repository-config.yaml`

Controls whether the enterprise repository is embedded in this clone, a git submodule, or an external path. See `framework/architecture-repository-design.md` for the scope model.

---

## Repository Structure

### Work Repositories

Each engagement maintains a set of role-owned work repositories under `engagements/<id>/work-repositories/`. These hold architecture artifacts, technology decisions, test strategies, safety analyses, and delivery metadata. No agent writes outside its designated repository path; cross-role transfers happen exclusively through handoff events.

| Repository | Owner |
|---|---|
| `architecture-repository/` | Co-owned: SA writes motivation/strategy/business/implementation layers; SwA writes application layer (`model-entities/application/`) in Phase C |
| `technology-repository/` | Software Architect / PE |
| `project-repository/` | Project Manager |
| `safety-repository/` | CSCO |
| `delivery-repository/` | Implementing Developer (metadata only) |
| `qa-repository/` | QA Engineer |
| `devops-repository/` | DevOps / Platform Engineer |

Architecture entities follow the **Entity Registry Pattern v2.0**: one `.md` file per entity, organised by ArchiMate layer (e.g. `model-entities/business/roles/`, `model-entities/business/collaborations/`, `model-entities/application/components/`), with machine-readable YAML frontmatter. The `ModelRegistry` is built from these files at startup. Architecture views in `diagram-catalog/diagrams/` include both PlantUML diagram files (`*.puml`) and matrix view files (`*.md`) authored by agents using the same model IDs and references. The full catalog of diagram/matrix conventions and authoring rules is in `framework/diagram-conventions.md`. The canonical registry of valid entity types, connection types, ArchiMate element types, and grouping stereotypes lives in `src/common/archimate_types.py` and is the single source of truth for both documentation and the `ModelVerifier`.

**Validated and semantically discoverable:** `src/common/model_verifier.py` (`ModelVerifier`) validates every entity, connection, and diagram file against ERP v2.0 rules — referential integrity, status lifecycle (E306/E307: baselined diagrams cannot reference draft elements), PlantUML syntax, required frontmatter fields, and ArchiMate type correctness. `src/common/model_query.py` (`ModelRepository`) provides keyword and synonym search, graph traversal, and the framework-aligned `list_artifacts` / `search_artifacts` / `read_artifact` query API used by all agents during Discovery Scan Step 0. Together these tools enable agents to efficiently query only what they need (targeted `entity_status()` lookup without full scans; `find_neighbors()` for local graph traversal) while the batch `verify_all()` ensures the entire model stays coherent. The same `ModelRegistry` interface is shared between the verifier and the query engine — no duplication.

In runtime use, these capabilities are exposed through MCP tool families (model query + model write + verification), so agents use tools to query, construct, and validate model entities, connections, and diagrams rather than relying on ad-hoc file walking.

This repository also provides an additional reusable MCP server, `sdlc-registry`, which exposes the agent and skill catalog defined here for discovery and runtime loading in other Claude Code or MCP-compatible setups. It is complementary to the model server (`sdlc-mcp-model`): registry MCP serves reusable role/skill metadata, while model MCP serves architecture model query and validation operations.

#### Diagram types produced

Matrix view artifacts (`diagram-catalog/diagrams/*.md`) are also first-class architecture views for dense mappings and coverage checks (for example skill I/O traceability matrices). Representation choice is intentional and balanced: use diagrams where structural/behavioral context matters, and use matrices where high-cardinality traceability is the primary concern. Matrix outputs do not replace contextual diagrams when topology or flow understanding would be lost.

Agents produce five families of PlantUML diagram. **No single diagram type has final authority over system behaviour** — the types are complementary and intentionally overlapping. An application component that appears in an ArchiMate diagram, a sequence diagram, an activity diagram, and an ER diagram must be mutually consistent across all four; deliberate overlap is the cross-verification mechanism that catches mismatches between structural, behavioural, and data specifications. The decision of which diagram type to use for a given aspect is a workflow concern, not a tooling constraint — the rules below guide applicability; some aspects warrant multiple diagram types by design.

**ArchiMate layer diagrams** — the primary structural deliverable of the architecture phases. One diagram per layer, using PlantUML's `!include` macro system against a shared stereotype library (`_archimate-stereotypes.puml`) and a per-engagement macro file (`_macros.puml`) auto-generated from entity `§display ###archimate` blocks. Typical diagrams: Motivation (stakeholders, drivers, goals, principles), Strategy (capabilities, value streams), Business (actors, roles, processes, services), Application (components, interfaces, services, data objects), Technology (nodes, system software, infrastructure services). Connections use ArchiMate relationship types (association, composition, realization, serving, assignment, influence, access). ArchiMate diagrams establish *what exists and how it is related* — they are the structural backbone. Behavioural, data, and interaction details require complementary diagram types.

**ER diagrams (via PlantUML class notation)** — specify the data model: field names, types, and cardinality relationships for persisted domain objects. Each entity's `§display ###er` block provides its class declaration and attribute list; connection files in `connections/er/` provide cardinality lines. ER diagrams are the authoritative field-level specification — the same attribute names appear in Pydantic models, database columns, and API payloads. They intentionally overlap with ArchiMate data-object and technology-node specifications: if an ER diagram and an ArchiMate diagram both reference a domain object, they must agree on its identity and structure.

**Activity diagrams (BPMN-oriented)** — specify workflows and process logic. Used at two levels within an engagement, both of which apply to the software being designed and built:

- **Business layer (Phase B — SA primary):** The workflows of the organisation the software serves — business processes, approval flows, multi-party collaboration procedures, operational sequences. Swim lanes are business actors and roles. These diagrams capture *what the organisation does* and provide the traceability bridge from business requirements to software scope. They overlap with and must be consistent with Phase B ArchiMate business-process entities.
- **Application layer (Phase C — SwA primary):** The process logic *within the software being built* — internal workflows, data-processing pipelines, state machines, multi-step request-handling sequences, and any application-level BPMN that gives precision and granularity to application components or services. Swim lanes are application components, services, or user-facing roles. These diagrams specify *how the software must behave internally* — complementing the structural ArchiMate application diagram with the temporal, conditional flow that structural diagrams intentionally omit. They overlap with sequence diagrams; where both exist for the same scenario, mutual consistency is required.

Decision diamonds map to branching logic in the implementation; action boxes map to discrete steps, handler calls, or service invocations.

> **ENG-001 note (meta-level):** ENG-001 uses this framework to govern the development of the framework itself. Its activity diagrams therefore cover both levels — the business processes of the multi-agent practice (Phase B) and the internal process logic of the multi-agent system (Phase C: skill invocation loop, CQ lifecycle, sprint review flow). In ENG-001, these diagrams are also the binding specification for `src/orchestration/` code, which is a consequence of the self-referential engagement, not a general property of activity diagrams.

**Sequence diagrams** — specify runtime interaction protocols between specific components for specific scenarios. Used for the skill invocation loop, the CQ lifecycle (agent → EventStore → dashboard → user → agent), the sprint review flow, and reverse-architecture reconstruction. Participants map to Python classes or modules; each arrow maps to a method call or event. Sequence diagrams share participants with activity and ArchiMate diagrams — the same component that appears as a box in an ArchiMate application diagram must appear as a participant in the sequence diagrams that govern its runtime behaviour.

**Use-case / user-story diagrams** — produced by the Product Owner and Solution Architect during Phases A and B to capture stakeholder interactions with the system and map them to capabilities and business services. Used as a communication and requirements-scoping artifact; typically accompanies the Architecture Vision and Requirements Register. Use-case actors correspond to business actors and roles in the ArchiMate business-layer diagram — consistency between the two is a required cross-check at Phase B gate.

### Target Repositories

The target project's source code lives in separate git repositories configured under `target-repositories` in `engagements-config.yaml`. Local clones are placed at `engagements/<id>/target-repos/<repo-id>/` and are `.gitignored`. Framework files never enter a target repository. Agents that write to target repos (Implementing Developer, DevOps) do so through git worktrees — one per agent per sprint — to prevent cross-contamination.

### Enterprise Repository

`enterprise-repository/` holds organisation-wide architecture data: approved standards, promoted entity files, cross-engagement governance records, and lessons learned. Engagement agents have read access only; write authority belongs exclusively to Architecture Board members.

---

## Workflow State and Event Sourcing

All workflow state is event-sourced through an SQLite event store (`engagements/<id>/workflow.db`), which is git-tracked as the canonical record. Every meaningful action — phase transition, artifact creation, agent handoff, clarification request, gate evaluation, sprint close, user upload — produces an event. The current workflow state is reconstructed by replaying the event stream (or from a recent snapshot). Human-readable YAML projections are committed to `workflow-events/` at sprint boundaries.

The three-layer event emitter hierarchy is: (1) orchestration layer emits lifecycle events; (2) PM tools emit decision events; (3) specialist agent tools emit artifact and interaction events. Full event taxonomy is in `specs/IMPLEMENTATION_PLAN.md §4.9h` and §5a.

---

## User Interaction Surface

The engagement dashboard (Stage 5.5) is a local FastAPI web server that provides:
- A live view of engagement progress, produced artifacts, and agent activity
- A **Queries** tab surfacing open clarification requests for user response, with file upload support
- A **Review** tab for sprint-end approval workflows — users can mark artifacts as approved, flag items for revision, tag specific agents for corrections, and add comments
- An **Audit** view showing which agent used which skill to produce which artifact

---

## Implementation Status

The framework and ENG-001 reference model are being built incrementally. Current state (2026-04-06):

| Layer | Status |
|---|---|
| Framework specifications (all `framework/` files) | Complete |
| Agent and skill files (all `agents/<role>/`) | Complete |
| ENG-001 reference model — entities (99 files across motivation, strategy, business, application layers; entity types ArchiMate-correct: BusinessRole for agent roles, BusinessCollaboration for Architecture Board) | Complete |
| ENG-001 reference model — connections (89 files: realization, serving, assignment, composition, access, ER; includes 14 BPR→BSV business-layer realization files) | Complete |
| ENG-001 reference model — `_macros.puml` (99 macros, auto-generated from entity `§display ###archimate` blocks via `src/tools/generate_macros.py`) | Complete |
| ENG-001 reference model — diagrams (4/7 produced and semantically verified; sequence diagrams pending) | Partial |
| ENG-001 reference model — overview docs + ADRs | Pending |
| `src/common/model_verifier.py` — BDD-tested verifier for entity/connection/diagram files (71 scenarios); E306/E307 draft-reference checks with targeted `entity_status()`/`connection_status()` lookups; `entity_id_from_path()` formal-id extraction | Complete |
| `src/common/archimate_types.py` — canonical type registry for all entity, connection, element, and grouping stereotype types; single source of truth imported by verifier and referenced in documentation | Complete |
| `src/common/model_query.py` — `ModelRepository`: rich query engine for model-entities, connections, and diagrams; `list_artifacts(**filter)` / `search_artifacts(query)` / `read_artifact(id, mode)` framework-aligned API; keyword+synonym search with `SemanticSearchProvider` hook; graph traversal (`find_connections_for`, `find_neighbors`); CLI (`python -m src.common.model_query`); 36 BDD tests | Complete |
| `src/common/domain_vocabulary.py` — canonical SDLC/ArchiMate domain synonym map; `expand_tokens()` for bidirectional abbreviation expansion; `agent_abbreviations()` and `archimate_prefix_to_type()` lookup tables; shared by `model_query.py`, `LearningStore`, future NLP pipelines | Complete |
| MCP servers — `sdlc-mcp-model` (model query/construct/validate tool surface) and `sdlc-mcp-registry` (reusable agent/skill discovery surface) | Complete |
| Representation selection governance — balanced diagram-vs-matrix policy documented in framework and normalized across role skill runtime-tooling hints | Complete |
| `src/tools/generate_macros.py` — regenerates `_macros.puml` from entity `§display ###archimate` blocks | Complete |
| `pyproject.toml` + uv project setup | Complete |
| `docs/puml-bug-reports.md` — confirmed PlantUML 1.2025.x bugs (PB-001..PB-005) with reproduction cases and workarounds | Complete |
| `src/` Python implementation (EventStore, agents, orchestration, dashboard) | Pending |

**ArchiMate diagram conventions** (`framework/diagram-conventions.md`): §10 covers PlantUML compatibility constraints (PB-001..PB-005 workarounds, DECL_ two-token macro convention); §11 covers ArchiMate semantic constraints (layer boundary rule, active structure type rules, layer-aligned grouping stereotypes with prohibition on inline color overrides). For business operational decomposition (`§11.9.1a`), staged processes/interactions are diagrammed as nested parent containers (`BPR-NNN` / `BIA-NNN` as container element) with internal stage `flow`/`triggering`; parent→stage composition remains mandatory as connection files even when external composition arrows are omitted in the operational view.

See `specs/IMPLEMENTATION_PLAN.md` for the detailed stage-by-stage plan and current checklist.

---

## Further Reading

| Topic | Location |
|---|---|
| Sprint structure and ADM phase mapping | `framework/agile-adm-cadence.md` |
| Agent roles, phases, and RACI | `framework/raci-matrix.md` |
| Artifact versioning and path governance | `framework/repository-conventions.md` |
| Algedonic (fast-path escalation) protocol | `framework/algedonic-protocol.md` |
| Clarification request lifecycle | `framework/clarification-protocol.md` |
| Discovery scan protocol | `framework/discovery-protocol.md` |
| Entry points (EP-0 through EP-H) | `framework/sdlc-entry-points.md` |
| Agent runtime and prompt assembly | `framework/agent-runtime-spec.md` |
| LangGraph orchestration topology | `framework/orchestration-topology.md` |
| Entity Registry Pattern v2.0 | `framework/artifact-registry-design.md` |
| Diagram conventions and PUML templates | `framework/diagram-conventions.md` |
| Agent learning protocol | `framework/learning-protocol.md` |
| Agent personalities and conflict stances | `framework/agent-personalities.md` |
| Compact agent and skill index | `framework/agent-index.md` |
| Implementation plan and stage status | `specs/IMPLEMENTATION_PLAN.md` |
| Per-agent mandate and skill index | `agents/<role>/AGENT.md` |
| Artifact schemas | `framework/artifact-schemas/` |

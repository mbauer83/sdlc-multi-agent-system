# SDLC Multi-Agent System

A multi-agent AI framework that operationalises the full Software Development Lifecycle through a suite of specialised Claude-based agents. Each agent embodies a distinct professional role, carries role-specific skills scoped to the TOGAF ADM phases it owns, and participates in a structured workflow governed by architecture principles drawn from organisational theory, systems safety, and cybernetics.

---

## Goals

- Make TOGAF ADM phases executable end-to-end, not just documented
- Produce consistent, schema-valid architecture artifacts across every phase — from Architecture Vision through Implementation Governance and Change Management
- Support brownfield engagements as a first-class use case: the system can reconstruct an architecture model from an existing codebase and then govern it forward
- Keep humans in the loop at every meaningful decision point — not as a bottleneck, but through a structured query, review, and approval surface
- Treat safety and compliance as a woven-in concern at every phase transition, not a final gate

---

## Conceptual Foundations

### TOGAF ADM

The framework uses the TOGAF Architecture Development Method as its workflow backbone. Phases run in an **Agile ADM** cadence: time-boxed Architecture Sprints feed Delivery Sprints, with explicit phase-transition gates and support for non-linear iteration. Phases are not one-shot — any phase can be revisited when a change, a new requirement, or a corrective signal demands it. The full cadence, sprint structure, and gate model are specified in `framework/agile-adm-cadence.md`.

### Viable System Model (Beer)

Each agent is modelled as a cybernetic control unit in Stafford Beer's Viable System Model sense: a defined purpose, defined input/output contracts, and distinct upward (reporting, escalation), downward (direction, feedback), and lateral (peer handoff) communication channels. No agent has unbounded authority. The Project Manager occupies VSM System 3 — the coordinator that balances operational demands and allocates work. The Solution Architect occupies VSM System 4 — the outward-facing intelligence that monitors the environment and shapes the architecture accordingly.

The **algedonic channel** — Beer's fast-path signal that bypasses the hierarchy when severity demands — is formalised in `framework/algedonic-protocol.md` and referenced in every skill file.

### Contingency Theory (Lawrence & Lorsch; Galbraith)

The agent roster is designed around the principle of differentiated specialisation: each role owns a bounded domain of knowledge, a distinct set of phases, and a separate work repository. Integration is achieved not through shared state but through structured handoff events and explicit gate evaluations — the same pattern Lawrence and Lorsch identified as the mechanism by which differentiated organisations maintain coherence under environmental uncertainty.

Galbraith's information processing theory informs the discovery-before-CQ protocol: agents are expected to scan all available sources first, infer what they can, and raise clarification requests only for information that is genuinely absent. The system is designed to function usefully from an incomplete starting state rather than demanding a full brief upfront.

### STAMP / STPA Safety Engineering

Safety is represented as a first-class architectural concern, not a checklist. The Chief Safety and Compliance Officer agent applies STAMP (Systems-Theoretic Accident Model and Processes) and STPA (Systems-Theoretic Process Analysis) to identify hazardous control actions, inadequate feedback loops, and missing safety constraints at each phase. CSCO holds gate veto authority on every phase transition. Safety-relevant processes, actors, and components are explicitly flagged in architecture artifacts. The safety repository (`engagements/<id>/work-repositories/safety-repository/`) is the sole write target for CSCO and is never modified by other agents.

---

## Agent Roles

Nine specialist agents cover the full SDLC:

| Agent | VSM Position | Primary ADM Phases |
|---|---|---|
| Sales & Marketing Manager | System 4 (external intelligence) | Phase A |
| Product Owner | System 3* (requirements authority) | Prelim, A, B, H |
| Solution Architect | System 4 | A, B, C, H |
| Software Architect / Principal Engineer | System 3 | D, E, F, G, H |
| DevOps / Platform Engineer | System 1 | D, E, F, G |
| Implementing Developer | System 1 | G |
| QA Engineer | System 1 | E/F (planning), G (execution) |
| Project Manager | System 3 (coordinator/supervisor) | All (coordination) |
| Chief Safety & Compliance Officer | System 2 (regulator) | All phases (gate reviews) |

The Project Manager acts as the LangGraph supervisor node: it deliberates on what to do next, routes work to specialists, batches clarification requests for the user, evaluates phase-transition gates, and manages the sprint review workflow. It does not produce architecture artifacts — it coordinates their production.

Each agent's mandate, input/output contracts, entry-point behaviour, personality stance, and skill index are specified in `agents/<role>/AGENT.md`.

---

## Skills and ADM Phase Alignment

Each agent owns a set of skill files (`agents/<role>/skills/*.md`). A skill corresponds to a specific ADM phase or major capability — for example, the Solution Architect has skills for Phase A (Architecture Vision), Phase B (Business Architecture), Phase C (Application and Data Architecture), reverse architecture reconstruction (EP-G entry), and change management (Phase H).

Skills are the primary runtime delivery vehicle: when an agent is invoked, the orchestrator loads the relevant skill file and injects its instructions (steps, inputs, outputs, feedback loop, algedonic triggers) as the Layer 3 system prompt. Skills are authored at three complexity levels (`simple`, `standard`, `complex`) which govern their token budget. The skill loading and prompt assembly protocol is specified in `framework/agent-runtime-spec.md`.

A compact routing index of all agents and their skills is maintained in `framework/agent-index.md`.

---

## Workflows

### Forward SDLC (EP-0 cold start)

The standard greenfield flow: the user initiates a new engagement, the Project Manager runs the entry assessment, and the system executes ADM phases sequentially from Preliminary through Phase G, with gate evaluations at each transition. Sprints are time-boxed; artifacts are versioned and handed off through the event stream.

### Brownfield Onboarding (EP-G)

For existing codebases, the system enters at Phase G via a reverse architecture reconstruction workflow. Specialist agents scan the target repository (IaC, source structure, package manifests, configuration) and user-provided documents to infer and populate an ERP v2.0 architecture model. The user confirms inferred entities before they are committed. The result is a populated architecture repository that the system can then govern forward. The reverse architecture skills are in `agents/solution-architect/skills/` and `agents/software-architect/skills/`.

### Other Entry Points

Six additional entry points (EP-A through EP-H, excluding EP-0 and EP-G) handle mid-lifecycle starts — where the user arrives with existing artifacts, a requirements register, a completed design, or an in-flight change. Entry-point handling is specified in `framework/sdlc-entry-points.md` and in every `AGENT.md`.

### Change Management (Phase H)

The Solution Architect produces Change Records; the Project Manager handles intake and routing. Phase H can trigger a return to any earlier phase. The algedonic channel provides an immediate escalation path when a change has safety implications.

### Enterprise Promotion

Architecture entities developed within an engagement can be promoted to the enterprise repository for cross-engagement reuse, subject to Architecture Board review. The promotion procedure, ID assignment, and reference sweep are specified in `framework/repository-conventions.md §12`.

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
| `architecture-repository/` | Solution Architect |
| `technology-repository/` | Software Architect / PE |
| `project-repository/` | Project Manager |
| `safety-repository/` | CSCO |
| `delivery-repository/` | Implementing Developer (metadata only) |
| `qa-repository/` | QA Engineer |
| `devops-repository/` | DevOps / Platform Engineer |

Architecture entities follow the **Entity Registry Pattern v2.0**: one `.md` file per entity, organised by ArchiMate layer, with machine-readable YAML frontmatter. The `ModelRegistry` is built from these files at startup. Diagrams are PlantUML files authored by agents directly; the full catalog of diagram types, templates, and authoring conventions is in `framework/diagram-conventions.md`.

#### Diagram types produced

Agents produce four families of PlantUML diagram, each serving a distinct architectural purpose:

**ArchiMate layer diagrams** — the primary deliverable of the architecture phases. One diagram per layer, using PlantUML's `!include` macro system against a shared stereotype library (`_archimate-stereotypes.puml`) and a per-engagement macro file (`_macros.puml`) auto-generated from entity `§display ###archimate` blocks. Typical diagrams: Motivation (stakeholders, drivers, goals, principles), Strategy (capabilities, value streams), Business (actors, roles, processes, services), Application (components, interfaces, services, data objects), Technology (nodes, system software, infrastructure services). Connections between entities are rendered using ArchiMate relationship types (association, composition, realization, serving, assignment, influence, access).

**ER diagrams (via PlantUML class notation)** — used for domain model and data object specifications. Each entity's `§display ###er` block provides its class declaration and attribute list; connection files in `connections/er/` provide cardinality relationships. The resulting diagrams are the authoritative field-level specification for Pydantic models in `src/models/`. ER diagrams are scoped to persisted domain objects — transient runtime structures are excluded.

**Activity diagrams (BPMN-oriented)** — specify workflows and process logic. Used for sprint lifecycle sequences, ADM phase flows, and multi-party processes such as the CQ lifecycle, sprint review approval flow, and enterprise promotion procedure. Swim lanes divide responsibility by role (PM, Agent, User, EventStore). Decision diamonds map directly to LangGraph routing functions; action boxes map to node implementations. These diagrams are the binding specification for `src/orchestration/` code.

**Sequence diagrams** — specify runtime interaction protocols between system components. Used for the skill invocation loop (the core agent runtime sequence every developer must internalise), the CQ lifecycle (agent → EventStore → dashboard → user → agent), the sprint review flow, and reverse-architecture reconstruction. Participants map to Python classes or modules; each call maps to a method boundary.

**Use-case diagrams** — produced by the Product Owner and Solution Architect during Phases A and B to capture stakeholder interactions with the system and map them to capabilities and business services. Used as a communication artifact rather than a technical specification; typically accompanies the Architecture Vision and Requirements Register.

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

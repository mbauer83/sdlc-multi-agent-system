# SDLC Multi-Agent System — Claude Code Guide

## Project Overview

This project builds a multi-agent AI system operationalising the full Software Development Lifecycle through specialised Claude-based agents, each embodying a distinct professional role and equipped with role-specific skills scoped to the TOGAF ADM phases relevant to that role.

**Deployment model:** Clone one instance of this framework repository per software project. The framework instance lives separately from the target project's code repository. Framework files are never committed to the target project. The target project repo is configured in `engagements-config.yaml` (per-engagement `target-repository` field) and cloned locally to `engagements/<id>/target-repo/` (.gitignored).

## Repository Layout

```
framework/                       # Cross-cutting specifications (read these first)
  agile-adm-cadence.md           # Sprint structure, phase mapping, ADM iteration model, transition gates
  raci-matrix.md                 # Per-artifact, per-phase responsibility table
  repository-conventions.md      # Path governance, artifact versioning, handoff format, promotion
  algedonic-protocol.md          # Fast-path escalation specification
  clarification-protocol.md      # Knowledge adequacy and CQ lifecycle
  sdlc-entry-points.md           # Seven engagement entry points (EP-0 to EP-H)
  discovery-protocol.md          # Scan-first protocol: sources, inference rules, gap assessment, CQ generation
  architecture-repository-design.md  # Enterprise/Engagement/External scope model + EventStore
  artifact-schemas/              # One schema file per major handoff artifact

agents/<role>/                   # One directory per agent role
  AGENT.md                       # Mandate, constraints, input/output contracts, entry-point behaviour
  skills/                        # One .md skill file per phase or major capability

enterprise-repository/           # Organisation-wide architecture data (long-lived; Architecture Board governed)
  metamodel/                     # Framework decisions, governance procedures
  capability/                    # EA team structure, roles, tooling
  landscape/strategic/           # Enterprise-wide architecture
  landscape/segment/             # Domain/programme-level architecture
  landscape/capability/          # Promoted capability architectures
  standards/                     # SIB: approved technology standards and patterns
  reference-library/             # Reusable patterns, templates, reference models
  governance-log/                # Append-only cross-engagement governance records
  requirements/                  # Enterprise-level requirements
  solutions-landscape/           # Deployed/planned SBBs across the enterprise
  knowledge-base/                # Lessons learned, retrospectives
  diagram-catalog/               # Enterprise-scope element catalog (ontologically packaged; see diagram-conventions.md)
    elements/{motivation,business,application,technology,data}/
    connections/                 # ArchiMate, ER, sequence, BPMN relationships
    diagrams/                    # Enterprise-level .puml diagrams
    rendered/                    # SVG outputs; committed at sprint boundary

engagements/<id>/                # Per-engagement working directory
  engagement-profile.md          # Entry point, scope, warm-start status
  workflow.db                    # SQLite event store — canonical, git-tracked binary (NOT gitignored)
  workflow-events/               # YAML audit export — git-tracked; committed at sprint boundaries
  clarification-log/             # CQ records
  handoff-log/                   # Handoff event records
  algedonic-log/                 # Algedonic signal records
  work-repositories/
    architecture-repository/     # Owner: Solution Architect
      diagram-catalog/           # Engagement-scope element catalog; enterprise elements imported at bootstrap
        elements/{motivation,business,application,technology,data,sequences,processes}/
        connections/
        diagrams/                # Engagement .puml files; imported enterprise elements + project-specific
        rendered/                # SVG outputs; committed at sprint boundary
      business-architecture/_common/, <domain>/   # Phase B artifacts; domain-sliced if >1 bounded context
      application-architecture/_common/, <domain>/
      data-architecture/_common/, <domain>/
      architecture-vision/, technology-architecture/, principles/, decisions/, requirements/
    technology-repository/       # Owner: Software Architect / PE
    project-repository/          # Owner: Project Manager
    safety-repository/           # Owner: CSCO
    delivery-repository/         # Owner: Implementing Developer — delivery METADATA only (PRs, test reports, branch refs)
    qa-repository/               # Owner: QA Engineer
    devops-repository/           # Owner: DevOps / Platform Engineer

external-sources/                # Source adapter configs (Confluence, Jira, Git, etc.)
  <source-id>.config.yaml        # Read-only; agents never write to external sources

src/                             # Python implementation
  events/                        # EventStore + Pydantic v2 event models + Alembic migrations
  agents/                        # PydanticAI agent wrappers (one module per agent)
  orchestration/                 # Sprint runner, handoff event bus, CQ bus, algedonic handler
  sources/                       # External source adapters
  models/                        # Pydantic v2 artifact data models

enterprise-repository-config.yaml   # Enterprise repo mode: embedded | submodule | external
engagements-config.yaml             # Engagement mode: single-repo | multi-repo

tests/
  synthetic-project/             # End-to-end integration test scenario
```

## Authoring Rules

1. **Schemas before skills.** Never author a skill that produces or consumes an artifact whose schema does not yet exist in `framework/artifact-schemas/`.
2. **Framework files are the canonical reference.** Agent and skill files must be consistent with `agile-adm-cadence.md`, `raci-matrix.md`, `repository-conventions.md`, and `algedonic-protocol.md`. Update the framework first if you need to change a contract.
3. **Every skill file must have an `## Algedonic Triggers` section.** Explicit absence ("none identified") is a valid and required design decision.
4. **Every skill file must have a `## Knowledge Adequacy Check` section.** Specifies domain knowledge required, predictable gaps, and conditions requiring a CQ. Governed by `clarification-protocol.md`.
5. **Every AGENT.md must describe entry-point behaviour for all seven entry points.** Governed by `sdlc-entry-points.md`.
6. **Feedback loops must specify termination conditions.** Maximum iteration count and escalation path are required in every `## Feedback Loop` section.
7. **One accountable agent per artifact per phase.** Ambiguity must be resolved in `raci-matrix.md` before proceeding.
8. **No agent writes outside its designated engagement work-repository path.** Cross-role transfers occur through handoff events only. Enterprise repository writes require Architecture Board approval.
9. **All workflow events go through EventStore.** No agent accesses `workflow.db` directly via sqlite3. `workflow.db` is git-tracked (canonical event store); `workflow-events/*.yaml` are the human-readable projection also committed at sprint close.
10. **ADM iteration is non-linear.** Phases can be revisited. Skills must handle `trigger="revisit"` and `phase_visit_count > 1` cases explicitly. On revisit, preserve all non-affected content, update only sections affected by the triggering change, and increment the artifact version.
11. **Framework files never enter the target project repository.** The target project repo is a separate git repository configured per engagement in `engagements-config.yaml`. Source code lives only there. The engagement's `delivery-repository/` holds delivery metadata, not code.
12. **Discovery before CQs.** Every skill that begins phase work must execute the Discovery Scan (`framework/discovery-protocol.md §2`) as its first step. CQs are raised only for information that cannot be obtained from available sources (engagement state, enterprise repository, configured external sources, target-repo). Every inferred or sourced field must be annotated in the artifact. Governed by `framework/discovery-protocol.md`.
13. **Every AGENT.md must have a `## 11. Personality & Behavioral Stance` section.** Specifies the agent's role type (Integrator/Specialist/Framing/Coordinator), behavioral directives derived from the personality profile, conflict engagement posture, primary inter-role tensions, and a reference to `framework/agent-personalities.md`. Governed by `framework/agent-personalities.md`. Every skill file that involves significant cross-role interaction must include a `### Personality-Aware Conflict Engagement` subsection in its `## Feedback Loop` section (see `framework/agent-personalities.md §6`).
14. **Every AGENT.md and every skill file must have YAML frontmatter.** Frontmatter provides machine-readable routing metadata for the Python orchestration layer. AGENT.md required fields: `agent-id`, `name`, `display-name`, `role-type`, `vsm-position`, `primary-phases`, `invoke-when`, `owns-repository`, `personality-ref`, `skill-index`, `runtime-ref`, `system-prompt-identity`. The `system-prompt-identity` field is the compact static Layer 1 system prompt used by `build_agent()` in `src/agents/base.py` — 3–5 sentences covering: role name/abbreviation, authority domain, owned repository, one non-negotiable constraint. Skill file required fields: `skill-id`, `agent`, `name`, `invoke-when`, `trigger-phases`, `trigger-conditions` (LLM-hint prose; not machine-parsed), `entry-points`, `primary-outputs`, `complexity-class` (`simple | standard | complex` — governs SkillLoader token budget: ≤600/1200/2000). The `trigger-phases` list is the machine-readable routing key; `trigger-conditions` is documentation only. **Runtime extraction contract:** only two AGENT.md extractions reach the live agent — `system-prompt-identity` (Layer 1, always) and `### Runtime Behavioral Stance` from §11 (Layer 2, always). All other AGENT.md content is authoring documentation that governs skill file authoring — it does not reach the agent directly. Skill files (Inputs Required + Steps + Algedonic Triggers + Feedback Loop + Outputs, up to `complexity-class` budget) are the primary runtime delivery vehicle, injected as Layer 3 when the skill is invoked. Use `framework/agent-index.md` as the compact routing reference (~500 tokens). Governed by `framework/agent-runtime-spec.md`.
15. **Agent runtime and orchestration are governed by two framework specs.** `framework/agent-runtime-spec.md` — PydanticAI agent construction, 4-layer system prompt assembly, skill loading protocol, tool sets, agent-as-tool pattern. `framework/orchestration-topology.md` — LangGraph graph topology, `SDLCGraphState`, PM supervisor node, routing functions, EventStore integration. Every `src/agents/` and `src/orchestration/` file must implement these specs. Do not introduce coordination patterns that contradict them without updating the framework first.
16. **Diagram production follows `framework/diagram-conventions.md`.** Every skill that produces or updates an architecture artifact must follow the diagram conventions spec. The engagement catalog (`architecture-repository/diagram-catalog/`) uses an ontological package structure (motivation/, business/, application/, technology/, data/, sequences/, processes/). Enterprise elements are imported into the engagement catalog at bootstrap — they are not referenced in-place from the enterprise catalog. Element scope is structural (catalog location), not a naming convention. Before creating any new element, agents must scan the engagement catalog; SA must run the enterprise catalog import check at engagement bootstrap. The `extends:` field on an element provides explicit cross-catalog traceability. Governed by `framework/diagram-conventions.md` and `framework/artifact-schemas/diagram-catalog.schema.md`.
17. **Every AGENT.md must have an `## Artifact Discovery Priority` section.** Specifies the ordered list of repositories and document types the agent must scan during Discovery Scan Step 0, role-specific. Feeds the `read_artifact` tool's default search scope. Architects prioritize `architecture-repository/` then `technology-repository/`; DE and DO must list `technology-repository/coding-standards/` first. Required for all roles; critical for integrators and implementation agents. Governed by `framework/discovery-protocol.md §9` (Standards and Coding Guidelines Discovery).
18. **Artifact references use the canonical format from `framework/repository-conventions.md §13`.** Every handoff, work-spec, or skill output that cites another artifact must use `[@<artifact-id> v<N.N>](<relative-path>)` in-text and list cited artifact-ids in frontmatter `references:`. This enables cross-artifact dependency resolution by the orchestration layer and dashboard. Agents must never reference artifacts by filename alone.

## Implementation Stages (see `specs/IMPLEMENTATION_PLAN.md`)

| Stage | Scope | Status |
|---|---|---|
| 1 | Foundation artifacts (framework + schemas + EventStore skeleton + directory structure) | Complete |
| 2 | Project Manager master skill | Complete |
| 3 | Primary implementation chain (SA → SwA → DevOps → Dev → QA) + discovery-protocol.md | Complete |
| 4 | Framing layer (PO, Sales, CSCO) | Partial |
| 4.5 | Cross-cutting framework extensions (diagram conventions, artifact references, standards discovery, agent profile condensation) | Pending |
| 5 | Python implementation layer (EventStore completion + PydanticAI agents + LangGraph orchestration + source adapters) | Pending |
| 5.5 | Engagement dashboard (local web server + PUML rendering + filesystem monitoring) | Pending |
| 6 | Integration testing on synthetic project | Pending |

## Technology Stack

- Python 3.11+, Pydantic v2 (models, artifact schemas, event payloads)
- PydanticAI for agent definition and tool use
- Anthropic Claude API (claude-sonnet-4-6 for primary agents; claude-haiku-4-5 for routing/summarisation)
- LangGraph optional for complex stateful orchestration
- SQLite (per-engagement event store via EventStore class); Alembic for schema migrations
- File-based work-repositories (git-tracked) for artifact storage

## Commit Convention

Branch and tag names follow stage markers: `stage-1-foundation`, `stage-2-pm-master`, etc.

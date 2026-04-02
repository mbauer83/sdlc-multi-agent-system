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
  architecture-repository-design.md  # Enterprise/Engagement/External scope model + EventStore
  artifact-schemas/              # One schema file per major handoff artifact

agents/<role>/                   # One directory per agent role
  AGENT.md                       # Mandate, constraints, input/output contracts, entry-point behaviour
  skills/                        # One .md skill file per phase or major capability

enterprise-repository/           # Organisation-wide architecture data (long-lived)
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

engagements/<id>/                # Per-engagement working directory
  engagement-profile.md          # Entry point, scope, warm-start status
  workflow.db                    # SQLite event store — canonical, git-tracked binary (NOT gitignored)
  workflow-events/               # YAML audit export — git-tracked; committed at sprint boundaries
  clarification-log/             # CQ records
  handoff-log/                   # Handoff event records
  algedonic-log/                 # Algedonic signal records
  work-repositories/
    architecture-repository/     # Owner: Solution Architect
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
10. **ADM iteration is non-linear.** Phases can be revisited. Skills must handle `trigger="revisit"` and `phase_visit_count > 1` cases explicitly.
11. **Framework files never enter the target project repository.** The target project repo is a separate git repository configured per engagement in `engagements-config.yaml`. Source code lives only there. The engagement's `delivery-repository/` holds delivery metadata, not code.

## Implementation Stages (see `specs/IMPLEMENTATION_PLAN.md`)

| Stage | Scope | Status |
|---|---|---|
| 1 | Foundation artifacts (framework + schemas + EventStore skeleton + directory structure) | Complete |
| 2 | Project Manager master skill | Complete |
| 3 | Primary implementation chain (SA → SwA → DevOps → Dev → QA) | Pending |
| 4 | Framing layer (PO, Sales, CSCO) | Pending |
| 5 | Cross-cutting skills + PydanticAI wrappers + EventStore full implementation | Pending |
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

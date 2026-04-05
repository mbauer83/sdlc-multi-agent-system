# SDLC Multi-Agent System — Claude Code Guide

## Project Overview

This project builds a multi-agent AI system operationalising the full Software Development Lifecycle through specialised Claude-based agents, each embodying a distinct professional role and equipped with role-specific skills scoped to the TOGAF ADM phases relevant to that role.

**Deployment model:** Clone one instance of this framework repository per software project. The framework instance lives separately from the target project's code repositories. Framework files are never committed to any target project. Target repositories are configured in `engagements-config.yaml` under `target-repositories` (multi-repo list, preferred) or `target-repository` (single-repo, backward-compatible). Local clones live at `engagements/<id>/target-repos/<repo-id>/` (.gitignored). Multi-repo engagements (microservices, CQRS, microfrontends) are first-class: each registered repo has an `id`, `label`, `role`, and `domain`; one repo is designated `primary`. The Repository Map artifact (`REPO-MAP`) documents all repos and their inter-dependencies.

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

enterprise-repository/           # Organisation-wide architecture data (long-lived; Architecture Board members only write here)
  metamodel/                     # Framework decisions, governance procedures
  capability/                    # EA team structure, roles, tooling
  landscape/strategic/           # Enterprise-wide architecture
  landscape/segment/             # Domain/programme-level architecture
  landscape/capability/          # Promoted capability architectures
  standards/                     # SIB: approved technology standards and patterns
  reference-library/             # Reusable patterns, templates, reference models
  governance-log/                # Append-only cross-engagement governance records
    id-counters.yaml             # Global per-prefix entity ID counters; updated on every promotion
  requirements/                  # Enterprise-level requirements
  solutions-landscape/           # Deployed/planned SBBs across the enterprise
  knowledge-base/                # Lessons learned, retrospectives
  model-entities/                # Enterprise ArchiMate entity files (one .md per instance; ModelRegistry built from frontmatter)
    motivation/                  # Enterprise motivation entities: stakeholders, drivers, requirements, constraints, goals, principles
    strategy/                    # Enterprise strategy entities: capabilities, value-streams
    business/                    # Enterprise business layer entities: actors, roles, processes, functions, services, objects
    application/                 # Enterprise application layer entities: components, services, interfaces, data-objects
    technology/                  # Enterprise technology layer entities: nodes, system-software, tech-services
    implementation/              # Enterprise implementation entities: work-packages, plateaus, gaps
  connections/                   # Enterprise connection files: connections/<lang>/<type>/
  diagram-catalog/               # Enterprise diagrams; entity files live in model-entities/ above
    _macros.puml                 # Auto-generated from entity §display ###archimate blocks
    _archimate-stereotypes.puml  # ArchiMate skinparam + stereotype library
    diagrams/                    # Enterprise-level architecture views (.puml diagrams + matrix .md files)
    templates/                   # Blank per-type diagram stubs agents copy and adapt
    rendered/                    # SVG outputs; committed at sprint boundary

engagements/<id>/                # Per-engagement working directory
  engagement-profile.md          # Entry point, scope, warm-start status
  workflow.db                    # SQLite event store — canonical, git-tracked binary (NOT gitignored)
  workflow-events/               # YAML audit export — git-tracked; committed at sprint boundaries
  clarification-log/             # CQ records
  handoff-log/                   # Handoff event records
  algedonic-log/                 # Algedonic signal records
  work-repositories/
    architecture-repository/     # Co-owned: SA (motivation/strategy/business layers), SwA (application layer — Phase C)
      model-entities/            # ArchiMate entity files (one .md per instance; ModelRegistry built from frontmatter)
        motivation/              # Motivation entities: stakeholders, drivers, requirements, constraints, goals, principles
        strategy/                # Strategy entities: capabilities, value-streams
        business/                # Business layer entities: actors, roles, processes, functions, services, objects
        application/             # Application layer entities: components, services, interfaces, data-objects
        implementation/          # Implementation entities: work-packages, plateaus, gaps
      connections/               # Connection files: connections/<lang>/<type>/ (archimate/er/sequence/activity/usecase)
      diagram-catalog/           # Diagrams over the model
        _macros.puml             # Auto-generated from entity §display ###archimate blocks
        _archimate-stereotypes.puml
        diagrams/                # Engagement architecture views (.puml diagrams + matrix .md files)
        templates/               # Blank per-type diagram stubs agents copy and adapt
        rendered/                # SVG outputs; committed at sprint boundary
      decisions/                 # Architecture Decision Records
      overview/                  # Architecture Vision + high-level narrative docs
    technology-repository/       # Owner: Software Architect / PE
    project-repository/          # Owner: Project Manager
    safety-repository/           # Owner: CSCO
    architecture-repository/
      repository-map.md          # Required for multi-repo engagements (REPO-MAP artifact)
    delivery-repository/         # Owner: Implementing Developer — delivery METADATA only (PRs, test reports, branch refs)
      repos/<repo-id>/           # Per-target-repo subdirectory (multi-repo engagements)
    qa-repository/               # Owner: QA Engineer
    devops-repository/           # Owner: DevOps / Platform Engineer

external-sources/                # Source adapter configs (Confluence, Jira, Git, etc.)
  <source-id>.config.yaml        # Read-only; agents never write to external sources

src/                             # Python implementation
  events/                        # EventStore + Pydantic v2 event models + Alembic migrations
  agents/                        # PydanticAI agent wrappers (one module per agent)
    learning_store.py            # LangGraph BaseStore wrapper for agent learning memory
  orchestration/                 # Sprint runner, handoff event bus, CQ bus, algedonic handler
  sources/                       # External source adapters + TargetRepoManager (multi-repo)
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
8. **No agent writes outside its designated engagement work-repository path.** Cross-role transfers occur through handoff events only. The enterprise repository is written to exclusively by Architecture Board members; engagement agents have no write path to it (`RegistryReadOnlyError`).
9. **All workflow events go through EventStore.** No agent accesses `workflow.db` directly via sqlite3. `workflow.db` is git-tracked (canonical event store); `workflow-events/*.yaml` are the human-readable projection also committed at sprint close.
10. **ADM iteration is non-linear.** Phases can be revisited. Skills must handle `trigger="revisit"` and `phase_visit_count > 1` cases explicitly. On revisit, preserve all non-affected content, update only sections affected by the triggering change, and increment the artifact version.
11. **Framework files never enter the target project repository.** The target project repo is a separate git repository configured per engagement in `engagements-config.yaml`. Source code lives only there. The engagement's `delivery-repository/` holds delivery metadata, not code.
12. **Discovery before CQs.** Every skill that begins phase work must execute the Discovery Scan (`framework/discovery-protocol.md §2`) as its first step. Layers 1, 2, and 4 (engagement work-repos, enterprise repo, target repos) are always queried via `list_artifacts(**filter)` and `search_artifacts(query)` — never by walking directories. External sources (Layer 3) are queried situatively only (reverse architecture, user-referenced source, PM explicit instruction). CQs are raised only for information absent from all available sources. Every inferred or sourced field must be annotated. Governed by `framework/discovery-protocol.md`.
13. **Every AGENT.md must have a `## 11. Personality & Behavioral Stance` section.** Specifies the agent's role type (Integrator/Specialist/Framing/Coordinator), behavioral directives derived from the personality profile, conflict engagement posture, primary inter-role tensions, and a reference to `framework/agent-personalities.md`. Governed by `framework/agent-personalities.md`. Every skill file that involves significant cross-role interaction must include a `### Personality-Aware Conflict Engagement` subsection in its `## Feedback Loop` section (see `framework/agent-personalities.md §6`).
14. **Every AGENT.md and every skill file must have YAML frontmatter.** Frontmatter provides machine-readable routing metadata for the Python orchestration layer. AGENT.md required fields: `agent-id`, `name`, `display-name`, `role-type`, `vsm-position`, `primary-phases`, `invoke-when`, `owns-repository`, `personality-ref`, `skill-index`, `runtime-ref`, `system-prompt-identity`. The `system-prompt-identity` field is the compact static Layer 1 system prompt used by `build_agent()` in `src/agents/base.py` — 3–5 sentences covering: role name/abbreviation, authority domain, owned repository, one non-negotiable constraint. Skill file required fields: `skill-id`, `agent`, `name`, `invoke-when`, `trigger-phases`, `trigger-conditions` (LLM-hint prose; not machine-parsed), `entry-points`, `primary-outputs`, `complexity-class` (`simple | standard | complex` — governs SkillLoader token budget: ≤600/1200/2000). The `trigger-phases` list is the machine-readable routing key; `trigger-conditions` is documentation only. **Runtime extraction contract:** only two AGENT.md extractions reach the live agent — `system-prompt-identity` (Layer 1, always) and `### Runtime Behavioral Stance` from §11 (Layer 2, always). All other AGENT.md content is authoring documentation that governs skill file authoring — it does not reach the agent directly. Skill files (Inputs Required + Steps + Algedonic Triggers + Feedback Loop + Outputs, up to `complexity-class` budget) are the primary runtime delivery vehicle, injected as Layer 3 when the skill is invoked. Use `framework/agent-index.md` as the compact routing reference (~500 tokens). Governed by `framework/agent-runtime-spec.md`.
15. **Agent runtime and orchestration are governed by two framework specs.** `framework/agent-runtime-spec.md` — PydanticAI agent construction, 4-layer system prompt assembly, skill loading protocol, tool sets, agent-as-tool pattern. `framework/orchestration-topology.md` — LangGraph graph topology, `SDLCGraphState`, PM supervisor node, routing functions, EventStore integration. Every `src/agents/` and `src/orchestration/` file must implement these specs. Do not introduce coordination patterns that contradict them without updating the framework first.
16. **Model-entity registry (ERP v2.0) and diagram production follow `framework/artifact-registry-design.md` and `framework/diagram-conventions.md`.** All architecture entities and connections are individual `.md` files organised by ArchiMate layer/aspect (no `_index.yaml`; `ModelRegistry` built from frontmatter at startup). **Entity filenames follow `TYPEABBR-NNN.friendly-name.md`** — the formal artifact-id is the prefix before the first `.`; code must use `entity_id_from_path(path)` from `src/common/model_verifier.py` to extract it (never `Path.stem` directly). Connection filenames are the artifact-id itself (no friendly name). Entity files contain `<!-- §content -->` and `<!-- §display -->` sections; `§display` has `### <language-id>` H3 subsections per diagram language. Connection files typed in filesystem (`connections/<lang>/<type>/`). Entities may exist without appearing in any diagram (model-first); diagram elements must have a backing entity in ModelRegistry (violations → ALG-C03). Engagement artifact-IDs are engagement-local; enterprise IDs are globally unique (assigned from `enterprise-repository/governance-log/id-counters.yaml` at promotion). Enterprise entities are read-only to engagement agents; Architecture Board members maintain them. Diagrams carry frontmatter in a PUML header comment block (no `index.yaml`); agents read `.puml` source directly for both local and enterprise diagrams — `render_diagram` is for user-facing output only. SA runs `regenerate_macros()` at bootstrap; no entity import step exists. Governed by `framework/artifact-registry-design.md`, `framework/diagram-conventions.md`, and `framework/artifact-schemas/entity-conventions.md`.
17. **Every AGENT.md must have an `## Artifact Discovery Priority` section.** Specifies the ordered list of repositories and document types the agent must scan during Discovery Scan Step 0, role-specific. Feeds the `read_artifact` tool's default search scope. Architects prioritize `architecture-repository/` then `technology-repository/`; DE and DO must list `technology-repository/coding-standards/` first. Required for all roles; critical for integrators and implementation agents. Governed by `framework/discovery-protocol.md §9` (Standards and Coding Guidelines Discovery).
18. **Artifact references use the canonical format from `framework/repository-conventions.md §13`.** Every handoff, work-spec, or skill output that cites another artifact must use `[@<artifact-id> v<N.N>](<relative-path>)` in-text and list cited artifact-ids in frontmatter `references:`. This enables cross-artifact dependency resolution by the orchestration layer and dashboard. Agents must never reference artifacts by filename alone.
20. **All Python implementation (`src/`) must follow the coding standards and domain-centred architecture defined in `specs/IMPLEMENTATION_PLAN.md §Python Coding Standards`.** Key rules: mandatory type annotations on all signatures; lowercase built-in collection aliases (`list[str]`, `x | y`) not superseded `typing` uppercase imports; inline type parameter syntax (`def f[T](...)`; PEP 695, Python 3.12+) — explicit `TypeVar` only when variance cannot be inferred; `Protocol` for structural subtyping; monadic `Result`-style error handling instead of exceptions for expected failures; no magic. Architecture: four-layer model (Common → Domain → Application → Infrastructure) with strict inward dependency rule; `src/common/` for cross-cutting concerns (logging, validation, parsing, normalisation) usable by all layers; ports-and-adapters for all I/O; domain Pydantic models are the single source of truth.

21. **Stage 4.9 entity/connection/diagram files are living implementation specifications.** They will change as Stage 5 implementation proceeds — this is expected and correct. The model-first discipline applies in both directions: (a) forward implementation — code divergences update entity/connection files first, then code; (b) reverse architecture — SA-REV and SWA-REV skills write entity files first, then diagrams follow. Requirements and constraints (REQ, CST, PRI) are updated when implementation reveals revision needs. Every Stage 5 deviation from a Stage 4.9 entity must update the entity file before the code change lands.

22. **All workflow events are event-sourced; emitter responsibility follows a three-layer hierarchy.** (1) Orchestration layer (LangGraph nodes + EngagementSession) emits lifecycle events: `engagement.started`, `sprint.started/close`, `phase.entered/transitioned/suspended/resumed`, `specialist.completed`, `review.sprint-closed`, `engagement.completed`. Each node receives `event_store: EventStorePort` directly. (2) PM agent tools emit decision events: `specialist.invoked`, `gate.evaluated`, `cq.batched`, `decision.recorded`, `review.pending`. (3) Specialist agent tools emit artifact/interaction events: `artifact.created/updated`, `handoff.created`, `cq.raised`, `algedonic.raised`, `source.scanned`, `entity.confirmed`, `file.referenced` — all tool-transparent; no skill instruction required. EventStore snapshots mandatory; situative triggers at `engagement.started`, `gate.evaluated/passed`, `sprint.close`; periodic every 100 events. Full taxonomy in `specs/IMPLEMENTATION_PLAN.md §4.9h` and §5a.

19. **Every skill file's `## Feedback Loop` must include a `### Learning Generation` subsection.**

23. **Run `ModelVerifier` after creating or modifying any entity, connection, or diagram file.** `src/common/model_verifier.py` provides `ModelVerifier.verify_entity_file()`, `verify_connection_file()`, and `verify_diagram_file()` (and `verify_all()` for batch scans). Run via `uv run python -c "from pathlib import Path; from src.common.model_verifier import ModelRegistry, ModelVerifier; repo=Path('engagements/ENG-001/work-repositories/architecture-repository'); v=ModelVerifier(ModelRegistry(repo)); results=v.verify_all(repo); errors=[(r.path.name,e.code,e.message) for r in results for e in r.errors]; print(f'{len(results)} files, {len(errors)} errors'); [print(x) for x in errors]"`. BDD tests in `tests/model/` cover all validation rules; run with `uv run pytest tests/model/`. The verifier is designed for Stage 5 `write_artifact` tool integration — its `ModelRegistry` interface matches the full Stage 5 registry. Specifies: which §3.1/§3.2 trigger conditions apply to this skill, the default `error-type`, the `importance` floor, and the `applicability` default. Governs when and what the agent records after a feedback cycle. The `artifact-type` in every learning entry is the PRIMARY OUTPUT artifact of the skill (what's being produced), not any input artifact reviewed or consumed — this is what makes `query_learnings` retrieval work correctly. Governed by `framework/learning-protocol.md §8` and `framework/artifact-schemas/learning-entry.schema.md`. The Discovery Scan for every skill must include Step 0.L (Learnings Lookup) before Layer 1. Governed by `framework/discovery-protocol.md §2` and `§10`.

24. **Tool-use in AGENT.md/skill markdown is intent guidance; runtime binding is code-owned.** Framework and agent/skill docs must describe *what kind* of tool action is required (discovery, filtering, querying, validation, model-write) but must not be treated as the runtime contract for concrete tool signatures. Concrete tool registration, names, argument schemas, and compatibility aliases are implemented in code via LangGraph + PydanticAI wiring (`src/agents/`, `src/orchestration/`, `src/tools/mcp_model_server.py`, `src/tools/model_mcp/`, `src/tools/model_write/`). Keep docs consistent with that code, and prefer documenting capability-level hints plus canonical mapping references.

25. **Keep per-agent search-space intentionally small (skills + tools) and document runtime load scope explicitly.** Skill inventories stay role-scoped and small (target <=12 skills per role); only one skill is injected at runtime via `active_skill_id` (Layer 3), with Layer 1/2 limited to `system-prompt-identity` and `### Runtime Behavioral Stance`. Tool surfaces are role-scoped and grouped by capability; keep per-agent callable tool exposure <=30 (preferred 12-26). If growth pressures exceed these limits, split skills by trigger/phase or consolidate tool families before adding new top-level tools. Governed by `framework/agent-runtime-spec.md`.

26. **Separate reusable skill intent from workflow-executable control logic.** Skill files should remain strict about outputs, quality checks, and domain procedure, but phase-gate execution logic (state transitions, dependency gating, retries, suspension/resume criteria) is owned by orchestration code and PM routing policies. Keep `invoke-when` / `trigger-conditions` as intent-level routing hints and documentation, not as the sole executable gate contract. Governed by `framework/agent-runtime-spec.md` and `framework/orchestration-topology.md`.

27. **Business operational decomposition diagrams use nested parent containers by default.** For staged business behavior in operational ArchiMate diagrams, the parent `BPR-NNN` / `BIA-NNN` element is the container and stage behaviors are nested within it, connected by internal `flow`/`triggering` lines. Do not model outer grouping wrappers with duplicated parent nodes. Keep parent→stage `archimate-composition` files in `connections/archimate/composition/` as model truth even when external composition arrows are omitted in the operational diagram. Governed by `framework/diagram-conventions.md §7.archimate-business-operational` and `§11.9.1a`.
28. **Representation choice must remain balanced: diagrams for context, matrices for dense mapping.** Matrix artifacts are first-class in `diagram-catalog/diagrams/*.md`, but they do not replace contextual diagrams. Use diagrams when topology, flow, sequence, or architectural narrative is required; use matrices when high-cardinality coverage and traceability are primary. Governed by `framework/diagram-conventions.md` and `framework/agent-runtime-spec.md`.

## End-of-Session Checklist

At the end of any work session — regardless of scope — complete all of the following before finishing:

1. **`specs/IMPLEMENTATION_PLAN.md`** — tick completed checklist items, update the "Current State & Immediate Next Actions" section, add any new design decisions resolved.
2. **`CLAUDE.md`** — update the Implementation Stages table status column; update any authoring rules or repository layout notes that changed.
3. **`README.md`** — update the Agent Roles table, Work Repositories table, Skills description, implementation status section, and any workflow sections that reflect the current state of the system.
4. **Model and diagram verification** — run `ModelVerifier.verify_all()` and confirm 0 errors. Re-render any modified diagrams with `java -jar tools/plantuml.jar -tsvg -o rendered/ diagrams/*.puml`. Commit both the corrected source and the updated SVGs.

These files are the canonical orientation documents. If they drift from reality, the next session starts with a false picture of the system.

---

## Implementation Stages (see `specs/IMPLEMENTATION_PLAN.md`)

| Stage | Scope | Status |
|---|---|---|
| 1 | Foundation artifacts (framework + schemas + EventStore skeleton + directory structure) | Complete |
| 2 | Project Manager master skill | Complete |
| 3 | Primary implementation chain (SA → SwA → DevOps → Dev → QA) + discovery-protocol.md | Complete |
| 4 | Framing layer (PO, Sales, CSCO) | Complete |
| 4.5 | Cross-cutting framework extensions (diagram conventions incl. balanced diagram-vs-matrix guidance, artifact references, standards discovery, agent profile condensation) | Complete |
| 4.6 | Learning protocol (agent learnings from mistakes — generation, retrieval, synthesis, promotion) | Complete |
| 4.6d | Learning protocol 2026 alignment (LangGraph BaseStore, semantic tier, graph connectivity, cross-agent visibility) | Complete |
| 4.7 | Multi-target-repository support (repository-map schema, multi-repo config, discovery Layer 4 update) | Complete |
| 4.8 | Entity Registry Pattern v2.0 (ERP): artifact-registry-design, entity-conventions, diagram-conventions; 4.8a–c/e/f complete; 4.8d complete; 4.8g pending; 4.8h (SA/SwA role boundary refactor) complete — ArchiMate layer = role boundary; Phase H split (SA business layer CR, SwA application/technology CR); Phase C primary=SwA | Partial |
| 4.9 | ENG-001 reference model: 4.9a–e complete; 4.9f partial — 4/7 diagrams done; ENG-001 business-layer rework required (§11.9 guidelines now in framework): VS stage updates, BFN/BEV/BOB/BIA entities, new connections, structural+operational diagrams, application diagram update | Partial |
| 5 | Python implementation layer (EventStore completion + PydanticAI agents + LangGraph orchestration + source adapters); `pyproject.toml` + uv project setup complete; `src/common/model_verifier.py` complete (71 BDD tests, E306/E307 draft-reference checks, `entity_status()`/`connection_status()` targeted lookups, E104 filename check, `entity_id_from_path()`); `src/common/archimate_types.py` canonical type registry; `src/common/model_query.py` complete — `ModelRepository` with `list_artifacts`/`search_artifacts`/`read_artifact` API, keyword+synonym search, graph traversal, `SemanticSearchProvider` Protocol, CLI (36 BDD tests); `src/common/domain_vocabulary.py` — canonical SDLC/ArchiMate synonym map | Partial |
| 5.5 | Engagement dashboard (local web server + PUML rendering + filesystem monitoring) | Pending |
| 6 | Integration testing on synthetic project | Pending |

## Technology Stack

- Python 3.12+, Pydantic v2 (models, artifact schemas, event payloads) — 3.12 required for PEP 695 inline type parameters
- PydanticAI for agent definition and tool use
- Anthropic Claude API (claude-sonnet-4-6 for primary agents; claude-haiku-4-5 for routing/summarisation)
- LangGraph optional for complex stateful orchestration
- SQLite (per-engagement event store via EventStore class); Alembic for schema migrations
- File-based work-repositories (git-tracked) for artifact storage

## Commit Convention

Branch and tag names follow stage markers: `stage-1-foundation`, `stage-2-pm-master`, etc.

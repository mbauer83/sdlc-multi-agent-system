---
name: SDLC Multi-Agent System — Project State
description: Current implementation stage, completed work, and what to resume next
type: project
---

**Stages 1–4.9d complete as of 2026-04-04.**

## Completed Stages

**Stage 1** — Foundation: framework files, artifact schemas, EventStore skeleton, directory structure, engagements/ENG-001, enterprise-repository/, external-sources/, src/events/.

**Stage 2** — Project Manager: AGENT.md + 6 skill files (master-agile-adm, phase-a, phase-e-f, phase-g, phase-h, retrospective-knowledge-capture).

**Stage 3** — Primary implementation chain: SA (6 skills), SwA (5 skills), DevOps (4 skills), DE (3 skills), QA (3 skills) + `framework/discovery-protocol.md`.

**Pre-Stage-4 additions** — Personality framework: `framework/agent-personalities.md`, §11 personality sections on all AGENT.md files, YAML frontmatter, `framework/agent-index.md`, `framework/agent-runtime-spec.md`, `framework/orchestration-topology.md`.

**Stage 4** — Framing layer: PO (AGENT.md + 5 skills), SM (AGENT.md + 3 skills), CSCO (AGENT.md + 7 skills). `framework/agent-index.md` updated.

**Stage 4.5** — Cross-cutting framework extensions:
- `framework/diagram-conventions.md` — PUML conventions, ontological catalog structure, D1–D6 protocol, 6 PUML templates, _macros.puml spec
- `framework/artifact-schemas/diagram-catalog.schema.md`
- `framework/repository-conventions.md §13` — canonical artifact reference format
- `framework/discovery-protocol.md §8` (Step 0.D) and `§9` (Step 0.S standards discovery)
- `framework/agent-runtime-spec.md §2` — Layer 2 = `### Runtime Behavioral Stance`
- `framework/algedonic-protocol.md` — ALG-C01 through ALG-C04 added
- All 9 AGENT.md files: `### Runtime Behavioral Stance` + `## Artifact Discovery Priority` + `complexity-class:`

**Stage 4.5f** — Diagram D1–D6 steps retroactively added to SA phase-b, SA phase-c-application, SA phase-c-data, SwA phase-d, SwA phase-e.

**Stage 4.6a** — Learning protocol framework: `framework/learning-protocol.md` + `framework/artifact-schemas/learning-entry.schema.md`.

**Stage 4.6b** — Retroactive skill patches: Step 0.L (Learnings Lookup) + `### Learning Generation` added to all 43 skill files. Learning Synthesis step added to PM retrospective.

**Stage 4.6d** — Learning protocol 2026 alignment: LangGraph BaseStore, sqlite-vec semantic tier, cross-agent visibility via PM cross-role-learnings/ index, A-MEM graph links.

**Stage 4.7** — Multi-target-repository support: repository-map.schema.md; multi-repo config format; discovery-protocol.md Layer 4 update.

**Stage 4.8 (partial):**

- **4.8a–h Complete** — ERP v2.0 full spec, entity conventions, diagram conventions, CLAUDE.md authoring rules, reverse architecture skills, domain artifact schemas, SA/SwA role boundary refactor. See prior session notes for full detail.

## Stage 4.9 — ENG-001 Architecture Model (In Progress)

**4.9a Complete** — ERP directory structure created at `engagements/ENG-001/work-repositories/architecture-repository/`; `_archimate-stereotypes.puml` stub with official ArchiMate 3 layer colors:
- Motivation: `#EDD6F0` (light lavender purple)
- Strategy: `#F5DEB3` (wheat/tan)
- Business: `#FFFAC8` (warm yellow)
- Application: `#CCF2FF` (light cyan)
- Technology: `#CCFFCC` (light green)
- Physical: `#FFE0B2` (light orange)
- Implementation: `#FFE4C4` (bisque)

No `index.yaml` files anywhere — ERP v2.0 uses frontmatter only; ModelRegistry and DiagramCatalog built from file scans at startup.

Entity files live under `model-entities/<layer>/<type>/` (e.g., `model-entities/motivation/stakeholders/STK-001.md`) per `artifact-registry-design.md §2.1`.

**4.9b Complete** — 25 motivation and strategy entity files authored:
- Stakeholders: STK-001 (User/Engagement Owner), STK-002 (Architecture Board)
- Drivers: DRV-001 (SDLC Execution Cost), DRV-002 (Architecture Documentation Debt)
- Goals: GOL-001 (Full ADM Phase Coverage), GOL-002 (End-to-End Traceability), GOL-003 (Safety-by-Default)
- Requirements: REQ-001 (Multi-Agent Coordination), REQ-002 (Human-in-the-Loop), REQ-003 (Brownfield Support), REQ-004 (Resumable State), REQ-005 (Agent Learning)
- Constraints: CST-001 (No Framework Lock-In), CST-002 (Local-Only Runtime)
- Principles: PRI-001 (Domain-Centric Layering), PRI-002 (EventStore Primacy), PRI-003 (Model-First)
- Capabilities: CAP-001–006 (Phase Execution, Artifact Production, Multi-Agent Orchestration, Knowledge Retention, User Interaction, Reverse Architecture)
- Value Streams: VS-001 (Forward SDLC), VS-002 (Brownfield Onboarding)

**4.9c Complete** — 28 business layer entity files authored:
- Actors: ACT-001–011 (User, PM, SA, SwA, DevOps, DE, QA, PO, SM, CSCO, Architecture Board)
- Processes: BPR-001–008 (Sprint Planning, Skill Execution, CQ Lifecycle, Gate Evaluation, Algedonic Escalation [safety-relevant: true], Sprint Review, Enterprise Promotion, Reverse Architecture)
- Services: BSV-001–009 (Business Architecture, App&Tech Architecture, Project Coordination, Safety Governance, Requirements Management, Code Delivery, Quality Assurance, Platform Engineering, User Decisions)

**4.9d Complete** — 46 application layer entity files authored:
- APP-001–022 (components: EventStore, ModelRegistry, LearningStore, SkillLoader, AgentFactory, AgentRegistry, 9 agent instances, LangGraph Orchestrator, EngagementSession, UserInteractionOrchestrator, PromotionOrchestrator, DashboardServer, UserInputGateway [renamed from InteractionHandler], TargetRepoManager)
- AIF-001–006 (interfaces/ports: EventStorePort, LLMClientPort, SourceAdapterPort, ArtifactReadWriterPort, DiagramToolsPort, LearningStorePort)
- ASV-001–005 (services: Agent Invocation, Artifact I/O, Sprint Review, CQ Management, Learning)
- DOB-001–013 (data objects: WorkflowEvent, Engagement, LearningEntry, ClarificationRequest, AlgedonicSignal, HandoffRecord, GateOutcome, ReviewItem, WorkflowState, AgentDeps, PMDecision, SDLCGraphState, ArtifactRecord)

All entities have §content + §display ###archimate blocks. DOB entities additionally have ###er blocks with field lists.

**Naming decision**: APP-021 renamed from `InteractionHandler` to `UserInputGateway` — "gateway" (ports-and-adapters entry point) + "UserInput" (write-side user submissions) is more specific and self-explanatory than "handler".

## Next: Stage 4.9e

Connection files (~50 files across archimate/realization, serving, assignment, composition, access; er/one-to-many). Each is a `.md` with frontmatter + §content + §display ###archimate. Then 4.9f (7 PUML diagrams), 4.9g (overview docs + ADRs), then Stage 5 Python implementation.

## Key Architectural Decisions

1. **ModelRegistry replaces `_index.yaml`**: in-process lookup built from frontmatter at startup; never persisted; per-EngagementSession scope covering all work-repositories + enterprise (read-only paths).
2. **Two-scope ID spaces**: engagement IDs (`CAP-001` etc.) are local-only; enterprise IDs globally unique assigned from `id-counters.yaml` at promotion time. `promote_entity` performs a deterministic reference sweep (old → new ID) before moving the file.
3. **Architecture Board members are the only enterprise-repo writers.** Engagement agents get `RegistryReadOnlyError` on any write attempt to enterprise paths.
4. **No entity import at bootstrap**: enterprise entities visible via unified ModelRegistry (read-only paths); no file copying.
5. **Diagrams carry frontmatter in PUML header comment blocks** — no index.yaml for diagrams.
6. **Model-first**: entities/connections may exist without diagrams; diagram elements must have a backing entity (violations → ALG-C03). Reverse architecture skills enforce this: entities first, then optionally diagrams.
7. **ArchiMate layer = role boundary**: SA owns Motivation/Strategy/Business layers; SwA owns Application/Technology layers.
8. Layer 2 system prompt = `### Runtime Behavioral Stance` (independently authored, ≤350 tokens).
9. `workflow.db` (SQLite) is git-tracked as the canonical event store.
10. Multi-repo: `target-repositories` (plural) preferred; `target-repository` backward-compat.
11. Learning store: LangGraph BaseStore at runtime; files are durable serialisation; sqlite-vec semantic tier optional.

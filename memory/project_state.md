---
name: SDLC Multi-Agent System — Project State
description: Current implementation stage, completed work, and what to resume next
type: project
---

**Stages 1–4.7 complete + Stage 4.8 substantially complete as of 2026-04-04.**

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

- **4.8a Complete** — `framework/artifact-registry-design.md` v2.0.0: ERP master spec, ArchiMate-organised entity directories, ModelRegistry, §content/§display file format, connection type registry, model-first rule, tool contracts. **Plus:** two-scope ID design — engagement IDs are local-only; enterprise IDs globally unique from `enterprise-repository/governance-log/id-counters.yaml` assigned at promotion; `promote_entity` does reference sweep then moves file; Architecture Board members are the only enterprise-repo writers.

- **4.8b Complete** — `framework/artifact-schemas/entity-conventions.md` v2.0.0: unified frontmatter schema (no `references`, no `diagram-element-id`), §content/§display structure, properties tables per ArchiMate type, five exemplar files.

- **4.8c Complete** — `framework/diagram-conventions.md` v2.0.0: no elements/ subdir, _macros.puml from §display blocks, artifact-ids as PUML aliases, D1–D5 protocol, ER tools. **Plus:** diagram referencing design — existing diagrams referenced in-place via `entry_type: reference` in `diagrams/index.yaml`; never copied; bootstrap has no entity import step.

- **4.8e Complete** — CLAUDE.md updated: ERP authoring rules, repository layout, stages table.

- **4.8f Complete (2026-04-03)** — Reverse architecture skills (3 files): SA-REV-PRELIM-A, SA-REV-BA, SWA-REV-TA. See below.

- **4.8d Pending** — Domain artifact schemas + cross-cutting framework doc updates (discovery-protocol, agent-runtime-spec, skill file retroactive patches).

## Stage 4.8f — Reverse Architecture Skills (New)

Three EP-G warm-start skill files authored:

1. `agents/solution-architect/skills/reverse-architecture-bprelim-a.md` (SA-REV-PRELIM-A, complexity: complex)
   - Reconstructs Prelim/Phase A motivation and strategy entities from user input, docs, target repos, external sources
   - Entity types: STK, DRV, ASS, GOL, PRI, REQ, CST, CAP, VS, RES
   - Key steps: discovery scan → batched user context query → entity inference → 2-iteration user confirmation → write entity files → write connections → produce Architecture Vision overview → CQs/handoffs
   - ALG-REV-001: new signal for unknown safety classification blocking reconstruction

2. `agents/solution-architect/skills/reverse-architecture-ba.md` (SA-REV-BA, complexity: complex)
   - Reconstructs Phase B business layer entities from codebase domain decomposition + user docs
   - Entity types: ACT, ROL, BPR, BFN, BSV, BEV, BOB, BIF, BCO, PRD
   - Key codebase evidence: package structure, controller/service/repository class naming, RBAC config, API specs, event bus topics, DB schemas
   - Flags safety-relevant processes; handoffs to CSCO

3. `agents/software-architect/skills/reverse-architecture-ta.md` (SWA-REV-TA, complexity: complex)
   - Reconstructs Phase D/E technology layer from IaC, Dockerfiles, CI/CD, package manifests
   - Entity types: NOD, DEV, SSW, TSV, ART, NET, TFN, TEV, TIF
   - Also authors ADR stubs (status: reconstructed) for all major technology selections
   - Gap & Risk Assessment: lifecycle, security, SIB deviation, ADR coverage
   - ALG-REV-SEC: new signal for plaintext credentials / missing TLS in production

All three skills registered in SA/SwA AGENT.md §8 skill indexes and `framework/agent-index.md`.

## Key Architectural Decisions

1. **ModelRegistry replaces `_index.yaml`**: in-process lookup built from frontmatter at startup; never persisted; per-EngagementSession scope covering all work-repositories + enterprise (read-only paths).
2. **Two-scope ID spaces**: engagement IDs (`CAP-001` etc.) are local-only; enterprise IDs globally unique assigned from `id-counters.yaml` at promotion time. `promote_entity` performs a deterministic reference sweep (old → new ID) before moving the file.
3. **Architecture Board members are the only enterprise-repo writers.** Engagement agents get `RegistryReadOnlyError` on any write attempt to enterprise paths.
4. **No entity import at bootstrap**: enterprise entities visible via unified ModelRegistry (read-only paths); no file copying.
5. **Diagrams referenced not copied**: existing enterprise/prior-engagement diagrams in `diagrams/index.yaml` as `entry_type: reference`; `render_diagram` renders in place at source path.
6. **Model-first**: entities/connections may exist without diagrams; diagram elements must have a backing entity (violations → ALG-C03). Reverse architecture skills enforce this: entities first, then optionally diagrams.
7. Diagram catalog organized by ontological layer; vertical domain slicing at artifact level only.
8. Layer 2 system prompt = `### Runtime Behavioral Stance` (independently authored, ≤350 tokens).
9. `workflow.db` (SQLite) is git-tracked as the canonical event store.
10. Multi-repo: `target-repositories` (plural) preferred; `target-repository` backward-compat.
11. Learning store: LangGraph BaseStore at runtime; files are durable serialisation; sqlite-vec semantic tier optional.

## Runtime Extraction Contract

- Layer 1: `system-prompt-identity` frontmatter (≤150 tokens, always)
- Layer 2: `### Runtime Behavioral Stance` in §11 (≤350 tokens, always)
- Layer 3: full skill file up to complexity-class budget (≤600/1200/2000)
- Layer 4: on-demand via `read_artifact` tool

## Stage 4.8d — Complete (2026-04-03)

Domain artifact schemas and cross-cutting framework docs updated for ERP v2.0 (see IMPLEMENTATION_PLAN.md §4.8d for full detail).

## Stage 4.8h — Substantially Complete (2026-04-04)

SA/SwA role boundary refactored. The ArchiMate layer boundary is now the role boundary:
- **SA** owns Motivation, Strategy, Business layers (primary-phases: A, B, H). Phase C is consulting (traceability review).
- **SwA** owns Application and Technology layers (primary-phases: C, D, E, F, G, H app/tech).
- `architecture-repository/` co-owned: SA writes motivation/strategy/business/implementation; SwA writes application/ (Phase C entities: APP, IFC, ASV, DOB).

**Completed in this stage:**
- framework/raci-matrix.md: Phase B (SwA ○ added), Phase C (SA● → SwA●, SwA○ → SA○)
- agents/solution-architect/AGENT.md v1.1.0: primary-phases [A,B,H], consulting C
- agents/software-architect/AGENT.md v1.1.0: primary-phases [C,D,E,F,G], entry-points include EP-C
- SA phase-c-application.md → SA-PHASE-C-APP-REVIEW (consulting traceability skill)
- SA phase-c-data.md → SA-PHASE-C-DATA-REVIEW (consulting traceability skill)
- NEW SwA phase-c-application.md (SwA-PHASE-C-APP — primary Phase C application skill)
- NEW SwA phase-c-data.md (SwA-PHASE-C-DATA — primary Phase C data skill)
- SwA phase-d.md inputs: AA/DA now self-produced (no SA handoff)
- agents/csco/skills/gate-phase-c.md: SA → SwA as coordination partner
- framework/artifact-schemas/application-architecture.schema.md v2.1.0: Owner → SwA
- framework/artifact-schemas/data-architecture.schema.md v2.1.0: Owner → SwA
- CLAUDE.md: agent phase table, architecture-repository ownership note
- specs/IMPLEMENTATION_PLAN.md: agent roles table, repository ownership, ACT/APP/BSV descriptions, 4.8h checklist

**Deferred (before Stage 5 Python):**
- SA phase-h.md: scope to business/motivation/strategy layer only
- SwA phase-h.md: expand to cover application/technology layer CR authoring
- framework/agile-adm-cadence.md: Phase C primary agent
- framework/agent-index.md: SA/SwA routing tables
- framework/repository-conventions.md §2.2: Phase C path governance
- framework/artifact-registry-design.md: application-layer entity type owner annotations
- framework/discovery-protocol.md: SA/SwA scan priority order

## Next: Stage 4.9

ENG-001 reference model — now unblocked. Produce motivation/strategy/business entities (SA) and application/data entities (SwA) for ENG-001. Then Stage 5 Python implementation.

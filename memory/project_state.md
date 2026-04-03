---
name: SDLC Multi-Agent System — Project State
description: Current implementation stage, completed work, and what to resume next
type: project
---

**All stages through 4.6b are complete as of 2026-04-03.**

## Completed Stages

**Stage 1** — Foundation: framework files, artifact schemas, EventStore skeleton, directory structure, engagements/ENG-001, enterprise-repository/, external-sources/, src/events/.

**Stage 2** — Project Manager: AGENT.md + 6 skill files (master-agile-adm, phase-a, phase-e-f, phase-g, phase-h, retrospective-knowledge-capture).

**Stage 3** — Primary implementation chain: SA (6 skills), SwA (5 skills), DevOps (4 skills), DE (3 skills), QA (3 skills) + `framework/discovery-protocol.md`.

**Pre-Stage-4 additions** — Personality framework: `framework/agent-personalities.md`, §11 personality sections on all AGENT.md files, YAML frontmatter, `framework/agent-index.md`, `framework/agent-runtime-spec.md`, `framework/orchestration-topology.md`.

**Stage 4** — Framing layer: PO (AGENT.md + 5 skills), SM (AGENT.md + 3 skills), CSCO (AGENT.md + 7 skills: stamp-stpa-methodology, gate-phase-a through gate-phase-d, gate-phase-g, gate-phase-h, incident-response). `framework/agent-index.md` updated with PO/SM/CSCO skill routing tables.

**Stage 4.5** — Cross-cutting framework extensions:
- `framework/diagram-conventions.md` — PUML conventions, ontological catalog structure, D1–D6 protocol, 6 PUML templates, _macros.puml spec
- `framework/artifact-schemas/diagram-catalog.schema.md`
- `framework/repository-conventions.md §13` — canonical artifact reference format
- `framework/discovery-protocol.md §8` (Step 0.D diagram catalog lookup) and `§9` (Step 0.S standards discovery)
- `framework/agent-runtime-spec.md §2` — Layer 2 = `### Runtime Behavioral Stance` (independently authored, ≤350 tokens)
- `framework/algedonic-protocol.md` — ALG-C01 through ALG-C04 added (diagram catalog violations)
- All 9 AGENT.md files: `### Runtime Behavioral Stance` + `## Artifact Discovery Priority` + `complexity-class:` on all skill frontmatter

**Stage 4.5f** — Diagram D1–D6 steps retroactively added to SA phase-b (3 steps), SA phase-c-application (2 steps), SA phase-c-data (1 step), SwA phase-d (Step 0.D + 2 diagram steps), SwA phase-e (1 diagram step).

**Stage 4.6a** — Learning protocol framework: `framework/learning-protocol.md` + `framework/artifact-schemas/learning-entry.schema.md`.

**Stage 4.6b** — Retroactive skill patches: Step 0.L (Learnings Lookup) + `### Learning Generation` added to all 43 skill files. Learning Synthesis step added to PM retrospective.

**Learning protocol clarification (2026-04-03):** `artifact-type` on a learning entry = the PRIMARY OUTPUT artifact of the skill when the mistake occurred, NOT the input artifact reviewed/consumed. This ensures `query_learnings(artifact_type=<primary_output>)` in Step 0.L retrieves corrections at the start of the same skill type. Schema example corrected; CLAUDE.md rule #19 updated.

## Key Architectural Decisions

1. Diagram catalog organized by ontological layer (not vertical domain slice). Vertical slicing by domain IS used at artifact level (phase B/C/D subdirs) but NOT in the element catalog.
2. Enterprise/engagement catalog separation is STRUCTURAL (separate repos/dirs), not a naming convention. `extends:` field for cross-catalog traceability.
3. Import-not-include: engagement catalog imports enterprise elements at bootstrap. PUML diagrams include only engagement `_macros.puml`.
4. Layer 2 system prompt = `### Runtime Behavioral Stance` (independently authored, NOT compressed from §11). Three mandatory elements: default bias, conflict posture, cross-cutting rule.
5. `workflow.db` (SQLite) is git-tracked as the canonical event store. YAML export in `workflow-events/` is human-readable projection.

## Runtime Extraction Contract

- Layer 1: `system-prompt-identity` frontmatter (≤150 tokens, always)
- Layer 2: `### Runtime Behavioral Stance` in §11 (≤350 tokens, always)
- Layer 3: full skill file up to complexity-class budget (≤600/1200/2000) — PRIMARY behavioral delivery vehicle
- Layer 4: on-demand via `read_artifact` tool
- All other AGENT.md sections = authoring documentation only, not runtime-injected

## Python Coding Standards (Stage 5 onward)

Defined in `specs/IMPLEMENTATION_PLAN.md §Python Coding Standards` and CLAUDE.md rule #20. Key points:
- Mandatory type annotations on all signatures; lowercase generics (`list[str]`, `x | y`); `Protocol` for structural subtyping
- Monadic `Result`-style error handling; no exceptions for expected failures
- Domain-centred four-layer architecture: Common → Domain → Application → Infrastructure
- `src/common/` for cross-cutting concerns (logging, validation, parsing, normalisation) — usable by all layers
- Ports-and-adapters for all I/O; domain Pydantic models are single source of truth

## Next: Stage 5

Python implementation layer: EventStore completion + PydanticAI agents + LangGraph orchestration + source adapters + skill loader. Fully detailed in `specs/IMPLEMENTATION_PLAN.md §Stage 5`.

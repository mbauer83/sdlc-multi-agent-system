---
name: SDLC Multi-Agent System — Project State
description: Current implementation stage, completed work, and what to resume next
type: project
---

Stage 3 (primary implementation chain) is complete as of 2026-04-02. All 5 core agents authored:
- Solution Architect (AGENT.md + 6 skills)
- Software Architect/PE (AGENT.md + 5 skills)
- DevOps/Platform Engineer (AGENT.md + 4 skills)
- Implementing Developer (AGENT.md + 3 skills)
- QA Engineer (AGENT.md + 3 skills)

Also authored in Stage 3: `framework/discovery-protocol.md` — the discovery-first protocol.

Stage 4 (framing layer) is partially complete as of 2026-04-02:
- Product Owner: AGENT.md + 5 skills — complete
- Sales & Marketing: AGENT.md + 3 skills — complete
- CSCO: AGENT.md + `stamp-stpa-methodology.md` + `gate-phase-a.md` through `gate-phase-d.md` — complete (gate-phase-g.md, gate-phase-h.md, incident-response.md still needed; may exist as unreviewed background-agent drafts — check before authoring)

**Stage 4.5 specified (2026-04-03) — not yet authored:**
New cross-cutting framework extensions defined in IMPLEMENTATION_PLAN.md §4.5:
- `framework/diagram-conventions.md` — PUML diagram conventions, common architecture model (ontological packages: motivation/business/application/technology/data/sequences/processes), enterprise/engagement two-catalog design (import-not-include), reuse-first protocol, ALG-C01–C04
- `framework/artifact-schemas/diagram-catalog.schema.md` — schema for element sub-catalogs, connections, sequence/process render maps, diagram index
- `framework/repository-conventions.md §13` — canonical artifact reference format (`[@artifact-id v1.2](path)`)
- `framework/discovery-protocol.md §8` — Step 0.D diagram catalog lookup (ontological sub-catalog scan)
- `framework/discovery-protocol.md §9` — Step 0.S standards/coding-guidelines discovery (mandatory SwA/DE/DO)
- `framework/agent-runtime-spec.md §2` update — Layer 2 renamed to "Runtime Behavioral Stance"; ≤200 tokens; imperative voice; three elements: default bias, conflict posture, cross-cutting rule; not a compression of §11
- New AGENT.md section requirement: `## Artifact Discovery Priority` (all roles)
- New `### Runtime Behavioral Stance` subsection in all AGENT.md §11 (retroactive)

**Key architectural decisions made 2026-04-03:**
1. Diagram catalog organized by ontological layer (not vertical slice). Vertical slicing by domain IS used at artifact level (phase B/C/D subdirs) but NOT in the element catalog.
2. Enterprise/engagement catalog separation is STRUCTURAL (separate repos/dirs), not a naming convention. Element scope = where the file lives. `extends:` field for cross-catalog traceability.
3. Import-not-include: engagement catalog imports enterprise elements at bootstrap (new local IDs + extends: back-ref). PUML diagrams include only the engagement catalog's `_macros.puml` — no collision risk.
4. Layer 2 system prompt = `### Runtime Behavioral Stance` (independently authored, NOT compressed from §11). Three mandatory elements: default bias, conflict posture, cross-cutting rule. Layer 1 = identity only (no behavioral content).
5. Stage 5.5 dashboard gains: PUML rendering (local plantuml CLI, cached SVG), file/image display, SSE-based filesystem monitoring, diagram browser view.

**Stage 4.5 retroactive AGENT.md/skill updates — COMPLETE (2026-04-03):**
- All 9 AGENT.md files: `system-prompt-identity` scan-order sentence + `### Runtime Behavioral Stance` (§11) + `## 12. Artifact Discovery Priority`
- All 40 skill files: `complexity-class:` added (13 complex, 18 standard, 9 simple — after fixing DE phase-g, SA phase-a, SwA phase-g-governance to complex)
- Step 0.S added to SwA phase-g-governance, DE phase-g, DO phase-g
- IMPLEMENTATION_PLAN.md: stale "Condensed Behavioral Directives" references fixed; ≤700 cap replaced with complexity-class budgets; retroactive checkboxes marked complete
- CLAUDE.md rule 14: `complexity-class:` added to required skill frontmatter; runtime extraction contract documented (only 2 AGENT.md fields reach runtime; skill files are the primary runtime vehicle)

**Runtime extraction contract (key architectural fact):**
- Layer 1: `system-prompt-identity` frontmatter field (≤150 tokens, always present)
- Layer 2: `### Runtime Behavioral Stance` in §11 (≤350 tokens, always present)
- Layer 3: full skill file content up to complexity-class budget (≤600/1200/2000), injected when skill is invoked — PRIMARY behavioral delivery vehicle
- Layer 4: on-demand via `read_artifact` tool
- All other AGENT.md sections = authoring documentation only, not runtime-injected

**Still pending (Stage 4.5 retroactive, blocked):**
- Step 0.D + diagram production Steps D1-D4 for SA phase-b/phase-c-application/phase-c-data and SwA phase-d/phase-e — blocked on `framework/diagram-conventions.md`

**How to apply:** Next: Stage 4 remaining CSCO skills (gate-phase-g.md, gate-phase-h.md, incident-response.md — check if background drafts exist first), then update agent-index.md (add PO, SM, CSCO rows), then Stage 4.5 framework documents.

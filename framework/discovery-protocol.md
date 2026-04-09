# Discovery Protocol

**Version:** 1.2.0  
**Status:** Approved  
**Owner:** Project Manager  
**Last Updated:** 2026-04-09

---

## 1. Purpose

Discovery prepares the agent to execute the current task with confidence and traceable evidence.

Principle: **scan first, infer second, ask last**.

If confidence remains insufficient after discovery, a CQ is the fallback mechanism to close only the remaining blocking gaps. Skipping discovery before raising a CQ is a governance violation (ALG-018 risk).

### Tool Binding Boundary (runtime-owned)

This document specifies behavior, not hard-coded tool signatures.

- Canonical model query tools: `model_query_stats`, `model_query_list_artifacts`, `model_query_search_artifacts`, `model_query_count_artifacts_by`, `model_query_read_artifact`, `model_query_find_connections_for`, `model_query_find_neighbors`
- Canonical validation tools: `model_verify_file`, `model_verify_all`
- Canonical model write tools: `model_write_help`, `model_create_entity`, `model_create_connection`, `model_create_diagram`, `model_create_matrix`
- Aliases in skills (for example `list_artifacts`, `search_artifacts`, `read_artifact`) are intent hints only.

Execution gating is owned by orchestration code, not skill prose.

---

## 2. Discovery Scan Procedure

Run in this order:
1. Step 0.L (Learnings Lookup — corrections + skill-amendments; episodic on revisit)
2. Step 0.M (Memento Recall)
3. Layers 1-5
4. Optional Step 0.D, 0.S, and/or 0.F when applicable
5. Gap Assessment (Section 3)
6. Execution confidence decision: proceed or raise CQ fallback (Section 4)

End-of-skill close (after primary output is produced):
7. `save_memento_state(phase, key_decisions, open_threads)` — always, unconditional
8. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred (governed by `framework/learning-protocol.md §13.3`)
9. `record_learning(...)` — if a §3.1/§3.2 trigger was met (governed by `framework/learning-protocol.md §3–§4`)

### Step 0.L — Learnings Lookup

Execute before Step 0.M and Layer 1.

1. Query role/phase/output learnings:
   - `query_learnings(phase, artifact_type, domain)` — retrieves corrections and calibrations. Include enterprise and cross-role indexes (see `framework/learning-protocol.md §5` for full retrieval procedure).
   - `query_learnings(skill_id=<active_skill_id>, entry_type="skill-amendment")` — same tool, different filter shape: retrieves skill-specific procedure amendments by exact skill-id match. Prepend to working context before general corrections; cap at 3 per skill-id. (A separate tool was deliberately not created — see `framework/learning-protocol.md §9` design rationale.)
   - If `phase_visit_count > 0`: `query_learnings(phase, entry_type="episodic")` — retrieves prior episode summaries for this phase.
2. Rank by importance then recency; apply combined N=5 cap across corrections + episodic (skill-amendments are capped separately at 3).
3. Inject returned corrections, amendments, and episode summaries into working context.

Purpose: learned corrections and continuity context shape interpretation of all subsequent artifacts.

### Step 0.M — Memento Recall

Execute after Step 0.L, before Layer 1. Always run; returns nothing on first invocation for this phase.

1. Call `get_memento_state(phase=<current_phase>)`.
2. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists.
3. If no state exists (first invocation for this phase): skip injection; proceed to Layer 1.

Purpose: carry forward the agent's key decisions and open threads from the previous invocation in this phase. Complements Step 0.L (corrections) with ephemeral continuity context. Governed by `framework/learning-protocol.md §13`.

### Layer 1 — Engagement State

Use indexed artifact/event access; no directory walking.

1. Read invocation context from `AgentDeps`: engagement config + `workflow_state`.
2. Filter artifact metadata (`list_artifacts(...)`) for current phase/domain.
3. Read summaries first (`read_artifact(..., mode="summary")`), escalate to full only when required.
4. Use concept search (`search_artifacts(...)`) when metadata is insufficient.
5. Query event payload history when needed (`query_events(...)`).

Role-priority defaults:
- SA: motivation/strategy/business first; application when traceability requires.
- SwA Phase C: application + business.
- SwA Phase D+: technology + application.
- DE/DO: standards scan first (Step 0.S), then technology-layer artifacts.

### Layer 2 — Enterprise Repository

Use the same query interface with enterprise scope filters.

Required/typical checks:
- Approved standards and patterns
- Existing capability/segment architectures
- Enterprise requirements/constraints/principles
- Enterprise concept search when classification is uncertain

Do not walk enterprise directories directly.

### Layer 3 — External Sources (situative)

External sources are queried only when one of these applies:
- Reverse architecture context (EP-G/EP-H or REV skills)
- User explicitly references an external source in CQ response
- PM explicitly instructs a source lookup

Otherwise: skip Layer 3 and record that it was skipped.

When executed:
1. Resolve applicable source configs.
2. Query only phase-relevant scope (or only the user-cited item for CQ references).
3. Emit source-query events.
4. Annotate sourced fields as `[source: <source-id>]`.
5. Raise conflict signal if sourced content contradicts baselined artifacts.

### Layer 4 — Target Repository / Repositories

Read all registered accessible repos from engagement config.

For each repo:
1. Structure and manifest scan
2. Infra/deployment scan
3. Architecture-doc scan
4. Interface/schema scan
5. Test-structure scan

Annotate inferences with repo-scoped source tags:
- Multi-repo: `[inferred: target-repo:<repo-id> scan]`
- Single-repo: `[inferred: target-repo scan]`

For multi-repo engagements, additionally detect shared-dependency drift, undocumented inter-repo contracts, and circular dependencies.

### Layer 5 — EventStore State

Use injected `workflow_state` as primary source.

Check at minimum:
- `current_phase`
- `phase_visit_counts`
- `gate_outcomes`
- `baselined_artifacts`
- `open_cqs`
- `last_algedonic`

Use event queries only for payload details not already present in state.

### Optional Step 0.D — Diagram Catalog Lookup

Apply only for skills that produce or update diagrams.

1. Derive diagram scope from the concrete skill step (type + purpose).
2. Query required entities and connections via model tools.
3. Confirm `§display` coverage for target diagram language.
4. Then execute D1-D5 from `framework/diagram-conventions.md §5`.

### Optional Step 0.S — Standards and Coding Guidelines Discovery

Apply for SwA/DE/DO implementation-facing phases.

1. Scan `technology-repository/coding-standards/`.
2. Scan enterprise standards.
3. If no usable standards exist, record a standards gap and raise CQ when blocking.
4. Cite governing standards in implementation-facing outputs.

### Optional Step 0.F — Framework Knowledge Lookup

Apply when execution depends on framework policy/protocol interpretation.

1. List candidate docs via metadata filters (`list_framework_docs(...)`).
2. Find candidate sections via query (`search_framework_docs(...)`).
3. Read only selected section(s) summary-first (`read_framework_doc(..., section=..., mode="summary")`).
4. Escalate to `mode="full"` only if the section summary is insufficient for a binding decision.

For policy citations in outputs, use formal framework references per
`[@DOC:repository-conventions#13-5-framework-spec-cross-references-formal](framework/repository-conventions.md#13-5-framework-spec-cross-references-formal)`.

Prohibited pattern: unconditional pre-read of all `framework/` docs.

---

## 3. Gap Assessment Output

Produce an internal table before CQ generation.

| Section | Status | Source(s) | Notes |
|---|---|---|---|
| Schema section identifier | Covered/Partially Covered/Inferred/Missing | Artifact/source refs | Why this status |

Status semantics:
- **Covered**: fully producible from discovered inputs.
- **Partially Covered**: producible with explicit gaps.
- **Inferred**: derivable but requires validation where binding.
- **Missing**: not discoverable; CQ candidate.

---

## 4. CQ Generation Rules

1. **Exhaust discovery first**.
2. **Batch by target** (user or agent), not per field.
3. **Mark blocking vs non-blocking**.
4. **Annotate provenance** in outputs:
   - `[source: user-input]`
   - `[source: <source-id>]`
   - `[inferred: target-repo... ]`
   - `[derived: <artifact-id>]`
   - `[assumed: ...]`
5. **Record discovery scope** in artifact assumptions/header metadata.

---

## 5. Non-Linear ADM and Revisit Discovery

When revisiting a phase (`phase_visit_count > 1`):

1. Read trigger reason from EventStore.
2. Start from latest artifact version.
3. Scope updates to affected sections only.
4. Preserve unaffected content; increment version.
5. Re-run discovery only for changed scope.
6. Re-raise CQs only for unresolved in-scope fields.

---

## 6. Skill File Requirement

Every phase-starting or non-EP-0-entry skill must begin procedure with a discovery step and end with a memory close step.

Minimum template:

```markdown
### Step 0 — Discovery Scan

Execute `framework/discovery-protocol.md §2`.
Complete Step 0.L (corrections + skill-amendments; add episodic if phase_visit_count > 0) + Step 0.M + Layers 1-5.
Apply 0.D/0.S/0.F only when applicable.
Produce internal Gap Assessment before Step 1.

### End-of-Skill Memory Close

After producing primary output artifacts, execute in order:
1. `save_memento_state(phase, key_decisions, open_threads)` — always, unconditional.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery, constraint revelation, or key decision occurred (governed by `framework/learning-protocol.md §13.3`).
3. `record_learning(...)` — if a §3.1/§3.2 trigger was met (governed by `framework/learning-protocol.md §3–§4`).
```

---

## 7. References

- `framework/clarification-protocol.md`
- `framework/repository-conventions.md`
- `framework/sdlc-entry-points.md`
- `framework/architecture-repository-design.md`
- `framework/algedonic-protocol.md`
- `framework/diagram-conventions.md`
- `framework/learning-protocol.md`
- `framework/framework-knowledge-index.md`

---

## 8. Optional-Step Quick Rules

Step 0.L and Step 0.M are **mandatory** for every skill invocation. For Step 0.D (diagram), Step 0.S (standards), and Step 0.F (framework):
1. Run only when applicable to the current skill/task.
2. Use query-first retrieval, then section-scoped reads.
3. Treat missing mandatory inputs as discovery gaps and raise CQ only when blocking.

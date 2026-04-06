---
skill-id: SA-PHASE-C-DATA-REVIEW
agent: SA
name: phase-c-data
display-name: Phase C — Data Architecture Traceability Review
invoke-when: >
  SwA has produced a Data Architecture draft (0.x.x) and requests SA traceability
  review; or SwA has baselined DA at 1.0.0 and SA has not yet cast consulting acknowledgement.
  This skill is consulting — SA is not the primary author of DA; SwA is.
trigger-phases: [C]
trigger-conditions:
  - handoff.created from SwA (handoff-type=phase-C-sa-traceability-review, artifact-type=data-architecture)
  - artifact.baselined from SwA (artifact_type=data-architecture) — fallback trigger if no explicit review handoff
entry-points: [EP-0, EP-A, EP-B, EP-C]
primary-outputs: [SA Traceability Feedback, SA Consulting Acknowledgement]
complexity-class: standard
version: 1.1.0
---

# Skill: Phase C — Data Architecture Traceability Review

**Agent:** Solution Architect  
**Version:** 1.1.0  
**Phase:** C — Information Systems Architecture (Data sub-track, SA consulting role)  
**Skill Type:** Phase consulting — traceability review  
**Framework References:** `agile-adm-cadence.md §6.4`, `framework/artifact-schemas/data-architecture.schema.md`, `raci-matrix.md §3.5`, `clarification-protocol.md`, `algedonic-protocol.md`

> **Role note (Stage 4.8h):** SA is no longer the primary author of Data Architecture. SwA produces DA; SA reviews it to verify correct derivation from the Business Architecture (BA). The primary skill for DA production is `agents/software-architect/skills/phase-c-data.md`.

---

## Runtime Tooling Hint


Representation choice (balanced and mandatory):
- Use `.puml` diagrams when flow, topology, sequence, trust boundaries, or interaction context is the primary concern.
- Use matrix artifacts (`model_create_matrix`) for dense many-to-many mappings, coverage, and traceability where node-link readability degrades.
- Do not replace contextual architecture views with matrices alone: keep a reasonable set of diagrams that preserves end-to-end context for the domain slice.
- Practical threshold: if a single node-link view would exceed about 25 elements or become edge-dense, keep/author at least one contextual diagram and shift dense cross-reference detail to a matrix.

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Data Architecture (`DA`) draft | SwA (via handoff) | Draft (0.x.x) or 1.0.0 | Full artifact required for traceability review |
| Business Architecture (`BA`) | SA (self-produced, Phase B) | Baselined at version 1.0.0 | Every DOB-nnn must trace to at least one BPR-nnn (CRUD operation) or BOB-nnn (business object) |
| Architecture Principles Register (`PR`) | SA (self-produced, Phase A) | Version 0.1.0 or higher | Technology-independence principle: DA must be technology-independent (no database products, storage formats) |
| Handoff record from SwA | SwA | `handoff.created` emitted | Triggers this skill; contains review scope and draft path |

---

## Knowledge Adequacy Check

### Required Knowledge

- Full BA Business Architecture: all BPR-nnn (business processes and their CRUD operations), BOB-nnn (business objects), BSV-nnn (business services that deliver data) — these are the SA-produced entities that every DOB-nnn must derive from.
- Architecture Principles Register: technology-independence principle is the key SA enforcement concern.
- Any BA data-relevant decisions: ownership of business objects across ORG units; any business process that explicitly creates or destroys data.

### Known Unknowns

| Unknown | Blocking | CQ Target | Impact |
|---|---|---|---|
| DOB-nnn classification requires regulatory jurisdiction (PII, health, financial) not resolved in Phase A | No — SA flags the gap; CSCO has primary authority on regulatory classification | CSCO | SA feedback note |
| Business object ownership ambiguous between two BA ORG units | No — SA notes the ambiguity in feedback | SwA or PM | SA feedback item |

### Clarification Triggers

SA raises a CQ when:
1. A DOB-nnn derives from a BA business object (BOB-nnn) that does not exist in the baselined BA — phantom derivation. SA raises a CQ to SwA: "What business object does [DOB-nnn name] represent? It is not in BA v1.0.0."
2. The DA's logical data model contains relationship structures that contradict the BA's business process model (e.g., a process-owned entity appears to be shared across two exclusive business processes). SA raises a bounded CQ to SwA and PO.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="C", artifact_type="data-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

1. Confirm the DA draft or baseline has been received via handoff from SwA.
2. Confirm BA is at version 1.0.0.
3. Read the DA artifact in full.
4. Read the BA's Business Object Catalog (BOB-nnn) and Business Process Catalog (BPR-nnn) — these are the primary traceability targets.

---

### Step 1 — Business-Object Traceability Check

For each DOB-nnn in the Data Entity Catalog:

1. Identify what BA entity it derives from: the `Owning Application` (APP-nnn) links back to BPR-nnn/BSV-nnn via the AA. Confirm the DOB corresponds to a real information concept present in the BA (via BOB-nnn, or as the information produced/consumed by a BPR-nnn).
2. If a DOB-nnn has no traceable BA business entity: **Gap D1 — Phantom data entity** (data entity with no business anchor).
3. Verify the DOB's classification is internally consistent with its BA context: a data entity involved exclusively in Public business processes should rarely be classified Restricted without explicit justification. Inconsistency: **Gap D2 — Classification inconsistency** (not a hard failure, but requires SwA rationale).
4. Verify no technology-specific data model elements appear: no database column names, no SQL types, no file formats, no storage product names. If found: **Gap D3 — Technology-independence violation**.

5. Verify data needed to evidence `OUT-nnn` metrics remains represented and attributable in the DA path (`OUT -> COA -> CAP -> BPR/BSV -> DOB`). Missing evidentiary data lineage is **Gap D6 — Outcome evidence data gap**.

---

### Step 2 — CRUD Coverage Check

Review the Data/Business Function Matrix (CRUD):

1. For each BPR-nnn in the BA, verify at least one DOB-nnn has a Create (`C`) or Read (`R`) operation attributed to that process. A business process with no data operations is unusual — if intentional, it should be noted in the DA.
2. For each DOB-nnn, verify at least one BPR-nnn creates it (`C`). An entity with no creator: either it is imported externally (SA verifies there is an external integration entry for it) or it is an orphaned entity: **Gap D4 — No creator identified**.
3. An entity classified Restricted or Safety-Critical with a Create operation attributed to a non-safety-relevant process: **Gap D5 — Governance concern** (flag to SwA; may require CSCO attention).

---

### Step 3 — Compose Structured Feedback

Produce a structured feedback note addressed to SwA:

```
SA Traceability Review — Data Architecture [DA version]
Review Date: [date]
Reviewer: SA

## Summary
[1–2 sentences: overall assessment — pass / pass with minor gaps / significant gaps requiring revision]

## Findings

### D1 — Phantom data entities (if any)
[DOB-nnn "name"]: No traceable BA business entity or business process found.
Correction required: identify the BA anchor or remove the entity.

### D2 — Classification inconsistencies (if any)
[DOB-nnn "name"]: Classified [level] but involved only in [Public/Internal] business processes.
Correction required: provide rationale or adjust classification.

### D3 — Technology-independence violations (if any)
[DOB-nnn or data model element]: Contains technology-specific notation "[example]".
Correction required: replace with logical description.

### D4 — No creator identified (if any)
[DOB-nnn "name"]: No BPR-nnn Create operation in CRUD matrix. If externally sourced: note the external source.
Action required: identify creator or add external integration note.

### D5 — Governance concerns (if any)
[DOB-nnn "name"]: [Restricted/Safety-Critical] entity created by non-safety-relevant process [BPR-nnn].
Action required: SwA to coordinate with CSCO; add rationale to DA.

## No-Action Items
[List acceptable findings — e.g., a data entity derived from a business scenario rather than a BA process is acceptable if the scenario is documented.]

## SA Consulting Acknowledgement Status
[FEEDBACK REQUIRED — awaiting SwA revision] OR [ACKNOWLEDGED — no revision required]
```

Emit `handoff.created` to SwA: `handoff-type=phase-C-sa-feedback`, artifact path = feedback note, review round = 1 (or 2).

---

### Step 4 — Process SwA Revision (if applicable)

On receipt of revised DA from SwA:

1. Read revised DA.
2. Verify each D1–D5 finding from the prior round has been addressed.
3. If all material findings (D1, D3, D4) addressed: proceed to Step 5.
4. If material findings remain: compose revised feedback (Step 3), mark review round = 2.
5. **Maximum 2 rounds.** If D1, D3, or D4 gaps remain after round 2: raise `ALG-010` to PM. PM adjudicates. Do not proceed to SA Consulting Acknowledgement until PM resolves.

---

### Step 5 — SA Consulting Acknowledgement

When SA is satisfied (all material gaps resolved or PM-adjudicated):

1. Emit `handoff.created` to SwA and PM:
   - `handoff-type: phase-C-sa-consulting-ack`
   - `artifact-type: data-architecture`
   - `result: acknowledged`
   - `version`: the DA version reviewed
   - `open-items`: list D2/D5 items noted but not blocking
2. **SA does not cast the Phase C gate vote.** The C→D gate vote covering both AA and DA is SwA's authority. SA's consulting acknowledgement (for both AA and DA) is input to the gate evaluation.

---

## Feedback Loop

### SwA Revision Loop

- **Iteration 1:** SA provides structured feedback; SwA revises DA; re-sends.
- **Iteration 2:** SA reviews revision; if all material gaps resolved, acknowledges.
- **Termination:** SA Consulting Acknowledgement emitted.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` if after 2 iterations there remain D1, D3, or D4 findings. PM adjudicates.

### Personality-Aware Conflict Engagement

Data architecture traceability to business objects is a business-layer concern: SA has primary authority to define what constitutes a valid business anchor for a data entity. If SwA disputes that a DOB-nnn needs a BA anchor (e.g., arguing it is a technical artifact), SA's obligation is to explain what business information the entity represents and why it should appear in the BA model. If the BOB catalog genuinely lacks the entity, that is a BA gap — SA must update the BA rather than demanding SwA trace to a non-existent entity. Conflicts on D2 (classification inconsistency) and D5 (governance concerns) default to CSCO authority when the disagreement persists beyond 1 iteration.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 2 required for material D1/D3/D4 gaps | S2 |
| `algedonic` | ALG-010 raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from BA | S2 |

On trigger: call `record_learning()` with `artifact-type="data-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total).

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | A DOB-nnn classified Safety-Critical has no corresponding SCO reference visible in DA, despite a safety-relevant business process touching it | S1 | Flag to SwA and CSCO immediately; do not emit SA consulting acknowledgement until CSCO coordination is evidenced |
| ALG-003 | SA identifies during review that the DA covers data subject to a regulatory obligation (GDPR, HIPAA, PCI-DSS) not yet addressed in SCO | S1 | Emit `alg.raised`; notify CSCO and PM; SA cannot acknowledge until CSCO assesses |
| ALG-010 | Two review iterations exhausted with D1, D3, or D4 findings unresolved | S3 | Emit `alg.raised`; PM adjudicates |

---

## Outputs

| Output | Path | EventStore Event |
|---|---|---|
| SA Structured Traceability Feedback (rounds 1–2) | `engagements/<id>/handoff-log/` | `handoff.created` |
| SA Consulting Acknowledgement | `architecture-repository/overview/` + handoff to SwA and PM | `handoff.created` |

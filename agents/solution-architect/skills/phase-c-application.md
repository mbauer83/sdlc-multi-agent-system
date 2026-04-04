---
skill-id: SA-PHASE-C-APP-REVIEW
agent: SA
name: phase-c-application
display-name: Phase C — Application Architecture Traceability Review
invoke-when: >
  SwA has produced an Application Architecture draft (0.x.x) and requests SA traceability
  review; or SwA has baselined AA at 1.0.0 and SA has not yet cast consulting acknowledgement.
  This skill is consulting — SA is not the primary author of AA; SwA is.
trigger-phases: [C]
trigger-conditions:
  - handoff.created from SwA (handoff-type=phase-C-sa-traceability-review, artifact-type=application-architecture)
  - artifact.baselined from SwA (artifact_type=application-architecture) — fallback trigger if no explicit review handoff
entry-points: [EP-0, EP-A, EP-B, EP-C]
primary-outputs: [SA Traceability Feedback, SA Consulting Acknowledgement]
complexity-class: standard
version: 1.1.0
---

# Skill: Phase C — Application Architecture Traceability Review

**Agent:** Solution Architect  
**Version:** 1.1.0  
**Phase:** C — Information Systems Architecture (Application sub-track, SA consulting role)  
**Skill Type:** Phase consulting — traceability review  
**Framework References:** `agile-adm-cadence.md §6.4`, `framework/artifact-schemas/application-architecture.schema.md`, `raci-matrix.md §3.4`, `clarification-protocol.md`, `algedonic-protocol.md`

> **Role note (Stage 4.8h):** SA is no longer the primary author of Application Architecture. SwA produces AA; SA reviews it to verify correct realisation of the Business Architecture (BA). The primary skill for AA production is `agents/software-architect/skills/phase-c-application.md`.

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Application Architecture (`AA`) draft | SwA (via handoff) | Draft (0.x.x) or 1.0.0 | Full artifact required for traceability review |
| Business Architecture (`BA`) | SA (self-produced, Phase B) | Baselined at version 1.0.0 | SA's primary reference; every APP-nnn must trace to at least one BPR-nnn, BSV-nnn, or CAP-nnn |
| Architecture Principles Register (`PR`) | SA (self-produced, Phase A) | Version 0.1.0 or higher | Technology-independence principle must be enforced in AA review |
| Handoff record from SwA | SwA | `handoff.created` emitted | Triggers this skill; contains review scope and draft path |

---

## Knowledge Adequacy Check

### Required Knowledge

- Full BA Business Architecture: all BPR-nnn, BSV-nnn, CAP-nnn, BOB-nnn, VS-nnn entries — these are the SA-produced business entities that every APP-nnn must realise.
- Architecture Principles Register: the technology-independence principle is the SA's primary enforcement concern in this review.
- Any open CQs from Phase B that are relevant to application design (e.g., unresolved business process boundaries that affect component decomposition).

### Known Unknowns

| Unknown | Blocking | CQ Target | Impact |
|---|---|---|---|
| APP-nnn claims to realise a BPR not yet resolved in BA (BA CQ still open) | No — SA notes the gap and flags to SwA; not a review blocker | N/A | SA feedback item |
| Technology-independence violation: SA cannot determine if a component name implies technology without more context | No — SA requests clarification in feedback | SwA | SA feedback item |

### Clarification Triggers

SA raises a CQ when:
1. A technology product name embedded in an APP-nnn description is ambiguous — SA cannot confirm whether it is a logical label or a technology selection. SA raises a bounded CQ to SwA: "Is [name] a logical component label or a specific technology product?"
2. An APP-nnn realises no identifiable BPR-nnn, BSV-nnn, or CAP-nnn even after SA reads the full BA — the component has no business-layer anchor. SA raises a CQ to SwA and PO: "What business process or capability does [APP-nnn name] realise?"

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="C", artifact_type="application-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

1. Confirm the AA draft or baseline has been received via handoff from SwA.
2. Confirm BA is at version 1.0.0. If BA has changed since Phase B gate: note the current version and use the latest baselined BA as the reference.
3. Read the AA artifact in full (use `read_artifact` mode=full).
4. Read the BA's Business Process Catalog (BPR-nnn) and Business Services Catalog (BSV-nnn) in full — these are the primary traceability targets.

---

### Step 1 — Business-Layer Traceability Check

For each APP-nnn in the Application Component Catalog:

1. Identify which BPR-nnn, BSV-nnn, or CAP-nnn it claims to realise (per AA's `Realises Capability` field).
2. Verify the claimed entity exists in the baselined BA. If it does not: **Gap T1 — Phantom realisation claim** (APP-nnn references a non-existent business entity).
3. Verify the APP-nnn's responsibility description is consistent with the referenced business entity's purpose. If the component does something unrelated to the business entity it claims to realise: **Gap T2 — Mismatch between component and business entity**.
4. Verify no technology product names appear in component names, type descriptions, or responsibility fields. If found: **Gap T3 — Technology-independence violation** (hard architecture constraint).

**Reverse check:** For each BPR-nnn in BA, verify at least one APP-nnn marks it as a primary (`●`) realisation. Any BPR-nnn with no primary APP-nnn is: **Gap T4 — Unrealised business process** (AA coverage gap).

---

### Step 2 — Interface Traceability Check

For each IFC-nnn in the Interface Catalog:

1. Verify `Exposed By` and `Consumed By` APP-nnn references exist in the Component Catalog.
2. Verify the interface's protocol style is logical (REST / gRPC / Event / Batch / Websocket / Manual) — not a specific version or product name. If a specific product is named: **Gap T3 variant**.
3. Check that interfaces involving external actors correspond to external integration points identified in the BA Business Services Catalog (external-facing BSV-nnn). An external integration not traceable to the BA is potentially an unreviewed scope change: **Gap T5 — Untraced external integration**.

---

### Step 3 — Compose Structured Feedback

Produce a structured feedback note addressed to SwA:

```
SA Traceability Review — Application Architecture [AA version]
Review Date: [date]
Reviewer: SA

## Summary
[1–2 sentences: overall assessment — pass / pass with minor gaps / significant gaps requiring revision]

## Findings

### T1 — Phantom realisation claims (if any)
[APP-nnn]: References [entity-id] which does not exist in BA v1.0.0.
Correction required: either remove the claim or reference the correct entity.

### T2 — Component/business entity mismatches (if any)
[APP-nnn]: Responsibility description does not align with [BPR/BSV/CAP-nnn].
Correction required: align responsibility description or change the realisation reference.

### T3 — Technology-independence violations (if any)
[APP-nnn or IFC-nnn]: Contains technology product name "[name]".
Correction required: replace with logical description.

### T4 — Unrealised business processes (if any)
[BPR-nnn "name"]: No APP-nnn marks this as primary realisation.
Action required: SwA to add APP-nnn or note that this process is realised by an existing component.

### T5 — Untraced external integrations (if any)
[IFC-nnn]: External integration with "[system]" has no corresponding external-facing BSV-nnn in BA.
Action required: SA will update BA BSV catalog, or SwA should flag the integration as a new scope item for PM.

## No-Action Items
[List findings that SA acknowledges as acceptable with no revision needed — e.g., a component that spans two BPRs is a reasonable design choice.]

## SA Consulting Acknowledgement Status
[FEEDBACK REQUIRED — awaiting SwA revision] OR [ACKNOWLEDGED — no revision required]
```

Emit `handoff.created` to SwA: `handoff-type=phase-C-sa-feedback`, artifact path = feedback note, review round = 1 (or 2).

---

### Step 4 — Process SwA Revision (if applicable)

On receipt of revised AA from SwA:

1. Read revised AA.
2. Verify each T1–T5 finding from the prior round has been addressed.
3. If all findings addressed: proceed to Step 5 (SA Consulting Acknowledgement).
4. If findings remain: compose revised feedback (Step 3), mark review round = 2.
5. **Maximum 2 rounds.** If significant T1–T4 gaps remain after round 2: raise `ALG-010` to PM. PM adjudicates between SA's business-layer traceability requirements and SwA's design decisions. Do not proceed to SA Consulting Acknowledgement until PM resolves.

---

### Step 5 — SA Consulting Acknowledgement

When SA is satisfied with traceability (all material gaps resolved or PM-adjudicated):

1. Emit `handoff.created` to SwA and PM:
   - `handoff-type: phase-C-sa-consulting-ack`
   - `artifact-type: application-architecture`
   - `result: acknowledged`
   - `version`: the AA version reviewed
   - `open-items`: list any remaining non-material findings (T5 scope items) that PM should be aware of
2. Log consulting acknowledgement in `architecture-repository/overview/` as a brief note.
3. **SA does not cast the Phase C gate vote.** The C→D gate vote is SwA's authority. SA's consulting acknowledgement is an input to the gate, not the gate itself.

---

## Feedback Loop

### SwA Revision Loop

- **Iteration 1:** SA provides structured feedback; SwA revises AA; re-sends.
- **Iteration 2:** SA reviews revision; if all material gaps resolved, acknowledges.
- **Termination:** SA Consulting Acknowledgement emitted.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` if after 2 iterations there remain material T1–T4 findings. PM adjudicates. SA may not withhold acknowledgement indefinitely to enforce preferred design choices — only genuine business-layer traceability failures (T1, T2, T4) or hard architecture violations (T3) warrant continued blocking.

### Personality-Aware Conflict Engagement

SA brings breadth across business and technical domains; SwA brings implementation depth. Disagreements on traceability are resolved by reference to BA artifact-ids — not by assertion. If SA flags a T4 (unrealised BPR) and SwA disputes that the process needs a dedicated component, SA's obligation is to explain which BA business entity is left unrealised and what the architectural risk is — not to mandate a specific decomposition. SwA's obligation is to provide a specific component mapping that satisfies the traceability requirement, not to argue that the BA is wrong. If the BA is genuinely wrong, that is a BA revision (SA authority, not reviewable by SwA alone).

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 2 required for material T1/T2/T4 gaps | S2 |
| `algedonic` | ALG-010 raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from BA | S2 |

On trigger: call `record_learning()` with `artifact-type="application-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total).

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | An APP-nnn or IFC-nnn would violate a safety constraint in SCO Phase B (e.g., safety-critical component designed without CSCO acknowledgement visible in AA) | S1 | Flag to SwA immediately; do not emit SA consulting acknowledgement until SwA provides evidence of CSCO coordination |
| ALG-010 | Two review iterations exhausted with material traceability gaps unresolved | S3 | Emit `alg.raised`; PM adjudicates; SA records both positions |
| ALG-018 | SA skips traceability review and emits consulting acknowledgement without reading full BA and AA | S2 | Emit `alg.raised`; invalidate acknowledgement; re-run review |

---

## Outputs

| Output | Path | EventStore Event |
|---|---|---|
| SA Structured Traceability Feedback (rounds 1–2) | `engagements/<id>/handoff-log/` | `handoff.created` |
| SA Consulting Acknowledgement | `architecture-repository/overview/` + handoff to SwA and PM | `handoff.created` |

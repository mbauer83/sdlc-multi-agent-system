---
skill-id: PM-PHASE-A
agent: PM
name: phase-a
display-name: Phase A Coordination — Architecture Vision
invoke-when: >
  Entry point is assessed and PM must run the Scoping Interview (EP-0) or validate warm-start
  artifacts (EP-A/B); coordinates SA through Phase A and evaluates the A→B gate.
trigger-phases: [Prelim, A]
trigger-conditions:
  - cycle.initiated (entry-point=EP-0)
  - sprint.started (phase=A)
  - gate.vote_cast (phase_from=A, from=solution-architect)
entry-points: [EP-0, EP-A, EP-B]
primary-outputs: [Scoping Interview/Entry Assessment Report, Statement of Architecture Work, Phase A Gate Record]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase A Coordination — Architecture Vision

**Agent:** Project Manager  
**Version:** 1.0.0  
**Phase:** A — Architecture Vision  
**Skill Type:** Phase coordination  
**Framework References:** `agile-adm-cadence.md §6.2`, `sdlc-entry-points.md §4.1–4.2`, `clarification-protocol.md`, `raci-matrix.md §3.2`, `framework/artifact-schemas/architecture-vision.schema.md`

---

## Runtime Tooling Hint

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

- Engagement Profile (`engagements/<id>/engagement-profile.md`) — entry point, scope, constraints
- User-provided inputs (varies by entry point — see EP procedures below)
- Any warm-start artifacts produced during entry assessment (AV-000 for EP-A/B entries)
- Requirements Register from PO (if available — EP-B and later)
- CSCO initial safety scan result (for EP-A/B/C entries)

---

## Knowledge Adequacy Check

**Domain knowledge required:**
- Phase A gate checklist: AV baselined, SoAW approved, safety envelope signed off by CSCO
- Scoping Interview CQ topics (EP-0): regulatory environment, stakeholder universe, safety domain, technology constraints — see `sdlc-entry-points.md §4.1`
- AV schema required sections: per `framework/artifact-schemas/architecture-vision.schema.md`

**PM does not assess architecture domain knowledge.** The PM's knowledge adequacy in this skill is limited to:
- Is the scoping interview complete?
- Have all G-holders been identified and engaged?
- Are all input artifacts at the correct version before gate evaluation?

**CQ trigger:** Raise a CQ if the user's stated scope cannot be mapped to a definite entry point.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PM", phase="A", artifact_type="process")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### EP-0 Entry: Scoping Interview

When `entry-point: EP-0` in the Engagement Profile, Phase A begins with a Scoping Interview.

**Step 1 — Prepare scoping questions:**
Working with SA, compile a CQ batch covering the minimum topics from `sdlc-entry-points.md §4.1`:
- What problem is being solved and for whom?
- What does success look like in concrete terms?
- Are there existing systems that must be integrated or replaced?
- What is the regulatory or compliance environment?
- Are there safety-relevant components?
- Are there technology constraints?
- Who are the key stakeholders and decision-makers?

Add engagement-specific questions identified by SA (architecture domain) and CSCO (safety/compliance domain). Do not add generic questions — every CQ must be specific to what cannot be inferred from context.

**Step 2 — Deliver Scoping Interview:**
Format as an Entry Assessment Report per `sdlc-entry-points.md §6`. Deliver to user. Emit `cq.batched` for all CQs. Mark all phase work as suspended until minimum blocking CQs are answered.

**Step 3 — Process answers:**
Route answers to SA (architecture domain), CSCO (safety domain), PO (requirements domain). Update Engagement Profile phase scope table based on answers. Confirm ADM cycle level: capability, segment, or strategic.

**Step 4 — Instruct SA to begin Phase A sprint:**
Emit `sprint.started` for Architecture Sprint AS-1 (Phase A). SA proceeds per `agents/solution-architect/skills/phase-a.md`.

### Non-EP-0 Entry

For EP-A and later entries, Phase A sprint is preceded by warm-start artifact validation. See `skills/master-agile-adm.md §Entry Point Assessment` and `sdlc-entry-points.md §4.2–4.7`. The PM's role:
1. Collect warm-start artifacts from SA.
2. Verify schema conformance summary — SA confirms all required AV sections are populated or flagged.
3. Batch remaining CQs; deliver Entry Assessment Report.
4. On answers: trigger Phase A gate if AV is sufficiently complete; otherwise run a remediation sprint.

### Phase A Gate Coordination

**Pre-gate checklist (PM evaluates):**
1. Architecture Vision (`AV`) — version 1.0.0+; all required header fields present; `pending-clarifications` empty or assumption-only.
2. Stakeholder Map — baselined alongside AV.
3. Statement of Architecture Work (`SoAW`) — PM and SA co-produced; PM signs off.
4. Safety Envelope Statement in `SCO` — CSCO has signed off.
5. SA has submitted `gate.vote_cast` (approved).
6. CSCO has submitted `gate.vote_cast` (approved).

**Gate blocked conditions:**
- CSCO has not signed off on safety envelope → wait; if overdue, emit ALG-004.
- AV has open blocking CQs → CQs must be resolved or converted to documented assumptions before gate.
- SoAW is missing PM signature → PM self-blocks; complete SoAW.

**On gate passed:**
1. Record gate decision in `project-repository/decision-log/gate-A-B.md`.
2. Emit `gate.evaluated` with `result: passed`.
3. Notify SA to begin Phase B planning.
4. Update Engagement Profile: Phase A `status: complete`.

---

## Statement of Architecture Work

The PM co-produces the Statement of Architecture Work with SA. PM contributes:
- Sprint plan and timeline (logical sequencing of subsequent phases)
- Resource allocation (which agents are engaged in which phases)
- Communication plan (how user interactions will be handled)
- Governance plan (which gates apply; who holds G authority)

SA contributes:
- Architecture scope statement
- Constraints and assumptions from Phase A work
- Architecture definition approach

Write to `project-repository/` — this is a PM-owned artifact. Path: `project-repository/statement-of-architecture-work/saw-<version>.md`.

---

## Feedback Loop

**Scoping Interview loop:**
- Iteration 1: PM delivers scoping questions; user responds.
- Iteration 2 (if needed): PM delivers follow-up on ambiguous answers; user responds.
- Termination: All blocking CQs resolved or converted to documented assumptions.
- Max iterations: 2 user interactions before PM documents remaining gaps as assumptions with risk flags.
- Escalation: If safety-domain CQs are unanswered after iteration 2 → ALG-017.

**Phase A gate loop:**
- Iteration 1: Gate evaluation; if blocked, SA/CSCO address open items.
- Iteration 2: Re-evaluation.
- Escalation: After 2 blocked evaluations → ALG-005 (timeline collapse).

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="process"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Action |
|---|---|---|
| ALG-002 | CSCO unavailable; safety gate review required | Halt Phase A progression; do not pass gate without CSCO approval |
| ALG-004 | Phase A gate cannot complete because CSCO sign-off is overdue | Escalate to CSCO with deadline; notify user |
| ALG-005 | Phase A gate has required 2+ extensions | Escalate to user for scope reassessment; consider EP re-classification |
| ALG-017 | Safety-domain CQ unanswered; assumption cannot safely be made | Halt safety-relevant phase work; escalate to user and CSCO |

---

## Outputs

| Output | Path | Owner |
|---|---|---|
| Scoping Interview / Entry Assessment Report | Delivered to user | PM |
| Statement of Architecture Work | `project-repository/statement-of-architecture-work/saw-<v>.md` | PM (with SA input) |
| Phase A Gate Record | `project-repository/decision-log/gate-A-B.md` | PM |
| Sprint AS-1 kickoff/closeout records | `project-repository/sprint-log/AS-1-*.md` | PM |
| EventStore events: sprint.started, gate.evaluated | `workflow.db` | PM |

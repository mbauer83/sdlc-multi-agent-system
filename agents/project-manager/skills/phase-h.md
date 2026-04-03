---
skill-id: PM-PHASE-H
agent: PM
name: phase-h
display-name: Phase H — Architecture Change Management
invoke-when: >
  A change request arrives from any source (user, Phase G deviation, algedonic resolution);
  PM creates the Warm-Start Change Record, routes to SA/SwA/CSCO, and manages phase returns.
trigger-phases: [H]
trigger-conditions:
  - alg.resolved (any algedonic that identifies an architectural gap)
  - handoff.created (handoff-type=phase-g-deviation-report)
  - sprint.started (phase=H)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Warm-Start Change Intake Record, Phase Return Scope Statement, Revision Sprint Records]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase H — Architecture Change Management

**Agent:** Project Manager  
**Version:** 1.0.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Phase coordination; change record intake and routing  
**Framework References:** `agile-adm-cadence.md §5.4, §6.8`, `raci-matrix.md §3.10`, `framework/artifact-schemas/change-record.schema.md`

---

## Inputs Required

- Change trigger (one of: user request, Phase G compliance deviation, architecture consistency issue, algedonic resolution, external driver)
- Existing baselined artifacts in all work-repositories (SA, SwA, CSCO — read-only for PM)
- Current WorkflowState from EventStore (phase visit counts, open CQs, current cycle state)
- Implementation Plan (if Phase H is triggered during or after Phase G)

---

## Knowledge Adequacy Check

**Domain knowledge required:**
- Change classification scheme (per `agile-adm-cadence.md §10` if defined; otherwise per change record schema): Minor / Significant / Major / Emergency
- Phase return scope rules: a phase return re-opens only `affected-artifacts`; all others remain authoritative
- CSCO authority: safety-relevant changes are blocked until CSCO assessment is complete regardless of change class

**CQ triggers:**
- If the change trigger is ambiguous (the user describes a change but its architectural scope is unclear) → PM raises CQ to SA and SwA before classifying.
- If a change affects a safety-critical component but the SCO version is uncertain → PM raises CQ to CSCO.

---

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PM", phase="H", artifact_type="change-record")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

## Change Record Intake

Every Phase H entry begins by creating a Change Record.

### CR-001 format (written by PM to `architecture-repository/change-records/` — wait, no):

**Correction:** Change Records are produced by SA (accountable per RACI §3.10). PM creates a Warm-Start Change Record (CR-000) for ingestion, but SA produces and owns the baselined artifact. PM's intake procedure:

**Step 1 — PM creates Warm-Start CR:**
Write to `project-repository/` (PM scope): `project-repository/change-intake/cr-intake-<id>.md`.

```markdown
---
intake-id: CR-INTAKE-<id>
received-from: user | phase-g-deviation | algedonic | external
received-date: <ISO date>
description: [verbatim or paraphrased change description]
initial-classification: unknown | minor | significant | major | emergency
safety-flag: unknown | not-safety-relevant | safety-relevant
---

## Change Description
[Precise description of what must change and why]

## Scope Assessment (preliminary)
[Which artifacts might be affected — preliminary PM assessment; to be confirmed by SA/SwA]

## Urgency
[Is this a production incident? A compliance deadline? An improvement suggestion?]
```

**Step 2 — Route to SA and SwA for impact assessment:**
SA identifies which architecture artifacts are affected. SwA identifies which technology artifacts are affected. PM collects their assessments.

**Step 3 — Route to CSCO for safety assessment:**
Always, regardless of apparent safety relevance. CSCO confirms `safety-relevant: true/false` and whether a safety gate review is required.

**Step 4 — Classify change:**

| Class | Description | Phase Return Required | Gate Re-evaluation |
|---|---|---|---|
| **Minor** | Clarification or correction that does not alter a key decision; affects ≤1 artifact; no SCO impact | No | No (version increment only) |
| **Significant** | New requirement or corrected decision that revises one phase's outputs; limited ripple effect | One phase return | Gate re-evaluation for the affected phase |
| **Major** | Structural change or reversal of key decision; multiple artifact versions affected; possible SCO impact | One or more phase returns | Full gate re-evaluation for all affected phases |
| **Emergency** | Production incident or compliance breach requiring immediate action outside normal ADM sprint | Governance override | Post-hoc gate record required |

**Step 5 — Instruct SA to produce baselined Change Record:**
PM hands off the intake record and classification to SA. SA produces the formal CR artifact in `architecture-repository/`. PM tracks the handoff.

---

## Phase Return Coordination

When a Significant or Major change requires a phase return:

**Step 1 — Emit `phase.return-triggered`:**
```python
event_store.append(EventEnvelope(
    event_type="phase.return-triggered",
    payload=PhaseReturnTriggeredPayload(
        target_phase="B",         # or whichever phase
        trigger_source="phase-h",
        change_record_id="CR-001",
        affected_artifacts=["BA-001", "AA-001"]
    ).model_dump()
))
```

**Step 2 — Scope the return:**
Only `affected-artifacts` are re-opened. All other baselined artifacts remain authoritative. PM writes a scope statement in `project-repository/decision-log/phase-return-<cr-id>.md`:
```markdown
## Phase Return Scope: CR-<id>

**Target phase(s):** [list]  
**Affected artifacts:** [list with current versions]  
**Unaffected artifacts:** [list — these remain authoritative]  
**Return trigger:** [change-record-id or algedonic-id]  
**Visit count after return:** [phase_visit_counts check]  
```

**Step 3 — Check visit count:**
Read `CycleState.phase_visit_counts` from EventStore. If this return would bring any phase to visit count 4 → ALG-005 before proceeding.

**Step 4 — Plan revision sprint:**
The revision sprint is an Architecture Sprint targeting only the affected artifacts. PM plans it as a standard sprint with explicit scope limitation. Emit `sprint.planned` with `scope: revision` and `affected-artifacts` list.

**Step 5 — Monitor revision and re-gate:**
After revision sprint closes, re-evaluate the gate(s) for all affected phases. A Major change may require re-evaluating multiple gates in sequence.

---

## Emergency Change Procedure

For Emergency class changes (production incident, compliance breach):

1. PM activates emergency response: notify all relevant agents immediately.
2. CSCO assesses safety impact — ALG-014 if CSCO unavailable.
3. SwA and Dev assess minimal remediation path.
4. Work may proceed ahead of formal Architecture Contract if PM documents the override and a post-hoc Architecture Contract is planned.
5. Post-hoc gate record is required within the next sprint close.
6. PM writes Emergency Change Record in `project-repository/change-intake/`.

---

## Change Monitoring (Continuous Phase H)

Phase H is not purely reactive. The PM continuously monitors for emerging change triggers:

- New or changed requirements in the Requirements Register (PO updates)
- Phase G compliance deviations that exceed the "approved variation" threshold
- External events (user-reported technology changes, regulatory updates)
- Algedonic resolutions that identify architectural gaps

PM reviews the Requirements Register at each sprint close. If staleness is detected (RR not updated in 2 sprints during active Phase G), PM notifies PO.

---

## Feedback Loop

**Change assessment loop:**
- PM delivers intake to SA, SwA, and CSCO concurrently.
- Each agent has one sprint cycle to respond with impact assessment.
- Iteration 1: Assessments consolidated; classification determined.
- Iteration 2 (if assessments conflict): PM adjudicates based on RACI.
- Max iterations: 2. Escalation: if SA and SwA disagree on scope after iteration 2 → PM adjudicates and records decision.
- Termination: Change classified; phase return scope defined (or change rejected with reason).

**Phase return revision loop:**
- Revision sprint closes; gate re-evaluated.
- If gate still blocked → iteration 2.
- Max: 2 consecutive blocked re-evaluations → ALG-005.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="change-record"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Action |
|---|---|---|
| ALG-003 | Artifact discovered to violate regulatory/compliance obligation not previously identified | CSCO immediate; PM concurrent; halt affected phase work |
| ALG-005 | Phase return causes visit count to reach 4 | Halt; escalate to user for scope reassessment |
| ALG-014 | Safety-Critical change request; CSCO unavailable | Halt change; document; await CSCO |

---

## Outputs

| Output | Path | Trigger |
|---|---|---|
| Warm-Start Change Intake Record | `project-repository/change-intake/cr-intake-<id>.md` | Phase H entry |
| Phase Return Scope Statement | `project-repository/decision-log/phase-return-<cr-id>.md` | Significant/Major change |
| Revision Sprint Records | `project-repository/sprint-log/revision-<id>-*.md` | Phase return sprint |
| EventStore events: phase.return-triggered, sprint.* | `workflow.db` | Phase H transitions |

---
skill-id: PM-PHASE-G
agent: PM
name: phase-g
display-name: Phase G — Implementation Governance
invoke-when: >
  Phase F gate has passed and Solution Sprints begin; PM coordinates each sprint, records
  Governance Checkpoint Records, tracks compliance assessments, and evaluates the Phase G exit gate.
trigger-phases: [G]
trigger-conditions:
  - gate.evaluated (from_phase=F, result=passed)
  - sprint.started (phase=G, sprint-type=solution)
  - artifact.baselined (artifact-type=architecture-contract)
entry-points: [EP-0, EP-G]
primary-outputs: [Governance Checkpoint Records, Phase G Exit Gate Record, Sprint log records]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase G — Implementation Governance

**Agent:** Project Manager  
**Version:** 1.0.0  
**Phase:** G — Implementation Governance  
**Skill Type:** Phase coordination and governance record-keeping  
**Framework References:** `agile-adm-cadence.md §6.7`, `raci-matrix.md §3.9`, `framework/artifact-schemas/architecture-contract.schema.md`

---

## Runtime Tooling Hint

This PM skill coordinates workflow and quality gates; it does not directly author architecture diagrams. Apply diagram and matrix conventions only when validating or requesting specialist outputs that include diagram artifacts.

Workflow-net alignment:
- Non-trivial `(agent, phase, skill)` execution behavior for this skill is modeled in `g-activity-pm-phase-g-governance-workflow-v1.puml`.
- The skill-level control flow aligns with cross-phase control nets (`lifecycle-activity-sprint-v1`, `cq-activity-lifecycle-v1`, `sprint-review-activity-workflow-v1`, `specialist-invocation-activity-workflow-v1`).

## Inputs Required

- Implementation Plan (baselined, Phase F output)
- Solution Sprint Plan (Phase F output)
- Architecture Contract(s) (`AC`) from SwA — one per work package or Sprint
- Compliance Assessments from QA and CSCO
- Test Execution Reports from QA
- Deployment Records from DevOps
- CSCO Spot-check Records (for safety-relevant components)
- Defect Register from QA (open defects)

---

## Knowledge Adequacy Check

**Domain knowledge required:**
- Architecture Contract content: what ABBs are authorised, what constraints apply, what acceptance criteria must be met — read from SwA's AC artifacts
- Compliance assessment criteria: defined in Test Strategy and Safety Constraint Overlay — read from QA and CSCO artifacts
- Phase G exit conditions per `agile-adm-cadence.md §6.7`: full regression pass, deployment record, CSCO sign-off on all safety-relevant components

**CQ triggers:**
- If an Architecture Contract is missing required CSCO sign-off for a safety-relevant work package → ALG-009 (governance violation), not a CQ.
- If a Compliance Assessment references requirements not traceable to the Architecture Contract → raise CQ to QA and SwA.
- If a Deployment Record is absent but work package is marked complete → raise CQ to DevOps.

---

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PM", phase="G", artifact_type="architecture-contract")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="G")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


## Solution Sprint Coordination

### Per-Sprint Governance

For each Solution Sprint:

**Sprint kickoff (PM responsibilities):**
1. Verify Architecture Contract for this sprint's work package is baselined (SwA accountable) and CSCO-signed if safety-relevant.
2. Verify environment is provisioned (DevOps confirms readiness).
3. Verify QA test cases are ready for this sprint's acceptance criteria.
4. Emit `sprint.started`.
5. Write sprint kickoff record per `master-agile-adm.md §Phase 2`.

**During sprint:**
- Monitor handoff events between Dev and QA.
- Monitor CSCO spot-check schedule for safety-relevant components.
- Track open defects from Defect Register. If Severity-1 defect is raised on a safety-relevant component → ALG-013.
- Track compliance assessment progress.
- For fast-path safety escalation, collect CSCO assessment and user advisory notes, then execute explicit branch decision: continue with targeted rework (route back into phase-work), pause pending resume trigger, or stop engagement path.

**Sprint closeout (PM responsibilities):**
1. Verify no open Severity-1 defects.
2. Verify QA has signed off on test execution report.
3. Verify Compliance Assessment is complete (QA + CSCO G authority).
4. Verify Deployment Record exists (DevOps accountable).
5. Evaluate `review-gates` policy for this phase/stage. If blocking user review is required for phase-output artifacts, emit `review.pending` and block progression until `review.submitted` is processed.
6. Route corrections from review decisions to tagged agents before gate progression.
7. Write Governance Checkpoint Record (see below).
8. Emit `sprint.closed`.
9. Execute EventStore commit procedure (per `master-agile-adm.md §Phase 5`).

### Governance Checkpoint Record

Written to `project-repository/sprint-log/<sprint-id>-governance-checkpoint.md`:
```markdown
---
sprint-id: <id>
work-package-id: <WP-id>
architecture-contract: <AC-id> v<version>
date: <ISO date>
result: compliant | non-compliant | partial
---

## Compliance Summary
| Criterion | Status | Evidence Artifact | Notes |
|---|---|---|---|
| All ABBs implemented as specified | | QA report ref | |
| No prohibited technology choices | | AC ref | |
| Safety-relevant components CSCO-checked | | CSCO spot-check ref | |
| Test execution: all acceptance criteria pass | | QA test report ref | |
| No open Sev-1 defects | | Defect register ref | |

## Deviations from Architecture Contract
[List any deviations; classify each as: approved variation / defect requiring rework / change request raised]

## Open Items
[List any items that must be resolved before Phase G exit]
```

---

## Architecture Contract Oversight

The PM does not produce Architecture Contracts (SwA accountable). PM responsibilities:

1. **Verify AC exists** before each Solution Sprint begins. If SwA has not yet produced the AC for an upcoming work package → block sprint start; notify SwA.
2. **Verify CSCO sign-off** on safety-relevant ACs before sprint start (ALG-009 if missing).
3. **Track AC versions**: if SwA issues a revised AC after a sprint has begun, assess impact on in-progress work; may require sprint scope adjustment.
4. **Cross-reference AC against Implementation Plan**: every work package in the IP must have a corresponding AC. Report gaps.

---

## Compliance Assessment Coordination

1. QA produces Compliance Assessment per work package.
2. CSCO reviews and signs off if `safety-relevant: true` on any AC in scope.
3. PM reviews for completeness: all criteria addressed, all deviations documented.
4. PM records sign-off status in Governance Checkpoint Record.
5. Non-compliant assessments: PM notifies SwA and Dev; work package is blocked until defects resolved and assessment re-run.

---

## Phase G Exit

**Exit conditions (all must be satisfied):**
1. All work packages from the Implementation Plan are marked complete.
2. All Governance Checkpoint Records show `result: compliant` (or partial with approved deviations logged as Change Records for Phase H).
3. Full regression test pass recorded by QA.
4. All Deployment Records present for all deployed work packages.
5. CSCO has completed spot-check coverage for all safety-relevant components.
6. No open Severity-1 defects.
7. SwA has cast `gate.vote_cast` (approved).
8. CSCO has cast `gate.vote_cast` (approved).

**Phase G exit gate record:**
Written to `project-repository/decision-log/gate-G-exit.md`. Same structure as standard gate records.

**On Phase G exit:**
- If no change requests are outstanding: proceed to engagement close (activate `skills/retrospective-knowledge-capture.md`).
- If change requests are open: transition to Phase H.

---

## Feedback Loop

**Defect resolution loop:**
- Severity-1: Dev must address before next governance checkpoint. Max 2 sprint cycles before ALG-013 escalation.
- Severity-2/3: Tracked in Defect Register; must be resolved before Phase G exit.
- Termination: QA signs off on defect resolution; PM updates Governance Checkpoint Record.

**Compliance re-assessment loop:**
- If initial assessment is `non-compliant`: Dev/DevOps address deviations; QA re-assesses.
- Max iterations: 2 re-assessments before PM escalates to SwA for Architecture Contract review.
- Escalation: ALG-010 if loop is exhausted without resolution.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="architecture-contract"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Action |
|---|---|---|
| ALG-009 | Architecture Contract lacks CSCO sign-off for safety-relevant work package | Block sprint start; escalate to CSCO immediately; notify PM |
| ALG-012 | CSCO veto on compliance assessment is overridden | Immediate halt; escalate to user |
| ALG-013 | Severity-1 defect in safety-relevant component | Halt deployment; escalate to CSCO and SwA; do not advance sprint |
| ALG-005 | Phase G exit gate requires 2+ extensions | Escalate to user; assess whether scope reduction or phase reset is required |

---

## Outputs

| Output | Path | Trigger |
|---|---|---|
| Governance Checkpoint Records | `project-repository/sprint-log/<id>-governance-checkpoint.md` | Each Solution Sprint close |
| Phase G Exit Gate Record | `project-repository/decision-log/gate-G-exit.md` | Phase G exit evaluation |
| Sprint log records | `project-repository/sprint-log/<id>-*.md` | Each Solution Sprint |
| EventStore events: sprint.*, gate.evaluated | `workflow.db` | Each Sprint and Gate event |

---

## End-of-Skill Memory Close

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="G", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

---
skill-id: QA-PHASE-H
agent: QA
name: phase-h-regression
display-name: Phase H — Regression Impact Assessment
invoke-when: >
  A Change Record is routed to QA (via PM handoff) requiring assessment of which existing
  tests must re-run and whether the Test Strategy must be updated.
trigger-phases: [H]
trigger-conditions:
  - handoff.created (handoff-type=change-record-intake, to=qa-engineer)
  - phase.return-triggered (any affected-artifacts)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Regression Impact Assessment, Updated Test Strategy]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase H — Regression Impact Assessment

**Agent:** QA Engineer  
**Version:** 1.0.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Consulting — regression analysis  
**Framework References:** `agile-adm-cadence.md §6.9`, `raci-matrix.md §3.10`, `framework/artifact-schemas/change-record.schema.md`, `clarification-protocol.md`, `algedonic-protocol.md`

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
| Change Record (`CR`) | Solution Architect (baselined) or PM (intake draft) | Draft acceptable for initial assessment; final CR required for TS update | Describes the change and affected artifacts |
| Affected architecture artifacts list | SA (via CR §affected-artifacts) | Read as referenced | Required to scope regression |
| Test Strategy (`TS`) — current baselined version | QA (self) | Baselined | Basis for regression scope analysis |
| Defect Register (current) | QA (self) | Current sprint | Prior defect history informs regression risk |
| Architecture Contract (if Phase G in progress) | SwA | Current version | Determines whether in-flight AC compliance criteria change |

---

## Knowledge Adequacy Check

### Required Knowledge

- Scope of change: which architecture artifacts are affected (AV, BA, AA, DA, TA, AC)
- Safety relevance of changed components: does the change affect safety-relevant components?
- Current test suite coverage: which tests cover the changed components

### Clarification Triggers

Raise a CQ when:
1. The Change Record does not specify affected artifacts precisely enough to determine which tests are impacted.
2. A changed component has no existing test coverage and its safety-relevance classification is unknown.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="QA", phase="H", artifact_type="test-strategy")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 1 — Read Change Record and Affected Artifacts

1.1 Read the Change Record (CR). Extract: change class (Minor/Significant/Major/Safety-Critical), affected artifact list, phase-return scope.

1.2 For each affected artifact: read the artifact summary header. Identify which application components (APP-nnn), data entities (DE-nnn), or technology components (TC-nnn) are changed.

1.3 Cross-reference changed components against the Test Strategy's coverage register to identify which tests cover those components.

### Step 2 — Produce Regression Scope

2.1 For each affected component, list the tests that must re-run:
- All acceptance criteria (AC-nnn) that reference the changed component
- All integration tests involving the changed component's interfaces (IFC-nnn)
- Regression suite (always required for any change)
- Safety Acceptance tests for changed components if safety-relevant (coordinate with CSCO for scope)

2.2 Identify tests that can be safely skipped (components not affected by the change, confirmed by traceability to unaffected APP-nnn/DE-nnn/TC-nnn entries).

2.3 Classify regression scope:
- **Minor**: run regression suite only; no acceptance criterion re-verification required
- **Significant**: re-run acceptance criteria for affected WPs + regression
- **Major**: re-run all affected phase's acceptance criteria + full regression
- **Safety-Critical**: re-run all Safety Acceptance tests for affected components + full regression; CSCO co-designs regression scope

2.4 Estimate effort: number of test cases to re-run, estimated time (in sprint-days). Deliver to PM for sprint planning.

### Step 3 — Update Test Strategy

3.1 If the change adds new components, interfaces, or data entities: add new acceptance criteria to TS §3.4. Update test scope (§3.2).

3.2 If the change removes components: retire the corresponding acceptance criteria (mark as `retired: true`; retain for audit trail). Update test scope.

3.3 If the change modifies a component's interface or behaviour: revise affected acceptance criteria.

3.4 If safety-relevant components are added or their safety classification changes: coordinate with CSCO for new Safety Acceptance test criteria.

3.5 Increment TS version (e.g., 1.0.0 → 1.1.0 for minor updates; 1.0.0 → 2.0.0 for major change scope revision). Re-baseline TS. Emit `artifact.baselined`.

3.6 Deliver updated TS to SwA for AC acceptance criteria alignment if AC is being revised in parallel.

### Step 4 — Deliver Regression Impact Assessment

4.1 Produce Regression Impact Assessment document:
- Change Record reference (CR-nnn)
- Regression scope classification (Minor/Significant/Major/Safety-Critical)
- Test cases to re-run (list by test type)
- Test cases confirmed safe to skip (with traceability justification)
- New test cases required (if any)
- Estimated effort in sprint-days
- Safety Acceptance test scope (CSCO-confirmed if safety-relevant)

4.2 Write to `qa-repository/regression-assessments/RA-<cr-id>.md`.

4.3 Create `handoff.created` to PM. PM uses this for sprint planning of the Phase H implementation sprint.

---

## Feedback Loop

**No multi-iteration feedback loop for this skill.** The Regression Impact Assessment is a consulting deliverable. If PM finds the scope estimate unclear, PM routes a clarification request to QA as a CQ. QA responds within the current sprint. Maximum 1 clarification iteration.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="test-strategy"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-001 | Change Record analysis reveals the change would invalidate a Safety Acceptance test that was previously passing | S1 | Emit to CSCO (immediate) and PM; do not baseline TS update until CSCO confirms revised safety test scope |
| ALG-003 | Change introduces a new regulatory or compliance testing obligation not previously in the TS | S1 | Emit to CSCO (immediate) and PM; QA cannot define compliance test criteria without CSCO input |

---

## Outputs

| Output | Path | EventStore Event |
|---|---|---|
| Regression Impact Assessment | `qa-repository/regression-assessments/RA-<cr-id>.md` | `handoff.created` (to PM) |
| Updated Test Strategy | `qa-repository/test-strategy/TS-<nnn>-<x.y.0>.md` | `artifact.baselined` |

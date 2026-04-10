---
skill-id: QA-PHASE-G
agent: QA
name: phase-g-execution
display-name: Phase G — Test Execution and Compliance Assessment
invoke-when: >
  Each Solution Sprint starts and QA has received a PR-ready handoff from DE and a Deployment
  Record confirming staging deployment; QA executes tests and produces Test Execution Reports.
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [G]
trigger-conditions:
  - sprint.started (phase=G, sprint-type=solution)
  - handoff.created (handoff-type=pr-ready-for-review, to=qa-engineer)
  - artifact.baselined (artifact-type=deployment-record)
entry-points: [EP-0, EP-G]
primary-outputs: [Test Execution Report, Defect Register, Compliance Assessment contribution]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase G — Test Execution and Compliance Assessment

**Agent:** QA Engineer  
**Version:** 1.0.0  
**Phase:** G — Implementation Governance  
**Skill Type:** Phase primary — test execution + governance  
**Framework References:** `agile-adm-cadence.md §6.8`, `raci-matrix.md §3.9`, `framework/artifact-schemas/test-strategy.schema.md`, `framework/artifact-schemas/architecture-contract.schema.md`, `algedonic-protocol.md`, `discovery-protocol.md`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Test Strategy (`TS`) | QA (self-produced) | Baselined (v1.0.0+) | Hard prerequisite — QA may not begin Phase G execution without baselined TS |
| Architecture Contract (`AC`) per Solution Sprint | Software Architect/PE | Baselined (v1.0.0+) | Defines acceptance criteria and authorised SBBs for each sprint |
| PR-ready handoff | Implementing Developer | `handoff.created` received | Signals that a Work Package is ready for QA testing |
| Deployment Record | DevOps | Current sprint | Confirms deployment to test environment; QA does not test against undeployed code |
| Safety Constraint Overlay (`SCO`) | CSCO | Current baselined version | Governs safety-relevant components; required for Safety Acceptance test execution |
| `sprint.started` event | PM | Emitted per Solution Sprint | Hard prerequisite — QA does not begin sprint testing without this event |

---

## Knowledge Adequacy Check

### Required Knowledge

- Full Test Strategy — test types, coverage targets, acceptance criteria, defect classification, entry/exit criteria
- Current Architecture Contract — which ABBs and SBBs are in force; specific acceptance criteria AC-nnn for this sprint
- Deployment status — is the feature deployed to the test environment? On which environment?
- Safety-relevant component identification — which APP-nnn and DE-nnn entries are safety-relevant in this sprint

### Known Unknowns

| Unknown | Blocking | CQ Target | Notes |
|---|---|---|---|
| Test environment not available | Yes — cannot execute without environment | DevOps (via PM) | Raise ALG-013 if environment unavailable and sprint is blocked |
| Acceptance criterion in AC is ambiguous or unstestable | Yes — cannot verify without clarity | SwA (via PM) | Raise structured feedback to SwA (Feedback Loop A) |
| Business policy required for pass/fail decision (e.g., SLA threshold) | Yes for that criterion | User (via PM) | Raise CQ to user |
| Safety-relevant component identification not confirmed by CSCO | Yes for Safety Acceptance tests | CSCO (via PM) | Raise CQ; proceed with other test types while awaiting CSCO confirmation |

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="QA", phase="G", artifact_type="test-strategy")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="G")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0 — Discovery Scan (Sprint Entry)

At the start of each Solution Sprint, execute the Discovery Scan per `framework/discovery-protocol.md §2`.

**Expected sources for each sprint:**
- `qa-repository/defect-register/` — open defects from previous sprints that may affect this sprint
- `technology-repository/architecture-contract/` — current AC for this sprint
- `devops-repository/deployment-records/` — most recent deployment record
- `delivery-repository/pr-records/` — which PRs have been submitted for this sprint's WPs
- EventStore state — open algedonic signals, open CQs, prior sprint compliance history

**This prevents re-testing work that is already tested and re-raising CQs that are already answered.**

---

### Sprint Lifecycle (repeated for each Solution Sprint SS-nnn)

#### Step 1 — Sprint Entry Validation

1.1 Confirm `sprint.started` has been emitted for SS-nnn.

1.2 Confirm Architecture Contract for this sprint is baselined (AC-nnn v1.0.0+). If AC is at draft version (0.x.x): halt; raise ALG-008 to PM; do not begin testing.

1.3 Confirm test environment is available per TS §3.8 and the Deployment Record confirms deployment to Staging. If environment is unavailable: raise ALG-013 to PM; halt sprint test execution pending resolution.

1.4 Confirm all Test Strategy entry criteria are met: unit tests pass (per DE report), deployment successful (per Deployment Record), test data prepared.

#### Step 2 — Test Execution

2.1 For each Work Package in the current sprint scope, execute all applicable test types from the TS:

**Unit and Integration tests (coordinated with DE):**
- Review DE's unit test report (in `delivery-repository/test-reports/`). Confirm coverage meets TS threshold.
- Execute integration tests for all interfaces exercised by this sprint's WPs. Each IFC-nnn in scope must be exercised by at least one integration test.

**System / End-to-End tests:**
- Execute system tests for each value stream (VS-nnn) that is partially or fully implemented by this sprint's WPs.
- Record pass/fail per acceptance criterion AC-nnn from the AC.

**Performance tests (at milestone sprints per TS):**
- Execute performance tests per TS §3.7 NFR specifications.
- Record actual measurements vs. NFR thresholds.
- Any NFR threshold miss is a defect. Classify per TS §3.5 (typically Severity 2 if a functional path is affected; escalate to Severity 1 if safety-relevant performance threshold is missed).

**Security tests:**
- Execute OWASP Top 10 baseline checks per TS §3.3.
- Review pipeline security gate outputs (SAST, dependency scan) from DevOps; record whether gates passed.
- Any security vulnerability at High severity or above is a Severity 1 defect.

**Regression tests:**
- Execute full regression suite on each deployment to Staging.
- Any regression failure is a Severity 2 defect at minimum (Severity 1 if it affects a previously-passing safety acceptance test).

**Safety Acceptance tests (for safety-relevant components):**
- Execute Safety Acceptance tests per CSCO-approved criteria in TS.
- Record pass/fail per SCO constraint.
- Any Safety Acceptance test failure: immediately raise ALG-013 (Severity 1 — safety-critical defect). Halt deployment of affected component. Notify CSCO immediately without waiting for sprint boundary.

#### Step 3 — Defect Management

3.1 For each defect found:
- Assign a Defect ID: `DEF-<engagement-id>-<nnn>`
- Record in Defect Register with: ID, description, severity, test type, AC-nnn reference (if applicable), reproduction steps, affected component (APP-nnn or TC-nnn), sprint detected

3.2 Route defect to the responsible agent based on classification:
- **Functional defect** (implementation incorrect) → DE: create `handoff.created` to DE
- **Architecture non-conformance** (implementation deviates from AC constraint) → SwA via PM: create `handoff.created` to PM
- **Environment defect** (infrastructure/configuration issue) → DevOps via PM: create `handoff.created` to PM
- **Acceptance criterion ambiguity** (criterion cannot be verified) → SwA for AC clarification: structured feedback (Feedback Loop A)
- **Safety-critical defect** → CSCO immediately (ALG-013); also notify PM and SwA

3.3 Update Defect Register status as defects are fixed and re-tested. A defect is only marked `resolved` after QA has performed a re-test and confirmed the fix. Producing agent's claim of "fixed" does not close a defect.

#### Step 4 — Produce Test Execution Report

4.1 At the end of each Solution Sprint's test execution cycle, produce a Test Execution Report.

4.2 Write to `qa-repository/test-execution/TER-SS-<nnn>.md` following TS §3.9 format.

4.3 The TER must include: test type summary table, all open defects (with severity and owner), all resolved defects (with re-test confirmation), acceptance criteria pass/fail by AC-nnn, coverage achieved vs. target.

4.4 Emit `artifact.baselined` for the TER (sprint-level artifact).

#### Step 5 — Produce Compliance Assessment Contribution

5.1 Produce the QA dimension of the AC Compliance Assessment (AC §3.7):
- For each acceptance criterion (AC-nnn): verdict (Compliant / Non-compliant / Partially Compliant / Deferred), evidence reference (TER-SS-nnn), and verified-by (QA sign-off)
- For each architecture constraint (CON-nnn) where test evidence is applicable: verdict and evidence

5.2 Deliver Compliance Assessment contribution to SwA (Feedback Loop B). SwA merges QA and SwA dimensions into the final AC §3.7 and re-baselines the AC.

5.3 QA signs the merged Compliance Assessment (co-sign per AC schema §3.7).

#### Step 6 — Phase G Exit Gate Vote

At the conclusion of all Solution Sprints:

6.1 Perform exit gate checklist:
- [ ] All AC acceptance criteria have test evidence (pass or formally deferred with PM+QA approval)
- [ ] All Severity 1 defects closed and re-test verified
- [ ] All Severity 2 defects closed or formally deferred with PM approval
- [ ] All Safety Acceptance criteria verified (CSCO co-signed, if safety-relevant)
- [ ] Regression suite passed on final Staging deployment
- [ ] All TERs produced and signed off

6.2 Cast `gate.vote_cast` for Phase G exit. Vote `approved` only if all checklist items are satisfied. Vote `blocked` with specific condition list if any item is unsatisfied.

6.3 QA's Phase G exit vote is a gate block if any Severity 1 defect is unresolved. PM cannot pass the Phase G exit gate with an unresolved Severity 1 defect without user-level escalation.

---


## Common Rationalizations (Rejected)

| Rationalization | Rejection |
|---|---|
<!-- TODO: add 2-3 skill-specific rationalization rows -->
| "I can skip discovery because I already know the context from prior sessions" | Discovery is mandatory per Step 0; any skip must be recorded as a PM-accepted assumption with a risk flag; silent assumptions are governance violations |
| "A CQ with a reasonable assumed answer is equivalent to waiting — I'll proceed with the assumption" | Assumed answers must be explicitly recorded in the artifact with a risk flag; they never silently replace CQ answers |

## Feedback Loop

### Feedback Loop A: Acceptance Criterion Clarification (QA ↔ SwA)

**Purpose:** Resolve ambiguous or unverifiable acceptance criteria in the AC.

- **Iteration 1**: QA raises specific ambiguity in writing (criterion ID, ambiguity statement, proposed clarification). SwA responds with revised criterion or explanation.
- **Iteration 2**: QA confirms revised criterion is testable, or raises a second clarification.
- **Termination**: All AC criteria are testable (binary-verifiable by available test methods).
- **Maximum iterations**: 2. Unresolvable after Iteration 2 → ALG-010 to PM.

### Feedback Loop B: Compliance Assessment Co-Production (QA ↔ SwA)

**Purpose:** Produce a complete, joint AC Compliance Assessment.

- **Iteration 1**: QA submits QA dimension; SwA submits SwA dimension. Both merged. Any contradiction identified by either party triggers a joint review.
- **Termination**: Compliance Assessment has no contradictions; both parties sign.
- **Maximum iterations**: 1 (joint production). Unresolvable contradiction → ALG-010 to PM.

### Feedback Loop C: Defect Resolution Verification (QA ↔ DE)

**Purpose:** Confirm defect fixes are effective before closing.

- **Iteration 1**: DE notifies fix complete. QA re-tests.
- **Iteration 2**: If fix introduces a regression, QA notifies DE with regression detail. DE fixes regression. QA re-tests.
- **Termination**: Defect verified fixed with no new regressions.
- **Maximum iterations**: 2 per defect (3 test executions total: original + fix + regression re-test). Beyond 2 iterations without resolution: escalate to PM as ALG-010 for Severity 1-2 defects.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="test-strategy"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---


## Red Flags

Pre-escalation observable indicators. Raise an algedonic signal or CQ if two or
more of these are true simultaneously:

<!-- TODO: add 5-7 role-specific observable indicators for this skill -->
- Outputs section of the primary artifact is blank after completing the procedure
- Any required input artifact is missing and no CQ has been raised
- Feedback loop iteration count has reached the maximum with no resolution

## Algedonic Triggers <!-- workflow -->

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-001 | Test execution reveals that an implementation decision violates a safety constraint in the SCO | S1 | Halt deployment of affected component; emit to CSCO (immediate) and PM (concurrent) |
| ALG-008 | QA is asked to begin test execution against a draft Architecture Contract (v0.x.x) | S2 | Do not begin testing; emit to PM; await baselined AC |
| ALG-010 | Acceptance criterion clarification loop exhausted (2 iterations) without resolution | S3 | Emit to PM for adjudication |
| ALG-013 | Test execution reveals a Severity 1 defect in a safety-relevant component | S1 | Halt deployment of affected component immediately; emit to CSCO (immediate) and SwA; PM notified concurrently |
| ALG-013 | Test environment unavailable for ≥ 1 sprint cycle, blocking all Phase G execution | S1 | Emit to PM; PM routes to DevOps; sprint cannot close without test evidence |

---


## Verification

Before emitting the completion event for this skill, confirm:

<!-- TODO: extend with skill-specific checklist items -->
- [ ] All blocking CQs resolved or documented as PM-accepted assumptions
- [ ] Primary output artifact exists at the required minimum version
- [ ] CSCO sign-off recorded where required (`csco-sign-off: true`)
- [ ] All required EventStore events emitted in this invocation
- [ ] Handoffs to downstream agents created
- [ ] Learning entries recorded if a §3.1 trigger was met this invocation
- [ ] Memento state saved (End-of-Skill Memory Close)

## Outputs

| Output | Path | EventStore Event |
|---|---|---|
| Test Execution Report (per sprint) | `qa-repository/test-execution/TER-SS-<nnn>.md` | `artifact.baselined` |
| Defect Register (maintained throughout Phase G) | `qa-repository/defect-register/DR-<engagement>-current.md` | Updated in place; `handoff.created` per defect routed |
| Compliance Assessment contribution (QA dimension) | `qa-repository/compliance-assessment/CA-SS-<nnn>-QA.md` | `handoff.created` (to SwA for merge) |
| Phase G exit gate vote | EventStore | `gate.vote_cast` |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="G", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

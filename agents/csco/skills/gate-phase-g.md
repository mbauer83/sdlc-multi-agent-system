---
skill-id: CSCO-GATE-G
agent: CSCO
name: gate-phase-g
display-name: Phase G Safety Spot-Checks and G-Exit Gate
invoke-when: >
  (Mode 1) PM emits a spot-check request (handoff.created from PM with
  handoff_type=spot-check-request) for a specific implementation item during a
  Phase G Solution Sprint. (Mode 2) QA Compliance Assessment is baselined
  (artifact.baselined from QA, artifact_type=compliance-assessment) or PM requests
  G-exit gate review. CSCO operates in both modes concurrently during Phase G.
trigger-phases: [G]
trigger-conditions:
  - handoff.created from PM (handoff_type=spot-check-request)
  - artifact.baselined from QA (artifact_type=compliance-assessment)
  - sprint.started (phase=G) — CSCO activates for the sprint duration
  - cq.answered resolving a blocking Phase G CSCO safety CQ
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-G]
primary-outputs:
  - Spot-check Record(s) (scr-<sprint>-<seq>.md) — one per PM spot-check request
  - G-Exit Gate Record (gr-G-exit-1.0.0.md)
  - gate.vote_cast for G-exit gate
  - SCO Phase G annotation (if violations found; minor version increment)
complexity-class: standard
version: 1.0.0
---

# Skill: Phase G Safety Spot-Checks and G-Exit Gate

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** G — Implementation Governance
**Skill Type:** Phase G — two-mode gate activity: implementation spot-checks + G-exit gate vote
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (constraint verification against UCAs)
**Framework References:** `agile-adm-cadence.md §6.7`, `raci-matrix.md §3.7`, `framework/artifact-schemas/architecture-contract.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| SCO — all phases (A through D) | CSCO — safety-repository/safety-constraint-overlay/ | All phase baselines at 1.0.0 | Full SCO is the reference for all constraint checks; if any phase baseline is absent, CSCO flags the gap before accepting G-exit |
| Architecture Contract (AC) | SwA — technology-repository/architecture-contract/ | Baselined at version 1.0.0 | Primary reference for what Phase G implementations must satisfy; CSCO verifies SCO constraints are reflected in AC |
| QA Compliance Assessment (CA) | QA — qa-repository/ | Baselined at 1.0.0 for G-exit review; in-progress for mid-sprint spot-checks | Mode 2 (G-exit) requires CA to be baselined; Mode 1 (spot-check) may reference in-progress CA |
| Spot-check target (Mode 1 only) | PM handoff | PR, deployment record, test report, or configuration item | PM specifies which implementation item to review and which SCO constraints are suspected to be at risk |
| PR log and test reports | DE / QA — delivery-repository/, qa-repository/ | Current sprint's merged PRs and test reports | CSCO reads these for Mode 1 spot-checks and for G-exit context |
| sprint.started event | PM | Must be emitted for Phase G sprint | CSCO activates for the sprint duration on this event |

---

## Knowledge Adequacy Check

### Required Knowledge

- All SCO constraints (SC-nnn) through Phase D: which constraints apply to implementation (G-phase) as opposed to earlier design phases.
- The Architecture Contract's compliance acceptance criteria: what the AC specifies as satisfactory for each constrained area.
- Implementation-level safety verification patterns: what evidence (test results, configuration audit, code review finding) constitutes proof that an SC-nnn constraint is satisfied at Phase G.
- QA Compliance Assessment schema: how CA is structured, what sections map to which SCO constraints, and how to identify uncovered constraints.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Which SC-nnn constraints are testable vs. auditable vs. procedural | No — CSCO classifies each constraint's verification method based on constraint type and Phase D SCO annotations | — | Spot-check Record, G-exit Gate Record |
| Specific implementation detail of a flagged PR (code-level) | No — CSCO reviews architectural compliance, not code correctness; DE or SwA are the code-level reviewers | SwA (if architecture compliance question) | Spot-check Record |
| Whether a QA test covers a specific UCA | No — CSCO infers from test description; if uncertain, raises a non-blocking CQ to QA | QA | G-exit Gate Record (constraint coverage assessment) |

### Clarification Triggers

CSCO raises a CQ when:

1. **SCO constraint not covered by CA:** The QA Compliance Assessment does not include a test or audit finding that addresses an SC-nnn constraint applicable to Phase G implementation. If the constraint is safety-critical (SC classification S1 or S2): blocking CQ to QA; G-exit gate cannot be cast until coverage is confirmed or constraint is accepted as residual risk.
2. **AC does not reference SCO constraint:** The Architecture Contract fails to include an acceptance criterion for an SC-nnn constraint. This is a compliance gap in the AC, not the CA. CSCO raises a CQ to SwA to update the AC.
3. **Spot-check target not identifiable from PM handoff:** PM's spot-check request does not specify which SCO constraints to assess against, or the target artifact is not accessible. CSCO raises a non-blocking CQ to PM for clarification; begins the spot-check review on any identifiable constraints.

---

## Mode 1 — Implementation Spot-Check

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="CSCO", phase="G", artifact_type="safety-constraint-overlay")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan (Mode 1)

Execute the Discovery Scan per `framework/discovery-protocol.md §2` before each spot-check:

1. **Layer 1 — Engagement State:** Read all SCO phase baselines from safety-repository/; read the AC from technology-repository/architecture-contract/; read the PM handoff requesting the spot-check (identifies target item and suspected constraints); read the specific PR or deployment record identified in the handoff; read algedonic-log/ for any open ALG signals affecting Phase G.
2. **Layer 2 — Enterprise Standards:** Read enterprise-repository/standards/ for applicable Phase G standards (coding standards, security testing requirements, deployment security standards) relevant to the spot-check target.
3. **Layer 3 — External Sources and Target Repo:** If target-repo is configured: read the specific files or configuration items referenced in the PR or deployment record being spot-checked.
4. **Layer 5 — Inference:** Note which SCO constraints are theoretically exercised by the implementation item being reviewed; annotate inferred coverage links.

---

### Step M1-1 — Identify Applicable Constraints

From the PM handoff: identify the specific SC-nnn constraints to be assessed for this spot-check target.

If the PM handoff does not specify constraints: CSCO selects the applicable constraints independently by:
- Identifying the Phase and capability domain of the implementation item
- Reading the relevant SCO sections (§5 and §7 UCAs) for constraints applicable to that domain
- Limiting the spot-check scope to constraints that are testable or auditable at Phase G implementation depth

Record the applicable SC-nnn list in the Spot-check Record header.

---

### Step M1-2 — Review the Spot-Check Target

Review the specified implementation item (PR, deployment record, test report, or configuration item) against each SC-nnn constraint identified in Step M1-1:

For each applicable SC-nnn constraint:

1. **Identify the constraint's verification criterion:** What must be true in the implementation for the constraint to be satisfied? Classify: testable (test result provides evidence), auditable (code or configuration provides evidence), procedural (process record provides evidence).
2. **Assess the evidence in the target item:** Does the PR diff / deployment record / test report provide evidence of constraint satisfaction?
3. **Record the finding:** Pass (evidence present and sufficient) / Fail (constraint violated or evidence absent) / Deferred (constraint verification belongs to another item or future sprint; note which).

A "Fail" finding requires a structured feedback item: SC-nnn violated, nature of the violation, the specific line or configuration that violates it (if identifiable), and the minimal remediation required.

---

### Step M1-3 — Produce Spot-check Record and Emit Events

Author `safety-repository/spot-check-records/scr-<sprint-id>-<seq>.md`:

- **Header:** Sprint ID, sequence number, target item (PR reference, deployment record ID, or configuration item path), date, SC-nnn constraints assessed.
- **Findings table:** One row per SC-nnn assessed — constraint ID, verification method, evidence reviewed, finding (Pass / Fail / Deferred), finding detail.
- **Actions required:** For each Fail finding: the responsible agent (DE for implementation, DO for deployment/config, SwA for architecture contract update), the required remediation, and the blocking status (blocking current PR merge / blocking sprint close / blocking G-exit).

Emit `artifact.baselined` for the Spot-check Record.
Emit `handoff.created` to PM with spot-check outcome summary and any blocking actions.

If any Fail finding is safety-critical (violates S1 or S2 constraint): raise ALG-007 immediately (do not wait for PM routing).

---

## Mode 2 — G-Exit Gate Review

### Step 0 — Discovery Scan (Mode 2)

Execute the Discovery Scan per `framework/discovery-protocol.md §2`:

1. **Layer 1 — Engagement State:** Read all SCO phase baselines; read the AC; read the QA Compliance Assessment (baselined); read all Spot-check Records produced during this Phase G engagement (to identify any open Fail findings); read algedonic-log/ for any open ALG signals; read handoff-log/ for PM's G-exit review request.
2. **Layer 2 — Enterprise Standards:** Read enterprise-repository/standards/ for any Phase G exit criteria in applicable compliance frameworks.
3. **Layers 3–5:** Standard discovery; annotate inferred fields.

---

### Step M2-1 — Map SCO Constraints to Compliance Assessment Coverage

For every SC-nnn constraint in the SCO that is applicable at Phase G (i.e., constraints of type: Technical, Operational, Regulatory — these are implementation-layer constraints):

1. Identify whether the QA Compliance Assessment addresses this constraint — either through a specific test finding (test ID, pass/fail status) or an explicit audit finding.
2. Mark each SC-nnn as: **Covered** (CA provides sufficient evidence), **Partial** (CA addresses the constraint area but evidence is incomplete), or **Uncovered** (no CA entry maps to this constraint).
3. For Partial or Uncovered constraints: determine whether the gap is: (a) a missing test (QA gap), (b) a missing constraint citation in the AC (SwA gap), or (c) a residual risk already accepted by the user.

Record the mapping in the G-Exit Gate Record.

---

### Step M2-2 — Reconcile Spot-check Record Findings

Review all Spot-check Records produced during Phase G:

- **Open Fail findings** (not remediated before G-exit request): each is a potential veto condition.
- **Deferred findings**: each must be assessed — is the deferral to Phase H, or is it blocking G-exit?
- **Pass findings**: record as constraint evidence in the G-exit record.

If an open Fail finding involves an S1 safety-critical constraint: G-exit gate vote is **Veto** regardless of all other findings.

---

### Step M2-3 — Cast G-Exit Gate Vote

**Approve** if: all SC-nnn Phase G constraints are Covered in the CA or covered by Spot-check Pass findings; no open Fail spot-check findings for S1 or S2 constraints; all open Fail findings are for non-critical constraints and PM has accepted them as tracked items for Phase H.

**Conditional** if: one or more Partial coverage entries exist for S3 or below constraints; or one or more Phase G constraints are deferred to Phase H with PM's explicit agreement. Specify: the constraint IDs deferred, the Phase H artifact where coverage is required, and the sprint deadline.

**Veto** if: one or more S1 or S2 constraints are Uncovered in the CA with no accepted residual risk; or one or more open Fail spot-check findings for S1 or S2 constraints remain. Cite each: SC-nnn ID, coverage gap description, minimal remediation required (specific test type or implementation change).

Emit `gate.vote_cast` for the G-exit gate.

---

### Step M2-4 — Produce G-Exit Gate Record and Emit Events

Author `safety-repository/gate-records/gr-G-exit-1.0.0.md`:
- SCO constraints reviewed: full constraint-to-coverage mapping table
- Spot-check records cited: all SCR IDs with their final finding status
- Vote result and rationale
- Any conditional requirements with responsible agent and deadline
- Open findings transferred to Phase H (if conditional or deferred)

Emit `artifact.baselined` for the Gate Record.
Emit `handoff.created` to PM with G-exit gate vote status.
Emit `handoff.created` to QA with any constraint coverage gaps requiring CA update.
Emit `handoff.created` to SwA with any AC gaps identified during G-exit review.

If vote is Approve or Conditional: emit `artifact.baselined` for SCO Phase G annotation (adding Phase G constraint verification status to SCO §11 Phase Gate Summary — minor version increment; no new constraints added at Phase G).

---

## Feedback Loop

**Maximum iterations: 2.** After Iteration 2 without G-exit approval: raise ALG-010 (inter-agent deadlock) to PM.

**Mode 1 (spot-check) iterations:** Spot-check Records have their own bounded feedback cycle:
- Iteration 1: CSCO emits Spot-check Record with Fail findings; DE/DO/SwA remediate; resubmit PR or corrected item.
- Iteration 2: CSCO reviews remediation only. If Fail finding persists: CSCO records second Fail and escalates to PM as a sprint blocker. CSCO does not do a third round of spot-check review — PM manages sprint resolution.

**Mode 2 (G-exit) iterations:**
- Iteration 1: Veto with specific SC-nnn gaps. QA updates CA or DE/DO remediate and resubmit. PM re-requests G-exit review.
- Iteration 2: CSCO reviews only the updated CA sections and remediated items. If any S1/S2 constraint remains Uncovered: second veto. PM escalates to user.

**Termination conditions:**
- **Satisfied:** All Phase G constraints Covered or conditionally deferred. CSCO emits G-exit `gate.vote_cast (approve)`. Loop closes.
- **User risk acceptance:** User accepts residual coverage gaps. PM records in decision log. CSCO marks in SCO §11 and G-exit Gate Record as accepted residuals. Emits `gate.vote_cast (approve with accepted residuals)`.
- **Deadlock (ALG-010):** After Iteration 2 with S1/S2 gap unresolved. PM adjudicates; CSCO veto stands throughout.

### Personality-Aware Conflict Engagement

**CSCO ↔ QA (compliance assessment completeness):**

QA may argue that a specific SCO constraint is implicitly covered by a test even though no explicit mapping exists in the CA. CSCO's stance: implicit coverage is insufficient. The CA must contain an explicit test-to-constraint mapping. CSCO provides the specific SC-nnn ID and asks QA to add the mapping if the test genuinely covers it, or to explain the gap. If QA can demonstrate that a test covers the constraint but the CA documentation is simply incomplete: CSCO accepts after CA is updated — not before. Documentation is not bureaucracy; it is the audit trail.

**CSCO ↔ SwA (architecture contract gaps):**

SwA may argue that an SC-nnn constraint omitted from the AC is covered by the overall architecture design. CSCO's stance: the AC is the binding contract for Phase G; if a constraint is not in the AC, DE had no guidance to implement it, and there is no contractual basis to require compliance. CSCO identifies the gap and requires AC update or risk acceptance — not post-hoc claims of implicit coverage.

**CSCO ↔ PM (G-exit sprint pressure):**

PM may argue that the G-exit gate is holding up Phase H and request CSCO to conditionally approve while gaps are tracked. CSCO's stance: CSCO will issue a conditional approval for S3 and below uncovered constraints where PM accepts Phase H tracking. CSCO will not approve conditionally for S1 or S2 uncovered constraints — these are blocking regardless of sprint pressure. CSCO communicates the exact minimal action required (specific test or configuration change) to achieve approval, not a comprehensive list.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="safety-constraint-overlay"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

- **ALG-001 (S1 — Safety-Critical):** A spot-check or G-exit review reveals that an S1 safety-critical SCO constraint has been violated in the deployed implementation and no feasible remediation can be applied within the current sprint (e.g., a security architecture bypass, a missing authentication gate on a safety-critical operation, or a data constraint violation that cannot be rolled back without data loss). Raised immediately; concurrent escalation to CSCO (self) and PM; affected deployment or feature is halted.
- **ALG-007 (S1 — Governance Violation):** Implementation is merged to the main branch without passing a CSCO spot-check on a safety-critical item, or the G-exit gate is declared by PM without CSCO's G-exit vote having been cast. Raised immediately.
- **ALG-010 (S3 — Inter-Agent Deadlock):** After two iterations, QA and CSCO cannot agree on whether CA coverage satisfies an SC-nnn constraint, or DE/DO and CSCO cannot agree on the interpretation of a constraint for implementation purposes. Raised to PM.

---

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Spot-check Record(s) | `SCR-<sprint>-<seq>` | `safety-repository/spot-check-records/scr-<sprint>-<seq>.md` | `artifact.baselined` |
| G-Exit Gate Record | `GR-G-EXIT-1.0.0` | `safety-repository/gate-records/gr-G-exit-1.0.0.md` | `artifact.baselined` |
| Gate Vote — G-exit | (event payload) | EventStore | `gate.vote_cast` |
| SCO Phase G annotation | `SCO-G-<minor-version>` | `safety-repository/safety-constraint-overlay/sco-G-<minor>.md` | `artifact.baselined` (if any violations found requiring SCO update) |
| Structured feedback to QA | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` |
| Structured feedback to SwA | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` |

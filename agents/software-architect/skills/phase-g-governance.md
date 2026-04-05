---
skill-id: SwA-PHASE-G
agent: SwA
name: phase-g-governance
display-name: Phase G — Implementation Governance
invoke-when: >
  Phase F gate has passed and each Solution Sprint starts; SwA authors the Architecture
  Contract, reviews PRs for compliance, and issues Compliance Notices throughout Phase G.
trigger-phases: [G]
trigger-conditions:
  - gate.evaluated (from_phase=F, result=passed)
  - sprint.started (phase=G, sprint-type=solution)
  - handoff.created (handoff-type=pr-ready-for-review, to=software-architect)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G]
primary-outputs: [Architecture Contract, Architecture Compliance Notices, Compliance Assessment contribution]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase G — Implementation Governance

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** G — Implementation Governance  
**Skill Type:** Governance + Architecture production  
**Framework References:** `agile-adm-cadence.md §6.8`, `raci-matrix.md §3.9`, `framework/artifact-schemas/architecture-contract.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`

---

## Runtime Tooling Hint

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Implementation Plan (`IP`) | Project Manager | **Baselined** (v1.0.0+) | Provides work packages and Solution Sprint scope for each AC |
| Solution Sprint Plan | Project Manager | **Baselined** (v1.0.0+) | Authorises the Implementation Stream; specifies sprint entry/exit conditions |
| Test Strategy (`TS`) | QA Engineer | **Baselined** (v1.0.0+) | Provides acceptance criteria that are incorporated into each AC |
| Safety Constraint Overlay (`SCO`) — Phase D update | CSCO | **Baselined** (v1.0.0+) | Governs which work packages are safety-relevant; required for CSCO sign-off determination |
| Technology Architecture (`TA`) | SwA | **Baselined** (v1.0.0+) | Self-produced; provides TC-nnn, ADR-nnn, and deployment constraints for each AC |
| Application Architecture (`AA`) | Solution Architect | **Baselined** (v1.0.0+) | Provides APP-nnn and IFC-nnn ABBs in force per sprint |
| Data Architecture (`DA`) | Solution Architect | **Baselined** (v1.0.0+) | Provides DE-nnn ABBs in force per sprint |
| Sprint kickoff event per Solution Sprint | PM | `sprint.started` emitted | A new Architecture Contract is authored at each Solution Sprint kickoff |

**RACI note:** SwA is **●** (accountable) for the Architecture Contract. PM is **●** for Governance Checkpoint Records. QA is **●** for Compliance Assessment (with SwA ○ contribution). The AC is authored by SwA; QA and PM sign-off within their respective roles.

---

## Knowledge Adequacy Check

### Required Knowledge

- Full Implementation Plan — all work packages, their acceptance criteria, and sprint assignments
- Full Test Strategy — acceptance criteria per work package (these are copied into the AC verbatim)
- Current SCO — which work packages touch safety-relevant components (determines CSCO sign-off requirement)
- All baselined architecture artifacts (AA, DA, TA) at the versions that govern this sprint
- PR and deployment records from the previous sprint (to assess cumulative compliance state)

### Known Unknowns

The following gaps are predictably present at Phase G entry or during ongoing governance:

1. **Implementation approach within a work package**: The Architecture Contract specifies *what* must be built (ABBs, constraints, acceptance criteria) but not *how* the Developer implements it. The SwA must govern compliance without constraining legitimate implementation choices within the AC's authorised SBB space.
2. **Emerging technical debt**: During implementation, the Developer may identify technical constraints not visible at architecture design time. The SwA must distinguish between legitimate implementation feedback (requiring AC revision) and scope creep (requiring a Change Record).
3. **Defect versus non-compliance**: A test failure can indicate either a defect in implementation (within AC scope) or a misspecified acceptance criterion in the AC itself. The SwA must assess which case applies before issuing a Compliance Notice.

### Clarification Triggers

Raise a CQ (`target: User`) if:
- An acceptance criterion in the Test Strategy cannot be verified without user-specific environmental access that has not been provisioned
- A compliance determination requires knowing a business policy (e.g., "does a 2-second response time constitute an SLA breach?") that is not specified in any artifact

Route structured feedback to QA (`target: QA Engineer`) if:
- An acceptance criterion in the Test Strategy is ambiguous or contradicts the AC's constraint statement
- A test report does not provide sufficient evidence to make a binary compliance determination

Route to PM if:
- A compliance issue has been raised and the Developer/DevOps has not responded within the current sprint boundary (non-responsiveness may be ALG-015)

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="G", artifact_type="architecture-contract")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0.S — Standards and Coding Guidelines Discovery

Before producing or updating any Architecture Contract, scan the following in order:

1. `technology-repository/coding-standards/` — read the full active coding standards document for the target language/platform stack. The AC §3 (Implementation Constraints) must reference coding standards by name and version.
2. `enterprise-repository/standards/` — retrieve current SIB (Standards Information Base) entries for all technologies appearing in the sprint's IC catalog. Any technology not in the SIB requires an ADR before inclusion in the AC.
3. `technology-repository/architecture-decisions/` — retrieve ADRs relevant to the work packages in scope. AC §2 (ABBs in Force) must be consistent with relevant ADRs.

This step is non-skippable. If `technology-repository/coding-standards/` does not exist, raise CQ to PM before producing the AC.

---

### Architecture Contract Production (per Solution Sprint)

The Architecture Contract is produced at each Solution Sprint entry. A new AC is not shared across sprints — each sprint has its own AC referencing the specific work packages in scope for that sprint.

#### Step AC-1 — Read Sprint Scope

AC-1.1 At each `sprint.started` event for a Solution Sprint, read the sprint's work package scope from the Solution Sprint Plan.

AC-1.2 Identify the specific WP-nnn entries assigned to this sprint. For each WP-nnn, retrieve:
- ABBs in force: which APP-nnn, DE-nnn, and TC-nnn are being realised or relied upon
- Authorised SBBs: which specific products/libraries/infrastructure components (from the IC catalog) are authorised for this sprint
- Acceptance criteria: the specific criteria from the Test Strategy that govern this sprint

AC-1.3 Identify which WP-nnn entries are safety-relevant (flagged in IP). If any, CSCO sign-off is required before the AC is considered signed and the sprint implementation may begin.

#### Step AC-2 — Author the Architecture Contract

AC-2.1 Produce the Architecture Contract document per `framework/artifact-schemas/architecture-contract.schema.md`:

**AC Header (§3.1):**
```yaml
artifact-type: architecture-contract
artifact-id: AC-nnn
version: 1.0.0
phase: G
status: draft → signed
owner-agent: software-architect
produced-in: <sprint-id>
path: technology-repository/architecture-contract/AC-nnn-1.0.0.md
depends-on: [IP-nnn, TS-nnn, AA-nnn, DA-nnn, TA-nnn, SCO-nnn]
consumed-by: [Implementing Developer, DevOps, QA]
safety-relevant: <true|false>
csco-sign-off: <true|false>
pm-sign-off: true
```

**Contract Scope (§3.2):** Identify the Solution Sprint ID, work package references, architecture artifact versions in force, and signatories.

**ABBs in Force (§3.3):** List every APP-nnn, DE-nnn, and TC-nnn that is authoritative for this sprint. For each, state the specific constraint imposed on implementation (e.g., "APP-003 must expose interface IFC-007 as specified; the interface contract is binding and may not be changed without a Change Record").

**Authorised SBBs (§3.4):** List every SBB authorised for use in this sprint — named, versioned products and libraries. Any library, tool, or service not listed here requires a Change Record before it may be introduced to the codebase.

**Architecture Constraints (§3.5):** List non-negotiable constraints derived from AA, DA, TA, and SCO. For each constraint:
- Assign a Constraint ID (CON-nnn)
- State the source artifact (e.g., "TA §3.9, SCO §4.2")
- State the constraint in implementable terms (not architecture language — implementation language)
- Specify severity if violated: "Blocks deployment" (hard violation; deployment must be rolled back) or "Requires waiver" (soft violation; must be justified and approved by SwA)

**Acceptance Criteria (§3.6):** Copy the relevant AC entries from the Test Strategy verbatim. Do not paraphrase. Include test type (unit / integration / contract / performance / security) and verifying agent (QA Engineer).

AC-2.2 **Prohibited Patterns section** (not in schema but required by SwA mandate): Add a section listing patterns explicitly prohibited for this sprint. These are patterns identified during Phase D/E that would violate architecture constraints:
- Prohibited: direct database access from UI components (violates APP layer separation)
- Prohibited: storing plaintext credentials in source control (violates Security constraint CON-nnn)
- Prohibited: synchronous coupling to external services without a circuit breaker (violates resilience constraint CON-nnn)
List all patterns relevant to this sprint's work packages.

**Monitoring and Reporting Requirements** (add to §3.5 as constraints): Specify what observability must be in place for the sprint's deliverables:
- Metrics: which metrics must be emitted (identified in TA observability TC)
- Logs: what log levels and log format are required
- Alerts: which alert thresholds must be configured before deployment to Staging

AC-2.3 The AC Compliance Assessment section (§3.7) is left empty at draft time. It is populated during and after the sprint by QA and SwA jointly.

#### Step AC-3 — Obtain Signatures

AC-3.1 **SwA signs**: SwA self-signs the AC as the producing agent and technology authority. Record SwA sign-off in the AC header.

AC-3.2 **CSCO sign-off (mandatory if safety-relevant)**: If any WP-nnn in this sprint is safety-relevant, the AC must not be distributed to implementing agents until CSCO has signed off. Emit `handoff.created` to CSCO with the AC draft. If CSCO sign-off is not obtained before the sprint's first implementation task begins, raise ALG-009 (S1 — AC without CSCO sign-off for safety-relevant sprint).

AC-3.3 **PM records**: PM records the AC governance acceptance in the Governance Checkpoint Record. PM does not produce AC content; PM records the governance process.

AC-3.4 **Implementing agents accept**: Dev and DevOps receive the AC via handoff and emit `handoff.acknowledged`. Their acknowledgement is their binding acceptance of the AC's constraints.

#### Step AC-4 — Baseline and Distribute

AC-4.1 Baseline the AC at version 1.0.0 once all required signatures are obtained. Emit `artifact.baselined`.

AC-4.2 Distribute via handoff events:
- `handoff.created` → Implementing Developer (AC is the binding implementation contract)
- `handoff.created` → DevOps/Platform Engineer (deployment constraints and monitoring requirements)
- `handoff.created` → QA Engineer (acceptance criteria and compliance assessment responsibility)

AC-4.3 Confirm all three agents emit `handoff.acknowledged`. Record in PM's Governance Checkpoint Record.

---

### Ongoing Governance During Phase G

Phase G is not a single sprint — it spans the entire Implementation Stream. The SwA performs ongoing governance across all Solution Sprints.

#### Step G-1 — Governance Checkpoint Participation

G-1.1 Participate in PM's Governance Checkpoint reviews. For each checkpoint:
- Provide a technology compliance verdict: "In compliance" / "Partial — see Compliance Notice CN-nnn" / "Non-compliant — see CN-nnn, blocking"
- The compliance verdict must be criterion-by-criterion against the AC (§3.3 ABBs, §3.4 SBBs, §3.5 constraints, §3.6 acceptance criteria) — not a holistic judgement.
- Record the verdict in the Compliance Assessment section of the AC (§3.7).

G-1.2 The compliance verdict is based on evidence: test reports from QA, PR reviews by SwA, deployment records from DevOps. Do not issue a compliance verdict without reviewing the evidence.

#### Step G-2 — PR Architecture Compliance Reviews

G-2.1 Review Pull Requests from the Implementing Developer for architecture compliance within the sprint cycle.

G-2.2 PR review scope for SwA: architecture compliance, not code quality. Specifically:
- Does the implementation conform to the APP-nnn component boundaries (no unauthorised cross-component coupling)?
- Are the authorised SBBs (AC §3.4) the only products/libraries used?
- Are the prohibited patterns (AC Prohibited Patterns section) absent?
- Do the interface implementations match the IFC-nnn specifications from the AA Interface Catalog?
- Are monitoring and observability requirements implemented (correct metrics emitted, correct log format)?

G-2.3 PR review result:
- **Compliant**: SwA approves the PR from an architecture compliance perspective (QA approval is separate).
- **Non-compliant**: SwA raises an Architecture Compliance Notice (CN-nnn) — see Step G-4. Do not approve the PR. Note: SwA's non-compliance determination blocks the PR from merging until remediated.
- **Requires discussion**: SwA opens a discussion item in the PR. This is not a compliance notice — it is a clarification request to the Developer. The Developer responds within the current sprint.

#### Step G-3 — Deployment Record Review

G-3.1 Review deployment records from DevOps for environment compliance.

G-3.2 Deployment review scope:
- Are the correct TC-nnn component versions deployed (matching AC §3.4 authorised SBBs)?
- Are environment separation rules respected (no Production data in Staging environments)?
- Are monitoring and alerting configurations as specified in the AC?
- Are network boundaries and security configurations consistent with the Infrastructure Diagram and SCO constraints?

G-3.3 Deployment review result: record in Compliance Assessment. If non-compliant, issue Compliance Notice as per Step G-4.

#### Step G-4 — Architecture Compliance Notice

G-4.1 When non-compliance is detected (in PR review or deployment review), issue an Architecture Compliance Notice.

G-4.2 Architecture Compliance Notice format — write to `technology-repository/architecture-contract/CN-<nnn>-<sprint-id>.md`:
```yaml
notice-id: CN-nnn
sprint: SS-nnn
artifact-ref: AC-nnn
constraint-violated: CON-nnn (or SBB ref, or AC §3.3 ABB ref)
severity: blocking | non-blocking
detected-in: PR-nnn | Deployment record DR-nnn | Test report TR-nnn
```
**Condition**: precise description of the non-compliance (what was found vs. what was required)  
**Required correction**: specific, actionable remediation (what the Developer/DevOps must change)  
**Deadline**: must be resolved before sprint closeout (blocking) or within the next sprint (non-blocking)  
**Resolution record**: (filled by PM upon resolution confirmation)

G-4.3 Deliver Compliance Notice to PM via handoff event. PM records in the Governance Checkpoint Record and routes to the responsible implementing agent (Dev or DevOps).

G-4.4 If a Compliance Notice is not resolved by the deadline:
- Blocking notices: immediately emit ALG-008 (S2 — draft/non-compliant artifact treated as authoritative) and notify PM. No sprint may close with unresolved blocking notices.
- Non-blocking notices: track across sprint boundaries. If still unresolved after 2 sprints, escalate to ALG-008.

#### Step G-5 — Phase G Exit Gate Vote

G-5.1 The SwA votes on the Phase G exit gate. The SwA's vote represents the technology compliance dimension of the gate.

G-5.2 Pre-vote checklist (SwA evaluates):
- [ ] All AC Compliance Assessment sections are populated for all Solution Sprints
- [ ] All blocking Compliance Notices are resolved and documented
- [ ] All AC acceptance criteria are verified as met by QA test reports
- [ ] No safety-relevant component has an unresolved Compliance Notice
- [ ] All authorised SBBs are the versions specified in the ACs (no unauthorised version drift)
- [ ] Deployment records exist and are compliant for all production deployments
- [ ] CSCO spot-check records exist for all safety-relevant sprints

G-5.3 Cast gate vote: emit `gate.vote_cast` with `gate: G-exit`, `vote: approved` (or `vote: blocked` with specific blocking condition list from the pre-vote checklist above). Do not cast an approved vote with any unresolved blocking condition.

---

## Feedback Loop

### Compliance Remediation Loop (SwA ↔ Dev/DevOps)

**Purpose:** Resolve non-compliant implementation or deployment decisions.

- **Iteration 1**: SwA issues Compliance Notice (CN-nnn) specifying violation and required correction. PM routes to responsible agent. Dev/DevOps corrects and resubmits PR or updated deployment record.
- **Iteration 2**: SwA reviews resubmission. If corrected: Compliance Notice resolved; AC Compliance Assessment updated. If still non-compliant: SwA issues final determination.
- **Termination**: Non-compliance resolved; CN-nnn status set to `resolved`.
- **Maximum iterations**: 2. If the iteration-2 resubmission is still non-compliant, escalate to PM as ALG-008 (S2) with specific statement of what remains non-compliant. PM adjudicates within the current sprint.
- **Escalation path**: ALG-008 → PM reviews both positions; PM may mandate acceptance with documented waiver (recorded in AC §3.7 under "exceptions") or may require a third remediation. If PM mandate conflicts with a safety constraint, CSCO is engaged immediately.

### Personality-Aware Conflict Engagement

**Expected tension in this skill:** The SwA (Integrator — Technology) and the DE/DO (Specialists) have a structurally designed tension: the SwA maintains conceptual integrity; the specialists surface what is locally feasible and correct. The compliance loop is not a one-way correction mechanism — it is a dialogue in which the specialist's implementation experience may reveal that an architecture constraint is wrong.

**SwA engagement directive:** A Compliance Notice must contain: (a) the specific AC clause that is violated (AC-ID), (b) the specific implementation behaviour that violates it, and (c) a specific correction requirement. A CN that says "this does not follow clean architecture principles" without a specific AC reference is invalid. When the DE or DO responds with a technical objection, the SwA must engage the argument — if the argument has merit (the constraint was too broadly stated, misapplied in this context, or was not actually required), the SwA revises the AC and documents the revision as a CN resolution. If the argument does not have merit, the SwA restates the requirement with the specific technical reason the objection does not hold. The SwA does not simply re-issue the CN without engaging the objection.

**Resolution directive in this context:** The Compliance Remediation Loop is resolved when: (a) the implementation is demonstrably compliant per a specific AC-ID and the CN is marked resolved, or (b) the AC is revised such that the implementation is now compliant and the revision is baselined. A CN that is closed by ignoring the specialist's objection, rather than engaging it, is a process violation.

### Compliance Assessment Co-Production Loop (SwA ↔ QA)

**Purpose:** Jointly produce the AC Compliance Assessment section.

- **Iteration 1**: QA produces the test-evidence portion of the Compliance Assessment (test types, pass/fail against AC-IDs). SwA produces the architecture-evidence portion (PR review results, deployment review results). Both portions are merged into AC §3.7.
- **Termination**: Compliance Assessment is complete when both QA and SwA have submitted their portions and there are no contradictions (e.g., QA marks an AC ID as passing but SwA's PR review shows a prohibited pattern was used).
- **Maximum iterations**: 1 (joint production; if contradictions exist, SwA and QA resolve by reviewing evidence together before submitting to PM). Unresolvable contradiction escalated to PM via ALG-010.

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

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-001 | PR or deployment contains a safety constraint violation (SCO-referenced constraint breached) | S1 | Halt sprint; emit to CSCO (immediate) and PM (concurrent); block deployment until CSCO resolution |
| ALG-007 | SwA detects any agent has written architecture artifacts outside their designated repository path | S1 | Emit to PM immediately; assess which artifacts are affected and whether they are in the AC's SBB scope |
| ALG-008 | Blocking Compliance Notice unresolved after 2 iterations; non-compliant artifact is being treated as sprint-complete | S2 | Emit to PM; provide written non-compliance statement; sprint cannot close with unresolved blocking CN |
| ALG-009 | AC for a safety-relevant work package is distributed to implementing agents without CSCO sign-off | S1 | Emit to CSCO (immediate) and PM (concurrent); halt implementation on safety-relevant WP until CSCO signs |
| ALG-010 | Compliance remediation loop exhausted (two iterations) without resolution | S3 | Emit to PM for adjudication; provide written compliance statement |
| ALG-012 | SwA detects any agent has proceeded despite a CSCO veto of an AC or AC constraint | S1 | Emit to PM (immediate halt) and CSCO (notify); no further implementation may proceed in affected scope |
| ALG-013 | Test execution reveals a Severity-1 defect in a safety-relevant component | S1 | Halt deployment of affected component; emit to CSCO (immediate) and SwA already notified — coordinate with CSCO on rollback decision |
| ALG-015 | Sprint log or governance checkpoint not updated for two consecutive sprint closings | S4 | Emit to PM (self-alert; PM to remediate) |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Architecture Contract (per Solution Sprint) | `technology-repository/architecture-contract/AC-<nnn>-1.0.0.md` | 1.0.0 | `artifact.baselined` |
| Architecture Compliance Notices | `technology-repository/architecture-contract/CN-<nnn>-<sprint-id>.md` | — | `handoff.created` (to PM) |
| Compliance Assessment contribution (embedded in AC §3.7) | Within AC document | Appended at sprint close (AC v1.1.0) | — |
| AC distribution to Dev | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| AC distribution to DevOps | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| AC distribution to QA | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| G exit gate vote | EventStore | — | `gate.vote_cast` |

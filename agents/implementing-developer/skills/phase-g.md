# Skill: Phase G — Feature Implementation

**Agent:** Implementing Developer  
**Version:** 1.0.0  
**Phase:** G — Implementation Governance  
**Skill Type:** Primary implementation  
**Framework References:** `agile-adm-cadence.md §4.3`, `raci-matrix.md §3.9`, `repository-conventions.md §2.1`, `clarification-protocol.md`, `algedonic-protocol.md`, `framework/artifact-schemas/architecture-contract.schema.md`

---

## Inputs Required

| Input | Source | Minimum State | Retrieval Depth |
|---|---|---|---|
| Architecture Contract (`AC`) for current sprint | Software Architect/PE | Baselined — version 1.0.0+ | Full retrieval (binding output depends on it) |
| Solution Sprint Plan | Project Manager | Baselined for current sprint | Full retrieval |
| Implementation Plan (`IP`) — Work Package definitions | Project Manager | Baselined | Summary sufficient unless WP detail is needed |
| Application Architecture (`AA`) — relevant APP-nnn components | Solution Architect | Baselined | Summary first; full retrieval if interface contract detail is needed |
| Data Architecture (`DA`) — relevant DE-nnn entities | Solution Architect | Baselined | Summary first; full retrieval if field specification detail is needed |
| Technology Architecture (`TA`) — relevant TC-nnn components | Software Architect/PE | Baselined | Summary sufficient for most implementations; full retrieval if SBB configuration details are needed |
| Environment Provisioning Catalog (`EPC`) | DevOps/Platform Engineer | Current sprint provisioning completed | Summary sufficient |
| Defect Register — DE-assigned defects | QA Engineer | Current sprint state | Full retrieval of DE-assigned defect records only |
| Target project repository access | Target project adapter (`engagements/<id>/target-repo/`) | Cloned and accessible | Direct read/write access |

**Prerequisite confirmation:** Before beginning any implementation task, DE must confirm:
1. `sprint.started` has been emitted for this Solution Sprint.
2. Architecture Contract is at version 1.0.0 (baselined), not a draft (v0.x.x).
3. AC has been acknowledged by DE via `handoff.acknowledged` event.

If any prerequisite is not met, DE raises a CQ to PM before proceeding.

---

## Knowledge Adequacy Check

### Required Knowledge

- All ABBs listed in the Architecture Contract §3.3 that are in scope for the current Work Package.
- All authorised SBBs (§3.4 of AC): specific product names, library versions, and restrictions. The DE must implement using only authorised SBBs.
- All Architecture Constraints (§3.5 of AC): non-negotiable constraints applicable to the current WP implementation.
- All Acceptance Criteria (§3.6 of AC): the specific test types and coverage thresholds that constitute a complete and compliant delivery.
- Interface contracts for all API/service interfaces the WP touches — retrieved from the relevant APP-nnn entries in the AA if not fully specified in the AC.
- Data entity field specifications for all data entities the WP creates, reads, updates, or deletes — retrieved from DA if not fully specified in the AC.
- Feature branch naming convention — from Implementation Plan (IP) or from sprint kickoff notes.
- CI pipeline configuration — from EPC or DevOps implementation notes.

### Known Unknowns

- **Business logic edge cases:** The AC specifies what must be implemented and tested, but specific business logic edge cases (e.g., validation rules, rounding behaviour, state machine transitions) may not be fully specified. These are a predictable gap requiring CQ to PM (routed to PO) before implementing the affected logic.
- **Error handling contracts:** Interface error responses are frequently underspecified in AC. The DE must check AA interface detail before implementing error responses. If still underspecified, raise CQ to SwA.
- **Environment-specific configuration:** The AC authorises SBBs but may not specify environment-specific values (URLs, credentials, ports). These are DevOps authority; DE raises CQ via PM if EPC is silent.
- **Test data specifications:** The Test Strategy defines test data requirements but specific test data values for unit tests are DE authority. Synthetic test data is acceptable; production data must never be used in unit test suites.

### Clarification Triggers

| Condition | Route | Blocking? |
|---|---|---|
| AC Acceptance Criteria (§3.6) reference a compliance threshold (e.g., coverage %) that is absent or contradictory | CQ → SwA via PM | Yes — cannot confirm unit test scope |
| Interface contract (APP-nnn) is absent from AC and AA summary is insufficient to define the data format or error behaviour | CQ → SwA via PM | Yes — cannot implement compliant interface |
| A required SBB is not listed in AC §3.4 but is needed for the implementation approach | CQ → SwA via PM | Yes — cannot select technology until authorised |
| Business logic is ambiguous and two valid interpretations produce materially different behaviour | CQ → PM (routed to PO) | Yes — cannot implement until resolved |
| Environment is not provisioned as expected by EPC | CQ → PM (routed to DevOps) | Yes (for environment-dependent work); non-blocking for isolated unit-testable logic |
| AC is at v0.x.x when DE is asked to begin implementation | Raise ALG-008 to PM | Yes — do not implement against a draft AC |
| An in-flight Change Record affects the current WP | Await PM instruction | Yes — halt implementation of affected WP |

**DO NOT raise a CQ for:**
- General coding decisions within an authorised SBB (e.g., which internal design pattern to use, how to name internal classes and variables, test case organisation within the coverage threshold)
- Choices between architecturally equivalent implementation approaches within AC constraints
- Performance micro-optimisation choices not governed by an NFR in the AC

---

## Procedure

The following procedure governs one complete Work Package implementation cycle within a Solution Sprint. Repeat for each Work Package assigned to DE in the current sprint.

### Step 1 — Read the Architecture Contract for this Work Package

Retrieve the AC in full (full retrieval is mandatory — this is a binding output dependency). Identify:
- The specific ABBs (§3.3) binding for this WP
- The authorised SBBs (§3.4) DE is permitted to use
- All Architecture Constraints (§3.5) applicable to this WP
- All Acceptance Criteria (§3.6) that must be satisfied

Log: `[RETRIEVAL] AC-<id> v<version> | full | binding implementation dependency`

### Step 2 — Read relevant architecture artifacts

Apply the confidence-threshold retrieval protocol (`repository-conventions.md §4`):

1. Retrieve summary headers for relevant APP-nnn components (AA) and DE-nnn entities (DA) and TC-nnn components (TA).
2. Assess: is the summary sufficient to understand all interface contracts and data structures I will implement against?
   - **Yes:** Proceed with summary only. Log retrieval.
   - **No:** Retrieve the full component entry. Log retrieval with reason.
3. Full retrieval of AA component detail is **mandatory** when the WP touches an inter-component interface (IFC-nnn) or creates/modifies a data entity that has a defined schema in the DA.

### Step 3 — Confirm environment readiness

Read the EPC summary for the current sprint. Confirm:
- The development environment is provisioned and accessible.
- Required infrastructure services (databases, queues, caches, external APIs) are available in the development/integration environment.

If environment is not ready: raise CQ to PM (routed to DevOps). Record in implementation notes. Begin implementation on local/synthetic stubs while awaiting environment — flag this explicitly in implementation notes as a risk item.

### Step 4 — Create feature branch in target-repo

Create a feature branch in the target project repository following the naming convention specified in the Implementation Plan. Canonical convention if not otherwise specified:

```
feature/<sprint-id>-<wp-id>-<short-description>
```

Example: `feature/SS-003-WP-012-user-auth-jwt`

Record the branch reference in `delivery-repository/branch-refs/br-<sprint-id>.md`.

### Step 5 — Implement the feature

Implement the Work Package on the feature branch in the target project repository.

Implementation must:
- Use only SBBs authorised in AC §3.4
- Conform to all Architecture Constraints in AC §3.5
- Implement all interface contracts specified or referenced in the AC (APP-nnn entries from AA)
- Handle all data entities per the schemas specified or referenced in the AC (DE-nnn entries from DA)
- Produce no writes to any path in the framework repository

As implementation proceeds, record significant implementation decisions and discovered hidden dependencies in `delivery-repository/implementation-notes/in-<sprint-id>-<wp-id>.md`. This is a living document updated throughout the implementation cycle.

**Revisit handling (`trigger="revisit"`, `phase_visit_count > 1`):** If this WP is being revisited (e.g., due to a Change Record or a defect fix requiring architectural change), first identify which sections of the prior implementation are affected. Preserve all unaffected code. Revise only the affected scope. Record the revisit context and change scope in the implementation notes.

### Step 6 — Write unit tests

Write unit tests for the implemented code:
- Coverage must meet or exceed the threshold specified in AC §3.6 Acceptance Criteria. If no specific threshold is stated in the AC, default to ≥ 80% line coverage per `test-strategy.schema.md §3.3`.
- Test cases must cover: happy path, primary error paths, and boundary conditions for all interface inputs and outputs.
- Unit tests must not depend on live external services; mock or stub all external dependencies.
- Unit tests must use only synthetic test data. Production data is prohibited in unit test suites under all circumstances.

### Step 7 — Run CI pipeline and address failures

Execute the CI pipeline for the feature branch. The CI pipeline is defined and maintained by DevOps; DE's role is to ensure the pipeline passes.

For each CI failure:
- Classify the failure: DE code failure (fix it), environment failure (raise CQ to DevOps via PM), pipeline configuration failure (raise CQ to DevOps via PM).
- Address all DE code failures before proceeding.
- If a CI failure reflects an architecture compliance gap (e.g., a security scan failure triggered by an authorised SBB), flag to SwA via PM before attempting a workaround.

CI must pass (all stages green) before proceeding to Step 8.

### Step 8 — Architecture compliance self-check

Before creating the PR, perform an explicit self-check against all Architecture Contract compliance criteria:

For each constraint in AC §3.5:
- [ ] This constraint is satisfied by the current implementation — confirm with specific code reference or evidence.
- [ ] OR this constraint cannot be fully satisfied — document the specific gap, the reason, and any mitigating measure taken.

For each acceptance criterion in AC §3.6:
- [ ] A unit test (or flagged integration test) directly verifies this criterion.
- [ ] OR the criterion is verified by a non-test means (e.g., static analysis, code review) — state the verification method explicitly.

Any gap must be documented in the PR description with: the AC constraint ID, the specific gap, the reason, and the justification for proceeding. Do not conceal gaps. Concealed non-compliance is a governance violation.

### Step 9 — Create pull request in target-repo

Create a pull request from the feature branch to the trunk/main branch of the target project repository. The PR description must include:

1. **Work Package reference:** WP-id, Sprint-id
2. **Architecture Contract reference:** AC-id, version
3. **Summary of implementation:** what was built and how it satisfies the ABBs
4. **Compliance self-check result:** explicit confirmation or documented exceptions (from Step 8)
5. **Test coverage achieved:** percentage and tool used
6. **Known limitations or deferred items:** anything not addressed in this PR with justification

Record the PR reference in `delivery-repository/pr-records/pr-<wp-id>-<branch-name>.md`.

### Step 10 — Emit handoff.created (PR ready)

Emit a `handoff.created` event to notify:
- **SwA:** PR is ready for architecture review
- **QA:** PR is ready for test execution (QA may begin test environment deployment in parallel with SwA review)

Payload includes: `from_agent: implementing-developer`, `to_agents: [software-architect, qa-engineer]`, `artifact_id: <pr-reference>`, `version: initial`, `handoff_type: pr-ready-for-review`, `sprint: <sprint-id>`, `work-package: <wp-id>`

Write the handoff record to `engagements/<id>/handoff-log/<sprint-id>-<wp-id>-pr-handoff.md`.

### Step 11 — Address review feedback (max 2 iterations)

**Iteration 1:** Receive SwA's architecture review feedback (structured feedback per `repository-conventions.md §6`). Address all blocking feedback items. Push changes to the feature branch. CI must re-pass before notifying SwA.

**Iteration 2 (if required):** If SwA raises additional blocking feedback, address it. Push changes. CI must pass.

**Escalation:** If SwA's feedback cannot be addressed within 2 iterations:
- Do not attempt a third iteration unilaterally.
- Emit `alg.raised` with `trigger_id: ALG-010`, `category: IA`, `severity: S3`, `escalation_target: pm`.
- Write the algedonic record to `engagements/<id>/algedonic-log/<sprint-id>-ALG-<sequence>.md`.
- Await PM adjudication before continuing.

Similarly for QA defect feedback: max 2 fix iterations per defect before escalating to PM. Severity 1 defects (safety-critical): see Algedonic Triggers.

### Step 12 — Record merge and update delivery metadata

On PR approval and merge:
- Update `delivery-repository/pr-records/pr-<wp-id>-<branch-name>.md` with status: merged, merge SHA, and merge date.
- Update the test report reference in `delivery-repository/test-reports/tr-<sprint-id>-<wp-id>.md` with final coverage percentage and pass/fail confirmation.
- Emit `artifact.baselined` for the PR record and test report reference (delivery metadata artifacts).

---

## Feedback Loop

### PR Review Loop (DE ↔ SwA)

| Iteration | Action | Termination Condition |
|---|---|---|
| 1 | SwA provides structured review feedback; DE addresses all blocking items; CI re-passes | SwA approves PR |
| 2 | SwA provides additional blocking feedback; DE addresses; CI re-passes | SwA approves PR |
| Escalation | DE emits ALG-010 to PM; PM adjudicates; PM may restructure sprint, override, or request AC revision | PM decision resolves deadlock |

**Maximum iterations:** 2 before escalation. The DE must not informally negotiate with SwA to bypass the escalation — the PM adjudication is the correct resolution path.

### Defect Fix Loop (DE ↔ QA)

| Iteration | Action | Termination Condition |
|---|---|---|
| 1 | QA raises defect record; DE fixes and pushes; CI re-passes; DE notifies QA | QA confirms defect resolved |
| 2 | QA confirms fix or raises follow-on defect; DE addresses | QA confirms all defects resolved |
| Escalation | DE escalates to PM for sprint scope adjudication; PM may defer to next sprint or restructure | PM decision resolves |

**Maximum iterations:** 2 per defect before escalation to PM. A defect that is re-introduced after a fix (regression) counts as a new defect, not a new iteration of the original.

---

## Algedonic Triggers

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-007 | DE has written or is about to write application code to any path within the framework repository (not the target-repo) | S1 | Halt immediately; do not commit; notify PM; the write must not occur |
| ALG-008 | DE is asked to begin implementation against an AC that is at draft version (v0.x.x) or against an AC that has not been baselined | S2 | Do not begin implementation; notify PM; await baselined AC |
| ALG-008 | DE discovers that a completed implementation relied on a draft AC (the AC was updated to 1.0.0 after implementation had begun on a 0.x.x version) | S2 | Notify PM; assess whether implementation is consistent with the baselined AC; revise if needed |
| ALG-010 | PR review feedback loop has been exhausted (2 iterations) without SwA approval | S3 | Raise ALG-010; notify PM; do not merge PR; do not attempt further implementation revisions until PM adjudicates |
| ALG-011 | DE identifies that the Architecture Contract is internally inconsistent or contradicts a baselined TA or AA artifact | S3 | Raise feedback to SwA (producing agent) immediately; notify PM if unresolved within the sprint |
| ALG-006 | A Change Record affecting an in-flight Work Package arrives mid-sprint and the sprint plan cannot be completed as specified without PM adjudication | S2 | Halt implementation of the affected WP; do not merge any open PRs for that WP; notify PM; await guidance |

**Note on safety-critical defects:** If QA identifies a Severity 1 defect in a safety-relevant component (which QA classifies and routes), QA is responsible for raising ALG-013. The DE's role is to halt further development on the affected component and await CSCO and SwA resolution. DE does not independently classify safety-critical defects — that is CSCO and QA authority.

---

## Outputs

| Output | Location | Event Emitted |
|---|---|---|
| Application source code (feature branch) | Target project repository (`engagements/<id>/target-repo/`) — NOT the framework repo | — |
| Pull Request | Target project repository (PR UI) | `handoff.created` (PR-ready) |
| PR record | `delivery-repository/pr-records/pr-<wp-id>-<branch-name>.md` | `artifact.baselined` |
| Unit test report reference | `delivery-repository/test-reports/tr-<sprint-id>-<wp-id>.md` | `artifact.baselined` |
| Implementation notes | `delivery-repository/implementation-notes/in-<sprint-id>-<wp-id>.md` | — (informational; no event) |
| Branch registry | `delivery-repository/branch-refs/br-<sprint-id>.md` | — (informational; updated throughout sprint) |
| Algedonic signal records (if raised) | `engagements/<id>/algedonic-log/<sprint-id>-ALG-<sequence>.md` | `alg.raised` |
| CQ records (if raised) | `engagements/<id>/clarification-log/<sprint-id>-CQ-<sequence>.md` | `cq.raised` |

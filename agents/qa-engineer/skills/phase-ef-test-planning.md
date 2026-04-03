---
skill-id: QA-PHASE-EF
agent: QA
name: phase-ef-test-planning
display-name: Phase E/F — Test Strategy Planning and Baseline
invoke-when: >
  Phase C gate has passed and AA and DA are baselined; QA produces Initial Test Strategy in
  Phase E and finalises it in Phase F after IP is baselined at 1.0.0.
trigger-phases: [E, F]
trigger-conditions:
  - gate.evaluated (from_phase=C, result=passed)
  - sprint.started (phase=E)
  - artifact.baselined (artifact-type=implementation-plan, version=1.0.0)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F]
primary-outputs: [Initial Test Strategy draft, Final Test Strategy, Test Environment Requirements]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase E/F — Test Strategy Planning and Baseline

**Agent:** QA Engineer  
**Version:** 1.0.0  
**Phase:** E — Opportunities & Solutions (initial draft); F — Migration Planning (finalisation and baseline)  
**Skill Type:** Primary artifact production  
**Framework References:** `agile-adm-cadence.md §4.1`, `raci-matrix.md §3.7–3.8`, `repository-conventions.md §3–5`, `clarification-protocol.md`, `algedonic-protocol.md`, `framework/artifact-schemas/test-strategy.schema.md`

---

## Inputs Required

| Input | Source | Minimum State | Retrieval Depth |
|---|---|---|---|
| Application Architecture (`AA`) | Solution Architect | Baselined (v1.0.0+) | Summary first; full retrieval for interface testability assessment |
| Data Architecture (`DA`) | Solution Architect | Baselined (v1.0.0+) | Summary first; full retrieval for data quality test requirements |
| Architecture Vision (`AV`) | Solution Architect | Baselined (v1.0.0+) | Summary sufficient for safety-relevant component identification |
| Safety Constraint Overlay (`SCO`) — Phase C update | CSCO | Baselined | Full retrieval — all SCO safety constraints must map to at least one safety test |
| Requirements Register (`RR`) | Product Owner | Current | Summary first; full retrieval if specific NFR values are needed |
| Implementation Candidate Catalog (`ICC`) — Phase E | Software Architect/PE | Draft acceptable for Phase E | Summary sufficient |
| Work Package Catalog (`WPC`) — Phase E | Project Manager | Draft acceptable for Phase E | Summary sufficient |
| Risk Register — Phase E | Project Manager | Draft acceptable | Summary sufficient |
| Architecture Contract draft — Phase F alignment | Software Architect/PE | Draft (v0.x.x) acceptable for alignment review; but TS must not be *based on* AC — TS informs AC | Summary sufficient; full retrieval for acceptance criteria alignment |
| Implementation Plan (`IP`) — Phase F | Project Manager | Baselined (v1.0.0+) for Phase F finalisation | Summary sufficient for sprint scope alignment |
| Environment Provisioning Catalog (`EPC`) — Phase F | DevOps/Platform Engineer | Draft acceptable | Summary sufficient for environment requirement identification |

**Phase E prerequisite:** AA and DA must be baselined before the Initial Test Strategy draft is produced. If AA or DA are still in draft, the Test Strategy scope will be incomplete and must flag this explicitly in `pending-clarifications`.

**Phase F prerequisite:** The Implementation Plan must be baselined before the Final Test Strategy is finalised. QA must also have received and reviewed the Architecture Contract draft (v0.x.x) from SwA before completing AC alignment (Steps 7–9 below).

---

## Knowledge Adequacy Check

### Required Knowledge

- All application components (APP-nnn) and interfaces (IFC-nnn) in the AA — used to define test scope and integration test coverage.
- All data entities (DE-nnn) and their quality requirements in the DA — used to define data quality test cases.
- All safety constraints in the current SCO — each must map to at least one safety acceptance test criterion in the Test Strategy.
- NFR values from the Requirements Register: performance latency/throughput targets, availability targets, security classification, scalability bounds. These are the pass thresholds for non-functional tests.
- The full set of Work Packages (from WPC) that are in scope for the engagement — used to define acceptance criteria per WP.
- Regulatory testing requirements, if any: any compliance testing obligations (GDPR data boundary testing, PCI-DSS card data scope, HIPAA PHI boundary tests, accessibility standards) that arise from the regulatory environment identified in the Architecture Vision.

### Known Unknowns

- **NFR thresholds:** Performance and availability thresholds are frequently absent or underspecified in the Requirements Register at Phase E. These are the most predictable knowledge gap for this skill and must be resolved via CQ before the Test Strategy can be baselined.
- **Safety-relevant component classification:** The SCO may be in a partial state at Phase E. If a component's safety-relevant classification is uncertain, this is a blocking gap for safety acceptance test scope definition.
- **Regulatory testing obligations:** The regulatory jurisdiction is engagement-specific and cannot be assumed. If the AV safety envelope or business context indicates a regulated industry (healthcare, financial, safety-critical systems), regulatory testing obligations must be explicitly confirmed via CQ before the Test Strategy scope is declared complete.
- **Test environment data requirements:** Specific anonymised production data subsets (if needed) must be approved and specified. This is typically a Phase F/G concern but should be flagged at Phase E.
- **Third-party API test environment availability:** If any WP integrates with an external API, the availability of a sandbox/test environment for that API is engagement-specific and cannot be assumed.

### Clarification Triggers

| Condition | Route | Blocking? |
|---|---|---|
| NFR thresholds for performance (latency, throughput) are absent from RR | CQ → PM (routed to PO for product NFRs; to SwA for architecture-driven NFRs) | No — TS produced with placeholder; AC alignment cannot complete without values |
| NFR thresholds for availability (uptime %, RTO, RPO) are absent | CQ → PM (routed to PO) | No — placeholder; AC alignment incomplete |
| Safety-relevant classification of specific components is undefined or unclear in SCO | CQ → PM (routed to CSCO) | Yes — safety acceptance test scope cannot be defined without this |
| Regulatory testing obligations are implied but not specified (e.g., system is described as handling personal data but jurisdiction is not stated) | CQ → PM (routed to user/PO) | Yes — compliance testing scope cannot be defined without jurisdiction |
| A WP in scope has no requirements tracing to it in the RR (untraceable WP) | Structured feedback to PM | No — QA flags the gap; PM resolves via PO; QA defers acceptance criteria for that WP |
| Test environment data classification is unclear — QA cannot determine whether anonymisation is required | CQ → PM (routed to SA/CSCO) | No — QA defaults to synthetic test data; flags production-data-adjacent requirements as open |

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="QA", phase="E", artifact_type="test-strategy")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Phase E: Initial Test Strategy

#### Step 1 — Read all available architecture artifacts; identify testability concerns

Apply the confidence-threshold protocol. Retrieve summary headers for AA, DA, AV, and SCO. Retrieve full content for:
- SCO (all safety constraints must be catalogued)
- AA (interface contracts and application component boundaries drive integration test scope)
- DA (data entity schemas and governance rules drive data quality tests)

For each AA component (APP-nnn), assess testability:
- Is the component boundary clearly defined? (unclear boundary → note as CQ candidate)
- Are interface contracts specified to sufficient detail for test case design?
- Are there circular dependencies between components that complicate integration test isolation?

For each data entity (DE-nnn), assess data quality testability:
- Is there a defined schema or field specification? (absent → flag for DA CQ)
- Are there defined data quality rules (uniqueness, referential integrity, format constraints)?

Record testability concerns in `qa-repository/test-strategy/phase-e-testability-notes-<sprint-id>.md`.

#### Step 2 — Define test levels and coverage targets

Define the test level structure per `test-strategy.schema.md §3.3`:

| Test Level | Scope | Default Coverage Target | Owner | Notes |
|---|---|---|---|---|
| Unit | Component-level logic | ≥ 80% line coverage | Implementing Developer | Minimum; AC may specify higher |
| Integration | IFC-nnn interfaces | All in-scope interfaces exercised at least once | Implementing Developer + QA | Focus on boundary behaviour and error paths |
| System / End-to-End | Full value stream execution | All in-scope value streams (from AA value stream catalog) | QA Engineer | One E2E test per value stream minimum |
| Performance | Throughput/latency under defined load | Per NFR thresholds (to be filled from RR CQ) | QA Engineer | Placeholder if NFR values not yet available |
| Security | Vulnerability, access control, data boundaries | OWASP Top 10 baseline + SCO security constraints | QA + DevOps | SCO security constraints are hard minimum |
| Regression | Prior functionality preservation | Full suite on each Staging deployment | QA Engineer | Automated preferred |
| Safety Acceptance | SCO constraint verification | 100% SCO constraint coverage | QA + CSCO | Every SCO constraint needs at least one test |

If NFR thresholds are unknown, raise a CQ per the Clarification Triggers table and use placeholder values marked `[PENDING CQ-id]` in the Test Strategy draft.

#### Step 3 — Identify safety-relevant components; coordinate with CSCO

From the AV safety envelope and the current SCO, identify all components and data flows that are classified as safety-relevant.

For each safety-relevant component:
1. Map it to one or more APP-nnn entries in the AA.
2. Identify the specific SCO constraint(s) it must satisfy.
3. Draft a Safety Acceptance test criterion stub: `SC-SAT-nnn: [component] must satisfy [SCO constraint] — verification method: [test type + approach]`.

Create a handoff to CSCO (via PM): request CSCO review of the draft safety acceptance test scope. Specifically ask CSCO to confirm:
- Is the list of safety-relevant components complete?
- Are the draft safety test approaches acceptable, or does CSCO require additional formal verification methods?
- Are there regulatory testing standards that must be referenced?

CSCO review is the limiting input for safety test scope finalisation. If CSCO is unavailable, flag to PM (risk of incomplete safety scope) and proceed with what is available, marking safety sections as `[PENDING CSCO REVIEW]`.

#### Step 4 — Define non-functional test strategy

For each non-functional requirement category from the RR and SCO, define a test approach:

**Performance testing approach:**
- Define load profiles (concurrent users, requests/sec, data volumes) derived from RR NFRs.
- Identify performance test entry points (which APIs or service boundaries to load test).
- Specify pass thresholds (latency P95, P99 under peak load; throughput targets).
- If thresholds are absent: placeholder with `[PENDING NFR CQ]`.

**Security testing approach:**
- OWASP Top 10 baseline always applies.
- SCO security constraints are additive — enumerate each and specify the test approach.
- Identify authentication/authorisation test scope: which roles and permission boundaries must be verified?
- Identify data boundary test scope: which data entities are classified confidential/restricted (from DA) and must be verified not to leak across boundary?

**Availability and resilience testing:**
- If RR specifies RTO/RPO: define chaos/failover test scenarios.
- If not specified: flag as NFR gap CQ.

#### Step 5 — Identify test data requirements

Define test data requirements per `test-strategy.schema.md §3.8`:

- **Unit test data:** Synthetic only. No production data. DE authority.
- **Integration test data:** Synthetic with anonymised production subsets where structural realism is needed. Confirm with SA/CSCO whether anonymised production data is permitted (CQ if unclear).
- **Staging test data:** Full-volume anonymised production subset or high-fidelity synthetic data. Must be approved by SA/CSCO if it requires production data input.

**Hard rule:** Test environments must not use unanonymised production data. If any test data requirement would require raw production data, flag to PM and CSCO immediately. This is not a grey area.

For each data entity (DE-nnn) in scope, specify test data needs: minimum record count, required value distributions (for performance testing), required edge cases (null values, maximum field lengths, special characters).

#### Step 6 — Produce Initial Test Strategy draft (v0.1.0)

Write the Initial Test Strategy to `qa-repository/test-strategy/ts-0.1.0.md` using the schema from `framework/artifact-schemas/test-strategy.schema.md`.

The draft must include all required sections per the schema (§3.1–§3.8). Sections dependent on open CQs are produced with placeholder content and `[PENDING CQ-id]` markers. The artifact summary header must list all open CQs in `pending-clarifications`.

Emit `artifact.baselined` with `status: draft` and `version: 0.1.0`. Write a handoff record to PM for awareness.

#### Step 7 — Submit to SwA for AC alignment review (max 2 iterations)

Create a handoff to SwA with the Test Strategy draft. Request SwA to confirm:
1. Are the acceptance criteria in §3.4 consistent with what SwA plans to specify in the Architecture Contract (§3.6)?
2. Are the coverage targets in §3.3 achievable with the authorised technology stack?
3. Are there any AC compliance criteria SwA intends to include that are not covered by the current test scope?

**Iteration 1:** SwA returns structured feedback. QA addresses all blocking feedback items; updates TS draft; increments version (v0.2.0).

**Iteration 2 (if required):** SwA raises further blocking feedback. QA addresses. Version increments to v0.3.0.

**Escalation:** If SwA alignment cannot be achieved within 2 iterations, QA emits ALG-010 (S3) to PM for adjudication. PM adjudicates the disputed criteria. QA does not unilaterally override SwA's feedback or proceed with a Test Strategy known to be inconsistent with the planned AC.

---

### Phase F: Test Strategy Finalisation

#### Step 8 — Refine Test Strategy based on finalised Implementation Plan and Sprint Plan

After PM baselines the Implementation Plan, retrieve it in full. Update the Test Strategy to:
- Align WP-level acceptance criteria (§3.4) with the final WP scope per sprint.
- Confirm test scope per sprint (which tests run in which Solution Sprint).
- Update test coverage targets if the IP has added or removed WPs relative to the Phase E scope.
- Verify that all RR NFR values have been confirmed (or that remaining CQs are clearly marked as pending).

#### Step 9 — Produce test environment requirements → DevOps

From the updated Test Strategy §3.8, extract environment requirements:
- What test environment tiers are needed (unit/local, integration, staging)?
- What infrastructure components must be available in each tier?
- What test data volumes are needed in each tier?
- What external API sandbox/mock endpoints are needed?
- Are there any special hardware or network requirements?

Write the test environment requirements as a structured note to `qa-repository/test-strategy/env-requirements-<sprint-id>.md`. Create a handoff to DevOps (via PM) requesting these requirements be incorporated into the Environment Provisioning Catalog before the first Solution Sprint.

#### Step 10 — Baseline Final Test Strategy; emit artifact.baselined; handoff to PM

Once:
- All blocking CQs are answered or documented as assumptions with explicit risk acceptance
- CSCO has reviewed safety test scope (or CSCO review is documented as pending with PM notification)
- SwA alignment is complete (AC acceptance criteria are consistent with TS)
- Test environment requirements have been handed off to DevOps

Finalise the Test Strategy at version 1.0.0. The artifact must satisfy all quality criteria in `test-strategy.schema.md §5`.

Emit `artifact.baselined` with `artifact_id: ts-<id>`, `version: 1.0.0`, `status: baselined`.

Write handoff records to:
- **PM:** Test Strategy baselined; input to Phase F gate checklist
- **SwA:** Test Strategy baselined; SwA is a consuming agent (AC acceptance criteria sourced from TS)

Cast `gate.vote_cast` for Phase F→G gate (QA contribution): QA approves F→G passage when the Final Test Strategy is baselined and test environment requirements have been submitted to DevOps.

---

## Feedback Loop

### SwA Alignment Loop (QA ↔ SwA)

| Iteration | Action | Termination Condition |
|---|---|---|
| 1 | SwA reviews Test Strategy draft; returns structured feedback; QA addresses blocking items; version increments | SwA confirms alignment |
| 2 | SwA raises remaining blocking feedback; QA addresses; version increments | SwA confirms alignment |
| Escalation | QA emits ALG-010; PM adjudicates disputed criteria; TS updated per PM decision | PM resolution accepted by both parties |

**Maximum iterations:** 2 before escalation. Escalation target: PM (ALG-010, S3).

### CSCO Safety Test Review Loop (QA ↔ CSCO)

| Iteration | Action | Termination Condition |
|---|---|---|
| 1 | CSCO reviews safety acceptance test scope; returns feedback; QA addresses | CSCO confirms safety scope is complete |
| Escalation | If CSCO is unavailable: QA notifies PM; safety sections remain marked `[PENDING CSCO REVIEW]`; TS cannot be baselined with safety-relevant components until CSCO reviews | CSCO becomes available; completes review |

**Maximum iterations:** 1 substantive review round. If CSCO raises substantive feedback requiring architectural changes (new safety requirements), this feeds back as a structured feedback item from CSCO → QA, and QA updates the TS. CSCO cannot block TS baseline for non-safety sections; only safety-specific sections are held.  
**Escalation target:** PM (ALG-002 if CSCO unavailable and safety gate review is blocking sprint progression).

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
| ALG-002 | CSCO is unavailable and safety acceptance test scope cannot be reviewed; this blocks Test Strategy baseline for safety-relevant component scope | S1 | Halt safety section baseline; notify PM; do not proceed with safety test scope until CSCO available |
| ALG-010 | SwA alignment feedback loop exhausted (2 iterations) without agreement on acceptance criteria | S3 | Raise ALG-010; notify PM; await PM adjudication; do not baseline TS with known inconsistency with planned AC |
| ALG-017 | Regulatory testing jurisdiction is unknown and cannot be safely assumed; compliance test scope cannot be defined without it | S1 | Halt compliance test scope section; escalate to PM (routed to user); flag to CSCO concurrently |

---

## Outputs

| Output | Location | Event Emitted |
|---|---|---|
| Testability notes (Phase E) | `qa-repository/test-strategy/phase-e-testability-notes-<sprint-id>.md` | — (informational) |
| Initial Test Strategy draft (Phase E) | `qa-repository/test-strategy/ts-0.1.0.md` (versioned per iteration) | `artifact.baselined` (status: draft) |
| Final Test Strategy (Phase F baseline) | `qa-repository/test-strategy/ts-1.0.0.md` | `artifact.baselined` (status: baselined) |
| Test Environment Requirements | `qa-repository/test-strategy/env-requirements-<sprint-id>.md` | `handoff.created` (to DevOps via PM) |
| Handoff records | `engagements/<id>/handoff-log/` — TS to SwA (alignment), TS to PM (gate), env-requirements to DevOps | `handoff.created` |
| Phase F→G gate vote | EventStore | `gate.vote_cast` |
| CQ records (if raised) | `engagements/<id>/clarification-log/<sprint-id>-CQ-<sequence>.md` | `cq.raised` |
| Algedonic signal records (if raised) | `engagements/<id>/algedonic-log/<sprint-id>-ALG-<sequence>.md` | `alg.raised` |

# Schema: Test Strategy (`TS`)

**Version:** 1.0.0  
**ADM Phases:** E (initial), F (baselined), G (execution reports appended)  
**Owner:** QA Engineer  
**Consumed by:** Architecture Contract (AC), Compliance Assessment (CA), Implementation Plan (IP)  

---

## 1. Purpose

The Test Strategy defines the approach, coverage targets, test types, acceptance criteria, and execution governance for verifying that delivered SBBs satisfy the ABBs defined in the Architecture Artifacts. It is not a test plan (which is sprint-specific) — it is the overarching quality strategy for the full delivery scope. Execution reports are appended per Solution Sprint during Phase G.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Application Architecture (`AA`) | Solution Architect | Baselined |
| Data Architecture (`DA`) | Solution Architect | Baselined |
| Implementation Plan (`IP`) — work packages | Project Manager | At least Phase E draft |
| Safety Constraint Overlay (`SCO`) | CSCO | Phase D update baselined |
| Requirements Register (`RR`) | Product Owner | Current |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: test-strategy`
- `safety-relevant: true` if any safety-relevant component is in scope
- `csco-sign-off:` required if safety-relevant test coverage is defined

### 3.2 Test Scope

| In Scope | Out of Scope |
|---|---|
| [List of work packages, application components, and data entities to be tested] | [Explicitly excluded items with rationale] |

### 3.3 Test Types and Coverage Targets

| Test Type | Description | Coverage Target | Tools / Approach | Owner |
|---|---|---|---|---|
| Unit | Component-level logic verification | ≥ 80% line coverage (minimum) | | Implementing Developer |
| Integration | Interface and inter-component interaction | All IFC-nnn interfaces exercised | | Implementing Developer + QA |
| System / End-to-End | Full value stream execution | All VS-nnn value streams covered | | QA Engineer |
| Performance | Throughput, latency under load | Per non-functional requirements in RR | | QA Engineer |
| Security | Vulnerability, access control, data boundary verification | OWASP Top 10 baseline; SCO security requirements | | QA Engineer + DevOps |
| Regression | Confirmation that prior functionality is not degraded | Full suite on each deployment to Staging | | QA Engineer |
| Safety Acceptance | Verification of safety constraint satisfaction | All SCO constraints covered by at least one test | | QA Engineer + CSCO |

Coverage targets are minimums. Where the Requirements Register or SCO specifies higher targets, those take precedence.

### 3.4 Acceptance Criteria Register

Acceptance criteria are the binding conditions that a Work Package must satisfy to be considered complete. Each criterion maps to a requirement and to a test type.

| AC ID | Work Package | Requirement (RR ref) | Criterion Statement | Test Type | Verification Method | Safety-Relevant |
|---|---|---|---|---|---|---|
| AC-nnn | WP-nnn | RR-nnn | | | Automated / Manual / Review | Yes/No |

### 3.5 Defect Classification

| Severity | Definition | Resolution Requirement |
|---|---|---|
| **Severity 1 — Critical** | System cannot perform a primary function; safety constraint at risk of violation; data loss or corruption | Block deployment; immediate fix required; CSCO notification if safety-relevant |
| **Severity 2 — High** | Major function impaired; significant data quality issue; workaround is unduly burdensome | Fix before Solution Sprint closeout |
| **Severity 3 — Medium** | Minor function impaired; workaround available; no safety or data integrity impact | Fix in same or next sprint at PM discretion |
| **Severity 4 — Low** | Cosmetic issue; negligible functional impact | Tracked; fixed at convenience |

### 3.6 Entry and Exit Criteria (per Solution Sprint)

**Entry criteria (before testing begins):**
- [ ] Work package implemented and code merged to feature branch
- [ ] Unit test suite passes with no Severity 1 or 2 failures
- [ ] Deployment to Staging environment successful
- [ ] Test data prepared and validated

**Exit criteria (before Solution Sprint can close):**
- [ ] All Severity 1 and Severity 2 defects resolved or explicitly deferred with PM and QA approval
- [ ] Acceptance criteria for all in-scope work packages verified
- [ ] Test Execution Report produced and signed off by QA Engineer
- [ ] Regression suite passed against Staging
- [ ] Safety Acceptance tests passed for safety-relevant components (CSCO co-signs)

### 3.7 Non-Functional Requirements

| NFR ID | Category | Requirement Statement | Source (RR ref) | Verification Approach | Pass Threshold |
|---|---|---|---|---|---|
| NFR-nnn | Performance / Security / Availability / Scalability / Compliance | | | | |

### 3.8 Test Environment Requirements

| Environment | Purpose | Required Components | Data Requirements | Owner |
|---|---|---|---|---|
| Unit test | Isolated component testing | Component under test + mocks | Synthetic | Implementing Developer |
| Integration | Interface testing | Components + their dependencies | Synthetic + anonymised production subsets | QA Engineer |
| Staging | Full system testing | Full stack (mirror of production) | Anonymised production data subset | DevOps / QA |

### 3.9 Test Execution Reports (Phase G — appended per sprint)

One report is appended per Solution Sprint. Format:

```markdown
### Test Execution Report: SS-<n>

**Sprint:** SS-<n>  
**QA Engineer sign-off:** [name/role]  
**CSCO sign-off (if safety-relevant):** [yes/no/not-required]  

| Test Type | Tests Run | Passed | Failed | Blocked | Coverage Achieved |
|---|---|---|---|---|---|
| Unit | | | | | |
| Integration | | | | | |
| System/E2E | | | | | |
| Security | | | | | |
| Regression | | | | | |
| Safety Acceptance | | | | | |

**Open Defects:**
| Defect ID | Severity | Description | Owner | Target Sprint |
|---|---|---|---|---|

**Conclusion:** [Pass / Conditional Pass / Fail — with rationale]
```

---

## 4. Artifact Sub-Components

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Test Scope definition | Document section | Yes | §3.2 |
| Test Types & Coverage Targets | Table | Yes | §3.3 |
| Acceptance Criteria Register | Catalog | Yes | §3.4 |
| Defect Classification scheme | Reference table | Yes | §3.5 |
| Entry/Exit Criteria | Checklist | Yes | §3.6 |
| Non-Functional Requirements | Catalog | Yes | §3.7 |
| Test Environment Requirements | Table | Yes | §3.8 |
| Test Execution Reports | Log (appended per sprint) | Yes during Phase G | §3.9 |

---

## 5. Quality Criteria

- [ ] All in-scope work packages have at least one acceptance criterion.
- [ ] Coverage targets meet or exceed the minimums in §3.3, or documented justification for lower targets is provided.
- [ ] Every safety-relevant component has at least one Safety Acceptance test criterion.
- [ ] Defect classification scheme is consistent with the Implementation Plan's Definition of Done.
- [ ] CSCO sign-off present if safety-relevant test coverage is defined.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Phase E draft (scope and approach) |
| 1.0.0 | | | Baselined at Phase F gate |
| 1.x.x | | | Execution report appended (Phase G, per sprint) |

# Schema: Implementation Plan (`IP`)

**Version:** 1.0.0  
**ADM Phases:** E (Opportunities & Solutions) + F (Migration Planning)  
**Owner:** Project Manager  
**Consumed by:** Architecture Contract (AC), Test Strategy (TS), DevOps environment provisioning, all Solution Sprint agents  

---

## 1. Purpose

The Implementation Plan consolidates the outputs of Phases E and F into a single governing document for the Implementation Stream. It defines what will be built (work packages, SBBs), in what order (roadmap, dependencies), under what constraints (transition architectures, risk register), and how it will be delivered (Solution Sprint Plan, environment provisioning). It is the primary authorisation for the Implementation Stream to begin Solution Sprints.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Technology Architecture (`TA`) | Software Architect/PE | Baselined |
| All Phase C artifacts (AA, DA) | Solution Architect | Baselined |
| Requirements Register (`RR`) | Product Owner | Current |
| Safety Constraint Overlay (`SCO`) — Phase D update | CSCO | Baselined |
| Test Strategy (`TS`) — initial state | QA Engineer | Draft acceptable at Phase E; baselined at Phase F gate |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: implementation-plan`
- `safety-relevant: true` if any safety-relevant work package is included
- `csco-sign-off: true` (required — risk register review and safety-relevant work package approval)

### 3.2 Gap Analysis Summary (Phase E)

A consolidated gap analysis across all four architecture domains. Synthesises the per-domain gap analyses from AA, DA, and TA.

| Gap ID | Domain | Description | ABBs Affected | SBB Resolution Approach | Priority |
|---|---|---|---|---|---|
| GAP-nnn | Business / Application / Data / Technology | | APP/DE/TC-nnn | Build / Buy / Reuse / Retire | High / Med / Low |

### 3.3 Implementation Candidate Catalog (Phase E)

For each gap, one or more candidate solutions. Records the build/buy/reuse decision.

| Candidate ID | Name | Addresses Gap | Decision | Rationale | Dependencies | Risk Level |
|---|---|---|---|---|---|---|
| IC-nnn | | GAP-nnn | Build / Buy / Reuse / Retire | | IC-nnn, ... | Low/Med/High |

Each selected candidate becomes a Work Package in §3.4.

### 3.4 Work Package Catalog

A work package is the unit of delivery planning. Each work package produces one or more SBBs.

| WP ID | Name | Description | SBBs Produced | Responsible Agent | Dependencies | Acceptance Criteria | Safety-Relevant |
|---|---|---|---|---|---|---|---|
| WP-nnn | | | TC/APP-nnn, ... | Implementing Developer / DevOps / QA | WP-nnn, ... | | Yes/No |

### 3.5 Architecture Roadmap

The Architecture Roadmap shows the sequence of work packages leading from the current baseline to the target architecture, potentially via one or more transition architectures.

**Transition Architectures:** If the gap between baseline and target cannot be bridged in a single delivery wave, intermediate "plateau" states are defined:

| Transition ID | Name | Description | Work Packages Included | ABBs Active | SBBs Introduced |
|---|---|---|---|---|---|
| TR-000 | Baseline | Current state | — | (existing) | (existing) |
| TR-001 | | | WP-nnn, ... | | |
| TR-nnn | Target | Full target state | all | all target | all |

ArchiMate viewpoint: **Implementation and Migration Viewpoint** (work packages, deliverables, plateaus, gaps).

### 3.6 Dependency Matrix

| | WP-001 | WP-002 | WP-nnn |
|---|---|---|---|
| **WP-001** | — | depends | |
| **WP-002** | blocks | — | |

`depends` = row depends on column being complete first; `blocks` = row must complete before column can start.

### 3.7 Risk Register

| Risk ID | Description | Category | Probability | Impact | Severity | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| RSK-nnn | | Schedule / Technical / Safety / Regulatory / Resource | High/Med/Low | High/Med/Low | H/M/L | | Agent role | Open/Mitigated/Accepted |

**Severity** = Probability × Impact using H=3, M=2, L=1 scale. Severity ≥ 6 requires CSCO review.

### 3.8 Solution Sprint Plan

The plan authorising the Implementation Stream. Produced at Phase F completion.

| Sprint ID | Scope (Work Packages) | Entry Conditions | Exit Conditions | Architecture Contract Required |
|---|---|---|---|---|
| SS-001 | WP-nnn, WP-nnn | Artifacts baselined: [list] | Acceptance criteria met; QA sign-off | AC-nnn |
| SS-nnn | | | | |

### 3.9 Environment Provisioning Catalog

Owned by DevOps/Platform Engineer; included here by reference.

| Environment | Purpose | Technology Components Required | Owner | Entry Condition |
|---|---|---|---|---|
| Development | Developer testing | TC-nnn, ... | DevOps | Before SS-001 |
| Staging | Integration + QA | | DevOps | Before QA execution |
| Production | Live | | DevOps | After Phase G exit gate |

### 3.10 Deployment Record (sub-artifact, populated during Phase G)

The Deployment Record is appended to the Implementation Plan document as Solution Sprints complete. It is not filled at Phase F; it accumulates during Phase G.

| Deployment ID | Sprint | Work Packages Deployed | Environment | Date | DevOps Agent | Status |
|---|---|---|---|---|---|---|
| DEP-nnn | SS-nnn | WP-nnn, ... | Staging / Production | | | Success / Partial / Rolled Back |

---

## 4. Artifact Sub-Components

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Gap Analysis Summary | Matrix | Yes | §3.2; synthesised from AA/DA/TA gap analyses |
| Implementation Candidate Catalog | Catalog | Yes | §3.3 |
| Work Package Catalog | Catalog | Yes | §3.4 |
| Architecture Roadmap | Diagram (ArchiMate Impl. & Migration VP) | Yes | §3.5 |
| Transition Architecture descriptions | Catalog | Yes if gap requires multiple plateaus | §3.5 |
| Dependency Matrix | Matrix | Yes | §3.6 |
| Risk Register | Catalog | Yes | §3.7; CSCO review required for high severity |
| Solution Sprint Plan | Table | Yes | §3.8; required before Phase G entry |
| Environment Provisioning Catalog | Catalog | Yes | §3.9; DevOps input required |
| Deployment Record | Log (appended during Phase G) | Yes | §3.10 |

---

## 5. Quality Criteria

- [ ] Every gap in the Gap Analysis is addressed by at least one Implementation Candidate.
- [ ] Every accepted Implementation Candidate has a Work Package.
- [ ] All safety-relevant work packages are flagged and CSCO-reviewed.
- [ ] Risk Register contains no unmitigated High-severity risks at Phase F gate.
- [ ] Dependency Matrix is acyclic (no circular dependencies).
- [ ] Solution Sprint Plan is present and approved by PM before Phase G entry.
- [ ] CSCO sign-off recorded on risk register and all safety-relevant work packages.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Phase E draft (candidates and gaps) |
| 0.2.0 | | | Phase F additions (sprint plan, environments) |
| 1.0.0 | | | Baselined at Phase F gate |

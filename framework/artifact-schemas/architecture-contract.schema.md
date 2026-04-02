# Schema: Architecture Contract (`AC`)

**Version:** 1.0.0  
**ADM Phase:** G  
**Owner:** Software Architect / Principal Engineer  
**Consumed by:** Implementing Developer, QA Engineer, CSCO (spot-check), Project Manager (governance)  

---

## 1. Purpose

The Architecture Contract is the binding agreement between the Architecture Stream and the Implementation Stream for a specific Solution Sprint. It specifies which ABBs must be realised, what SBBs are authorised, and what acceptance criteria govern delivery. No Solution Sprint may begin without a signed Architecture Contract for its work packages.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Implementation Plan (`IP`) — work packages for this sprint | Project Manager | Baselined |
| Test Strategy (`TS`) — acceptance criteria | QA Engineer | Baselined |
| Safety Constraint Overlay (`SCO`) — current | CSCO | Phase D update baselined |
| Architecture artifacts (AA, DA, TA) for relevant work packages | SA / SwA | Baselined |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: architecture-contract`
- `safety-relevant:` inherited from the work packages covered
- `csco-sign-off: true` if any safety-relevant work package is included

### 3.2 Contract Scope

| Field | Value |
|---|---|
| Solution Sprint | SS-nnn |
| Work Packages | WP-nnn, WP-nnn, ... |
| Architecture Artifacts in Force | AV v1.x, BA v1.x, AA v1.x, DA v1.x, TA v1.x (list versions) |
| Contract Signed By | Software Architect/PE (Architecture Stream) |
| Contract Accepted By | Implementing Developer + DevOps (Implementation Stream) |
| CSCO Sign-Off | [sign-off ID from SCO, if safety-relevant] |

### 3.3 ABBs in Force

List the specific ABBs (from AA, DA, TA) that are authoritative for this sprint. The implementing agents are bound by these; any deviation requires a Change Record.

| ABB ID | Source Artifact | Description | Constraints Imposed |
|---|---|---|---|
| APP-nnn | AA v1.x | | |
| DE-nnn | DA v1.x | | |
| TC-nnn | TA v1.x | | |

### 3.4 Authorised SBBs

The specific SBBs (products, libraries, infrastructure components) authorised for use in this sprint.

| SBB ID | Name | Type | Version | Authorised For | Restrictions |
|---|---|---|---|---|---|
| SBB-nnn | | Code library / Platform service / Infrastructure component | | WP-nnn | |

### 3.5 Architecture Constraints

Non-negotiable constraints derived from the architecture artifacts that apply to this sprint's implementation.

| Constraint ID | Source | Statement | Applies To | Severity if Violated |
|---|---|---|---|---|
| CON-nnn | AA/DA/TA/SCO ref | | WP-nnn / APP-nnn / TC-nnn | Blocks deployment / Requires waiver |

### 3.6 Acceptance Criteria (from Test Strategy)

Copy of the relevant acceptance criteria from the Test Strategy (`TS`) for this sprint's work packages.

| AC ID | Work Package | Criterion | Test Type | Verified By |
|---|---|---|---|---|
| AC-nnn | WP-nnn | | | QA Engineer |

### 3.7 Compliance Assessment (populated during/after sprint)

The Compliance Assessment is the record of whether the sprint's deliverables satisfy the Architecture Contract. Produced by QA Engineer and Software Architect/PE jointly.

| Assessment Item | Expected | Actual | Compliant | Evidence |
|---|---|---|---|---|
| [ABB satisfied] | | | Yes / No / Partial | Test ref / Code review |
| [Constraint met] | | | | |
| [AC passed] | | | | |

**Overall compliance:** Full / Partial (with documented exceptions) / Non-compliant  
**QA sign-off:**  
**SwA/PE sign-off:**  
**CSCO sign-off (if safety-relevant):**  

---

## 4. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Contract draft |
| 1.0.0 | | | Signed at sprint entry |
| 1.1.0 | | | Compliance assessment appended at sprint closeout |

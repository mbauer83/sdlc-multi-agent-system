# Schema: Architecture Vision (`AV`)

**Version:** 1.0.0  
**ADM Phase:** A  
**Owner:** Solution Architect  
**Consumed by:** Business Architecture (BA), Safety Constraint Overlay (SCO), Statement of Architecture Work, all downstream phases  

---

## 1. Purpose

The Architecture Vision defines the agreed scope, stakeholder landscape, high-level capability map, and safety envelope for a given architecture engagement. It is the first binding artifact produced in the ADM cycle and authorises all subsequent phase work. Every downstream artifact must be traceable to at least one element of the Architecture Vision.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Architecture Principles Register (`PR`) | Solution Architect | Baselined |
| Requirements Register (`RR`) — initial state | Product Owner | At least one iteration complete |
| Market Analysis / Business Scenarios | Sales & Marketing | Draft acceptable |
| Stakeholder identification | Product Owner + Sales & Marketing | Complete |

---

## 3. Required Sections

### 3.1 Summary Header
Conforms to the universal format in `repository-conventions.md §7`. Required fields for this artifact type:
- `artifact-type: architecture-vision`
- `safety-relevant: true` (always — the safety envelope is defined here)
- `csco-sign-off: true` (always required before baselining)

### 3.2 Engagement Context
- Engagement name and identifier
- Reference to authorising business mandate or project charter
- Architecture scope statement: what is in scope, what is explicitly out of scope
- Constraints inherited from Architecture Principles Register (list by principle ID)

### 3.3 Stakeholder Register

| Stakeholder ID | Name / Role | Concern | Viewpoint | Engagement Level |
|---|---|---|---|---|
| STK-nnn | | | | Active / Passive / Inform-only |

**Required fields per row:** ID, role description, primary concern, relevant ArchiMate viewpoint (Stakeholder Viewpoint), engagement level.  
**Minimum:** All agent roles are stakeholders; external stakeholders added as identified.

### 3.4 Business Drivers and Goals

| Driver ID | Description | Priority | Source Stakeholder |
|---|---|---|---|
| DRV-nnn | | High / Medium / Low | STK-nnn |

Each driver must be traceable to at least one stakeholder concern.

### 3.5 Capability Overview

A high-level capability map covering the primary domains in scope. Uses ArchiMate **Strategy Viewpoint** structure:

- **Capability clusters** (3–7 top-level groupings)
- For each capability cluster:
  - Name and one-sentence description
  - Primary value delivered
  - Current state: Existing / Planned / Gap
  - Strategic importance: Core / Supporting / Commodity

This is intentionally high-level. Detail is produced in Phase B (Business Architecture).

### 3.6 Architecture Principles (Phase A application)

Reference the Architecture Principles Register. List the principles most directly constraining this engagement, with a one-line statement of how each applies.

| Principle ID | Principle Name | Application to This Engagement |
|---|---|---|
| P-nnn | | |

### 3.7 Safety Envelope

**This section requires CSCO authorship or co-authorship and CSCO sign-off.**

- **System boundary:** What systems, processes, and components are in scope for safety analysis
- **Hazard categories identified:** High-level hazard types applicable to this engagement (e.g., data loss, availability failure, regulatory non-compliance, physical harm)
- **Initial safety constraints:** Top-level constraints that all subsequent phases must satisfy (will be elaborated in SCO updates per phase)
- **Safety analysis method:** Reference to STAMP/STPA as applied; initial control structure scope
- **CSCO declaration:** Confirmation that the safety envelope is adequate for the engagement scope at this stage of knowledge

### 3.8 Gap Analysis (Baseline vs Target — high level)

| Domain | Baseline State | Target State | Gap Description |
|---|---|---|---|
| Business | | | |
| Application | | | |
| Data | | | |
| Technology | | | |

Detail refined in each subsequent phase.

### 3.9 Architecture Vision Statement

A prose statement (200–400 words) that describes the target future state at a level that is meaningful to senior stakeholders. Must be free of technical jargon. This is the human-readable core of the artifact and is what non-architect agents (PM, PO, Sales/Marketing) primarily consume.

### 3.10 Statement of Architecture Work (reference)

The Statement of Architecture Work is a co-produced artifact (SA + PM). Its identifier is recorded here as a cross-reference. The SoAW document itself is maintained in `engagements/<id>/work-repositories/project-repository/`.

---

## 4. Artifact Sub-Components (catalogs, matrices, diagrams)

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Stakeholder Register | Catalog | Yes | §3.3 |
| Business Drivers Register | Catalog | Yes | §3.4 |
| Capability Overview | Diagram (ArchiMate Strategy VP) | Yes | §3.5 |
| Principles Application Table | Matrix | Yes | §3.6 |
| Safety Envelope Statement | Document section | Yes | §3.7; CSCO owns |
| Gap Analysis Table | Matrix | Yes | §3.8 |
| Architecture Vision Statement | Prose document | Yes | §3.9 |

---

## 5. Quality Criteria (gate checklist supplement)

Before the Phase A gate can pass, the Architecture Vision artifact must satisfy:

- [ ] All stakeholder concerns are captured; no known stakeholder is absent from the register.
- [ ] Every business driver is traceable to at least one stakeholder.
- [ ] Capability overview covers all in-scope domains with no unexplained gaps.
- [ ] Safety envelope is present, authored or co-authored by CSCO, and CSCO sign-off recorded.
- [ ] Architecture Vision Statement is comprehensible to a non-architect stakeholder.
- [ ] Gap analysis is present for all four architecture domains.
- [ ] `csco-sign-off: true` in the summary header.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Initial draft |
| 1.0.0 | | | Baselined at Phase A gate |

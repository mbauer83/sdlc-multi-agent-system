# Schema: Business Architecture (`BA`)

**Version:** 1.0.0  
**ADM Phase:** B  
**Owner:** Solution Architect  
**Consumed by:** Application Architecture (AA), Data Architecture (DA), Safety Constraint Overlay (SCO update), Implementation Plan (IP)  

---

## 1. Purpose

The Business Architecture elaborates the capability map introduced in the Architecture Vision into a detailed model of business capabilities, processes, value streams, and organisational structure. It establishes the functional and motivational ABBs that constrain all information systems and technology decisions in subsequent phases. It is the primary input to Phase C and to the CSCO's business-level safety constraint analysis.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Architecture Vision (`AV`) | Solution Architect | Baselined |
| Requirements Register (`RR`) | Product Owner | Current iteration complete |
| Business Scenarios (detailed) | Product Owner | Draft acceptable |
| Safety Envelope Statement (from `AV`) | CSCO | Baselined (in AV) |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: business-architecture`
- `safety-relevant: true` (always — safety constraints at business level defined here)
- `csco-sign-off: true` (always required)

### 3.2 Business Capability Map

The primary deliverable of Phase B. Structured as a two-level hierarchy:

**Level 1 — Capability Domains** (3–7): High-level groupings aligned with the capability clusters from the Architecture Vision.

**Level 2 — Capabilities** (per domain): Specific, named capabilities with the following attributes per capability:

| Capability ID | Name | Domain | Description | Strategic Classification | Maturity Level | Gap |
|---|---|---|---|---|---|---|
| CAP-nnn | | | | Core / Supporting / Commodity | Current / Developing / Target | Yes / No |

ArchiMate viewpoint: **Capability Map Viewpoint**.

### 3.3 Business Process Catalog

For each in-scope business process:

| Process ID | Name | Owning Capability | Description | Triggering Event | Outcome | Safety-Relevant |
|---|---|---|---|---|---|---|
| BPR-nnn | | CAP-nnn | | | | Yes / No |

Safety-relevant processes must be flagged and will be incorporated into the CSCO's STAMP control structure.

### 3.4 Business Function / Process Matrix

A matrix showing which capabilities are realised by which processes:

| | BPR-001 | BPR-002 | ... |
|---|---|---|---|
| **CAP-001** | ● | — | |
| **CAP-002** | ○ | ● | |

Symbols: ● = primary realisation; ○ = contributing; — = no relationship.

### 3.5 Value Stream Map

For each primary value stream in scope:

| Value Stream ID | Name | Triggering Stakeholder | Value Delivered | Key Processes (ordered) | Metrics |
|---|---|---|---|---|---|
| VS-nnn | | STK-nnn | | BPR-nnn, ... | |

ArchiMate viewpoint: **Business Process Cooperation Viewpoint** (showing cross-process interactions within a value stream).

### 3.6 Motivation Architecture

Traces from stakeholder goals through to architecture drivers and business capabilities. Uses ArchiMate **Goal Realization Viewpoint** structure:

| Goal ID | Stakeholder | Goal Statement | Driver (from AV) | Realising Capability |
|---|---|---|---|---|
| GL-nnn | STK-nnn | | DRV-nnn | CAP-nnn |

### 3.7 Organisational Model

| Org Unit ID | Name | Type | Primary Capabilities Owned | Key Roles |
|---|---|---|---|---|
| ORG-nnn | | Division / Team / External | CAP-nnn, ... | |

ArchiMate viewpoint: **Organisation Viewpoint**.

### 3.8 Business Services Catalog

Business services are the externally visible outputs of the business architecture — what the business provides to stakeholders.

| Service ID | Name | Provider (ORG) | Consumer (Stakeholder) | Realised By (Process) |
|---|---|---|---|---|
| BSV-nnn | | ORG-nnn | STK-nnn | BPR-nnn |

### 3.9 Gap Analysis (Business Domain)

Elaboration of the business-domain gap row from the Architecture Vision:

| Capability | Baseline State | Target State | Gap Type | Priority |
|---|---|---|---|---|
| CAP-nnn | | | Missing / Underdeveloped / Redundant | High / Med / Low |

### 3.10 Business-Level Safety Constraint Overlay (reference)

The CSCO produces or updates the Safety Constraint Overlay artifact (`SCO`) with business-level safety constraints derived from this artifact. The `SCO` version that incorporates Phase B analysis is cross-referenced here by artifact ID and version.

---

## 4. Artifact Sub-Components

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Business Capability Map | Catalog + Diagram (ArchiMate Capability Map VP) | Yes | §3.2 |
| Business Process Catalog | Catalog | Yes | §3.3 |
| Business Function/Process Matrix | Matrix | Yes | §3.4 |
| Value Stream Map | Diagram (ArchiMate BPC VP) | Yes | §3.5 |
| Motivation Architecture | Diagram (ArchiMate Goal Realization VP) | Yes | §3.6 |
| Organisational Model | Diagram (ArchiMate Organisation VP) | Yes | §3.7 |
| Business Services Catalog | Catalog | Yes | §3.8 |
| Gap Analysis — Business | Matrix | Yes | §3.9 |
| SCO cross-reference | Reference | Yes | §3.10 |

---

## 5. Quality Criteria

- [ ] Every capability in the Capability Map is traceable to at least one business driver from the Architecture Vision.
- [ ] Every safety-relevant process is flagged and cross-referenced to the Safety Constraint Overlay.
- [ ] All value streams are complete end-to-end (trigger → outcome).
- [ ] Motivation architecture traces from every goal to at least one realising capability.
- [ ] CSCO sign-off on the business-level SCO update is recorded.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Initial draft |
| 1.0.0 | | | Baselined at Phase B gate |

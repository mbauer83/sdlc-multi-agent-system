# RACI Matrix

**Version:** 1.0.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager  
**Last Updated:** 2026-04-02

---

## 1. Purpose and Notation

This document defines the responsibility assignment for every artifact and phase gate in the system. It is the authoritative reference for resolving ownership ambiguity. No artifact may be produced without an accountable agent identified here.

| Symbol | Meaning |
|---|---|
| **●** | Accountable — owns the artifact; produces it; signs off on its readiness |
| **○** | Consulted — contributes content or review; must be engaged before baseline |
| **~** | Informed — receives the artifact summary on completion; no contribution required |
| **G** | Gate authority — must approve before phase transition; veto blocks the gate |
| **—** | Not involved |

**Rule:** Every artifact row must have exactly one **●**. Multiple **○** are permitted. A CSCO **G** on any row means CSCO holds gate authority for that artifact regardless of other roles.

---

## 2. Agent Role Abbreviations

| Abbreviation | Role |
|---|---|
| SM | Sales & Marketing Manager |
| PO | Product Owner |
| SA | Solution Architect |
| SwA | Software Architect / Principal Engineer |
| DE | Implementing Developer |
| QA | QA Engineer |
| DO | DevOps / Platform Engineer |
| PM | Project Manager |
| CS | Chief Safety & Compliance Officer |

---

## 3. Artifact Ownership Matrix

### 3.1 Foundation & Cross-Cutting Artifacts

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Architecture Principles Register (`PR`) | — | ○ | ● | ○ | — | — | — | G | G |
| Requirements Register (`RR`) | ○ | ● | ○ | — | — | — | — | ~ | ○ |
| Safety Constraint Overlay (`SCO`) | — | — | ○ | ○ | — | — | — | G | ● |
| Architecture Repository structure | — | — | ● | ○ | — | — | — | ○ | — |
| RACI Matrix (this document) | — | — | ○ | — | — | — | — | ● | ○ |

### 3.2 Phase A — Architecture Vision

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Stakeholder Map | ○ | ○ | ● | — | — | — | — | ○ | ○ |
| Architecture Vision (`AV`) | ~ | ○ | ● | ○ | — | — | — | G | G |
| Statement of Architecture Work | — | ○ | ○ | — | — | — | — | ● | G |
| Safety Envelope Statement (in `SCO`) | — | — | ○ | — | — | — | — | — | ● |

### 3.3 Phase B — Business Architecture

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Business Architecture (`BA`) | — | ○ | ● | — | — | — | — | G | G |
| Business Capability Map | — | ○ | ● | — | — | — | — | ~ | — |
| Business Process Catalog | — | ○ | ● | — | — | — | — | ~ | — |
| Value Stream Diagram | — | ○ | ● | — | — | — | — | ~ | — |
| Business-level `SCO` update | — | — | ○ | — | — | — | — | — | ● |

### 3.4 Phase C — Application Architecture

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Application Architecture (`AA`) | — | — | ● | ○ | — | — | — | G | G |
| Application Component Catalog | — | — | ● | ○ | — | — | — | ~ | — |
| Interface Catalog | — | — | ● | ○ | — | — | — | ~ | — |
| Application Interaction Matrix | — | — | ● | ○ | — | — | — | ~ | — |
| Application-level `SCO` update | — | — | ○ | — | — | — | — | — | ● |

### 3.5 Phase C — Data Architecture

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Data Architecture (`DA`) | — | — | ● | ○ | — | — | — | G | G |
| Data Entity Catalog | — | — | ● | ○ | — | — | — | ~ | — |
| Logical Data Model | — | — | ● | ○ | — | — | — | ~ | — |
| Data Classification Register | — | — | ● | — | — | — | — | ~ | ○ |
| Data-level `SCO` update | — | — | ○ | — | — | — | — | — | ● |

### 3.6 Phase D — Technology Architecture

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Technology Architecture (`TA`) | — | — | ○ | ● | — | — | ○ | G | G |
| Technology Component Catalog | — | — | — | ● | — | — | ○ | ~ | — |
| Technology/Application Matrix | — | — | ○ | ● | — | — | — | ~ | — |
| ADR Register | — | — | — | ● | — | — | — | ~ | ○ |
| Infrastructure Diagram | — | — | — | ● | — | — | ○ | ~ | — |
| Technology-level `SCO` update | — | — | — | ○ | — | — | — | — | ● |

### 3.7 Phase E — Opportunities & Solutions

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Implementation Candidate Catalog | — | ○ | ○ | ● | — | — | — | G | G |
| Gap Analysis Matrix | — | — | ○ | ● | — | — | — | ○ | — |
| Work Package Catalog | — | — | — | ○ | — | — | — | ● | ~ |
| Initial Test Strategy (`TS`) | — | — | — | ○ | — | ● | — | G | ○ |
| Risk Register | — | — | ○ | ○ | — | — | — | ● | G |
| Architecture Roadmap draft (`AR`) | — | — | ○ | ○ | — | — | — | ● | ~ |

### 3.8 Phase F — Migration Planning

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Implementation Plan (`IP`) | — | — | ○ | ○ | — | — | ○ | ● | G |
| Architecture Roadmap final (`AR`) | — | — | ○ | ○ | — | — | — | ● | ~ |
| Environment Provisioning Catalog | — | — | — | ○ | — | — | ● | ~ | — |
| Dependency Matrix | — | — | — | ○ | — | — | — | ● | ~ |
| Transition Architecture Diagrams | — | — | ○ | ● | — | — | — | ~ | ○ |
| Solution Sprint Plan | — | — | — | — | — | — | — | ● | ~ |

### 3.9 Phase G — Implementation Governance

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Architecture Contract (`AC`) | — | — | — | ● | — | — | — | G | G |
| Feature Implementation (code, PR) | — | — | — | ○ | ● | — | — | ~ | — |
| Unit / Integration Test Reports | — | — | — | — | — | ● | — | ~ | — |
| Compliance Assessment (`CA`) | — | — | — | ○ | — | ● | — | G | G |
| Deployment Record (`DR`) | — | — | — | — | — | — | ● | ~ | — |
| CSCO Spot-check Record | — | — | — | — | — | — | — | ~ | ● |
| Governance Checkpoint Record | — | — | — | — | — | — | — | ● | — |
| Defect Register | — | — | — | — | ○ | ● | — | ~ | — |

### 3.10 Phase H — Architecture Change Management

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Change Record (`CR`) | — | ○ | ● | ○ | — | — | — | G | G |
| Updated Architecture Artifacts | — | — | ● | ○ | — | — | — | G | G |
| Retrospective Note | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ |
| Knowledge Base update | — | — | — | — | — | — | — | ● | — |

### 3.11 Requirements Management (Cross-Phase)

| Artifact | SM | PO | SA | SwA | DE | QA | DO | PM | CS |
|---|---|---|---|---|---|---|---|---|---|
| Requirements Register updates | ○ | ● | ○ | — | ○ | — | — | ~ | ○ |
| Requirements Traceability Matrix | — | ● | ○ | — | — | — | — | G | — |
| Market Analysis / Business Scenarios | ● | ○ | — | — | — | — | — | ~ | — |

---

## 4. Phase Gate Authority Matrix

This table identifies who holds gate authority at each phase transition. **G** = gate authority (must approve); **●** = PM records decision.

| Gate | PM | SA | SwA | CS | Notes |
|---|---|---|---|---|---|
| Prelim → A | ● | G | — | G | RACI confirmed by all agents required |
| A → B | ● | G | — | G | Safety envelope + SoAW must be approved |
| B → C | ● | G | — | G | Business-level SCO accepted |
| C → D | ● | G | G | G | Both AA and DA must be baselined |
| D → E | ● | ○ | G | G | All ADRs recorded |
| E → F | ● | ○ | G | G | Risk Register reviewed by CS |
| F → G | ● | ○ | G | G | Solution Sprint Plan approved |
| G exit | ● | — | G | G | Full regression + deployment record |
| H (formal) | ● | G | G | G | Change class determines scope |

---

## 5. Cross-Reference: Artifact ID → Schema

| Artifact ID | Schema File |
|---|---|
| `AV` | `framework/artifact-schemas/architecture-vision.schema.md` |
| `BA` | `framework/artifact-schemas/business-architecture.schema.md` |
| `AA` | `framework/artifact-schemas/application-architecture.schema.md` |
| `DA` | `framework/artifact-schemas/data-architecture.schema.md` |
| `TA` | `framework/artifact-schemas/technology-architecture.schema.md` |
| `IP` | `framework/artifact-schemas/implementation-plan.schema.md` |
| `TS` | `framework/artifact-schemas/test-strategy.schema.md` |
| `AC` | `framework/artifact-schemas/architecture-contract.schema.md` |
| `CR` | `framework/artifact-schemas/change-record.schema.md` |
| `SCO` | `framework/artifact-schemas/safety-constraint-overlay.schema.md` |
| `RR` | `framework/artifact-schemas/requirements-register.schema.md` |

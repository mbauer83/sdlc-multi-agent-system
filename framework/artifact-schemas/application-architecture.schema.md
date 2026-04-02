# Schema: Application Architecture (`AA`)

**Version:** 1.0.0  
**ADM Phase:** C (Application sub-track)  
**Owner:** Solution Architect  
**Consumed by:** Data Architecture (DA — mutual reference), Technology Architecture (TA), Architecture Contract (AC), Safety Constraint Overlay (SCO update)  

---

## 1. Purpose

The Application Architecture defines the logical application components, their responsibilities, interfaces, and interaction patterns that realise the business capabilities and processes defined in the Business Architecture. It establishes application-level ABBs that directly constrain Phase D technology decisions. The Application Architecture is technology-independent: it describes *what* components exist and how they interact, not *how* they are implemented.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Business Architecture (`BA`) | Solution Architect | Baselined |
| Requirements Register (`RR`) | Product Owner | Current |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: application-architecture`
- `safety-relevant: true` (any application with a safety-relevant process must be flagged)
- `csco-sign-off:` required if any safety-relevant application component is defined

### 3.2 Application Component Catalog

The definitive list of logical application components (ABBs) in scope.

| Component ID | Name | Type | Responsibility | Realises Capability | Safety-Relevant | Status |
|---|---|---|---|---|---|---|
| APP-nnn | | Service / Store / Gateway / UI / Integration | One-sentence description | CAP-nnn | Yes/No | New/Existing/Modified/Retiring |

**Component Types:**
- **Service** — encapsulates business logic or process execution
- **Store** — manages data persistence (logical; physical details in DA)
- **Gateway** — mediates access between external actors and internal components
- **UI** — user-facing presentation layer
- **Integration** — connects components or external systems (adapter, broker, event bus)

### 3.3 Interface Catalog

All interfaces (APIs, events, messages) exposed by or consumed by application components.

| Interface ID | Name | Exposed By | Consumed By | Protocol / Style | Data Entities Involved | Safety-Relevant |
|---|---|---|---|---|---|---|
| IFC-nnn | | APP-nnn | APP-nnn (or external) | REST / gRPC / Event / Batch | DE-nnn (from DA) | Yes/No |

### 3.4 Application/Business Function Matrix

Cross-reference showing which application components realise which business processes.

| | APP-001 | APP-002 | APP-nnn |
|---|---|---|---|
| **BPR-001** | ● | — | |
| **BPR-002** | ○ | ● | |

Symbols: ● = primary realisation; ○ = contributing; — = no relationship.

### 3.5 Application Interaction Diagram

ArchiMate **Application Cooperation Viewpoint** — shows how application components interact to realise business services and value streams. One diagram per major value stream or functional domain is recommended.

Content requirements per diagram:
- All application components involved
- Interfaces used between components (from Interface Catalog)
- External systems or actors at the boundary
- Direction and nature of interactions (synchronous / asynchronous / event-driven)

### 3.6 Application Architecture Diagram (overview)

A single overview diagram (ArchiMate **Service Realization Viewpoint**) showing how the full application landscape realises business services. Uses layered notation: business layer → application layer.

### 3.7 External System and Integration Points

| Integration ID | External System | Integration Type | Direction | Interface Used | Data Sensitivity |
|---|---|---|---|---|---|
| INT-nnn | | Direct API / Event / Batch / Manual | Inbound / Outbound / Bidirectional | IFC-nnn | Public / Internal / Confidential / Restricted |

### 3.8 Application-Level Gap Analysis

| Component | Baseline (existing system) | Target (this architecture) | Gap | Resolution Approach |
|---|---|---|---|---|
| APP-nnn | | | New / Modified / Retired | Build / Buy / Reuse / Retire |

### 3.9 Application-Level Safety Constraint Overlay (reference)

Cross-reference to the `SCO` version that incorporates Phase C (Application) constraints. Safety-relevant components must have their safety constraints explicitly noted here by APP-ID.

| Component ID | Safety Constraint Reference (SCO section) |
|---|---|
| APP-nnn | SCO §n.n |

---

## 4. Artifact Sub-Components

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Application Component Catalog | Catalog | Yes | §3.2 |
| Interface Catalog | Catalog | Yes | §3.3 |
| Application/Business Function Matrix | Matrix | Yes | §3.4 |
| Application Interaction Diagram(s) | Diagram (ArchiMate App Cooperation VP) | Yes | §3.5; one per major value stream |
| Application Architecture Overview | Diagram (ArchiMate Service Realization VP) | Yes | §3.6 |
| External Integration Catalog | Catalog | Yes | §3.7 |
| Gap Analysis — Application | Matrix | Yes | §3.8 |
| SCO cross-reference | Reference | Yes if safety-relevant | §3.9 |

---

## 5. Quality Criteria

- [ ] Every application component realises at least one business capability or process from the BA.
- [ ] Every interface in the Interface Catalog is referenced by at least one interaction diagram.
- [ ] All safety-relevant components are flagged and cross-referenced to the SCO.
- [ ] The application architecture is technology-independent — no specific products, platforms, or languages are specified (those belong in Phase D).
- [ ] External integration points are all catalogued with data sensitivity classification.
- [ ] CSCO sign-off present if any safety-relevant component is defined.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Initial draft |
| 1.0.0 | | | Baselined at Phase C gate |

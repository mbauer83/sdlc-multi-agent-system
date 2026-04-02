# Schema: Technology Architecture (`TA`)

**Version:** 1.0.0  
**ADM Phase:** D  
**Owner:** Software Architect / Principal Engineer  
**Consumed by:** Implementation Plan (IP), Architecture Contract (AC), Safety Constraint Overlay (SCO update), DevOps/Platform Engineer (environment provisioning)  

---

## 1. Purpose

The Technology Architecture defines the concrete technology stack, infrastructure topology, platform services, and deployment model that realise the application and data ABBs from Phase C. Phase D is the transition point from technology-independent ABBs to SBB candidates: specific products, platforms, and infrastructure patterns are selected here and recorded in Architecture Decision Records (ADRs). The Technology Architecture is the primary input for implementation planning (Phase E/F) and directly governs the DevOps/Platform Engineer's work.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Application Architecture (`AA`) | Solution Architect | Baselined |
| Data Architecture (`DA`) | Solution Architect | Baselined |
| Architecture Principles Register (`PR`) | Solution Architect | Baselined |
| Safety Constraint Overlay (`SCO`) — Phase C update | CSCO | Baselined |
| Technology standards and constraints (from SIB) | Software Architect/PE | Draft acceptable |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: technology-architecture`
- `safety-relevant: true` if any safety-relevant application or data component is in scope (inherited from AA/DA)
- `csco-sign-off: true` (always required — technology choices have safety and security implications)

### 3.2 Technology Component Catalog

The definitive list of technology components (SBB candidates) selected for this architecture.

| Component ID | Name | Type | Selected Product / Platform | Version Constraint | Realises App Component | Rationale (ADR ref) | Status |
|---|---|---|---|---|---|---|---|
| TC-nnn | | Runtime / Platform / Store / Network / Security / Observability | | | APP-nnn or DA entity | ADR-nnn | Selected / Evaluated / Rejected |

**Component Types:**
- **Runtime** — language runtime, container runtime, serverless platform
- **Platform** — cloud platform, Kubernetes, PaaS
- **Store** — database, object storage, cache, message broker
- **Network** — load balancer, API gateway, VPN, CDN
- **Security** — identity provider, secrets manager, WAF, certificate authority
- **Observability** — metrics, logging, tracing, alerting

### 3.3 Technology/Application Matrix

Cross-reference between technology components and the application components they host or support.

| | TC-001 | TC-002 | TC-nnn |
|---|---|---|---|
| **APP-001** | ● | ○ | |
| **APP-002** | — | ● | |

Symbols: ● = primary host/support; ○ = auxiliary; — = no relationship.

### 3.4 Infrastructure Diagram

ArchiMate **Technology Viewpoint** — shows technology components, their deployment relationships, and communication paths.

Required elements:
- All technology components from the catalog
- Hosting relationships (what runs on what)
- Network connections between components (typed: synchronous / async / managed service)
- Deployment environments: at minimum Production and one non-production environment

### 3.5 Deployment Topology

ArchiMate **Technology Usage Viewpoint** (or **Physical Viewpoint** for on-premises components) showing how application components map to technology components across environments.

| Deployment Zone | Technology Components | Application Components Hosted | Connectivity |
|---|---|---|---|
| Production | TC-nnn, ... | APP-nnn, ... | Internal / External |
| Staging | | | |
| Development | | | |

### 3.6 Architecture Decision Records (ADR Register)

One ADR per significant technology decision. ADRs are the authoritative rationale record for all Phase D choices.

**ADR format:**

```markdown
### ADR-nnn: <Title>

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-nnn  
**Decision Maker:** Software Architect/PE  
**Sprint:** <sprint-id>

**Context:**
[What is the problem or requirement driving this decision?]

**Decision:**
[What was decided? Be precise — name the specific product/pattern/approach chosen.]

**Rationale:**
[Why this option over the alternatives considered? Link to constraints from PR, AA, DA, SCO.]

**Consequences:**
[What becomes easier? What becomes harder? What risks are introduced?]

**Alternatives Considered:**
[Other options evaluated and why they were not selected.]
```

**Mandatory ADRs:** One ADR is required for each of the following decision types if in scope:
- Primary runtime/compute platform
- Primary data store per data classification level
- Authentication and authorisation approach
- Network boundary and ingress strategy
- Observability stack
- Any decision that overrides or constrains an Architecture Principle

### 3.7 Technology Standards Catalog

| Standard ID | Standard Name | Type | Source | Applies To | Mandatory / Recommended |
|---|---|---|---|---|---|
| STD-nnn | | Industry / Internal / Regulatory | | TC-nnn or domain | |

### 3.8 Technology Lifecycle Analysis

| Component ID | Product | Current Version | End-of-Support Date | Upgrade Path | Risk Level |
|---|---|---|---|---|---|
| TC-nnn | | | | | Low / Medium / High |

Components with a High lifecycle risk must have a mitigation ADR.

### 3.9 Technology-Level Safety Constraint Overlay (reference)

Cross-reference to the `SCO` version covering Phase D constraints. Technology choices that affect safety constraints must be noted here.

| Component ID | Safety Constraint Reference (SCO section) | Impact |
|---|---|---|
| TC-nnn | SCO §n.n | |

### 3.10 Technology Gap Analysis

| Domain | Baseline State | Target State | Gap | Resolution in Phase E/F |
|---|---|---|---|---|
| Runtime | | | | |
| Storage | | | | |
| Network | | | | |
| Security | | | | |
| Observability | | | | |

---

## 4. Artifact Sub-Components

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Technology Component Catalog | Catalog | Yes | §3.2 |
| Technology/Application Matrix | Matrix | Yes | §3.3 |
| Infrastructure Diagram | Diagram (ArchiMate Technology VP) | Yes | §3.4 |
| Deployment Topology | Diagram (ArchiMate Tech Usage VP) | Yes | §3.5 |
| ADR Register | Catalog (structured records) | Yes | §3.6; min. one per mandatory decision type |
| Technology Standards Catalog | Catalog | Yes | §3.7 |
| Technology Lifecycle Analysis | Catalog | Yes | §3.8 |
| SCO cross-reference | Reference | Yes | §3.9 |
| Gap Analysis — Technology | Matrix | Yes | §3.10 |

---

## 5. Quality Criteria

- [ ] Every application component from the AA is mapped to at least one technology component.
- [ ] Every data entity classification level has a corresponding storage technology decision with an ADR.
- [ ] All mandatory ADR types are present.
- [ ] No technology component is selected without an ADR.
- [ ] Technology lifecycle risks are assessed; High-risk components have mitigation ADRs.
- [ ] Safety-relevant technology constraints are cross-referenced to the SCO.
- [ ] CSCO sign-off recorded.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Initial draft |
| 1.0.0 | | | Baselined at Phase D gate |

# Schema: Data Architecture (`DA`)

**Version:** 1.0.0  
**ADM Phase:** C (Data sub-track)  
**Owner:** Solution Architect  
**Consumed by:** Application Architecture (AA — mutual reference), Technology Architecture (TA), Architecture Contract (AC), Safety Constraint Overlay (SCO update)  

---

## 1. Purpose

The Data Architecture defines the logical data model, data entity catalogue, data flows, classification scheme, and governance rules for all data in scope. It establishes data-level ABBs that constrain Phase D persistence and platform decisions. Like the Application Architecture, it is technology-independent at baseline: it defines *what* data exists and how it relates, not *where* or *how* it is stored.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Business Architecture (`BA`) | Solution Architect | Baselined |
| Application Architecture (`AA`) | Solution Architect | At minimum draft — mutual reference |
| Requirements Register (`RR`) | Product Owner | Current |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined |

---

## 3. Required Sections

### 3.1 Summary Header
- `artifact-type: data-architecture`
- `safety-relevant: true` if any data entity is safety-relevant (e.g., safety logs, control data)
- `csco-sign-off:` required if safety-relevant data entities are defined

### 3.2 Data Entity Catalog

The definitive list of logical data entities (ABBs) in scope.

| Entity ID | Name | Description | Classification | Owning Application | Retention | Safety-Relevant |
|---|---|---|---|---|---|---|
| DE-nnn | | | Public / Internal / Confidential / Restricted / Safety-Critical | APP-nnn | Policy ref | Yes/No |

**Classification levels:**
- **Public** — no access restrictions; freely shareable
- **Internal** — organisational use only; no external sharing without approval
- **Confidential** — role-based access; subject to data governance policy
- **Restricted** — highly sensitive; named-individual access; legal/regulatory obligations apply
- **Safety-Critical** — data whose corruption, loss, or unauthorised modification could trigger a safety constraint violation

### 3.3 Logical Data Model

A diagram showing entities, their attributes, and relationships. ArchiMate **Information Structure Viewpoint**.

Requirements:
- All entities from the Data Entity Catalog represented
- Relationships typed: Association / Composition / Aggregation / Specialisation
- Cardinality noted on all relationships
- Key attributes listed per entity (not an exhaustive field list — that belongs in detailed design)

### 3.4 Data/Business Function Matrix

Cross-reference showing which data entities are created, read, updated, or deleted (CRUD) by which business processes.

| | DE-001 | DE-002 | DE-nnn |
|---|---|---|---|
| **BPR-001** | C | R | RU |
| **BPR-002** | — | CRU | D |

Symbols: C=Create, R=Read, U=Update, D=Delete. Combine as needed (e.g., CRUD, RU).

### 3.5 Data Flow Diagram

Shows how data moves between application components, external systems, and stores. One diagram per major value stream or integration boundary is recommended.

Content requirements:
- All data entities involved in cross-component flows
- Direction of flow
- Transformation or processing that occurs in transit (if any)
- Trust boundaries (clearly marked — relevant for security and safety analysis)

### 3.6 Data Classification Register

A summary register of all data sensitivity boundaries identified:

| Boundary ID | Type | Data Crossing Boundary | Classification | Protection Requirement |
|---|---|---|---|---|
| DB-nnn | Internal/External / Trust / Regulatory | DE-nnn, ... | | Encryption / Anonymisation / Access control / Audit log |

### 3.7 Data Governance Rules

| Rule ID | Scope (entities) | Rule Statement | Owner | Enforcement Point |
|---|---|---|---|---|
| DGR-nnn | DE-nnn, ... | | ORG-nnn | Application component / Infrastructure / Policy |

Minimum rules required:
- Retention and deletion rules for each entity classification level
- Access control rules for Confidential and above
- Audit logging requirements for Safety-Critical entities
- Cross-border or regulatory transfer restrictions (if applicable)

### 3.8 Data-Level Gap Analysis

| Entity / Domain | Baseline State | Target State | Gap | Resolution |
|---|---|---|---|---|
| DE-nnn or domain | | | New / Modified / Deprecated | Migrate / Cleanse / Create |

### 3.9 Data-Level Safety Constraint Overlay (reference)

Cross-reference to the `SCO` version covering Phase C (Data) constraints, particularly for Safety-Critical entities.

| Entity ID | Safety Constraint Reference (SCO section) |
|---|---|
| DE-nnn | SCO §n.n |

---

## 4. Artifact Sub-Components

| Sub-Component | Type | Required | Notes |
|---|---|---|---|
| Data Entity Catalog | Catalog | Yes | §3.2 |
| Logical Data Model | Diagram (ArchiMate Information Structure VP) | Yes | §3.3 |
| Data/Business Function Matrix (CRUD) | Matrix | Yes | §3.4 |
| Data Flow Diagram(s) | Diagram | Yes | §3.5; one per major value stream |
| Data Classification Register | Register | Yes | §3.6 |
| Data Governance Rules | Catalog | Yes | §3.7 |
| Gap Analysis — Data | Matrix | Yes | §3.8 |
| SCO cross-reference | Reference | Yes if safety-relevant | §3.9 |

---

## 5. Quality Criteria

- [ ] Every data entity is traceable to at least one business process in the BA.
- [ ] Every entity has a classification and a retention rule.
- [ ] All Safety-Critical entities are flagged and cross-referenced to the SCO.
- [ ] Data flows across all trust boundaries are documented.
- [ ] The data model is technology-independent — no specific databases, file formats, or storage mechanisms are prescribed (those belong in Phase D).
- [ ] CRUD matrix covers all in-scope processes and entities.
- [ ] CSCO sign-off present if Safety-Critical entities are defined.

---

## 6. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Initial draft |
| 1.0.0 | | | Baselined at Phase C gate |

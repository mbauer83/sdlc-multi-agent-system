# Schema: Data Architecture (`DA`)

**Version:** 2.0.0
**ADM Phase:** C (Data sub-track)
**Owner:** Solution Architect
**Consumed by:** Application Architecture (AA — mutual reference), Technology Architecture (TA), Architecture Contract (AC), Safety Constraint Overlay (SCO update)

---

## 1. Purpose

The Data Architecture defines the logical data model, data entity catalogue, data flows, classification scheme, and governance rules for all data in scope. It establishes data entities that constrain Phase D persistence and platform decisions. Like the Application Architecture, it is **technology-independent** at baseline: it defines *what* data exists and how it relates, not *where* or *how* it is stored.

Under ERP v2.0 the Data Architecture is the set of entity and connection files produced in the architecture-repository during Phase C (data sub-track). Data objects live in the `application/data-objects/` directory (ArchiMate Information Structure layer). An overview document (`overview/da-overview.md`) provides the cross-phase handoff summary.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Business Architecture (`BA`) | Solution Architect | Baselined |
| Application Architecture (`AA`) | Solution Architect | At minimum draft — mutual reference |
| Requirements Register (`RR`) | Product Owner | Current |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined |

---

## 3. ERP Entity Output

Phase C (data track) produces entity files in the `application/data-objects/` directory and corresponding connections. All files follow the universal format in `framework/artifact-schemas/entity-conventions.md`.

### 3.1 Data Object Entities — `architecture-repository/application/data-objects/`

| Prefix | artifact-type | Directory | §content Required Sections |
|---|---|---|---|
| `DOB-nnn` | `data-object` | `application/data-objects/` | Name; Description; Classification (see §3.2); Owning Application (`APP-nnn`); Retention Policy; Safety-Relevant (true/false); Key Attributes (name: type, not exhaustive — full field list is detailed design) |

### 3.2 Data Classification Levels

| Level | Meaning | Minimum Controls |
|---|---|---|
| Public | No access restrictions; freely shareable | None required |
| Internal | Organisational use only; no external sharing | Access control policy |
| Confidential | Role-based access; subject to data governance | RBAC + audit log |
| Restricted | Highly sensitive; named-individual access | RBAC + encryption + legal/regulatory compliance |
| Safety-Critical | Corruption, loss, or unauthorised modification could trigger a safety constraint violation | All Restricted controls + integrity checking + CSCO sign-off |

### 3.3 `§display` Requirements

Every `DOB-nnn` that appears in an ER diagram must have a `### er` subsection in `§display`. The `### er` block specifies: `class-label` (entity name for the PUML class declaration) and `attributes` (list of `name: type` pairs for key attributes). The `generate_er_content(entity_ids)` tool reads these blocks to produce PUML class declarations.

`DOB-nnn` entities that appear in ArchiMate diagrams (e.g., in a data flow or motivation diagram) additionally need a `### archimate` subsection.

---

## 4. Connections Produced

### 4.1 ER Connections — `architecture-repository/connections/er/`

ER connections represent logical data model relationships between `DOB-nnn` entities.

| Connection Type | Source → Target | Directory | Notes |
|---|---|---|---|
| `er-one-to-many` | `DOB-nnn` → `DOB-nnn` | `connections/er/one-to-many/` | One source instance relates to many target instances; use `foreign-key:` field in `§content` |
| `er-many-to-many` | `DOB-nnn` → `DOB-nnn` | `connections/er/many-to-many/` | Many-to-many; note the junction entity if applicable |
| `er-one-to-one` | `DOB-nnn` → `DOB-nnn` | `connections/er/one-to-one/` | One-to-one ownership or identity relationship |

Each ER connection file must include a `### er` subsection in `§display` specifying the cardinality notation (`|o--o{`, `||--||`, etc.) for use by `generate_er_relations(connection_ids)`.

### 4.2 ArchiMate Access Connections — `architecture-repository/connections/archimate/access/`

These are produced jointly by AA and DA tracks once both are sufficiently populated:

| Connection Type | Source → Target | Directory | Notes |
|---|---|---|---|
| `archimate-access` | `APP-nnn` → `DOB-nnn` | `connections/archimate/access/` | Component accesses data object; `access-type:` field: read/write/read-write |

### 4.3 CRUD Matrix Representation

The Data/Business Function CRUD matrix (which processes Create/Read/Update/Delete which entities) is documented in `overview/da-overview.md` as a table. Individual CRUD relationships do not require separate connection files; the matrix in the overview is authoritative.

---

## 5. Data Governance Catalog

SA records the following governance artefacts in `overview/da-overview.md` (not as separate entity files):

- **Data Classification Register** — boundary-crossing table: `DB-nnn | Type | Data Crossing Boundary | Classification | Protection Requirement`
- **Data Governance Rules** — `DGR-nnn | Scope | Rule Statement | Owner | Enforcement Point`
  - Minimum rules: retention/deletion per classification; access control for Confidential+; audit logging for Safety-Critical; cross-border/regulatory transfer restrictions if applicable.

---

## 6. Overview Document

SA produces `architecture-repository/overview/da-overview.md` as a **repository-content artifact** (frontmatter `artifact-type: da-overview`).

Required sections:
- **Summary Header** — YAML frontmatter per `repository-conventions.md §7`:
  - `artifact-type: da-overview`; `safety-relevant: true` if Safety-Critical entities defined; `csco-sign-off: required if safety-critical entities`
  - `summary:` 2–4 sentences covering entity count, classification distribution, open data governance gaps
  - `key-decisions:` list; `open-issues:` list; `pending-clarifications:` list
- **CRUD Matrix** — `BPR-nnn` rows × `DOB-nnn` columns; symbols C/R/U/D combined.
- **Data Classification Register** (see §5).
- **Data Governance Rules** (see §5).
- **Data-Level Gap Analysis** — Entity/Domain / Baseline / Target / Gap / Resolution.
- **Safety Constraint Overlay Cross-reference** — per `DOB-nnn` with `safety-relevant: true`: SCO section reference.

---

## 7. Quality Criteria

- [ ] Every `DOB-nnn` is traceable to at least one `BPR-nnn` in the CRUD matrix.
- [ ] Every entity has a `classification` field and an entry in the Data Classification Register.
- [ ] All Safety-Critical entities are flagged `safety-relevant: true` and cross-referenced to the SCO.
- [ ] Data flows across trust boundaries are documented in the CRUD matrix or Data Flow section of the overview.
- [ ] The data model is technology-independent — no specific databases, file formats, or storage mechanisms appear in any `DOB-nnn` entity.
- [ ] CSCO sign-off present (`csco-sign-off: true` in `da-overview.md`) if Safety-Critical entities are defined.

---

## 8. Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-04-02 | Initial schema — monolithic artifact format |
| 2.0.0 | 2026-04-03 | Refactored to ERP v2.0 entity-file output; data objects in application/data-objects/; ER connections in connections/er/ |

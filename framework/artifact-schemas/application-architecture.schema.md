# Schema: Application Architecture (`AA`)

**Version:** 2.0.0
**ADM Phase:** C (Application sub-track)
**Owner:** Solution Architect
**Consumed by:** Data Architecture (DA — mutual reference), Technology Architecture (TA), Architecture Contract (AC), Safety Constraint Overlay (SCO update)

---

## 1. Purpose

The Application Architecture defines the logical application components, their responsibilities, interfaces, and interaction patterns that realise the business capabilities and processes defined in the Business Architecture. It establishes application-level entities that directly constrain Phase D technology decisions. The Application Architecture is **technology-independent**: it describes *what* components exist and how they interact, not *how* they are implemented.

Under ERP v2.0 the Application Architecture is the set of entity and connection files produced in the architecture-repository during Phase C (application sub-track). An overview document (`overview/aa-overview.md`) provides the cross-phase handoff summary.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Business Architecture (`BA`) | Solution Architect | Baselined |
| Requirements Register (`RR`) | Product Owner | Current |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined |

---

## 3. ERP Entity Output

Phase C (application track) produces entity files in the `application/` layer and related connections. All files follow the universal format in `framework/artifact-schemas/entity-conventions.md`.

### 3.1 Application Layer Entities — `architecture-repository/application/`

| Prefix | artifact-type | Directory | §content Required Sections |
|---|---|---|---|
| `APP-nnn` | `application-component` | `application/components/` | Name; Type (Service/Store/Gateway/UI/Integration); Responsibility (one sentence); Realises Capability (`CAP-nnn`); Safety-Relevant (true/false); Status (New/Existing/Modified/Retiring) |
| `AIF-nnn` | `application-interface` | `application/interfaces/` | Name; Exposed By (`APP-nnn`); Consumed By (`APP-nnn` or external); Protocol/Style (REST/gRPC/Event/Batch); Data Entities Involved (`DOB-nnn` list from DA); Safety-Relevant (true/false) |
| `ASV-nnn` | `application-service` | `application/services/` | Name; Description; Provided By (`APP-nnn`); Consumed By (actor or other `APP-nnn`); Realises (`BSV-nnn` from BA) |

**Component Types:**
- **Service** — encapsulates business logic or process execution
- **Store** — manages data persistence (logical; physical details in DA)
- **Gateway** — mediates access between external actors and internal components
- **UI** — user-facing presentation layer
- **Integration** — connects components or external systems (adapter, broker, event bus)

**Technology-independence constraint:** No `APP-nnn` entity may name a specific technology, product, language, or framework. Those belong in Phase D. An `APP-nnn` with `type: Store` says only *what is stored* and *who uses it*, not whether it is PostgreSQL or Redis.

### 3.2 `§display` Requirements

Every `APP-nnn` must have a `### archimate` subsection in `§display` so `regenerate_macros()` can include it in `_macros.puml`. `APP-nnn` entities that appear in sequence or activity diagrams must also have `### sequence` or `### activity` subsections respectively. `AIF-nnn` entities that appear in sequence diagrams need `### sequence` subsections.

---

## 4. Connections Produced

| Connection Type | Source → Target | Directory | Notes |
|---|---|---|---|
| `archimate-realization` | `APP-nnn` → `CAP-nnn` | `connections/archimate/realization/` | Component realises capability |
| `archimate-realization` | `ASV-nnn` → `BSV-nnn` | `connections/archimate/realization/` | App service realises business service |
| `archimate-serving` | `APP-nnn` → `APP-nnn` | `connections/archimate/serving/` | Component-to-component dependency |
| `archimate-serving` | `APP-nnn` → `ACT-nnn` | `connections/archimate/serving/` | Component serves actor |
| `archimate-access` | `APP-nnn` → `DOB-nnn` | `connections/archimate/access/` | Component reads/writes data object (DA must exist) |
| `archimate-composition` | `APP-nnn` → `APP-nnn` | `connections/archimate/composition/` | Structural containment (component owns sub-component) |

**Mutual reference with DA:** `archimate-access` connections reference `DOB-nnn` entities produced by the Data Architecture track. SA authors these connections once both AA and DA entity files exist; the connection file is stored in `architecture-repository/connections/archimate/access/`.

---

## 5. Overview Document

SA produces `architecture-repository/overview/aa-overview.md` as a **repository-content artifact** (frontmatter `artifact-type: aa-overview`).

Required sections:
- **Summary Header** — YAML frontmatter per `repository-conventions.md §7`:
  - `artifact-type: aa-overview`; `safety-relevant: true` (if any safety-relevant component); `csco-sign-off: required if safety-relevant components`
  - `summary:` 2–4 sentences covering component count, key interaction patterns, external integration boundaries
  - `key-decisions:` list; `open-issues:` list; `pending-clarifications:` list
- **Application/Business Function Matrix** — table mapping `BPR-nnn` × `APP-nnn` (● primary; ○ contributing; — none).
- **External Integration Catalog** — external systems not modelled as `APP-nnn` entities, with their interface type and data sensitivity.
- **Application-Level Gap Analysis** — per component: Baseline State / Target State / Gap / Resolution Approach.
- **Safety Constraint Overlay Cross-reference** — per `APP-nnn` with `safety-relevant: true`: reference to SCO Phase C section.

---

## 6. Quality Criteria

- [ ] Every `APP-nnn` realises at least one `CAP-nnn` or `BPR-nnn` (via realization connection or documented in `§content`).
- [ ] Every `AIF-nnn` in the interface list is referenced by at least one `archimate-serving` or `archimate-access` connection.
- [ ] All safety-relevant components are flagged `safety-relevant: true` and cross-referenced to the SCO.
- [ ] No specific technology, product, or language appears in any `APP-nnn` or `AIF-nnn` entity.
- [ ] External integration points are all catalogued as `AIF-nnn` entries with data sensitivity classification.
- [ ] CSCO sign-off present (`csco-sign-off: true` in `aa-overview.md`) if any safety-relevant component is defined.

---

## 7. Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-04-02 | Initial schema — monolithic artifact format |
| 2.0.0 | 2026-04-03 | Refactored to ERP v2.0 entity-file output; removed monolithic section model |

# Schema: Business Architecture (`BA`)

**Version:** 2.0.0
**ADM Phase:** B
**Owner:** Solution Architect
**Consumed by:** Application Architecture (AA), Data Architecture (DA), Safety Constraint Overlay (SCO update), Implementation Plan (IP)

---

## 1. Purpose

The Business Architecture elaborates the capability map introduced in the Architecture Vision into a detailed model of business capabilities, processes, value streams, and organisational structure. It establishes the functional and motivational entities that constrain all information systems and technology decisions in subsequent phases. It is the primary input to Phase C and to the CSCO's business-level safety constraint analysis.

Under ERP v2.0 the Business Architecture is **not a single file**. It is the set of entity and connection files produced in the architecture-repository during Phase B, each conforming to `framework/artifact-schemas/entity-conventions.md`. An overview document (`overview/ba-overview.md`) narrates the whole and provides the cross-phase handoff summary.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Architecture Vision (`AV`) | Solution Architect | Baselined |
| Requirements Register (`RR`) | Product Owner | Current iteration complete |
| Business Scenarios (detailed) | Product Owner | Draft acceptable |
| Safety Envelope Statement (from `AV`) | CSCO | Baselined (in AV) |

---

## 3. ERP Entity Output

Phase B produces entity files across three ArchiMate layers. All files follow the universal frontmatter and `§content`/`§display` structure in `framework/artifact-schemas/entity-conventions.md`.

### 3.1 Motivation Layer Entities — `architecture-repository/motivation/`

These entities carry over or are refined from Phase A. SA produces or updates them.

| Prefix | artifact-type | Directory | §content Required Sections |
|---|---|---|---|
| `STK-nnn` | `stakeholder` | `motivation/stakeholders/` | Name; Role (user/consumer/regulator/sponsor); Concerns; Influence; Safety Relevance |
| `DRV-nnn` | `driver` | `motivation/drivers/` | Name; Statement; Category (market/regulatory/technical/safety); Urgency |
| `GOL-nnn` | `goal` | `motivation/goals/` | Name; Statement; Stakeholder (`STK-nnn`); Realised By (`CAP-nnn`) |
| `OUT-nnn` | `outcome` | `motivation/outcomes/` | Name; Statement; Measurable Evidence (metric, target, source artifact); Related Goal (`GOL-nnn`) |
| `REQ-nnn` | `requirement` | `motivation/requirements/` | Name; Statement; Type (Functional/Non-Functional/Constraint/Safety); Source (`STK-nnn`/`DRV-nnn`) |
| `CST-nnn` | `constraint` | `motivation/constraints/` | Name; Statement; Type (Business/Regulatory/Technical/Safety); Imposed By |
| `PRI-nnn` | `principle` | `motivation/principles/` | Name; Statement; Rationale; Implications |

Every `REQ-nnn` produced in Phase A is reviewed for completeness before Phase B begins. New requirements uncovered in Phase B are added here.

### 3.2 Strategy Layer Entities — `architecture-repository/strategy/`

| Prefix | artifact-type | Directory | §content Required Sections |
|---|---|---|---|
| `CAP-nnn` | `capability` | `strategy/capabilities/` | Name; Description (what the business *has the ability to do*); Domain (Level-1 cluster); Strategic Classification (Core/Supporting/Commodity); Maturity Level (Current/Developing/Target); Gap (Yes/No); Traceable To (`DRV-nnn`) |
| `VS-nnn` | `value-stream` | `strategy/value-streams/` | Name; Triggering Stakeholder (`STK-nnn`); Value Delivered; Key Processes (ordered `BPR-nnn` list); Metrics |
| `COA-nnn` | `course-of-action` | `strategy/courses-of-action/` | Name; Strategic Approach; Realized Through (`CAP-nnn`); Outcome Target (`OUT-nnn`) |
| `VAL-nnn` | `value` | `motivation/values/` | Name; Stage Value Statement; Value Stream Stage Reference; Evidence Link (`OUT-nnn`) |

**Level 1 / Level 2 capability hierarchy:** Level-1 domains are modelled as `CAP-nnn` entries with `strategic-classification: domain`; Level-2 capabilities are `CAP-nnn` entries with a `parent-domain:` field naming the Level-1 domain. This is recorded in the entity's `§content` properties table; no separate index file is required.

**Traceability constraint:** Every `CAP-nnn` must reference at least one `DRV-nnn`. Capabilities without a traceable driver are either out-of-scope (remove) or signals of a missing driver (add `DRV-nnn` and note the AV revision).

### 3.3 Business Layer Entities — `architecture-repository/business/`

| Prefix | artifact-type | Directory | §content Required Sections |
|---|---|---|---|
| `ACT-nnn` | `business-actor` | `business/actors/` | Name; Type (Human/System/External); Description; Safety Relevance |
| `ROL-nnn` | `business-role` | `business/roles/` | Name; Description; Performed By (`ACT-nnn`) |
| `BPR-nnn` | `business-process` | `business/processes/` | Name; Owning Capability (`CAP-nnn`); Description; Triggering Event; Outcome; Safety-Relevant (Yes/No) |
| `BSV-nnn` | `business-service` | `business/services/` | Name; Provider (`ACT-nnn` or org unit); Consumer (`STK-nnn`); Realised By (`BPR-nnn`) |
| `BOB-nnn` | `business-object` | `business/objects/` | Name; Description; Owning Process (`BPR-nnn`); Classification (Public/Internal/Confidential/Restricted/Safety-Critical) |

**Safety-relevant process rule:** A process is `safety-relevant: true` if it directly controls a safety-relevant component, operates on Safety-Critical data, or is in a causal chain to a hazard category in AV §3.7. When in doubt: mark `true`. CSCO may downgrade; SA never downgrades unilaterally.

### 3.4 `§display` Requirements

Every `CAP-nnn` entity must have a `### archimate` subsection in `§display` (used by `regenerate_macros()` to build `_macros.puml`). `BPR-nnn` and `ACT-nnn` entities that appear in diagrams must also have `### archimate` subsections. `BPR-nnn` entities that appear in activity diagrams additionally need `### activity` subsections.

---

## 4. Connections Produced

Connection files are written to `architecture-repository/connections/` subdirectories. Each connection file follows `entity-conventions.md §2.2` (model-connection frontmatter + `§content` + optional `§display ###archimate`).

| Connection Type | Source → Target | Directory | Notes |
|---|---|---|---|
| `archimate-influence` | `DRV-nnn` → `GOL-nnn` | `connections/archimate/influence/` | Each goal must trace to a driver |
| `archimate-association` | `STK-nnn` → `GOL-nnn` | `connections/archimate/association/` | Stakeholder holds the goal |
| `archimate-realization` | `BPR-nnn` → `CAP-nnn` | `connections/archimate/realization/` | Process realises capability |
| `archimate-realization` | `BSV-nnn` → `CAP-nnn` | `connections/archimate/realization/` | Service realises capability |
| `archimate-realization` | `OUT-nnn` → `GOL-nnn` | `connections/archimate/realization/` | Outcome evidences goal achievement |
| `archimate-realization` | `CAP-nnn` → `COA-nnn` | `connections/archimate/realization/` | Capability operationalizes course of action |
| `archimate-assignment` | `ACT-nnn` → `BPR-nnn` | `connections/archimate/assignment/` | Actor performs process |
| `archimate-serving` | `BSV-nnn` → `STK-nnn` | `connections/archimate/serving/` | Service serves stakeholder |
| `archimate-triggering` | `BPR-nnn` → `BPR-nnn` | `connections/archimate/triggering/` | Process sequence within a value stream |
| `archimate-association` | `OUT-nnn` → `VAL-nnn` | `connections/archimate/association/` | Outcome evidence linked to delivered value |
| `archimate-association` | `VAL-nnn` → `VS-nnn` | `connections/archimate/association/` | Value tied to value-stream stage context |

---

## 5. Overview Document

SA produces `architecture-repository/overview/ba-overview.md` as a **repository-content artifact** (no `§display` section; frontmatter `artifact-type: ba-overview`). This is the primary cross-phase handoff summary.

Required sections:
- **Summary Header** — YAML frontmatter per `repository-conventions.md §7`:
  - `artifact-type: ba-overview`; `safety-relevant: true`; `csco-sign-off: true`
  - `summary:` 2–4 sentences describing capability clusters, safety-relevant process count, open gaps
  - `key-decisions:` list
  - `open-issues:` list
  - `pending-clarifications:` list
- **Business Function/Process Matrix** — table mapping `CAP-nnn` × `BPR-nnn` (● primary; ○ contributing; — none). Every capability must have at least one ● process.
- **Capability/Process CRUD Matrix** — which processes Create/Read/Update/Delete which business objects.
- **Gap Analysis** — table of capability gaps (Capability / Baseline State / Target State / Gap Type / Priority).
- **Safety Constraint Overlay Cross-reference** — `SCO` version incorporating Phase B analysis; per-process safety constraint references.

---

## 6. Quality Criteria

- [ ] Every `CAP-nnn` is traceable to at least one `DRV-nnn` from the Architecture Vision.
- [ ] Every in-scope `GOL-nnn` has at least one measurable `OUT-nnn` with evidence fields.
- [ ] Every in-scope `OUT-nnn` has at least one `COA-nnn` and at least one capability operationalization path.
- [ ] Every safety-relevant `BPR-nnn` is flagged `safety-relevant: true` and appears in the SCO Phase B update.
- [ ] All `VS-nnn` value streams are complete end-to-end (trigger `STK-nnn` → outcome → `CAP-nnn`).
- [ ] Value-stream stages have explicit delivered-value bindings (`VAL-nnn`) evidenced by outcomes.
- [ ] Motivation architecture traces: every `GOL-nnn` has an `archimate-influence` connection to a `DRV-nnn`.
- [ ] `ba-overview.md` summary header is complete and `csco-sign-off: true` is recorded after CSCO Phase B gate review.
- [ ] No entity file is referenced by a diagram alias that lacks a backing `§display ###archimate` subsection (enforced by `validate_diagram`).

---

## 7. Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-04-02 | Initial schema — monolithic artifact format |
| 2.0.0 | 2026-04-03 | Refactored to ERP v2.0 entity-file output; removed monolithic section model |

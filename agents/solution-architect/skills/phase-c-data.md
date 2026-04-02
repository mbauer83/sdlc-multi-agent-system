# Skill: Phase C — Data Architecture

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** C — Information Systems Architecture (Data sub-track)  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.4`, `framework/artifact-schemas/data-architecture.schema.md`, `raci-matrix.md §3.5`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Business Architecture (`BA`) | SA (self-produced, Phase B) | Baselined at version 1.0.0 | Hard prerequisite — DA cannot begin without baselined BA; data entities are derived from BA processes and value streams |
| Application Architecture (`AA`) | SA (self-produced, Phase C concurrent) | Draft (0.x.x) — mutual reference with DA | DA and AA are produced concurrently; DA entity IDs are referenced by AA Interface Catalog; AA component IDs are referenced by DA data flow diagrams |
| Requirements Register (`RR`) | Product Owner | Current (Phase C iteration) | SA reads RR for data-specific requirements: retention, sensitivity classification, sovereignty, regulatory obligations |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined | Identifies which data types or data operations are safety-relevant; sets initial Safety-Critical entity classification criteria |
| Architecture Principles Register (`PR`) | SA (self-produced, Phase A) | Version 0.1.0 or higher | Technology-independence principle is critical; data model must be technology-independent |
| `sprint.started` event | PM | Must be emitted for the Phase C Architecture Sprint | Hard prerequisite — same sprint as AA production |

---

## Knowledge Adequacy Check

### Required Knowledge

- Business processes and data operations from BA: every BPR-nnn entry is a source of data entity identification (what data the process creates, reads, updates, or deletes).
- Application component responsibilities from AA: `Store`-type components imply data entities; `Service`-type components imply data creation/mutation operations.
- Regulatory classification requirements: GDPR, HIPAA, PCI-DSS, financial regulations, etc. — the SA must know which regulations apply to identify PII, health data, financial data, and other protected categories. If the regulatory jurisdiction is unknown, a blocking CQ must be raised before data classification can be completed.
- Data retention obligations: retention periods are often legally mandated (e.g., financial records: 7 years; medical records: jurisdiction-specific). Without this knowledge, retention rules in §3.7 cannot be correctly specified.
- Cross-border data transfer constraints: where data will reside or transit affects data sovereignty requirements.

### Known Unknowns

| Unknown | Blocking | CQ Target | DA Section Affected |
|---|---|---|---|
| Data retention requirements (legally mandated periods for specific data categories) | Yes, for §3.7 (Governance Rules — retention rules) | User (for business policy) or CSCO (for regulatory mandates) | §3.7 |
| Data sovereignty constraints (jurisdictional restrictions on where data may be stored or processed) | Yes, for §3.6 (Classification Register — cross-border boundaries) and §3.7 | User | §3.6, §3.7 |
| PII categories present in the system (specific personal data categories under GDPR or equivalent) | Yes, for entity classification (§3.2) of Restricted entities | User or CSCO | §3.2, §3.6 |
| Health data classification requirements (jurisdiction-specific) | Yes, if health domain | User or CSCO | §3.2, §3.6, §3.7 |
| Existing data model (if migrating from a legacy system — baseline state) | Partially blocking for §3.8 (Gap Analysis); non-blocking for §3.2–§3.7 | User | §3.8 |
| Third-party data sharing obligations (contractual data sharing agreements with external parties) | Partially — can proceed; flag as assumption | User | §3.7 |

### Clarification Triggers

SA raises a CQ when:

1. **Unknown data retention requirements:** RR contains no retention constraints and the domain clearly has legally mandated retention periods (finance, health, legal, HR). Blocking CQ: "What data retention periods apply to [entity type]? Is there a data retention policy in effect?"
2. **Unknown regulatory environment for data:** The regulatory jurisdiction was not resolved in Phase A and data entities of type PII, health, or financial are identified. This is a blocking CQ — entity classification cannot be completed without it. Escalate to CSCO concurrently (CSCO may have jurisdiction information from SCO Phase B work).
3. **Unclear data sovereignty:** The system involves users or data in multiple jurisdictions and it is unknown whether cross-border data transfer applies. Blocking CQ for §3.6 trust boundary classification.
4. **Unknown safety-critical data:** A data entity appears to be involved in a safety-relevant process (from BA) but the SCO does not yet classify it. SA marks the entity as `Safety-Relevant: TBD` and raises a handoff to CSCO requesting classification. This is non-blocking for other entities.
5. **Ambiguous data ownership:** Two BA processes (owned by different ORG units) both appear to be the primary author of the same logical entity. SA raises a bounded CQ: "Is [entity] created by [Process A] or [Process B]? Or is one process creating a different version of the entity?"

---

## Procedure

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase C Architecture Sprint.
2. Confirm BA is at version 1.0.0 (baselined). If not, SA must halt — do not produce DA from a draft BA.
3. Confirm AA production has begun — at minimum, the Application Component Catalog (§3.2) draft must exist, as DA identifies data entities owned by APP-nnn components.
4. Read SCO Phase B update — identify any data entities pre-classified as Safety-Critical by CSCO.
5. Read RR current version — note all data-specific requirements (retention, sovereignty, classification, regulatory).

---

### Step 1 — Identify All Data Entities from BA Processes and AA Components

**Entity identification sources (check all):**

1. **BA Business Process Catalog (BPR-nnn):** Every process that creates, reads, updates, or deletes data implies at least one data entity. For each BPR-nnn, ask: "What data does this process operate on?" Add a DE-nnn for each identifiable entity.
2. **AA Application Component Catalog — Store-type components:** Each `Store` component manages a data entity group. Ensure a corresponding DE-nnn group exists for each Store.
3. **AA Interface Catalog (IFC-nnn):** Interfaces that carry data imply the data entities being carried. Identify all entities referenced in interface descriptions.
4. **BA Business Services Catalog (BSV-nnn):** Services that deliver data to stakeholders imply data entities delivered. Ensure those entities are in the catalog.
5. **RR Non-Functional Requirements:** Requirements referencing specific data types (e.g., "Customer PII must be encrypted at rest") identify entity classification requirements.

Produce an initial entity list before proceeding to Step 2. Each entity on the list gets a DE-nnn identifier at this stage — IDs are stable once assigned and cross-referenced in AA.

---

### Step 2 — Author Data Entity Catalog

Produce DA §3.2 with all DE-nnn entries.

Per-entity attributes (per schema §3.2):
- `Entity ID`: DE-nnn (sequential, engagement-unique; stable once assigned)
- `Name`: singular noun ("Customer", "Payment Transaction", "Audit Log Entry")
- `Description`: 1–2 sentences — what information this entity represents
- `Classification`: Public / Internal / Confidential / Restricted / Safety-Critical
- `Owning Application`: APP-nnn — the application component responsible for the authoritative copy of this entity
- `Retention`: policy reference (e.g., "7 years — financial record regulatory requirement") or "TBD — CQ pending"
- `Safety-Relevant`: Yes / No / TBD

**Classification guidance:**
- **Public:** Freely accessible data; no personal information.
- **Internal:** Organisational use only; operational data with no personal information.
- **Confidential:** Business-sensitive or personal data not reaching the Restricted threshold; role-based access required.
- **Restricted:** PII (under GDPR or equivalent), financial account data, health records, credentials, legally privileged data. Named-individual access; specific regulatory obligations apply.
- **Safety-Critical:** Data whose loss, corruption, or unauthorised modification could cause a safety constraint violation (from SCO). Examples: safety log records, control system state data, emergency shutdown signals.

When in doubt between classification levels: assign the higher classification. Downgrading requires explicit CSCO or legal sign-off.

---

### Step 3 — Author Logical Data Model

Produce DA §3.3: a Logical Data Model in ArchiMate **Information Structure Viewpoint** format.

Requirements (per schema §3.3):
- All DE-nnn entities from the Data Entity Catalog represented
- Relationships between entities typed: Association / Composition / Aggregation / Specialisation
- Cardinality on all relationships (1:1, 1:N, M:N)
- Key attributes listed per entity (not exhaustive — 3–7 key attributes that characterise the entity's identity and primary content; full attribute lists are detailed design, not architecture)

Rendered as structured text using ArchiMate notation described textually:
- Entity represented as: `[DE-nnn] EntityName: (key-attribute-1, key-attribute-2, ...)`
- Relationship represented as: `[DE-nnn] ── Relationship-Type ──> [DE-nnn] (cardinality)`

**Technology independence constraint (hard):** The logical data model describes entities and relationships — not tables, documents, columns, or database schemas. No database product names, file formats, storage mechanisms, or persistence specifics appear here. Those belong in Phase D.

---

### Step 4 — Build Data/Business Function Matrix (CRUD)

Produce DA §3.4: a CRUD matrix showing which business processes (BPR-nnn) create, read, update, or delete which data entities (DE-nnn).

Matrix notation:
- **C** = Create (process produces a new instance of this entity)
- **R** = Read (process reads but does not modify)
- **U** = Update (process modifies an existing entity instance)
- **D** = Delete or Archive (process removes or retires an entity instance)
- Combinations: CR, RU, CRUD, etc.
- **—** = no relationship

Validation rules:
- Every DE-nnn must have at least one **C** operation. An entity with no Creator is either imported from an external system (note the external source in the entity description) or is orphaned (flag as a DA gap).
- An entity classified as `Safety-Critical` that is Created by a non-safety-relevant process (BPR `Safety-Relevant: No`) is a potential inconsistency — flag to CSCO for review.
- An entity classified as `Restricted` that is Read by more than 5 distinct processes should trigger a review comment: "Wide read access to Restricted entity — governance rule required in §3.7."

---

### Step 5 — Author Data Flow Diagrams

Produce one Data Flow Diagram per major value stream (VS-nnn from BA).

Per diagram requirements (per schema §3.5):
- All DE-nnn entities involved in cross-component flows within this value stream
- Direction of each flow (which component is source, which is destination)
- Transformation or processing that occurs in transit (if any — e.g., "anonymisation applied before export")
- **Trust boundaries explicitly marked:** where data moves from an internal component to an external system, from a lower-classification zone to a higher-classification zone, or across a network boundary that carries regulatory significance

Trust boundary types to mark:
- Internal-to-External: data leaving the internal network boundary to external actors or systems
- Classification boundary: data crossing from a lower to a higher classification zone (e.g., Public data enriched with Restricted data)
- Regulatory boundary: data crossing a jurisdiction boundary (e.g., EU→US data transfer)

Rendered as structured text: list each flow step, the entity flowing, the source and destination component, the trust boundary crossed (if any), and the transformation applied.

---

### Step 6 — Author Data Classification Register

Produce DA §3.6: a register of all data sensitivity boundaries identified in the data flow diagrams.

For each boundary (DB-nnn):
- `Boundary ID`: DB-nnn
- `Type`: Internal/External / Classification-crossing / Regulatory
- `Data Crossing Boundary`: DE-nnn list
- `Classification`: classification of the data crossing (use the highest classification among the crossing entities)
- `Protection Requirement`: Encryption / Anonymisation / Access control / Audit log / Consent record / Legal basis / (combinations)

Every trust boundary marked in the Data Flow Diagrams (Step 5) must have a corresponding DB-nnn entry in this register. A boundary in a diagram without a register entry is an incomplete DA.

---

### Step 7 — Author Data Governance Rules

Produce DA §3.7: a catalog of data governance rules.

Required minimum rules (per schema §3.7):
1. **Retention rules** — one rule per entity classification level (and per specific entity if regulatory mandate differs from the classification default). Must specify: entities in scope, retention period, deletion/archiving obligation, and enforcement point.
2. **Access control rules** — one rule per entity classification level of `Confidential` and above. Must specify: who may access (role level, not individual name), under what conditions, and how access is controlled (enforcement point).
3. **Audit logging rules** — for every entity classified `Safety-Critical` or `Restricted`. Must specify: which operations are logged (C/R/U/D), log retention period, and who has access to the logs.
4. **Cross-border or regulatory transfer rules** — if any DB-nnn boundary is of type `Regulatory`. Must specify: the applicable regulation, the transfer mechanism (adequacy decision, contractual clauses, consent, etc.), and the enforcement point.

If a required rule cannot be specified because a CQ is open (e.g., retention period unknown): write the rule structure with `[TBD — CQ: CQ-id pending]` in the specific field. The rule must be present; only the detail is TBD.

---

### Step 8 — Author Data-Level Gap Analysis

Produce DA §3.8:

For each entity or entity domain:
- `Entity / Domain`: DE-nnn or a domain group name
- `Baseline State`: current state of this entity/domain (e.g., "Stored in legacy CRM — CSV export format" or "Does not exist — greenfield")
- `Target State`: the target state per this DA
- `Gap`: New (entity must be created) / Modified (entity exists but structure must change) / Deprecated (entity must be retired)
- `Resolution`: Migrate / Cleanse / Create / Retire

For a greenfield engagement: Baseline State = "Not applicable — greenfield". Gap = New for all entities.

For an EP-G engagement where the existing data model is known: Baseline State = description of existing model; Gap = what must change.

---

### Step 9 — Cross-Reference SCO Phase C Data Update; Flag Safety-Critical Entities

Before baselining DA:

1. For every DE-nnn marked `Safety-Relevant: Yes` or `Safety-Critical`, confirm a handoff to CSCO has been created requesting Phase C Data SCO update.
2. Once CSCO produces the Phase C Data SCO update: read it. For each safety constraint that applies to a DE-nnn, update DA §3.9 (SCO cross-reference table):

| Entity ID | Safety Constraint Reference (SCO section) |
|---|---|
| DE-nnn | SCO §n.n |

3. Any entity still marked `Safety-Relevant: TBD` must be resolved before baseline. Raise a blocking handoff to CSCO if any TBD entries remain.
4. Cross-check: every entity classified `Safety-Critical` must appear in the DA §3.9 SCO cross-reference table. An entity classified Safety-Critical with no SCO cross-reference is an incomplete DA and a potential ALG-001 condition.

---

### Step 10 — Coordinate with AA for Mutual Reference Resolution

Before baselineing either DA or AA, resolve all mutual reference placeholders:

1. SA (wearing "DA author" hat): confirm that every DE-nnn referenced in AA Interface Catalog entries has a corresponding entry in the DA Entity Catalog.
2. SA (wearing "AA author" hat): confirm that every `[DA-entity-TBD]` placeholder in the AA Interface Catalog has been replaced with a DE-nnn ID.
3. Confirm: every `Store`-type APP-nnn component in the AA has a clear owning entity group in the DA Entity Catalog (`Owning Application: APP-nnn`).
4. Confirm: the safety-relevance classification is consistent between AA and DA — if IFC-nnn is `Safety-Relevant: Yes`, the DE-nnn entities it carries should also be `Safety-Relevant: Yes` (or Safety-Critical). Flag any inconsistency to CSCO.

---

### Step 11 — Baseline DA and Cast Phase C Gate Vote (Combined)

1. Assemble all sections into `architecture-repository/data-architecture/da-1.0.0.md`.
2. Complete summary header:
   - `artifact-type: data-architecture`
   - `safety-relevant: true` if any DE-nnn is Safety-Relevant or Safety-Critical
   - `csco-sign-off: true` only if safety-relevant entities are defined AND CSCO has signed off
   - `pending-clarifications: [list open CQ-ids]`
3. Emit `artifact.baselined` for DA at version 1.0.0.
4. Create handoff to SwA: `handoff-type: phase-D-input` — DA is a secondary input to Technology Architecture (alongside AA). Include: Data Entity Catalog, Logical Data Model, Data Classification Register.
5. Create handoff to PM: both AA and DA are now baselined; Phase C gate may proceed.

**Cast Phase C gate vote (C→D) — ONLY after BOTH AA and DA are at version 1.0.0:**

Emit `gate.vote_cast`:
```
gate_id: gate-C-D
phase_from: C
phase_to: D
result: approved | veto
rationale: [if veto: specific deficiency; if approved: confirmation that both AA and DA meet schema quality criteria]
```

**SA self-checklist for Phase C gate vote (combined AA + DA):**
- [ ] Every DE-nnn is traceable to at least one BPR-nnn in the BA
- [ ] Every DE-nnn has a classification and a retention rule (or `[TBD — CQ: id]` with PM acceptance)
- [ ] All Safety-Critical entities are cross-referenced to the SCO (§3.9)
- [ ] Data flows across all trust boundaries are documented in DFDs
- [ ] DA is technology-independent — no database products, file formats, or storage mechanisms specified
- [ ] CRUD matrix covers all in-scope BPR-nnn and DE-nnn
- [ ] All `[AA-component-TBD]` mutual reference placeholders in DA are resolved
- [ ] All `[DA-entity-TBD]` mutual reference placeholders in AA are resolved
- [ ] CSCO sign-off present if Safety-Critical entities are defined
- [ ] `pending-clarifications` is empty or all items are `assumption`-flagged with PM acceptance
- [ ] AA is at version 1.0.0 (this gate vote covers both artifacts)

---

## Feedback Loop

### CSCO Safety Review Loop (Data-Level)

- **Iteration 1:** SA sends handoff of Safety-Relevant and Safety-Critical DE-nnn entries to CSCO. CSCO reviews; may add new Safety-Critical classifications or add data-level safety constraints.
- **Iteration 2:** SA updates affected entity entries; CSCO confirms Phase C Data SCO update.
- **Termination:** CSCO signs off; `csco-sign-off: true` in DA header.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` if unresolved after 2 iterations. PM adjudicates. Do not baseline DA without CSCO sign-off on safety-relevant data entities.

### SwA Feedback Loop (DA→TA Handoff Completeness)

After DA is baselined and handed off to SwA for Phase D:

- **Iteration 1:** SwA may return structured feedback on the DA handoff — specifically: entity classification constraints that conflict with the target storage technology, or missing data relationships required for TA schema design.
- **Iteration 2:** SA addresses feedback; resubmits DA at incremented version (1.0.1); creates a new handoff event.
- **Termination:** SwA acknowledges revised DA; proceeds with TA.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` if unresolved. PM adjudicates: if SwA's constraint is technology-domain, SwA's position governs (but the AA/DA must still record the logical requirement). If SwA's constraint would require a change to the logical data model (e.g., merging entities for performance), this is an architecture-layer decision and SA's position governs.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | A data entity or data flow is identified that would violate a safety constraint in the SCO Phase B baseline (e.g., Safety-Critical data transmitted without audit logging across a trust boundary) | S1 | Halt production of the violating data flow specification; emit `alg.raised`; notify CSCO immediately and PM concurrently; do not include the violating flow in DFDs until resolved |
| ALG-003 | During entity classification, SA identifies that the system must handle data subject to a regulatory obligation (GDPR, HIPAA, PCI-DSS, etc.) that was not identified in Phase A and for which no compliance framework is in place | S1 | Emit `alg.raised`; notify CSCO immediately and PM concurrently; halt classification of the affected entity type until CSCO assesses |
| ALG-008 | SA detects that the DA draft (0.x.x) has been consumed by SwA as an authoritative input before Phase C gate | S2 | Emit `alg.raised`; notify PM; PM invalidates consuming artifact sections; SwA must wait for DA 1.0.0 |
| ALG-010 | The two-iteration CSCO safety review loop on Phase C Data entities has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; do not baseline DA |
| ALG-010 | The two-iteration SwA feedback loop on DA→TA handoff has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Data Architecture (`DA`) | `architecture-repository/data-architecture/da-<version>.md` | 1.0.0 at Phase C gate | `artifact.baselined` |
| Handoff to SwA (DA → Phase D input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (Phase C data safety review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase C gate vote (combined AA+DA) | EventStore | — | `gate.vote_cast` (emitted only when both AA and DA are at 1.0.0) |

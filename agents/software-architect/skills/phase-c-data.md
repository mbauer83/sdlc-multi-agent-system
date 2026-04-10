---
skill-id: SwA-PHASE-C-DATA
agent: SwA
name: phase-c-data
display-name: Phase C — Data Architecture
invoke-when: >
  Phase B gate has passed and the Phase C Architecture Sprint starts; SA has baselined
  the Business Architecture (BA) at 1.0.0 and the BA handoff has been acknowledged.
  Produces the Data Architecture (DA) concurrently with the Application Architecture
  (AA sub-track, SwA-PHASE-C-APP).
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [C]
trigger-conditions:
  - gate.evaluated (from_phase=B, result=passed)
  - sprint.started (phase=C)
  - handoff.created from SA (artifact-type=business-architecture, handoff-type=phase-C-input)
entry-points: [EP-0, EP-A, EP-B, EP-C]
primary-outputs: [Data Architecture, Data Entity Catalog, Logical Data Model, Data Classification Register]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase C — Data Architecture

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** C — Information Systems Architecture (Data sub-track)  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.4`, `framework/artifact-schemas/data-architecture.schema.md`, `raci-matrix.md §3.5`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Runtime Tooling Hint

Diagram and matrix conventions apply only when this skill explicitly produces or updates diagram artifacts; use `framework/diagram-conventions.md` as the source of truth.

Tool-use statements here are intent-level guidance. Concrete tool signatures are runtime-bound.

- Discovery/query/search/filter: `model_query_*` family.
- Validation: `model_verify_file`, `model_verify_all`.
- Deterministic creation/update of entities, connections, and diagrams: `model_create_entity`, `model_create_connection`, `model_create_diagram`, `model_create_matrix` (use `dry_run` first).
- `invoke-when` and `trigger-conditions` are intent hints; runtime gating and phase-state enforcement belong to orchestration code.
- Preserve strict output and validation procedure; out-of-profile invocations should stop at pre-condition checks and escalate via CQ/algedonic flow.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Business Architecture (`BA`) | Solution Architect | Baselined at version 1.0.0 | Hard prerequisite — DA cannot begin without baselined BA; data entities are derived from BA processes (BPR-nnn), business objects (BOB-nnn), and value streams (VS-nnn) |
| Application Architecture (`AA`) | SwA (self-produced, Phase C concurrent) | Draft (0.x.x) — mutual reference with DA | DA and AA are produced concurrently; DOB-nnn entity IDs are referenced by AA Interface Catalog; APP-nnn component IDs are referenced by DA entity ownership |
| Requirements Register (`RR`) | Product Owner | Current (Phase C iteration) | SwA reads RR for data-specific requirements: retention, sensitivity classification, sovereignty, regulatory obligations |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined | Identifies which data types or operations are safety-relevant; sets initial Safety-Critical entity classification criteria |
| Architecture Principles Register (`PR`) | Solution Architect | Version 0.1.0 or higher | Technology-independence principle is critical; data model must be technology-independent |
| `sprint.started` event | PM | Must be emitted for the Phase C Architecture Sprint | Hard prerequisite — same sprint as AA production |

---

## Knowledge Adequacy Check

### Required Knowledge

- Business objects (BOB-nnn) from BA: every BOB-nnn is a direct source of a DOB-nnn; understanding the BA's business object model prevents phantom data entities.
- Business processes and data operations from BA: every BPR-nnn that creates, reads, updates, or deletes data implies at least one DOB-nnn. The CRUD matrix must cover all BPR-nnn.
- Application component responsibilities from AA: `Store`-type APP-nnn components imply DOB-nnn groups; `Service`-type components imply DOB-nnn mutation operations.
- Regulatory classification requirements: GDPR, HIPAA, PCI-DSS, financial regulations — SwA must know which apply to classify PII, health data, financial data correctly. If jurisdiction is unknown, a blocking CQ must be raised.
- Data retention obligations: legally mandated periods. Without this, governance rules cannot be correctly specified.
- Cross-border data transfer constraints: affects data sovereignty requirements.

### Known Unknowns

| Unknown | Blocking | CQ Target | DA Section Affected |
|---|---|---|---|
| Data retention requirements (legally mandated periods for specific categories) | Yes, for Data Governance Rules (retention rules) | User (policy) or CSCO (regulatory) | Governance Rules |
| Data sovereignty constraints (jurisdictional restrictions) | Yes, for Data Classification Register (cross-border boundaries) | User | Classification Register, Governance Rules |
| PII categories present in the system (specific categories under GDPR or equivalent) | Yes, for entity classification of Restricted entities | User or CSCO | Entity Catalog, Classification Register |
| Health data classification requirements (jurisdiction-specific) | Yes, if health domain | User or CSCO | Entity Catalog, Classification Register, Governance Rules |
| Existing data model (if migrating from a legacy system) | Partially blocking for Gap Analysis; non-blocking for entity catalog | User | Gap Analysis |
| Third-party data sharing obligations | Partially — can proceed; flag as assumption | User | Governance Rules |

### Clarification Triggers

SwA raises a CQ when:

1. **Unknown data retention requirements:** RR contains no retention constraints and domain has legally mandated periods. Blocking CQ: "What data retention periods apply to [entity type]?"
2. **Unknown regulatory environment:** Regulatory jurisdiction was not resolved in Phase A and PII, health, or financial data entities are identified. Blocking CQ — classify to CSCO concurrently.
3. **Unclear data sovereignty:** System involves users or data in multiple jurisdictions with unknown cross-border transfer applicability.
4. **Unknown safety-critical data:** A data entity appears involved in a safety-relevant process (from BA) but SCO does not classify it. Non-blocking — mark entity as `Safety-Relevant: TBD`; raise handoff to CSCO.
5. **Ambiguous data ownership:** Two BA processes owned by different ORG units both appear to be primary author of the same entity. Bounded CQ to PO.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="C", artifact_type="data-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="C")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase C Architecture Sprint.
2. Confirm BA handoff from SA has been received and BA is at version 1.0.0. If not: halt — do not produce DA from a draft BA.
3. Confirm AA production has begun — at minimum, the Application Component Catalog draft must exist, as DOB-nnn entities will reference APP-nnn `Store`-type components.
4. Read SCO Phase B update — identify any data entities pre-classified as Safety-Critical by CSCO.
5. Read RR current version — note all data-specific requirements.

---

### Step 1 — Identify All Data Entities from BA Objects and Processes

**Entity identification sources (check all):**

1. **BA Business Objects Catalog (BOB-nnn):** Each BOB-nnn maps directly to one or more DOB-nnn entities. A BOB represents a business-domain concept; a DOB is the information system representation of that concept.
2. **BA Business Process Catalog (BPR-nnn):** Every process that creates, reads, updates, or deletes data implies at least one data entity. For each BPR-nnn: "What information does this process operate on?"
3. **AA Application Component Catalog — Store-type components:** Each `Store` APP-nnn manages a data entity group. Ensure a corresponding DOB-nnn group exists.
4. **AA Interface Catalog (IFC-nnn):** Interfaces that carry data imply the entities being carried.
5. **BA Business Services Catalog (BSV-nnn):** Services that deliver data to stakeholders imply entities delivered.
6. **RR Non-Functional Requirements:** Requirements referencing specific data types identify classification requirements.

Produce an initial entity list before proceeding. Each entity gets a DOB-nnn identifier at this stage — IDs are stable once assigned and cross-referenced in AA.

Write each DOB-nnn as an ERP-compliant entity file at `architecture-repository/model-entities/application/data-objects/DOB-nnn.md`.

---

### Step 2 — Author Data Entity Catalog and ER Diagram

Per-entity attributes (per schema §3.2):
- `entity-id`: DOB-nnn (sequential, engagement-unique; stable once assigned)
- `name`: singular noun ("Customer", "Payment Transaction", "Audit Log Entry")
- `entity-type`: DataObject
- `description`: 1–2 sentences — what information this entity represents
- `classification`: Public / Internal / Confidential / Restricted / Safety-Critical
- `owning-application`: APP-nnn — the application component responsible for the authoritative copy
- `retention`: policy reference or "TBD — CQ pending"
- `safety-relevant`: Yes / No / TBD

**Classification guidance:**
- **Public:** Freely accessible; no personal information.
- **Internal:** Operational data; no personal information; organisational use only.
- **Confidential:** Business-sensitive or personal data not reaching Restricted; role-based access required.
- **Restricted:** PII (GDPR or equivalent), financial account data, health records, credentials, legally privileged data.
- **Safety-Critical:** Data whose loss, corruption, or unauthorised modification could cause a safety constraint violation (from SCO).

When in doubt between classification levels: assign the higher classification. Downgrading requires explicit CSCO or legal sign-off.

**Diagram Step D — Class/ER Diagram (Canonical Data Model)**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="data-object")` to retrieve all DOB-nnn entities. Call `list_connections(artifact_type="er-one-to-many")` and related ER connection types to identify existing cardinality relationships.
- **D2:** For each DOB-nnn appearing in the diagram, verify its `§display ###er` subsection exists. Add missing subsections via `write_artifact`; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.class-er")`. Call `generate_er_content(entity_ids)` and `generate_er_relations(connection_ids)` to produce PUML class blocks and cardinality lines. Write to `architecture-repository/diagram-catalog/diagrams/c-er-canonical-data-model-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate.

---

### Step 3 — Author Logical Data Model

Produce DA §3.3: a Logical Data Model in ArchiMate **Information Structure Viewpoint** format.

Requirements (per schema §3.3):
- All DOB-nnn entities represented
- Relationships typed: Association / Composition / Aggregation / Specialisation
- Cardinality on all relationships (1:1, 1:N, M:N)
- Key attributes listed per entity (3–7 key attributes — not exhaustive; full attribute lists are detailed design)

**Technology independence constraint (hard):** The logical data model describes entities and relationships — not tables, columns, documents, or storage schemas. No database product names, file formats, or storage mechanisms.

---

### Step 4 — Build Data/Business Function Matrix (CRUD)

Produce DA §3.4: CRUD matrix — BPR-nnn (rows) × DOB-nnn (columns):

Authoring method:
- Create the CRUD matrix as a matrix artifact via `model_create_matrix` in `diagram-catalog/diagrams/*.md`.
- Keep BPR/DOB IDs in the canonical row/column definitions; use auto-linking for readable, navigable cells.
- Reserve PUML diagrams for data-flow topology; keep CRUD coverage in matrix form.

- **C** = Create; **R** = Read; **U** = Update; **D** = Delete or Archive; combinations (CR, RU, CRUD); **—** = no relationship

Validation rules:
- Every DOB-nnn must have at least one **C** operation. An entity with no Creator is either imported from an external system (note the source) or is orphaned (flag as DA gap).
- An entity classified Safety-Critical Created by a non-safety-relevant process: flag to CSCO for review.
- An entity classified Restricted Read by more than 5 distinct processes: add a governance review comment in §3.7.

---

### Step 5 — Author Data Flow Diagrams

Produce one Data Flow Diagram per major value stream (VS-nnn from BA).

Per diagram requirements (per schema §3.5):
- All DOB-nnn entities involved in cross-component flows within this value stream
- Direction of each flow (source component, destination component)
- Transformation or processing in transit (anonymisation, aggregation, etc.)
- **Trust boundaries explicitly marked:** Internal-to-External, Classification boundary (lower→higher classification zone), Regulatory boundary (jurisdiction crossing)

---

### Step 6 — Author Data Classification Register

Produce DA §3.6: register of all data sensitivity boundaries from the data flow diagrams.

For each boundary (DB-nnn):
- `Boundary ID`: DB-nnn
- `Type`: Internal/External / Classification-crossing / Regulatory
- `Data Crossing Boundary`: DOB-nnn list
- `Classification`: highest classification among crossing entities
- `Protection Requirement`: Encryption / Anonymisation / Access control / Audit log / Consent record / Legal basis / combinations

Every trust boundary in the Data Flow Diagrams must have a corresponding DB-nnn entry.

---

### Step 7 — Author Data Governance Rules

Produce DA §3.7: catalog of data governance rules.

Required minimum rules:
1. **Retention rules** — one rule per entity classification level (and per specific entity if regulatory mandate differs).
2. **Access control rules** — for every entity classified Confidential and above: who may access, under what conditions, enforcement point.
3. **Audit logging rules** — for Safety-Critical and Restricted entities: which operations are logged, log retention period, who has access.
4. **Cross-border transfer rules** — if any DB-nnn boundary is of type Regulatory.

If a required rule cannot be specified because a CQ is open: write the rule structure with `[TBD — CQ: CQ-id pending]`.

---

### Step 8 — Author Data-Level Gap Analysis

Produce DA §3.8:

For each entity or entity domain:
- `Baseline State`: current state or "Not applicable — greenfield"
- `Target State`: the target state per this DA
- `Gap`: New / Modified / Deprecated
- `Resolution`: Migrate / Cleanse / Create / Retire

---

### Step 9 — Cross-Reference SCO Phase C Data Update; Flag Safety-Critical Entities

Before baselining DA:

1. For every DOB-nnn marked `Safety-Relevant: Yes` or `Safety-Critical`: confirm handoff to CSCO has been created requesting Phase C Data SCO update.
2. Once CSCO produces Phase C Data SCO update: read it. Update each entity file's safety cross-reference in `§content`.
3. Any entity still marked `Safety-Relevant: TBD` must be resolved before baseline. Raise a blocking handoff to CSCO if any TBD entries remain.
4. Cross-check: every entity classified Safety-Critical must have an SCO cross-reference. An entity classified Safety-Critical with no SCO reference is an incomplete DA and a potential ALG-001 condition.

---

### Step 10 — Coordinate with AA for Mutual Reference Resolution

Before baselining either DA or AA, resolve all mutual reference placeholders:

1. Confirm every DOB-nnn referenced in AA Interface Catalog (IFC-nnn `data-entities-involved`) has a corresponding entry in the DA entity catalog.
2. Confirm every `[DA-entity-TBD]` placeholder in AA has been replaced with a DOB-nnn ID.
3. Confirm every `Store`-type APP-nnn in AA has a clear owning entity group in DA (`owning-application: APP-nnn`).
4. Confirm safety-relevance classification consistency: if IFC-nnn is `Safety-Relevant: Yes`, the DOB-nnn entities it carries should also be `Safety-Relevant: Yes` or Safety-Critical. Flag any inconsistency to CSCO.

---

### Step 11 — Send to SA for Traceability Review

Before baselining DA at 1.0.0:

1. Emit `handoff.created` to SA: `handoff-type=phase-C-sa-traceability-review`, `artifact-type=data-architecture`, including draft DA path.
2. Await SA's structured traceability feedback (SA-PHASE-C-DATA-REVIEW skill). SA has up to 2 review iterations.
3. Address all material findings (D1 phantom entities, D3 technology-independence violations, D4 no-creator gaps).
4. Once SA emits consulting acknowledgement for DA: proceed to Step 12.

---

### Step 12 — Baseline DA and Cast Phase C Gate Vote (Combined)

1. Write all DOB-nnn entity files to `architecture-repository/model-entities/application/data-objects/` at version 1.0.0 via `write_artifact`.
2. Write ER connection files to `architecture-repository/connections/er/`.
3. Write `architecture-repository/overview/da-overview.md`.
4. Emit `artifact.baselined` for DA at version 1.0.0.
5. Create handoff to PM: both AA and DA are now baselined; Phase C gate may proceed.

**Cast Phase C gate vote (C→D) — ONLY after BOTH AA and DA are at version 1.0.0:**

Emit `gate.vote_cast`:
```
gate_id: gate-C-D
phase_from: C
phase_to: D
result: approved | veto
rationale: [if veto: specific deficiency; if approved: confirmation that both AA and DA meet schema quality criteria and SA consulting acknowledgements are on record]
```

**SwA self-checklist for Phase C gate vote (combined AA + DA):**
- [ ] Every DOB-nnn is traceable to at least one BPR-nnn or BOB-nnn in the BA
- [ ] Every DOB-nnn has a classification and a retention rule (or `[TBD — CQ: id]` with PM acceptance)
- [ ] All Safety-Critical entities are cross-referenced to SCO
- [ ] Data flows across all trust boundaries are documented in DFDs
- [ ] DA is technology-independent — no database products, file formats, or storage mechanisms
- [ ] CRUD matrix covers all in-scope BPR-nnn and DOB-nnn
- [ ] All `[AA-component-TBD]` mutual reference placeholders in DA are resolved
- [ ] All `[DA-entity-TBD]` mutual reference placeholders in AA are resolved
- [ ] CSCO Phase C Data SCO update received; all TBD safety flags resolved
- [ ] SA Consulting Acknowledgement received (SA-PHASE-C-DATA-REVIEW completed)
- [ ] AA is at version 1.0.0 (this gate vote covers both artifacts)

---


## Common Rationalizations (Rejected)

| Rationalization | Rejection |
|---|---|
<!-- TODO: add 2-3 skill-specific rationalization rows -->
| "I can skip discovery because I already know the context from prior sessions" | Discovery is mandatory per Step 0; any skip must be recorded as a PM-accepted assumption with a risk flag; silent assumptions are governance violations |
| "A CQ with a reasonable assumed answer is equivalent to waiting — I'll proceed with the assumption" | Assumed answers must be explicitly recorded in the artifact with a risk flag; they never silently replace CQ answers |

## Feedback Loop

### SA Traceability Review Loop

- **Iteration 1:** SwA sends DA draft to SA. SA reviews for BA object/process traceability. SA provides structured feedback.
- **Iteration 2:** SwA addresses findings; resends revised DA.
- **Termination:** SA emits consulting acknowledgement. SwA proceeds to baseline.
- **Max iterations:** 2.
- **Escalation:** `ALG-010` to PM if material D1/D3/D4 findings remain after round 2.

### CSCO Safety Review Loop (Data-Level)

- **Iteration 1:** SwA sends handoff of Safety-Relevant and Safety-Critical DOB-nnn entries to CSCO. CSCO reviews; may add Safety-Critical classifications or data-level safety constraints.
- **Iteration 2:** SwA updates affected entity entries; CSCO confirms Phase C Data SCO update.
- **Termination:** CSCO signs off.
- **Max iterations:** 2.
- **Escalation:** `ALG-010` if unresolved; PM adjudicates. Do not baseline DA without CSCO sign-off on safety-relevant data entities.

### Personality-Aware Conflict Engagement

SA brings business-domain authority on data entity derivation (D1 phantom entities, D4 creator gaps); SwA brings implementation depth on data model structure. When SA identifies a D1 finding (phantom entity), SwA's obligation is to provide the BA anchor — either by identifying the correct BOB-nnn/BPR-nnn or by raising a BA gap CQ to SA. When CSCO raises Safety-Critical classification requirements, SwA applies them without negotiation and documents the consequence in entity metadata and governance rules.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | SA round-2 feedback requires structural revision | S2 |
| `gate-veto` | Phase C gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from BA or existing SCO | S2 |

On trigger: call `record_learning()` with `artifact-type="data-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total).

---


## Red Flags

Pre-escalation observable indicators. Raise an algedonic signal or CQ if two or
more of these are true simultaneously:

<!-- TODO: add 5-7 role-specific observable indicators for this skill -->
- Outputs section of the primary artifact is blank after completing the procedure
- Any required input artifact is missing and no CQ has been raised
- Feedback loop iteration count has reached the maximum with no resolution

## Algedonic Triggers <!-- workflow -->

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | A data entity or data flow would violate a safety constraint in SCO Phase B (e.g., Safety-Critical data transmitted without audit logging across a trust boundary) | S1 | Halt production of violating data flow specification; emit `alg.raised`; notify CSCO immediately and PM concurrently |
| ALG-003 | During entity classification, SwA identifies that the system must handle data subject to a regulatory obligation (GDPR, HIPAA, PCI-DSS) not identified in Phase A and for which no compliance framework is in place | S1 | Emit `alg.raised`; notify CSCO immediately and PM concurrently; halt classification of affected entity type until CSCO assesses |
| ALG-008 | SwA detects that the DA draft (0.x.x) has been consumed by another agent as authoritative input before Phase C gate | S2 | Emit `alg.raised`; notify PM |
| ALG-010 | Two-iteration SA traceability review loop exhausted with material findings unresolved | S3 | Emit `alg.raised`; PM adjudicates |
| ALG-010 | Two-iteration CSCO safety review loop on Phase C Data entities exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; do not baseline DA |

---


## Verification

Before emitting the completion event for this skill, confirm:

<!-- TODO: extend with skill-specific checklist items -->
- [ ] All blocking CQs resolved or documented as PM-accepted assumptions
- [ ] Primary output artifact exists at the required minimum version
- [ ] CSCO sign-off recorded where required (`csco-sign-off: true`)
- [ ] All required EventStore events emitted in this invocation
- [ ] Handoffs to downstream agents created
- [ ] Learning entries recorded if a §3.1 trigger was met this invocation
- [ ] Memento state saved (End-of-Skill Memory Close)

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Data Object entities (DOB-nnn) | `architecture-repository/model-entities/application/data-objects/` | 1.0.0 at Phase C gate | `artifact.baselined` per entity |
| ER connection files | `architecture-repository/connections/er/` | — | `artifact.created` |
| DA Overview | `architecture-repository/overview/da-overview.md` | — | `artifact.created` |
| Canonical Data Model ER diagram | `architecture-repository/diagram-catalog/diagrams/c-er-canonical-data-model-v1.puml` | — | `artifact.created` |
| Handoff to SA (DA draft for traceability review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (Phase C data safety review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase C gate vote (combined AA+DA) | EventStore | — | `gate.vote_cast` (emitted only when both AA and DA are at 1.0.0) |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="C", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

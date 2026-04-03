---
skill-id: SA-PHASE-C-APP
agent: SA
name: phase-c-application
display-name: Phase C — Application Architecture
invoke-when: >
  Phase B gate has passed and the Phase C Architecture Sprint starts; produces the Application
  Architecture (AA) concurrently with the Data Architecture (DA sub-track).
trigger-phases: [C]
trigger-conditions:
  - gate.evaluated (from_phase=B, result=passed)
  - sprint.started (phase=C)
  - artifact.baselined (artifact-type=business-architecture, version=1.0.0)
entry-points: [EP-0, EP-A, EP-B, EP-C]
primary-outputs: [Application Architecture, Interface Catalog, Application Interaction Diagrams]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase C — Application Architecture

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** C — Information Systems Architecture (Application sub-track)  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.4`, `framework/artifact-schemas/application-architecture.schema.md`, `raci-matrix.md §3.4`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Business Architecture (`BA`) | SA (self-produced, Phase B) | Baselined at version 1.0.0 | Hard prerequisite — AA cannot begin without baselined BA |
| Requirements Register (`RR`) | Product Owner | Current (Phase C iteration) | SA reads RR for non-functional requirements and interface constraints |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined | SA cross-references safety-relevant components against SCO Phase B constraints |
| Data Architecture (`DA`) — draft | SA (self-produced, concurrent) | Draft (0.x.x) — mutual reference with AA | AA and DA are produced concurrently; each references the other's draft IDs; neither may be baselined until both are at 1.0.0 |
| Architecture Principles Register (`PR`) | SA (self-produced, Phase A) | Version 0.1.0 or higher | Technology-independence principle is critical; read before authoring any component entry |
| `sprint.started` event | PM | Must be emitted for the Phase C Architecture Sprint | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- Business capabilities and processes from BA: the complete set of CAP-nnn and BPR-nnn entries that the AA must realise.
- Non-functional requirements from RR: performance, availability, security, scalability — these constrain component design (e.g., a high-availability requirement implies components must support redundant deployment, though the deployment mechanism is a Phase D decision).
- Integration context: what external systems exist, what data they expose, what protocols they use (at a protocol-style level: REST, event, batch — not specific products).
- Safety constraints at application level: from SCO Phase B — which processes must be safety-critical components.
- The mutual reference constraint: AA Interface Catalog references DA entity IDs (DE-nnn) for data entities involved in each interface. This requires DA to be drafted concurrently.

### Known Unknowns

| Unknown | Blocking | CQ Target | AA Section Affected |
|---|---|---|---|
| Unknown integration constraints (external systems present but interface not characterised) | Yes, for §3.7 (External Integration Catalog) | User or PO | §3.7 |
| Unclear interface requirements (a business process requires inter-component communication but direction and protocol style are not determinable) | Partially — SA can produce a component and flag the interface as TBD | PO or User | §3.3 Interface Catalog |
| Ambiguous component boundaries (a business process spans what could be one component or multiple) | No — SA makes a reasoned architectural decision; documents in ADR | — | §3.2 Application Component Catalog |
| Safety classification of a specific component (depends on SCO Phase B, which may not be complete when AA production begins) | Partially — SA marks component as `Safety-Relevant: TBD` and awaits CSCO | CSCO | §3.2, §3.9 |

### Clarification Triggers

SA raises a CQ when:

1. **Unknown integration constraints:** An external system is identified (from RR or business scenarios) but its interface is entirely uncharacterised — no protocol style, no data format direction, no known custodian. This blocks the corresponding entries in §3.7. Bounded CQ example: "Does system X expose an API, or does it provide batch data extracts?"
2. **Unclear interface requirements for a specific business process:** A BPR-nnn requires that two components exchange data, but the direction and triggering condition are not determinable from the BA or RR. Non-blocking — SA produces the component entries and marks the interface as `IFC-TBD` with a CQ reference; component interactions proceed without the interface.
3. **Missing non-functional requirements:** The RR contains no non-functional requirements (no availability, performance, or security constraints), and the domain strongly implies these are relevant (e.g., a payment processing system with no availability requirement). SA raises a non-blocking CQ to PO: "Are there availability, performance, or security requirements that should be recorded in the RR?"
4. **External system ownership unclear:** An external integration point is identified but no stakeholder or ORG unit is identified as the custodian. SA raises a non-blocking CQ to PO; the integration point is catalogued with `Data Sensitivity: unknown` and flagged.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="C", artifact_type="application-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase C Architecture Sprint.
2. Confirm BA is at version 1.0.0 (baselined). If not, SA must halt — do not begin AA production on a draft BA (ALG-008 if SA self-detects).
3. Confirm DA production has begun (even if only a skeleton) — AA and DA must be produced concurrently.
4. Read SCO Phase B update — note all safety constraints at application level.
5. Read RR current version — note all non-functional requirements and constraint-type requirements.

---

### Step 1 — Decompose Business Capabilities and Processes into Application Components

Starting from BA CAP-nnn and BPR-nnn entries, decompose the business function space into logical application components (ABBs).

**Decomposition principle:** One application component is the smallest logical unit that:
- Encapsulates a single, cohesive set of responsibilities
- Has a clearly defined boundary: what it does and what it does NOT do
- Can be specified by its interfaces (inputs, outputs) without reference to implementation

**Technology independence constraint (hard):** At this stage, no technology product names, frameworks, databases, or infrastructure specifics appear in any component entry. The AA defines logical ABBs. Physical SBBs are Phase D work.

For each component (APP-nnn):
- `Component ID`: APP-nnn (sequential, engagement-unique)
- `Name`: noun phrase ("Customer Identity Service", "Payment Processing Engine", "Audit Log Store")
- `Type`: Service / Store / Gateway / UI / Integration (per schema §3.2)
- `Responsibility`: one sentence — what this component does and what it is solely responsible for
- `Realises Capability`: CAP-nnn (one or more capabilities this component realises)
- `Safety-Relevant`: Yes / No / TBD (TBD if CSCO Phase B safety review is incomplete)
- `Status`: New / Existing / Modified / Retiring

Cross-reference: every BPR-nnn must be realisable by at least one APP-nnn. After producing the initial component list, do a reverse check against the Business Process Catalog — any process with no corresponding component is an AA gap.

---

### Step 2 — Author Application Component Catalog

Produce `architecture-repository/application-architecture/aa-0.1.0.md` §3.2 with all APP-nnn entries from Step 1.

Validate against the technology-independence constraint:
- Review each component description for technology product names. If found, remove them and replace with logical descriptions.
- If an architectural style decision is made (e.g., "this component is an event-driven integration adapter"), record the decision in `architecture-repository/adrs/adr-<id>.md` with rationale. The ADR is an architecture-domain decision — not a technology-domain ADR (which would belong in `technology-repository/`).

**Diagram Step D — ArchiMate Application Architecture Diagram**

Execute D1–D6 per `framework/diagram-conventions.md §5–5c`:
- **D1–D4:** Scan `elements/application/` sub-catalogs (components.yaml CMP-nnn, interfaces.yaml IFC-nnn, services.yaml ASV-nnn). Register new catalog entries for each APP-nnn component and IFC-nnn interface defined in this step. Validate no duplicate IDs; populate `linked_data_entity` cross-references where applicable.
- **D5a:** Load PUML template `framework/diagram-conventions.md §7.archimate-application`. Author ArchiMate application-layer diagram: components (CMP-nnn), interfaces (IFC-nnn), application services (ASV-nnn); catalog IDs as PUML aliases. Write to `architecture-repository/diagram-catalog/diagrams/c-archimate-application-v1.puml`. Update `diagrams/index.yaml`.
- **D6:** Call `validate_diagram`; fix errors; re-validate before proceeding.


---

### Step 3 — Author Interface Catalog

For each interface between components or between a component and an external actor:

Per-interface attributes (per schema §3.3):
- `Interface ID`: IFC-nnn
- `Name`: descriptive name ("Customer Registration API", "Payment Event Stream")
- `Exposed By`: APP-nnn (the component that provides this interface)
- `Consumed By`: APP-nnn or external actor name
- `Protocol / Style`: REST / gRPC / Event / Batch / Websocket / Webhook / Manual (logical style — not specific versions or products)
- `Data Entities Involved`: DE-nnn from DA (use DA draft IDs — mutual reference; if DA entity IDs are not yet defined, write `[DA-entity-TBD: description]` and resolve when DA draft is available)
- `Safety-Relevant`: Yes / No (follows from involved components and data entities)

Every interface must appear in at least one Application Interaction Diagram (Step 5). An interface in the catalog with no corresponding diagram is an incomplete AA.

**Diagram Step D — Sequence Diagrams (Key Interaction Flows)**

Execute D1–D6 per `framework/diagram-conventions.md §5–5c`:
- **D1–D4:** Scan `elements/application/components.yaml` and `elements/application/interfaces.yaml` for CMP-nnn and IFC-nnn participants. Check `sequences/participant-map.yaml`; register lifeline entries for any participants not yet mapped.
- **D5a:** Load PUML template `framework/diagram-conventions.md §7.sequence`. For each key interaction flow identified in this step, author a sequence diagram: CMP-nnn lifelines, IFC-nnn boundaries, synchronous vs. async message notation, `alt`/`opt` blocks for error paths. Write to `architecture-repository/diagram-catalog/diagrams/c-sequence-<flow-id>-v1.puml`. Update `diagrams/index.yaml`.
- **D6:** Call `validate_diagram`; fix errors; re-validate before proceeding.


---

### Step 4 — Build Application/Business Function Matrix

Produce the matrix (per schema §3.4) cross-referencing BPR-nnn (rows) × APP-nnn (columns):

- **●** = primary realisation (this component is the primary application realisation of this process)
- **○** = contributing (this component participates but is not primary)
- **—** = no relationship

Validation rules:
- Every BPR-nnn must have at least one **●** APP-nnn. A process with no primary application realisation is an AA gap.
- A single APP-nnn with **●** across more than 4–5 unrelated processes is likely a "god component" anti-pattern — consider decomposing. If decomposing, document the architectural decision in an ADR.

---

### Step 5 — Author Application Interaction Diagrams

Produce one Application Interaction Diagram per major value stream (VS-nnn from BA).

Per diagram, include (per schema §3.5):
- All APP-nnn components involved in that value stream
- All IFC-nnn interfaces used between those components
- All external systems or actors at the boundary (from §3.7 External Integration Catalog)
- Direction and nature of each interaction: synchronous (request-response) / asynchronous (event/message) / batch
- Trust boundaries (where components cross an internal/external or high-trust/low-trust boundary)

Rendered as structured text (ArchiMate Application Cooperation Viewpoint notation described textually, with a tabular or itemised representation of component interactions). A diagram tool rendering is optional at this stage — the structured text form is the canonical representation.

---

### Step 6 — Author Application Architecture Overview Diagram

Produce the single overview diagram (per schema §3.6) showing how the full application landscape realises business services (BSV-nnn from BA).

Structure: layered representation — business layer (BSV-nnn) → application layer (APP-nnn) → interface layer (IFC-nnn, showing data flows).

ArchiMate viewpoint: **Service Realization Viewpoint**.

This is the "one-page architecture" view that PM, PO, and SwA use as the primary reference during Phase D.

---

### Step 7 — Catalog External Integration Points

Produce the External System and Integration Points catalog (per schema §3.7):

For each external system integration:
- `Integration ID`: INT-nnn
- `External System`: name of the external system
- `Integration Type`: Direct API / Event / Batch / Manual / Unknown (if unknown, raise CQ)
- `Direction`: Inbound / Outbound / Bidirectional
- `Interface Used`: IFC-nnn (the interface through which integration occurs)
- `Data Sensitivity`: Public / Internal / Confidential / Restricted (classify based on the data entities involved; if uncertain, classify as Restricted pending CSCO review)

Every external system mentioned in: RR, BA Business Services Catalog (as external consumers), BA Stakeholder Register (as external systems), or Scoping Interview answers must appear in this catalog. An external system not catalogued is an AA gap.

---

### Step 8 — Author Application-Level Gap Analysis

Produce the Application-Level Gap Analysis (per schema §3.8):

For each APP-nnn:
- `Component`: APP-nnn name
- `Baseline (existing system)`: what currently exists that performs this component's function, or "None — greenfield"
- `Target (this architecture)`: the component as defined in the Application Component Catalog
- `Gap`: New / Modified / Retired
- `Resolution Approach`: Build / Buy / Reuse / Retire

For any component where `Resolution Approach: Buy` or `Reuse`, note that vendor/product selection is a Phase D decision — AA records the logical requirement, not the product answer.

---

### Step 9 — Cross-Reference SCO Phase C Application Update

Before baselining the AA:

1. For every APP-nnn marked `Safety-Relevant: Yes`, confirm that a handoff to CSCO has been created requesting the Phase C Application SCO update.
2. Once CSCO produces the Phase C Application SCO update: read the SCO update. For each safety constraint that applies to an APP-nnn, update AA §3.9 (SCO cross-reference table):

| Component ID | Safety Constraint Reference (SCO section) |
|---|---|
| APP-nnn | SCO §n.n |

3. If the CSCO's SCO update introduces new constraints that require AA component or interface changes: update the affected APP-nnn or IFC-nnn entries; increment the AA version; re-check the Application/Business Function Matrix and Application Interaction Diagrams for consistency.

4. Any `Safety-Relevant: TBD` fields must be resolved to Yes or No before AA can be baselined. Raise a blocking CQ to CSCO if any are still TBD.

---

### Step 10 — Coordinate with DA (Mutual Reference Resolution)

Before baselineing either AA or DA, resolve all mutual reference placeholders:

1. SA (wearing "AA author" hat): review all IFC-nnn entries that have `[DA-entity-TBD: description]` in the `Data Entities Involved` field. Replace each with the correct DE-nnn ID from the DA draft.
2. SA (wearing "DA author" hat): review all DA data flow entries that reference `[AA-component-TBD: description]`. Replace each with the correct APP-nnn ID.
3. Confirm that every IFC-nnn with `Safety-Relevant: Yes` references at least one DE-nnn with `Safety-Relevant: Yes` in the DA, or has a documented rationale for the classification mismatch.
4. Confirm that the AA Component Catalog's `Store` type components each have a corresponding data entity group in the DA Entity Catalog.

This step is a self-coordination step — SA is both the AA author and the DA author. The check is formal (it goes into the sprint log) even though no inter-agent communication is required.

---

### Step 11 — Baseline AA and Cast Phase C Gate Vote (AA component)

1. Assemble all sections into `architecture-repository/application-architecture/aa-1.0.0.md`.
2. Complete summary header:
   - `artifact-type: application-architecture`
   - `safety-relevant: true` if any safety-relevant component is defined
   - `csco-sign-off: true` only if safety-relevant components are defined AND CSCO has signed off
   - `pending-clarifications: [list open CQ-ids]`
3. Emit `artifact.baselined` for AA at version 1.0.0.
4. Create handoff to SwA: `handoff-type: phase-D-input` — AA is the primary input to Technology Architecture. Include: Application Component Catalog, Interface Catalog, Application/Business Function Matrix, External Integration Catalog.
5. Create handoff to CSCO: `handoff-type: phase-C-application-safety-review` if not already completed in Step 9.
6. The Phase C gate vote (C→D) is cast ONLY after BOTH AA and DA are at version 1.0.0. See `skills/phase-c-data.md` for the combined gate vote procedure.

**SA self-checklist for AA readiness (pre-gate):**
- [ ] Every APP-nnn realises at least one BPR-nnn from the BA
- [ ] Every IFC-nnn appears in at least one Application Interaction Diagram
- [ ] All safety-relevant components are flagged and cross-referenced to SCO (§3.9)
- [ ] No technology product names appear in any component or interface description
- [ ] All External Integration Points are catalogued with data sensitivity classification
- [ ] All `[DA-entity-TBD]` mutual reference placeholders are resolved
- [ ] CSCO sign-off present if any safety-relevant component is defined

---

## Feedback Loop

### SwA Feedback Loop (AA→TA Handoff Completeness)

After AA is baselined and handed off to SwA for Phase D:

- **Iteration 1:** SwA may return structured feedback on the AA handoff — specifically: ambiguous component boundaries, missing interface details required for TA, or interface style constraints that conflict with the target technology environment. SA reviews and, if the feedback is valid, updates the AA (not the TA — AA is the authoritative source).
- **Iteration 2:** SA addresses outstanding feedback; resubmits AA at incremented version (1.0.1); creates a new handoff event.
- **Termination:** SwA acknowledges the revised AA; proceeds with TA.
- **Max iterations:** 2.
- **Escalation:** If SwA's feedback after 2 iterations still identifies irresolvable conflicts (e.g., SwA's technology environment mandates a constraint that the AA cannot accommodate), raise `ALG-010` to PM. PM adjudicates: either AA must accommodate the constraint (requires RACI authority — if the constraint is technology-domain, SwA's position governs) or the technology environment constraint must be challenged (if it violates an architecture principle, SA's position governs). PM records the decision.

### CSCO Safety Review Loop (Application-Level)

- **Iteration 1:** SA sends handoff of safety-relevant APP-nnn entries; CSCO reviews; may flag additional safety-relevant components or add constraints.
- **Iteration 2:** SA updates affected entries; CSCO confirms Phase C Application SCO update.
- **Termination:** CSCO signs off; `csco-sign-off: true`.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` if unresolved; PM adjudicates. Do not baseline AA without CSCO sign-off if safety-relevant components are present.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="application-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | An application component is designed in a way that would violate a safety constraint in the SCO Phase B baseline | S1 | Halt production of the violating component design; emit `alg.raised`; notify CSCO immediately; do not include in ACC until resolved |
| ALG-008 | SA detects that the AA draft (0.x.x) has been consumed by SwA as an authoritative input before Phase C gate | S2 | Emit `alg.raised`; notify PM; PM invalidates consuming artifact sections; SwA must wait for AA 1.0.0 |
| ALG-010 | The two-iteration SwA feedback loop on AA→TA handoff completeness has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; SA may not unilaterally revise AA to match TA constraints that violate architecture principles |
| ALG-010 | The two-iteration CSCO safety review loop on Phase C Application components has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; do not baseline AA |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Application Architecture (`AA`) | `architecture-repository/application-architecture/aa-<version>.md` | 1.0.0 at Phase C gate (after DA also at 1.0.0) | `artifact.baselined` |
| Handoff to SwA (AA → Phase D input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (Phase C application safety review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase C gate vote (combined AA+DA) | EventStore | — | `gate.vote_cast` (emitted after DA also baselined — see `phase-c-data.md`) |

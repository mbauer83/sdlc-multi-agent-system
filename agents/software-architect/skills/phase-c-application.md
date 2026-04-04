---
skill-id: SwA-PHASE-C-APP
agent: SwA
name: phase-c-application
display-name: Phase C — Application Architecture
invoke-when: >
  Phase B gate has passed and the Phase C Architecture Sprint starts; SA has baselined
  the Business Architecture (BA) at 1.0.0 and the BA handoff has been acknowledged.
  Produces the Application Architecture (AA) concurrently with the Data Architecture
  (DA sub-track, SwA-PHASE-C-DATA).
trigger-phases: [C]
trigger-conditions:
  - gate.evaluated (from_phase=B, result=passed)
  - sprint.started (phase=C)
  - handoff.created from SA (artifact-type=business-architecture, handoff-type=phase-C-input)
entry-points: [EP-0, EP-A, EP-B, EP-C]
primary-outputs: [Application Architecture, Interface Catalog, Application Interaction Diagrams]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase C — Application Architecture

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** C — Information Systems Architecture (Application sub-track)  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.4`, `framework/artifact-schemas/application-architecture.schema.md`, `raci-matrix.md §3.4`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Business Architecture (`BA`) | Solution Architect | Baselined at version 1.0.0 | Hard prerequisite — AA cannot begin without baselined BA; BA is the primary derivation source for all APP-nnn entities |
| Requirements Register (`RR`) | Product Owner | Current (Phase C iteration) | SwA reads RR for non-functional requirements and interface constraints |
| Safety Constraint Overlay (`SCO`) — Phase B update | CSCO | Baselined | SwA cross-references safety-relevant components against SCO Phase B constraints |
| Data Architecture (`DA`) — draft | SwA (self-produced, concurrent) | Draft (0.x.x) — mutual reference with AA | AA and DA are produced concurrently; each references the other's draft IDs; neither may be baselined until both are at 1.0.0 |
| Architecture Principles Register (`PR`) | Solution Architect | Version 0.1.0 or higher | Technology-independence principle is critical; read before authoring any component entry |
| `sprint.started` event | PM | Must be emitted for the Phase C Architecture Sprint | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- Business capabilities and processes from BA: the complete set of CAP-nnn, BPR-nnn, and BSV-nnn entries that the AA must realise. Every APP-nnn must have a BA anchor.
- Business objects (BOB-nnn): Store-type components own data entities derived from business objects; understanding BOB-nnn boundaries prevents over- or under-decomposition.
- Non-functional requirements from RR: performance, availability, security, scalability — constrain component design at the logical level (e.g., high availability implies redundancy-capable components, though deployment mechanism is Phase D).
- Integration context: what external systems exist, what data they expose, what protocol style is appropriate (REST, event, batch — not specific products).
- Safety constraints at application level: from SCO Phase B — which business processes must result in safety-relevant application components.
- The mutual reference constraint: AA Interface Catalog references DA entity IDs (DOB-nnn) for data entities involved in each interface. DA must be drafted concurrently.

### Known Unknowns

| Unknown | Blocking | CQ Target | AA Section Affected |
|---|---|---|---|
| Unknown integration constraints (external system interface not characterised) | Yes, for External Integration Catalog | User or PO | External Integration Catalog |
| Unclear interface requirements for a specific business process | Partially — SwA produces component and flags interface as TBD | PO or User | Interface Catalog |
| Ambiguous component boundaries (one process could map to one or multiple components) | No — SwA makes reasoned architectural decision; documents in ADR | — | Application Component Catalog |
| Safety classification of a specific component (depends on SCO Phase B) | Partially — mark `Safety-Relevant: TBD`; await CSCO | CSCO | Component Catalog, Phase C safety cross-reference |

### Clarification Triggers

SwA raises a CQ when:

1. **Unknown integration constraints:** An external system is identified (from RR or BA) but its interface is entirely uncharacterised. Bounded CQ: "Does system X expose an API, or does it provide batch data extracts?"
2. **Unclear interface requirements for a specific business process:** A BPR-nnn requires component data exchange but direction and triggering condition are not determinable. Non-blocking — SwA produces the component entries and marks the interface as `IFC-TBD`.
3. **Missing non-functional requirements:** RR contains no NFRs and the domain strongly implies relevance (e.g., a payment system with no availability requirement). Non-blocking CQ to PO.
4. **External system ownership unclear:** No stakeholder identified as custodian. Non-blocking — catalogue with `Data Sensitivity: unknown` and flag.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="C", artifact_type="application-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase C Architecture Sprint.
2. Confirm BA handoff from SA has been received and BA is at version 1.0.0. If BA is not at 1.0.0: do not begin AA production (ALG-008 if self-detected attempt to proceed on draft BA).
3. Confirm DA production has begun (even if only a skeleton) — AA and DA must be produced concurrently.
4. Read SCO Phase B update — note all safety constraints at application level.
5. Read RR current version — note all non-functional requirements and constraint-type requirements.
6. Read Architecture Principles Register — the technology-independence principle is a hard constraint on every APP-nnn entry.

---

### Step 1 — Decompose Business Capabilities and Processes into Application Components

Starting from BA CAP-nnn, BPR-nnn, and BSV-nnn entries, decompose the business function space into logical application components (ABBs).

**Decomposition principle:** One application component is the smallest logical unit that:
- Encapsulates a single, cohesive set of responsibilities
- Has a clearly defined boundary: what it does and what it does NOT do
- Can be specified by its interfaces (inputs, outputs) without reference to implementation

**Technology independence constraint (hard):** At this stage, no technology product names, frameworks, databases, or infrastructure specifics appear in any component entry. The AA defines logical ABBs. Physical SBBs are Phase D work.

For each component (APP-nnn entity file in `architecture-repository/model-entities/application/components/`):
- `entity-id`: APP-nnn (sequential, engagement-unique)
- `name`: noun phrase ("Customer Identity Service", "Payment Processing Engine", "Audit Log Store")
- `entity-type`: ApplicationComponent
- `subtype`: Service / Store / Gateway / UI / Integration (per schema §3.2)
- `responsibility`: one sentence — what this component does and what it is solely responsible for
- `realises`: CAP-nnn or BPR-nnn or BSV-nnn (one or more BA entities this component realises)
- `safety-relevant`: Yes / No / TBD (TBD if CSCO Phase B safety review is incomplete)
- `status`: New / Existing / Modified / Retiring

Cross-reference: every BPR-nnn must be realisable by at least one APP-nnn or, for collaborative multi-service behavior, by an AIA-nnn (ApplicationInteraction). After producing the initial component list, do a reverse check against the BA Business Process Catalog — any process with no realizing element is an AA gap.

**Realization rule — collaborative behavior (mandatory):** When multiple application services jointly realize a business process, use the Collaboration + Interaction pattern (see `framework/diagram-conventions.md §11.5`):
1. Create `ACO-nnn` (ApplicationCollaboration in `model-entities/application/collaborations/`) aggregating the participating services.
2. Create `AIA-nnn` (ApplicationInteraction in `model-entities/application/interactions/`) describing the structured sequence those services perform.
3. Connect: `ACO-nnn --assignment--> AIA-nnn` and `AIA-nnn --realization--> BPR-nnn`.
Do NOT create individual `ASV-nnn --realization--> BPR-nnn` connections when the realization requires multiple services acting together.

Write each entity as an ERP-compliant `.md` file: `architecture-repository/model-entities/application/components/APP-nnn.md`.

---

### Step 2 — Author Application Component Catalog and Archimate Diagram

Validate each APP-nnn against the technology-independence constraint:
- Review each component description for technology product names. If found, remove and replace with logical descriptions.
- If an architectural style decision is made (e.g., "this component is an event-driven integration adapter"), record in `architecture-repository/decisions/adr-<id>.md` as an architecture-level ADR (not a technology ADR — technology ADRs belong in `technology-repository/`).

**Diagram Step D — ArchiMate Application Architecture Diagram**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="application-component")`, `list_artifacts(artifact_type="application-interface")`, and `list_artifacts(artifact_type="application-service")` to identify entities in scope. Use `search_artifacts` for cross-layer entities (BA services BSV-nnn that application services realise).
- **D2:** For each entity that will appear in the diagram, verify its `§display ###archimate` subsection exists. Add missing subsections via `write_artifact`; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.archimate-application")`. Author ArchiMate application-layer diagram with entity artifact-ids as PUML aliases. Include required frontmatter comment block. Write to `architecture-repository/diagram-catalog/diagrams/c-archimate-application-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate before proceeding.

---

### Step 3 — Author Interface Catalog

For each interface between components or between a component and an external actor, produce an entity file at `architecture-repository/model-entities/application/interfaces/IFC-nnn.md`:

Per-interface attributes (per schema §3.3):
- `entity-id`: IFC-nnn
- `name`: descriptive name ("Customer Registration API", "Payment Event Stream")
- `entity-type`: ApplicationInterface
- `exposed-by`: APP-nnn (the component that provides this interface)
- `consumed-by`: APP-nnn or external actor name
- `protocol-style`: REST / gRPC / Event / Batch / Websocket / Webhook / Manual (logical style — not specific versions or products)
- `data-entities-involved`: DOB-nnn from DA (use DA draft IDs — mutual reference; write `[DA-entity-TBD: description]` if DA IDs not yet available)
- `safety-relevant`: Yes / No (follows from involved components and data entities)

Every interface must appear in at least one Application Interaction Diagram (Step 5).

**Diagram Step D — Sequence Diagrams (Key Interaction Flows)**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="application-component")` and `list_artifacts(artifact_type="application-interface")` to identify component lifelines and interface boundaries. Use `search_artifacts` for cross-layer participants (BA actors ACT-nnn that initiate flows).
- **D2:** For each entity appearing as a participant, verify its `§display ###sequence` subsection. Add missing subsections; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.sequence")`. For each key interaction flow, author a sequence diagram. Write to `architecture-repository/diagram-catalog/diagrams/c-sequence-<flow-id>-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors.

---

### Step 4 — Build Application/Business Function Matrix

Produce the matrix (per schema §3.4) cross-referencing BPR-nnn (rows) × APP-nnn (columns):

- **●** = primary realisation
- **○** = contributing
- **—** = no relationship

Validation rules:
- Every BPR-nnn must have at least one **●** APP-nnn. A process with no primary application realisation is an AA gap.
- A single APP-nnn with **●** across more than 4–5 unrelated processes is likely a "god component" anti-pattern — consider decomposing; document in ADR.

---

### Step 5 — Author Application Interaction Diagrams

Produce one Application Interaction Diagram per major value stream (VS-nnn from BA).

Per diagram (per schema §3.5):
- All APP-nnn components involved in that value stream
- All IFC-nnn interfaces used between those components
- All external systems or actors at the boundary
- Direction and nature of each interaction: synchronous (request-response) / asynchronous (event/message) / batch
- Trust boundaries (where components cross an internal/external or high-trust/low-trust boundary)

---

### Step 6 — Author Application Architecture Overview Diagram

Produce the single overview diagram (per schema §3.6) showing how the full application landscape realises business services (BSV-nnn from BA).

Structure: layered representation — business layer (BSV-nnn) → application layer (APP-nnn) → interface layer (IFC-nnn, showing data flows).

ArchiMate viewpoint: **Service Realization Viewpoint**.

Write overview narrative to `architecture-repository/overview/aa-overview.md`.

---

### Step 7 — Catalog External Integration Points

Produce the External System and Integration Points catalog (per schema §3.7):

For each external system integration:
- `Integration ID`: INT-nnn
- `External System`: name
- `Integration Type`: Direct API / Event / Batch / Manual / Unknown
- `Direction`: Inbound / Outbound / Bidirectional
- `Interface Used`: IFC-nnn
- `Data Sensitivity`: Public / Internal / Confidential / Restricted (if uncertain: Restricted pending CSCO review)

Every external system mentioned in RR, BA Business Services Catalog (as external consumers), BA Stakeholder Register (as external systems), or Scoping Interview answers must appear in this catalog.

---

### Step 8 — Author Application-Level Gap Analysis

Produce the Application-Level Gap Analysis (per schema §3.8):

For each APP-nnn:
- `Baseline (existing system)`: what currently exists, or "None — greenfield"
- `Target (this architecture)`: the component as defined
- `Gap`: New / Modified / Retired
- `Resolution Approach`: Build / Buy / Reuse / Retire (product selection is Phase D; AA records the logical requirement)

---

### Step 9 — Cross-Reference SCO Phase C Application Update

Before baselining the AA:

1. For every APP-nnn marked `Safety-Relevant: Yes`: confirm a handoff to CSCO has been created requesting Phase C Application SCO update.
2. Once CSCO produces Phase C Application SCO update: read it. For each safety constraint applying to an APP-nnn, update the entity's `§content` safety cross-reference section.
3. Any `Safety-Relevant: TBD` fields must be resolved before AA can be baselined. Raise a blocking CQ to CSCO if any TBD entries remain.

---

### Step 10 — Coordinate with DA (Mutual Reference Resolution)

Before baselining either AA or DA, resolve all mutual reference placeholders:

1. Review all IFC-nnn entries with `[DA-entity-TBD: description]`. Replace each with the correct DOB-nnn ID from the DA draft.
2. Confirm every IFC-nnn with `Safety-Relevant: Yes` references at least one DOB-nnn with `Safety-Relevant: Yes` in the DA, or has documented rationale.
3. Confirm AA `Store`-type APP-nnn components each have a corresponding data entity group in DA.

---

### Step 11 — Send to SA for Traceability Review

Before baselining AA at 1.0.0:

1. Emit `handoff.created` to SA: `handoff-type=phase-C-sa-traceability-review`, `artifact-type=application-architecture`, including draft AA path.
2. Await SA's structured traceability feedback (SA-PHASE-C-APP-REVIEW skill). SA has up to 2 review iterations.
3. Address all material findings (T1 phantom realisation claims, T2 component/entity mismatches, T3 technology-independence violations, T4 unrealised business processes).
4. Re-send revised AA draft on each iteration.
5. Once SA emits consulting acknowledgement: proceed to Step 12.

---

### Step 12 — Baseline AA and Cast Phase C Gate Vote (AA component)

1. Write all APP-nnn and IFC-nnn entity files to `architecture-repository/model-entities/application/components/` and `application/interfaces/` at version 1.0.0 via `write_artifact`.
2. Write `architecture-repository/overview/aa-overview.md` (summary narrative, artifact-id list, safety-relevant flag summary).
3. Emit `artifact.baselined` for AA at version 1.0.0.
4. Create handoff to CSCO: `handoff-type: phase-C-application-safety-review` if not already completed in Step 9.
5. The Phase C gate vote (C→D) is cast ONLY after BOTH AA and DA are at version 1.0.0. See `skills/phase-c-data.md` for the combined gate vote procedure.

**SwA self-checklist for AA readiness (pre-gate):**
- [ ] Every APP-nnn realises at least one BPR-nnn, BSV-nnn, or CAP-nnn from the BA
- [ ] Every IFC-nnn appears in at least one Application Interaction Diagram
- [ ] All safety-relevant components are flagged; CSCO Phase C Application SCO update received
- [ ] No technology product names appear in any component or interface description
- [ ] All External Integration Points are catalogued with data sensitivity classification
- [ ] All `[DA-entity-TBD]` mutual reference placeholders are resolved
- [ ] SA Consulting Acknowledgement received (SA-PHASE-C-APP-REVIEW completed)

---

## Feedback Loop

### SA Traceability Review Loop

- **Iteration 1:** SwA sends AA draft to SA. SA reviews for BA traceability (business-layer anchoring, technology-independence). SA provides structured feedback.
- **Iteration 2:** SwA addresses findings; resends revised AA.
- **Termination:** SA emits consulting acknowledgement. SwA proceeds to baseline.
- **Max iterations:** 2.
- **Escalation:** If SA's round-2 feedback still identifies material T1/T2/T3/T4 findings: raise `ALG-010` to PM. PM adjudicates. SwA may not baseline AA without SA acknowledgement (or PM adjudication override) — the C→D gate will not pass without the consulting acknowledgement on record.

### CSCO Safety Review Loop (Application-Level)

- **Iteration 1:** SwA sends handoff of safety-relevant APP-nnn entries; CSCO reviews; may flag additional safety-relevant components or add constraints.
- **Iteration 2:** SwA updates affected entries; CSCO confirms Phase C Application SCO update.
- **Termination:** CSCO signs off; `csco-sign-off: true` in AA summary.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` if unresolved; PM adjudicates. Do not baseline AA without CSCO sign-off if safety-relevant components are present.

### Personality-Aware Conflict Engagement

SwA respects SA's authority over business-layer traceability. When SA raises a T4 finding (unrealised BPR), SwA's obligation is to either map the BPR to an existing component or explain why the process does not require a dedicated application realisation (e.g., it is realised through an existing BSV-nnn). SwA does not dispute SA's identification of a T3 technology-independence violation — product names must be removed from logical architecture artifacts without negotiation. When CSCO raises Phase C safety constraints that require component restructuring, SwA applies the constraint and documents the rationale in an ADR.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | SA round-2 feedback requires structural revision | S2 |
| `gate-veto` | Phase C gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from BA or RR | S2 |

On trigger: call `record_learning()` with `artifact-type="application-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | An application component is designed in a way that would violate a safety constraint in the SCO Phase B baseline | S1 | Halt production of the violating component design; emit `alg.raised`; notify CSCO immediately; do not include in entity files until resolved |
| ALG-008 | SwA detects that the AA draft (0.x.x) has been consumed by another agent as an authoritative input before Phase C gate | S2 | Emit `alg.raised`; notify PM; PM invalidates consuming artifact sections; consuming agent must wait for AA 1.0.0 |
| ALG-010 | The two-iteration SA traceability review loop has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates |
| ALG-010 | The two-iteration CSCO safety review loop on Phase C Application components has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; do not baseline AA |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Application Component entities (APP-nnn) | `architecture-repository/model-entities/application/components/` | 1.0.0 at Phase C gate (after DA also at 1.0.0) | `artifact.baselined` per entity |
| Interface entities (IFC-nnn) | `architecture-repository/model-entities/application/interfaces/` | 1.0.0 | `artifact.baselined` per entity |
| Application Service entities (ASV-nnn) | `architecture-repository/model-entities/application/services/` | 1.0.0 | `artifact.baselined` per entity |
| AA Overview | `architecture-repository/overview/aa-overview.md` | — | `artifact.created` |
| Phase C ArchiMate diagram | `architecture-repository/diagram-catalog/diagrams/c-archimate-application-v1.puml` | — | `artifact.created` |
| Phase C Sequence diagrams | `architecture-repository/diagram-catalog/diagrams/c-sequence-<flow-id>-v1.puml` | — | `artifact.created` |
| Handoff to SA (AA draft for traceability review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (Phase C application safety review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase C gate vote (combined AA+DA) | EventStore | — | `gate.vote_cast` (emitted after DA also baselined — see `phase-c-data.md`) |

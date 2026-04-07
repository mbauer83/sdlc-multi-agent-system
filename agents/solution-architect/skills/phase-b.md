---
skill-id: SA-PHASE-B
agent: SA
name: phase-b
display-name: Phase B — Business Architecture
invoke-when: >
  Phase A gate has passed (gate.evaluated phase=A result=passed) and the Phase B Architecture
  Sprint starts; or when Architecture Vision is baselined at 1.0.0 and BA does not yet exist.
trigger-phases: [B]
trigger-conditions:
  - gate.evaluated (from_phase=A, result=passed)
  - sprint.started (phase=B)
entry-points: [EP-0, EP-A, EP-B]
primary-outputs: [Business Architecture, Business Process Catalog, Value Stream Map, Organisational Model]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase B — Business Architecture

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** B — Business Architecture  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.3`, `framework/artifact-schemas/business-architecture.schema.md`, `raci-matrix.md §3.3`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Runtime Tooling Hint

Representation choice (balanced and mandatory):
- Use `.puml` diagrams when flow, topology, sequence, trust boundaries, or interaction context is the primary concern.
- Use matrix artifacts (`model_create_matrix`) for dense many-to-many mappings, coverage, and traceability where node-link readability degrades.
- Do not replace contextual architecture views with matrices alone: keep a reasonable set of diagrams that preserves end-to-end context for the domain slice.
- Practical threshold: if a single node-link view would exceed about 25 elements or become edge-dense, keep/author at least one contextual diagram and shift dense cross-reference detail to a matrix.
- If edges remain congested after one layout pass, split the relationship family into focused sub-diagrams and stop tuning the monolith.
- Where traceability is split across multiple diagrams, produce a matrix companion that captures complete many-to-many coverage.

This skill describes tool-use intent. Runtime binding is code-owned.

- Discovery/search/filter/query: use model query tools (`model_query_*`) or compatible aliases.
- Validation: use model verifier tools (`model_verify_file`, `model_verify_all`).
- Building entities/connections/diagrams: use deterministic model write tools (`model_create_entity`, `model_create_connection`, `model_create_diagram`, `model_create_matrix`) with `dry_run` before writes.
- `invoke-when` and `trigger-conditions` remain intent-level guidance; runtime gate/state enforcement is owned by orchestration and PM routing.
- Keep BA output structure strict and schema-aligned even when invoked from different entry profiles.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Architecture Vision (`AV`) | SA (self-produced, Phase A) | Baselined at version 1.0.0 | Hard prerequisite — Phase B cannot begin if AV is not baselined |
| Requirements Register (`RR`) | Product Owner | Current iteration complete; `cq.answered` events received for all Phase A-relevant CQs | SA reads RR for business process and capability requirements |
| Business Scenarios (detailed) | Product Owner | Draft acceptable; at least one value stream describable from available scenarios | Non-blocking absence: SA raises a non-blocking CQ to PO if no scenarios provided |
| Safety Constraint Overlay (`SCO`) — Phase A baseline | CSCO | Baselined (the SCO produced or updated after Phase A gate) | SA must cross-reference safety-relevant processes against SCO constraints |
| Architecture Principles Register (`PR`) | SA (self-produced) | Version 0.1.0 or higher | SA reads PR to ensure BA respects architecture principles |
| `sprint.started` event | PM | Must be emitted for the Phase B Architecture Sprint | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- Business domain characterisation: sufficient to decompose AV capability clusters into Level-1 and Level-2 capabilities. This must come from: AV §3.5, RR, Business Scenarios, or Scoping Interview answers.
- Organisational structure: sufficient to populate the Organisational Model (§3.7). May be partially inferred from stakeholder register.
- Business process semantics: sufficient to describe triggering events, outcomes, and key steps for each in-scope process. This may require PO input.
- Value stream end-points: sufficient to define the triggering stakeholder and the delivered value for each value stream.
- STAMP control structure scope: from SCO Phase A — to correctly flag safety-relevant processes.

### Known Unknowns

| Unknown | Blocking | CQ Target | BA Section Affected |
|---|---|---|---|
| Detailed business processes (steps, triggers, outcomes) for domains SA cannot characterise from available inputs | Yes, for BPC (§3.3) | PO or User | §3.3 Business Process Catalog |
| Organisational structure (business units, teams, external parties) | Partially — BA can proceed with partial org model | User or PO | §3.7 Organisational Model |
| Value stream triggers and metrics | Partially — BA can document known value streams; flag unknowns | PO | §3.5 Value Stream Map |
| Capability ownership when multiple org units could own a capability | No — SA makes reasoned assignment and documents as ADR | — | §3.2 Business Capability Map |
| Business goals not traceable to any available AV driver | No — SA raises a non-blocking CQ to PO; proceeds with known goals | PO | §3.6 Motivation Architecture |

### Clarification Triggers

SA raises a CQ when:

1. **Undefined business processes:** A capability cluster from AV §3.5 cannot be decomposed into any identifiable processes because the domain is unfamiliar and the RR and Business Scenarios do not describe it. Blocking for BPC entries in that domain.
2. **Unknown organisational structure:** The Organisational Model cannot have any entries because no org information is present in any available artifact. Non-blocking (BA proceeds; §3.7 populated with placeholder `ORG-001: Engagement Sponsor` plus agent roles); SA raises a non-blocking CQ.
3. **Conflicting capability claims:** Two requirements in the RR assign the same capability to different organisational owners, and the conflict would produce materially different BA structures. SA raises this as a CQ to PO with a specific resolution question, not an open-ended one.
4. **Unclear value stream boundaries:** When two described processes overlap in a way that makes it impossible to assign process IDs unambiguously. Raise a bounded CQ: "Does process X terminate before process Y begins, or do they run concurrently?"
5. **Ambiguous requirement mapped to multiple capabilities:** A requirement in the RR refers to an activity that spans two capability domains; the correct decomposition is not determinable from available information. SA raises a CQ to PO with two specific interpretations and asks which is correct.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="B", artifact_type="business-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase B Architecture Sprint.
2. Confirm AV is at version 1.0.0 (baselined).
3. Read AV §3.5 (Capability Overview) and §3.3 (Stakeholder Register) — primary inputs.
4. Read SCO Phase A baseline — note safety constraints applicable at the business process level.
5. Read current RR — note all business-level requirements.

Discovery: call `list_artifacts(artifact_type="value-stream")` and `list_artifacts(artifact_type="capability")` to find any existing VS or CAP entities from a prior pass through this phase; use as starting points rather than recreating from scratch.

---

### Step 0.VS — Define Value Stream Stages *(Outside-In Entry Point)*

**This step precedes capability decomposition.** Business architecture is built outside-in: start from what stakeholders receive (value streams and the services they deliver), then work inward toward processes, functions, and roles. See `framework/diagram-conventions.md §11.9.1`.

For each value stream identified in AV §3.5 or the Stakeholder Register:

1. Check via `list_artifacts(artifact_type="value-stream")` whether VS entities already exist. Read each via `read_artifact(id, mode="full")` to see whether stages are already documented in `§content`.
2. For each VS-nnn, document 3–7 named stages in the entity `§content` section. Each stage must state:
   - **Stage name** (noun phrase, e.g., "Customer Onboarding")
   - **Consuming stakeholder** (STK-nnn or description)
   - **Value delivered** at this stage (one sentence)
   - **Key business services** (BSV-nnn to be defined in Step 2) — link by ID once created
3. If no VS entities exist: create VS-nnn entities via `write_artifact`, one per identified value stream.
4. If stages are already documented: verify they are stakeholder-value-focused, **not ADM-phase-focused**. Revise any stage definitions that describe internal process steps rather than stakeholder-facing value delivery.

**CQ trigger:** If the engagement scope cannot support even one identifiable value stream with a concrete consuming stakeholder, raise a blocking CQ to PO before proceeding.

---

### Step 1 — Identify and Scope Business Services per VS Stage

**Primary step of Phase B.** For each VS stage defined in Step 0.VS, enumerate the business services (BSV-nnn) that constitute the value delivered at that stage. Business services are the **stable external contracts** — what the stakeholder can depend on regardless of internal process implementation.

Check via `list_artifacts(artifact_type="business-service")` for existing BSV entities. Read each to assess whether VS stage linkage is documented.

For each BSV-nnn:
- `Service ID`: BSV-nnn
- `Name`: noun phrase as the consuming stakeholder would name it
- `VS Stage(s)`: which stage(s) of which VS-nnn deliver this service
- `Consumer`: STK-nnn — who receives this service
- `Description`: externally visible behavior (no internal "how")
- `Safety-Relevant`: Yes / No

**Completeness rule:** Every VS stage must have at least one BSV. A stage with no associated service is either mislabeled (it describes an internal step, not stakeholder-facing value) or a model gap requiring a CQ to PO.

**Traceability back to AV:** Every BSV must ultimately trace to at least one AV DRV-nnn driver. Record this traceability explicitly. A service untraceable to any driver is either out of scope or points to a missing driver in AV.

**Outcome-evidence completion (mandatory):** For each in-scope goal (`GOL-nnn`), model at least one verifiable outcome (`OUT-nnn`) and at least one course of action (`COA-nnn`) that operationalizes the outcome through capabilities and execution paths. Required operational chain at Phase B baseline:
`STK -> DRV -> GOL -> OUT -> COA -> CAP -> (BPR and/or BSV) -> value delivered in VS stage`.
Each `OUT-nnn` must include measurable evidence fields in properties (metric, threshold/target, evidence source artifact).

---

### Step 1.1 — Capability Cross-Reference *(Supporting EA step — not the entry point)*

Capability mapping provides enterprise architecture context for the business layer. It should not drive the business architecture — that is driven by value streams and services (Steps 0.VS and 1). Perform this step **after** BSV entities are modeled, to cross-reference which capabilities enable each service.

From AV §3.5, verify existing CAP-nnn entities via `list_artifacts(artifact_type="capability")`. For each CAP-nnn, record which BSV-nnn(s) it supports (association) and which BFN-nnn(s) realize it (realization connection). If AV §3.5 capability clusters do not cover domains implied by the BSV set, note as AV gaps (SA action item); do not block BA progress.

Capability map is documented as a supporting table in the BA narrative — it is not the primary ArchiMate diagram.

---

### Step 1.5 — Build Business Concept Map (Objects, Interfaces, Events)

**Perform this step before authoring processes.** Business objects and events are the structural glue that makes processes coherent — modeling them first prevents process definitions that operate on undefined concepts.

**1.5a — Business Objects (BOB-nnn):** Identify the key business objects that persist across VS stages or are produced/consumed by multiple processes. Check via `list_artifacts(artifact_type="business-object")` for any already modeled. Each BOB-nnn requires:
- A globally stable name (e.g., "Architecture Artifact", "Sprint Plan", "Gate Outcome")
- A description of its lifecycle — which VS stage creates it, which stages consume or transform it
- A corresponding DOB-nnn at the application layer (create or reference): record the BOB↔DOB mapping as an `archimate-association` connection

**1.5b — Business Interfaces (BIF-nnn):** Identify any formal access points through which external stakeholders interact with the system's business services — named entry/exit points used by more than one stakeholder or process. Many engagements will have few or no BIF entities; do not manufacture them.

**1.5c — Business Events (BEV-nnn):** Identify events that trigger transitions between processes or between VS stages. Events are stimuli — they do not perform work themselves; they initiate a BPR. Each BEV-nnn requires:
- A name in past-tense or noun-event form ("Sprint Started", "Gate Passed", "CQ Raised")
- The process(es) it triggers (BPR-nnn) — record as `archimate-triggering` connection files

**Concept map completeness check:** Every BOB-nnn must connect to at least one BPR/BIA (via access or association). Every BEV-nnn must connect to at least one BPR (via triggering). Isolated objects or events are model gaps.

---

### Step 2 — Author Business Process Catalog

For each CAP-nnn, enumerate in-scope business processes (BPR-nnn).

Per-process attributes (per schema §3.3):
- `Process ID`: BPR-nnn
- `Name`: verb phrase ("Onboard Customer", "Process Payment")
- `Owning Capability`: CAP-nnn
- `Description`: 2–4 sentences describing what the process does from start to finish
- `Triggering Event`: what initiates this process (a stakeholder action, a time event, a system event, or an upstream process outcome)
- `Outcome`: what the process delivers when complete
- `Safety-Relevant`: Yes / No

**Safety-relevance determination:**  
A process is safety-relevant if it: (a) directly operates on or controls a system component identified as safety-relevant in the SCO, (b) produces, modifies, or deletes data classified as Safety-Critical in the SCO, or (c) is in a causal chain that could lead to a hazard category identified in AV §3.7.

When in doubt: mark as `Safety-Relevant: Yes`. The CSCO will review and may downgrade. Never downgrade unilaterally.

Safety-relevant processes must be cross-referenced in the SCO Phase B update produced by CSCO.

**Realization rule — collaborative business behavior (mandatory):** When multiple business roles or actors *jointly* perform a business process in a structured sequence, use the BusinessCollaboration + BusinessInteraction pattern (see `framework/diagram-conventions.md §11.5`):
1. Create `BCO-nnn` (BusinessCollaboration in `model-entities/business/collaborations/`) grouping the participating roles/actors.
2. Create `BIA-nnn` (BusinessInteraction in `model-entities/business/interactions/`) describing the structured sequence.
3. Connect: `BCO-nnn --assignment--> BIA-nnn` and `BIA-nnn --realization--> BSV-nnn` or `BIA-nnn --realization--> BPR-nnn` as appropriate.
Do NOT create individual `BPR-nnn --realization--> BSV-nnn` connections when the realization requires multiple actors collaborating in a structured flow.

**Diagram Step D — Activity/BPMN Process Diagrams**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="business-process", filter={"safety-relevant": true})`, `list_artifacts(artifact_type="business-interaction")`, and `list_artifacts(artifact_type="business-actor")` to identify swimlane participants and safety-relevant processes. Also call `list_artifacts(artifact_type="business-event")` to identify triggering events for each process.
- **D2:** For each BPR-nnn, BIA-nnn, and ACT-nnn that will appear, verify `§display ###activity` subsections exist. Add missing subsections via `write_artifact`; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.activity-bpmn")`. For each process or interaction with non-trivial branching or multi-party flow, author an Activity/BPMN diagram. Swimlane pools keyed to entity artifact-ids. Write to `architecture-repository/diagram-catalog/diagrams/b-bpmn-<bpr-id>-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate before proceeding.

---

### Step 2.5 — Decompose Business Functions

**Business functions** (BFN-nnn) are stable organizational groupings — continuous capabilities that own clusters of related processes. They are not the same as processes (which are time-bounded and sequential). Functions provide the structural container to which roles and actors are assigned in the structural viewpoint.

Check via `list_artifacts(artifact_type="business-function")` for any existing BFN entities.

For each BFN-nnn define:
- `Name`: noun phrase for the stable organizational function (e.g., "Project Governance Function")
- `Description`: what this function is continuously responsible for
- `Realizes`: BSV-nnn(s) and CAP-nnn(s) — create `archimate-realization` connection files
- `Assigned roles/actors`: ACT-nnn and BCO-nnn — create `archimate-assignment` connection files

**Function-to-process relationship:** A BFN groups related BPRs. This relationship is documented in the BA narrative; it does not require separate ArchiMate connection files (the structural diagram shows the grouping visually).

**Coverage rule:** Every BPR-nnn must belong to exactly one BFN. Every BFN must have at least one assigned ACT or BCO. Every BFN must realize at least one BSV or CAP. Verify via `list_connections(source=<bfn-id>)` and `list_connections(target=<bfn-id>)` after creating connection files.

**Diagram Step D — Business Architecture ArchiMate Diagrams**

Produce the dual-viewpoint ArchiMate diagrams per `framework/diagram-conventions.md §11.9.4` and §7 templates. Decide whether a single combined diagram suffices (≤ ~25 elements total) or separate structural and operational diagrams are needed; document the decision in diagram frontmatter.

Execute D1–D4 per `framework/diagram-conventions.md §5` for each diagram:

**Structural viewpoint** (`b-archimate-business-structural-v1.puml`):
- **D1:** `list_artifacts` for BFN, ACT, BCO, BSV, CAP; `list_connections` to verify assignment and realization coverage.
- **D2:** Verify `§display ###archimate` on all entities. Add missing via `write_artifact`; `regenerate_macros()`.
- **D3:** Load `read_framework_doc("framework/diagram-conventions.md §7.archimate-business")`. Group by function; roles/actors inside or adjacent to their function grouping; services outside. Include capabilities. Write via `write_artifact`.
- **D4:** `validate_diagram`; cross-check that every BFN shown has at least one role and one service connection visible.

**Operational viewpoint** (`b-archimate-business-operational-v1.puml`) — or combined if scale permits:
- **D1:** `list_artifacts` for BPR, BIA, BEV, ACT, BCO, BSV; `list_connections` for assignment, realization, triggering.
- **D2:** Verify `§display ###archimate` on all entities. Add missing; `regenerate_macros()`.
- **D3:** Load `read_framework_doc("framework/diagram-conventions.md §7.archimate-business-operational")`. Group by process cluster or VS stage; events connected to the processes they trigger. For decomposed behavior, draw the parent `BPR-nnn` / `BIA-nnn` as the container element and nest stage behaviors inside it with internal `flow`/`triggering` lines (per `framework/diagram-conventions.md §11.9.1a`); do not use outer grouping + duplicate parent nodes. Write via `write_artifact`.
- **D3a (decomposition sizing check):** Do not force a fixed stage count (for example, 3-step templates). Use a manageable stage count driven by domain behavior. If a parent decomposition becomes crowded or mixes concerns, split into additional top-level `BPR`/`BIA` elements and coordinate them explicitly (triggering/event-mediated links) rather than adding excessive nested stages.
- **D4:** `validate_diagram`; cross-check that every BPR shown has at least one role and one realizing service visible.

Multiple diagrams per viewpoint are acceptable and encouraged when scope is large: produce one operational diagram per major VS stage or process cluster rather than one monolithic diagram.

---

### Step 3 — Author Value Stream Map

For each primary value stream (a sequence of business processes that delivers tangible value to an external stakeholder):

Per-value-stream attributes (per schema §3.5):
- `Value Stream ID`: VS-nnn
- `Name`: noun phrase ending in the value delivered ("Customer Acquisition", "Order Fulfilment")
- `Triggering Stakeholder`: STK-nnn from Stakeholder Register
- `Value Delivered`: what the triggering stakeholder receives at the end
- `Key Processes (ordered)`: BPR-nnn, BPR-nnn, ... (ordered by execution sequence)
- `Metrics`: how value delivery is measured (e.g., "Order processing time < 2 hours")

ArchiMate viewpoint: **Business Process Cooperation Viewpoint** — rendered as a textual representation of cross-process interactions and sequencing within each value stream.

Minimum: one value stream per Level-1 capability domain. A domain with no identifiable value stream is a BA gap — flag it as an open item and raise a non-blocking CQ to PO.

**Diagram Step D — Value Stream Use Case Diagrams**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="value-stream")` and `list_artifacts(artifact_type="business-actor")` to identify VS-nnn entries and their triggering stakeholder ACT-nnn. Verify each VS-nnn traces to a delivered outcome CAP-nnn via `list_artifacts(artifact_type="capability")`.
- **D2:** For each ACT-nnn and VS-nnn entity that will appear, verify `§display ###archimate` subsections exist. Add missing subsections via `write_artifact`; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.use-case")`. Author one Use Case diagram per value stream: triggering stakeholder as entity alias actor, value stream stages as use cases, participating actors annotated. Include required frontmatter comment block. Write to `architecture-repository/diagram-catalog/diagrams/b-usecase-<vs-id>-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate before proceeding.

---

### Step 4 — Build Business Function/Process Matrix

Produce the matrix (per schema §3.4) mapping each CAP-nnn to each BPR-nnn:

Tooling pattern (required for large mappings):
- Author the mapping as ID-first markdown and write it via `model_create_matrix` to `architecture-repository/diagram-catalog/diagrams/`.
- Keep IDs in cells for deterministic parsing; enable auto-linking so output remains human-readable and navigable.
- Do not replace this matrix with a single dense node-link diagram.

- **●** = primary realisation (this process is the primary means by which this capability is realised)
- **○** = contributing (this process contributes to the capability but is not the primary realisation)
- **—** = no relationship

Every capability must have at least one **●** process. A capability with only **—** entries is either out of scope or has a missing process — resolve before baseline.

Every process must have exactly one **●** capability. A process with two **●** entries spans two capabilities — split the process or choose the primary capability and mark the other **○**.

---

### Step 5 — Author Motivation Architecture

Produce the Motivation Architecture table (per schema §3.6):

For each stakeholder goal (GL-nnn):
- `Goal ID`: GL-nnn
- `Stakeholder`: STK-nnn
- `Goal Statement`: plain-language statement of what the stakeholder wants to achieve
- `Driver (from AV)`: DRV-nnn — which architecture driver corresponds to this goal
- `Realising Capability`: CAP-nnn — which capability satisfies this goal

Traceability chain at Phase B: DRV-nnn (AV) → GL-nnn (Motivation) → CAP-nnn (Capability Map).

Every external stakeholder (non-agent) in the Stakeholder Register must have at least one GL-nnn entry. Agent-role stakeholders (STK-001 to STK-009) do not require goal entries unless the engagement is specifically about improving the development process.

ArchiMate viewpoint: **Goal Realization Viewpoint** — rendered as a textual table; not required to be a graphical model at this stage.

---

### Step 6 — Author Organisational Model

Produce the Organisational Model (per schema §3.7):

For each organisational unit:
- `Org Unit ID`: ORG-nnn
- `Name`: formal name of the unit
- `Type`: Division / Team / External Party / Regulatory Body / System (for automated actors)
- `Primary Capabilities Owned`: CAP-nnn list — capabilities this org unit is responsible for delivering
- `Key Roles`: named roles within this unit that interact with in-scope processes

Sources for organisational information: Scoping Interview answers, stakeholder register (external stakeholders often map to ORG entries), RR stakeholder column, Business Scenarios.

If organisational structure is unknown: produce ORG-001 (Engagement Sponsor — the client organisation) and ORG-002 (Development Team — the SA's engagement team) as minimum placeholders. Flag as incomplete and raise a non-blocking CQ to PO.

ArchiMate viewpoint: **Organisation Viewpoint**.

---

### Step 7 — Author Business Services Catalog

Produce the Business Services Catalog (per schema §3.8):

A business service is a named service that the business provides externally — the externally visible output of a business process or value stream.

For each BSV-nnn:
- `Service ID`: BSV-nnn
- `Name`: service name as the consuming stakeholder would call it
- `Provider (ORG)`: ORG-nnn — which org unit provides the service
- `Consumer (Stakeholder)`: STK-nnn — which stakeholder consumes the service
- `Realised By (Process)`: BPR-nnn — the business process that delivers the service

Every value stream must produce at least one business service. Every external stakeholder (non-agent) must consume at least one business service — if a stakeholder has no service, either the stakeholder is passive/inform-only (in which case they may not need a BSV) or there is a BA gap.

---

### Step 8 — Author Gap Analysis (Business Domain)

Elaborate the Business domain row from AV §3.8 into a per-capability gap analysis (per schema §3.9):

| Capability | Baseline State | Target State | Gap Type | Priority |
|---|---|---|---|---|
| CAP-nnn | Current maturity | Target maturity | Missing / Underdeveloped / Redundant | High / Medium / Low |

Gap types:
- **Missing:** No current capability exists; must be built or acquired.
- **Underdeveloped:** Capability exists but does not meet target maturity.
- **Redundant:** Capability exists in duplicate; rationalisation is needed.

Priority: High for Core capabilities with Missing or Underdeveloped gaps; Medium for Supporting; Low for Commodity.

---

### Step 9 — Cross-Reference SCO Phase B Update

Before baselining the BA:

1. Review all BPR-nnn entries marked `Safety-Relevant: Yes`.
2. For each safety-relevant process, confirm that the CSCO has been notified — this should occur via the handoff created in Step 2 as soon as safety-relevant processes are identified. If the handoff has not been created, create it now.
3. After CSCO produces the Phase B SCO update: read the SCO update and cross-reference the BA §3.10 field with the SCO version ID and version number.
4. If the CSCO's SCO update adds new safety constraints that affect BA process definitions (e.g., a process must now include an audit logging step), update the affected BPR-nnn entries and re-check the Business Function/Process Matrix.

---

### Step 10 — Baseline BA and Cast Phase B Gate Vote

1. Assemble all sections into `architecture-repository/business-architecture/ba-1.0.0.md`.
2. Complete the summary header:
   - `artifact-type: business-architecture`
   - `safety-relevant: true` (always — safety constraints at business level defined here)
   - `csco-sign-off: true` (only after CSCO has signed off on Phase B SCO update)
   - `pending-clarifications: [list any open CQ-ids]`
3. Emit `artifact.baselined` for BA at version 1.0.0.
4. Create handoff to CSCO: `handoff-type: phase-B-sco-update-input` — BA is ready for CSCO's Phase B SCO update.
5. Create handoff to PM: BA is baselined; Phase B gate may proceed.
6. Cast `gate.vote_cast` for B→C gate:
   - `result: approved` only if all items in the SA self-checklist below are satisfied.
   - `result: veto` with rationale if any item is not satisfied.

**SA self-checklist for Phase B gate vote:**
- [ ] Every VS-nnn has ≥ 3 named stages in `§content`, each stage names ≥ 1 BSV
- [ ] Every BSV-nnn has ≥ 1 realizing BPR, BFN, or BIA
- [ ] Every BPR-nnn has ≥ 1 assigned ACT or BCO; every BPR is served by ≥ 1 ASV or annotated as manual
- [ ] Every BFN-nnn has ≥ 1 assigned ACT or BCO and realizes ≥ 1 BSV or CAP
- [ ] Every BOB-nnn is accessed by ≥ 1 BPR or BIA; every BEV-nnn triggers ≥ 1 BPR
- [ ] Cross-layer traceability: every BSV has a downward connection to ≥ 1 application-layer element; every BPR has ≥ 1 serving ASV (or manual annotation) — verified via `list_connections(target=<id>)`
- [ ] Every safety-relevant process is flagged and a handoff to CSCO has been created
- [ ] CSCO has signed off on the Phase B SCO update (`csco-sign-off: true`)
- [ ] At least one structural and one operational ArchiMate diagram produced (or one combined diagram for small systems) and validated
- [ ] `pending-clarifications` is empty or all items are `assumption`-flagged with PM acceptance

---

## Feedback Loop

### PO Collaboration Loop (Business Process Accuracy)

- **Iteration 1:** SA produces draft BPC and Value Stream Map; creates structured feedback request to PO asking for accuracy review of process descriptions. PO reviews and provides corrections or additions.
- **Iteration 2:** SA incorporates corrections; sends revised BPC for confirmation.
- **Termination:** PO confirms process catalog accuracy, or SA accepts remaining items as assumptions documented in BA `## Assumptions` section.
- **Max iterations:** 2.
- **Escalation:** If Iteration 2 produces conflicting requirements (PO's process description contradicts a requirement already in the RR), raise `ALG-010` to PM for adjudication. Do not proceed on a contested process definition.

### CSCO Safety Review Loop (Safety-Relevant Processes)

- **Iteration 1:** SA sends handoff of safety-relevant BPR entries to CSCO. CSCO reviews; may add safety constraints or flag additional safety-relevant processes.
- **Iteration 2:** SA updates any newly flagged BPR entries; CSCO confirms Phase B SCO update.
- **Termination:** CSCO signs off on Phase B SCO update; `csco-sign-off: true` in BA header.
- **Max iterations:** 2.
- **Escalation:** If unresolved after 2 iterations, raise `ALG-010`. Do not baseline BA without CSCO sign-off.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="business-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | A business process is identified that would directly violate a safety constraint in the current SCO (Phase A baseline) | S1 | Halt production of the process; emit `alg.raised`; notify CSCO immediately; do not include the violating process in BPC until CSCO resolves |
| ALG-008 | SA detects that a consuming agent (Phase C) has begun work using a draft BA (version 0.x.x) before Phase B gate | S2 | Emit `alg.raised`; notify PM; PM invalidates the consuming artifact until BA is baselined |
| ALG-010 | The two-iteration feedback loop with PO on business process accuracy has been exhausted without resolution — conflicting process definitions remain | S3 | Emit `alg.raised`; PM adjudicates; halt affected BPR finalisation |
| ALG-010 | The two-iteration CSCO safety review loop has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; do not baseline BA |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Business Architecture (`BA`) | `architecture-repository/business-architecture/ba-<version>.md` | 1.0.0 at Phase B gate | `artifact.baselined` |
| Handoff to SwA (BA baselined at 1.0.0; Phase C primary input — `handoff-type: phase-C-ba-input`) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (Phase B SCO update input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PM (BA baselined; Phase B gate input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase B gate vote | EventStore | — | `gate.vote_cast` |

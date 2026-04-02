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
version: 1.0.0
---

# Skill: Phase B — Business Architecture

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** B — Business Architecture  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.3`, `framework/artifact-schemas/business-architecture.schema.md`, `raci-matrix.md §3.3`, `clarification-protocol.md`, `algedonic-protocol.md`

---

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

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase B Architecture Sprint.
2. Confirm AV is at version 1.0.0 (baselined).
3. Read AV §3.5 (Capability Overview) — this is the primary input to Step 1.
4. Read SCO Phase A baseline — note all safety constraints that apply at the business process level.
5. Read current RR — note all business-level requirements (Functional and Constraint types).

---

### Step 1 — Decompose Capability Clusters into Business Capability Map

Starting from AV §3.5 capability clusters, produce the two-level Business Capability Map:

**Level 1 — Capability Domains:** One per AV capability cluster (preserve names for traceability). Add additional domains only if RR or Business Scenarios identify capabilities not represented in AV §3.5; if added, flag as a gap to be reflected in an AV revision (or accepted as a scope refinement with PM approval).

**Level 2 — Capabilities (CAP-nnn):** For each Level-1 domain, enumerate specific, named capabilities. Naming rule: noun phrase describing what the business *has the ability to do*, e.g., "Customer Identity Verification", not "Verify Customer Identity".

Attributes per capability (per schema §3.2):
- `Capability ID`: CAP-nnn (sequential, engagement-unique)
- `Name`: noun phrase
- `Domain`: Level-1 domain name
- `Description`: one sentence — what the capability enables; no "how"
- `Strategic Classification`: Core / Supporting / Commodity
- `Maturity Level`: Current (exists and operates) / Developing (exists but immature) / Target (does not yet exist)
- `Gap`: Yes (target not met) / No (current meets target)

**Traceability constraint:** Every CAP-nnn must be traceable to at least one AV DRV-nnn business driver. Record the traceability explicitly in the BA document. Any capability not traceable to a driver is either an out-of-scope item (remove it) or a missing driver (add DRV-nnn to AV §3.4 and note the AV revision as an action item for SA).

ArchiMate viewpoint: **Capability Map Viewpoint** (structured as a matrix or tree; rendered in text form as a nested list or table).

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

---

### Step 4 — Build Business Function/Process Matrix

Produce the matrix (per schema §3.4) mapping each CAP-nnn to each BPR-nnn:

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
- [ ] Every CAP-nnn is traceable to at least one DRV-nnn from AV
- [ ] Every safety-relevant process is flagged and a handoff to CSCO has been created
- [ ] Every value stream is complete end-to-end (trigger → outcome)
- [ ] Every external stakeholder has at least one GL-nnn entry in the Motivation Architecture
- [ ] CSCO has signed off on the Phase B SCO update (`csco-sign-off: true`)
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
| Handoff to CSCO (Phase B SCO update input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PM (BA baselined; Phase B gate input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase B gate vote | EventStore | — | `gate.vote_cast` |

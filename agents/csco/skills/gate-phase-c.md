---
skill-id: CSCO-GATE-C
agent: CSCO
name: gate-phase-c
display-name: Phase C Safety Gate Review — Application and Data Architecture
invoke-when: >
  SwA produces both Application Architecture (AA) and Data Architecture (DA) at version
  1.0.0 (artifact.baselined emitted for both). CSCO reviews AA and DA for application-level
  and data-governance safety, performs STAMP Level 2 analysis, authors SCO Phase C update,
  and casts the C→D gate vote. Review is triggered by whichever of AA or DA baselines last;
  CSCO awaits both before casting the gate vote.
trigger-phases: [C]
trigger-conditions:
  - artifact.baselined from SwA (artifact_type=application-architecture) AND artifact.baselined from SwA (artifact_type=data-architecture) — both required
  - handoff.created from SwA requesting CSCO safety review of AA and DA
  - cq.answered resolving a blocking Phase C CSCO safety CQ
entry-points: [EP-0, EP-A, EP-B, EP-C]
primary-outputs:
  - SCO Phase C Update (sco-C-1.0.0.md)
  - Gate Record Phase C (gr-C-D-1.0.0.md)
  - gate.vote_cast for C→D gate
complexity-class: standard
version: 1.0.0
---

# Skill: Phase C Safety Gate Review — Application and Data Architecture

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** C — Application Architecture and Data Architecture
**Skill Type:** Gate review — STAMP Level 2 analysis + gate vote
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (STAMP Level 2 — application component UCAs and data safety constraints)
**Framework References:** `agile-adm-cadence.md §6.4`, `raci-matrix.md §3.4`, `framework/artifact-schemas/application-architecture.schema.md`, `framework/artifact-schemas/data-architecture.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `framework/discovery-protocol.md §2`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Application Architecture (AA) | SA — architecture-repository/application-architecture/ | Baselined at version 1.0.0 | Both AA and DA must be baselined before the C→D gate vote is cast |
| Data Architecture (DA) | SA — architecture-repository/data-architecture/ | Baselined at version 1.0.0 | If AA baselines first and DA is still at 0.x.x: CSCO begins AA review but does not cast C→D vote until DA is also baselined |
| SCO Phase B Baseline | CSCO — safety-repository/safety-constraint-overlay/ | Baselined at version 1.0.0 | Required — Phase C update is an extension of Phase B; if absent: CSCO must produce combined SCO |
| Business Architecture (BA) | SA — architecture-repository/business-architecture/ | Baselined at version 1.0.0 | Cross-reference for capability→component traceability |
| Requirements Register (RR) | PO — project-repository/ | Current version (draft acceptable) | Used to identify safety-relevant requirements traced to application components |
| sprint.started event | PM | Must be emitted for Phase C sprint | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- The STAMP Level 2 analysis procedure: component-level control actions, interface-level UCAs, data entity safety classification implications.
- Application architecture safety patterns: component isolation, authentication and authorisation at component interfaces, error propagation control, safe failure modes.
- Data governance principles: data classification (Public / Internal / Confidential / Restricted), access control requirements per classification, data retention and deletion obligations, personal data processing requirements (GDPR and equivalent).
- Interface safety: authentication (who can call this interface), authorisation (what they can do), input validation (preventing injection of unsafe values), error handling (what happens when the interface fails).

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Access control model for safety-relevant components (who can call what) | No at Phase C — CSCO notes the gap; access control implementation is Phase D/G. Phase C constraint specifies the requirement. | SA (AA Interface Catalog) | SCO §7 (UCAs — authorisation context), §5 (Constraints — access control constraints) |
| Data classification for every data entity in the DA Data Entity Catalog | Yes if any entity lacks a classification — the DA must classify every entity | SA (DA Data Classification Register) | SCO §5 (data-level constraints), §7 (data access UCAs) |
| Sensitivity of external system data (data from external integrations) | No — CSCO assumes worst-case classification (most sensitive) for unclassified external data | SA (AA External Integration Catalog) | SCO §5 (external data constraints) |
| GDPR/privacy lawful basis for each category of personal data processing | Yes for systems processing personal data in regulated jurisdictions | User (via PM) or SA (DA Governance Rules) | SCO §9 (Compliance Requirements — privacy) |

### Clarification Triggers

CSCO raises a CQ when:

1. **DA Data Classification Register is incomplete or absent:** The DA does not provide a data classification for every data entity in the Entity Catalog. Data entities without a classification cannot be assigned safety constraints. CSCO raises a blocking CQ to SA to complete the classification register before the C→D gate can be cast.
2. **Application component performs safety-critical function not described in AA:** An AA component's functional description is too vague to identify its control actions (e.g., "TransactionService — handles transactions" without specifying what types, what actors can initiate them, what the output format is). CSCO raises a CQ to SA requesting sufficient detail for UCA analysis.
3. **Privacy lawful basis not established for personal data processing:** For a system in a GDPR-applicable jurisdiction, the DA or AA does not identify the lawful basis (consent, contract, legal obligation, legitimate interest) for processing each category of personal data. Blocking for compliance checklist completion.
4. **Safety-relevant interface has no authentication description:** An AA interface that handles Confidential or Restricted data specifies no authentication requirement. CSCO raises a CQ to SA (and notes this as a Phase C Violation Type A finding — the interface design violates the relevant SC-nnn authentication constraint).

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="CSCO", phase="C", artifact_type="safety-constraint-overlay")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`:

1. **Layer 1 — Engagement State:** Read AA and DA from architecture-repository/; read SCO Phase B baseline from safety-repository/; read BA from architecture-repository/business-architecture/; read RR if available; read clarification-log/ (safety-relevant CQs from Phase C); read handoff-log/ (SA handoffs for AA and DA review); read algedonic-log/ (open ALG signals affecting Phase C scope).
2. **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for data protection regulations (GDPR, HIPAA, CCPA, etc.), application security standards (OWASP ASVS, ISO 27001 Annex A controls applicable at design level), and any domain-specific application safety standards.
3. **Layer 3 — External Sources:** Check external-sources/ for any configured compliance databases with application-level or data-level requirements.
4. **Layer 4 — Target Repository:** If target-repo is configured, check for existing API security documentation, data classification policies, or privacy impact assessments.
5. **Layer 5 — Inference:** Annotate all inferred fields with `[inferred — source: domain knowledge]`.

---

### Step 1 — Confirm Gate Readiness

1. Confirm `artifact.baselined` has been emitted for both AA and DA at version 1.0.0. If only one is baselined: begin review of the baselined artifact but do not cast the C→D gate vote. Record the pending gate vote in SCO §10 as an open finding.
2. Confirm SCO Phase B baseline exists at 1.0.0.
3. Check for revisit trigger. If revisit: proceed to Step 9 (revisit handling).
4. Load the CSCO-STAMP-STPA methodology reference.

---

### Step 2 — Read Application Architecture in Full

Read the AA document:

- **Application Component Catalog (APP-nnn):** For each component: note the component's function, its inputs and outputs, the business capability it realises, and any functional descriptions indicating safety-relevant operations (data access, state mutation, external communication, authorisation decision).
- **Interface Catalog (IFC-nnn):** For each interface: note the caller, the callee, the data transferred, and any stated authentication or authorisation requirements. Flag interfaces that handle safety-relevant data categories (Confidential or Restricted per DA data classification) or perform safety-relevant operations.
- **Application/Business Function Matrix:** Verify that every safety-relevant business function from the BA has been allocated to an application component. Flag any safety-relevant business function with no allocated component as a gap.
- **Application Interaction Diagrams:** Review for safety-relevant interaction flows: does the sequence of interactions ensure that safety-critical steps (validation, authorisation, audit) are always executed before consequential actions?
- **External Integration Catalog:** For each external integration: note the data exchanged, the direction (inbound/outbound), and the trust level of the external system.

---

### Step 3 — Read Data Architecture in Full

Read the DA document:

- **Data Entity Catalog (DE-nnn):** For each data entity: note the entity name, the type of data it represents, and its classification from the Data Classification Register. If any entity lacks a classification: flag immediately (blocking finding per Knowledge Adequacy Check trigger 1).
- **Logical Data Model:** Note relationships between data entities — particularly relationships that could allow a less-sensitive entity to be used to infer or access a more-sensitive entity.
- **Data Classification Register:** Read in full. For entities classified as Confidential or Restricted: note which application components (from AA) create, read, update, or delete these entities (CRUD matrix).
- **Data/Business Function Matrix (CRUD):** Identify which business functions (and therefore which processes and roles) have CRUD access to which data entities.
- **Data Flow Diagrams:** Review for safety-relevant data flows: data crossing trust boundaries (internal system to external system, authenticated component to unauthenticated channel), sensitive data transmitted without encryption indication, and data aggregation patterns that could create new risks.
- **Data Governance Rules:** Review for any governance rule that has a safety constraint implication (e.g., "Customer records must be deleted within 30 days of account closure" → requires a SC-nnn constraint on the deletion process).

---

### Step 4 — Perform STAMP Level 2 Analysis — Application Component UCAs

Using the existing SCO Phase B §6 (Control Structure — business level) as the starting point, extend the control structure to the application component level:

**4a. Extend Control Structure (SCO §6 update — Level 2):**

For each safety-relevant application component identified in Step 2:
- Identify its control actions (the operations the component performs that could affect safety: data reads, writes, deletions, state transitions, authorisation decisions, external calls).
- Identify the controlled process for each control action (the component or data entity being acted upon).
- Identify feedback channels (how the component knows the operation succeeded or failed: return codes, exception handling, acknowledgement events, audit log entries).
- Add Level 2 entries to SCO §6 Control Structure table.

**4b. Identify Component-Level UCAs (SCO §7 update — Level 2):**

For each control action identified in 4a: apply all four UCA types. Phase C UCAs focus on:

- **Authentication failures:** An API interface provides data to a caller without verifying the caller's identity (not-provided: authentication check not provided).
- **Authorisation failures:** A component performs a write operation for a caller who does not have the required role or permission (provided when not needed: the write is executed in a context where the caller lacks authorisation).
- **Validation failures:** A component processes input data without validating it against expected constraints, allowing malformed or malicious data to propagate (not-provided: validation not provided).
- **Error propagation:** A component propagates an upstream error state to a downstream consumer without sanitising the error, causing the downstream component to enter an unsafe state (provided too early: the downstream call is made before the error is handled).
- **Data access violations:** A component accesses a data entity classified as Restricted through a path that bypasses the DA's stated access control rules.

For each UCA: author UCA-nnn per `skills/stamp-stpa-methodology.md UCA format`. Link to H-nnn and L-nnn.

**4c. Interface Safety Review:**

For each interface in the AA Interface Catalog that handles Confidential or Restricted data:
1. Authentication check: Is there a stated authentication requirement? If not: Violation Type A against the applicable SC-nnn authentication constraint (or SC-PENDING if no constraint exists yet).
2. Authorisation check: Is there a stated authorisation scope? If not: Violation Type B finding (missing coverage).
3. Input validation check: Is there any description of how the interface validates input? If the interface accepts external or untrusted input and no validation is described: Violation Type A.
4. Error handling check: Is there a stated error response for the interface? If the interface has no described error handling and the operation is safety-relevant: Violation Type B.

---

### Step 5 — Perform Data Safety Analysis

For each data entity in the DA Data Classification Register classified as Confidential or Restricted:

1. **Access constraint check:** Verify that the SCO contains an SC-nnn constraint governing who can access this entity and under what conditions. If no constraint exists: author a new SC-nnn (data-level access constraint) and add it to SCO §5.
2. **Retention constraint check:** If a regulatory standard (GDPR, HIPAA, SOX) requires a specific retention or deletion period for this entity type: verify the DA Governance Rules reflect this obligation. If absent: Violation Type A against the applicable regulatory SC-nnn.
3. **Cross-entity risk:** Review the Logical Data Model for relationships between Restricted entities and lower-classification entities that could enable inference attacks (e.g., a join between an anonymised dataset and a user identifier table that re-identifies personal data). If found: flag as Violation Type A and author a new SC-nnn addressing data aggregation risk.
4. **Data flow trust boundary:** Review Data Flow Diagrams for any flow where a Confidential or Restricted entity crosses a trust boundary (internal to external, or authenticated zone to unauthenticated zone) without an indication of encryption or access control. Flag as Violation Type A.

---

### Step 6 — Author New Safety Constraints (SCO §5 update)

For each new UCA, interface safety gap, and data safety finding from Steps 4 and 5 where no existing SC-nnn constraint covers it: author a new SC-nnn constraint per `skills/stamp-stpa-methodology.md §Step 3`:

Phase C constraints are primarily:
- **Architectural type:** Component isolation requirements, service boundary requirements (e.g., "Safety-critical components must be deployed in isolation from general-purpose components").
- **Technical type (preliminary):** Interface-level authentication and authorisation requirements (e.g., "IFC-003 must require OAuth2 bearer token authentication"). Note: these will be refined to specific technology choices in Phase D; Phase C constraints state the requirement, not the implementation.
- **Regulatory type:** Data protection and privacy obligations derived from DA governance rules and regulatory standards.

---

### Step 7 — Update SCO with Phase C Content

Update the SCO document to produce `sco-C-0.1.0.md` (draft):

- §5: Add new SC-nnn constraints from Steps 4c, 5, and 6. Retain all Phase A and Phase B constraints verbatim.
- §6: Add Level 2 control structure entries from Step 4a. Retain all Phase A/B entries.
- §7: Add Level 2 UCA-nnn records from Step 4b. Retain all Phase A/B UCAs.
- §8: Add new LS-nnn loss scenarios for each new UCA. Retain all Phase A/B loss scenarios.
- §9: Update compliance requirements for data protection obligations. Add specific article references for each regulatory standard.
- §10: Add new open safety findings from Steps 4 and 5. Close findings from Phase B that are addressed in the AA or DA. Flag any DA entity lacking a data classification as an open blocking finding.
- §11: Add Phase C gate summary when gate vote is cast.

---

### Step 8 — Cast C→D Gate Vote

**Approve** if: all Violation Type A findings from Steps 4 and 5 are resolved, all DA data entities have classifications, SCO Phase C update is complete with at least one constraint per new UCA, and no blocking SF-nnn items remain in SCO §10.

**Conditional** if: Violation Type B findings exist (coverage gaps in areas not yet designed by SwA in Phase D), but no Violation Type A conflicts are present. Specify: the gap, the Phase D artifact where coverage is expected, and the sprint deadline.

**Veto** if: one or more Violation Type A findings remain after SA revision. Specifically:
- A data entity without a classification in the DA (blocking finding — cannot proceed to Phase D without complete classification).
- An interface handling Restricted data with no authentication requirement stated.
- A data flow crossing a trust boundary for Restricted data without access control indication.

Emit `gate.vote_cast` for C→D gate. If approve or conditional: promote SCO Phase C to `sco-C-1.0.0.md`. Emit `artifact.baselined` for SCO Phase C update. Produce Gate Record `gr-C-D-1.0.0.md`. Emit `artifact.baselined` for Gate Record. Emit `handoff.created` to PM and to SA (structured feedback).

---

### Step 9 — Revisit Handling (trigger="revisit" only)

If `trigger="revisit"` and `phase_visit_count > 1`:

1. Read the EventStore gate history to identify which AA or DA sections changed.
2. Read the prior SCO Phase C version.
3. Apply Steps 2–7 only to the changed sections. Preserve all non-affected content verbatim.
4. Update only the SCO constraints, UCAs, and findings affected by the changes.
5. Increment SCO version and re-cast the C→D gate vote.

---

## Feedback Loop

**Maximum iterations: 2.** After Iteration 2 without resolution: raise ALG-010 (inter-agent deadlock) to PM.

**Iteration 1:** CSCO emits `gate.vote_cast (veto)` with specific SC-nnn and structured feedback. SA revises AA or DA (or both) and re-baselines. SA emits `artifact.baselined` for each revised artifact.

**Iteration 2:** CSCO reviews only the revised sections. If all Violation Type A findings resolved: approve. If any remain: cast second veto.

**Termination conditions:**
- **Satisfied:** All Violation Type A findings resolved. CSCO approves.
- **User risk acceptance:** User explicitly accepts residual risks. CSCO records acceptance in SCO §10 and approves.
- **Deadlock (ALG-010):** Raised to PM after Iteration 2. CSCO veto stands during adjudication.

### Personality-Aware Conflict Engagement

**CSCO ↔ SA (data classification and interface safety):**

SA may assert that data classification is the PO's domain or that interface security is a Phase D concern. CSCO's stance: data classification is a DA artifact requirement (per `framework/artifact-schemas/data-architecture.schema.md`) — SA is accountable for the DA, including the Data Classification Register. Interface authentication and authorisation requirements are architecture-level constraints (not implementation-level) — they belong in Phase C. CSCO distinguishes consistently: Phase C specifies the requirement (e.g., "this interface requires caller authentication"); Phase D specifies the mechanism (e.g., "implement OAuth2 with JWT bearer tokens").

**CSCO ↔ SA (missing component isolation for safety-critical functionality):**

If CSCO identifies that a safety-critical business function is allocated to a component that is co-located with general-purpose, non-safety components in the AA, and the SCO contains an isolation constraint, CSCO raises a Violation Type A finding. SA may argue that isolation is an infrastructure concern (Phase D). CSCO's response: the component architecture decision (which components are co-located or separated) is Phase C. The technology implementation of isolation (containers, VMs, network zones) is Phase D. If the AA design does not reflect isolation at the component allocation level, the Phase D isolation is architecturally undermined.

**CSCO ↔ PM (both AA and DA must be baselined before gate vote):**

PM may push CSCO to cast the C→D gate vote based on AA alone while DA is still being revised. CSCO's stance: the C→D gate covers both AA and DA. CSCO can begin AA review immediately after AA baselines, but the C→D gate vote is not cast until both artifacts are baselined and reviewed. CSCO communicates this dependency to PM as a process constraint, not a personal preference.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="safety-constraint-overlay"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

- **ALG-001 (S1 — Safety-Critical):** A safety-critical application component (one that controls a safety-critical process or handles safety-critical data) has no isolation mechanism described in the AA, and no feasible isolation approach can be identified at the architecture level. Raised immediately to PM and user. Phase D does not begin until the AA is revised to reflect an isolation approach.
- **ALG-001 (S1 — Safety-Critical):** A data entity classified as Restricted in the DA has no access control constraint in the SCO and no access control requirement in the AA Interface Catalog, and the entity is accessible via at least one external-facing interface. Raised immediately to PM.
- **ALG-010 (S3 — Inter-Agent Deadlock):** After two iterations, CSCO and SA cannot agree on data entity classification, interface authentication requirements, or component isolation scope. Raised to PM for adjudication.

---

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Safety Constraint Overlay — Phase C Update | `SCO-C-1.0.0` | `safety-repository/safety-constraint-overlay/sco-C-1.0.0.md` | `artifact.baselined` |
| STAMP/STPA Analysis — Phase C Update | `sa-001-C.md` | `safety-repository/stamp-stpa/sa-001-C.md` | `artifact.baselined` |
| Gate Record — C→D | `GR-C-D-1.0.0` | `safety-repository/gate-records/gr-C-D-1.0.0.md` | `artifact.baselined` |
| Gate Vote — C→D | (event payload) | EventStore | `gate.vote_cast` |
| Structured feedback to SA (AA and DA findings) | (handoff records) | engagements/<id>/handoff-log/ | `handoff.created` |

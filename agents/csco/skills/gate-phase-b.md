---
skill-id: CSCO-GATE-B
agent: CSCO
name: gate-phase-b
display-name: Phase B Safety Gate Review — Business Architecture
invoke-when: >
  SA produces Business Architecture (BA) at version 1.0.0 (artifact.baselined emitted).
  CSCO reviews BA for process-level safety implications, performs STAMP Level 1 update
  (business process UCAs), authors SCO Phase B update, and casts the B→C gate vote.
trigger-phases: [B]
trigger-conditions:
  - artifact.baselined from SA (artifact_type=business-architecture)
  - handoff.created from SA requesting CSCO safety review of BA
  - cq.answered resolving a blocking Phase B CSCO safety CQ
entry-points: [EP-0, EP-A, EP-B]
primary-outputs:
  - SCO Phase B Update (sco-B-1.0.0.md)
  - Gate Record Phase B (gr-B-C-1.0.0.md)
  - gate.vote_cast for B→C gate
version: 1.0.0
---

# Skill: Phase B Safety Gate Review — Business Architecture

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** B — Business Architecture
**Skill Type:** Gate review — STAMP Level 1 update + gate vote
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (STAMP Level 1 — business process UCA analysis)
**Framework References:** `agile-adm-cadence.md §6.3`, `raci-matrix.md §3.3`, `framework/artifact-schemas/business-architecture.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `framework/discovery-protocol.md §2`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Business Architecture (BA) | SA — architecture-repository/business-architecture/ | Baselined at version 1.0.0 | Formal gate review cannot begin until BA is baselined |
| SCO Phase A Baseline | CSCO — safety-repository/safety-constraint-overlay/ | Baselined at version 1.0.0 | Required — Phase B SCO update is an extension of Phase A; if Phase A SCO is absent, CSCO must produce a combined Phase A+B SCO |
| Architecture Vision (AV) | SA — architecture-repository/architecture-vision/ | Baselined at version 1.0.0 | Cross-reference for consistency between BA capabilities and AV capability overview |
| Requirements Register (RR) | PO — project-repository/ | At least draft (0.x.x acceptable) | Used to identify safety-relevant requirements that the BA must address |
| sprint.started event | PM | Must be emitted for Phase B sprint | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- The STAMP Level 1 control structure from SCO Phase A: which system-level control actions and controllers have already been identified.
- The business process vocabulary of the engagement domain: what constitutes a safe vs. unsafe execution of a business process in this domain (e.g., for healthcare: medication dosage calculation, patient record update; for finance: transaction authorisation, balance calculation).
- The BA artifact schema: Business Process Catalog, Business Capability Map, Value Stream Map, Business Services Catalog — CSCO must know what to look for in each.
- The STAMP/STPA Level 1 UCA analysis procedure per `skills/stamp-stpa-methodology.md §Steps 4–5`.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Safety-relevant business processes not described in the BA | Yes if the process is safety-critical; no if CSCO can infer process intent from capability names | SA (BA revision) | SCO §6 (Control Structure — business level), §7 (UCAs) |
| Owner and authorisation rules for safety-relevant business processes | No — CSCO can proceed with process-level UCA analysis without knowing the exact access control model (that is Phase C/D) | SA or PO | SCO §7 (UCAs — specific context conditions) |
| Regulatory process requirements (e.g., four-eyes principle for financial approval processes) | Yes if compliance checklist is being produced; no if CSCO infers from regulatory domain already identified | User (via PM) or enterprise-repository/standards/ | SCO §9 (Compliance Requirements — process obligations) |

### Clarification Triggers

CSCO raises a CQ when:

1. **Business process is safety-relevant but insufficiently described:** The BA names a business process that appears safety-critical (e.g., "medical record update", "payment authorisation") but provides insufficient detail about the process steps, actors, and error conditions for CSCO to perform UCA analysis. CSCO raises a CQ to SA requesting process detail sufficient for UCA analysis.
2. **Regulatory process obligation identified but not reflected in BA:** CSCO identifies a process-level regulatory requirement (e.g., audit log obligation, segregation of duties, approval workflow) that is not reflected in any BA process or business service. CSCO raises a CQ to SA and PO requesting that the process be added to the BA or the omission be explicitly documented as a design decision.
3. **Capability introduced in BA that is not in AV scope:** The BA introduces a business capability not present in the AV capability overview. CSCO raises a CQ to SA to confirm whether this is an intentional scope extension (requiring an AV revision) or an error.

---

## Steps

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`:

1. **Layer 1 — Engagement State:** Read the current BA from architecture-repository/business-architecture/; read SCO Phase A baseline from safety-repository/safety-constraint-overlay/; read AV from architecture-repository/architecture-vision/ (for scope cross-reference); read RR if available from project-repository/; read clarification-log/ (any open safety-relevant CQs); read handoff-log/ (SA handoff requesting CSCO BA review); read algedonic-log/ (any open ALG signals affecting Phase B scope).
2. **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for any process-level regulatory standards (SOX segregation of duties, GDPR processing obligations, HIPAA treatment workflow requirements, etc.).
3. **Layer 3 — External Sources:** Check external-sources/ for any configured sources with process-level safety or compliance requirements.
4. **Layer 4 — Target Repository:** If target-repo is configured, check for existing business process documentation, Standard Operating Procedures, or compliance procedures that may describe safety-relevant process requirements.
5. **Layer 5 — Inference:** Annotate all inferred fields with `[inferred — source: domain knowledge — <domain>]`.

---

### Step 1 — Confirm Gate Readiness

1. Confirm `artifact.baselined` has been emitted for BA version 1.0.0. If BA is at 0.x.x: do not cast formal gate vote. Provide informal guidance; await 1.0.0 baseline.
2. Confirm SCO Phase A baseline exists at 1.0.0. If absent: CSCO must produce a combined SCO Phase A+B before proceeding (apply CSCO-GATE-A procedure for Phase A, then continue with this skill's Steps 3 onward).
3. Check for revisit trigger (`trigger="revisit"`, `phase_visit_count > 1`). If revisit: proceed to Step 8 (revisit handling) instead of Steps 2–7.
4. Load the CSCO-STAMP-STPA methodology reference (`skills/stamp-stpa-methodology.md`).

---

### Step 2 — Read Business Architecture in Full

Read the BA document from `architecture-repository/business-architecture/ba-1.0.0.md`:

- **Business Capability Map:** Identify which capabilities are safety-relevant (process data, control physical systems, serve regulated stakeholders, handle sensitive information).
- **Business Process Catalog:** Read each defined process. For each process: note the actors (roles), process steps, inputs, outputs, error conditions (if described), and the business capability it realises.
- **Value Stream Map:** Note value streams where a process failure would affect the end customer directly (safety-relevant value streams are those where a failure leads to a direct stakeholder harm).
- **Business Services Catalog:** Note all business services that provide safety-relevant functionality.
- **Motivation Architecture:** Note any business goals or drivers that create incentives that could conflict with safety constraints (e.g., a goal of "maximise processing speed" may conflict with SC-nnn requirements for validation steps).
- **Organisational Model:** Note roles with authority over safety-relevant processes — these become controllers in the Level 1 control structure.

---

### Step 3 — Perform STAMP Level 1 Analysis Update — Business Process UCAs

Using the existing SCO Phase A §6 (Control Structure) as the starting point, extend the control structure to include business-process-level control relationships identified in the BA:

**3a. Extend Control Structure (SCO §6 update):**

For each safety-relevant business process identified in Step 2:
- Identify the controller (role or system that initiates or controls the process).
- Identify the controlled process (the business activity being controlled).
- Identify the control actions (the commands, approvals, or data inputs the controller uses to direct the process).
- Identify the feedback channels (how the controller knows the process has executed correctly: confirmation messages, audit logs, status indicators).
- Add each new controller→process relationship to SCO §6 Control Structure table.

**3b. Identify Process-Level UCAs (SCO §7 update):**

For each new control action added in 3a: apply all four UCA types from `skills/stamp-stpa-methodology.md §Steps 5`:

| UCA Type | Business Process Example |
|---|---|
| Not Provided | An approval step in a regulated process is skipped because the controller assumes a prior actor already approved |
| Provided When Not Needed | A data deletion action is triggered on records that are still within a legally mandated retention period |
| Provided Too Early / Too Late | A compliance report is submitted before all transactions for the period are processed; or after a regulatory deadline |
| Applied Too Long / Stopped Too Soon | A data validation step is terminated before all records are validated due to a timeout condition |

For each UCA identified: author a UCA-nnn record per `skills/stamp-stpa-methodology.md UCA format`. Link each UCA to the H-nnn hazard it activates and the L-nnn loss it contributes to.

**3c. Identify New Safety Constraints Required (SCO §5 update):**

For each new UCA where no existing SC-nnn constraint prevents the unsafe action: author a new SC-nnn constraint. Phase B constraints are Architectural type (they specify process design requirements) or Regulatory type (mandatory process obligations from regulatory standards). Technical constraints are not introduced at Phase B.

---

### Step 4 — Review BA Against Updated SCO

With the SCO Phase B update drafted, cross-reference the BA against all applicable SC-nnn constraints:

**For each SC-nnn constraint that applies to the business layer:**
- Determine whether the BA process design satisfies the constraint.
- Flag violations using the same three types as Phase A (Type A: direct conflict; Type B: missing coverage; Type C: wrong abstraction level).

**Specific Phase B checks:**

1. **Segregation of duties:** Where a regulatory standard (SOX, GDPR, ISO 27001) requires segregation of duties for a process, verify the BA organisational model reflects separate roles for each segregated function.
2. **Audit trail requirements:** Where a regulatory or SCO constraint requires an audit trail for a business process, verify the BA Business Process Catalog includes an audit/logging step.
3. **Approval workflow requirements:** Where a process involves a safety-relevant decision (e.g., record deletion, access grant, payment release), verify the BA describes an approval step and identifies the approving role.
4. **Error handling coverage:** For every safety-relevant process, check whether the BA describes what happens when the process encounters an error, rejection, or exception. Missing error handling in safety-relevant processes is a Violation Type B finding.
5. **Incentive conflicts:** If the BA includes business goals or performance targets (from Motivation Architecture), check whether any goal creates an incentive to bypass or shorten a safety-relevant process step. Flag incentive conflicts as Violation Type A.

For each violation: produce a structured feedback item with constraint ID, violation type, BA section and content, and required revision.

---

### Step 5 — Produce Loss Scenario Update

For each new UCA in SCO §7: author LS-nnn loss scenarios per `skills/stamp-stpa-methodology.md §Step 6`:

- Identify causal factors at the business process level: process design gaps, missing approval steps, unclear roles, conflicting incentives, delayed feedback channels.
- For each loss scenario without an existing SC-nnn constraint: add a new constraint in SCO §5.

---

### Step 6 — Update SCO with Phase B Content

Update the SCO document to produce `sco-B-0.1.0.md` (draft):

- §5: Add new SC-nnn constraints from Steps 3c and 5. Retain all Phase A constraints verbatim.
- §6: Add new control structure entries from Step 3a. Retain all Phase A control structure entries.
- §7: Add new UCA-nnn records from Step 3b. Retain all Phase A UCAs.
- §8: Add new LS-nnn loss scenarios from Step 5. Retain all Phase A loss scenarios.
- §9: Update compliance requirements for any process-level regulatory obligations identified.
- §10: Update open safety findings — add new findings from Step 4 review; close findings from Phase A that have been addressed in the BA.
- §11: Add Phase B gate summary (to be completed when gate vote is cast).

---

### Step 7 — Cast B→C Gate Vote

**Approve** if: all Violation Type A findings from Step 4 are resolved (via SA revision or user risk acceptance), SCO Phase B update is complete with at least one constraint per new UCA identified, and no blocking SF-nnn items remain in SCO §10 that are attributable to the BA.

**Conditional** if: Violation Type B findings exist (missing process coverage in areas not yet designed), but no Violation Type A conflicts are present. Specify: the coverage gap, the Phase C artifact (AA or DA) where coverage is expected, and the sprint deadline.

**Veto** if: one or more Violation Type A conflicts remain after SA revision (Iteration 1 feedback not resolved). Cite the specific SC-nnn violated and the exact BA content that violates it. Provide the minimal revision required.

Emit `gate.vote_cast` for B→C gate. If approve or conditional: promote SCO Phase B to `sco-B-1.0.0.md`. Emit `artifact.baselined` for SCO Phase B update.

Produce Gate Record `safety-repository/gate-records/gr-B-C-1.0.0.md`. Emit `artifact.baselined` for Gate Record. Emit `handoff.created` to PM with gate vote status and any conditional requirements. Emit `handoff.created` to SA with structured feedback items from Step 4.

---

### Step 8 — Revisit Handling (trigger="revisit" only)

If `trigger="revisit"` and `phase_visit_count > 1`:

1. Read the EventStore gate history to identify which BA sections changed.
2. Read the prior SCO Phase B version.
3. Apply Steps 2–6 only to the changed BA sections and their safety implications.
4. Update only SCO constraints, UCAs, and loss scenarios affected by the changes. Preserve all non-affected content verbatim.
5. Increment SCO version (minor for draft, major for new baseline).
6. Re-cast the B→C gate vote. Earlier gate votes do not need to be re-cast unless the safety classification changed.

---

## Feedback Loop

**Maximum iterations: 2.** After Iteration 2 without resolution: raise ALG-010 (inter-agent deadlock) to PM.

**Iteration 1:** CSCO emits `gate.vote_cast (veto)` with specific SC-nnn reference and structured feedback items. SA revises BA and re-baselines. SA emits `artifact.baselined` for revised BA.

**Iteration 2:** CSCO reviews only the sections SA revised. If all Violation Type A findings resolved: approve. If any remain: cast second veto.

**Termination conditions:**
- **Satisfied:** All Violation Type A findings resolved. CSCO emits `gate.vote_cast (approve)`. Loop closes.
- **User risk acceptance:** User explicitly accepts residual risks. CSCO updates SCO §10. CSCO emits `gate.vote_cast (approve with accepted residuals)`. Loop closes.
- **Deadlock (ALG-010):** After Iteration 2 with Violation Type A unresolved. PM adjudicates; CSCO veto stands during adjudication.

### Personality-Aware Conflict Engagement

**CSCO ↔ SA (business process safety gate):**

SA may argue that a business process constraint identified by CSCO is implementation detail that does not belong in the Business Architecture. CSCO's stance: if the constraint governs *how* a business process must be structured (approval steps, segregation of duties, audit obligations) it is a valid business architecture constraint — it constrains the process design, not the technology implementation. CSCO distinguishes clearly between process-level constraints (Phase B) and technical implementation constraints (Phase C/D). If SA identifies a CSCO constraint that genuinely belongs at a later phase, CSCO relocates it (updates the SC-nnn phase field) and withdraws the Phase B finding — CSCO does not maintain incorrect phase assignments.

**CSCO ↔ PM (delivery pressure):**

PM may argue that business architecture review is holding up Phase C. CSCO's engagement: CSCO completes the BA review within one sprint of BA baselinement. If a Violation Type A finding exists, CSCO provides the minimal revision path — not a comprehensive BA redesign. For Violation Type B findings: CSCO issues a conditional approval, not a veto, allowing Phase C to begin while the coverage gap is tracked for Phase C.

**CSCO ↔ PO (process scope):**

PO may argue that certain business processes are outside the system's scope and therefore not subject to safety analysis. CSCO's engagement: CSCO reviews the scope boundary in AV §3.2 and the safety boundary in SCO §1. If a process is genuinely outside the agreed scope boundary, CSCO notes this and does not raise a finding. If a process appears to have been informally excluded from scope to avoid a safety constraint: CSCO flags the scope exclusion as a finding for PM and user review.

---

## Algedonic Triggers

- **ALG-001 (S1 — Safety-Critical):** A business process in the BA introduces a hazard that cannot be controlled within the proposed architecture approach — for example, a process that requires a human actor to make a safety-critical decision without any described validation, approval, or audit mechanism, and where no feasible control mechanism can be added at the process design level. Raised immediately with concurrent escalation to CSCO (self) and PM. Phase C does not begin until the process design is revised.
- **ALG-010 (S3 — Inter-Agent Deadlock):** After two iterations, CSCO and SA cannot agree on whether a process-level safety constraint is valid or whether a process design satisfies the constraint. Raised to PM for adjudication.

---

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Safety Constraint Overlay — Phase B Update | `SCO-B-1.0.0` | `safety-repository/safety-constraint-overlay/sco-B-1.0.0.md` | `artifact.baselined` |
| STAMP/STPA Analysis — Phase B Update | `sa-001-B.md` | `safety-repository/stamp-stpa/sa-001-B.md` | `artifact.baselined` |
| Gate Record — B→C | `GR-B-C-1.0.0` | `safety-repository/gate-records/gr-B-C-1.0.0.md` | `artifact.baselined` |
| Gate Vote — B→C | (event payload) | EventStore | `gate.vote_cast` |
| Structured feedback to SA | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` |

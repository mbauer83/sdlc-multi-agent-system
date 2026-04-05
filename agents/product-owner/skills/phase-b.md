---
skill-id: PO-PHASE-B
agent: PO
name: phase-b
display-name: Phase B — Business Architecture Consultation and RTM Update
invoke-when: >
  Phase B Business Architecture Sprint starts (sprint.started emitted with phase=B) and the
  Architecture Vision artifact is baselined at version 1.0.0. Also invoked when SA has produced
  a BA draft (handoff.created from SA to PO) and PO's consulting review is required before
  Phase B gate. Invoked on revisit when trigger=revisit and phase_visit_count > 1 for Phase B.
trigger-phases: [B]
trigger-conditions:
  - sprint.started (phase=B)
  - handoff.created (from SA with BA draft for PO consulting review)
  - cq.answered (blocking Phase B requirements CQs resolved)
  - artifact.baselined (SA — AV at version 1.0.0, confirming Phase A gate passed)
entry-points: [EP-0, EP-A, EP-B]
primary-outputs: [RTM v0.2.0 (Phase B traceability entries), BA feedback record, updated RR (if gaps found)]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase B — Business Architecture Consultation and RTM Update

**Agent:** Product Owner  
**Version:** 1.0.0  
**Phase:** B — Business Architecture  
**Skill Type:** Phase consulting — traceability review and RTM update  
**Framework References:** `agile-adm-cadence.md §6.3`, `framework/artifact-schemas/requirements-register.schema.md`, `raci-matrix.md §3.3`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint


Representation choice (balanced and mandatory):
- Use `.puml` diagrams when flow, topology, sequence, trust boundaries, or interaction context is the primary concern.
- Use matrix artifacts (`model_create_matrix`) for dense many-to-many mappings, coverage, and traceability where node-link readability degrades.
- Do not replace contextual architecture views with matrices alone: keep a reasonable set of diagrams that preserves end-to-end context for the domain slice.
- Practical threshold: if a single node-link view would exceed about 25 elements or become edge-dense, keep/author at least one contextual diagram and shift dense cross-reference detail to a matrix.

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| `sprint.started` event (phase=B) | PM | Must be emitted before PO begins Phase B work | Hard prerequisite |
| Architecture Vision (`AV`) | SA | Version 1.0.0 (baselined — Phase A gate passed) | Blocking — PO cannot begin Phase B RTM work without confirmed capability clusters (AV §3.5) and business drivers (AV §3.4) |
| Business Architecture (`BA`) draft | SA | Draft acceptable (0.x.x); PO reviews during production, not only at baseline | Not blocking on sprint start; PO begins reading BA sections as SA produces them; final RTM entries at BA 1.0.0 |
| Requirements Register (`RR`) | PO (self-produced) | Version 1.0.0 (baselined at Phase A gate) | Blocking — RTM update requires a complete RR to cross-reference |
| RTM Skeleton | PO (self-produced) | Version 0.1.0 (from Phase A) | PO updates the existing skeleton with Phase B traceability entries |
| Safety Constraint Overlay (`SCO`) Phase A update | CSCO | Draft acceptable; absence is not blocking for PO's RTM work | PO reads SCO to identify safety-type requirements that may have been added post-Phase A |

---

## Knowledge Adequacy Check

### Required Knowledge

- Business Architecture structure: which capability elements (CAP-nnn), process elements (PRO-nnn), and value streams (VS-nnn) SA has defined in Phase B. PO must understand the BA identifier scheme to produce meaningful RTM entries.
- The complete RR at version 1.0.0 — which requirements exist, their types, and their current traceability status.
- The AV capability cluster overview (AV §3.5) — confirms the strategic-level mapping between requirements and BA capabilities.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Section Affected |
|---|---|---|---|
| BA identifier scheme for capabilities (CAP-nnn) and processes (PRO-nnn) | Yes, for RTM BA column | SA | RTM — BA column |
| Whether SA's BA covers all functional areas implied by the RR | No — PO identifies coverage gaps and flags them | SA | RR — gap additions; RTM — untraceable requirements |
| Whether SA's BA introduces capabilities with no backing requirement in the RR | No — PO flags reverse gaps; these are non-blocking unless they represent significant scope changes | PM | RR — potential additions |

### Clarification Triggers

PO raises a CQ when:

1. **BA identifier scheme not established:** SA has not published the identifier scheme for CAP-nnn and PRO-nnn elements. PO cannot complete the RTM BA column without this. Blocking — raises CQ to SA.
2. **BA capability with no traceable requirement:** SA's BA includes a capability with no corresponding requirement in the RR. Non-blocking — PO flags to PM and SA via feedback record. If the capability represents significant new scope, PM decides whether to treat it as a requirements addition (raise CQ to user) or an architecture excess (SA removes capability).
3. **RR requirement with no BA capability:** A Must-priority requirement in the RR has no corresponding capability in SA's BA after BA baseline. Blocking for Phase B gate — PO raises CQ to SA requesting explicit capability mapping or confirmation that the requirement is addressed at a later architecture phase.

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PO", phase="B", artifact_type="business-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/work-repositories/architecture-repository/business-architecture/` — BA artifacts being produced by SA (read progressively as SA produces sections)
- `engagements/<id>/work-repositories/architecture-repository/architecture-vision/` — AV at version 1.0.0 (capability clusters, business drivers, stakeholder register)
- `engagements/<id>/work-repositories/project-repository/requirements/` — current RR (1.0.0) and RTM skeleton (0.1.0)
- `engagements/<id>/work-repositories/safety-repository/` — SCO Phase A update (for safety requirements not yet in RR)
- `engagements/<id>/clarification-log/` — open CQs from Phase A that may affect Phase B RR content
- External sources (if configured): business process repositories, capability registries, Jira epics that correspond to business capabilities

**Pre-existing artifacts that may reduce CQ load:**

- AV §3.5 Capability Clusters → maps to BA CAP-nnn elements (Phase B elaborates these)
- AV §3.4 Business Drivers → maps to RR requirements that the BA capabilities must satisfy
- SCO Phase A update → maps to Safety-type requirements in the RR

---

### Step 1 — Read the Business Architecture

Read the BA draft from `architecture-repository/business-architecture/`. If the BA is being produced progressively (SA has completed some sections but not all), read what is available. Record the sections reviewed and their version numbers in the internal Gap Assessment.

Key BA sections to read for PO's consulting role:

- **Business Capability Map (§3.2):** List of all CAP-nnn capabilities. For each capability, note its name, description, classification (Core/Supporting/Commodity), and linkage to AV capability clusters.
- **Business Process Catalog (§3.3):** List of all BPR-nnn processes. For each process, note which business services it realizes and which stakeholders/roles are assigned to it.
- **Value Stream Map (§3.4):** Value streams identify how the system delivers stakeholder-facing value. Each VS-nnn must have named stages. Cross-reference each stage against the PO's Value Scenarios — every stage should correspond to at least one value scenario and at least one BSV. Flag stages with no BSV as BA gaps to SA.
- **Motivation Architecture (§3.7):** Goals, principles, and drivers. Confirm that every DRV-nnn business driver from the AV is reflected in the BA's motivation architecture. Gaps mean a driver has been dropped from the architecture — flag to SA.
- **Business Services Catalog (§3.8):** Services the business provides. Cross-reference against functional requirements in the RR — each Must-priority functional requirement should be addressable by at least one business service.

---

### Step 2 — Forward Cross-Reference: RR Requirements Against BA

For each requirement in the RR (all Active requirements):

1. Identify which BA element(s) address the requirement:
   - **Functional requirements:** Map to business services (BSV-nnn) and/or processes (BPR-nnn) that implement the function. Capability (CAP-nnn) mappings are supporting cross-references, not primary anchors.
   - **Non-Functional requirements:** Map to capabilities or processes where the quality attribute must be enforced. If a non-functional requirement applies system-wide, map it to all capabilities (mark as `system-wide` in the RTM).
   - **Constraint requirements:** Map to the capability or process that is constrained. If a constraint applies globally (e.g., EU data residency), map it to all data-handling capabilities.
   - **Safety requirements:** Map to the capability, process, or interface where the safety constraint applies.

2. For each mapping found: record in the RTM BA column as:
   - `●` (primary satisfaction) if the BA element is the primary vehicle through which the requirement is addressed.
   - `○` (partial/contributing) if the BA element partially contributes but does not fully address the requirement.

3. For each requirement with NO mapping found after reading the complete BA: mark status as `Untraceable (Phase B)`. This is a gap that must be flagged to SA.

---

### Step 3 — Reverse Cross-Reference: BA Capabilities Against RR

For each capability (CAP-nnn) and process (PRO-nnn) in the SA's Business Architecture:

1. Identify which requirement(s) in the RR justify this capability or process.
2. If a capability has at least one `●` requirement in the RR: it is requirements-backed. No action needed.
3. If a capability has only `○` requirements in the RR: flag as `weakly backed` in the internal Gap Assessment. Non-blocking for Phase B gate, but PO notes this in the feedback record to SA as a design risk (a capability with weak requirements backing may be over-engineering).
4. If a capability has NO requirement in the RR — no `●` and no `○`: flag as `unreferenced capability`. This may indicate:
   - A missing requirement: there is a real business need for this capability but PO has not captured it. PO adds the requirement to the RR with `phase-elicited: B` and `source: SA-BA-review`. Assign next RQ-nnn ID.
   - An architecture excess: SA has designed a capability that exceeds the stated requirements scope. PO flags to PM and SA. PM decides whether to extend scope (requires user CQ) or request SA to remove the capability from the BA.

---

### Step 4 — Update the RTM with Phase B Traceability Entries

Produce `project-repository/requirements/rtm-0.2.0.md` by updating the RTM skeleton:

1. For each RQ-nnn: populate the `BA` column with the CAP-nnn and PRO-nnn identifiers found in Steps 2–3, using `●` and `○` symbols per the schema.
2. Update the `Status` column:
   - `Traced` — at least one `●` entry in the BA column.
   - `Partially Traced` — only `○` entries in the BA column; no primary satisfaction element identified.
   - `Untraceable` — no BA column entries after Phase B review.
3. Add new requirements identified in Step 3 (reverse cross-reference additions) to the RTM as new rows with `phase-elicited: B`.
4. Emit `artifact.baselined` for RTM at version 0.2.0.

---

### Step 5 — Produce BA Feedback Record and Submit to SA

Produce the feedback record to SA:

**Feedback record structure** (written to `engagements/<id>/handoff-log/` as part of the handoff payload):

1. **Confirmed mappings:** List of requirements confirmed as traced to BA elements. No action needed from SA.
2. **Traceability gaps (forward):** Requirements in the RR with no BA element. For each gap: RQ-nnn, requirement title, requirement type, priority. PO's proposed resolution: "Does this requirement map to an existing capability that was not identified in Step 2? If so, provide the CAP-nnn reference. If not, this is a Phase B architecture gap."
3. **Unreferenced capabilities (reverse):** BA elements with no RR backing. For each: CAP-nnn or PRO-nnn, name, proposed disposition (add requirement, or confirm as excess scope for PM decision).
4. **Value stream coverage check:** For each value stream in the BA, confirm whether a corresponding Value Scenario exists in the Business Scenarios artifact. Flag value streams with no Value Scenario as a potential business communication gap.
5. **Weakly backed capabilities:** Capabilities with only `○` requirements. Listed for SA's awareness; not a blocking concern.

Create handoff to SA:
```
handoff-type: consulting-feedback
from: product-owner
to: solution-architect
artifact-id: BA-<engagement-id>
artifact-type: ba-requirements-feedback
purpose: RTM traceability gaps and reverse coverage check; PO requires SA response before
         Phase B gate; gaps must be resolved or formally risk-accepted
required-by: Phase B gate
```
Emit `handoff.created`.

Also submit RTM status report to PM:
```
handoff-type: status-report
from: product-owner
to: project-manager
artifact-id: RTM-<engagement-id>
artifact-version: 0.2.0
summary: [count] requirements traced, [count] partially traced, [count] untraceable
```
Emit `handoff.created`.

---

### Step 6 — Raise CQs for Remaining Gaps

After SA responds to the feedback record (Feedback Loop, Iteration 1):

For any traceability gaps that SA has not resolved through BA revision or capability mapping clarification, raise CQs:

- **Missing BA coverage for Must-priority requirements:** Raise CQ to SA requesting a specific resolution. If SA cannot address the gap within the current Phase B sprint scope: raise CQ to PM to determine whether (a) the requirement is deferred to Phase C or D, or (b) Phase B scope is extended, or (c) the requirement is formally risk-accepted as untraceable pending Phase C.
- **Unreferenced capability requiring user scope decision:** If SA confirms the capability is intentional and PO cannot trace it to any existing requirement, raise CQ to user (via PM): "SA's Business Architecture includes [capability name]. Is this within the intended scope of the engagement? If yes, PO will add a corresponding requirement to the RR."

---

### Step 7 — Final RTM Update and Phase B Gate Acknowledgement

Once SA has responded to feedback and all resolvable gaps have been resolved:

1. Update RTM to final Phase B version: incorporate any additional traceability entries from SA's response.
2. Confirm all Must-priority requirements have `●` entries in the BA column, or are explicitly documented as `risk-accepted` with PM approval.
3. Emit `artifact.baselined` for RTM at the final Phase B version.
4. Emit status update to PM: "PO Phase B consulting complete. RTM Phase B traceability complete. [count] untraceable Must-priority requirements remain — [list with disposition]."

**PO Phase B gate consultation checklist:**
- [ ] All Must-priority requirements have at least one `●` in the RTM BA column, or are explicitly risk-accepted.
- [ ] All unreferenced BA capabilities have been either traced to a new RR requirement or flagged to PM for scope decision.
- [ ] RTM version 0.2.x is baselined and accessible to SA for architecture column reference.
- [ ] All CQs raised in this phase are documented and tracked.

---

### Phase Revisit Handling

On `trigger="revisit"` and `phase_visit_count > 1` for Phase B:

1. Read the EventStore gate history to identify the triggering change (requirements change, Phase H return, SA BA revision).
2. Read the existing RTM at its current version. Identify which RTM entries are affected by the triggering change (which RQ-nnn rows correspond to the changed requirements or changed BA elements).
3. Scope the revisit: only the affected RTM rows and their corresponding BA elements are in scope. Do not re-review the entire BA if only a subset has changed.
4. Re-execute Steps 2–6 for the affected scope only. Preserve all non-affected RTM entries and their traceability status.
5. Increment RTM version (patch increment for minor changes; minor increment for scope additions).
6. Emit `artifact.baselined` for the updated RTM version.

---

## Feedback Loop

### BA Traceability Gap Resolution Loop (PO ↔ SA)

- **Iteration 1:** PO submits the BA feedback record (Step 5) to SA via `handoff.created`. SA reviews; either provides CAP-nnn/PRO-nnn references for flagged gaps, revises the BA to address missing requirements coverage, or explains why a gap is intentional (with a specific architecture rationale).
- **Iteration 2:** If gaps remain after SA's Iteration 1 response: PO reviews SA's response. For gaps that SA has not addressed with a specific architecture rationale: PO restates the gap with the specific requirement title, priority, and the user/business value it represents. SA must either resolve or formally escalate to PM.
- **Termination conditions:**
  - All Must-priority requirements are traced to BA elements (RTM BA column populated with at least one `●`), OR
  - Remaining gaps are formally documented as untraceable with PM-approved risk acceptance, OR
  - A CQ is jointly raised to the user for requirements scope confirmation.
- **Maximum iterations:** 2.
- **Escalation if unresolved after 2 iterations:** Raise `ALG-010` to PM. Document both positions (SA's architecture rationale for the gap, PO's requirements value statement) in the RTM as an open conflict. PM adjudicates.

### Personality-Aware Conflict Engagement

(Applicable when SA's response to PO's feedback record does not provide a specific BA element mapping for Must-priority requirements, or when SA asserts a requirement is out of Phase B scope without a specific rationale.)

**Expected tension in this skill's context:** PO ↔ SA tension in Phase B is lower than in Phase A but still significant. SA has the authority to define the BA structure; PO has the authority to declare what is required. If SA's BA does not cover a Must-priority requirement, this is either a genuine architecture gap (SA must address it) or a requirements framing issue (PO must refine the requirement). The two agents must distinguish between these cases.

**Engagement directive — how PO surfaces the conflict:**

When SA responds to a traceability gap feedback item by asserting "this requirement is out of Phase B scope" or "this requirement will be addressed in Phase C":

1. PO asks: "Which architecture phase and which artifact is responsible for addressing RQ-nnn? I need a specific artifact reference, not a phase label." An assertion that something is "a Phase C concern" without a specific artifact reference is not a resolution.
2. PO states the priority and value: "RQ-nnn is a Must-priority requirement addressing [STK-nnn]'s need for [outcome]. If it is not covered in the BA, the BA is incomplete at a business level. This has implications for the Phase B gate."
3. If SA provides a specific artifact reference (e.g., "RQ-042 will be addressed in the Application Architecture — APP-nnn"): PO accepts the deferral and marks the RTM entry as `Deferred to Phase C — APP-nnn` in the BA column. This is a resolved state.

**Resolution directive:**

A conflict is resolved when:
- SA provides a specific CAP-nnn, PRO-nnn mapping for the requirement (requirement is traced), OR
- SA provides a specific Phase C or D artifact reference for the requirement (requirement is deferred with a named artifact target), OR
- PM approves risk acceptance for the untraceable requirement, OR
- Both agents agree the requirement needs user validation (joint CQ raised).

A conflict is NOT resolved by SA asserting scope exclusion without a specific artifact reference, or by PO accepting a vague deferral.

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
| ALG-010 | PO ↔ SA feedback loop has been exhausted (2 iterations) and one or more Must-priority requirements remain untraceable in the BA with no agreed resolution | S3 | Emit `alg.raised`; PM adjudicates; document both positions in the RTM; Phase B gate blocked until PM adjudicates |
| ALG-006 | Multiple Must-priority requirements are untraceable and the Phase B gate deadline is at risk, creating a cascade threat to Phase C planning | S2 | Emit `alg.raised`; PM restructures sprint plan; PO and SA prioritise resolution of the most business-critical gaps |
| ALG-008 | PO identifies that SA has baselined the BA (version 1.0.0) while one or more Must-priority requirements flagged by PO in the feedback record remain explicitly unresolved and unacknowledged | S2 | Emit `alg.raised`; PM notified; PM invalidates the gate passage until SA addresses the open feedback items |
| ALG-016 | A blocking CQ to the user about requirements scope (raised because a BA capability has no RR backing and user scope confirmation is needed) has been open for more than 2 sprint cycles with no response | S2 | Emit `alg.raised`; PM consolidates open CQs and escalates to user |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Requirements Traceability Matrix — Phase B update (`RTM`) | `project-repository/requirements/rtm-<version>.md` | 0.2.0 (Phase B traceability entries added) | `artifact.baselined` |
| Updated Requirements Register (`RR`) | `project-repository/requirements/rr-<version>.md` | 1.x.0 (if new requirements added from reverse cross-reference) | `artifact.baselined` |
| BA Consulting Feedback Record | `engagements/<id>/handoff-log/` (payload of handoff to SA) | — | `handoff.created` |
| Phase B Status Report to PM | `engagements/<id>/handoff-log/` | — | `handoff.created` |

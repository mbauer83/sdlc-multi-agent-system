---
skill-id: PO-PHASE-H
agent: PO
name: phase-h
display-name: Phase H — Requirements Impact Assessment
invoke-when: >
  Phase H Architecture Change Management is active (sprint.started with phase=H emitted) and PM
  has issued a Change Record (CR) to PO via handoff.created. Also invoked when SA's Change Record
  assessment identifies requirements-layer impacts and requests PO's requirements update. Invoked
  at entry point EP-H when PO must assess requirements impact of an externally initiated change.
trigger-phases: [H]
trigger-conditions:
  - sprint.started (phase=H)
  - handoff.created (from PM with Change Record or SA change impact summary)
  - cq.answered (blocking Phase H requirements CQs resolved)
entry-points: [EP-H]
primary-outputs: [Updated RR (change-driven), Updated RTM (under-review links), Stakeholder change notification]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase H — Requirements Impact Assessment

**Agent:** Product Owner  
**Version:** 1.0.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Phase primary — requirements impact assessment and RR update  
**Framework References:** `agile-adm-cadence.md §6.8`, `framework/artifact-schemas/requirements-register.schema.md`, `framework/artifact-schemas/change-record.schema.md`, `raci-matrix.md §3.8`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md §4.7`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| `sprint.started` event (phase=H) | PM | Must be emitted before PO begins Phase H work | Hard prerequisite |
| Change Record (`CR`) | PM (forwarding SA's CR, or PM's Warm-Start CR from change intake) | At least draft (0.1.0); PM-issued change classification must be present | Blocking — PO cannot assess requirements impact without knowing what is changing |
| Change classification | PM | One of: Minor / Significant / Major / Safety-Critical | Determines the scope of PO's impact assessment and whether CSCO must be consulted |
| Current Requirements Register (`RR`) | PO (self-maintained) | Latest baselined version | Blocking — PO must read the current RR before identifying which requirements are affected |
| Current RTM | PO (self-maintained) | Latest baselined version | Blocking — PO must read the current RTM to identify which traceability links are affected by the change |
| SA change impact summary (if available) | SA | Draft acceptable | SA may have already identified which architecture artifacts are affected; this helps PO scope the requirements impact |
| Safety Constraint Overlay (`SCO`) latest update | CSCO | Latest available version | Non-blocking for initial assessment; required before PO can confirm safety-type requirements impact |

---

## Knowledge Adequacy Check

### Required Knowledge

- The full content of the Change Record: what is changing, what is being added or removed, what is the business rationale for the change.
- The current RR: all Active requirements and their current traceability status.
- The current RTM: which requirements map to which architecture elements (to identify which requirements are transitively affected by architecture changes).
- The change classification: Minor, Significant, Major, or Safety-Critical — determines depth of impact assessment required.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Section Affected |
|---|---|---|---|
| Which architecture artifacts are affected by the change (if SA's impact summary is not yet available) | Partially blocking — PO can assess direct requirements impact; transitive architectural impact requires SA's list | SA | RTM — under-review marking scope |
| Whether the change introduces entirely new functional scope | Yes, for determining whether user validation is needed | User (via PM) | RR — new requirements section |
| Stakeholder impact: which stakeholders are affected by the change | No — PO can infer from source stakeholder attribution in RR | PM / Stakeholder Register | Stakeholder communication record |

### Clarification Triggers

PO raises a CQ when:

1. **Change introduces new functional scope not captured in the CR:** The Change Record describes an architectural change but the PO identifies functional capabilities implied by the change that are not described in the CR. Blocking — PO cannot assess requirements impact on scope it cannot read. Raises CQ to PM/SA for CR elaboration.
2. **Change retires a Must-priority requirement with no stated user approval:** The Change Record removes a capability that satisfies a Must-priority requirement. Non-blocking for impact assessment; blocking for RR update. PO raises CQ to user (via PM): "Change CR-nnn removes [capability]. This satisfies requirement RQ-nnn (Must priority, attributed to STK-nnn). Do you accept this requirement change?"
3. **Safety-type requirement affected by a non-Safety-Critical change:** PO identifies a Safety-type requirement in the RR that is affected by the change, but the change is classified as Minor or Significant (not Safety-Critical). PO escalates classification question to PM and CSCO: "The change affects RQ-nnn (Safety type). Should the change be reclassified as Safety-Critical?"

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PO", phase="H", artifact_type="change-record")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/work-repositories/project-repository/requirements/` — current RR and RTM at latest baselined versions
- `engagements/<id>/work-repositories/architecture-repository/change-records/` — the CR issued by SA/PM
- `engagements/<id>/work-repositories/architecture-repository/` — all architecture artifacts referenced in the CR (AV, BA, AA, DA) to understand what is changing
- `engagements/<id>/work-repositories/safety-repository/` — SCO latest update (for safety-type requirements cross-reference)
- `engagements/<id>/clarification-log/` — open CQs; confirms whether the change may resolve previously open CQs
- `engagements/<id>/handoff-log/` — SA's change impact summary and PM's change classification decision
- External sources (if configured): change request systems, incident records, improvement tickets

**Pre-existing artifacts that may reduce CQ load:**

- SA's Change Impact Assessment (in the CR) → maps architecture-layer changes to affected artifacts, which implies requirements-layer impacts
- Current RTM → maps architecture elements to requirements; any architecture element changed in the CR has corresponding RTM traceability links that must be reviewed
- Current RR →  identifies all requirements, their status, and their current traceability

---

### Step 1 — Read and Interpret the Change Record

Read the Change Record in full. Extract:

1. **Change description:** What is changing — which capabilities, processes, components, or interfaces are being added, modified, or removed?
2. **Change classification:** Minor / Significant / Major / Safety-Critical (PM-assigned per `agile-adm-cadence.md §6.8`).
3. **Affected architecture artifacts:** Which AV, BA, AA, DA, TA artifacts are affected? (SA provides this list in the CR; if not present, PO infers from the change description.)
4. **Business rationale:** Why is the change being made? What user or business need is it addressing?
5. **Phase-return scope:** Which ADM phases does SA determine must be re-executed? (This determines how deep the requirements revisit must go.)

**Scope determination rule for PO's impact assessment:**
- **Minor change:** PO reviews only requirements directly attributable to the changed element. No new RR version required if no requirements are affected.
- **Significant change:** PO reviews all requirements that trace (via RTM) to the affected architecture elements. RTM must be updated with under-review markers.
- **Major change:** PO reviews the entire RR for potential impact. May require a full requirements re-elicitation sprint if the change touches the core functional scope.
- **Safety-Critical change:** PO immediately flags any Safety-type requirement affected, regardless of whether a deeper assessment is complete. Simultaneously notifies CSCO.

---

### Step 2 — Identify Affected Requirements

Using the RTM, identify which requirements (RQ-nnn) are affected by the change:

1. **Direct impact:** Requirements that trace directly to the changed architecture element(s) via `●` entries in the RTM. These requirements must be reviewed for:
   - **Modification:** The requirement still exists but must be updated to reflect the changed architecture.
   - **Retirement:** The requirement is no longer applicable because the capability or component it traced to has been removed.
   - **Status change:** The requirement remains valid but its traceability link is broken until the new architecture baseline is established.

2. **Transitive impact:** Requirements that trace to architecture elements that are transitively affected by the change (e.g., if a business capability is removed from the BA, all requirements that trace to that capability are transitively affected). Use the RTM to identify the full transitive set.

3. **New requirements introduced by the change:** If the change adds new scope (new capabilities, new processes, new interfaces), identify whether any new requirements should be added to the RR. Use the business rationale from the CR to infer potential new requirements.

For each affected requirement: record the impact type (Modification / Retirement / New / Traceability-break) and the specific change that triggers the impact.

---

### Step 3 — Update the RR with Change-Driven Modifications

For each affected requirement identified in Step 2:

**Modification (requirement remains valid but must be updated):**
1. Update the requirement's description to reflect the post-change scope.
2. Set `status: Changed`.
3. Add a change log entry:
   ```
   RCH-nnn | RQ-nnn | Modified | [description of the modification] | PO | H-sprint-id | [impact: Low/Medium/High]
   ```
4. Retain the original RQ-nnn ID — modified requirements do not receive new IDs.

**Retirement (requirement is no longer applicable):**
1. Set `status: Retired`.
2. Add a change log entry:
   ```
   RCH-nnn | RQ-nnn | Retired | Retired due to CR-nnn: [rationale] | PO | H-sprint-id | [impact: Low/Medium/High]
   ```
3. If the requirement was Must-priority: raise CQ to user (via PM) for explicit retirement approval before marking as Retired. A Must-priority requirement cannot be retired without user acknowledgement.
4. Retain the RQ-nnn ID in the register with `status: Retired` — retired requirements remain in the historical record.

**New requirements introduced by the change:**
1. Assign the next RQ-nnn ID sequentially.
2. Set `phase-elicited: H`.
3. Set `source: CR-nnn (change-driven)`.
4. Classify type and assign priority as per the standard PO authority rules.
5. Add a change log entry:
   ```
   RCH-nnn | RQ-nnn | New | New requirement introduced by CR-nnn: [rationale] | PO | H-sprint-id | Medium
   ```

**Traceability-break (requirement valid, but its RTM link is broken):**
1. The requirement remains `Active` in the RR.
2. Do NOT modify the requirement text — the requirement itself has not changed.
3. Mark only in the RTM (Step 4) — the RTM traceability link is set to `under-review`.

After all modifications, increments, and additions: determine the new RR version:
- Patch increment (e.g., 1.0.0 → 1.0.1): if only status changes or minor description updates.
- Minor increment (e.g., 1.0.0 → 1.1.0): if new requirements are added or existing Must-priority requirements are retired.
- Major increment: not triggered by Phase H — reserved for a full re-elicitation.

Emit `artifact.baselined` for the updated RR.

---

### Step 4 — Update the RTM with Under-Review Markers

For all requirements in the RTM that are directly or transitively affected by the change:

1. Mark the affected traceability links as `under-review` in the BA, AA, DA, or TA columns (as appropriate). `Under-review` means the link existed before the change but the corresponding architecture element is currently being revised; the link will be reinstated, modified, or removed once SA's updated artifacts are baselined.
2. For retired requirements: remove their RTM rows (or mark the row as `Retired` if the RTM maintains historical records).
3. For new requirements (added in Step 3): add new RTM rows with all architecture columns set to `—` (not yet traced). These will be updated when SA baselines the revised artifacts.
4. Emit `artifact.baselined` for the updated RTM.

---

### Step 5 — Notify Stakeholders and SA

**Notification to SA:**
Create handoff to SA with PO's requirements impact summary:
```
handoff-type: requirements-impact-summary
from: product-owner
to: solution-architect
artifact-id: CR-<id>
purpose: PO's assessment of requirements impact of the change. SA should review whether
         new requirements (if any) affect the change impact assessment already in progress.
         SA should notify PO when revised architecture artifacts are baselined so PO can
         update the RTM under-review links.
```
Emit `handoff.created`.

**Notification to PM:**
Create handoff to PM with Phase H requirements status:
```
handoff-type: status-report
from: product-owner
to: project-manager
artifact-id: RR-<engagement-id>
artifact-version: [new version]
summary: [count] requirements affected (Modified: n, Retired: n, New: n, Traceability-break: n).
         [count] under-review RTM links. [count] Must-priority retirements pending user approval (CQ-ids).
```
Emit `handoff.created`.

**Stakeholder communication:**
Invoke `skills/stakeholder-communication.md` to produce a stakeholder change notification record. The notification informs stakeholders about: which requirements are changing, what the change means for the user-facing functionality, and what decisions (if any) are required from stakeholders.

**CSCO notification (if Safety-type requirements are affected):**
If any Safety-type requirement is affected by the change:
```
handoff-type: safety-requirements-impact
from: product-owner
to: csco
artifact-id: RR-<engagement-id>
section: [list of affected Safety-type RQ-nnn IDs]
purpose: CSCO awareness that safety-type requirements are affected by CR-nnn. PO requests
         CSCO review to confirm whether change classification (current: [classification]) is
         appropriate given safety requirements impact.
```
Emit `handoff.created`.

---

### Step 6 — Raise CQs for User Validation (if required)

Based on the impact assessment:

1. **Must-priority requirement retirement:** For each Must-priority requirement proposed for retirement: raise a blocking CQ to user (via PM). CQ format: "Change CR-nnn removes [capability]. This satisfies requirement RQ-nnn ([requirement title], Must priority, attributed to [stakeholder name]). Do you accept that this requirement is no longer applicable? If yes, the RR will be updated to Retired status. If no, the change scope must be revised."

2. **Significant new functional scope:** If the change introduces new functional scope that represents more than minor elaboration: raise CQ to user. "Change CR-nnn introduces [new capability/function]. This implies a new requirement: [proposed RQ-nnn text]. Do you confirm this is the intended new requirement, and what priority should it receive (Must / Should / Could)?"

3. **Ambiguous change scope:** If the CR description is insufficiently detailed for PO to identify all affected requirements: raise CQ to SA requesting CR elaboration before completing the impact assessment.

---

### Phase Revisit Handling

On `trigger="revisit"` and `phase_visit_count > 1` for Phase H (a new change event arrives while a prior Phase H is still in progress):

1. Read the EventStore to identify whether a prior Phase H algedonic signal or change record is still open. If so, assess whether the new change is related (same capability area) or independent.
2. If related: append the new change impact to the existing open Phase H assessment record. Do not create a separate impact assessment; accumulate impacts.
3. If independent: flag to PM. PM decides whether to process as a separate Phase H sprint or to batch both changes into a combined assessment.
4. Preserve all RTM entries already marked `under-review` from the prior Phase H. The new Phase H adds additional `under-review` markers but does not reset the existing ones.

---

## Feedback Loop

### Change Impact Alignment Loop (PO ↔ SA)

- **Iteration 1:** PO submits requirements impact summary to SA (Step 5). SA reviews; either confirms the requirements impact is complete and consistent with SA's architecture impact assessment, or provides additional affected architecture elements that PO has not yet accounted for in the requirements impact.
- **Iteration 2:** If SA's Iteration 1 response identifies additional affected requirements: PO updates the RR and RTM for those additional elements; resubmits updated impact summary to SA. SA confirms final requirements impact scope.
- **Termination conditions:**
  - SA confirms the requirements impact summary is complete and consistent with the architecture impact assessment, OR
  - Both agents agree that all remaining unknowns require user validation (CQs raised), OR
  - The phase-return scope is confirmed and PO's requirements work is complete for the return phase.
- **Maximum iterations:** 2.
- **Escalation if unresolved after 2 iterations:** Raise `ALG-010` to PM. PM adjudicates the scope of the requirements impact. Document disagreement in both the CR and the RR change log.

### Personality-Aware Conflict Engagement

(Applicable when SA's change impact assessment identifies architecture changes that PO believes eliminate significant user value, or when SA's proposed change scope is broader than PO believes the business need warrants.)

**Expected tension in this skill's context:** Phase H creates a specific PO ↔ SA tension around change scope. SA determines what the architecture must change to accommodate the triggering event; PO determines what requirements implications follow. A conflict arises when SA's minimum-viable change impacts more requirements than the business rationale warrants, or when PO believes the change scope has been over-extended relative to the actual requirement change.

**Engagement directive — how PO surfaces the conflict:**

When SA's change impact assessment proposes changes that, in PO's judgment, eliminate or significantly modify requirements beyond what the business rationale of the CR justifies:

1. PO states the specific requirements affected and the business value they represent: "The proposed change to [architecture element] impacts RQ-nnn (Must priority: [requirement title]), which delivers [user outcome]. The CR's stated rationale is [rationale]. Does this rationale require eliminating this requirement?"
2. PO proposes a minimum viable change scope: "Could the architecture change be scoped to [narrower change] which achieves [CR rationale] without affecting RQ-nnn?"
3. PO accepts SA's constraint when SA explains the specific architecture coupling that makes the narrower scope infeasible.

**Resolution directive:**

A conflict is resolved when:
- SA accepts PO's narrower change scope, OR
- SA explains the specific architecture coupling that forces the broader scope and PO accepts this explanation, OR
- PM adjudicates the change scope and documents the decision in the decision log.

A conflict is NOT resolved by PO unilaterally restoring a retired requirement or by SA proceeding with a change scope that PO has formally flagged as value-destructive without PM adjudication.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="change-record"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | During requirements impact assessment, PO identifies that a proposed change would violate a Safety-type requirement in the RR (the change would remove a safety constraint that the system must satisfy) | S1 | Halt RR update for the affected requirement; emit `alg.raised`; notify CSCO immediately and PM concurrently; do not retire the safety requirement without CSCO explicit approval |
| ALG-012 | PO discovers that a prior Phase H change was executed (architecture artifacts updated, phase gate passed) without PO's requirements impact assessment being performed — i.e., requirements impact was bypassed | S1 | Emit `alg.raised`; PM halts further changes in the affected scope until requirements impact is retrospectively assessed and the RR is updated |
| ALG-010 | PO ↔ SA feedback loop has been exhausted (2 iterations) and the scope of requirements impact remains disputed | S3 | Emit `alg.raised`; PM adjudicates; document both positions in the CR and RR change log |
| ALG-014 | A change is classified as Safety-Critical but CSCO is unavailable to review the affected Safety-type requirements | S1 | Halt the Safety-type requirements update; emit `alg.raised`; PM records the signal; PO awaits CSCO availability before updating safety requirements in the RR |
| ALG-016 | A blocking CQ to the user about retirement of a Must-priority requirement has been open for more than 2 sprint cycles | S2 | Emit `alg.raised`; PM consolidates and escalates to user; PO marks the requirement as `status: Pending-User-Decision` in the RR — it cannot be retired or confirmed as Active until the user responds |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Updated Requirements Register (`RR`) | `project-repository/requirements/rr-<version>.md` | Incremented version (patch or minor per Step 3 rules) | `artifact.baselined` |
| Updated Requirements Traceability Matrix (`RTM`) | `project-repository/requirements/rtm-<version>.md` | Incremented version (patch — under-review markers only) | `artifact.baselined` |
| Requirements Impact Summary (handoff payload to SA) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase H Status Report to PM | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Safety Requirements Impact notification (conditional) | `engagements/<id>/handoff-log/` | — | `handoff.created` (if Safety-type requirements affected) |
| Stakeholder Change Notification record | `project-repository/requirements/stakeholder-communication/sc-H-<sprint-id>-<version>.md` | — | Produced by `skills/stakeholder-communication.md` |

---
skill-id: PO-REQ-MGMT
agent: PO
name: requirements-management
display-name: Requirements Management — Cross-Phase Currency and Traceability
invoke-when: >
  At each phase boundary (gate.evaluated result=passed), triggered by PM to perform
  requirements currency check. Also invoked when SA or SwA baselines a new architecture
  artifact (artifact.baselined event from SA or SwA) to update the RTM with new traceability
  entries. Also invoked when a cq.answered event resolves a requirements-related CQ, requiring
  RR update. Also invoked when PO's self-audit detects staleness or gap conditions.
trigger-phases: [A, B, C, D, E, F, G, H]
trigger-conditions:
  - gate.evaluated (result=passed — any phase transition)
  - artifact.baselined (from SA — AV, BA, AA, DA; or from SwA — TA, AC)
  - cq.answered (requirements-domain CQ resolved)
  - sprint.closed (any sprint boundary — triggers stakeholder communication)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-G, EP-H]
primary-outputs: [RR (currency-checked, incremented), RTM (new traceability entries), gap report to PM]
complexity-class: standard
version: 1.0.0
---

# Skill: Requirements Management — Cross-Phase Currency and Traceability

**Agent:** Product Owner  
**Version:** 1.0.0  
**Phase:** Cross-phase (all phases)  
**Skill Type:** Cross-phase maintenance — requirements currency and RTM maintenance  
**Framework References:** `agile-adm-cadence.md §5`, `framework/artifact-schemas/requirements-register.schema.md`, `raci-matrix.md`, `clarification-protocol.md`, `algedonic-protocol.md`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Trigger event | PM / EventStore | One of: `gate.evaluated`, `artifact.baselined`, `cq.answered`, `sprint.closed` | Required — this skill is event-triggered; it does not self-invoke |
| Current Requirements Register (`RR`) | PO (self-maintained) | Latest baselined version | Blocking — currency check requires reading the current RR |
| Current RTM | PO (self-maintained) | Latest baselined version | Blocking — traceability update requires reading the current RTM |
| Newly baselined architecture artifact (if triggered by `artifact.baselined`) | SA or SwA | Version 1.0.0 (baselined) or latest version | PO reads to identify new traceability entries; draft artifacts (0.x.x) are noted but not used for RTM entries |
| CQ answer (if triggered by `cq.answered`) | User (via PM) | PM has emitted `cq.answered` with the resolved CQ record | PO reads the answer to update any RR sections that were suspended pending the CQ |

---

## Knowledge Adequacy Check

### Required Knowledge

- Full content of the trigger event and its payload — which artifact was baselined, which gate was passed, which CQ was answered, which sprint was closed.
- The current RR at its latest baselined version: all Active requirements, their types, priorities, and current traceability status.
- The current RTM at its latest baselined version: all traceability links across AV, BA, AA, DA, TA, IP, TS, and SCO columns.
- The newly baselined artifact (if applicable): its identifier scheme, its element list, and how those elements map to requirements categories.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Section Affected |
|---|---|---|---|
| Identifier scheme of a newly baselined artifact (e.g., APP-nnn for AA, TC-nnn for TA) | Yes, for RTM update | SA or SwA | RTM — relevant architecture column |
| Whether a CQ answer changes requirement scope (adds, modifies, or retires requirements) | No — PO assesses after reading the answer | — | RR — affected sections |
| Whether a phase gate passage causes a requirements review of a deferred requirement | No — PO assesses from RTM `Deferred` entries | — | RTM — deferred requirements column |

### Clarification Triggers

PO raises a CQ when:

1. **Newly baselined artifact is internally inconsistent with RR:** A baselined architecture artifact contains an element that directly contradicts a Must-priority requirement (e.g., the Application Architecture does not include a component that satisfies a Must-priority functional requirement). Non-blocking for this skill run — PO flags the gap. Blocking for the next phase gate — PO raises a CQ to SA requesting resolution before the next gate.
2. **CQ answer introduces scope that conflicts with existing requirements:** A CQ answer from the user adds scope that, in PO's judgment, directly conflicts with an existing Must-priority requirement. Blocking for RR update of the new scope — PO raises CQ to user: "Your answer to CQ-nnn introduces [new scope], which appears to conflict with RQ-nnn ([existing requirement]). Do you want to modify RQ-nnn, or should the new scope take priority?"
3. **Stale requirement with no architecture coverage after Phase F gate:** At the Phase F gate boundary, a Must-priority requirement has no `●` entries in the RTM across any architecture column. This is a blocking gap for Phase G entry. PO raises CQ to SA and PM: "RQ-nnn has no architecture coverage at Phase F gate. This is a Phase G entry blocker."

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PO", phase="req-mgmt", artifact_type="requirements-register")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase=<current_phase>)`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment scoped to the trigger event. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/work-repositories/project-repository/requirements/` — current RR and RTM
- `engagements/<id>/work-repositories/architecture-repository/` — all SA-produced artifacts at current versions
- `engagements/<id>/work-repositories/technology-repository/` — TA and ADRs (for Phase D and E RTM updates)
- `engagements/<id>/work-repositories/safety-repository/` — SCO latest update (for safety requirements currency)
- `engagements/<id>/clarification-log/` — open and recently answered CQs
- `engagements/<id>/handoff-log/` — recent handoff events that may carry requirements implications

**Pre-existing artifacts that may reduce CQ load:**

- The trigger event payload directly identifies what changed, which scopes the gap assessment to the affected elements only.
- Existing RTM entries confirm which requirements are already traced; only new elements from the triggering artifact require assessment.

---

### Step 1 — Route by Trigger Type

Based on the trigger event that invoked this skill, determine the scope of the requirements management activity:

**If triggered by `gate.evaluated` (result=passed):**
Route to the Currency Check (Step 2). A phase gate passage means the engagement has advanced; PO must verify that the RR and RTM are current with respect to the completed phase.

**If triggered by `artifact.baselined` (SA or SwA artifact):**
Route to the Traceability Update (Step 3). A newly baselined artifact may contain architecture elements that are not yet in the RTM.

**If triggered by `cq.answered`:**
Route to the CQ Integration (Step 4). A resolved CQ may require updates to the RR or RTM.

**If triggered by `sprint.closed`:**
Route to the Sprint Boundary Status Check (Step 5). A sprint closure triggers a requirements currency summary and, if needed, a stakeholder communication record.

Multiple triggers may be active simultaneously (e.g., a gate passage and a CQ answer in the same sprint). Process each trigger route in sequence: Step 2 if applicable, then Step 3 if applicable, then Step 4 if applicable, then Step 5 if applicable.

---

### Step 2 — Currency Check (gate.evaluated trigger)

When a phase gate passage is confirmed:

1. **Identify the completed phase:** Determine which phase gate was passed (e.g., A→B means Phase A is complete).

2. **Identify deferred requirements:** Read the RTM for any requirements with status `Deferred to Phase [X]` where X is the phase that has just been entered. These requirements are now in scope for traceability work.

3. **Staleness detection:** For each Active requirement in the RR, check the following staleness conditions:

   | Staleness Condition | Detection Method | Action |
   |---|---|---|
   | Requirement was produced in an earlier phase and has `status: Active` but has no `●` in any RTM column for the phase that just completed | RTM cross-check | Flag as stale; raise non-blocking CQ to SA requesting RTM link; if Must-priority: raise blocking CQ |
   | Requirement was added from an architecture artifact (e.g., added in Phase B reverse cross-reference) but has not been confirmed by user or PM | `source: SA-BA-review` flag in RR | Raise non-blocking CQ to PM for scope confirmation |
   | Requirement's `linked-artifact` field references an artifact version that has been superseded by a newer baseline | Artifact version in `linked-artifact` vs. current baselined version in EventStore | Update `linked-artifact` to current version; if the new version changes the architecture element the requirement traces to, mark RTM link as `under-review` |

4. **Gap detection:** Check whether any architecture element introduced in the completed phase (capabilities, processes, components, interfaces) lacks a corresponding requirement in the RR. For each such element: determine whether it is a missing requirement (add to RR with PO judgment) or a design element with no requirement basis (flag to PM and SA via feedback note).

5. **Version the RR if updates were made:** If any requirements were modified, added, or flagged as stale: increment the RR version (patch) and emit `artifact.baselined`.

6. **Produce gap report for PM:**
   ```
   artifact-type: requirements-gap-report
   phase-completed: [phase]
   active-requirements: [count]
   fully-traced: [count]
   partially-traced: [count]
   untraceable: [count] — [list RQ-nnn ids with priority]
   new-requirements-added: [count]
   stale-requirements-flagged: [count]
   blocking-gaps: [count with RQ-nnn ids and priority]
   ```
   Emit status report to PM via `handoff.created`.

---

### Step 3 — Traceability Update (artifact.baselined trigger)

When SA or SwA baselines a new architecture artifact:

1. **Identify the artifact type and element list:**
   - `architecture-vision` (AV): Check AV §3.4 (business drivers) and §3.5 (capability clusters) for new DRV-nnn and CAP-nnn references. Map to RR requirements.
   - `business-architecture` (BA): Check BA for new CAP-nnn, PRO-nnn, VS-nnn elements. Map to RR requirements. Update RTM BA column.
   - `application-architecture` (AA): Check AA for new APP-nnn and IFC-nnn elements. Map to RR functional requirements. Update RTM AA column.
   - `data-architecture` (DA): Check DA for new DE-nnn elements. Map to RR requirements involving data handling, privacy, or persistence. Update RTM DA column.
   - `technology-architecture` (TA): Check TA for new TC-nnn (technology components) that implement capabilities traced to RR requirements. Update RTM TA column.
   - `architecture-contract` (AC): Check AC for work package assignments. Map to RR requirements via the AC's requirement reference fields. Confirm RTM AC column entries.

2. **Apply traceability updates to RTM:**
   For each RR requirement (RQ-nnn) that can now be mapped to an element in the newly baselined artifact:
   - Add the element identifier to the appropriate RTM column.
   - Set the symbol: `●` (primary satisfaction) if this artifact/element is the primary vehicle; `○` if partial/contributing.
   - Update `status` field: `Traced` if at least one `●` exists; `Partially Traced` if only `○` entries.
   - For requirements previously marked `Untraceable`: update to `Traced` or `Partially Traced` if a link is now found; emit a status update note.

3. **Check for architecture elements with no RR backing (reverse gap):**
   For each new element in the baselined artifact, verify it can be traced back to at least one RQ-nnn requirement. Elements with no RR backing are flagged in the gap report.

4. **Update `under-review` links:**
   For any RTM entries marked `under-review` (placed there by Phase H or by an earlier incomplete assessment): check whether the newly baselined artifact resolves the under-review condition. If yes: restore the link (or update it if the architecture element changed). If no: leave `under-review` and note the pending resolution in the gap report.

5. **Emit `artifact.baselined` for updated RTM version.** Increment patch version.

---

### Step 4 — CQ Integration (cq.answered trigger)

When a CQ answer is received that affects requirements:

1. **Read the CQ record:** Identify which requirement (RQ-nnn) or requirement section the CQ was blocking, and what the user's answer resolves.

2. **Update the RR:**
   - If the CQ answer confirms a requirement: set `status: Active`; remove `[UNKNOWN — CQ: CQ-id]` annotation; fill in the specific field that was unknown.
   - If the CQ answer modifies a requirement: update the requirement description; set `status: Changed`; add change log entry `RCH-nnn | RQ-nnn | Modified | CQ-id resolved | PO | [sprint] | Low`.
   - If the CQ answer retires a requirement: set `status: Retired`; add change log entry.
   - If the CQ answer introduces a new requirement: assign next RQ-nnn ID; add to RR with `source: cq-answer (CQ-id)`.

3. **Update the RTM:** If new requirements were added: add new RTM skeleton rows (all architecture columns `—`). If requirements were retired: mark their RTM rows as `Retired`.

4. **Emit `artifact.baselined` for updated RR and RTM versions** (if changes were made).

5. **Notify PM:** Status note: "CQ-id resolved. RR updated. [count] requirements added/modified/retired."

---

### Step 5 — Sprint Boundary Status Check (sprint.closed trigger)

At each sprint closure:

1. **Self-audit checklist:**
   - [ ] All requirements added since the last sprint closure have been assigned RQ-nnn IDs and classified.
   - [ ] All RTM columns for the phases completed in this sprint have been updated.
   - [ ] All `under-review` RTM links from Phase H or prior assessments have been resolved or have a documented reason for remaining under-review.
   - [ ] All open CQs affecting the RR have been batched and submitted to PM for user routing.
   - [ ] All Must-priority requirements are traced to at least one architecture artifact column in the RTM (or have a documented, PM-approved deferral).

2. **Produce sprint requirements summary:**
   The sprint summary is produced by invoking `skills/stakeholder-communication.md` at sprint close. See that skill for format.

3. **Flag blockers to PM:**
   If the self-audit checklist reveals items that must be resolved before the next phase gate: emit a status report to PM listing the blocking items with RQ-nnn IDs and CQ-ids.

4. **Emit `artifact.baselined`** for RR and RTM if any updates were made during the sprint boundary check.

---

### Staleness Detection Rules

The following conditions constitute a stale requirement:

| Condition | Staleness Level | Action |
|---|---|---|
| Active requirement with no RTM entry in any column after the phase in which it was elicited (i.e., the phase that produced the architecture artifact it should map to has passed) | High — blocking for next gate | Flag to SA and PM; raise CQ |
| Active requirement whose `linked-artifact` references a superseded artifact version | Medium — non-blocking | Update `linked-artifact` reference; check whether the new version still satisfies the requirement |
| Requirement with `source: SA-BA-review` (added from architecture reverse gap) that has not been confirmed by user after 2 sprints | Medium — non-blocking for work; affects RR authority | Raise non-blocking CQ to PM for user confirmation |
| Requirement with `status: Deferred to Phase X` where Phase X gate has passed | High — Phase X should have produced the traceability link | Flag to SA; check whether the architecture artifact for Phase X contains the expected element |
| Safety-type requirement with no SCO cross-reference column entry after Phase B | High — potential safety gap | Notify CSCO; raise CQ |

---

## Feedback Loop

### Requirements Currency Alignment Loop (PO → SA or SwA, via PM)

This feedback loop is invoked when the currency check (Step 2) or traceability update (Step 3) identifies requirements gaps that require a response from SA or SwA.

- **Iteration 1:** PO emits gap report to PM and a targeted feedback note to SA or SwA via `handoff.created`. The feedback note lists specific RQ-nnn IDs and the architecture elements that PO has been unable to find in the baselined artifact, requesting: element references that PO may have missed, or confirmation that the gap is intentional.
- **Iteration 2:** If SA or SwA's response does not resolve the gap: PO restates the gap with the specific requirement title, priority, and the phase gate it is blocking. SA or SwA must provide a specific artifact reference or escalate to PM.
- **Termination conditions:**
  - All Must-priority gaps are resolved (traced) or formally risk-accepted by PM, OR
  - All remaining gaps are formally deferred to a specific named phase and artifact (documented in RTM), OR
  - All unresolvable gaps are escalated to PM for adjudication.
- **Maximum iterations:** 2.
- **Escalation if unresolved after 2 iterations:** Raise `ALG-010` to PM. PM adjudicates the gap disposition.

Single-agent operations (Steps 4 and 5 — CQ integration and sprint boundary check) have no cross-role feedback loop. They are PO-internal operations; the feedback channel is the CQ lifecycle managed by PM.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="requirements-register"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-007 | PO identifies (in self-audit) that an architecture agent has written a requirements artifact (containing RQ-nnn IDs or requirement statements) outside PO's `project-repository/requirements/` path — requirements content in architecture-repository without PO ownership | S1 | Emit `alg.raised`; PM halts; PO and SA reconcile the duplicate requirements content; PO absorbs the requirements into the RR under proper IDs |
| ALG-010 | PO ↔ SA feedback loop for a currency check gap has completed 2 iterations without resolution of a Must-priority untraceable requirement | S3 | Emit `alg.raised`; PM adjudicates within the current sprint |
| ALG-015 | PO self-audit detects that the RR or RTM has not been updated for 2 consecutive sprint closings despite phase gate passages and artifact baselines occurring during that period | S4 | Emit `alg.raised` (advisory); PM notified; PO executes a catch-up currency check immediately |
| ALG-016 | A CQ requesting user confirmation of a requirements scope item has been open for more than 2 sprint cycles with no response, blocking the RTM from being confirmed as current | S2 | Emit `alg.raised`; PM consolidates open CQs and escalates to user; PO marks the affected RR section as `pending-user-decision` |
| ALG-018 | PO self-audit detects that a requirements update was made (requirement added or modified) without a prior discovery scan being executed | S2 | Emit `alg.raised`; PM notified; PO executes the discovery scan retrospectively and validates the update was still warranted |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Updated Requirements Register (`RR`) | `project-repository/requirements/rr-<version>.md` | Patch increment per update cycle | `artifact.baselined` (only if requirements were added, modified, or retired) |
| Updated Requirements Traceability Matrix (`RTM`) | `project-repository/requirements/rtm-<version>.md` | Patch increment per traceability update | `artifact.baselined` (only if RTM entries changed) |
| Gap Report to PM | `engagements/<id>/handoff-log/` (handoff payload) | — | `handoff.created` |
| Traceability feedback note to SA (or SwA) | `engagements/<id>/handoff-log/` | — | `handoff.created` (conditional on gaps found) |

---

## End-of-Skill Memory Close

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase=<current_phase>, key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

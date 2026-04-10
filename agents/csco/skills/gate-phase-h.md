---
skill-id: CSCO-GATE-H
agent: CSCO
name: gate-phase-h
display-name: Phase H Safety Gate Review — Architecture Change Management
invoke-when: >
  SA produces a Change Record (artifact.baselined from SA, artifact_type=change-record)
  or PM routes a Change Record to CSCO for safety impact classification. Also activated
  when a safety-critical change is detected mid-sprint (algedonic escalation to CSCO
  via ALG-001 or ALG-014) requiring immediate safety impact assessment.
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [H]
trigger-conditions:
  - artifact.baselined from SA (artifact_type=change-record)
  - handoff.created from PM (handoff_type=change-safety-review)
  - algedonic.raised involving safety constraint violation in live system
  - cq.answered resolving a blocking Phase H CSCO safety CQ
entry-points: [EP-H]
primary-outputs:
  - Change Safety Classification (embedded in SCO §12 or standalone annotation)
  - SCO Phase H update (sco-H-<version>.md) — if change affects safety constraints
  - Gate Record Phase H (gr-H-<change-id>-1.0.0.md)
  - gate.vote_cast for H gate (or emergency vote for safety-critical changes)
complexity-class: simple
version: 1.0.0
---

# Skill: Phase H Safety Gate Review — Architecture Change Management

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** H — Architecture Change Management
**Skill Type:** Gate review — change safety impact classification + H gate vote
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (constraint impact tracing)
**Framework References:** `agile-adm-cadence.md §6.8`, `raci-matrix.md §3.8`, `framework/artifact-schemas/change-record.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Change Record (CR) | SA — architecture-repository/ | Baselined at 1.0.0 (or draft for emergency classification) | Describes the proposed change, its impact scope, and the phase(s) affected |
| SCO — all applicable phases | CSCO — safety-repository/safety-constraint-overlay/ | All baselines for affected phases at 1.0.0 | CSCO reads all SCO phase baselines to identify which SC-nnn constraints the change may affect |
| Architecture Contract (AC) | SwA — technology-repository/architecture-contract/ | Current baselined version | Reference for what the change is being applied against; CSCO checks whether the change affects AC-referenced SC-nnn constraints |
| Prior H-phase SCO update | CSCO — safety-repository/ | If phase_visit_count > 1 for Phase H, prior SCO-H version must exist | Revisit handling — preserve non-affected SCO content |
| Algedonic signal (emergency track only) | PM / Algedonic channel | Active ALG signal with change scope | Emergency classification track is activated only when an ALG-001 or ALG-014 signal is in play |

---

## Knowledge Adequacy Check

### Required Knowledge

- All SCO constraints through Phase D (and Phase G annotations): which constraints are potentially affected by the proposed change scope.
- The change impact classification taxonomy (Safety-Neutral, Safety-Relevant, Safety-Critical) and the criteria that distinguish them.
- STAMP constraint impact tracing: for a proposed change to a system element, which Loss-Hazard-Constraint chains does the change touch?

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Full technical scope of the change (which components, interfaces, data entities are affected) | Yes if classification cannot be made without scope detail | SA (CR §3 Impact Scope) or SwA (TA cross-reference) | Change Safety Classification |
| Whether a proposed change to a live system can be made safely without taking the system offline | No for classification; yes if a constraint requires downtime-safe deployment | SwA / DO (TA + operational context) | SCO Phase H update (operational constraints) |
| Regulatory notification obligations triggered by the change (e.g., GDPR data breach notification timelines, safety authority notification) | Yes if the regulatory domain includes mandatory change notification | User (via PM) | SCO Phase H update (regulatory obligations) |

### Clarification Triggers

CSCO raises a CQ when:

1. **Change scope is ambiguous for constraint impact assessment:** The Change Record's impact scope (§3) does not specify which application components, interfaces, or data entities are affected. Without this, CSCO cannot determine which SC-nnn constraints are touched. Blocking CQ to SA to revise §3 with sufficient scope detail.
2. **Change appears to relax a safety constraint:** The proposed change involves removing, weakening, or bypassing an existing SC-nnn constraint (e.g., removing an authentication step, reducing data retention, widening a network access rule). CSCO raises this immediately to SA and PM — the change must include explicit user-level risk acceptance for any safety constraint it relaxes.
3. **Change affects a live regulated system:** The system is in production and processes regulated data or performs safety-relevant functions. The change has not identified whether it triggers any regulatory change-notification obligation. CSCO raises a CQ to the user (via PM) to confirm regulatory notification requirements.

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="CSCO", phase="H", artifact_type="safety-constraint-overlay")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="H")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`:

1. **Layer 1 — Engagement State:** Read the Change Record from architecture-repository/; read all SCO phase baselines from safety-repository/; read the Architecture Contract from technology-repository/; read the clarification-log/ for any open safety CQs related to this change; read algedonic-log/ for any active ALG signals associated with this change.
2. **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for change management regulatory requirements (e.g., change freeze obligations, regulated system change approval requirements, notification timelines).
3. **Layer 4 — Target Repository:** If target-repo is configured and the change affects the live system: check deployment history, existing security configuration, and any compliance certifications that the change may affect.
4. **Layer 5 — Inference:** For CR fields where impact cannot be sourced from available artifacts, apply conservative inference (assume worst-case safety classification when ambiguous). Annotate: `[inferred — conservative — reason: <reason>]`.

---

### Step 1 — Confirm Gate Readiness

1. Confirm the Change Record is baselined at 1.0.0 (or PM has explicitly requested emergency classification on a draft CR — emergency track only).
2. Check whether this is a revisit (`trigger="revisit"`, `phase_visit_count > 1`). If revisit: read the prior SCO-H version; scope the review to the revised or new elements of the Change Record only (Step 7).
3. Check for an active algedonic signal (ALG-001 or ALG-014) triggering emergency classification. If present: proceed directly to Step 3 (Classify) without completing full discovery; emergency classification must complete within 2 hours of ALG signal receipt.

---

### Step 2 — Read the Change Record

Read the Change Record from `architecture-repository/change-record/cr-<id>-1.0.0.md` in full:

- **§2 Change Description:** What is being changed, why, and by whose request.
- **§3 Impact Scope:** Which phases, architecture layers, components, interfaces, data entities, and operational processes are affected.
- **§4 Gap Analysis:** What the current state is and what the target state will be.
- **§5 Safety and Compliance Flags:** Whether SA has pre-flagged safety-relevant concerns; read SA's preliminary assessment.
- **§6 Recommended Phase Return:** Which ADM phase(s) the change requires revisiting; note which agents are involved.

---

### Step 3 — Classify the Change

For each element identified in the Change Record's impact scope (§3): trace the constraint impact chain:

1. Identify all SC-nnn constraints that apply to the affected elements (components, interfaces, data entities, operational processes).
2. For each applicable SC-nnn: assess whether the change:
   - Has no effect on the constraint (constraint remains fully satisfied after the change) → **Safety-Neutral** contribution
   - Potentially affects the constraint's satisfaction (the change modifies a controlled element, control action, or feedback channel identified in the SCO UCAs) → **Safety-Relevant** contribution
   - Directly relaxes, bypasses, or removes the constraint, or introduces a new hazard path not currently in the SCO → **Safety-Critical** contribution

**Overall change classification (take the maximum severity across all SC-nnn assessments):**

- **Safety-Neutral:** No SC-nnn constraint is affected. Change may proceed through normal Phase H governance without additional SCO update. CSCO may approve the H gate vote immediately.
- **Safety-Relevant:** One or more SC-nnn constraints require re-evaluation against the proposed change. The SCO must be updated to reflect the change's effect on the constraint (updated loss scenarios or UCA context; no removal of constraints). CSCO may approve the H gate vote conditionally, with SCO update required before the affected architecture phase can re-close.
- **Safety-Critical:** The change relaxes or removes an SC-nnn constraint, or introduces a new hazard. **This classification requires user-level risk acceptance before the H gate vote can be cast.** CSCO raises ALG-001 if the change is proposed for a live regulated system or safety-critical system.

Record the classification and its constraint-by-constraint rationale in the Gate Record.

---

### Step 4 — Update SCO (Safety-Relevant and Safety-Critical changes only)

If classification is Safety-Relevant or Safety-Critical:

**For Safety-Relevant changes:**
- Update the affected SC-nnn constraints in SCO §5: add a version annotation noting the change ID and the revised scope or applicability condition.
- Update affected UCAs in SCO §7 if the change modifies a control action or feedback channel.
- Update affected loss scenarios in SCO §8 if the change introduces new causal factors.
- Add a Phase H gate summary entry to SCO §11.
- Produce `sco-H-<version>.md` (minor version increment from the most recent SCO phase baseline).

**For Safety-Critical changes:**
- In addition to the above: flag the constraint(s) being relaxed or removed in SCO §5 with status "SCO-PENDING-USER-ACCEPTANCE: [change-id]".
- Do not remove any SC-nnn constraint from the SCO until user-level risk acceptance has been confirmed via PM decision record.
- If user accepts the risk: update the constraint status to "accepted residual — user decision [date] — change-id [cr-id]" and note the accepted risk level.

---

### Step 5 — Cast H Gate Vote

**Approve** if: change is Safety-Neutral; or change is Safety-Relevant and SCO update is complete with no new blocking constraints; or change is Safety-Critical and user-level risk acceptance has been confirmed by PM (decision record exists).

**Conditional** if: change is Safety-Relevant and SCO update is in progress; CSCO approves the return to the affected phase(s) but requires SCO update to be completed before the re-entered phase can re-close its gate.

**Veto** if: change is Safety-Critical and user-level risk acceptance has NOT been confirmed. CSCO will not approve a safety-critical change without user-level decision. This is not negotiable via peer-agent pressure.

Emit `gate.vote_cast` for the H gate.

---

### Step 6 — Produce Gate Record and Emit Events

Author `safety-repository/gate-records/gr-H-<change-id>-1.0.0.md`:
- Change Record ID and version reviewed
- Classification result (Safety-Neutral / Safety-Relevant / Safety-Critical) with constraint-by-constraint rationale
- SC-nnn constraints affected (list with assessment outcome per constraint)
- Vote result and rationale
- Conditional requirements (if conditional vote)
- User risk acceptance reference (if Safety-Critical with accepted residuals)

Emit `artifact.baselined` for the Gate Record.
If SCO was updated: emit `artifact.baselined` for the SCO Phase H version.
Emit `handoff.created` to PM with H gate vote status, classification, and any conditional requirements.
Emit `handoff.created` to SA with the classification result and SCO update details (for SA to reflect in the Change Record §5 safety flags).

---

### Step 7 — Revisit Handling (trigger="revisit" only)

If `trigger="revisit"` and `phase_visit_count > 1` for Phase H:

1. Read the prior SCO-H version.
2. Read the revised Change Record — identify what changed from the prior version.
3. Apply Steps 2–5 only to the revised elements. Do not re-classify elements assessed in the prior H visit.
4. Update the SCO with a new minor version increment; preserve all non-affected content.
5. Re-cast the H gate vote. If the prior vote was a veto that has now been resolved: approve or conditionally approve.

---

## Feedback Loop

**Maximum iterations: 2.** After Iteration 2 without resolution: raise ALG-010 (inter-agent deadlock) to PM.

**Iteration 1:** CSCO emits H gate veto with the specific SC-nnn constraint requiring user-level risk acceptance and the exact change element triggering Safety-Critical classification. SA revises the Change Record to either (a) scope the change to avoid the safety-critical element, or (b) PM routes the risk acceptance to the user.

**Iteration 2:** CSCO reviews only the revised Change Record elements. If user risk acceptance has been confirmed: CSCO approves. If the change still touches a Safety-Critical constraint without user acceptance: second veto.

**Termination conditions:**
- **Satisfied:** All SC-nnn impacts addressed (constraint updated or risk accepted). CSCO approves. Loop closes.
- **User risk acceptance:** PM provides user decision record. CSCO records accepted residuals and approves.
- **Deadlock (ALG-010):** After Iteration 2, risk acceptance not forthcoming, change cannot be de-scoped. PM escalates to user directly.

### Personality-Aware Conflict Engagement

**CSCO ↔ SA (safety-critical classification dispute):**

SA may argue that a proposed change does not relax a safety constraint because the constraint can still be logically satisfied by a different mechanism after the change. CSCO's stance: if the proposed change modifies a control element, control action, or feedback channel that is cited in an SC-nnn constraint's UCA or loss scenario, CSCO classifies it as Safety-Relevant at minimum. CSCO does not accept implicit re-satisfaction claims without an explicit revised UCA analysis demonstrating that the new control mechanism satisfies the original constraint at the same confidence level. If SA can provide this analysis: CSCO reviews and may downgrade the classification. Without it, the classification stands.

**CSCO ↔ PM (change urgency vs safety classification):**

PM may argue that the change is operationally urgent and the safety classification process is adding unacceptable delay. CSCO's response: Safety-Neutral and Safety-Relevant changes (with SCO update in progress) can be approved within one sprint of Change Record receipt. Safety-Critical changes require user-level risk acceptance — CSCO communicates the minimum information required from the user (the specific risk to accept, with a one-paragraph description) and asks PM to obtain it as quickly as possible. CSCO will not approve a Safety-Critical change under time pressure without user acceptance — delivery urgency does not override safety gate authority.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="safety-constraint-overlay"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers <!-- workflow -->

- **ALG-001 (S1 — Safety-Critical):** A Safety-Critical classified change is proposed for a live regulated or safety-critical system, and the change would take effect before user-level risk acceptance is confirmed. Raised immediately to CSCO (self) and PM; change deployment halted pending user acceptance.
- **ALG-014 (S1 — Safety-Critical Change Without CSCO Clearance):** A Phase H change is implemented in the target repository without CSCO's H gate vote having been cast. Raised immediately on discovery, regardless of the change's apparent safety classification. All subsequent deployments of the affected system are halted until CSCO completes the H gate review.
- **ALG-010 (S3 — Inter-Agent Deadlock):** After two iterations, CSCO and SA cannot agree on the change's safety classification. PM adjudicates; CSCO veto stands during adjudication.

---

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Gate Record — H | `GR-H-<change-id>-1.0.0` | `safety-repository/gate-records/gr-H-<change-id>-1.0.0.md` | `artifact.baselined` |
| SCO Phase H Update (if applicable) | `SCO-H-<version>` | `safety-repository/safety-constraint-overlay/sco-H-<version>.md` | `artifact.baselined` |
| Gate Vote — H | (event payload) | EventStore | `gate.vote_cast` |
| Structured feedback to SA | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="H", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

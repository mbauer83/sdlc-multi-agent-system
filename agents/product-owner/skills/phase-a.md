---
skill-id: PO-PHASE-A
agent: PO
name: phase-a
display-name: Phase A — Requirements Register and Business Scenarios
invoke-when: >
  Preliminary phase or Phase A Architecture Sprint starts (sprint.started emitted), or entry
  point EP-0/EP-A/EP-B is active and the Requirements Register does not yet exist at version
  1.0.0. Also invoked when PO is the primary requirements-framing agent for any warm-start
  ingestion of a user document that contains requirements, vision, or business scenario content.
trigger-phases: [Prelim, A]
trigger-conditions:
  - sprint.started (phase=Prelim or phase=A)
  - cq.answered (blocking Phase A requirements CQs resolved)
  - handoff.created (from PM with scoping interview answers or user document)
  - handoff.created (from SA with architecture feasibility feedback on RR draft)
entry-points: [EP-0, EP-A, EP-B]
primary-outputs: [Requirements Register v0.1.0→1.0.0, Business Scenarios v0.1.0, RTM skeleton v0.1.0]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase A — Requirements Register and Business Scenarios

**Agent:** Product Owner  
**Version:** 1.0.0  
**Phase:** Preliminary / A — Architecture Vision  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.2`, `framework/artifact-schemas/requirements-register.schema.md`, `raci-matrix.md §3.2`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md §4.1–4.2`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| `sprint.started` event | PM | Must be emitted before PO begins work | Hard prerequisite — no work begins without this event |
| Scoping Interview answers (EP-0) or user document (EP-A/EP-B) | User (via PM) | CQ answers received; PM has emitted `cq.answered` or PM has forwarded user document | Blocking — PO cannot produce RR without at minimum the engagement context and a stated problem or vision |
| Engagement Profile | PM | Must exist at `engagements/<id>/engagement-profile.md` | Defines entry point, cycle level, scope, and target-repository config |
| Enterprise requirements baseline | enterprise-repository/requirements/ | Present or absent; absence is not blocking | PO reads enterprise-level requirements before eliciting engagement requirements; enterprise constraints take priority |
| SA Architecture Principles Register (PR) | SA | Draft acceptable (0.x.x) | If PR exists, PO checks engagement-specific principles for requirement constraints; absence is not blocking at Prelim |
| Market Analysis / Business Scenarios (SM) | Sales & Marketing Manager | Draft acceptable; absence is not blocking | If SM has produced a Market Analysis, PO incorporates market-driven requirements; absence noted in RR header |
| Safety Constraint Overlay (SCO) | CSCO | Not yet existing at Prelim/Phase A — SCO is CSCO's Phase A output | PO does not block on SCO; safety requirements are provisional at this stage and flagged for CSCO review |

---

## Knowledge Adequacy Check

### Required Knowledge

- The engagement's business domain — sufficient to identify functional areas and elicit initial requirements clusters.
- The user's or stakeholder's primary objectives — the "what" and "why" that requirements must serve.
- The stakeholder universe — who is affected by the system; whose needs must be represented in the RR.
- Scope boundaries — what is explicitly in scope and out of scope; without this, requirement prioritisation cannot be performed.
- Any enterprise-level requirements or standards that constrain the engagement — these take priority over engagement-level requirements.

### Known Unknowns

The following are predictably unknown at Phase A entry and require CQs before the relevant RR section can be completed:

| Unknown | Blocking | CQ Target | Artifact Section Affected |
|---|---|---|---|
| Non-functional requirement targets (performance, availability, scalability) | Yes, for NFR section of RR | User | RR — Non-Functional requirements |
| Regulatory or compliance requirements applicable to this engagement | Yes, if the domain is regulated (health, finance, critical infrastructure, data privacy) | User (via PM) | RR — Constraint requirements; RTM — SCO column |
| Stakeholder universe beyond the agent roles | Yes, for RR source-stakeholder attribution | User or SA | RR — Source Stakeholder column |
| Priority ordering when multiple requirements conflict | No — PO declares initial priority and flags conflicts | User | RR — Priority column |
| Acceptance criteria for functional requirements | No — can be deferred to Business Scenarios production | User | Business Scenarios |
| Market differentiation requirements (competitive positioning) | No — SM input; absence noted in RR header | SM | RR — Functional requirements (market-facing) |

### Clarification Triggers

PO raises a CQ (`cq.raised` event + CQ record in `engagements/<id>/clarification-log/`) when:

1. **Undefined business objective:** The user's input does not state what problem the system is solving or what outcome it must deliver. This is a blocking CQ — the RR cannot be structured without at least one stated objective.
2. **No functional scope:** The user's input describes a technology choice or implementation approach but not what the system must do for users. Blocking — functional requirements cannot be inferred from implementation intent alone.
3. **Unknown stakeholder for a stated requirement:** A requirement is present in the user's input but has no identifiable source stakeholder. Non-blocking — PO assigns `STK-TBD` and raises a non-blocking CQ.
4. **Contradictory requirements:** Two requirements in the user's input are mutually exclusive (e.g., "must be available 24/7" and "must have weekly maintenance windows without impact mitigation"). Blocking for priority assignment — PO cannot assign Must priority to both; CQ asks user to choose.
5. **Regulated domain without stated compliance requirements:** The business domain involves regulated activity (personal data, financial transactions, health records, safety-critical control) but no compliance requirements are stated. Blocking for the Constraint section of the RR; PO simultaneously notifies CSCO via handoff.

CQ format: per `clarification-protocol.md §3`. All Phase A requirements CQs are batched and routed to the user via PM. PO does not raise separate CQs for each unknown field — related unknowns are grouped into a single structured CQ record per target.

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PO", phase="A", artifact_type="architecture-vision")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/engagement-profile.md` — entry point, scope, cycle level, warm-start status
- `engagements/<id>/work-repositories/project-repository/` — any existing sprint log, SoAW, or requirements drafts
- `engagements/<id>/work-repositories/architecture-repository/` — existing AV or PR (may constrain requirements)
- `enterprise-repository/requirements/` — enterprise-level requirements applicable to this engagement
- `enterprise-repository/standards/` — technology and process standards that generate constraint requirements
- External sources (if configured): product vision wikis, business requirements confluence spaces, existing backlog tools (Jira)
- Target-repo (if configured): README, documentation, existing feature flags or feature files that imply implemented requirements

**Pre-existing artifacts that may reduce CQ load:**

- Architecture Vision (AV) → maps to business drivers (DRV-nnn) that imply requirements
- Architecture Principles Register (PR) → maps to constraint requirements derived from engagement-specific principles
- SM Market Analysis → maps to market-facing functional requirements
- Enterprise requirements → maps directly to RR Constraint or Functional requirements

---

### Step 1 — Ingest and Structure Input

After completing the Discovery Scan and Gap Assessment:

**For EP-0 (Cold Start):**
Read the Scoping Interview answers forwarded by PM. Extract every stated objective, problem, desired outcome, and scope boundary. For each extracted item, classify tentatively as: Functional (a thing the system must do), Non-Functional (a quality the system must have), or Constraint (a fixed boundary the system must operate within).

**For EP-A (Vision Entry):**
Read the user's vision document in full before producing any output. Extract stated capabilities, desired user outcomes, competitive differentiators, and any explicitly stated constraints. Annotate every extracted item with `[source: user-input]`. Items inferred by reasoning from the document are annotated `[inferred: reasoning]`.

**For EP-B (Requirements Entry):**
Read the user's requirements document in full. If the document uses the user's own requirement IDs, record those IDs in a `source-ref` field alongside the assigned RQ-nnn IDs. Do not discard the user's IDs — they are needed for traceability to the user's source document.

In all cases: produce an internal extraction list — a raw, unstructured list of all requirements-relevant items found. This is not an output artifact; it is the working input to Steps 2–4.

---

### Step 2 — Apply Requirement ID Scheme

Assign RQ-nnn IDs to all requirements in the extraction list. Rules:

1. Start at RQ-001 for a new engagement. For revisit sprints, continue from the highest existing RQ-nnn in the current RR.
2. Assign IDs in the order the requirements are encountered in the source material. Do not attempt to group by type or priority before assigning IDs — IDs are assigned first; grouping is in Step 3.
3. Each distinct requirement receives exactly one RQ-nnn ID. A requirement repeated in the source material in multiple places receives one ID; the repetitions are noted in the requirement's description field.
4. Compound requirements ("the system must do X and Y") are split into separate RQ-nnn records. Each atomic requirement is traceable and testable independently.
5. Record the `phase-elicited` field as `A` for all requirements produced in this skill invocation.

---

### Step 3 — Classify and Prioritise Requirements

For each RQ-nnn in the extraction list:

**Classification (Type field):**
- `Functional` — the system must perform a specific action or provide a specific capability. ("The system must allow users to export their data in CSV format.")
- `Non-Functional` — a quality attribute the system must satisfy across its functional behaviour. ("The system must respond to all user-initiated queries within 2 seconds at 95th percentile.")
- `Constraint` — a fixed boundary that limits design or implementation choices. ("The system must operate within EU data residency boundaries.") Constraints may originate from regulatory, contractual, technology, or budget sources.
- `Safety` — a requirement that derives from or contributes to the Safety Constraint Overlay. Flag any requirement involving potential harm, irreversible data loss, regulatory non-compliance, or system failure with real-world consequences. Mark `safety-flag: true`. PO simultaneously creates a handoff notification to CSCO for safety-relevant requirements.

**Priority assignment (Priority field):**
- `Must` — the system cannot be considered acceptable to the user or market without this requirement. Regulatory requirements are always `Must`.
- `Should` — high value; should be delivered in the primary engagement scope unless technical constraints force deferral.
- `Could` — useful but can be deferred to a subsequent phase or engagement without blocking the primary value delivery.

PO declares priority based on: explicit user statements of importance; regulatory mandates (always `Must`); business driver alignment (requirements that directly satisfy a DRV-nnn driver are elevated); and PO's own judgment about market and user impact. Priority is not a consensus vote — PO decides and documents the rationale in the requirement's description.

**Source Stakeholder (STK-nnn):**
Attribute each requirement to the stakeholder whose concern it addresses. Use the Stakeholder Register (if AV §3.3 is available) or the internal stakeholder list constructed from the Scoping Interview. If no specific stakeholder can be attributed, mark `STK-TBD` and raise a non-blocking CQ.

---

### Step 4 — Author Business Scenarios

Produce `project-repository/requirements/business-scenarios-0.1.0.md`. For each major functional area identified in the RR:

**User Stories (one per functional requirement cluster):**
Format: `As a [user role], I want to [do something], so that [I achieve an outcome].`

Rules:
- One user story per distinct user goal. Do not write user stories that describe technical implementation ("As a developer, I want a REST API..."). User stories describe user-facing goals.
- Each user story references the RQ-nnn requirements it encompasses (field: `covers: [RQ-001, RQ-002]`).
- Each user story has at least one acceptance criterion stated as a testable condition. Acceptance criteria are written in plain language — not test code or Gherkin at this stage.

**Use Cases (for complex interactions with multiple actors or steps):**
For each functional area with more than one user role or more than three steps: write a brief use case:
- Use Case ID: UC-nnn (sequential from UC-001)
- Actor(s): which user roles participate
- Preconditions: what must be true before the use case begins
- Main Flow: numbered steps (no more than 7; split into sub-use-cases if more steps are needed)
- Postcondition: what is true after the use case completes successfully
- References: `covers: [RQ-nnn, ...]`

**Value Scenarios (one per major business outcome):**
A value scenario is a short narrative (3–5 sentences) describing the business or user outcome the system enables. It is written for a senior non-technical stakeholder. It references the user stories and use cases it encompasses. Value scenarios are the PO's highest-level statement of what success looks like — they are used to evaluate scope decisions ("does this decision help us deliver this value scenario?").

---

### Step 5 — Produce RTM Skeleton

Produce `project-repository/requirements/rtm-0.1.0.md`. At Phase A, the RTM is a skeleton with the requirements column populated and all architecture columns empty:

| Req ID | Title | AV | BA | AA | DA | TA | IP | TS | SCO | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| RQ-001 | [title] | — | — | — | — | — | — | — | — | Untraceable |

Rules:
- All architecture columns default to `—` (not addressed) at this stage.
- Status defaults to `Untraceable` — will be updated to `Traced` as architecture artifacts are produced.
- The RTM is a living document — this skeleton is the baseline that all future RTM updates build on.

Emit `artifact.baselined` at version 0.1.0 for RTM.

---

### Step 6 — Submit RR Draft and Consult SA

Assemble the Requirements Register at version 0.1.0:

1. Complete the summary header per `framework/artifact-schemas/requirements-register.schema.md §2.1`:
   - `artifact-type: requirements-register`
   - `safety-relevant: true` if any Safety-type requirements are present
   - `csco-sign-off: not-required` (PO owns RR; CSCO contributes safety requirements directly)
   - `pending-clarifications: [list any open CQ-ids blocking RR sections]`
   - `assumptions: [Discovery scope record: which layers were scanned and which were unavailable]`

2. Create handoff to SA:
   ```
   handoff-type: requirements-input
   from: product-owner
   to: solution-architect
   artifact-id: RR-<engagement-id>
   artifact-version: 0.1.0
   purpose: Architecture feasibility awareness; SA should flag any requirement that is
            architecturally infeasible within stated scope
   required-by: Phase A gate
   ```
   Emit `handoff.created`.

3. Create handoff to PM (status report):
   ```
   handoff-type: status-report
   from: product-owner
   to: project-manager
   artifact-id: RR-<engagement-id>
   artifact-version: 0.1.0
   purpose: PM awareness of requirements baseline; input to SoAW
   ```
   Emit `handoff.created`.

4. If any Safety-type requirements were identified: create handoff to CSCO:
   ```
   handoff-type: safety-review-request
   from: product-owner
   to: csco
   artifact-id: RR-<engagement-id>
   artifact-version: 0.1.0
   section: Safety-type requirements (RQ-nnn list)
   purpose: CSCO awareness of PO-identified safety requirements; CSCO should confirm scope
            and add any missing safety constraints
   ```
   Emit `handoff.created`.

5. Emit `artifact.baselined` for RR at version 0.1.0.

---

### Step 7 — Resolve SA Feedback and Baseline RR

Upon receiving SA feedback on the RR draft (via `handoff.created` from SA with feedback record):

1. Read SA's feedback. For each flagged requirement:
   - **Architecture feasibility concern:** SA identifies that a requirement cannot be satisfied within the architecture constraints of the stated scope. PO engages the Feedback Loop (see below). If the conflict is resolved, update the requirement to reflect the agreed constraint. If unresolved after 2 iterations, escalate to PM.
   - **Requirements gap:** SA identifies a capability or principle that implies a requirement not in the RR. PO adds the requirement to the RR with `phase-elicited: A` and `source: SA-feedback`. This is not a conflict — it is a requirements addition.
   - **Traceability reference:** SA provides an initial architecture element reference (e.g., "this requirement maps to capability cluster CAP-002 in AV §3.5"). PO records this reference in the RTM.

2. Once all blocking SA feedback is resolved: update RR to version 1.0.0.
3. Emit `artifact.baselined` for RR at version 1.0.0.
4. Cast the PO's phase-gate consulting acknowledgement: emit `handoff.created` to PM noting that RR is at 1.0.0 and ready for Phase A gate consideration.

---

### Warm-Start Procedure: EP-A (Vision Entry)

When `entry-point: EP-A` and a user vision document is provided:

1. Complete Discovery Scan (Step 0) before reading the user document.
2. Read the user's vision document in full. Apply Steps 1–4 above, annotating each requirement with `[source: user-input]` or `[inferred: reasoning]`.
3. Flag requirements that cannot be inferred from the document with `[UNKNOWN — CQ: CQ-id]`.
4. Produce RR-000 at version 0.1.0 alongside Business Scenarios-000 at version 0.1.0.
5. Raise all blocking CQs before attempting to baseline RR at 1.0.0. Submit CQs to PM for batching.

---

### Warm-Start Procedure: EP-B (Requirements Entry)

When `entry-point: EP-B` and a user requirements document is provided:

1. Complete Discovery Scan (Step 0) before reading the user document.
2. Read the user's requirements document in full. Apply Steps 1–5 above.
3. If the user's document has its own requirement IDs, cross-reference and preserve them in `source-ref` fields.
4. Validate completeness: for each functional area implied by the stated business goals, check whether at least one functional requirement covers it. Flag uncovered functional areas as gaps.
5. Produce RR-000 (v0.1.0), Business Scenarios-000 (v0.1.0), and RTM skeleton-000 (v0.1.0).
6. Submit to SA for architecture alignment. On SA feedback: resolve per Step 7.

---

## Feedback Loop

### RR Feasibility Review Loop (PO ↔ SA)

This is the primary feedback loop for this skill. SA reviews the RR draft for architectural feasibility and provides structured feedback.

- **Iteration 1:** PO sends RR draft (v0.1.0) to SA via `handoff.created`. SA reviews; either acknowledges receipt with no concerns, or returns a structured feedback record identifying: (a) requirements that are architecturally infeasible within stated scope, (b) requirements that conflict with architecture principles, (c) requirements that imply missing architecture capabilities not yet in the AV.
- **PO response to Iteration 1 feedback:** PO engages per the Personality-Aware Conflict Engagement subsection below. PO either accepts the constraint (updates requirement), proposes a scope modification (revises requirement scope to preserve value while respecting constraint), or challenges the constraint (asks SA for the specific principle reference).
- **Iteration 2:** If the conflict is unresolved after PO's response: SA and PO exchange one more structured response. SA must provide the specific principle reference if it asserts a constraint. PO must state the specific business value at stake if it challenges a constraint.
- **Termination conditions:**
  - All SA concerns are resolved (SA withdraws feedback items, or PO has updated requirements to reflect agreed constraints): PO proceeds to Step 7 to baseline RR at 1.0.0.
  - All unresolvable conflicts are explicitly documented in the RR as open issues with `status: conflict — escalated to PM`.
- **Maximum iterations:** 2.
- **Escalation if unresolved after 2 iterations:** PO raises `ALG-010` to PM. PM adjudicates: reviews SA's constraint (specific principle reference) and PO's value statement (specific user outcome affected). PM records the adjudication decision in `project-repository/decision-log/`. If PM adjudication produces a scope change requiring user confirmation, PM escalates to user.

### CQ Resolution Loop (PO → User, via PM)

- **Iteration 1:** PO raises blocking CQs; PM batches and delivers to user; user responds via PM-structured interaction.
- **Iteration 2:** PO raises follow-up CQs on ambiguous answers; PM re-batches; user responds.
- **Termination conditions:** All blocking CQs answered; PO proceeds with non-blocking items as documented assumptions with risk flags in the RR header.
- **Maximum iterations:** 2 user interactions.
- **Escalation:** If blocking CQs are unanswered after 2 iterations: PO documents the gap as an assumption with `assumption-risk: high` in the RR header. Emits status report to PM. If the unanswered CQ concerns a safety-relevant requirement: raises `ALG-016`.

---

### Personality-Aware Conflict Engagement

(Applicable when SA feedback on the RR draft identifies requirements as architecturally infeasible or in conflict with architecture principles.)

**Expected tension in this skill's context:** PO ↔ SA is the highest-tension pairing in this skill. PO has authored requirements based on user and market value. SA reviews these requirements against architecture feasibility constraints. SA may identify requirements that are outside the feasible architecture scope, that conflict with the technology-independence principle, or that imply capabilities not yet established in the AV. This is a value vs coherence tension — exactly the tension the system is designed to surface and resolve productively.

**Engagement directive — how PO surfaces the conflict (not smooths it over):**

When SA flags a requirement as architecturally infeasible, PO does NOT:
- Silently remove the requirement.
- Mark the requirement as retired without explanation.
- Accept the SA constraint without understanding what specifically it prohibits.

PO DOES:
1. Ask SA for the specific principle or architecture constraint at stake: "Which principle (P-nnn) or constraint in the AV does this requirement violate?" A general assertion of infeasibility is not a valid conflict statement — SA must be specific.
2. State the user or market value the requirement delivers: "This requirement addresses [STK-nnn]'s need for [outcome]. Removing it means [specific impact on user / market scenario]."
3. Propose a scope modification: "Would a requirement that [narrower version of the same outcome] satisfy the architecture constraint while still delivering [core value]?"

This constitutes a valid conflict statement in this context: it names the specific value at stake, names the specific constraint, and proposes a concrete resolution path.

**Resolution directive — what constitutes a resolved conflict before escalating to PM:**

A conflict is resolved when:
- SA accepts PO's proposed scope modification as architecture-feasible, OR
- PO accepts SA's constraint because SA has provided a specific principle reference (e.g., P-002: Technology Independence) and PO can see why the requirement, as written, violates it, OR
- Both agents agree the conflict cannot be resolved without a user decision and jointly raise a CQ to PM, documenting both positions.

A conflict is NOT resolved by:
- PO unilaterally removing the requirement without SA agreement.
- SA restating the same infeasibility assertion without providing a principle reference after PO has asked for one.
- Either agent producing output that implicitly works around the conflict without naming it.

If two feedback iterations are complete and the conflict meets none of the resolution conditions above: raise `ALG-010`. Document both positions in the RR as an open conflict. PM adjudicates.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="architecture-vision"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-006 | SA feedback loop is exhausted (2 iterations) and a conflict over a Must-priority requirement remains unresolved; the conflict risks blocking the Phase A gate and cascading sprint delay | S2 | Emit `alg.raised`; PM adjudicates; PO and SA both document their positions; halt RR baseline of the affected requirement section until PM adjudicates |
| ALG-010 | PO ↔ SA feedback loop has completed 2 iterations without resolution of an architecturally contested requirement | S3 | Emit `alg.raised`; PM adjudicates within the current sprint; document both positions in the RR |
| ALG-016 | A blocking CQ to the user concerning requirements scope, regulatory context, or functional objectives has been open for more than 2 sprint cycles with no response | S2 | Emit `alg.raised`; PM consolidates all open CQs and escalates to user as priority interaction; PO halts RR baseline of the affected sections |
| ALG-018 | PO identifies (in self-audit) that a CQ was raised without a prior discovery scan | S2 | Emit `alg.raised`; PM notified; PO executes the discovery scan retrospectively and re-evaluates whether the CQ is still needed; invalidates the original CQ if discovery resolves it |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Requirements Register (`RR`) | `project-repository/requirements/rr-<version>.md` | 0.1.0 (draft at Prelim/Phase A start); 1.0.0 at Phase A gate after SA feedback resolved | `artifact.baselined` |
| Business Scenarios | `project-repository/requirements/business-scenarios-<version>.md` | 0.1.0 (draft); promoted to 1.0.0 alongside RR | `artifact.baselined` |
| RTM Skeleton | `project-repository/requirements/rtm-<version>.md` | 0.1.0 (skeleton; no architecture columns populated yet) | `artifact.baselined` |
| Handoff to SA (RR draft for feasibility review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PM (status report; SoAW input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (safety requirements notification) | `engagements/<id>/handoff-log/` | — | `handoff.created` (conditional on safety requirements present) |

---
skill-id: CSCO-GATE-A
agent: CSCO
name: gate-phase-a
display-name: Phase A Safety Gate Review — Architecture Vision
invoke-when: >
  SA produces Architecture Vision (AV) at version 1.0.0 (artifact.baselined emitted) or SA
  emits handoff.created requesting CSCO safety review of the AV Safety Envelope draft. Also
  activated when SA requires csco-sign-off on AV §3.7 before Phase A gate can close.
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [A]
trigger-conditions:
  - artifact.baselined from SA (artifact_type=architecture-vision)
  - handoff.created from SA (handoff_type=review-and-sign-off, section=§3.7 Safety Envelope)
  - sprint.started (phase=A) when SCO Phase A baseline does not yet exist
  - cq.answered resolving a blocking Phase A CSCO safety CQ
entry-points: [EP-0, EP-A, EP-B]
primary-outputs:
  - SCO Phase A Baseline (sco-A-1.0.0.md)
  - Gate Record Phase A (gr-A-B-1.0.0.md)
  - gate.vote_cast for Prelim→A gate
  - gate.vote_cast for A→B gate
complexity-class: standard
version: 1.0.0
---

# Skill: Phase A Safety Gate Review — Architecture Vision

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** A — Architecture Vision
**Skill Type:** Gate review — safety analysis + gate vote
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (STAMP Level 1 procedure)
**Framework References:** `agile-adm-cadence.md §6.2`, `raci-matrix.md §3.2`, `framework/artifact-schemas/architecture-vision.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `sdlc-entry-points.md §4.1–4.2`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Architecture Vision (AV) | SA — architecture-repository/architecture-vision/ | Baselined at version 1.0.0 | Formal gate review cannot begin until AV is baselined; informal pre-review guidance may be given on 0.x.0 |
| AV Safety Envelope draft (§3.7 or separate document) | SA — included in AV or handoff from SA | Draft acceptable; authored by SA; CSCO reviews and confirms or corrects | If §3.7 is absent from AV, CSCO raises a blocking CQ to SA |
| Engagement Profile | PM — engagements/<id>/engagement-profile.md | Must exist | Provides scope, entry point, target-repo config |
| Enterprise Standards baseline | enterprise-repository/standards/ | Available (read-only) | Used to identify applicable regulatory frameworks; absence does not block review |
| Prior SCO version | CSCO — safety-repository/safety-constraint-overlay/ | Not required at Phase A (first SCO); required if revisit (phase_visit_count > 1) | If revisit: read prior SCO and update only affected sections |
| sprint.started event | PM | Must be emitted for Phase A sprint | Hard prerequisite — no gate work begins without this event |

---

## Knowledge Adequacy Check

### Required Knowledge

- Safety classification taxonomy for the engagement domain: what constitutes a safety-critical, safety-related, or non-safety system in the engagement's industry sector (healthcare, finance, transport, infrastructure, commercial software, etc.).
- The system's proposed purpose and scope as described in the AV (§3.1 Engagement Context, §3.2 Scope, §3.5 Capability Overview, §3.7 Safety Envelope).
- Applicable regulatory frameworks for the engagement's domain and jurisdiction (e.g., GDPR, HIPAA, ISO 26262, IEC 61508, PCI-DSS, SOX).
- STAMP/STPA Level 1 procedure per `skills/stamp-stpa-methodology.md §Steps 1–4`.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Safety classification of the system | Yes — SCO §1 cannot be completed; Level 1 hazard list cannot be produced | User (via PM), with SA as co-informant | SCO §1 (Classification), §3 (Hazard List), §5 (Constraints), AV §3.7 sign-off |
| Regulatory jurisdiction and applicable standards | Yes for regulated domains (healthcare, finance, transport, critical infrastructure); no for clearly non-regulated commercial software | User (via PM) | SCO §2 (Regulatory Domain), compliance checklists |
| System boundary for safety analysis | Yes — control structure (Step 4) cannot be drawn without a defined boundary | SA (via AV §3.7 or revision handoff) | SCO §4 (Control Structure), SCO §7 (UCAs) |
| Third-party or external system dependencies with safety implications | No — absence is noted; constraints are scoped to the in-scope system | SA (via AV §3.8 Gap Analysis) or user | SCO §5 (Constraints — external system constraints) |

### Clarification Triggers

CSCO raises a CQ when:

1. **Safety classification is indeterminate from AV content:** The AV describes a system whose domain, functionality, or stakeholders are ambiguous with respect to safety classification. This is a blocking CQ targeting the user (with SA as co-respondent). CSCO does not infer safety classification when the domain is genuinely ambiguous — the consequences of a wrong inference in either direction are too significant.
2. **AV §3.7 Safety Envelope is absent:** SA has not authored a Safety Envelope section in the AV, and no handoff has been sent requesting CSCO's initial safety scan. CSCO raises a non-blocking CQ to SA to produce §3.7 before the Phase A gate can be cast.
3. **Regulatory jurisdiction is unknown for a regulated domain:** The AV describes functionality that appears to fall within a regulated domain but does not identify the applicable regulatory framework. Blocking CQ for the compliance checklist; non-blocking for the hazard analysis (CSCO proceeds with known hazard categories and notes the regulatory gap).
4. **Safety Envelope proposes a safety classification that appears incorrect:** SA has classified the system as "non-safety" but the AV describes functionality that CSCO assesses as safety-relevant (e.g., the system processes personal health data, controls financial transactions, or interfaces with a physical control system). CSCO raises a CQ to SA and the user to confirm the classification before accepting the Safety Envelope.

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="CSCO", phase="A", artifact_type="safety-constraint-overlay")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="A")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2` before any artifact review or SCO authoring:

1. **Layer 1 — Engagement State:** Read engagement-profile.md; read all existing safety-repository/ content (check for any prior SCO drafts); read architecture-repository/architecture-vision/ (the AV being gated); read architecture-repository/architecture-principles/ (Architecture Principles Register); read clarification-log/ (safety-relevant CQs and answers); read handoff-log/ (incoming handoff from SA requesting CSCO review); read algedonic-log/ (any open ALG signals that affect Phase A scope).
2. **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for applicable regulatory and compliance standards. Read enterprise-repository/reference-library/ for relevant safety patterns applicable to the engagement domain.
3. **Layer 3 — External Sources:** Check external-sources/ configuration for any regulatory or compliance databases configured for this engagement.
4. **Layer 4 — Target Repository:** If target-repo is configured and accessible, check for any existing safety documentation, security policies, or compliance certifications.
5. **Layer 5 — Inference:** For SCO fields that cannot be sourced from Layers 1–4, apply domain-knowledge inference based on engagement domain. Annotate every inferred field: `[inferred — source: domain knowledge — <engagement domain>]`. Do not raise CQs for fields that can be confidently inferred.

Record the Discovery Scan completion in the Gate Record before proceeding.

---

### Step 1 — Confirm Gate Readiness

Before beginning the substantive gate review:

1. Confirm that `artifact.baselined` has been emitted for AV version 1.0.0 or higher. If AV is still at 0.x.x: do not cast a formal gate vote. Provide informal guidance to SA on what §3.7 must contain; await `artifact.baselined` for 1.0.0.
2. Confirm that `sprint.started` has been emitted for the Phase A gate review sprint.
3. Check whether this is a revisit (`trigger="revisit"` and `phase_visit_count > 1`). If revisit: read the prior SCO Phase A version and the EventStore gate history to identify which AV sections changed. Scope the review to changed sections only (Step 8 covers revisit procedure).
4. Load the CSCO-STAMP-STPA methodology reference (`skills/stamp-stpa-methodology.md`) — all terminology and procedures in Steps 2–6 follow that specification.

---

### Step 2 — Read Architecture Vision in Full

Read the entire AV document from `architecture-repository/architecture-vision/av-1.0.0.md` (or current version):

- §3.1 Engagement Context: note the system's stated purpose, the problem it solves, and the user's intent.
- §3.2 Scope: note the explicit in-scope and out-of-scope boundaries.
- §3.3 Stakeholder Register: note all stakeholder categories — relevant for identifying who is harmed by each loss.
- §3.4 Business Drivers and Goals: note the priorities — relevant for identifying which losses are most consequential to the user.
- §3.5 Capability Overview: note the capability clusters — relevant for identifying which capabilities are safety-relevant.
- §3.6 Architecture Principles Application: note safety-relevant principles applied.
- §3.7 Safety Envelope: read in detail — this is the primary CSCO review section. Note the proposed safety boundary, hazard categories, initial constraints, and the `csco-sign-off` field status.
- §3.8 Gap Analysis: note gaps that may have safety implications (e.g., unknown integration points, undefined external system behaviour).

---

### Step 3 — Identify System Safety Classification

Based on the AV content and Discovery Scan findings, classify the system:

**Safety-Critical:** The system directly controls physical processes, safety mechanisms, or life-critical decisions, or a failure of the system could directly cause injury, death, or irreversible harm. Examples: industrial control systems, medical device software, autonomous vehicle software, aircraft systems.

**Safety-Related:** The system processes data or controls processes where failures could lead to significant harm, financial loss, regulatory non-compliance, or serious privacy breach, but the system is not directly in the control loop of a physical process. Examples: healthcare data management systems, financial transaction systems, personal data processors, emergency dispatch software.

**Non-Safety:** The system's failure produces inconvenience or business disruption but no safety, health, privacy, or regulatory consequences. Examples: internal productivity tools, content management systems, marketing platforms (where no sensitive data is involved).

Record the classification in SCO §1 with a one-paragraph rationale. If the classification cannot be determined from available information, raise a blocking CQ (per Knowledge Adequacy Check trigger 1). Do not proceed past Step 3 until classification is confirmed.

---

### Step 4 — Review AV Safety Envelope (§3.7)

Review SA's Safety Envelope draft against the following criteria:

1. **Safety boundary completeness:** Does the boundary statement identify all components and external interfaces that are in scope for safety analysis? Flag any capability cluster from §3.5 that appears safety-relevant but is not included in the safety boundary.
2. **Hazard category coverage:** Does SA's initial hazard list cover the hazard categories appropriate for the system's safety classification and domain? CSCO corrects or extends the list — SA's hazard identification is input, not final.
3. **Constraint quality:** Are SA's proposed initial constraints stated as system-level constraints (what the system must enforce), not solutions (how it will enforce them)? Constraints that specify technology or implementation approach at Phase A are premature and must be revised to the appropriate level of abstraction.
4. **STAMP analysis reference:** Has SA referenced STAMP/STPA as the analysis method? If not, CSCO adds this to the SCO.
5. **CSCO declaration field:** Is the `csco-sign-off: pending` field present? If not, flag to SA that the AV header must include this field.

For each deficiency found: produce a structured feedback item specifying the §3.7 subsection, the exact deficiency, and the required revision. Do not revise SA's artifact directly.

---

### Step 5 — Author SCO Phase A Baseline

Author `safety-repository/safety-constraint-overlay/sco-A-0.1.0.md` (draft until gate vote is cast, then promoted to 1.0.0):

**§1 System Safety Classification:**
Record the classification determined in Step 3 with rationale.

**§2 Regulatory Domain:**
List all applicable regulatory standards identified during Discovery Scan and Step 2 review. For each standard: jurisdiction, authority, applicability rationale, key obligation categories. If regulatory jurisdiction is unknown: record the domain assessment, note that a CQ is open, and list the potential applicable standards for the identified domains.

**§3 System-Level Losses:**
Apply STAMP/STPA Step 1 (from `skills/stamp-stpa-methodology.md`): enumerate L-nnn losses for the engagement. Trace each loss to one or more stakeholders and any applicable regulatory obligation.

**§4 System-Level Hazards:**
Apply STAMP/STPA Step 2: enumerate H-nnn hazards for the engagement. Trace each hazard to one or more L-nnn losses. Include the worst-case environmental conditions that convert each hazard to a loss.

**§5 Safety Constraints:**
Apply STAMP/STPA Step 3: author SC-nnn constraints — one minimum per hazard. Mark each constraint with type (Architectural / Operational / Technical / Regulatory) and phase (Phase A). Incorporate and refine SA's proposed constraints from §3.7 if they are correctly formulated; replace incorrectly formulated ones with corrected versions. All Phase A constraints are Architectural or Regulatory type — Technical constraints come at Phase D.

**§6 Control Structure:**
Apply STAMP/STPA Step 4: produce the Level 1 control structure — role-level and system boundary-level controllers only at Phase A. Record controllers, control actions, controlled processes, and feedback channels for the top-level system boundary.

**§7 Unsafe Control Actions:**
Apply STAMP/STPA Step 5 at Level 1: identify UCAs for the control actions identified in §6. Focus on system boundary UCAs — which system-level actions, if not provided, provided incorrectly, or timed incorrectly, lead to H-nnn hazards.

**§8 Loss Scenarios:**
Apply STAMP/STPA Step 6 at Level 1: identify causal factors that would lead to the Level 1 UCAs. At Phase A these are high-level causal categories — specific implementation scenarios are deferred to Phase C and D.

**§9 Compliance Requirements:**
For each regulatory standard in §2: list the key compliance obligations and map each to an SC-nnn constraint. Where a compliance obligation does not yet have a corresponding SC-nnn: flag it as "SC-PENDING" and note it in §10.

**§10 Open Safety Findings:**
Record any safety issues identified during the AV review that are not yet resolved: missing §3.7 content, unconfirmed safety classification, unknown regulatory jurisdiction, and any AV scope items that appear safety-relevant but are not constrained. For each finding: SF-nnn, description, status (open), owner (SA or user), blocking gate: yes/no.

**§11 Phase Gate Summary:**
Leave for population when gate vote is cast.

---

### Step 6 — Review AV Against SCO Phase A

With the SCO Phase A draft complete, perform a cross-reference review of the AV against the SCO:

For each SC-nnn constraint in SCO §5: determine whether the AV (specifically §3.7, §3.5, and §3.8) reflects or is consistent with the constraint. Flag violations:

**Violation type A — Direct conflict:** The AV describes a scope, approach, or assumption that directly contradicts an SC-nnn constraint. Example: AV §3.5 describes a capability that requires exposing Restricted data to unauthenticated external actors, but SC-003 requires that Restricted data is never accessible to unauthenticated actors.

**Violation type B — Missing constraint coverage:** The AV describes a scope element (capability, integration point, data category) that is safety-relevant but for which no SC-nnn constraint exists. This requires authoring a new SC-nnn in the SCO (or flagging it as SC-PENDING in §10).

**Violation type C — Constraint at wrong level of abstraction:** The AV §3.7 contains a constraint that is actually a technology specification (premature). Flag this to SA as a revision requirement — the constraint must be restated at the architecture level.

For each violation found: produce a structured feedback item (constraint ID, violation type, AV section and content, required revision, blocking status). Aggregate all feedback items before emitting the gate vote.

---

### Step 7 — Cast Gate Votes

**Prelim→A Gate Vote:**
Cast `gate.vote_cast` for the Prelim→A gate:
- **Approve** if: safety classification is confirmed, regulatory domain is identified (or definitively non-regulated), SCO Phase A §1–§5 are complete, and no Violation Type A blocking findings exist.
- **Conditional** if: safety classification is confirmed but regulatory jurisdiction CQ is open; SCO Phase A is otherwise complete. Specify: evidence required (regulatory jurisdiction confirmation), source (user via PM), deadline (within current sprint).
- **Veto** if: safety classification cannot be determined (blocking CQ open) or SCO §1 cannot be completed. Specify: SC-PENDING (classification blocker) with remediation path (user provides classification via PM CQ).

**A→B Gate Vote:**
Cast `gate.vote_cast` for the A→B gate:
- **Approve** if: all Violation Type A findings from Step 6 are resolved (via SA revision or user risk acceptance), SCO Phase A is baselined at 1.0.0, AV §3.7 `csco-sign-off: true` is recorded, and no blocking SF-nnn items remain in SCO §10.
- **Conditional** if: one or more Violation Type B findings (missing constraints) exist for scope elements not yet designed, but no Violation Type A conflict is present. Specify: the missing constraint domain, the artifact where coverage is expected (Phase B BA), and the sprint deadline.
- **Veto** if: one or more Violation Type A conflicts exist after SA's first revision (Iteration 1 feedback not resolved). Reference the SC-nnn violated and specify minimal revision required.

Emit `gate.vote_cast` events for both gates. Record the votes in SCO §11.

---

### Step 8 — Promote SCO and Emit Events

If the A→B gate vote is **approve** or **conditional**:
1. Promote SCO Phase A from draft (0.1.0) to baselined (1.0.0). Update SCO §11 with gate vote results.
2. Emit `artifact.baselined` for SCO Phase A version 1.0.0 with path `safety-repository/safety-constraint-overlay/sco-A-1.0.0.md`.
3. Produce Gate Record `safety-repository/gate-records/gr-A-B-1.0.0.md` containing: gate ID, AV artifact ID and version reviewed, SCO constraints verified, vote result, rationale, any conditional requirements, open findings.
4. Emit `artifact.baselined` for the Gate Record.
5. Emit `handoff.created` to PM confirming A→B gate vote status and any conditional requirements.
6. Emit `handoff.created` to SA: AV §3.7 sign-off (`csco-sign-off: true`) and any revision requirements from Step 6.

If the A→B gate vote is **veto**: proceed to Feedback Loop (do not promote SCO to 1.0.0 until veto is resolved; maintain at 0.1.0 as working draft).

### Step 9 — Revisit Handling (trigger="revisit" only)

If `trigger="revisit"` and `phase_visit_count > 1`:

1. Read the EventStore gate history to identify which AV sections changed in this revisit (SA will have provided a change scope in the revision handoff).
2. Read the prior SCO Phase A version.
3. Apply Steps 2–6 only to the changed AV sections. Do not re-analyse sections that are unchanged.
4. Update only the SCO constraints, UCAs, and loss scenarios affected by the changes.
5. Increment SCO version (minor increment for draft; major for new baseline).
6. Re-cast the A→B gate vote. The Prelim→A gate vote does not need to be re-cast unless the safety classification itself changed.
7. Preserve all non-affected SCO content verbatim.

---

## Feedback Loop

**Maximum iterations: 2.** After Iteration 2 without resolution: raise ALG-010 (inter-agent deadlock) to PM.

**Iteration 1:** CSCO emits `gate.vote_cast (veto)` citing specific SC-nnn and structured feedback items from Step 6. SA revises AV §3.7 and any other flagged sections. SA re-baselines AV with a new version. SA emits `artifact.baselined` for the revised AV.

**Iteration 2:** CSCO receives revised AV. CSCO reviews only the sections that were revised (not the full AV again — only the sections SA changed in response to Iteration 1 feedback). If all Violation Type A findings are resolved: CSCO approves. If any Violation Type A finding remains unresolved: CSCO casts second veto.

**Termination conditions:**
- **Satisfied:** All Violation Type A findings resolved by SA revision or user risk acceptance. CSCO emits `gate.vote_cast (approve)`. Loop closes.
- **User risk acceptance:** User explicitly accepts one or more residual risks (recorded by PM in decision log). CSCO updates SCO §10 to mark accepted findings as "accepted — user decision [date]". CSCO emits `gate.vote_cast (approve with accepted residuals)`. Loop closes.
- **Deadlock (ALG-010):** After Iteration 2 with Violation Type A unresolved: CSCO raises ALG-010 to PM. PM adjudicates within current sprint. If PM cannot resolve: PM escalates to user. CSCO veto stands throughout. Loop transfers to PM arbitration.

### Personality-Aware Conflict Engagement

**CSCO ↔ SA (architecture scope vs safety gate):**

SA may dispute a CSCO finding on the grounds that: (a) the safety classification is overstated, (b) a proposed constraint is impractical at the architecture level, or (c) the AV already contains sufficient safety coverage.

CSCO's stance in each case:

**(a) Classification dispute:** CSCO does not negotiate safety classification on the basis of delivery convenience. If SA believes the classification is overstated, SA must provide domain evidence (regulatory guidance, industry standard, comparable system classification) that contradicts CSCO's assessment. CSCO reviews the evidence and revises the classification if the evidence is compelling. Without evidence, the CSCO classification stands. If after Iteration 2 the classification is still disputed: ALG-010 to PM; user resolves.

**(b) Constraint practicability:** CSCO's constraints specify what the system must achieve, not how. If SA asserts a constraint is architecturally infeasible, CSCO does not revise the constraint — CSCO asks SA to demonstrate that no architecture pattern can satisfy the constraint. If SA can demonstrate infeasibility, CSCO raises ALG-001 (hazard without a feasible constraint) and escalates to PM and user. A constraint is not removed because it is inconvenient; it is removed or accepted as residual risk only when demonstrated to be unachievable.

**(c) Existing coverage:** CSCO reads the cited coverage carefully. If SA's existing §3.7 content genuinely satisfies the SC-nnn constraint: CSCO withdraws the finding and approves. CSCO does not maintain a veto on the basis of format preferences or stylistic disagreement — only genuine safety constraint violations.

**CSCO ↔ PM (gate velocity pressure):**

PM may push CSCO to approve the Phase A gate to maintain sprint cadence. CSCO's stance: CSCO will not approve the A→B gate while a Violation Type A finding is open. CSCO will approve conditionally when findings are Violation Type B (coverage gaps in future phases) or Violation Type C (abstraction level — non-blocking for progression). CSCO communicates the minimal revision required (not a comprehensive list of nice-to-haves) to enable approval in the current sprint.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="safety-constraint-overlay"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---


## Red Flags

Pre-escalation observable indicators. Raise an algedonic signal or CQ if two or
more of these are true simultaneously:

<!-- TODO: add 5-7 role-specific observable indicators for this skill -->
- Outputs section of the primary artifact is blank after completing the procedure
- Any required input artifact is missing and no CQ has been raised
- Feedback loop iteration count has reached the maximum with no resolution

## Algedonic Triggers <!-- workflow -->

- **ALG-001 (S1 — Safety-Critical):** The AV scope requires a safety constraint that cannot be satisfied by any known architecture approach — for example, a safety-critical system (physical control, life-critical data) with no proposed isolation mechanism and no feasible isolation path identified by CSCO's analysis. Raised immediately with concurrent escalation to CSCO (self) and PM. Phase A work halts on the affected scope until a feasible safety architecture is proposed.
- **ALG-012 (S1 — Governance Violation):** SA attempts to baseline AV at 1.0.0 and proceed to Phase B without CSCO's Phase A gate sign-off having been cast. Raised immediately to PM with concurrent notification. Phase B work does not begin.
- **ALG-017 (S1 — Knowledge Gap):** The safety classification of the system cannot be determined from the AV or any available source, and the engagement domain appears to be regulated or safety-relevant. Raised to user via PM; CSCO concurrent; halt affected Phase A gate work. The gate remains open until classification is confirmed.

---


## Verification

Before emitting the completion event for this skill, confirm:

<!-- TODO: extend with skill-specific checklist items -->
- [ ] All blocking CQs resolved or documented as PM-accepted assumptions
- [ ] Primary output artifact exists at the required minimum version
- [ ] CSCO sign-off recorded where required (`csco-sign-off: true`)
- [ ] All required EventStore events emitted in this invocation
- [ ] Handoffs to downstream agents created
- [ ] Learning entries recorded if a §3.1 trigger was met this invocation
- [ ] Memento state saved (End-of-Skill Memory Close)

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Safety Constraint Overlay — Phase A Baseline | `SCO-A-1.0.0` | `safety-repository/safety-constraint-overlay/sco-A-1.0.0.md` | `artifact.baselined` |
| STAMP/STPA Analysis — Phase A | `sa-001-A.md` | `safety-repository/stamp-stpa/sa-001-A.md` | `artifact.baselined` |
| Gate Record — A→B | `GR-A-B-1.0.0` | `safety-repository/gate-records/gr-A-B-1.0.0.md` | `artifact.baselined` |
| Gate Vote — Prelim→A | (event payload) | EventStore | `gate.vote_cast` |
| Gate Vote — A→B | (event payload) | EventStore | `gate.vote_cast` |
| Compliance Checklist (per regulatory domain) | `cl-<domain>-1.0.0.md` | `safety-repository/compliance-checklists/` | `artifact.baselined` |
| Structured feedback to SA | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="A", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

---
skill-id: SA-PHASE-A
agent: SA
name: phase-a
display-name: Phase A — Architecture Vision
invoke-when: >
  Phase A Architecture Sprint starts (sprint.started emitted) or entry point EP-0/EP-A/EP-B is
  active and the Architecture Vision artifact does not yet exist at version 1.0.0.
trigger-phases: [Prelim, A]
trigger-conditions:
  - sprint.started (phase=A)
  - cq.answered (blocking Phase A CQs resolved)
  - handoff.created (from PM with scoping interview answers)
entry-points: [EP-0, EP-A, EP-B]
primary-outputs: [Architecture Vision, Architecture Principles Register, Stakeholder Map]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase A — Architecture Vision

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** A — Architecture Vision  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.2`, `framework/artifact-schemas/architecture-vision.schema.md`, `raci-matrix.md §3.2`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md §4.1–4.2`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Scoping Interview answers (EP-0) or user input document (EP-A/B) | User (via PM) | CQ answers received; PM has emitted `cq.answered` | Blocking — SA cannot produce AV without at minimum the engagement context |
| Requirements Register (`RR`) | Product Owner | At least one iteration complete (draft acceptable) | Not blocking on EP-0 if SA authors AV from Scoping Interview answers; RR-000 acceptable |
| Architecture Principles Register (`PR`) | SA (self-produced, prerequisite) | Must be drafted before AV; version 0.1.0 acceptable for AV production | If PR does not exist, SA produces it as Step 1 of this skill |
| Market Analysis / Business Scenarios | Sales & Marketing (SM) | Draft acceptable; absence is not blocking | If absent, SA notes the gap in AV §3.4 and raises a non-blocking CQ to SM |
| Safety Constraint Overlay (SCO) baseline | CSCO | Not yet existing at Phase A start — SA produces Safety Envelope draft; CSCO reviews | CSCO review and sign-off is a gate prerequisite, not a production prerequisite |
| `sprint.started` event | PM | Must be emitted before SA begins work | Hard prerequisite — no work begins without this event |

---

## Knowledge Adequacy Check

### Required Knowledge

- The engagement's business domain — sufficient to characterise capability clusters (§3.5) and identify relevant hazard categories (§3.7).
- The regulatory and compliance environment — determines which safety constraints are non-negotiable and which are configurable.
- The stakeholder universe — sufficient to populate the Stakeholder Register (§3.3) at a minimum with all agent roles plus named external stakeholders.
- The scope boundary — what is explicitly in scope and out of scope; without this the Gap Analysis (§3.8) cannot be produced.
- Architecture Principles applicable to the engagement — SA authors the PR if none exist; if the enterprise-repository contains a baseline PR, read it first.

### Known Unknowns

The following are predictably unknown at Phase A entry and require CQs before the relevant AV section can be completed:

| Unknown | Blocking | CQ Target | AV Section Affected |
|---|---|---|---|
| Regulatory jurisdiction and applicable standards | Yes, if safety-relevant or regulated domain | User | §3.7 (Safety Envelope), §3.6 (Principles Application) |
| Safety classification of the system | Yes, for §3.7 | User (via PM) and CSCO | §3.7 (Safety Envelope) |
| Existing system landscape (systems to integrate or replace) | Yes, for §3.8 (Gap Analysis) | User | §3.8 |
| Named external stakeholders beyond agent roles | No (agent roles always present; external stakeholders can be added later) | User or PO | §3.3 |
| Detailed business drivers not present in user's input | No — SA can derive initial drivers from stated problem and scope; refine post-CQ | User or PO | §3.4 |
| Market Analysis from SM | No — absence noted; AV proceeds with available drivers | SM | §3.4, §3.5 |

### Clarification Triggers

SA raises a CQ (`cq.raised` event + CQ record in `engagements/<id>/clarification-log/`) when:

1. **Unknown business domain:** The user's input does not characterise the business domain sufficiently for SA to identify even one capability cluster. This is a blocking CQ — AV §3.5 cannot proceed.
2. **Unclear safety classification:** The user's input contains components that *may* be safety-relevant (physical systems, financial transactions, health data, infrastructure control) but has not stated a safety classification. Blocking for §3.7; non-blocking for other sections.
3. **Ambiguous scope boundaries:** The user's input describes a scope that cannot be cleanly bounded — the set of in-scope systems is undefined. Blocking for §3.2 (Engagement Context, scope statement) and §3.8 (Gap Analysis).
4. **Unknown regulatory environment:** The system touches domains (health, finance, transport, critical infrastructure, data privacy) where regulatory jurisdiction is unknown. Blocking for §3.7 and §3.6 in regulated domains; non-blocking for §3.5 and §3.4.
5. **Missing key stakeholders:** The SA cannot identify any business-side stakeholder with decision authority. Blocking for §3.3 (Stakeholder Register cannot have only agent roles).

For CQs 2 and 4, SA simultaneously notifies CSCO via handoff event to begin an initial safety scan on available information — CSCO work and SA CQ resolution proceed concurrently.

CQ format: per `clarification-protocol.md §3`. All Phase A CQs are architecture-domain CQs. SA does not raise CQs for process-governance knowledge — those are PM domain.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="A", artifact_type="architecture-vision")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

Before beginning any production step:
1. Confirm `sprint.started` has been emitted for the current Architecture Sprint.
2. Confirm that all blocking CQs from the Scoping Interview or Entry Assessment are answered (or that a documented assumption has been accepted by PM).
3. Read the current Architecture Principles Register from `enterprise-repository/` if it exists. If it does not, proceed to Step 1 to author a new one.

---

### Step 1 — Author Architecture Principles Register (prerequisite artifact)

**If PR does not already exist for this engagement:**

Produce `architecture-repository/architecture-principles/pr-0.1.0.md` containing:

1. **Methodology Principles** (always present):
   - Technology Independence: Architecture artifacts (AV, BA, AA, DA) are technology-independent; technology decisions belong in Phase D.
   - Traceability: Every architecture element must be traceable to a business driver or stakeholder concern.
   - Safety First: Safety constraints (from SCO) are non-negotiable; architecture cannot proceed past a phase gate where a safety constraint is unresolved.
   - Single Accountability: Every artifact has exactly one accountable agent per the RACI matrix.

2. **Enterprise Principles** (if present in `enterprise-repository/metamodel/` or `enterprise-repository/standards/`): import applicable principles with their IDs.

3. **Engagement-Specific Principles** (derived from Scoping Interview or user input): any principles that are engagement-specific (e.g., "All processing must remain within EU jurisdiction", "No proprietary lock-in for core platform").

Format per `repository-conventions.md §7`. Emit `artifact.baselined` at version 0.1.0 (draft; will be upgraded to 1.0.0 at Phase A gate if no further revisions are required).

**If PR already exists:** Read it. Note any principles directly constraining this engagement scope. Proceed to Step 2.

---

### Step 2 — Produce Stakeholder Register

Produce `architecture-repository/stakeholder-map/sm-0.1.0.md` containing the Stakeholder Register per `architecture-vision.schema.md §3.3`.

**Always-present stakeholders (agent roles as internal stakeholders):**

| Stakeholder ID | Role | Primary Concern | Viewpoint | Engagement Level |
|---|---|---|---|---|
| STK-001 | Product Owner | Requirements satisfaction; feature delivery | Business Layer | Active |
| STK-002 | Project Manager | Process governance; timeline; risk | Stakeholder Viewpoint | Active |
| STK-003 | Solution Architect | Architecture integrity; traceability | Multiple viewpoints | Active |
| STK-004 | Software Architect / PE | Technology decisions; implementation feasibility | Technology Layer | Active |
| STK-005 | Chief Safety & Compliance Officer | Safety constraints; regulatory compliance | Safety Constraint VP | Active |
| STK-006 | QA Engineer | Test coverage; quality attributes | Application Layer | Active |
| STK-007 | DevOps / Platform Engineer | Deployment; operations | Infrastructure VP | Active |
| STK-008 | Implementing Developer | Implementation clarity; interface contracts | Application Layer | Active |
| STK-009 | Sales & Marketing Manager | Business value; market positioning | Business Layer | Inform-only |

**External stakeholders** are added from: Scoping Interview answers, PO's RR stakeholder column, SM's market analysis, and SA's domain knowledge. Each external stakeholder must have a named role, a primary concern, and an engagement level (Active / Passive / Inform-only).

Emit `artifact.baselined` at version 0.1.0 (Stakeholder Map).

---

### Step 3 — Produce Business Drivers and Goals Register

Populate AV §3.4 (Business Drivers and Goals):

1. Extract stated goals and problems from: Scoping Interview answers, user's vision document (EP-A), or user's requirements document (EP-B).
2. Derive implicit drivers from stakeholder concerns (especially external stakeholders' primary concerns).
3. Assign DRV-nnn identifiers sequentially.
4. Assign priority (High / Medium / Low) based on: stakeholder influence level, regulatory mandates (always High), stated urgency from user.
5. Ensure every driver is traceable to at least one stakeholder.

If SM has provided a Market Analysis, cross-reference and incorporate market-driven drivers. If Market Analysis is absent, note: "Market-driven drivers: not yet characterised — pending SM input (non-blocking)."

---

### Step 4 — Sketch Value Streams and Author Capability Overview

**Value stream sketch (Step 4a — precedes capability overview):** Identify 1–3 primary value streams at a strategic level. Create VS-nnn entity stubs (via `write_artifact`) with `status: draft`, naming each VS, its triggering stakeholder, and its end-state value delivered. Stage detail is intentionally incomplete at Phase A — Phase B will refine the stages. This early sketch ensures Phase B has a starting point and anchors the capability overview to stakeholder-facing value.

For each VS-nnn stub:
- `name`: noun phrase ("Software Delivery", "Brownfield Onboarding")
- `triggering-stakeholder`: STK-nnn
- `value-delivered`: one sentence
- `stages`: note "to be detailed in Phase B" — or sketch 2–3 top-level stage names if obvious

**Capability overview (Step 4b):** Produce AV §3.5 using the **ArchiMate Strategy Viewpoint** structure. Capability clusters at this stage serve as a supporting enterprise architecture cross-reference, not the primary Phase B entry point — business services and value streams drive Phase B.

**Constraint:** 3–7 capability clusters at this stage. This is a strategic overview — detail is deferred to Phase B.

For each capability cluster:
- Assign a name (noun phrase, not a verb phrase; e.g., "Customer Engagement" not "Engage Customers")
- Write a one-sentence description of what the cluster encompasses
- State the primary value delivered (to which stakeholder, delivering what) — cross-reference to VS-nnn stub if applicable
- Classify current state: Existing / Planned / Gap
- Classify strategic importance: Core / Supporting / Commodity

**Traceability check:** Every capability cluster must be traceable to at least one DRV-nnn business driver and at least one VS-nnn stub. Capability with no VS anchor is either out of scope or indicates a missing value stream.

---

### Step 5 — Apply Architecture Principles to Engagement Context

Populate AV §3.6 (Architecture Principles Application):

For each principle in the Architecture Principles Register that applies to this engagement:
- Record the Principle ID (P-nnn) and Principle Name
- Write a one-sentence statement of how the principle constrains or guides *this specific engagement*

If a principle does not apply to this engagement, do not include it in §3.6 — include only the principles that have concrete implications for this engagement's architecture decisions.

---

### Step 6 — Produce Safety Envelope Draft

Produce AV §3.7 (Safety Envelope) as a **draft requiring CSCO review and sign-off**.

**SA responsibilities in this step:**
1. State the system boundary for safety analysis: which components, processes, and external interfaces are in scope for safety analysis.
2. Identify high-level hazard categories present in this engagement domain (e.g., "Data loss — irreversible financial records", "Availability failure — operational process interruption", "Regulatory non-compliance — GDPR data handling"). Use domain knowledge and available inputs. Do NOT guess where the regulatory environment is unknown — raise CQ instead (per Knowledge Adequacy Check).
3. Propose initial safety constraints (top-level constraints that subsequent phases must satisfy). State these as constraints, not solutions: "The system must not expose Restricted data to unauthenticated actors" not "Use OAuth2".
4. Reference STAMP/STPA as the analysis method; note the initial control structure scope.
5. Leave the **CSCO declaration** field blank — CSCO must complete this.

Mark `csco-sign-off: pending` in the AV summary header until CSCO completes review.

**Create handoff to CSCO:**
```
handoff-type: review-and-sign-off
from: solution-architect
to: csco
artifact-id: AV-<id>
artifact-version: 0.x.0
section: §3.7 Safety Envelope
required-by: Phase A gate
```

Emit `handoff.created` event.

**If no safety-relevant component can be identified:** Still produce §3.7 with the finding that no safety-relevant components have been identified, and request CSCO confirmation. The CSCO must explicitly confirm this before `csco-sign-off: true` can be recorded.

---

### Step 7 — Author Gap Analysis Table

Produce AV §3.8 (Gap Analysis — Baseline vs Target) covering all four architecture domains:

| Domain | Baseline State | Target State | Gap Description |
|---|---|---|---|
| Business | Description of current business capability state (from user input or "Not characterised — assumed greenfield") | Description of target state implied by business drivers and vision statement | Summary of the gap |
| Application | Current application landscape (from user input or "Not characterised") | Target application capability required | Summary |
| Data | Current data state | Target data requirements | Summary |
| Technology | Current technology constraints | Target technology direction (high-level, not prescriptive) | Summary |

This table is intentionally high-level. Each domain gap is elaborated in the corresponding phase (Phase B for Business, Phase C for Application and Data, Phase D for Technology).

**If the engagement is a greenfield:** State "Not applicable — greenfield engagement" for the Baseline column. State target state from business drivers and vision. Gap is the full target state.

---

### Step 8 — Write Architecture Vision Statement

Produce AV §3.9 (Architecture Vision Statement): a prose statement of 200–400 words describing the target future state.

**Quality requirements:**
- Written for a senior non-architect stakeholder: no technology product names, no acronyms without expansion, no architecture jargon without plain-English explanation.
- Answers these questions: What will the system do? For whom? What will be different from today? What are the defining characteristics (not "it uses microservices" but "it can be scaled and modified component by component without disrupting other components")?
- References the capability clusters from §3.5 by name (not by ID) as organising concepts.
- Consistent with every business driver in §3.4 — no driver should feel unaddressed after reading this statement.
- Mentions the safety envelope at a high level if safety-relevant: "the system is designed to [operate safely under X condition]."

Do not finalise the Architecture Vision Statement until §§3.2–3.8 are complete — the statement synthesises everything in those sections.

---

### Step 9 — Assemble and Baseline AV

1. Assemble all sections (§3.1–3.10) into `architecture-repository/architecture-vision/av-0.x.0.md` per `repository-conventions.md §7` summary header format.
2. Complete the summary header:
   - `artifact-type: architecture-vision`
   - `safety-relevant: true` (always)
   - `csco-sign-off: pending` (until CSCO signs off)
   - `pending-clarifications: [list any open CQ-ids]`
   - `open-issues: [list any assumptions made in lieu of CQ answers]`
3. Submit draft to CSCO for Safety Envelope review (if not already done in Step 6).
4. Once CSCO signs off: update header to `csco-sign-off: true`; remove §3.7 CSCO declaration blank; version becomes 1.0.0.
5. Emit `artifact.baselined` for AV at version 1.0.0.
6. Create handoff to PM: `handoff-type: soaw-input` (SA's contribution to Statement of Architecture Work).

---

### Step 10 — Cast Phase A Gate Vote

Once AV is at version 1.0.0, all blocking CQs are resolved, and the CSCO has signed off on the Safety Envelope:

Emit `gate.vote_cast`:
```
gate_id: gate-A-B
phase_from: A
phase_to: B
result: approved | veto
rationale: [if veto: specific deficiency; if approved: confirmation that AV meets schema quality criteria]
```

**SA self-checklist before casting approved vote:**
- [ ] All AV sections (§3.1–3.10) are populated; no section is marked `[UNKNOWN]`
- [ ] Every capability cluster (§3.5) is traceable to at least one DRV-nnn
- [ ] Stakeholder Register contains all agent roles and all identified external stakeholders
- [ ] Safety Envelope is present; CSCO sign-off recorded (`csco-sign-off: true`)
- [ ] Architecture Vision Statement is non-technical and 200–400 words
- [ ] Gap analysis covers all four domains
- [ ] `pending-clarifications` list is empty (or all items are `assumption`-flagged with PM acceptance)

If any item is not satisfied, cast `gate.vote_cast` with `result: veto` and specific rationale.

---

### Warm-Start Procedure: EP-A

When `entry-point: EP-A` and a user document is provided:

1. Read the user's document in full before producing any output.
2. Produce `architecture-repository/architecture-vision/av-0.1.0.md` by mapping user content to each AV schema section. Use this annotation convention:
   - `[source: user-input]` — content directly from the user's document
   - `[derived: reasoning]` — content SA inferred by sound reasoning from user's document
   - `[UNKNOWN — CQ: CQ-id]` — content that cannot be derived; CQ has been or will be raised
3. For Architecture Principles: if `enterprise-repository/` contains a PR, import it. Otherwise produce PR-0.1.0 draft (Step 1 above).
4. Submit all `[UNKNOWN]` fields to PM as CQs before attempting Phase A gate.
5. Version AV-000 = 0.1.0. Phase A gate requires version 1.0.0.

---

### Warm-Start Procedure: EP-B

When `entry-point: EP-B` and a user requirements document is provided:

1. Read the PO's Warm-Start Requirements Register (RR-000).
2. Produce a **Gap Assessment Matrix** (written to `architecture-repository/architecture-vision/gap-assessment-matrix-0.1.0.md`):
   - List every required section from `architecture-vision.schema.md` and `business-architecture.schema.md`
   - Mark each: Covered (derivable from RR or user doc) / Partially Covered (some content available) / Missing (requires CQ or Phase A/B sprint work)
3. Produce AV-000 from available requirements. Derivation logic: requirements describe *what the system must do*, which implies capability clusters and business drivers. SA derives §3.4 (Drivers) and §3.5 (Capabilities) from the requirements. §3.3 (Stakeholders) is derived from the stakeholder column of the RR.
4. Flag to PM: if the Gap Assessment Matrix shows §3.2, §3.7, and §3.9 are all Covered or Partially Covered, Phase A may qualify as `externally-completed`. PM decides.
5. Raise CQs for Missing items that are blocking for Phase B entry.

---

## Feedback Loop

### Safety Envelope Review Loop (SA ↔ CSCO)

- **Iteration 1:** SA produces Safety Envelope draft (AV §3.7) and sends handoff to CSCO. CSCO reviews; either signs off or returns structured feedback (additions, corrections, vetoes of specific constraints).
- **Iteration 2:** SA incorporates CSCO feedback; revises §3.7; resubmits.
- **Termination:** CSCO signs off; `csco-sign-off: true` recorded.
- **Max iterations:** 2.
- **Escalation if unresolved after 2 iterations:** Raise `ALG-017` if the disagreement concerns a safety-domain knowledge gap (e.g., CSCO identifies a hazard category that SA cannot characterise without user input). Raise `ALG-010` if the disagreement is an inter-agent dispute about the scope or content of the safety envelope. In either case, halt §3.7 finalisation; do not pass Phase A gate.

### Scoping Interview / CQ Resolution Loop (SA → User, via PM)

- **Iteration 1:** SA raises CQs; PM batches and delivers to user; user responds.
- **Iteration 2:** SA raises follow-up CQs on ambiguous answers; PM re-batches; user responds.
- **Termination:** All blocking CQs answered; SA proceeds with any remaining non-blocking items as documented assumptions.
- **Max iterations:** 2 user interactions before SA documents remaining gaps as assumptions with risk flags and notifies PM.
- **Escalation:** If safety-domain CQs are unanswered after 2 iterations, raise `ALG-017`.

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
| ALG-001 | During Safety Envelope authoring, SA identifies that a proposed architecture element would violate a safety constraint already established in the PR or SCO | S1 | Halt production of the violating element; emit `alg.raised`; notify CSCO immediately and PM concurrently |
| ALG-002 | CSCO is unavailable and Phase A gate requires CSCO sign-off on the Safety Envelope | S1 | Halt Phase A gate progression; emit `alg.raised`; PM records and awaits CSCO |
| ALG-010 | SA and CSCO have completed 2 feedback iterations on the Safety Envelope without resolution | S3 | Emit `alg.raised`; PM adjudicates; halt §3.7 finalisation until adjudication is complete |
| ALG-017 | A safety-domain CQ (e.g., regulatory jurisdiction, hazard category for a safety-critical component) is unanswered after 2 sprint cycles and an assumption cannot safely be made | S1 | Halt production of the affected Safety Envelope section; emit `alg.raised`; escalate to user via PM and notify CSCO concurrently |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Architecture Vision (`AV`) | `architecture-repository/architecture-vision/av-<version>.md` | 1.0.0 at Phase A gate | `artifact.baselined` |
| Architecture Principles Register (`PR`) | `architecture-repository/architecture-principles/pr-<version>.md` | 0.1.0 (draft at Phase A; promoted to 1.0.0 at Prelim→A gate) | `artifact.baselined` |
| Stakeholder Map (`SM`) | `architecture-repository/stakeholder-map/sm-<version>.md` | 1.0.0 alongside AV | `artifact.baselined` |
| Safety Envelope (draft, within AV §3.7) | Part of AV document | CSCO signs off before 1.0.0 | Included in AV `artifact.baselined` |
| Gap Assessment Matrix (EP-B only) | `architecture-repository/architecture-vision/gap-assessment-matrix-<version>.md` | 0.1.0 (working document) | Not separately baselined |
| Handoff to PM (SoAW input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (Safety Envelope review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase A gate vote | EventStore | — | `gate.vote_cast` |

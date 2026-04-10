---
skill-id: SM-REQ-FEEDBACK
agent: SM
name: requirements-management-feedback
display-name: Requirements Management — Market Coverage Feedback
invoke-when: >
  PM requests SM to review PO's Requirements Register for market coverage gaps; or SM
  independently identifies a significant change in the competitive landscape post-Phase-A
  that may render Market Analysis demand signals obsolete or introduce new uncovered signals;
  or PM activates SM at EP-H when a Change Record affects market-facing functionality.
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [req-mgmt, H]
trigger-conditions:
  - handoff.created (from PM instructing SM to review RR)
  - artifact.baselined (PO emits RR baseline — SM checks for demand signal coverage)
  - trigger=market-landscape-change (SM identifies significant competitive shift post-Phase-A)
  - sprint.started (phase=H, change affects market-facing functionality)
entry-points: [EP-0, EP-A, EP-H]
primary-outputs: [Requirements Market Coverage Feedback Record]
complexity-class: simple
version: 1.0.0
---

# Skill: Requirements Management — Market Coverage Feedback

**Agent:** Sales & Marketing Manager  
**Version:** 1.0.0  
**Phase:** Requirements Management (cross-phase); Phase H  
**Skill Type:** Cross-phase advisory — feedback production  
**Framework References:** `agile-adm-cadence.md §9`, `raci-matrix.md §3.8`, `clarification-protocol.md`, `algedonic-protocol.md`, `discovery-protocol.md §2`, `framework/agent-personalities.md §3.5`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Requirements Register (RR) | PO (via `project-repository/requirements/`) | Baselined version (1.0.0) preferred; draft (0.x.x) acceptable for advisory review | Blocking — SM cannot produce market coverage feedback without access to current RR content |
| Market Analysis (MA) | SM (self-produced, stored at `project-repository/market-analysis/`) | Baselined version (1.0.0) required; draft not acceptable as reference for cross-phase coverage check | Blocking — MA is the reference against which RR demand signal coverage is assessed; if MA is not baselined, SM must complete SM-PHASE-A-MR first |
| PM instruction or trigger event | PM | `handoff.created` from PM to SM, or algedonic routing; or SM's own market landscape monitoring | Required to initiate this skill — SM does not invoke SM-REQ-FEEDBACK unilaterally; if SM detects a market landscape change, SM raises it to PM first and awaits PM instruction before executing this skill |
| Change Record (CR) | SA (via `architecture-repository/`) | Present only at EP-H trigger | Required only when SM-REQ-FEEDBACK is triggered at EP-H; SM reads the CR to scope the feedback to change-affected demand signals and requirements |
| SWOT Analysis (SWOT) | SM (self-produced, stored at `project-repository/market-analysis/`) | Baselined version (1.0.0) preferred | Non-blocking; if available, SM cross-references SWOT Opportunities against RR coverage in addition to MA Demand Signals |

---

## Knowledge Adequacy Check

### Required Knowledge

- **Current RR content:** SM must be able to read the full RR to assess which requirements address which demand signals and which demand signals are not addressed by any requirement. Without RR read access, this skill cannot proceed.
- **Baselined Market Analysis:** SM must have a baselined MA (version 1.0.0) as the canonical reference for demand signals. If the MA is only at draft status, SM notes this as a limitation: "Feedback is provisional — MA not yet baselined; demand signal set may change before MA 1.0.0."
- **Market landscape currency:** SM must assess whether the baselined MA is still current. If significant time has elapsed since MA baseline or if SM has detected competitive landscape changes, SM notes data-age risk in the feedback record header.
- **Change Record scope (EP-H only):** SM must read the Change Record to understand which product features or customer-facing behaviours are affected before producing a change-scoped market feedback assessment.

### Known Unknowns

| Unknown | Blocking | CQ Target | Feedback Section Affected |
|---|---|---|---|
| Reason for a requirement that does not trace to any MA Demand Signal | No — SM notes the gap and flags to PO for clarification | PO | §3 Market-Obsolete Requirements |
| Customer segment associated with a demand signal when RR requirement is phrased abstractly | No — SM makes a reasonable inference; annotates `[inferred]` | PO | §2 Uncovered Demand Signals |
| Whether a market-apparent gap is already addressed by an in-flight sprint work item not yet in the RR | No — SM flags the gap and recommends PO confirm RR completeness | PO | §2 Uncovered Demand Signals |
| Change Record impact on customer-facing market position (EP-H) | No — SM assesses from available information; annotates confidence | SA or PM (for CR scope clarification) | §4 Change Impact on Market Position |

### Clarification Triggers

SM raises a CQ when:

1. **Market Analysis not baselined:** SM is instructed to execute SM-REQ-FEEDBACK but MA is not at version 1.0.0. SM raises a non-blocking CQ to PM noting that the feedback will be provisional pending MA baseline. SM proceeds with the draft MA as reference but annotates all feedback items: `[provisional — MA not yet baselined at 1.0.0]`.
2. **RR not accessible:** PO has not yet produced or shared the Requirements Register and SM cannot read it from `project-repository/requirements/`. SM raises a blocking CQ to PM for RR access before proceeding. This skill cannot produce useful feedback without RR content.
3. **Significant market landscape change — PM instruction required:** If SM's market monitoring identifies a significant competitive landscape change (e.g., a major competitor has launched a feature that addresses multiple MA demand signals, or a regulatory change is creating new market demand), SM raises this to PM as a potential Phase H trigger or SM-REQ-FEEDBACK trigger — SM does not self-activate. SM raises a `cq.raised` event (directed to PM) describing the change and requesting instruction to execute SM-REQ-FEEDBACK. PM decides whether to activate the skill.

CQ format: per `clarification-protocol.md §3`. CQs raised in this skill are SM-domain CQs routed by PM.

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SM", phase="req-mgmt", artifact_type="requirements-register")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase=<current_phase>)`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/work-repositories/project-repository/market-analysis/` — baselined Market Analysis (MA-nnn, 1.0.0) and SWOT (SWOT-nnn, 1.0.0); SM reads these as the canonical demand-signal and competitive reference
- `engagements/<id>/work-repositories/project-repository/requirements/` — Requirements Register (current version, all RQ-nnn records); SM reads all requirements to assess coverage
- `engagements/<id>/work-repositories/architecture-repository/` — Change Record (CR-nnn) if EP-H trigger; Architecture Vision (AV) for scope confirmation
- `engagements/<id>/clarification-log/` — prior market-domain CQs and answers; if SM previously raised a demand-signal CQ that PO answered, that answer informs the coverage assessment
- `engagements/<id>/handoff-log/` — SM-PHASE-A-MR handoff acknowledgements (confirms PO received MA); SM-PHASE-A-SWOT handoffs
- `enterprise-repository/knowledge-base/` — lessons learned; prior engagement requirements coverage patterns

**External source query types:**

- For market landscape currency check: configured external sources (wiki, Confluence) for recent competitive intelligence or market news that post-dates the MA baseline.

**Target-repo paths (if target-repo configured):**

- `README.md`, product documentation — confirm whether any recently implemented features address demand signals that the RR does not record (i.e., SM identifies implemented-but-unrecorded features).

**Pre-existing artifacts that may reduce CQ load:**

- Baselined Market Analysis (MA-nnn, 1.0.0) → provides the canonical demand signal set for coverage check
- Prior SM-REQ-FEEDBACK records → if this skill has been run before, prior feedback records provide a baseline for delta assessment

**Revisit mode:** This skill does not have a formal revisit mode (it is an advisory skill, not a phase-primary artifact production skill). If SM-REQ-FEEDBACK is run multiple times, each execution produces a new feedback record (incrementing the version suffix). Prior feedback records are retained as audit trail.

---

### Step 1 — Read Current Requirements Register

1. Locate the current RR in `project-repository/requirements/`. Confirm the version and status.
2. Read all RQ-nnn requirement records. For each requirement, extract:
   - RQ-nnn identifier
   - Requirement statement
   - Source stakeholder or input (if recorded in the RR)
   - Any market or demand rationale stated in the requirement (e.g., in a "why" or "context" field)
   - Priority as assigned by PO
3. Build an internal working map: `{RQ-nnn: requirement-summary, priority, stated-demand-context}`.
4. Note the RR version and date in the feedback record header.

---

### Step 2 — Cross-Reference RR Requirements Against Market Analysis Demand Signals

For each Demand Signal in the baselined Market Analysis (DS-nnn):

1. **Coverage check:** Does any RQ-nnn requirement in the RR directly or substantively address this demand signal? A requirement "addresses" a demand signal if:
   - The requirement is traceable to the same customer need the demand signal represents, OR
   - The requirement, if implemented, would satisfy the demand signal (SM's judgment from market perspective).

2. **Classify coverage status:**
   - `Covered`: at least one RQ-nnn addresses this demand signal with at least Medium confidence.
   - `Partially Covered`: one or more requirements are related but do not fully address the demand signal scope (e.g., a demand signal for multi-channel delivery is partially covered by a web-delivery requirement but not a mobile-delivery requirement).
   - `Not Covered`: no RQ-nnn can be reasonably associated with this demand signal.

3. **Annotate confidence of the coverage assessment:**
   - High: the requirement and demand signal clearly correspond; SM has high confidence in the mapping.
   - Medium: SM has inferred a correspondence; the requirement does not explicitly reference the demand signal.
   - Low: SM is inferring coverage from a loosely related requirement; PO confirmation recommended.

4. Record the result in the internal working coverage map: `{DS-nnn: coverage-status, mapped-RQ-nnn[], confidence}`.

---

### Step 3 — Identify Market-Obsolete Requirements

For each RQ-nnn requirement in the RR that does not trace to any MA Demand Signal:

1. **Assess whether the requirement is market-obsolete:** A requirement may be present in the RR for reasons other than market demand (e.g., internal process requirement, regulatory compliance requirement, technical prerequisite). SM does not flag these as obsolete.
2. **Market-obsolete classification:** A requirement is market-obsolete when:
   - It was authored based on a demand signal that SM's current MA identifies as no longer valid (e.g., a feature that addressed a competitor gap that the competitor has since closed, making feature parity less strategically important).
   - The MA explicitly shows that the market has shifted away from this requirement's implied value proposition.
3. **Note:** SM flags market-obsolete requirements as advisory observations only. PO decides whether to remove, reprioritise, or retain them. SM does not modify the RR. SM never removes requirements.
4. **If the time since MA baseline is substantial:** SM applies data-age judgment — a requirement that was market-relevant at MA baseline may still be valid even if SM's current market knowledge has shifted, because the RR was authored based on that earlier MA. SM notes the data-age context: "This requirement was authored at a point when [demand signal] was identified as High confidence. Current MA data-age is [YYYY-MM]. If market conditions have changed, PO may wish to reassess."

---

### Step 4 — Produce Feedback Record

Produce `project-repository/market-analysis/req-feedback-<version>.md`:

**Summary Header:**

```
artifact-type: requirements-market-coverage-feedback
artifact-id: REQFB-<nnn>
version: <major.minor.patch>
status: advisory
agent: SM
phase: req-mgmt | H
engagement-id: <id>
produced-date: <YYYY-MM-DD>
rr-input: RQ-<version> (as-of <date>)
ma-input: MA-<nnn> v1.0.0 (baselined: <date>)
swot-input: SWOT-<nnn> v1.0.0 (if available)
cr-input: CR-<nnn> (if EP-H trigger; else: not applicable)
ma-data-age-assessment: [current | potentially stale — <months> since baseline | stale — recommend MA revisit]
assumptions: >
  [Documented assumptions made in coverage assessment. E.g., "Coverage of DS-nnn by RQ-nnn inferred — PO confirmation recommended."]
```

**§1 — Summary Statistics**

| Metric | Count |
|---|---|
| Total Demand Signals in MA | [n] |
| Demand Signals Covered by RR | [n] |
| Demand Signals Partially Covered | [n] |
| Demand Signals Not Covered | [n] |
| RR Requirements with no MA Demand Signal match | [n] |
| Requirements assessed as market-obsolete | [n] |

**§2 — Covered Demand Signals**

Confirms which demand signals are adequately addressed by current requirements. This section provides a positive confirmation to PO that the RR is capturing market needs — not only gaps.

| DS-nnn | Demand Signal | Mapped RQ-nnn(s) | Coverage Status | SM Confidence |
|---|---|---|---|---|
| DS-001 | [signal] | RQ-005, RQ-012 | Covered | High |
| DS-002 | [signal] | RQ-007 | Partially Covered | Medium |
| ... | | | | |

**§3 — Uncovered Demand Signals**

Demand signals from the Market Analysis that are not addressed by any current requirement. These are advisory flags to PO — not requirements, not mandates. PO decides whether to create requirements from these signals.

For each uncovered demand signal:

- **DS-nnn:** [signal description from MA]
- **MA source confidence:** [High | Medium | Low]
- **Customer segment(s):** [which segments from MA §1 exhibit this demand]
- **Competitive context:** [is this demand already served by a named competitor? If yes: which competitor, at what confidence level]
- **Market urgency:** [Critical | High | Medium | Low — from MA §6 or SM's current assessment]
- **SM recommendation:** [one sentence advisory — e.g., "Consider creating a requirement for [capability area] to address this demand signal, given [competitor] already offers [equivalent capability]." SM frames the recommendation from market perspective; PO decides.]
- **PO action:** `[To be decided by PO]` — SM records PO's disposition if PO provides it during the feedback acknowledgement step.

**§4 — Market-Obsolete Requirements (if any)**

Requirements in the RR that SM assesses as potentially no longer market-relevant based on current MA.

For each potentially obsolete requirement:

- **RQ-nnn:** [requirement summary]
- **Original demand signal (if identifiable):** [DS-nnn or description of the demand it addressed]
- **Market shift:** [description of how market conditions have changed such that this requirement may be less relevant]
- **SM confidence in obsolescence assessment:** [High | Medium | Low]
- **Data-age context:** [MA baseline date vs requirement authoring date]
- **SM recommendation:** [advisory only — e.g., "PO may wish to reassess the priority of RQ-nnn given [market shift description]." SM does not recommend deletion.]
- **PO action:** `[To be decided by PO]`

**§5 — Change Impact on Market Position (EP-H trigger only)**

*Populate this section only when SM-REQ-FEEDBACK is triggered by a Phase H Change Record.*

1. **Change Record summary:** CR-nnn [description], classified as [classification per SA's assessment].
2. **Market-facing features affected:** which customer-visible capabilities or behaviours does this change affect?
3. **Demand signal impact:** does the change affect SM's existing demand signal coverage? Does it:
   - Close a demand signal gap (the change adds a capability that was an uncovered demand signal)?
   - Open a new gap (the change removes or degrades a capability that addressed a demand signal)?
   - Create a new market signal opportunity (the change enables a capability that was not previously in scope but now could address a market need)?
4. **Competitive position impact:** does the change improve, maintain, or reduce competitive position relative to the competitive landscape described in MA §3?
5. **SM recommendation to PO and SA:** [advisory — SM states the market consequence of the change in terms of demand signal coverage and competitive position. SM does not recommend accepting or rejecting the change — that is PM/SA/PO authority.]

---

### Step 5 — Submit Feedback Record to PO; Copy PM as Informational Record

1. Create a handoff event to PO:
   ```
   handoff-type: market-feedback
   from: SM
   to: PO
   artifact-id: REQFB-<nnn>
   artifact-version: <current>
   required-action: review advisory feedback; decide whether to act on uncovered demand signals and market-obsolete requirement flags
   required-by: [end of current sprint or next RR review cycle]
   notes: SM-REQ-FEEDBACK is advisory only. PO decides all requirements actions. SM's uncovered demand signal flags in §3 are not requirements mandates — they are market observations for PO consideration.
   ```
2. Create an informational record to PM:
   ```
   handoff-type: market-feedback-copy
   from: SM
   to: PM
   artifact-id: REQFB-<nnn>
   artifact-version: <current>
   required-action: none — informational copy for sprint log
   notes: SM has delivered requirements market coverage feedback to PO. PM may note §3 significant gaps or §5 change impact (if EP-H trigger) as inputs to sprint planning.
   ```
3. Emit `handoff.created` for both.

**Termination:** SM-REQ-FEEDBACK is complete when the feedback record is submitted to PO and PM via handoff events. SM does not track PO's response or wait for acknowledgement beyond the standard handoff acknowledgement window. PO is the decision authority — SM has fulfilled its advisory function upon submission.

SM does **not** iterate on this feedback record based on PO's response (unlike MA and SWOT, which have defined feedback loops). SM-REQ-FEEDBACK is a one-direction advisory contribution. If PO wants to discuss a specific SM feedback item, PO initiates a CQ to SM or PM; SM responds as a consulted party.

---

## Feedback Loop

This skill's feedback loop is single-direction by design. SM produces the feedback record and submits it. SM is the consulted (`C`) party in the requirements domain; PO is accountable. No SM-PO iteration cycle is required for this skill.

**Consultation responses:** If PO raises a question about a specific SM feedback item (via CQ routed by PM), SM responds within the current sprint with:
- Clarification of the demand signal evidence behind the feedback item.
- Updated confidence annotation if PO provides contradicting evidence.
- Acknowledgement if PO's context leads SM to revise an assessment.

SM never holds a requirements decision hostage to SM's feedback. PO's authority over the RR is absolute. SM's advisory function is fulfilled by the feedback record submission.

### Personality-Aware Conflict Engagement

**Expected tension in this skill's context:** If PO ignores or dismisses SM's uncovered demand signal flags, SM may experience pressure to escalate or to characterise PO's non-response as a governance issue. This would be incorrect — PO's authority over requirements prioritisation is absolute and non-negotiable.

**Engagement directive:** SM's confrontation posture in this skill is deliberately constrained. SM's one assertive move is: if SM has identified an uncovered demand signal with High confidence and material competitive urgency (MA §6: Critical or High), and PO has not acknowledged the feedback record or has explicitly dismissed the signal without stated rationale within the agreed review window, SM notifies PM in the informational handoff follow-up: "PO has not acknowledged REQFB-nnn §3 item DS-nnn, which is High confidence and competitive-urgency High. SM recommends PM note this in the sprint log." SM does not escalate beyond this notification.

**Resolution directive:** SM's advisory function is resolved by PO acknowledging the feedback record. PO may act, defer, or dismiss SM's signals — all are valid PO decisions. The only unresolved state SM escalates is: feedback record not acknowledged by PO after the standard handoff window has elapsed (SM routes this to PM as a non-urgent sprint log item, not an algedonic signal unless the signal is also Critical-urgency).

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="requirements-register"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers <!-- workflow -->

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-015 | SM-REQ-FEEDBACK identifies that a significant number of High-confidence, Critical-urgency demand signals (MA §6: Critical) have no corresponding RR requirements, AND the current sprint plan does not include any work items that would address them — indicating a potential timeline collapse risk where the market window may close before the capability is delivered | S2 | SM emits `alg.raised` to PM; PM assesses sprint plan and routes to PO for requirements prioritisation decision; SM notes the specific demand signals and urgency classification in the algedonic signal payload |
| ALG-001 | During §5 Change Impact analysis (EP-H), SM identifies that a Change Record's market-facing modifications would create or close a regulated market access requirement (e.g., CE marking, HIPAA market access) that CSCO has not assessed | S2 | SM emits `alg.raised` to PM with routing instruction to CSCO; SM annotates §5 with `[CSCO engagement required — regulated market access implication identified]`; SM does not characterise the safety/compliance dimension |

---

## Outputs

| Output | Artifact ID | Path | Version at Baseline | EventStore Event |
|---|---|---|---|---|
| Requirements Market Coverage Feedback Record | REQFB-nnn | `project-repository/market-analysis/req-feedback-<version>.md` | Not separately baselined (advisory artifact); version increments with each execution | Not emitted as `artifact.baselined` — this is an advisory record, not a baselined artifact |
| Handoff to PO | — | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Informational copy to PM | — | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| CQ records (if any) | CQ-nnn | `engagements/<id>/clarification-log/` | — | `cq.raised` |
| Algedonic signals (if triggered) | ALG-nnn | `engagements/<id>/algedonic-log/` | — | `alg.raised` |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase=<current_phase>, key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

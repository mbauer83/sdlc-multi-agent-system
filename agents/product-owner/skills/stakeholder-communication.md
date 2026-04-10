---
skill-id: PO-STAKEHOLDER
agent: PO
name: stakeholder-communication
display-name: Stakeholder Communication — Requirements Updates and Sprint Summaries
invoke-when: >
  At sprint boundaries (sprint.closed event), at phase gate outcomes (gate.evaluated event),
  when a CQ answer resolves a requirements decision that stakeholders need to know about
  (cq.answered event with stakeholder-visible implications), when Phase H change requirements
  impact must be communicated (invoked by phase-h.md Step 5), or when PM explicitly requests
  a stakeholder communication record for user interaction preparation.
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [A, B, C, D, E, F, G, H]
trigger-conditions:
  - sprint.closed (any sprint — triggers sprint requirements summary)
  - gate.evaluated (result=passed — triggers phase transition stakeholder notification)
  - cq.answered (stakeholder-visible requirements decision resolved)
  - handoff.created (from PM requesting stakeholder communication record)
  - invoke from phase-h.md Step 5 (requirements impact notification)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-G, EP-H]
primary-outputs: [Stakeholder communication record (project-repository/requirements/stakeholder-communication/)]
complexity-class: standard
version: 1.0.0
---

# Skill: Stakeholder Communication — Requirements Updates and Sprint Summaries

**Agent:** Product Owner  
**Version:** 1.0.0  
**Phase:** Cross-phase (all phases)  
**Skill Type:** Cross-phase support — stakeholder communication record production  
**Framework References:** `agile-adm-cadence.md §5`, `raci-matrix.md`, `clarification-protocol.md`, `algedonic-protocol.md`, `framework/discovery-protocol.md §2`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Trigger event | PM / EventStore | One of: `sprint.closed`, `gate.evaluated`, `cq.answered`, `handoff.created` (from PM), or direct invocation from phase-h.md | Required — this skill is event-triggered or directly invoked |
| Current Requirements Register (`RR`) | PO (self-maintained) | Latest baselined version | Blocking — communication record must accurately reflect the current requirements state |
| Sprint log (summary of sprint activities) | PM | Latest sprint log entry | Non-blocking — PO reads sprint log for context; if absent, PO summarises from EventStore events |
| Gate evaluation outcome (if triggered by `gate.evaluated`) | PM | Gate outcome record in EventStore | PO reads gate outcome to summarise what was approved or vetoed |
| CQ answer record (if triggered by `cq.answered`) | PM | CQ record with user's answer | PO reads the CQ answer to identify which stakeholders are affected by the decision |
| Phase H requirements impact summary (if invoked from phase-h.md) | PO (self-produced in Phase H assessment) | PO's own impact summary from phase-h.md Step 5 | PO uses this as the primary input for change notification records |
| Stakeholder Register | SA (in AV §3.3) | Version 1.0.0 (baselined alongside AV) | PO reads the Stakeholder Register to identify the correct recipient scope for each communication record |

---

## Knowledge Adequacy Check

### Required Knowledge

- The trigger event and its payload — determines which type of communication record to produce and what content it must cover.
- The current RR — ensures the communication record accurately represents the current requirements state.
- The Stakeholder Register (AV §3.3) — identifies which stakeholders are affected by the communication subject matter.
- The sprint log or gate evaluation record — provides context for the activities being communicated.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Section Affected |
|---|---|---|---|
| Preferred communication format or level of detail for specific external stakeholders | No — PO uses standard format; PM adapts for actual user interaction | PM | Communication record — detail level |
| Whether a specific stakeholder is still active (Stakeholder Register may be stale) | No — PO uses the current Stakeholder Register; flags staleness to SA if detected | SA | Communication record — recipient scope |
| Stakeholder decision required (not just notification) | Yes, if the communication is asking for a decision rather than informing | PM | Communication record — decision framing |

### Clarification Triggers

PO raises a CQ when:

1. **Stakeholder decision required but decision authority unclear:** The communication subject matter requires a decision from a stakeholder, but the Stakeholder Register does not clearly identify who holds decision authority for this type of decision. Non-blocking for the communication record itself; blocking for the decision being requested. PO raises CQ to PM: "Who holds decision authority for [decision topic]?"
2. **Conflicting stakeholder positions:** PO is aware from the engagement history that two stakeholders hold conflicting positions on the requirements topic being communicated. PO flags this to PM before producing the communication record so PM can plan the user interaction to address the conflict directly.

---

## Steps

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PO", phase="all", artifact_type="process")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase=<current_phase>)`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Scoped to the trigger event — read only what is needed to produce an accurate communication record. Proceed to Step 1 only after the relevant sources are checked.

**Expected sources for this skill:**

- `engagements/<id>/work-repositories/project-repository/requirements/` — current RR and RTM
- `engagements/<id>/work-repositories/architecture-repository/architecture-vision/` — Stakeholder Register (AV §3.3)
- `engagements/<id>/work-repositories/project-repository/` — sprint log (PM-produced; PO reads)
- `engagements/<id>/clarification-log/` — open CQs affecting the communication subject matter
- `engagements/<id>/handoff-log/` — recent handoff events that may be relevant to the communication

**Pre-existing artifacts that may reduce CQ load:**

- Stakeholder Register (AV §3.3) → identifies which stakeholders are affected by which capability areas
- Previous communication records → provides continuity context; PO checks for consistency with prior communications

---

### Step 1 — Route by Trigger Type

Based on the trigger event or invoking skill, determine the communication record type to produce:

| Trigger | Communication Record Type | Primary Content |
|---|---|---|
| `sprint.closed` | Sprint Requirements Summary | What requirements work was completed this sprint; RR and RTM status; open CQs; next sprint requirements expectations |
| `gate.evaluated` (result=passed) | Phase Transition Notification | What phase was completed; what architecture artifacts were baselined; what it means for requirements; what is happening next |
| `gate.evaluated` (result=hold or veto) | Gate Hold Notification | Which gate was held or vetoed; what the blocking condition is; what the requirements impact is; what is expected from stakeholders |
| `cq.answered` (stakeholder-visible) | Requirements Decision Notification | What decision was made; how it affects requirements; what RR changes were made as a result |
| Invoked from phase-h.md | Requirements Change Notification | What change is being made; which requirements are affected; what decisions (if any) are required from stakeholders |
| PM request | Ad-hoc Requirements Status | PM-specified content; PO produces a status record with the requested information |

---

### Step 2 — Determine Recipient Scope

Using the Stakeholder Register (AV §3.3):

1. For each communication record type, identify which stakeholders are affected by the subject matter:
   - **Sprint Requirements Summary:** all Active stakeholders in the Stakeholder Register.
   - **Phase Transition Notification:** all Active stakeholders whose primary concerns include requirements or business capabilities (typically all STK-nnn except Inform-only stakeholders receive the full notification; Inform-only stakeholders receive a condensed summary).
   - **Gate Hold Notification:** all Active stakeholders; escalation-relevant stakeholders (those whose authority is needed to resolve the hold) are flagged as `requires-response: true`.
   - **Requirements Decision Notification:** stakeholders attributed to the requirements affected by the decision (`source-stakeholder` field in RR).
   - **Requirements Change Notification (Phase H):** stakeholders attributed to the affected requirements, plus all Active stakeholders if the change affects core business scope (Must-priority requirements).

2. For each recipient stakeholder, determine the appropriate detail level:
   - **Active stakeholders with decision authority:** full detail — specific RQ-nnn IDs, requirement text, impact assessment, and decision request if applicable.
   - **Active stakeholders without decision authority:** standard summary — functional area impact, requirements status overview, no detailed requirement text.
   - **Inform-only stakeholders:** condensed summary — one-paragraph description of what changed and whether any action is required of them.

---

### Step 3 — Produce the Communication Record

**Communication record format:**

Produce `project-repository/requirements/stakeholder-communication/sc-<sprint-id>-<record-type>-<version>.md` with the following structure:

```markdown
---
record-id: SC-<sprint-id>-<sequence>
record-type: [sprint-summary | phase-transition | gate-hold | requirements-decision | requirements-change | ad-hoc]
trigger: [event type and ID that triggered this record]
produced-by: product-owner
sprint: [current sprint identifier]
status: draft
---

# [Record Type Title]

**Sprint:** [sprint identifier]  
**Date:** [sprint date]  
**Prepared by:** Product Owner

---

## Summary

[2–4 sentence plain-language summary of what this communication covers. Written for a senior
non-technical stakeholder. No requirement IDs, no jargon. What happened, what it means,
what comes next.]

---

## Requirements Status Overview

[Relevant to sprint-summary, phase-transition, and gate-hold records.]

| Metric | Count |
|---|---|
| Total Active requirements | |
| Fully traced (RTM) | |
| Partially traced | |
| Untraceable (open gap) | |
| New requirements this sprint | |
| Requirements retired this sprint | |
| Open CQs affecting requirements | |

---

## Key Requirements Developments This Sprint / At This Gate

[Relevant to all record types. Bulleted list — 3–7 items max. Each item is one sentence.
Written in plain language. References functional areas (not RQ-nnn IDs unless the record
is for a stakeholder with decision authority).]

- [Development 1]
- [Development 2]
- ...

---

## Requirements Affected by This Change / Decision

[Relevant to requirements-decision and requirements-change records only.]

| Requirement | Type | Priority | Status Change | Business Impact |
|---|---|---|---|---|
| [Functional description — no jargon] | Functional/NFR/Constraint/Safety | Must/Should/Could | [New/Modified/Retired] | [Plain-language impact on users or business] |

---

## Decisions Required From Stakeholders

[Relevant when one or more stakeholders must respond before work can continue.]

[If no decisions required: "No decisions required at this time. This is an informational update."]

[If decisions required:]

For each decision:

**Decision topic:** [Plain-language description of what must be decided]  
**Context:** [Why this decision is needed now]  
**Options:** [2–3 options, described without jargon]  
**Default if no response by [deadline]:** [What PO/PM will assume if no response]  
**Respond to:** PM (who will route the response to PO)

---

## What Happens Next

[2–3 sentences describing the next phase or sprint, and what requirements work PO will
be doing. Written in plain language. Gives stakeholders context for when they will next
hear from the team.]

---

## Open Requirements Questions

[Non-blocking items that stakeholders may have context on, but which are not yet formal CQs.]

[If none: "No open requirements questions at this time."]

- [Question 1]
- [Question 2]
```

---

### Step 4 — Quality Check Before Submission

Before submitting the communication record to PM:

**Self-checklist:**
- [ ] Summary is written in plain language — no architecture acronyms without expansion, no RQ-nnn IDs in the summary section unless the record is addressed to a technical stakeholder.
- [ ] All RQ-nnn references in the "Decisions Required" section are accompanied by a plain-language description of the requirement.
- [ ] Recipient scope is correct — Active stakeholders are addressed; Inform-only stakeholders receive the condensed version.
- [ ] "Decisions Required" section accurately identifies which decisions need responses and from whom.
- [ ] "What Happens Next" is forward-looking and gives stakeholders adequate context to understand the engagement's current position.
- [ ] The record does not contradict the current RR — all requirement statuses cited are accurate as of the current RR version.
- [ ] The record does not promise scope or features that are not in the RR — PO does not make commitments in communications that are not reflected in the RR.

---

### Step 5 — Submit to PM for Execution

Communication records are not sent directly to stakeholders by PO. PO writes the record; PM executes the actual user interaction.

Create handoff to PM:
```
handoff-type: stakeholder-communication-record
from: product-owner
to: project-manager
artifact-id: SC-<sprint-id>-<sequence>
purpose: PM to execute this communication as part of the next user interaction.
         PO has prepared the content; PM adapts format for the actual interaction medium.
requires-response: [true if any decisions are required from stakeholders; false otherwise]
response-deadline: [sprint identifier by which responses are needed; if requires-response=true]
```
Emit `handoff.created`.

Emit no `artifact.baselined` for communication records — they are supporting documents, not artifacts. They are written to `project-repository/requirements/stakeholder-communication/` and governed by the PO's write authority.

---

### Communication Record Versioning

Communication records are sequentially numbered within each sprint: SC-<sprint-id>-001, SC-<sprint-id>-002, etc. They are not versioned in the semver sense — each record is a point-in-time communication, not a living document. If a communication record requires amendment before PM executes it (e.g., new information arrives after production), PO produces an amended version (SC-<sprint-id>-001a) and notifies PM of the amendment.

---

## Feedback Loop

This skill has no cross-agent feedback loop. The communication record is a PO-internal production that PM executes unmodified (or with PM-specific formatting adaptations). PM does not return the record to PO for revision.

If PM determines that the communication record content is inadequate for the intended stakeholder interaction, PM raises a CQ to PO with specific additional content requirements. PO produces an amended record. Maximum 1 amendment cycle — if PO and PM cannot agree on the communication record content, PM escalates to a user interaction without the PO communication record and notes the gap in the sprint log.

Single-agent skill: the only cross-role interaction in this skill's lifecycle is the handoff to PM. No feedback loop is required for the communication record production itself.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="process"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---


## Red Flags

Pre-escalation observable indicators. Raise an algedonic signal or CQ if two or
more of these are true simultaneously:

<!-- TODO: add 5-7 role-specific observable indicators for this skill -->
- Outputs section of the primary artifact is blank after completing the procedure
- Any required input artifact is missing and no CQ has been raised
- Feedback loop iteration count has reached the maximum with no resolution

## Algedonic Triggers <!-- workflow -->

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-015 | PO self-audit detects that no stakeholder communication record has been produced for the past 2 consecutive sprint closings, despite gate passages and requirements changes occurring during that period | S4 | Emit `alg.raised` (advisory); PM notified; PO produces a catch-up communication record covering the missed sprint closings |
| ALG-006 | PM requests a stakeholder communication record because a gate hold has been triggered by a requirements gap that PO was responsible for detecting and flagging — i.e., the gate hold could have been prevented if PO's requirements currency checks had been performed on schedule | S2 | Emit `alg.raised`; PM investigates root cause; PO identifies which currency check or RTM update was missed; remediate and update requirements-management.md practice if needed |

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

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Stakeholder Communication Record | `project-repository/requirements/stakeholder-communication/sc-<sprint-id>-<sequence>.md` | Not versioned (point-in-time record) | No `artifact.baselined` — supporting document |
| Handoff to PM (communication record for execution) | `engagements/<id>/handoff-log/` | — | `handoff.created` |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase=<current_phase>, key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

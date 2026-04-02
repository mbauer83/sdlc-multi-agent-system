---
skill-id: PM-RETRO
agent: PM
name: retrospective-knowledge-capture
display-name: Retrospective and Knowledge Capture
invoke-when: >
  Activated at every sprint close for a Sprint Retrospective, at every phase gate for a Gate
  Observation, and once at engagement close for the full Engagement Retrospective and promotion review.
trigger-phases: [A, B, C, D, E, F, G, H, req-mgmt]
trigger-conditions:
  - sprint.closed (any)
  - gate.evaluated (any)
  - engagement.closed
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Sprint Retrospective Note, Engagement Retrospective, Lessons Learned, Promotion Request Records]
complexity-class: standard
version: 1.0.0
---

# Skill: Retrospective and Knowledge Capture

**Agent:** Project Manager  
**Version:** 1.0.0  
**Phase Coverage:** Cross-phase; activated at sprint close, phase gate, and engagement close  
**Skill Type:** Knowledge stewardship  
**Framework References:** `agile-adm-cadence.md §5.2 (Retrospective Sync)`, `raci-matrix.md §3.10`, `repository-conventions.md §12`

---

## Inputs Required

- Sprint closeout inputs from all agents (lessons-learned notes, surprise flags, process observations)
- Phase gate records from current engagement
- Algedonic log from current engagement (closed signals and their resolutions)
- CQ log from current engagement (CQ patterns, recurring gaps)
- Defect Register (for implementation-phase retrospectives)
- Compliance Assessment reports (for Phase G retrospectives)

---

## Knowledge Adequacy Check

**Domain knowledge required:**
- Structure of `project-repository/knowledge-base/` — PM maintains this; no external knowledge required.
- Enterprise promotion criteria per `repository-conventions.md §12.1` — applied at engagement close.
- Lessons-learned taxonomy: process lessons (how we worked), architecture lessons (what we learned about the domain), safety lessons (near-misses, constraint gaps), technology lessons (ADR outcomes, toolchain observations).

**CQ triggers:** None specific to this skill. If an agent's retrospective note references an unresolved technical question, PM routes it as a CQ rather than capturing it as a lesson learned.

---

## Sprint Retrospective (per sprint close)

### When activated

Activated at every sprint close. For Solution Sprints, this is the most substantive. For short architecture revision sprints, a brief note suffices.

### Procedure

**Step 1 — Collect agent inputs:**
Request a retrospective note from the sprint's primary agent(s). Notes should cover:
- What worked well (process or technical)
- What was harder than expected (with specific reason)
- What would be done differently
- Any knowledge gaps that slowed work (that should inform framework CQ templates)
- Any algedonic signals triggered — was the threshold right?

**Step 2 — PM synthesis:**
PM synthesises agent notes into a single Retrospective Note. Do not just concatenate agent inputs — identify cross-cutting patterns that span multiple agents' observations.

Retrospective Note format (written to `project-repository/knowledge-base/<sprint-id>-retro.md`):
```markdown
---
sprint-id: <id>
phase: <phase>
date: <ISO date>
participants: [agent roles]
---

## What Worked Well
[1–5 items; specific and actionable]

## What Was Hard
[1–5 items; with root cause where identifiable]

## Process Observations
[Observations about the framework process itself — CQ protocol, handoff timing, gate criteria, etc.]

## Knowledge Gaps Identified
[Gaps that were not resolvable within this sprint; candidates for framework CQ template improvement]

## Action Items
| Item | Owner | Target Sprint |
|---|---|---|
```

**Step 3 — Action item routing:**
Any action item that involves a framework change → flagged for PM review at engagement close (potential framework update recommendation).  
Any action item that involves an architecture artifact → converted to a Phase H Change Record if material.  
Any action item that involves agent process → recorded in PM's decision log for this engagement.

---

## Phase Gate Retrospective (per gate)

At each phase gate — whether passed, blocked, or failed — PM captures a brief gate observation:
- What made this gate easy or hard to pass?
- Were the gate criteria well-calibrated (too strict / too loose)?
- Were all G-holders able to respond within the sprint?

Written as an addendum to the Gate Record in `project-repository/decision-log/<gate-id>-gate-record.md`.

---

## Engagement Close Retrospective

Activated once at engagement close. More comprehensive than sprint retrospectives.

**Step 1 — Synthesise all sprint retrospective notes:**
Review all `project-repository/knowledge-base/*-retro.md` files from the engagement. Identify cross-sprint patterns.

**Step 2 — Produce Engagement Retrospective:**
Written to `project-repository/knowledge-base/engagement-retro.md`:

```markdown
---
engagement-id: <id>
closed: <ISO date>
cycle-level: <capability | segment | strategic>
entry-point: <EP-n>
phases-completed: [list]
total-sprints: <n>
---

## Engagement Summary
[1–2 paragraphs: what was built/analysed, what entry point, any notable scope changes]

## Phase-by-Phase Observations
| Phase | Visits | Key Learnings | Notable CQs | Algedonics Triggered |
|---|---|---|---|---|

## Recurring Patterns (cross-phase)
[Patterns that appeared in multiple phases — e.g., "CSCO sign-off was consistently the gate bottleneck", "EP-G reverse reconstruction underestimated data architecture complexity"]

## Framework Recommendations
[Specific, actionable recommendations for framework improvements — with reference to specific framework document and section]

## Knowledge Promoted to Enterprise Repository
[List of artifact-ids promoted, with their enterprise target paths]
```

**Step 3 — Enterprise Promotion Review:**
SA identifies promotion candidates per `repository-conventions.md §12.1`. PM reviews each candidate:
- Confirm it meets the criteria: reusable cross-engagement, establishes an org standard, or documents a class-of-system safety constraint.
- Write Promotion Request record to `enterprise-repository/governance-log/promotion-request-<id>.md`.
- Await Architecture Board (or PM if no Board) approval.
- On approval: coordinate with SA to copy artifact to enterprise target path with engagement-specific metadata stripped.

Promotion Request format:
```markdown
---
promotion-request-id: PR-<id>
artifact-id: <artifact-id>
artifact-version: <version>
proposed-target: enterprise-repository/<path>/
justification: <why this qualifies for enterprise promotion>
required-modifications: [changes needed to remove engagement-specific content]
status: pending | approved | rejected
---
```

**Step 4 — Knowledge Base consolidation:**
Ensure `project-repository/knowledge-base/` is complete: all sprint retros, engagement retro, lessons learned, and promoted artifact records. This is the PM's final act before marking the engagement as `archived`.

---

## Knowledge Base Structure

```
project-repository/knowledge-base/
  <sprint-id>-retro.md          # Per-sprint retrospective notes
  engagement-retro.md           # Engagement-level synthesis
  lessons-learned.md            # Curated, cross-sprint lessons (PM edits this continuously)
  cq-patterns.md               # Recurring CQ patterns that could be pre-empted in future engagements
  algedonic-review.md          # Review of all algedonic signals: were they correctly calibrated?
```

`lessons-learned.md` is a living document maintained by PM throughout the engagement. It is the primary artifact consumed by future engagement teams as context. PM updates it after each significant phase event, not just at sprint close.

---

## Feedback Loop

**Retrospective note collection:**
- PM requests notes from sprint agents.
- If an agent does not submit a note within one sprint cycle → PM waives the note for short sprints; flags for ALG-015 review for long sprints.
- Termination: PM synthesises note from available inputs; writes retrospective.
- Max iterations: 1 request + 1 follow-up. If still no response, PM writes note from observable outputs.

**Enterprise Promotion Review:**
- PM submits Promotion Request.
- Architecture Board has one engagement sprint cycle to respond.
- If no response: PM escalates to user as advisory (no algedonic; this is an advisory delay).
- Termination: Approval or rejection received and recorded.
- Max iterations: 1 submission + 1 escalation.

---

## Algedonic Triggers

| ID | Condition | Action |
|---|---|---|
| ALG-015 | Sprint log or governance checkpoint not updated for 2 consecutive sprint closings | PM self-alert; remediate immediately; ensure retrospective notes are captured retroactively |

No other algedonic triggers specific to this skill. However, retrospective review may identify historical algedonic miscalibration — documented in `algedonic-review.md` as a framework recommendation, not a current-engagement signal.

---

## Outputs

| Output | Path | Trigger |
|---|---|---|
| Sprint Retrospective Note | `project-repository/knowledge-base/<sprint-id>-retro.md` | Every sprint close |
| Gate Observation (addendum) | `project-repository/decision-log/<gate-id>-gate-record.md` | Every gate evaluation |
| Engagement Retrospective | `project-repository/knowledge-base/engagement-retro.md` | Engagement close |
| Lessons Learned (living doc) | `project-repository/knowledge-base/lessons-learned.md` | Updated throughout; finalised at close |
| CQ Patterns | `project-repository/knowledge-base/cq-patterns.md` | Engagement close |
| Algedonic Review | `project-repository/knowledge-base/algedonic-review.md` | Engagement close |
| Promotion Request Records | `enterprise-repository/governance-log/promotion-request-<id>.md` | Engagement close (if candidates exist) |

---
skill-id: PM-MASTER
agent: PM
name: master-agile-adm
display-name: Master Agile ADM Orchestration
invoke-when: >
  Activated once at engagement start and remains active throughout; orchestrates all phases,
  sprint planning, gate evaluation, CQ routing, and algedonic signal handling.
trigger-phases: [Prelim, A, B, C, D, E, F, G, H, req-mgmt]
trigger-conditions:
  - cycle.initiated
  - sprint.planned
  - sprint.started
  - gate.evaluated
  - cq.raised
  - alg.raised
  - artifact.baselined (any)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Engagement Profile, Sprint kickoff records, Sprint closeout records, Gate records, CQ records, Algedonic records]
complexity-class: complex
version: 1.0.0
---

# Skill: Master Agile ADM Orchestration

**Agent:** Project Manager  
**Version:** 1.0.0  
**Phase Coverage:** All phases (coordination authority)  
**Skill Type:** Master — invoked at engagement start; remains active throughout the engagement lifecycle  
**Framework References:** `agile-adm-cadence.md`, `repository-conventions.md`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md`, `architecture-repository-design.md §4.8`

---

## Runtime Tooling Hint

This PM skill coordinates workflow and quality gates; it does not directly author architecture diagrams. Apply diagram and matrix conventions only when validating or requesting specialist outputs that include diagram artifacts.

## Inputs Required

- Engagement Profile (`engagements/<id>/engagement-profile.md`) — produced during bootstrap; read at every sprint boundary
- Current WorkflowState from EventStore (`event_store.current_state()`)
- Open CQs from `engagements/<id>/clarification-log/`
- Open algedonic signals from `engagements/<id>/algedonic-log/`
- Sprint closeout inputs from all agents (artifact baselines, handoff records, working notes)
- User-provided answers to pending CQs (when resuming after a Clarification Interaction)

---

## Knowledge Adequacy Check

**Domain knowledge required for this skill:**
- Framework knowledge index (query-first): discover relevant policy sections via framework-doc search/list tools, then read only required sections (summary-first, full-read escalation only)
- Current engagement state: open CQs, open algedonics, current phase, phase visit counts — read from EventStore
- Phase gate checklist requirements per `agile-adm-cadence.md §7` and RACI matrix
- Artifact schema requirements per `framework/artifact-schemas/` — to evaluate readiness of submissions

**Predictable gaps at engagement start:**
- User's domain context, regulatory environment, safety classification — addressed by Scoping Interview (EP-0) or Entry Assessment Report (EP-A through EP-H)
- Technology constraints — may be unknown until Phase D
- Deployment environment details — may be unknown until Phase F

**Conditions requiring a CQ before proceeding:**
- Any mandatory Engagement Profile field is blank and cannot be inferred from user's stated inputs
- The entry point classification is ambiguous (user's inputs straddle two EPs)
- The engagement scope is not bounded clearly enough to plan Preliminary Phase

**This skill does NOT raise CQs for architecture domain knowledge** — those are raised by SA, SwA, CSCO. The PM raises CQs only for process-governance knowledge: scope, constraints, stakeholder identification, timeline expectations.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="PM", phase="all", artifact_type="process")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase=<current_phase>)`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Phase 0: Engagement Bootstrap

Performed once per engagement before any sprint begins. Follows `architecture-repository-design.md §4.8`.

**Step 1 — Create engagement directory structure:**
```
engagements/<id>/
  work-repositories/
    architecture-repository/README.md
    technology-repository/README.md
    project-repository/README.md
    safety-repository/README.md
    delivery-repository/README.md
    qa-repository/README.md
    devops-repository/README.md
  workflow-events/
  clarification-log/
  handoff-log/
  algedonic-log/
```

Write `README.md` for each work-repository per `repository-conventions.md §8` format (owner, scope, path governance, access rules, contents).

**Step 2 — Initialise EventStore:**
```python
from src.events.event_store import EventStore
event_store = EventStore(engagement_id="ENG-<id>")
event_store.initialise()   # creates workflow.db with schema; runs Alembic migrations
```

**Step 3 — Write `engagement-profile.md`:**
At `engagements/<id>/engagement-profile.md`. Fill in all frontmatter fields. Mark entry point, cycle level, target repository configuration. Leave phases in scope as `pending` until entry assessment complete.

**Step 4 — Update `engagements-config.yaml`:**
Add the new engagement entry with `engagement-id`, `entry-point`, `status: active`, and `target-repository` fields. This is the only time PM writes to `engagements-config.yaml` unless re-configuration is requested.

**Step 5 — Emit `cycle.initiated` event:**
```python
from src.events.models.cycle import CycleInitiatedPayload
event_store.append(EventEnvelope(
    event_type="cycle.initiated",
    engagement_id="ENG-<id>",
    actor="project-manager",
    payload=CycleInitiatedPayload(
        cycle_level="capability",  # or strategic | segment
        entry_point="EP-0",        # per assessment
        parent_cycle_id=None
    ).model_dump()
))
```

**Step 6 — Perform entry point assessment (see §Entry Point Assessment below).**

**Step 7 — Initial git commit:**
After entry assessment report is delivered (but before sprint work begins), commit:
- `engagements/<id>/engagement-profile.md`
- `engagements/<id>/work-repositories/*/README.md`
- `engagements-config.yaml`
- `engagements/<id>/workflow-events/` (exported events from cycle.initiated)

Commit message format per `repository-conventions.md §9`:
```
[engagement-profile] ENG-<id> v0.1.0 — bootstrap: entry assessment complete

Sprint: bootstrap
Agent: project-manager
Gate: n/a
```

---

### Phase 1: Entry Point Assessment

Performed once immediately after bootstrap. See `sdlc-entry-points.md` for full procedure per entry point.

**1.1 Determine entry point:**
Apply EP classification matrix from `sdlc-entry-points.md §2.1`:
- What artefacts does the user already have?
- Are those artefacts schema-conformant?
- What ADM phases are effectively already done?
- What phases are genuinely missing?

**1.2 Collect CQs from agents:**
Instruct relevant agents to assess user's inputs and submit CQs:
- SA: architecture domain gaps
- SwA (if EP-D or later): technology domain gaps
- CSCO: safety and compliance gaps
- PO (if EP-A/B): requirements domain gaps

Do NOT begin this collection as sequential agent invocations. Invoke all relevant agents concurrently with the user's inputs.

**1.3 Consolidate into Entry Assessment Report:**
Structure per `sdlc-entry-points.md §6`. Order questions by domain (Business → Application/Data → Technology → Safety/Compliance) and by blocking severity. Mark which work proceeds on assumptions and which is blocked.

**1.4 Deliver to user and await response:**
Emit `cq.batched` event for all CQs in the batch. Do not begin sprint work until the user responds, except for work marked "proceeds on documented assumption" in the report.

**1.5 Process answers:**
Route each answer to the relevant agent via `cq.answered` event. Update Engagement Profile with confirmed scope, phases, and target repository details. Update phase status table: `externally-completed` or `pending` per assessment conclusions.

---

### Phase 2: Sprint Planning

Performed at the start of each sprint.

**2.1 Sprint prerequisites check:**
Before planning a sprint, confirm:
- All blocking CQs for this sprint's input artifacts are resolved or have documented assumptions.
- Handoff events for all required input artifacts have been acknowledged by the PM.
- No open S1 algedonic signals affecting this sprint's scope.
- Phase visit count for the target phase is within the 3-visit limit (if revisit).

**2.2 Sprint scope definition:**
Record in `project-repository/sprint-log/<sprint-id>-kickoff.md`:
```markdown
---
sprint-id: <sprint-id>
sprint-type: architecture | business | solution
phase: <ADM phase>
participants: [list of agent roles]
entry-condition: <what triggered this sprint>
input-artifacts: [list of artifact-ids with versions]
output-artifacts: [list of artifact-ids to be produced]
exit-criteria: [specific conditions that define sprint complete]
open-cqs: [list of CQ-ids that are open going into this sprint]
assumptions: [list of assumptions being made due to unanswered CQs]
---
```

**2.3 Emit sprint events:**
```python
event_store.append(EventEnvelope(
    event_type="sprint.planned",
    cycle_id=current_cycle_id,
    actor="project-manager",
    payload=SprintPlannedPayload(...).model_dump()
))
event_store.append(EventEnvelope(
    event_type="sprint.started",
    ...
))
```

---

### Phase 3: In-Sprint Coordination

During a sprint, the PM monitors but does not direct the detailed work of producing agents. PM interventions during a sprint are:

**3.1 CQ management:**
When any agent raises a CQ (`cq.raised` event):
1. Assess severity: blocking (halts specific task) or non-blocking.
2. If blocking and user-facing: add to pending CQ batch; notify user if ALG-016 threshold is approached.
3. If blocking and agent-to-agent: route to the relevant producing agent.
4. If non-blocking: acknowledge; continue monitoring.
5. Record all CQs in `engagements/<id>/clarification-log/cq-<id>.md`.

**3.2 Handoff tracking:**
When any agent emits `artifact.baselined`:
1. Verify handoff event record exists in `engagements/<id>/handoff-log/`.
2. If not: PM writes handoff record (the producing agent should have done this; if not, PM writes it and logs a GV advisory).
3. Monitor consuming agent acknowledgements. If unacknowledged after sprint close, flag as blocker per `repository-conventions.md §5.3`.

**3.3 Algedonic signal handling:**
When `alg.raised` is received:
1. Read the signal from `engagements/<id>/algedonic-log/<id>.md`.
2. Apply routing table from `algedonic-protocol.md §3`:
   - S1: Halt affected work immediately. Notify user. Notify CSCO if SC/RB category. Emit `alg.received` event.
   - S2: Escalate before next sprint unit. Current work may continue in constrained mode.
   - S3: Escalate at sprint boundary.
   - S4: Record for awareness; no work halt.
3. Route to resolution procedure. Emit `alg.resolved` when condition is cleared.

**3.4 Phase revisit detection:**
If `phase.return-triggered` is emitted during a sprint:
1. Read `affected-artifacts` from the event payload.
2. Update phase status in Engagement Profile from `baselined` → `in-revision`.
3. Check visit count: if this would be the 4th visit, emit ALG-005 and escalate to user before continuing.
4. Re-open only the affected artifacts. All others remain authoritative.
5. Adjust sprint scope accordingly.

---

### Phase 4: Phase Gate Evaluation

Performed when the sprint owner signals all phase artifacts are candidate-complete.

**4.1 Read gate checklist from `agile-adm-cadence.md §7`** for the current phase.

**4.2 Evaluate each checklist item:**
For each required artifact:
- Is the artifact at version 1.0.0 or higher? (draft 0.x.x artifacts cannot be authoritative inputs to gate evaluation)
- Does the artifact summary header have all required fields populated? (per `repository-conventions.md §7`)
- Is `pending-clarifications` empty (or all items are `assumption`-tagged with documented risk)?
- Has the CSCO signed off if `safety-relevant: true`?
- Has a handoff event been created and acknowledged by all required consumers?

**4.3 Collect gate votes:**
For each G-holder in the RACI matrix for this gate (from `raci-matrix.md §4`):
- Emit `gate.vote_requested` to each G-holder.
- Wait for `gate.vote_cast` events.
- A single `vote: rejected` from any G-holder blocks the gate.

**4.4 Record gate outcome:**
```markdown
# Gate Record: Phase <X> → <Y>

**Sprint:** <sprint-id>  
**Date:** <ISO date>  
**Result:** passed | blocked | failed  

## Checklist Results
| Item | Status | Notes |
|---|---|---|
| <artifact-id> v<version> | ✓ | |
| CSCO sign-off (SCO) | ✓ | |
| ...  | | |

## G-Holder Votes
| Role | Vote | Notes |
|---|---|---|
| SA | approved | |
| CSCO | approved | |

## Open Items (if blocked)
- [list of items that must be resolved before re-evaluation]

## Action Required
[next steps if blocked/failed; "proceed to Phase Y" if passed]
```

Write to `project-repository/decision-log/<gate-id>-gate-record.md`.

**4.5 Emit gate event:**
```python
event_store.append(EventEnvelope(
    event_type="gate.evaluated",
    payload=GateEvaluatedPayload(
        from_phase="A",
        to_phase="B",
        result="passed",  # passed | blocked | failed
        open_items=[]
    ).model_dump()
))
```

---

### Phase 5: Sprint Closeout

Performed at the end of each sprint, before the next sprint begins.

**5.1 Sprint closeout checklist:**
- All sprint output artifacts are baselined (version 1.0.0+) OR blocked with documented reason.
- All handoff events are created for baselined artifacts.
- All sprint-scope CQs are resolved or documented as assumptions.
- Sprint log record is complete.
- No open S1 or S2 algedonic signals in this sprint's scope.
- Retrospective note received from sprint owner (or explicitly waived for short sprints).

**5.2 Write sprint closeout record:**
```markdown
# Sprint Closeout: <sprint-id>

**Phase:** <phase>  
**Date closed:** <ISO date>  
**Result:** complete | blocked | partial  

## Artifacts Produced
| Artifact ID | Version | Status | Handoff Created |
|---|---|---|---|

## Open CQs Carried Forward
| CQ-ID | Blocking? | Target Agent | Next Action |
|---|---|---|---|

## Algedonic Signals
| ALG-ID | Category | Status | Resolution |
|---|---|---|---|

## Retrospective Note
[Key learnings, surprises, process observations — captured by PM from agent outputs]
```

**5.3 EventStore commit procedure:**
```python
# 1. Export YAML projection for all events since last export
event_store.export_yaml()

# 2. Take a state snapshot
event_store.snapshot_state()

# 3. Git commit — artifacts + sprint log + workflow.db + workflow-events/
# (see commit format in repository-conventions.md §9)
```

**5.4 Git commit at sprint close:**
Stage and commit:
- All newly baselined artifacts in their owning work-repositories
- Sprint log record (`project-repository/sprint-log/<id>-closeout.md`)
- Gate record if a gate was evaluated
- `workflow.db` (canonical EventStore)
- `workflow-events/*.yaml` (YAML projection)
- Any handoff records, CQ records created in this sprint

Commit message format:
```
[sprint-close] <sprint-id> — <one-line result>

Sprint: <sprint-id>
Agent: project-manager
Gate: <gate if applicable, else "n/a">
```

---

### Phase 6: Clarification Interaction

Performed when the PM determines user input is needed (either because a blocking CQ batch is ready, or ALG-016 is triggered).

**6.1 Build CQ presentation:**
Aggregate all open user-facing CQs. Group by domain. Order: most-blocking first. Include:
- CQ-id, domain, precise question
- Why it is needed (what decision it unblocks)
- What assumption is being used in its absence (so user can evaluate risk)

**6.2 Deliver Entry Assessment Report or In-Sprint CQ Batch** to user.

**6.3 On receiving user's response:**
1. Parse each answer.
2. Emit `cq.answered` for each CQ addressed.
3. Route to relevant agent.
4. Update artifact `pending-clarifications` lists.
5. Resume suspended tasks in the order of their blocking dependencies.

**6.4 Unanswered questions:**
CQs not answered remain open. If the silence persists two more sprint cycles after delivery, emit ALG-016 and re-escalate as the highest-priority item in the next Clarification Interaction.

---

### Phase 7: Engagement Close

Performed when the final phase gate exits (typically Phase G exit or Phase H close), or when the user requests engagement closure.

**7.1 Final gate evaluation** (per Phase 4 procedure).

**7.2 Retrospective synthesis:**
Activate `skills/retrospective-knowledge-capture.md`.

**7.3 Enterprise Promotion Review:**
Instruct SA to identify promotion candidates per `repository-conventions.md §12.1`. Raise Promotion Request records in `enterprise-repository/governance-log/` for approved candidates.

**7.4 Engagement archive:**
Update `engagement-profile.md` status to `closed`. Update `engagements-config.yaml`. Emit `engagement.closed` event.

**7.5 Final git commit:**
```
[engagement-close] ENG-<id> — engagement closed; <n> artifacts promoted

Sprint: final
Agent: project-manager
Gate: engagement-close
```

---

## Feedback Loop

**Loop 1 — CQ feedback loop:**
- Producer: any agent raises a CQ
- Consumer: PM consolidates and routes
- Resolution: user or target agent provides answer → PM routes → agent integrates
- Termination: CQ closed when answer integrated OR assumption documented
- Max iterations per CQ: 3 user interactions (if unanswered after 3 batches delivered, PM escalates via ALG-016 and documents as permanent assumption with risk flag)

**Loop 2 — Artifact feedback loop (inter-agent):**
- Producer: producing agent baselines artifact
- Consumer: consuming agent raises structured feedback
- Max iterations: 2 (per `repository-conventions.md §6`)
- Termination: producing agent revises (new version) OR consuming agent accepts as-is with documented note
- Escalation: if iteration 2 exhausted without resolution → PM adjudicates (ALG-010)

**Loop 3 — Phase gate feedback loop:**
- Trigger: gate checklist incomplete or G-holder vote rejected
- Response: blocked items are addressed; re-evaluation scheduled
- Max iterations before escalation: 2 consecutive blocked gate evaluations
- Escalation: ALG-005 (timeline collapse) after 2 extensions without passing

**Loop 4 — Algedonic resolution loop:**
- S1 signals: PM halts work, routes to responsible party, monitors resolution
- Resolution: responsible party confirms condition cleared → PM emits `alg.resolved` → work resumes
- No iteration limit on safety-domain algedonics — they must be resolved before affected work continues

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="process"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Action |
|---|---|---|
| ALG-005 | Phase gate required 2+ extensions without passing | Halt phase; escalate to user for scope reassessment |
| ALG-007 | Agent wrote outside its repository | Halt agent; assess impact; correct immediately |
| ALG-008 | Draft artifact consumed as authoritative input | Invalidate output; require re-work |
| ALG-010 | Two-iteration artifact feedback loop exhausted | PM adjudicates; records decision; enforces resolution |
| ALG-012 | CSCO veto ignored or overridden | Immediate halt; escalate to user; invalidate affected outputs |
| ALG-015 | Sprint log not updated for 2 consecutive closings | PM self-alerts; remediate immediately |
| ALG-016 | User CQ unanswered 2+ sprint cycles | Consolidate and re-escalate as highest-priority user interaction |

The PM also receives and routes all algedonics raised by other agents. This skill does not raise ALG-001 through ALG-004 (safety domain — those are CSCO's triggers) but must act on them as the routing authority.

---

## Outputs

| Output | Path | Trigger |
|---|---|---|
| Engagement Profile | `engagements/<id>/engagement-profile.md` | Bootstrap |
| Work-Repository READMEs | `engagements/<id>/work-repositories/*/README.md` | Bootstrap |
| Entry Assessment Report | Delivered directly to user | Entry assessment |
| CQ records | `engagements/<id>/clarification-log/cq-<id>.md` | CQ raised |
| Sprint kickoff record | `project-repository/sprint-log/<id>-kickoff.md` | Sprint start |
| Sprint closeout record | `project-repository/sprint-log/<id>-closeout.md` | Sprint close |
| Gate record | `project-repository/decision-log/<gate-id>-gate-record.md` | Gate evaluated |
| Handoff event records | `engagements/<id>/handoff-log/<id>-handoff.md` | Artifact baselined |
| Algedonic records | `engagements/<id>/algedonic-log/<id>.md` | Algedonic signal |
| EventStore events | `workflow.db` + `workflow-events/*.yaml` | Every significant state change |

---

## End-of-Skill Memory Close

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase=<current_phase>, key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

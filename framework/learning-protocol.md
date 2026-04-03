---
document: learning-protocol
version: 1.0.0
status: Approved — Stage 4.6
last-updated: 2026-04-03
---

# Learning Protocol

## 1. Purpose

This document specifies how agents in the SDLC multi-agent system capture, store, retrieve, and synthesise **learnings** — structured records of patterns, corrections, and calibrations derived from work performed during engagements.

The goal is to prevent the same class of mistake from recurring without burdening agents with unbounded memory or degrading prompt quality with irrelevant noise. This is achieved through:

1. **Structured recording** triggered only by events with sufficient quality signal (revisions, algedonic signals, resolution of incorrectly-raised CQs)
2. **Retrieval at Discovery Scan time** — before task work begins, not after
3. **Periodic synthesis** at sprint retrospectives — compressing episodic entries into actionable heuristics
4. **Enterprise promotion** for the subset of learnings that are domain-agnostic and high-importance

### Conceptual basis

The design draws on three LLM agent memory approaches:

- **Reflexion** (Shinn et al. 2023): verbal self-correction expressed as natural language, prepended to context for future similar tasks. The core insight: correction expressed in the same language the model reasons in is more effective than any parametric update.
- **Generative Agents** (Park et al. 2023): importance scoring and periodic synthesis. Not every episode warrants a learning; periodic "reflection" synthesises patterns across episodes into higher-order heuristics.
- **ExpeL** (Zhao et al. 2023): insight extraction from task trajectories. What matters is not the raw episode but the extracted rule: "when X, do Y instead of Z."

The system does **not** use embedding-based retrieval or vector stores. Retrieval is metadata-filtered (phase, artifact type, applicability), which is deterministic, transparent, and appropriate for the structured, ontologically-rich context of SDLC work.

---

## 2. Learning Entry Format

Each learning is a single Markdown file with YAML frontmatter stored in the owning agent's role repository under `learnings/`.

### 2.1 File naming

```
<role-repo>/learnings/<ROLE>-L-<NNN>.md
```

Example: `safety-repository/learnings/CSCO-L-003.md`

The sequence number `NNN` is assigned at creation time; it is never reused. The learnings directory also contains `index.yaml` (see §2.3).

### 2.2 Entry fields

```yaml
---
learning-id: <ROLE>-L-<NNN>         # Immutable identifier; role-prefixed
agent: <ROLE>                        # CSCO | SA | SwA | DE | DO | QA | PM | PO | SM
phase: [<phase>, ...]                # ADM phases this applies to; one or more
artifact-type: <type>                # Artifact class where the mistake occurred (e.g., architecture-vision, sco, ta, ac)
trigger-event: <event-type>          # feedback-revision | algedonic | incorrectly-raised-cq | gate-veto
error-type: <type>                   # omission | wrong-inference | wrong-scope | protocol-skip | calibration
importance: <S1|S2|S3>               # S1=critical (algedonic/user-escalation), S2=significant (revision required), S3=minor
applicability: <scope>               # domain-agnostic | domain:<specific-domain> (e.g., domain:healthcare, domain:finance)
generated-at:
  phase: <phase>
  sprint: <N>
  engagement: <engagement-id>
promoted: false                      # true once promoted to enterprise-repository/knowledge-base/learnings/
---

## Trigger

<1–3 sentences describing the concrete situation that generated this learning.
What happened, in what phase, what artifact was involved, what was initially wrong.>

## Correction

<1–3 sentences stating the actionable correction in imperative first-person voice.
This is the text that will be injected into the agent's working context at retrieval time.
It must be specific, actionable, and self-contained — not dependent on remembering the Trigger.>

## Context (optional)

<Any additional detail useful for understanding or deciding whether to promote.
Not injected at retrieval time — authoring context only.>
```

### 2.3 Index file

`learnings/index.yaml` in each role repository is a compact listing of all entries, updated whenever a new learning is written:

```yaml
- learning-id: CSCO-L-001
  phase: [A]
  artifact-type: architecture-vision
  error-type: omission
  importance: S2
  applicability: domain-agnostic
  correction-summary: "When AV describes system as 'internal', check whether it processes employee PII before accepting non-safety classification"
  file: CSCO-L-001.md
  promoted: false
```

The `correction-summary` field is a one-sentence distillation of the Correction section, used for quick filtering without reading the full file. The orchestration layer (tool `query_learnings`) reads only the index for filtering; it reads the full file only for entries that pass the filter.

---

## 3. Trigger Conditions: When to Record a Learning

Recording a learning is not automatic — it requires a quality signal. The following trigger conditions govern when a learning MUST be generated, SHOULD be considered, and MUST NOT be generated.

### 3.1 MUST generate

| Event | Condition | error-type |
|---|---|---|
| **Feedback revision (Iteration 1)** | The skill's Feedback Loop reached Iteration 1 — i.e., the agent's first output was revised in response to feedback. The revision reveals a systematic gap, not just a content preference. | omission / wrong-scope / calibration |
| **Algedonic signal raised** | Any ALG-001 through ALG-C04 signal was raised by this agent or by another agent in response to this agent's output. | protocol-skip / wrong-inference / omission |
| **Gate veto** | CSCO cast a veto vote (for a CSCO agent) or a CSCO veto was raised citing this agent's artifact (for the owning agent). | wrong-scope / omission |
| **CQ resolved by available inference** | A CQ was raised to the user or PM, but the answer turned out to be inferable from artifacts already available in the Discovery Scan. The CQ was unnecessary. | wrong-inference |

### 3.2 SHOULD generate (if recurring or impact ≥ S2)

| Event | Condition |
|---|---|
| **Feedback revision (Iteration 2)** | Same mistake as Iteration 1 was not fully corrected. This is a pattern, not a one-off. Generate with `error-type: calibration`. |
| **User escalation resolved without new information** | The user confirmed an assumption the agent had already hedged rather than provided genuinely new information. The escalation was unnecessary. |
| **Conditional gate approval** | CSCO issued a conditional approval citing a coverage gap in this agent's artifact. The conditional requirement recurred from a prior phase. |

### 3.3 MUST NOT generate

| Situation | Reason |
|---|---|
| **Violation Type B finding (missing coverage in future phase)** | This is an expected gap by design — future phases address it. Not a mistake. |
| **Normal CQ flow** (user provided genuinely new information) | The CQ was correctly raised; the user's answer could not have been inferred. |
| **User changed their mind** | A stakeholder decision changed scope. The agent's initial interpretation was correct at the time. |
| **First-occurrence, low-impact correction** (importance S3 with `frequency-signal: first-occurrence`) | Noise risk outweighs benefit. May be reconsidered if the same pattern recurs. |

### 3.4 Importance classification

| Importance | Criteria |
|---|---|
| **S1** | Algedonic signal was raised; user was directly escalated; safety constraint was implicated |
| **S2** | Artifact revision was required (Iteration 1 reached); gate veto was cast; CQ could have been avoided |
| **S3** | Minor calibration; no revision required; low expected recurrence |

**Default when uncertain:** classify as S2 and generate. It is easier to discard a low-value entry at synthesis time than to recover a learning that was never captured.

---

## 4. Learning Generation Procedure

When a trigger condition (§3.1 or §3.2) is met, the agent generates a learning as part of the skill's closing steps.

### Step LG-1 — Assess trigger

Identify which §3.1 or §3.2 trigger applies. If no trigger applies: do not generate. If multiple triggers apply: generate one entry capturing the highest-importance trigger (do not generate multiple entries for the same underlying mistake).

### Step LG-2 — Classify

Assign:
- `phase` — the current ADM phase
- `artifact-type` — the artifact class where the mistake occurred
- `error-type` — the category from §2.2
- `importance` — from §3.4
- `applicability` — assess whether the correction is domain-agnostic (applies regardless of industry/system type) or domain-specific (only relevant in a particular sector or system class). When uncertain: classify as domain-agnostic and let synthesis refine it.

### Step LG-3 — Author the entry

Write the entry file following the format in §2.2. The most important field is **Correction** — it must be:
- **Imperative and first-person**: "When reviewing an AV that describes an 'internal' system..."
- **Self-contained**: comprehensible without reading the Trigger
- **Specific**: name the artifact section, field, or check that should be different
- **Concise**: 1–3 sentences maximum

Avoid: vague generalizations ("be more careful"), references to specific engagement details that won't generalize, negative framing ("don't forget to...") without the positive alternative.

### Step LG-4 — Assign ID and update index

1. Read `learnings/index.yaml` (or create it if absent). Find the highest existing sequence number for this role.
2. Assign the next sequence number as the new `learning-id`.
3. Write the entry file at `learnings/<ROLE>-L-<NNN>.md` using `write_artifact`.
4. Append the new entry to `learnings/index.yaml` (correction-summary = first sentence of Correction).
5. Emit `learning.created` EventStore event with: `learning_id`, `agent`, `phase`, `importance`, `error_type`.

---

## 5. Retrieval: Step 0.L — Learnings Lookup

**When:** At the start of every skill execution, as the **first sub-step** of the Discovery Scan (before Layer 1 — Engagement State). This ensures prior learnings shape how the agent reads all subsequent artifacts.

**Procedure:**

> ### Step 0.L — Learnings Lookup
>
> 1. Call `query_learnings(phase=<current_phase>, artifact_type=<primary_artifact>, domain=<engagement_domain>)`. The tool reads `<role-repo>/learnings/index.yaml`, filters entries, and returns the `correction-summary` texts for entries that pass ALL of:
>    - `phase` contains the current ADM phase (or is empty — applicable to all phases)
>    - `applicability` is `domain-agnostic`, OR `domain:<engagement_domain>` matches the engagement profile
>    - `importance` ≥ S2 (unless total results < 3, in which case include S3)
>    - Not `promoted: enterprise-superseded` (see §7)
> 2. Additionally call `query_learnings` against `enterprise-repository/knowledge-base/learnings/` (if it exists) with the same filter. Enterprise learnings supplement role-specific ones.
> 3. Sort results: S1 first, then S2, then by recency (most recent sprint first). Cap at **5 entries total** (role-specific + enterprise combined) to avoid context bloat.
> 4. Prepend the matching `Correction` texts (full, not correction-summary) to the agent's working context as: **"Learnings from prior work relevant to this task:"** followed by a numbered list. If no entries match: skip (no section added).
> 5. Proceed to Layer 1 — Engagement State.

**Why first, before discovery:** Learnings shape how the agent interprets what it reads. A learning that says "when AV describes an 'internal' system, check for employee PII handling" changes how the agent reads the AV during Layer 1. Inserting it after discovery would miss this interpretive benefit.

**N=5 cap rationale:** Based on Reflexion and ExpeL empirical findings — more than 5 prepended corrections begin to degrade task-focus and introduce confirmation bias. If more than 5 relevant entries exist, the synthesis step (§6) should have consolidated them into fewer, higher-quality heuristics.

---

## 6. Synthesis: Sprint Retrospective Learning Review

At every sprint retrospective, as part of the PM's `retrospective-knowledge-capture.md` skill, PM prompts each agent to run the synthesis procedure on their sprint's new learning entries.

### 6.1 Synthesis trigger

Synthesis is triggered when any of:
- 3 or more new learning entries were created in the sprint
- 2 or more entries share the same `error-type` and `phase`
- Any S1 entry was created (always synthesise after S1)

If no synthesis trigger is met: no synthesis entry is created (individual entries remain as-is).

### 6.2 Synthesis procedure (agent-side)

1. Read all learning entries created since the last synthesis (or all entries if first synthesis).
2. Identify the most significant pattern: which `error-type` or `phase` combination has the most entries? Which entries have the highest importance?
3. Generate a synthesis entry — a single, higher-order heuristic that captures the pattern across the individual entries:

```yaml
---
learning-id: <ROLE>-SYNTH-<NNN>
agent: <ROLE>
phase: [<phases covered>]
artifact-type: [<types covered>]
trigger-event: synthesis
error-type: <dominant error-type>
importance: <maximum importance of synthesised entries>
applicability: <domain-agnostic if all source entries were; else domain:<most specific common scope>>
synthesised-from: [<ROLE>-L-NNN, ...]
generated-at:
  sprint: <N>
  engagement: <engagement-id>
promoted: false
---

## Pattern

<2–3 sentences describing the recurring pattern across the synthesised entries.
What is the agent systematically missing or mis-calibrating?>

## Correction

<The consolidated, improved heuristic — supersedes the individual entry corrections.
Imperative, first-person, self-contained, 2–4 sentences.>
```

4. Write synthesis entry to `learnings/` and update `index.yaml`. Mark source entries `synthesis-superseded: <SYNTH-ID>` in the index so `query_learnings` returns the synthesis instead of the individual entries.
5. Emit `learning.synthesised` EventStore event.

### 6.3 PM's role at retrospective

PM does not write learning entries (agents generate their own). PM's role in the learning lifecycle:
- Prompts each agent to run synthesis if triggers are met
- Reviews synthesis entries for enterprise promotion candidacy (§7)
- Records cross-role patterns in `project-repository/knowledge-base/` if the same error-type appears in multiple agents' learnings (e.g., both SA and CSCO have omission entries about the same artifact section — this is a handoff gap, not a role-specific issue)

---

## 7. Enterprise Promotion

A learning entry is a candidate for enterprise promotion when it meets ALL of:
- `applicability: domain-agnostic`
- `importance: S1` or `importance: S2`
- The entry (or synthesis entry) recurred in 2+ sprints or was validated by PM as broadly applicable

**Promotion procedure:**
1. SA nominates the entry during engagement closeout promotion review (`retrospective-knowledge-capture.md` §4).
2. PM raises a Promotion Request per `repository-conventions.md §12`.
3. Architecture Board approves (or PM if no Board is constituted).
4. On approval: copy the entry to `enterprise-repository/knowledge-base/learnings/<ROLE>-GLOBAL-<NNN>.md`. Assign new ID. Remove engagement-specific metadata.
5. Update the original entry's `promoted: true` flag in the engagement's `learnings/index.yaml`.
6. Emit `learning.promoted` EventStore event.

Enterprise-promoted learnings are retrieved by ALL agents across ALL engagements (via the enterprise `query_learnings` call in Step 0.L). They become the cross-engagement institutional memory of the agent system.

**Supersession:** When a promoted learning becomes outdated (e.g., a framework rule changes that made the learning obsolete), the Architecture Board marks it `status: deprecated` in the enterprise index. `query_learnings` skips deprecated entries.

---

## 8. Skill File Requirement: `### Learning Generation` Subsection

Every skill file's `## Feedback Loop` section **must** include a `### Learning Generation` subsection. This subsection specifies the learning generation behaviour for this particular skill.

### Required content

```markdown
### Learning Generation

**Triggers (MUST generate):**
- [List the specific §3.1 trigger conditions that apply to this skill's feedback cycle.
  E.g.: "Iteration 1 reached: any revision to [artifact section] triggered by [type of finding]"]
- [E.g.: "Gate veto cast: any Violation Type A finding on [specific section]"]

**Triggers (SHOULD generate if recurring):**
- [List applicable §3.2 conditions for this skill.]

**Default error-type:** [omission | wrong-inference | wrong-scope | protocol-skip | calibration]
  Rationale: [1 sentence explaining why this is the most common error type for this skill]

**Importance floor:** [S1 | S2 | S3]
  Rationale: [Why this is the appropriate floor for this skill's typical mistakes]

**Applicability default:** [domain-agnostic | assess-per-instance]
  Guidance: [1 sentence on how to assess domain-specificity for this skill's typical corrections]
```

The `### Learning Generation` subsection is the authoring specification; the runtime behaviour is driven by the protocol in §3–§4 of this document.

---

## 9. Tool Specification (for Stage 5b implementation)

### `query_learnings(phase, artifact_type, domain) → list[str]`

- Reads `<role-repo>/learnings/index.yaml` and (optionally) `enterprise-repository/knowledge-base/learnings/index.yaml`
- Applies filters: phase match, applicability match, importance ≥ S2 (or S3 if results < 3), not deprecated/superseded
- Sorts: S1 first, then S2, then recency descending
- Caps results at 5 total (role-specific + enterprise combined)
- For each matching entry: reads the full `Correction` section from the entry file
- Returns list of Correction texts (not the full entries)

### `record_learning(entry: LearningEntry) → str`

- `LearningEntry` is a Pydantic model matching the §2.2 schema
- Validates all required fields; raises `LearningSchemaError` if invalid
- Assigns next sequence number from index
- Writes entry file via `write_artifact` (path-constrained to role's learnings/ directory)
- Appends to `index.yaml`
- Emits `learning.created` EventStore event
- Returns assigned `learning-id`

Both tools are registered in `universal_tools.py` and available to all agents. `record_learning` uses the path-constraint from `write_tools.py` — agents can only write to their own role repository's learnings/ directory.

---

## 10. EventStore Events

Two new event types (add to the event taxonomy in `framework/architecture-repository-design.md §4.4`):

| Event | Payload | Trigger |
|---|---|---|
| `learning.created` | `learning_id`, `agent`, `phase`, `importance`, `error_type`, `applicability` | Agent calls `record_learning()` |
| `learning.synthesised` | `synthesis_id`, `agent`, `sprint`, `source_ids[]`, `importance` | Agent runs synthesis at sprint retrospective |
| `learning.promoted` | `learning_id`, `enterprise_id`, `agent`, `engagement_id` | Enterprise promotion approved |

---

## 11. Reference

| Section | Governing Document |
|---|---|
| Discovery Scan procedure | `framework/discovery-protocol.md §2` |
| Step 0.L (Learnings Lookup) | `framework/discovery-protocol.md §10` |
| Sprint retrospective | `agents/project-manager/skills/retrospective-knowledge-capture.md` |
| Enterprise promotion | `framework/repository-conventions.md §12` |
| EventStore event taxonomy | `framework/architecture-repository-design.md §4.4` |
| Tool implementation | `src/agents/tools/universal_tools.py` — `query_learnings`, `record_learning` |
| Learning entry schema | `framework/artifact-schemas/learning-entry.schema.md` |

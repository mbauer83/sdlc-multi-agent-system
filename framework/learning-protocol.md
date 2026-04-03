---
document: learning-protocol
version: 1.1.0
status: Approved — Stage 4.6 (updated Stage 5 design)
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

The design draws on foundational LLM agent memory research and validated production memory patterns:

**Foundational research (2023) — remain valid:**
- **Reflexion** (Shinn et al. 2023): verbal self-correction expressed as natural language, prepended to context for future similar tasks. The core insight: correction expressed in the same language the model reasons in is more effective than any parametric update.
- **Generative Agents** (Park et al. 2023): importance scoring and periodic synthesis. Not every episode warrants a learning; periodic "reflection" synthesises patterns across episodes into higher-order heuristics.
- **ExpeL** (Zhao et al. 2023): insight extraction from task trajectories. What matters is not the raw episode but the extracted rule: "when X, do Y instead of Z."

**2025–2026 additions:**
- **File-based memory with MEMORY.md index** (Claude Code production pattern, 2026): Anthropic's Claude Code memory system uses exactly this pattern — individual human-readable Markdown files, a compact index (first 200 lines loaded every session), topic files loaded on-demand. An "AutoDream" background consolidation sub-agent prunes stale entries at sprint boundaries — this maps directly to the PM `retrospective-knowledge-capture.md` synthesis step. The file-based approach is validated as production-grade at the model capability level this system targets.
- **Anthropic `memory_20250818` tool** (official Claude API, 2026): Anthropic's official client-side memory tool type — commands: `view`, `create`, `str_replace`, `insert`, `delete`. The system prompt injected when enabled reads: "ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE" — structurally equivalent to Step 0.L in this protocol. In Stage 5, `LearningStore` may optionally use this tool type as its backend interface instead of direct file I/O, enabling the same memory patterns that Claude Code uses internally.
- **LangGraph BaseStore** (LangGraph 0.2+, 2025): LangGraph's memory layer provides a `BaseStore` abstraction with namespace-path key-value storage. The idiomatic namespace for this system: `(engagement_id, agent_role, phase)` tuple — e.g., `("ENG-001", "csco", "A")`. In Stage 5 the learning store is implemented using `LangGraph SQLiteStore` (reusing `workflow.db`) as the runtime backend, with the file-based `learnings/` directory as the durable serialisation layer.
- **A-MEM graph connectivity** (Adaptive Memory for Agents, 2025): Structured learnings maintain explicit `related` links to other entries, forming a lightweight traversal graph. This allows `query_learnings` to optionally "expand" a result set by following related-entry pointers when the primary filter returns < 3 results.
- **Memory consolidation as first-class operation**: Synthesis is not only a sprint-boundary activity — it must also be triggered when the unsynced index grows beyond 20 entries to prevent context-bloat at retrieval time.

**Memory type coverage (gap analysis):** The current learning protocol addresses **procedural memory** (corrections, calibrations, heuristics — "when X, do Y"). MIRIX (2026) and Mem0 identify three additional memory types not currently addressed: *episodic* (what specifically happened in past engagements), *semantic* (domain facts about the client's industry/system), and *resource* (shared documents, reference files). These are out of scope for this protocol version — they are addressed by the enterprise repository, engagement profile, and external source adapters respectively. Future protocol versions may formalise episodic retrieval (past engagement outcomes) and semantic caching (domain-fact extraction from CQ answers).

**Design invariants that hold despite evolution:**
- The system does **not** require a vector database for normal operation. Retrieval is primarily metadata-filtered (phase, artifact type, applicability), which is deterministic, transparent, and appropriate for the structured, ontologically-rich context of SDLC work.
- Optional semantic retrieval (§12) supplements metadata filtering only for the enterprise knowledge base query when the corpus exceeds 50 entries and `sqlite-vec` is available. It never replaces metadata filtering.
- The N=5 context cap is retained; research consistently shows > 5 prepended corrections degrade task-focus.
- Per-role skill scoping (each agent sees only its own ≤12 skills, not all 43+) is validated by the empirical finding that agent accuracy degrades significantly past 30 available tools — our scoping design is correct and must not be relaxed.

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
  artifact-type: safety-constraint-overlay
  error-type: omission
  importance: S2
  applicability: domain-agnostic
  correction-summary: "When producing Phase A SCO baseline, check whether any AV system described as 'internal' processes employee PII — if so, add as a safety-critical data scope constraint"
  file: CSCO-L-001.md
  promoted: false
  related: []           # IDs of related entries in this index (or enterprise index) — used by §12 expansion
  synthesis-superseded: null  # Set to synthesis entry ID when this entry is superseded
```

**`artifact-type` assignment rule:** Use the PRIMARY OUTPUT artifact of the skill, not the artifact reviewed or consumed as input. In the example above, CSCO is producing the `safety-constraint-overlay` (Phase A SCO baseline) when the mistake occurred — the AV was the input artifact being reviewed. The correction text describes what to examine in the input AV, but the learning is tagged by CSCO's output so that `query_learnings(artifact_type="safety-constraint-overlay")` retrieves it at the start of the next CSCO gate review skill. Had it been tagged `architecture-vision`, it would never be retrieved by CSCO's Step 0.L.

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
- `artifact-type` — the primary OUTPUT artifact of this skill (the artifact being produced when the mistake occurred). Not the input artifact reviewed or consumed. For procedural mistakes not tied to a specific output artifact, use `process`.
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

### `query_learnings(phase, artifact_type, domain, expand_related=True) → list[str]`

- Reads `<role-repo>/learnings/index.yaml` and (optionally) `enterprise-repository/knowledge-base/learnings/index.yaml`
- Applies filters: phase match, applicability match, importance ≥ S2 (or S3 if results < 3), not deprecated/superseded
- **Graph expansion (§12):** If primary filter returns < 3 results AND `expand_related=True`, traverse `related` pointers of matching entries to collect additional candidates; apply the same filters to candidates; add up to 2 expanded entries to the result set
- **Semantic supplement (§12):** If primary + expanded results < 3 AND enterprise corpus ≥ 50 entries AND `sqlite-vec` is available: run embedding similarity against the enterprise index using the current task context as query; add top-1 result if relevance score > 0.75
- Sorts: S1 first, then S2, then recency descending
- Caps results at 5 total (role-specific + enterprise + expanded combined)
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

---

## 12. Stage 5 Implementation Guidance

This section provides design decisions for the Python implementation of the learning store in Stage 5. It does not add new protocol requirements — it specifies *how* §8–§9 are implemented.

### 12.1 Storage Backend: LangGraph BaseStore

The learning store is implemented using **LangGraph's `BaseStore`** (`langgraph.store.base.BaseStore`), available from LangGraph 0.2+. This provides:
- Namespaced key-value storage: `(engagement_id, agent_role)` namespace per engagement
- Cross-thread access: learnings created by one agent invocation are visible to the next
- Pluggable backends: `InMemoryStore` for testing, `SQLiteStore` for production (reuses the existing `workflow.db` connection)

**Implementation contract:**
```python
# LearningStore wraps LangGraph BaseStore for typed learning access
# Namespace: (engagement_id, role_id, "learnings")  — e.g., ("ENG-001", "csco", "learnings")
# Key: learning_id                                   — e.g., "CSCO-L-003"
# Value: LearningEntry (Pydantic model, serialised to JSON by the store)
# Cross-role index namespace: (engagement_id, "pm", "cross-role-learnings")
# Enterprise namespace: ("enterprise", "global", "learnings")  — read-only for non-PM agents
```

**Durable serialisation:** On every `record_learning()` call, after writing to the store, the implementation also writes the `.md` file and updates `index.yaml`. The store is the runtime access path; the files are the durable, git-tracked record. `query_learnings()` reads from the store (fast, in-memory); the files are read only for disaster recovery (store rebuild from YAML/files).

**Store rebuild:** If the store is empty on startup (new session, new deployment), `EventStore.replay()` replays `learning.created` events and rehydrates the store from the `.md` files. This is a one-time startup cost, not a per-query cost.

### 12.2 Semantic Retrieval Tier (Enterprise Knowledge Base Only)

Semantic retrieval supplements metadata filtering only for the enterprise `query_learnings` call when:
- The enterprise `learnings/index.yaml` has ≥ 50 entries, AND
- The `sqlite-vec` extension is loadable (Python `sqlite-vec` package installed), AND
- The primary metadata filter returned fewer than 3 results

**Implementation:**
```python
# On enterprise index load (cached, refreshed at session start):
#   embed all correction-summary texts using a lightweight embedding model
#   (prefer sentence-transformers/all-MiniLM-L6-v2 — 22MB, no API call required)
#   store vectors in sqlite-vec virtual table within workflow.db
# On semantic query:
#   embed the current task context (agent role + phase + artifact_type + skill description)
#   query sqlite-vec for top-3 nearest; apply relevance threshold (cosine > 0.75)
#   return at most 1 additional result beyond metadata-filtered set
```

**Rationale for conservative design:** Semantic retrieval can surface thematically related learnings with different metadata labels (e.g., a CSCO `omission` learning about PII is semantically relevant to an SA learning about data classification). The 0.75 threshold and max-1 addition ensure the semantic signal is high-confidence before injecting into context.

### 12.3 Graph Expansion via `related` Links

Each `index.yaml` entry has a `related: [<id>, ...]` field. When the primary filter returns < 3 results:

1. Collect all `related` IDs from matching entries.
2. Load those entries from the same index (or enterprise index if the pointer crosses).
3. Apply the same metadata filters (phase, applicability, importance).
4. Add at most 2 qualifying entries to the result set.
5. These entries are marked with `[expanded]` in the Correction text so the agent knows they are related-expansion results, not direct matches.

`related` links are set at synthesis time (by the synthesising agent) and at enterprise promotion (by the Architecture Board). They are not set automatically.

### 12.4 Cross-Agent Learning Visibility

The file-based system is role-siloed (each agent reads its own `learnings/` directory). Cross-agent visibility is achieved at two levels:

**Level 1 — Enterprise promotion** (already in §7): Widely applicable learnings are promoted to `enterprise-repository/knowledge-base/learnings/`. All agents read this in Step 0.L. This is the primary cross-agent channel.

**Level 2 — PM cross-role synthesis index** (new in Stage 5): When PM's retrospective synthesis identifies the same error-type appearing in 2+ roles' learnings within the same sprint, PM writes a cross-role synthesis entry to `project-repository/knowledge-base/cross-role-learnings/index.yaml`. Agents read this as a third index in Step 0.L (after role-specific and enterprise):
```
query_learnings sources (in order):
  1. <role-repo>/learnings/index.yaml                              — role-specific
  2. enterprise-repository/knowledge-base/learnings/index.yaml    — enterprise
  3. project-repository/knowledge-base/cross-role-learnings/index.yaml  — cross-role (new)
```
Cross-role entries use the same format as regular learnings. They are authored by PM, not by the role agent. The `agent` field is set to `"PM-synthesis"`.

### 12.5 Consolidation Trigger

The existing sprint-boundary synthesis trigger (§6.1) is supplemented by a **growth trigger**: if `index.yaml` has more than 20 entries that are not `synthesis-superseded`, PM is alerted at the next sprint planning check-in to request synthesis from the affected agent. This prevents index bloat that would degrade the N=5 cap's effectiveness. The alert is an `algedonic`-adjacent signal routed to PM's decision queue (not a full ALG signal — it is informational, not urgent).

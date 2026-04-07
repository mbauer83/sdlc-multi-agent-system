# Clarification Protocol

**Version:** 1.2.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager  
**Last Updated:** 2026-04-08

---

## 1. Purpose

Every agent in this system operates under a **bounded knowledge model**: it knows what is in its skill files, the framework documents, and the artifacts it has retrieved. It does not know what it has not been told. This protocol governs what an agent must do when it detects that its current knowledge is insufficient to produce a correct, complete, or responsible output.

Knowledge inadequacy is not a failure state — it is an expected, normal occurrence, especially at the beginning of an engagement, when entering mid-SDLC, or when a domain is novel. The protocol specifies how agents surface knowledge gaps cleanly, route questions to the right party, suspend only the work that genuinely cannot proceed, and resume effectively once answers arrive.

**This protocol is a peer of the Algedonic Protocol.** Algedonic signals handle urgency and risk. Clarification Requests handle knowledge gaps. Both result in a work suspension, but through different channels and with different resolution authorities.

---

## 2. The Knowledge Adequacy Self-Assessment

### 2.1 When to Perform a Self-Assessment

An agent MUST perform a knowledge adequacy self-assessment at the following moments:

1. **At skill activation** — before beginning any task defined in a skill file, the agent confirms it has the inputs specified in that skill's `## Inputs Required` section.
2. **Before producing any section of a binding output** — before writing any section of a Deliverable (version 0.x.x or higher), the agent confirms it has sufficient domain knowledge for that section.
3. **When encountering an ambiguity** — when the available artifacts or context contain an ambiguity that would cause the agent's output to bifurcate into materially different outcomes depending on which interpretation is correct.
4. **When detecting a domain gap** — when the task requires knowledge about the user's specific business domain, technology context, or organisational context that is not present in any available artifact.
5. **Before a phase gate attestation** — before an agent records its sign-off on a phase gate checklist item, it confirms that it has verified the relevant artifacts with sufficient depth.

### 2.2 Self-Assessment Decision Rule

```
For each task T:

1. List all information required to produce T correctly and completely.
2. For each required item, check:
   a. Is it present in a baselined artifact? → Retrieve per confidence-threshold protocol.
   b. Is it derivable from available context by sound reasoning? → Proceed with explicit reasoning chain.
   c. Is it a reasonable assumption given domain standards? → Proceed with assumption DOCUMENTED in Working Notes.
   d. Is it unknown and not inferable? → CLARIFICATION REQUIRED.

3. If any item falls into category (d):
   - If T can be partially completed without it → proceed with partial output, flag gap.
   - If T cannot proceed without it → SUSPEND task, raise Clarification Request.
```

### 2.3 What Constitutes Insufficient Knowledge

The following conditions always constitute insufficient knowledge requiring a Clarification Request:

- **Undefined scope:** The task refers to a system, process, domain, or stakeholder group that has not been characterised in any available artifact.
- **Conflicting constraints:** Two available artifacts impose constraints that cannot be simultaneously satisfied, and the resolution requires a value judgement or business decision.
- **Missing domain-specific facts:** The correct output depends on a factual characteristic of the user's specific organisation, system, or environment (e.g., regulatory jurisdiction, existing technology stack, organisational structure) that is not present in any artifact.
- **Unresolved requirements ambiguity:** A requirement in the Requirements Register is stated ambiguously and the two plausible interpretations would produce materially different architecture decisions.
- **Safety-domain unfamiliarity:** A task requires STPA analysis of a hazard domain (physical, chemical, cyber-physical, medical, financial, etc.) where the agent lacks sufficient contextual knowledge to identify hazards reliably.

The following conditions do NOT require a Clarification Request:
- General knowledge about technologies, standards, or best practices — use internal knowledge.
- Preferences between architecturally equivalent options — make a reasoned choice and document it as an ADR.
- Stylistic or formatting decisions — exercise judgement.

---

## 3. Clarification Request Format

When an agent determines that a Clarification Request is needed, it writes a `CQ` (Clarification Query) record to `engagements/<id>/clarification-log/<sprint-id>-CQ-<sequence>.md`. The `<id>` is the current engagement identifier from the Engagement Profile.

```markdown
---
cq-id:            # <sprint-id>-CQ-<sequence>, e.g. AS-A-CQ-001
raised-by:        # agent role
raised-in:        # sprint identifier
target:           # User | PM
status:           # open | answered | superseded | withdrawn
blocking:         # true | false (is work suspended pending this answer?)
blocks-task:      # description of the specific task or artifact section that is blocked
artifact-in-progress: # artifact-id if a draft is being held (e.g. AV-001 v0.2.0)
---

## Context
[2–4 sentences explaining what the agent is working on and why this information is needed.
Be specific: reference the artifact, phase, and skill being executed.]

## What Is Known
[Bullet list of what the agent already has available — so the respondent can see the existing basis
and avoid repeating information already captured.]

## What Is Unknown
[Precise statement of the missing information. One or more specific, answerable questions.
Do NOT ask open-ended questions like "tell me about your business" — ask closed or bounded questions
like "Is this system subject to GDPR? If yes, which data categories are in scope?"]

## Questions
1. [Specific question — the more bounded, the better]
2. [...]

## Impact of Non-Response
[What the agent will do if this question is not answered: either proceed with a documented
assumption (state the assumption), or hold the task indefinitely.]

## Partial Progress
[Description of any partial output that has been produced while the blocking question is outstanding.
This section exists so the respondent knows what work is already done and what remains.]
```

### 3.1 Question Quality Standard

Every question in a Clarification Request MUST be:

- **Specific** — refers to a concrete decision, fact, or constraint, not an open-ended topic
- **Bounded** — has a finite answer space (yes/no, a choice, a specific value, a document reference)
- **Actionable** — the agent can immediately continue work once the answer is received
- **Non-redundant** — not already answerable from available artifacts (if it is, the CQ should be withdrawn)

Questions that fail this standard should be reformulated before the CQ is issued. A vague question produces a vague answer and does not unblock work.

### 3.2 Interaction Taxonomy (Wave 1)

This protocol uses two interaction classes and one explicit non-interaction boundary:

| Class | Definition | Typical Initiator | Typical Responder | Persistence Contract | Suspension Contract |
|---|---|---|---|---|---|
| User-facing Clarification Interaction (CQ) | Missing user/domain facts that cannot be retrieved from available artifacts or sources | Specialist agent or PM | User | `cq.raised`; `cq.batched` when PM consolidates; `phase.suspended` / `phase.resumed` when blocking | Blocking only when `blocking: true`; suspension scope is the minimum blocked task unit |
| Agent-directed Coordination Interaction | Inter-agent feedback, handoff, arbitration, review, or escalation | Specialist agent or PM | Producing specialist and/or PM (PM-governed routing) | `handoff.created`, `specialist.invoked`, `specialist.completed`, `decision.recorded`, `gate.evaluated`, `review.pending`; algedonic events when applicable | Non-blocking by default; may become blocking only if PM issues a hold or routes into CQ/algedonic handling |

**Boundary (non-goal for Wave 1):** Agent tool retrieval (`list/search/read/count/find`) is tool-use behavior, not an interaction class. Retrieval is governed by discovery and tool contracts (`framework/discovery-protocol.md`, `framework/tool-catalog.md`) and is never routed as a CQ.

---

## 4. Routing Rules

Clarification Requests are routed based on the nature of the gap:

| Gap Type | Route To | Rationale |
|---|---|---|
| Missing domain context (business, technology, regulatory) about the user's specific situation | **User** | Only the user has this knowledge |
| Ambiguity in an existing artifact owned by another agent | **Producing agent** (via structured feedback, `repository-conventions.md §6`) | Not a knowledge gap — it is an artifact quality issue |
| Conflicting constraints between two artifacts | **PM** (who routes to owning agents) | PM adjudicates inter-agent artifact conflicts |
| Scope ambiguity (is X in or out of scope?) | **PM** | Scope decisions require PM authority |
| Safety domain knowledge required for STPA analysis | **User** or **CSCO** if CSCO has the knowledge | Safety-domain specifics cannot be assumed |
| Architectural preference where both options are valid | **Resolved internally** — agent makes a reasoned choice and documents it as an ADR | Not a knowledge gap |

**User-facing CQs are the primary focus of this protocol.** Agent-to-agent gaps are handled by the structured feedback loop (`repository-conventions.md §6`).

### 4.2 Interaction Class Routing Contract

| Interaction Class | Who Initiates | Who Responds | PM Routing Responsibility | Required Event Touchpoints | Blocking Behavior |
|---|---|---|---|---|---|
| User-facing Clarification Interaction (CQ) | Specialist or PM | User | PM may batch, present, and resume work after answer integration | `cq.raised`, `cq.batched` (optional), `phase.suspended` / `phase.resumed` (if blocking) | Blocking when `blocking: true` only |
| Agent-directed Coordination Interaction | Specialist or PM | Specialist and/or PM | PM governs re-assignment, arbitration, gate sequencing, and review routing | `handoff.created`, `specialist.invoked`, `specialist.completed`, `decision.recorded`, `gate.evaluated`, `review.pending` | Non-blocking by default; PM can place explicit hold |

### 4.1 Inter-Agent Clarification Boundary

To avoid duplicating governance channels, direct agent-to-agent CQs are not introduced as a separate protocol path.

- If the issue is artifact ambiguity or quality: use structured feedback/handoff to the producing agent.
- If the issue is cross-artifact conflict or scope arbitration: route to PM for decision and re-assignment.
- If user/domain facts are missing: raise CQ to User.

This keeps CQ semantics reserved for missing knowledge, while inter-agent coordination remains in the feedback/handoff control loop.

---

## 5. Work Suspension and Partial Progress

### 5.1 Suspension Rules

When a CQ with `blocking: true` is raised:

1. **The specific task section** that requires the missing information is suspended.
2. **All other sections** of the same artifact that do NOT require the missing information MUST continue. Suspension is scoped to the minimum blocked unit, not the entire artifact or sprint.
3. The draft artifact (if one exists) is written to its canonical path at its current partial state with `status: draft` and `pending-clarifications: [CQ-id]` in its summary header.
4. The PM is notified via a handoff event marking the CQ as a sprint blocker.

### 5.2 What CAN Continue Without an Answer

The following work can always proceed in parallel with an open CQ:

- Sections of the artifact not dependent on the missing information
- Other artifacts in the same sprint not dependent on the missing information
- Business Stream work (requirements elicitation may actually surface the answer)
- Retrospective notes and knowledge base updates
- Review of other agents' artifacts

### 5.3 Assumption-Based Continuation

If a CQ is raised with `blocking: false`, the agent proceeds with a **documented assumption**. The assumption must be:

1. Recorded in the artifact's `## Assumptions` section (to be added to every artifact schema's optional sections)
2. Flagged in the artifact summary header under `open-issues`
3. Marked with the CQ-id so it can be resolved when the answer arrives
4. Conservative — the assumption must be the safest reasonable default, not the most optimistic

---

## 6. Answer Integration

When a CQ receives a response:

1. **PM or the raising agent** updates the CQ record: `status: answered`; appends the answer under a `## Response` section.
2. **The raising agent** reviews the answer against the partial work already done:
   - If the assumption made (if any) is validated → confirm assumption, remove `pending-clarifications` flag
   - If the assumption is contradicted → revise the relevant artifact sections; increment version; re-issue handoff event if already handed off
   - If the answer introduces new gaps → raise a new CQ (linked to the original)
3. **The artifact** is updated: `pending-clarifications` field cleared (or updated to remaining CQs); version incremented; draft progresses toward baseline if gate criteria are met.
4. **PM** removes the sprint blocker if the blocking CQ is resolved.

---

## 7. CQ as Sprint Metric

The PM tracks open CQs as a sprint health metric:

| Metric | Description | Action Threshold |
|---|---|---|
| **Open User CQs** | CQs awaiting user response | > 3 open simultaneously → PM consolidates into a single user interaction |
| **CQ Age** | Sprints elapsed since CQ raised | > 2 sprints without answer → PM escalates to algedonic signal (ALG-016) |
| **Assumption Density** | Artifact sections proceeding on undocumented assumptions | Any undocumented assumption → immediate CQ required |
| **CQ Retraction Rate** | CQs raised then found answerable from existing artifacts | > 20% retraction → agent self-assessment procedure needs review |

---

## 8. Skill File Requirement

Every skill file in `agents/*/skills/` must include the following section:

```markdown
## Knowledge Adequacy Check

### Required Knowledge
[List of domain knowledge, context, or decisions that must be present or confirmed
before this skill can produce correct outputs. Reference artifact IDs where applicable.]

### Known Unknowns
[Any domain-specific knowledge gaps that are predictably present for this skill
(e.g., "regulatory jurisdiction is always unknown at Phase A entry and must be resolved
via CQ before compliance constraints can be set")]

### Clarification Triggers
[Specific conditions that will cause this skill to raise a CQ rather than proceed.
Reference CQ routing rules from `clarification-protocol.md §4`.]
```

This section is REQUIRED. The statement "no clarification triggers identified for this skill" is a valid and complete entry if accurate — but it implies the author has verified that all inputs required by this skill are always derivable from available artifacts and standard knowledge.

---

## 9. Integration with Other Protocols

| Protocol | Relationship |
|---|---|
| Confidence-Threshold Retrieval (`repository-conventions.md §4`) | Governs *artifact reading depth*. A CQ is raised when full retrieval is insufficient — the information is simply not in any artifact. |
| Algedonic Protocol (`algedonic-protocol.md`) | A CQ that remains unanswered for > 2 sprints triggers ALG-016. A CQ about a safety-critical gap may also trigger ALG-001 or ALG-003. |
| Feedback Loop (`agile-adm-cadence.md §8`) | Ambiguities in received artifacts are resolved via structured feedback to the producing agent, not via CQ to the user. |
| Phase Gate Checklist (`agile-adm-cadence.md §6`) | No phase gate can pass while a blocking CQ is open on any artifact in that phase. |
| SDLC Entry Points (`sdlc-entry-points.md`) | Entry-point assessment systematically identifies expected knowledge gaps and pre-emptively raises CQs before any agent begins phase work. |

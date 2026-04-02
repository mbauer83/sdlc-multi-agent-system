---
skill-id: DE-PHASE-E-FEEDBACK
agent: DE
name: phase-e-feedback
display-name: Phase E Feedback — Implementation Complexity Estimation
invoke-when: >
  PM explicitly activates DE for Phase E consulting input; DE estimates implementation
  complexity per candidate in the ICC and identifies hidden dependencies.
trigger-phases: [E]
trigger-conditions:
  - handoff.created (handoff-type=consulting-activation, to=implementing-developer, phase=E)
entry-points: []
primary-outputs: [Implementation Complexity Report]
version: 1.0.0
---

# Skill: Phase E Feedback — Implementation Complexity Estimation

**Agent:** Implementing Developer  
**Version:** 1.0.0  
**Phase:** E — Opportunities & Solutions (consulting contribution)  
**Skill Type:** Consulting feedback  
**Framework References:** `agile-adm-cadence.md §4.1`, `raci-matrix.md §3.7`, `clarification-protocol.md §4`, `repository-conventions.md §4`

---

## Inputs Required

| Input | Source | Minimum State | Retrieval Depth |
|---|---|---|---|
| Implementation Candidate Catalog (`ICC`) | Software Architect/PE | Draft (v0.x.x) is acceptable for this consulting role | Full retrieval — DE needs implementation-level detail per candidate |
| Work Package Catalog (`WPC`) | Project Manager | Draft (v0.x.x) | Summary sufficient for scope context; full retrieval if WP effort fields need to be populated |
| Technology Architecture (`TA`) | Software Architect/PE | At least draft (v0.1.0+) | Summary sufficient for most estimates; full retrieval if technology component detail is needed to assess an implementation approach |
| Application Architecture (`AA`) | Solution Architect | Draft or baselined | Summary sufficient; full retrieval if interface complexity drives the estimate |
| Sprint activation instruction | Project Manager | PM instruction to provide Phase E input | — |

**Activation condition:** This skill is executed **only when PM explicitly activates DE for Phase E consulting input**. DE does not self-activate for Phase E. The PM emits an instruction (via sprint plan or handoff event) specifying which candidates and work packages require DE input.

---

## Knowledge Adequacy Check

### Required Knowledge

- The implementation candidates as described in the ICC: what each candidate is meant to build, which technology components it will use, which application components it touches, and any stated implementation approach.
- The technology component stack from the TA: which SBBs are available, their maturity, and any known integration complexity.
- The team's current skills profile — if this is known from the Engagement Profile or from prior sprint work. DE may document skill gap assumptions; it cannot infer team skills from architecture artifacts alone.

### Known Unknowns

- **Team skills availability:** The DE may be the sole agent representing "the team" in this multi-agent system, but in a real engagement the team's actual skill profile is organisation-specific. If a team skills register exists in `external-sources/` or the Engagement Profile, query it. If not, flag skill gaps as assumptions.
- **Build system and toolchain constraints:** Build system complexity (monorepo tooling, polyglot build chains, legacy build scripts) is not visible at the architecture layer and may significantly affect implementation effort. If the target project repository is accessible (EP-G entry point), query it. For EP-0 through EP-F, these are predictable unknowns; document as assumptions.
- **Third-party API integration complexity:** If any candidate requires integration with a third-party API, actual complexity depends on the API's documentation quality, authentication requirements, and rate limits — none of which are visible from architecture artifacts. Flag as a known unknown requiring CQ if the candidate is high-value and the estimate is consequential.

### Clarification Triggers

| Condition | Route | Blocking? |
|---|---|---|
| An implementation candidate references a technology component not present in the TA | Structured feedback to SwA (via PM) | No — DE estimates with an assumption; flags gap |
| PM requests estimates for candidates where no architecture detail is available (candidate is defined by title only) | CQ to PM | No — DE provides a very rough order-of-magnitude estimate with explicit assumption that detail is absent |
| A candidate's scope or boundary is ambiguous (e.g., it is unclear whether it includes a dependent service) | Structured feedback to PM for scope clarification | No — DE estimates the narrower interpretation; documents assumption |

This skill has **no blocking CQ conditions** — it is advisory only. DE proceeds with documented assumptions if knowledge is incomplete.

---

## Procedure

This procedure is executed once per PM activation, covering all candidates and work packages indicated in the PM instruction.

### Step 1 — Read the Implementation Candidate Catalog

Retrieve the ICC in full. For each candidate in scope:
- Identify the relevant TA technology components (SBBs) the candidate will use.
- Identify the relevant AA components (APP-nnn) and interfaces (IFC-nnn) the candidate touches.
- Note any stated constraints (reuse vs. build vs. buy recommendation from SwA).

### Step 2 — Classify implementation complexity per candidate

For each candidate, assign one complexity rating using the following classification:

| Rating | Definition |
|---|---|
| **Trivial** | Straightforward configuration, scripting, or boilerplate code using well-understood SBBs. No novel interface integration. Estimated ≤ 0.5 story points equivalent. |
| **Low** | Standard feature implementation using authorised SBBs. One or two interfaces. No significant data transformation. |
| **Medium** | Multiple interfaces or components involved. Non-trivial data transformation or state management. New integration with a known SBB. |
| **High** | Complex business logic; multiple cross-component interactions; integration with a third-party API or legacy system; significant data migration component. |
| **Very High** | Novel technology component with limited team experience; complex distributed systems concern (eventual consistency, distributed transactions, backpressure); safety-relevant logic requiring formal verification approaches. |

Record the rating and a one-paragraph rationale for each candidate. The rationale must be specific — not "complex because hard" but "medium because this candidate requires integrating APP-003 (order service) with TC-007 (message broker) via IFC-009 (async event schema), which involves schema evolution handling and at-least-once delivery semantics".

### Step 3 — Identify hidden implementation dependencies

For each candidate, identify dependencies that are not visible at the architecture layer:

1. **Library constraint dependencies:** Does the chosen SBB impose a minimum or maximum language runtime version that constrains other candidates? (e.g., library X requires Python ≥ 3.11 while legacy code may be on 3.9)
2. **Build system requirements:** Does this candidate require a build step, code generation pass, or schema compilation step that must precede other candidates?
3. **Database migration ordering:** If any candidate includes a data migration, identify whether the migration must run before or after another candidate's data access changes. Migrations that change column types or remove columns have strict ordering requirements relative to application deployments.
4. **API versioning constraints:** If multiple candidates touch the same API, identify whether a versioning strategy (additive-only, versioned endpoints, contract negotiation) is required to avoid breaking changes during the multi-sprint delivery.
5. **Shared module or library changes:** If two candidates both modify a shared module, they have an implicit merge dependency that requires branching strategy coordination.

Record identified hidden dependencies as: `HIDDEN-DEP-<n>: <description> — affects candidates: <ICC-ids>`.

### Step 4 — Flag technology-choice implementation constraints

For each candidate where the technology choice significantly constrains the implementation approach, produce a technology constraint note:

- If the authorised SBB for a candidate is immature (e.g., library is pre-1.0 or has limited community documentation), flag this as a risk to the PM — implementation effort estimates for immature SBBs carry higher uncertainty.
- If the candidate uses a technology component that the DE (or the known team) has limited experience with, flag as a skill gap.
- If a technology choice forces a specific implementation pattern (e.g., an ORM that requires active-record pattern, constraining the domain model), note the pattern lock-in and whether it conflicts with the application architecture's intended design.

### Step 5 — Flag skill gap candidates

For candidates that require skills not available or not confirmed available in the current team:
- Name the specific skill required (e.g., "React 18 concurrent rendering", "Kubernetes operator development", "WASM compilation pipeline").
- Note the consequence if the skill gap is not addressed: candidate cannot be delivered at the planned quality level, or will require significantly more time than the complexity rating alone suggests.
- This is advisory input to PM; PM decides whether to raise a CQ to the user or accept the risk.

### Step 6 — Produce the Implementation Complexity Report

Write the Implementation Complexity Report to `delivery-repository/implementation-notes/phase-e-complexity-report-<sprint-id>.md`.

Report structure:
```markdown
# Implementation Complexity Report

**Sprint:** <sprint-id>  
**Produced by:** Implementing Developer  
**Date:** <sprint date>  
**Inputs:** ICC-<id> v<version>, WPC-<id> v<version>

## Complexity Ratings

| Candidate ID | Name | Complexity | Rationale |
|---|---|---|---|

## Hidden Implementation Dependencies

<HIDDEN-DEP entries>

## Technology Choice Implementation Constraints

<Per-candidate notes>

## Skill Gap Flags

<List of skill gaps, if any>

## Assumptions

<List of assumptions made where knowledge was incomplete>
```

### Step 7 — Handoff to PM

Write a handoff record to `engagements/<id>/handoff-log/<sprint-id>-phase-e-complexity-handoff.md` directed to PM. Emit `handoff.created` with `handoff_type: consulting-input`, `artifact_id: phase-e-complexity-report-<sprint-id>`, `to_agents: [project-manager]`.

This is the terminal step for this skill activation. DE's contribution is complete; PM incorporates the complexity ratings and hidden dependencies into the Work Package Catalog effort estimates.

---

## Feedback Loop

This skill has a **single advisory iteration**:
- DE produces the report and hands off to PM.
- PM may request a single clarification or elaboration on a specific candidate (e.g., "why is candidate ICC-007 rated Very High?"). DE responds by updating the report and re-handing off.
- PM does not return the report for further iteration. If PM believes the estimates are systematically inconsistent, PM raises this to SwA for architectural review — it is not a DE defect.

**Maximum iterations:** 1 (report delivery) + 1 optional clarification response.  
**Escalation path:** None. This skill produces advisory output only; it has no gate authority and cannot block Phase E progression.

---

## Algedonic Triggers

No algedonic triggers identified for this skill.

The implementation complexity report is advisory input to PM planning. It does not constitute a binding output, does not affect a phase gate, and does not produce a deliverable that could create a governance, safety, or timeline-collapse condition. Any concerns identified in the report (skill gaps, hidden dependencies) are flagged through the normal PM reporting channel.

---

## Outputs

| Output | Location | Event Emitted |
|---|---|---|
| Implementation Complexity Report | `delivery-repository/implementation-notes/phase-e-complexity-report-<sprint-id>.md` | `handoff.created` (to PM) |
| Handoff record | `engagements/<id>/handoff-log/<sprint-id>-phase-e-complexity-handoff.md` | `handoff.created` |

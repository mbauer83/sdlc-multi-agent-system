---
skill-id: DE-PHASE-F-FEEDBACK
agent: DE
name: phase-f-feedback
display-name: Phase F Feedback — Implementation Dependency Validation
invoke-when: >
  PM explicitly activates DE for Phase F consulting input; DE validates the Implementation
  Plan's technical sequencing and identifies implicit implementation dependencies.
trigger-phases: [F]
trigger-conditions:
  - handoff.created (handoff-type=consulting-activation, to=implementing-developer, phase=F)
entry-points: []
primary-outputs: [Implementation Dependency Validation]
complexity-class: simple
version: 1.0.0
---

# Skill: Phase F Feedback — Implementation Dependency Validation

**Agent:** Implementing Developer  
**Version:** 1.0.0  
**Phase:** F — Migration Planning (consulting contribution)  
**Skill Type:** Consulting feedback  
**Framework References:** `agile-adm-cadence.md §4.1`, `raci-matrix.md §3.8`, `clarification-protocol.md §4`, `repository-conventions.md §4`

---

## Inputs Required

| Input | Source | Minimum State | Retrieval Depth |
|---|---|---|---|
| Implementation Plan (`IP`) | Project Manager | Draft (v0.x.x) — this skill contributes to its finalisation | Full retrieval |
| Dependency Matrix | Project Manager | Draft (v0.x.x) | Full retrieval |
| Work Package Catalog (`WPC`) | Project Manager | Draft, incorporating Phase E complexity ratings | Summary sufficient |
| Technology Architecture (`TA`) | Software Architect/PE | Baselined (v1.0.0+) | Summary sufficient; full retrieval if sequencing depends on specific TC-nnn deployment order |
| Phase E Complexity Report (DE's own) | Implementing Developer | Produced in Phase E | Full retrieval — this report informs the validation |
| Sprint activation instruction | Project Manager | PM instruction to provide Phase F input | — |

**Activation condition:** This skill is executed **only when PM explicitly activates DE for Phase F consulting input**. The PM emits an instruction specifying which sections of the IP and Dependency Matrix require DE validation.

---

## Knowledge Adequacy Check

### Required Knowledge

- The Implementation Plan's proposed sequencing of Work Packages across Solution Sprints: which WPs are scheduled in which sprints, which are marked as serial dependencies, and which are proposed to run in parallel.
- The Dependency Matrix: which WPs the PM has identified as having prerequisite relationships.
- The DE's own Phase E complexity ratings and hidden dependencies, which are primary inputs to this validation.
- The Technology Architecture's deployment topology: the order in which technology components are expected to be provisioned affects the order in which WPs that depend on those components can proceed.

### Known Unknowns

- **Actual team capacity per sprint:** The DE validates technical feasibility of sequencing, not resource capacity. Resource capacity is PM authority. DE flags where a proposed parallel delivery is technically infeasible (two WPs that share a code module or schema), but does not flag resource-capacity constraints unless they are technically encoded (e.g., a single CI pipeline serialises builds).
- **Future requirements changes:** The DE validates the IP as drafted. If requirements are still evolving (open PO CQs), sequencing decisions made on the current IP may be invalidated. DE documents this assumption.

### Clarification Triggers

| Condition | Route | Blocking? |
|---|---|---|
| IP references a Work Package that was not in the Phase E ICC scope — DE has no complexity estimate for it | CQ to PM | No — DE flags it as unvalidated; PM decides whether to request a supplementary estimate |
| IP proposes a sprint sequencing that appears to contradict a TA deployment dependency that is not captured in the Dependency Matrix | Structured feedback to PM | No — DE documents the concern and the affected WPs; PM adjudicates |

This skill has **no blocking CQ conditions** — it is advisory only.

---

## Procedure

This procedure is executed once per PM activation.

### Step 1 — Read the Implementation Plan and Dependency Matrix

Retrieve both the IP and Dependency Matrix in full. Build a working understanding of:
- The proposed sprint-by-sprint Work Package assignment.
- The WP-to-WP dependency relationships the PM has identified.
- The proposed feature branch strategy (if specified in the IP).

### Step 2 — Validate technical sequencing

For each dependency relationship in the Dependency Matrix, assess whether the ordering is technically correct from an implementation perspective:

**Schema and migration order:** Any WP that introduces a database schema change must precede any WP whose application code assumes that schema change is present. Verify the IP respects migration ordering for all schema-dependent WPs. An IP that deploys new application code before the corresponding migration runs will produce runtime failures.

**API versioning sequence:** Where multiple WPs touch a shared API, verify the IP sequences them such that breaking changes (e.g., removing a field, changing a type) are deployed in the correct order relative to dependent consumers. Additive changes (adding new optional fields) may be parallelised safely; breaking changes impose strict sequential ordering.

**Compilation and build dependencies:** In polyglot or monorepo configurations, verify that WPs that produce shared libraries or generated code are sequenced before WPs that consume those outputs. This is a build system dependency invisible at the architecture layer.

**Inter-service dependency chain:** If multiple WPs each build a different service that will call each other, verify the IP accounts for the bootstrapping order: the service that is called must be deployable before the service that calls it attempts to connect (or the caller must implement circuit-breaking/retry, which is itself a WP concern).

For each sequencing issue found, produce a **Sequencing Concern** entry:
```
SC-<n>: <description>  
Affects: WP-<ids>  
Proposed sequence: <as in IP>  
Required sequence: <as required technically>  
Reason: <one-sentence technical explanation>
```

### Step 3 — Identify implicit implementation dependencies not in the Dependency Matrix

Scan for dependencies the PM has not captured but which the DE can see from the implementation perspective:

1. **Shared module dependencies:** Two WPs that both modify the same shared module/library (as identified in the Phase E hidden dependencies) must be explicitly sequenced or assigned a coordination strategy (feature toggles, branch coordination). Flag each instance.
2. **Test data dependencies:** If WP-A creates test data (e.g., a seed script) that WP-B's integration tests depend on, WP-A's test data setup must precede WP-B's test execution. Flag if not captured.
3. **Environment prerequisite sequencing:** If WP-A provisions an infrastructure component that WP-B will use, WP-A must complete provisioning before WP-B can run integration tests. Verify this is reflected in the IP (or raise it for DevOps coordination).
4. **Database migration reversibility:** If an IP plans for sprint rollback, verify that all migrations in each sprint are reversible. Irreversible migrations (e.g., dropping a column) must be explicitly noted in the IP as point-of-no-return markers.

### Step 4 — Provide feature branch strategy input

Review the IP's proposed branching strategy (if specified). Provide input on:

**Parallel development viability:** Identify which WPs can safely be developed on independent feature branches (no shared code paths). Recommend that these be explicitly listed as parallelisable in the IP.

**Integration branch strategy:** If multiple WPs converge on a shared component, recommend an explicit integration branch (a shared feature branch that multiple WPs merge into before merging to trunk) rather than simultaneous trunk merges. Specify which WPs require this.

**Merge window sequencing:** For WPs with migration dependencies, recommend explicit merge windows: WP-A's PR (including migration) must be merged before WP-B's PR is opened for review, to avoid the migration being missing from the test environment when WP-B is tested.

**Branch lifetime risks:** Flag WPs whose estimated implementation duration is "High" or "Very High" (from Phase E complexity report) as having elevated merge conflict risk. Recommend incremental merges (small frequent PRs) over long-lived feature branches.

### Step 5 — Produce the Implementation Dependency Validation

Write the Implementation Dependency Validation to `delivery-repository/implementation-notes/phase-f-dependency-validation-<sprint-id>.md`.

Report structure:
```markdown
# Implementation Dependency Validation

**Sprint:** <sprint-id>  
**Produced by:** Implementing Developer  
**Date:** <sprint date>  
**Inputs:** IP-<id> v<version>, Dependency Matrix v<version>, Phase E Complexity Report <sprint-id>

## Sequencing Validation

### Confirmed Correct Sequences
<List of dependency relationships confirmed technically correct>

### Sequencing Concerns
<SC-n entries>

## Implicit Implementation Dependencies (not in Dependency Matrix)
<List of identified implicit dependencies>

## Feature Branch Strategy Recommendations
<Parallelisable WPs; integration branch recommendations; merge window sequencing; branch lifetime risks>

## Assumptions
<List of assumptions made where knowledge was incomplete>
```

### Step 6 — Handoff to PM

Write a handoff record to `engagements/<id>/handoff-log/<sprint-id>-phase-f-dependency-handoff.md` directed to PM. Emit `handoff.created` with `handoff_type: consulting-input`, `artifact_id: phase-f-dependency-validation-<sprint-id>`, `to_agents: [project-manager]`.

PM incorporates the sequencing concerns and implicit dependencies into the final Implementation Plan before baselining.

---

## Feedback Loop

This skill has a **single advisory iteration**:
- DE produces the validation and hands off to PM.
- PM may return one round of questions (e.g., "you flagged SC-2 — is there a branching strategy that would make parallel development possible?"). DE responds once.
- If the PM's final IP does not incorporate a sequencing concern the DE flagged, DE accepts PM's decision and documents the unresolved concern in the implementation notes as an open risk for Phase G.

**Maximum iterations:** 1 delivery + 1 optional clarification response.  
**Escalation path:** None. Advisory output only; Phase F gate authority rests with PM, SwA, and CSCO per `raci-matrix.md §4`.

---

## Algedonic Triggers

No algedonic triggers identified for this skill.

The implementation dependency validation is advisory input to PM planning. Unresolved sequencing concerns become documented risks in Phase G, not algedonic signals — the appropriate mechanism is to record them in implementation notes and flag them at the Phase G sprint kickoff. If an unresolved sequencing concern causes a sprint-blocking failure during Phase G, the relevant Phase G algedonic trigger (`ALG-006` — unresolvable dependency) would apply at that point, not during Phase F consulting.

---

## Outputs

| Output | Location | Event Emitted |
|---|---|---|
| Implementation Dependency Validation | `delivery-repository/implementation-notes/phase-f-dependency-validation-<sprint-id>.md` | `handoff.created` (to PM) |
| Handoff record | `engagements/<id>/handoff-log/<sprint-id>-phase-f-dependency-handoff.md` | `handoff.created` |

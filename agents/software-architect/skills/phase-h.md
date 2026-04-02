---
skill-id: SwA-PHASE-H
agent: SwA
name: phase-h
display-name: Phase H — Architecture Change Management (Technology Layer)
invoke-when: >
  SA routes a Change Record to SwA via handoff for technology-layer impact assessment; or a
  phase.return-triggered event identifies TA or AC as affected artifacts.
trigger-phases: [H]
trigger-conditions:
  - handoff.created (handoff-type=architecture-change-impact, to=software-architect)
  - phase.return-triggered (affected-artifacts includes TA or AC)
  - sprint.started (phase=H)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Technology Impact Assessment, Updated Technology Architecture, Updated Architecture Contract]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase H — Architecture Change Management (Technology Layer)

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Governance + Architecture revision  
**Framework References:** `agile-adm-cadence.md §6.9`, `agile-adm-cadence.md §11`, `raci-matrix.md §3.10`, `framework/artifact-schemas/architecture-contract.schema.md`, `framework/artifact-schemas/technology-architecture.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Change Record (`CR`) | Solution Architect | Draft (CR-nnn v0.1.0+) — SA initiates; SwA receives via handoff | SA is ● for the CR; SwA is ○ (consulted). The SwA does not initiate the CR — it receives a handoff from SA |
| Handoff acknowledgement: CR | SwA | Acknowledged | Emit `handoff.acknowledged` before Phase H assessment begins |
| Affected TA artifact(s) | SwA | Baselined — may be revised in this phase | Identify which TA version is current and affected |
| Affected AC artifact(s) | SwA | Baselined — may be revised in this phase | Identify all ACs whose compliance criteria may change |
| Architecture Principles Register (`PR`) | Solution Architect | Baselined | Required if the change would alter a principle-override ADR |
| Safety Constraint Overlay (`SCO`) — current | CSCO | Baselined | Required for Safety-Critical change classification |
| Phase G artifacts (if Phase G currently in progress) | All implementing agents | Current sprint state | Critical: assess in-flight impact immediately |
| Change classification (from CR) | SA | As recorded in CR | Determines SwA response scope: Minor / Significant / Major / Safety-Critical |

**RACI note for Phase H:** SA is **●** for the Change Record. SwA is **○** (consulted). For Updated Architecture Artifacts, SA is **●** for logical-layer artifacts (AA, DA); SwA is **●** for technology-layer artifacts (TA, AC). The RACI table shows SA ● / SwA ○ for "Updated Architecture Artifacts" at the phase level — but at the artifact level, SwA owns TA and AC revisions.

---

## Knowledge Adequacy Check

### Required Knowledge

- The complete Change Record (CR) including: change description, affected business functions, change classification, SA's initial impact assessment, and CSCO safety determination (if Safety-Critical)
- The current version of the TA (and all ACs in force) before assessing impact
- The change classification per `agile-adm-cadence.md §11`: Minor / Significant / Major / Safety-Critical
- If Phase G is in progress: the current sprint's scope, the active AC, and which work packages have already been completed vs. are in-flight

### Known Unknowns

The following gaps are predictably present when a Phase H change arrives:

1. **Scope of downstream impact**: The full ripple effect of a technology change on in-flight implementation (Developer code, DevOps configurations) may not be determinable from artifacts alone. Some impact will only be discovered when implementing agents review the updated AC.
2. **Vendor/product compatibility**: If the change involves a product version upgrade, backward compatibility with other TC-nnn components may need verification from vendor documentation not yet reviewed.
3. **Mid-sprint disruption scope**: If Phase G is in progress, the precise set of code artefacts that depend on the changed TC-nnn or ADR decision may be spread across the Developer's working branch in ways not visible to the SwA without PR review.

### Clarification Triggers

Raise a CQ (`target: User`) if:
- The change record describes a stakeholder-driven technology mandate (e.g., "use this specific product") that would override an existing ADR decision and the business reason is not documented in the CR
- The impact assessment identifies a significant increase in system complexity or operational burden and it is unclear whether the user accepts this trade-off

Route structured feedback to SA (`target: Solution Architect`) if:
- The CR is ambiguous about whether the change is at the logical layer (requiring AA/DA revision) or the technology layer only (TA/AC revision)
- The CR classifies the change as Minor but the SwA's impact assessment identifies technology-layer impacts that would require ADR revision (misclassification)

Route to PM if:
- A change arrives during Phase G without a formal CR, without SA initiation (change classification bypass is a governance violation)
- The change cannot be absorbed within the current sprint timeline and a sprint replanning event is required

---

## Procedure

### Step 1 — Receive Change Record and Acknowledge

1.1 Receive `handoff.created` event from SA referencing the CR. Read the CR in full.

1.2 Emit `handoff.acknowledged` for the CR handoff. Do not begin impact assessment until acknowledgement is recorded.

1.3 Read the change classification in the CR:
- **Minor**: technology layer unaffected → SwA provides technology confirmation to SA (Step 2); no TA/AC update required.
- **Significant**: one or more TA artifacts affected; no safety-relevant components → SwA assesses technology-layer impact (Steps 2–5); updates TA and relevant ADRs if required.
- **Major**: multiple phases or cross-cutting architecture decisions affected → Full impact assessment (Steps 2–5); coordinate with SA and PM; may trigger phase return to D or E.
- **Safety-Critical**: any change to a safety-relevant component or constraint → immediately escalate to CSCO before any TA revision (Step 2a); all other work on affected components is halted.

1.4 If Phase G is currently in progress, perform Step 3b (mid-sprint impact) immediately after acknowledgement, before any other step.

**Revisit handling:** If this is not the first Phase H visit for this engagement (`phase_visit_count > 1`), read the previous Phase H records to understand the cumulative change history. Ensure the current change is assessed against the post-previous-change TA version, not the original baseline.

### Step 2 — Assess Technology-Layer Impact

2.1 For each TC-nnn component in the Technology Component Catalog, determine whether the change affects it:
- Does the change modify a component's required functionality (requiring a different product selection)?
- Does the change modify a non-functional requirement (requiring a different version, configuration, or topology)?
- Does the change introduce a new component type not in the current catalog?
- Does the change retire a component that is currently in the catalog?

2.2 For each affected TC-nnn, identify:
- Which ADR-nnn governs this component's selection
- Which AC sections reference this component (§3.3 ABBs, §3.4 authorised SBBs, §3.5 constraints)
- Which work packages (WP-nnn) in the Implementation Plan include this component
- Which application components (APP-nnn) and data entities (DE-nnn) this component serves (Technology/Application Matrix)

2.3 For each affected ADR-nnn, assess:
- Is the current decision still valid after the change? → No update needed; add a note to the ADR under `Revision History`.
- Does the change invalidate the current decision? → A new ADR is required (see Step 4).
- Does the change add new alternatives that should be considered? → Flag for ADR review in the next relevant phase.

2.4 Produce a **Technology Impact Assessment** document covering:
- Summary: change impact on the technology layer (none / localised to TC-nnn / cross-cutting)
- Affected TC-nnn list with impact type for each
- Affected ADR-nnn list with revision assessment for each
- Affected AC sections (if Phase G in progress)
- Recommended response: no TA update / minor TA revision / major TA revision with ADR updates / phase return required

2.5 Deliver the Technology Impact Assessment to SA via handoff event. SA integrates it into the CR completion.

### Step 2a — Safety-Critical Change: Mandatory CSCO Coordination

2a.1 For any change classified as Safety-Critical (by CR or by SwA's own impact assessment revealing a safety-relevant TC-nnn is affected):

2a.2 **Immediately halt all work** on the affected TC-nnn components and their dependent work packages.

2a.3 Raise ALG-014 (S1 — safety-critical change without CSCO available) if CSCO is unavailable. Do not proceed with any technology assessment of the safety-relevant component until CSCO is available.

2a.4 If CSCO is available: emit `handoff.created` to CSCO with the CR and the preliminary Technology Impact Assessment. Do not update the TA or any AC for safety-relevant components until CSCO has reviewed the impact assessment and provided sign-off.

2a.5 Wait for CSCO sign-off before proceeding with Steps 4–5 for safety-relevant components. Non-safety-relevant components may be assessed in parallel (Steps 2–5) while awaiting CSCO sign-off.

### Step 3 — Prepare Technology Impact Assessment for SA

3.1 The Technology Impact Assessment (produced in Step 2.4) is the SwA's contribution to SA's CR completion. Ensure it contains:
- A clear statement of the technology-layer scope of the change
- The minimum TA revision scope (what must change vs. what can remain unchanged)
- Any new or revised ADR decisions required
- If AC revision is required: which specific AC sections change and how

3.2 Classify the technology-layer impact in the assessment using the same classification scheme as the CR (`agile-adm-cadence.md §11`):
- If the CR is classified as Minor but the SwA finds a technology-layer impact that would require ADR revision → flag the discrepancy to SA as structured feedback; the CR classification may need to be upgraded.

### Step 3b — Mid-Sprint Impact Assessment (if Phase G in progress)

3b.1 If Phase G is currently in progress, assess the in-flight impact immediately after acknowledging the CR.

3b.2 Identify which work packages in the current Solution Sprint are affected by the change:
- Are any in-progress work packages implementing TC-nnn components that are affected?
- Are any in-progress work packages relying on compliance criteria (CON-nnn) that would change?

3b.3 If any in-flight work package is affected:
- Immediately raise ALG-006 (S2 — sprint dependency cannot be resolved without PM intervention). Notify PM explicitly with the list of affected work packages and the nature of the conflict.
- Notify PM explicitly.
- Do not close the current sprint until the impact assessment is complete and PM has directed whether to: (a) continue current sprint under the existing AC with a Phase H amendment; (b) pause in-flight work and re-issue the AC; or (c) roll back in-flight work and re-plan the sprint after AC revision.

3b.4 If no in-flight work package is affected: note this in the Technology Impact Assessment; Phase G continues normally for unaffected work packages.

### Step 4 — Update TA (if Significant/Major/Safety-Critical change)

4.1 For Minor changes with no technology-layer impact: no TA update is required. Proceed to Step 5.

4.2 For Significant/Major/Safety-Critical changes with technology-layer impact: open the TA for revision.

4.3 Identify the `affected-artifacts` list from the `phase.return-triggered` event. Revise only the TA sections identified as affected. Preserve all other sections unchanged.

4.4 For each affected TC-nnn:
- If the product selection changes: update the Technology Component Catalog entry; supersede the existing ADR (mark as `Status: Superseded by ADR-nnn`); produce a new ADR for the new decision.
- If the version constraint changes: update the catalog entry; update the ADR `Consequences` section with a revision note.
- If the component is retired: update the catalog entry to `Status: Retired`; note the retirement in the Technology/Application Matrix.
- If a new component is added: assign TC-nnn; produce a new ADR; update the Technology/Application Matrix.

4.5 Update the Technology/Application Matrix, Infrastructure Diagram, and Deployment Topology for any component additions, removals, or relationship changes.

4.6 Update the Technology Lifecycle Analysis if the change affects end-of-support dates or upgrade paths.

4.7 Update the Technology-Level SCO Cross-Reference (TA §3.9) if safety-relevant constraints change.

4.8 Increment the TA version (minor increment for localised changes; e.g., 1.0.0 → 1.1.0; major increment for cross-cutting changes; e.g., 1.0.0 → 2.0.0). Re-baseline with `artifact.baselined` event.

4.9 Issue new handoffs to DevOps (if TC component changes affect environment provisioning) and CSCO (if safety-relevant SCO cross-reference changes).

### Step 5 — Update AC (if Compliance Criteria Change)

5.1 If the TA revision changes the ABBs in force, authorised SBBs, or architecture constraints that are referenced in an active AC, the AC must be revised.

5.2 For each affected AC (covering the in-progress or upcoming Solution Sprint):
- Update §3.3 ABBs in Force: reflect updated TC-nnn constraints
- Update §3.4 Authorised SBBs: reflect new product versions or new/removed products
- Update §3.5 Architecture Constraints: reflect changed or new CON-nnn entries
- Update Prohibited Patterns section: add any new prohibitions arising from the change
- Increment AC version (e.g., 1.0.0 → 1.1.0 for in-sprint amendment)

5.3 Re-obtain signatures:
- SwA self-signs the revised AC
- CSCO re-signs if any safety-relevant constraint changes (mandatory — ALG-009 if bypassed)
- PM records the AC revision in the Governance Checkpoint Record

5.4 Notify Dev and QA via handoff events that the AC has been revised. The revised AC supersedes the previous version immediately. Implementing agents must review the revision and confirm via `handoff.acknowledged`.

5.5 For QA: if acceptance criteria change (AC §3.6), QA must assess whether tests already executed under the old criteria remain valid. SwA coordinates with QA on this.

### Step 6 — Phase H Formal Gate Vote

6.1 For formal Phase H changes (Significant, Major, or Safety-Critical classification), cast a gate vote when the change cycle is complete.

6.2 Pre-vote checklist:
- [ ] Technology Impact Assessment delivered to SA and integrated into CR
- [ ] All affected TA sections revised and re-baselined (if required)
- [ ] All new ADRs produced for changed decisions
- [ ] All affected ACs revised and re-signed (if required)
- [ ] CSCO sign-off obtained for safety-relevant changes
- [ ] In-flight sprint impact resolved (mid-sprint impact, if applicable)
- [ ] Handoffs to DevOps (re-provisioning if required) and QA (test re-validation if required) completed

6.3 Cast gate vote: emit `gate.vote_cast` with `gate: H-formal`, `vote: approved` (or `vote: blocked` with specific unresolved item list).

---

## Feedback Loop

### SA Change Record Completion Loop (SwA ↔ SA)

**Purpose:** Ensure the Technology Impact Assessment fully informs the CR and any required TA updates are approved by SA before re-baselining.

- **Iteration 1**: SwA delivers Technology Impact Assessment to SA. SA reviews and may identify additional logical-layer (AA/DA) impacts that affect the technology assessment. SwA revises the impact assessment if SA's feedback changes the scope.
- **Iteration 2**: SA confirms impact assessment is complete. SwA proceeds to TA revision (if required).
- **Termination**: SA confirms the CR is complete from the technology perspective; SwA has revised all affected TA sections.
- **Maximum iterations**: 2. If SA's iteration-2 feedback still reveals unresolved impacts, escalate to PM as ALG-010 (S3). PM adjudicates which artifacts require revision and in what order.
- **Escalation**: ALG-010 → PM adjudication; if the dispute requires user input (e.g., scope decision), PM batches as CQ.

### AC Revision Acknowledgement Loop (SwA ↔ Dev/DevOps/QA)

**Purpose:** Ensure implementing agents have received and accepted revised AC content.

- **Iteration 1**: SwA distributes revised AC via handoff events. All three implementing agents must acknowledge within the current sprint.
- **Termination**: All three agents emit `handoff.acknowledged` for the revised AC.
- **Maximum iterations**: 1 (acknowledgement is binary). If an agent does not acknowledge within the sprint, raise ALG-006 (S2 — dependency unresolved within sprint) and notify PM. PM follows up with the non-acknowledging agent.
- **Escalation**: ALG-006 → PM resolves; if an implementing agent is unavailable, PM documents and halts affected work packages.

---

## Algedonic Triggers

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-001 | SwA's impact assessment reveals that the change would cause a technology configuration that violates an SCO safety constraint | S1 | Halt all affected work; emit to CSCO (immediate) and PM (concurrent); do not revise TA until CSCO directs |
| ALG-003 | Impact assessment reveals a regulatory or compliance obligation not previously identified in any artifact | S1 | Emit to CSCO (immediate) and PM (concurrent); halt affected TA revision |
| ALG-006 | A revised AC has been distributed and one or more implementing agents have not acknowledged within the current sprint | S2 | Emit to PM; halt affected implementation work; PM follows up |
| ALG-010 | SA/SwA impact assessment loop exhausted (two iterations) without agreement | S3 | Emit to PM for adjudication; provide both positions in writing |
| ALG-012 | SwA detects that implementation has proceeded against a changed technology component without acknowledgement of the revised AC | S1 | Emit to PM (immediate halt) and CSCO (if safety-relevant); affected deliverables are non-compliant until AC acknowledged and implementation verified |
| ALG-006 | In-flight work packages are affected by a change and sprint dependencies cannot be resolved within the current sprint without PM direction | S2 | Emit to PM with list of affected work packages; PM adjudicates sprint continuation/pause |
| ALG-014 | A Safety-Critical change arrives and CSCO is unavailable to review the technology-layer impact | S1 | Halt all technology assessment of safety-relevant components; emit to PM and CSCO; do not resume until CSCO is available |
| ALG-018 | SwA detects the change was implemented without a formal Change Record (bypass of Phase H procedure) | S2 | Emit to PM; require retroactive CR production by SA; AC must be revised retroactively before sprint can close |

---

## Outputs

| Output | Path | Version at Revision | EventStore Event |
|---|---|---|---|
| Technology Impact Assessment | Delivered to SA via handoff (may be written to `technology-repository/` as a working note if retained) | — | `handoff.created` |
| Updated Technology Architecture (`TA`) — if technology-layer impact | `technology-repository/technology-architecture/TA-<nnn>-<x.y.0>.md` | Incremented from prior baseline | `artifact.baselined` |
| New / superseded ADR(s) | `technology-repository/adr-register/ADR-<nnn>-<version>.md` | 1.0.0 (new ADR) | — |
| Updated Architecture Contract(s) — if AC compliance criteria change | `technology-repository/architecture-contract/AC-<nnn>-<x.y.0>.md` | Incremented from 1.0.0 | `artifact.baselined` |
| H formal gate vote | EventStore | — | `gate.vote_cast` |
| Handoff to DevOps (re-provisioning input, if TC components changed) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (if safety-relevant TA revision) | `engagements/<id>/handoff-log/` | — | `handoff.created` |

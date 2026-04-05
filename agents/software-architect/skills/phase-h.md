---
skill-id: SwA-PHASE-H
agent: SwA
name: phase-h
display-name: Phase H — Architecture Change Management (Application & Technology Layers)
invoke-when: >
  SA routes a Phase H handoff to SwA (handoff-type=phase-h-application-technology-track)
  following SA's business-layer CR; or a phase.return-triggered event identifies AA, DA,
  TA, or AC as affected artifacts. SwA is co-primary for Phase H: SA owns the
  business/motivation/strategy-layer CR; SwA owns the application/technology-layer CR.
trigger-phases: [H]
trigger-conditions:
  - handoff.created (handoff-type=phase-h-application-technology-track, to=software-architect)
  - phase.return-triggered (affected-artifacts includes AA or DA or TA or AC or application/ or technology/)
  - sprint.started (phase=H)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Application/Technology Change Record, Updated Application Architecture Entities, Updated Technology Architecture, Updated Architecture Contract]
complexity-class: complex
version: 1.1.0
---

# Skill: Phase H — Architecture Change Management (Application & Technology Layers)

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.1.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Phase co-primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.9`, `agile-adm-cadence.md §11`, `raci-matrix.md §3.10`, `framework/artifact-schemas/architecture-contract.schema.md`, `framework/artifact-schemas/technology-architecture.schema.md`, `framework/artifact-schemas/application-architecture.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`

---

## Runtime Tooling Hint

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| SA's business/motivation/strategy-layer Change Record (`CR`) | Solution Architect | Draft (CR-nnn-business v0.1.0+) — SA initiates and routes via handoff | SA is ● for the business-layer CR; SwA reads it to understand the change context |
| Handoff acknowledgement | SwA | Acknowledged | Emit `handoff.acknowledged` for SA's Phase H handoff before beginning |
| Affected Application Architecture entities (AA) | SwA (self-read) | Baselined — from `architecture-repository/model-entities/application/` | Identify which APP/AIF/ASV entities are affected by the change |
| Affected Data Architecture entities (DA) | SwA (self-read) | Baselined — from `architecture-repository/model-entities/application/data-objects/` | Identify which DOB entities are affected |
| Affected TA artifact(s) | SwA (self-read) | Baselined — from `technology-repository/` | Identify which TA version is current and affected |
| Affected AC artifact(s) | SwA (self-read) | Baselined — from `technology-repository/architecture-contract/` | Identify all ACs whose compliance criteria may change |
| Architecture Principles Register (`PR`) | Solution Architect | Baselined | Required if the change would alter a principle-override ADR |
| Safety Constraint Overlay (`SCO`) — current | CSCO | Baselined | Required for Safety-Critical change classification |
| Phase G artifacts (if Phase G currently in progress) | All implementing agents | Current sprint state | Critical: assess in-flight impact immediately |
| Change classification (from SA's CR) | SA | As recorded in SA's CR | Determines SwA response scope: Minor / Significant / Major / Safety-Critical |

**Phase H co-ownership:** SA is **●** for the business/motivation/strategy-layer Change Record. SwA is **●** for the application/technology-layer Change Record. These are two parallel CRs coordinated by PM. SwA produces its own CR covering AA/DA/TA/AC impact; SwA is not merely consulting — it has full authorship authority for its domain.

---

## Knowledge Adequacy Check

### Required Knowledge

- SA's business-layer Change Record (CR) including: change description, affected business functions, change classification, and which application/technology artifacts SA flagged as potentially affected
- The current versions of AA entities (APP, AIF, ASV, DOB) from `architecture-repository/model-entities/application/` and the TA and all ACs in force from `technology-repository/`
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

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="H", artifact_type="change-record")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 1 — Receive SA Handoff and Acknowledge

1.1 Receive `handoff.created` event from SA (handoff-type: `phase-h-application-technology-track`) referencing SA's business-layer CR. Read SA's CR in full.

1.2 Emit `handoff.acknowledged` for the handoff. Do not begin impact assessment until acknowledgement is recorded.

1.3 Read SA's change classification:
- **Minor**: application/technology layer likely unaffected → SwA performs lightweight impact confirmation (Step 2); if confirmed unaffected, produce a short CR with `impact: none` status; no TA/AC update required.
- **Significant**: one or more AA/DA/TA artifacts may be affected → SwA assesses full application/technology impact (Steps 2–5a); updates entities and artifacts as required.
- **Major**: multiple phases or cross-cutting decisions affected → Full assessment (Steps 2–5a); coordinate with SA and PM; may trigger phase return to Phase C or D.
- **Safety-Critical**: any change affecting a safety-relevant APP/DOB/TA component → immediately escalate to CSCO before any application/technology revision (Step 2a); all other work on affected components is halted.

1.4 If Phase G is currently in progress, perform Step 3b (mid-sprint impact) immediately after acknowledgement, before any other step.

**Revisit handling:** If this is not the first Phase H visit (`phase_visit_count > 1`), read previous Phase H records to understand cumulative change history. Assess the current change against the post-previous-change AA/DA/TA version.

**Revisit handling:** If this is not the first Phase H visit for this engagement (`phase_visit_count > 1`), read the previous Phase H records to understand the cumulative change history. Ensure the current change is assessed against the post-previous-change TA version, not the original baseline.

### Step 2 — Assess Application and Technology-Layer Impact

2.0 **Application-layer assessment (AA/DA — Phase C output):** Read AA and DA entities from `architecture-repository/model-entities/application/`. For each APP-nnn, AIF-nnn, ASV-nnn, and DOB-nnn, assess:
- Does the change require modification to component responsibilities (APP-nnn §content/Responsibility)?
- Does the change add, remove, or rename any application service (ASV-nnn) or interface (AIF-nnn)?
- Does the change affect the data model: new data entities, changed classifications, new relationships (DOB-nnn)?
- Does any safety-relevant flag change?

If AA/DA entities require modification, note them for the SwA CR §2.4 and for Step 4a below.

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

2.5 Use the Technology Impact Assessment as working input to Step 3c (Application/Technology Change Record production). It is no longer delivered to SA as SwA's primary output — SA reads the completed SwA CR instead. The Technology Impact Assessment document may be optionally written to `technology-repository/` as a working note if useful, but the SwA CR is the authoritative output.

### Step 2a — Safety-Critical Change: Mandatory CSCO Coordination

2a.1 For any change classified as Safety-Critical (by CR or by SwA's own impact assessment revealing a safety-relevant TC-nnn is affected):

2a.2 **Immediately halt all work** on the affected TC-nnn components and their dependent work packages.

2a.3 Raise ALG-014 (S1 — safety-critical change without CSCO available) if CSCO is unavailable. Do not proceed with any technology assessment of the safety-relevant component until CSCO is available.

2a.4 If CSCO is available: emit `handoff.created` to CSCO with the CR and the preliminary Technology Impact Assessment. Do not update the TA or any AC for safety-relevant components until CSCO has reviewed the impact assessment and provided sign-off.

2a.5 Wait for CSCO sign-off before proceeding with Steps 4–5 for safety-relevant components. Non-safety-relevant components may be assessed in parallel (Steps 2–5) while awaiting CSCO sign-off.

### Step 3 — Prepare Technology Impact Assessment for SA

3.1 The Technology Impact Assessment (produced in Step 2.4) feeds into Step 3c (SwA's CR). Ensure it contains:
- A clear statement of the application/technology scope of the change
- All affected AA/DA entities (Step 2.0) and their required changes
- The minimum TA revision scope (what must change vs. what can remain unchanged)
- Any new or revised ADR decisions required
- If AC revision is required: which specific AC sections change and how

3.2 Classify the application/technology-layer impact using the same scheme as SA's CR (`agile-adm-cadence.md §11`):
- If SA's CR is classified as Minor but SwA finds an application or technology-layer impact requiring ADR revision or AA entity updates → flag the discrepancy to SA as structured feedback; SA's CR classification may need to be upgraded.

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

### Step 3c — Produce Application/Technology Change Record

After completing the Technology Impact Assessment (Steps 2–3), SwA produces its own Change Record for the application/technology layer. This is SwA's primary output for Phase H — not merely a technology impact document delivered to SA.

3c.1 **Scope:** The SwA CR covers:
- All affected AA entities (`APP-nnn`, `AIF-nnn`, `ASV-nnn` in `architecture-repository/model-entities/application/`)
- All affected DA entities (`DOB-nnn` in `architecture-repository/model-entities/application/data-objects/`)
- All affected TA artifacts and technology-layer entities (`technology-repository/`)
- All affected ACs (`technology-repository/architecture-contract/`)

3c.2 **CR structure:** Produce a CR file at `architecture-repository/change-records/cr-<id>-application-tech-0.1.0.md` using the same `change-record.schema.md` structure as SA's CR. Key fields:

- `§2.2 Change Request`: reference SA's business-layer CR by artifact-id; describe the application/technology-layer interpretation of the change
- `§2.3 Change Impact Classification`: inherit SA's classification unless SwA's assessment reveals a higher classification (in which case, notify SA and CSCO)
- `§2.4 Affected Artifacts`: list APP/AIF/ASV/DOB/TA/AC artifacts with change required and new version
- `§2.5 Safety Impact Analysis`: from CSCO (Step 2a), or `Not applicable` if confirmed non-safety-relevant
- `§2.6 Decision Record`: for application/technology-layer changes, decision authority follows the same class rules; SwA is the accountable agent for application/technology artifacts
- `§2.7 Implementation Actions`: one ACT-nnn per artifact; owner: SwA (for AA/DA entities and TA); DevOps (for infrastructure changes); QA (for test re-validation)

3c.3 Create cross-reference: add a `related-cr:` field in SwA's CR referencing SA's business-layer CR artifact-id. SA's CR references SwA's CR in §2.4.

3c.4 Emit `artifact.baselined` for SwA's CR at version 1.0.0 after decision authority approves.

---

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

### Step 4a — Update Application Architecture Entities (if AA/DA affected)

4a.1 For Minor changes with no application-layer impact: skip this step.

4a.2 For Significant/Major/Safety-Critical changes with application-layer impact: open the affected AA/DA entity files from `architecture-repository/model-entities/application/`.

4a.3 For each affected APP-nnn:
- Update `§content/Responsibility` if the component's responsibilities change
- Update `§content/Safety-Relevant` if safety classification changes
- Update `§content/Status` if component is new, modified, or retiring
- Increment entity version; re-emit `artifact.baselined`

4a.4 For each affected AIF-nnn or ASV-nnn: update Protocol/Style, Data Entities, or Consumed By fields as required; re-emit `artifact.baselined`.

4a.5 For each affected DOB-nnn: update Classification, Owning Application, Key Attributes, or Safety-Relevant; re-emit `artifact.baselined`. Notify CSCO via handoff if any Safety-Critical data entity changes.

4a.6 After updating AA/DA entities: notify SA via handoff that application-layer entities have been revised and the Phase C CRUD matrix / data governance overview may need review.

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

### Step 6 — Phase H Formal Gate Vote (Application/Technology Layer)

6.1 For formal Phase H changes (Significant, Major, or Safety-Critical classification), cast a gate vote when the application/technology change cycle is complete.

6.2 Pre-vote checklist:
- [ ] Application/Technology Change Record produced and approved (Step 3c)
- [ ] All affected AA/DA entity files revised and re-baselined (if required — Step 4a)
- [ ] All affected TA sections revised and re-baselined (if required — Step 4)
- [ ] All new ADRs produced for changed decisions
- [ ] All affected ACs revised and re-signed (if required — Step 5)
- [ ] CSCO sign-off obtained for safety-relevant changes
- [ ] In-flight sprint impact resolved (mid-sprint impact, if applicable — Step 3b)
- [ ] Handoffs to DevOps (re-provisioning if required) and QA (test re-validation if required) completed
- [ ] Handoff to SA confirming application/technology CR is complete (for SA to record in their business-layer CR cross-reference)

6.3 Cast gate vote: emit `gate.vote_cast` with `gate: H-formal-application-tech`, `vote: approved` (or `vote: blocked` with specific unresolved item list).

**Note:** SA casts a separate gate vote for the business/motivation/strategy layer. PM waits for both gate votes before closing Phase H.

---

## Feedback Loop

### SwA CR ↔ SA CR Alignment Loop (SwA ↔ SA)

**Purpose:** Ensure the two parallel Phase H CRs (SA's business-layer + SwA's application/technology-layer) have consistent §2.4 cross-references and no scope gaps or overlaps.

- **Iteration 1**: SwA produces application/technology CR (Step 3c) and sends completion handoff to SA. SA reviews the cross-references in §2.4 and may identify business-layer impacts SwA's CR implicitly introduces. SwA revises if SA's feedback changes the AA/DA scope.
- **Iteration 2 (if needed)**: SA confirms alignment. SwA proceeds to TA/AA revision (if not already underway).
- **Termination**: SA confirms both CRs are aligned on scope. Both CRs can be baselined.
- **Maximum iterations**: 2. Escalate to PM as ALG-010 (S3) after iteration 2 without resolution. PM adjudicates using layer boundary: SA governs business-layer scope; SwA governs application/technology scope.
- **Escalation**: ALG-010 → PM adjudication; if the dispute requires user input, PM batches as CQ.

### Personality-Aware Conflict Engagement

SwA and SA are co-primaries in Phase H with strictly separated domains. When scope boundary disputes arise, SwA applies the ArchiMate layer boundary rule: application and technology artifacts are SwA's domain; SwA does not defer to SA on APP/DOB/TA/AC scope decisions. If SA's iteration-1 feedback attempts to reduce SwA's application-layer scope in ways that would leave affected entities un-updated, SwA escalates to PM rather than complying. Governed by `framework/agent-personalities.md §6`.

### AC Revision Acknowledgement Loop (SwA ↔ Dev/DevOps/QA)

**Purpose:** Ensure implementing agents have received and accepted revised AC content.

- **Iteration 1**: SwA distributes revised AC via handoff events. All three implementing agents must acknowledge within the current sprint.
- **Termination**: All three agents emit `handoff.acknowledged` for the revised AC.
- **Maximum iterations**: 1 (acknowledgement is binary). If an agent does not acknowledge within the sprint, raise ALG-006 (S2 — dependency unresolved within sprint) and notify PM. PM follows up with the non-acknowledging agent.
- **Escalation**: ALG-006 → PM resolves; if an implementing agent is unavailable, PM documents and halts affected work packages.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="change-record"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

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
| Application/Technology Change Record (SwA CR) | `architecture-repository/change-records/cr-<id>-application-tech-<version>.md` | 1.0.0 after decision authority approves | `artifact.baselined` |
| Updated Application Architecture entities (if AA affected) | `architecture-repository/model-entities/application/{components,interfaces,services,data-objects}/` | Incremented from prior baseline | `artifact.baselined` (per entity) |
| Updated Technology Architecture (`TA`) — if technology-layer impact | `technology-repository/technology-architecture/TA-<nnn>-<x.y.0>.md` | Incremented from prior baseline | `artifact.baselined` |
| New / superseded ADR(s) | `technology-repository/adr-register/ADR-<nnn>-<version>.md` | 1.0.0 (new ADR) | — |
| Updated Architecture Contract(s) — if AC compliance criteria change | `technology-repository/architecture-contract/AC-<nnn>-<x.y.0>.md` | Incremented from 1.0.0 | `artifact.baselined` |
| H formal gate vote (application/technology layer) | EventStore | — | `gate.vote_cast` |
| Handoff to SA (CR alignment — always created) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to DevOps (re-provisioning input, if TC components changed) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (if safety-relevant AA/DA/TA revision) | `engagements/<id>/handoff-log/` | — | `handoff.created` |

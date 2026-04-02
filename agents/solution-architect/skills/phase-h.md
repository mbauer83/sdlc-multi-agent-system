---
skill-id: SA-PHASE-H
agent: SA
name: phase-h
display-name: Phase H — Architecture Change Management
invoke-when: >
  PM routes a change request to SA via handoff (CR-000 intake), or a phase.return-triggered
  event identifies SA-owned architecture artifacts (AV, BA, AA, DA) as affected.
trigger-phases: [H]
trigger-conditions:
  - handoff.created (handoff-type=change-record-intake, to=solution-architect)
  - phase.return-triggered (affected-artifacts includes AV or BA or AA or DA)
  - sprint.started (phase=H)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Change Record, Updated Architecture Artifacts]
version: 1.0.0
---

# Skill: Phase H — Architecture Change Management

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §5.9 and §10`, `framework/artifact-schemas/change-record.schema.md`, `raci-matrix.md §3.10`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| PM's intake record (Warm-Start Change Record `CR-000`) | Project Manager | Version 0.1.0; PM has performed initial intake and urgency classification | PM creates CR-000 from the change request before routing to SA; SA does not initiate the Change Record — SA completes it |
| Affected architecture artifact summary headers | SA (self-read) from `architecture-repository/` | Current baselined versions | SA identifies and reads the summary headers of all potentially affected AV, BA, AA, DA artifacts |
| Current Architecture Principles Register (`PR`) | SA (self-read) | Current version | SA checks whether the proposed change violates any architecture principle |
| Safety Constraint Overlay (`SCO`) — current version | CSCO | Current baselined version | Required before SA can determine whether a change is safety-relevant |
| Requirements Register (`RR`) | Product Owner | Current version | Required if the change source is a requirement change — SA must assess RR impact |
| `sprint.started` event for the Phase H sprint | PM | Emitted | Hard prerequisite; SA does not begin Phase H work without this event |

---

## Knowledge Adequacy Check

### Required Knowledge

- The change request itself: what has changed or is requested to change; who raised it; what systems or processes it affects.
- The current state of all architecture artifacts: SA must read the summary headers (and relevant sections) of all baselined architecture artifacts before performing impact assessment.
- Change classification rules from `agile-adm-cadence.md §10`: Minor / Significant / Major / Safety-Critical — these determine the decision authority and phase-return scope.
- Safety constraint context: whether the change touches any component or data entity classified as safety-relevant in the SCO. If the SCO is not current, SA must note this gap before proceeding.
- RACI rules for change approval authority: Minor (PM only), Significant (SA + PM), Major (all affected owners + CSCO), Safety-Critical (CSCO mandatory; halt if unavailable).

### Known Unknowns

| Unknown | Blocking | CQ Target | CR Section Affected |
|---|---|---|---|
| Change scope unclear (the user's change request is ambiguous about whether it affects architecture or only implementation) | Yes — cannot classify without scope clarity | PM routes to User | §2.3 Change Impact Classification, §2.4 Affected Artifacts |
| Safety relevance of the change (the change touches a component that was not previously classified as safety-relevant, and SCO does not address it) | Yes — CSCO must assess before SA completes CR | CSCO | §2.5 Safety Impact Analysis, §2.3 |
| Impact on non-SA artifacts (e.g., change requires TA update — is SwA in scope?) | Partially — SA can flag likely TA impact; SwA confirms scope | SwA (via PM) | §2.4 Affected Artifacts, §2.7 Implementation Actions |
| Baseline state of affected artifacts (if some artifacts are not yet baselined — EP-H entry where architecture is partially complete) | Yes — SA must raise this to PM; may require earlier EP before Phase H can proceed | PM | All CR sections |

### Clarification Triggers

SA raises a CQ when:

1. **Change scope unclear:** The PM's CR-000 describes a change that could be: (a) a documentation correction affecting no architecture element, (b) a defect in an architecture artifact, (c) a new capability request, or (d) a structural modification to the architecture. SA cannot determine the classification without clarification. Bounded CQ: "Does this change require any modification to: (a) the Business Capability Map, (b) the Application Component Catalog, (c) the Data Entity Catalog, (d) the Architecture Vision Statement? Or does it affect only the Technology Architecture or implementation?"
2. **Safety impact unclear:** The change affects a component or process that is near (but not clearly within) the safety boundary defined in the SCO. SA cannot determine `safety-relevant: true/false` unilaterally. SA raises a CQ to CSCO: "Does component [APP-nnn / BPR-nnn / DE-nnn] fall within the safety boundary defined in SCO §[section] for this engagement?"
3. **Phase return scope unclear for Major changes:** A Major change affects multiple artifacts spanning multiple phases. SA cannot determine the minimum phase-return scope without understanding the causal chain. If the causal chain is not clear from available artifacts, SA raises a CQ to PM and SwA jointly: "Does this change require both Phase C and Phase B revisit, or can it be addressed in Phase C alone?"

---

## Procedure

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase H sprint.
2. Read PM's CR-000 in full — understand the change request, urgency, and any PM-assigned initial classification.
3. Check: do the affected architecture artifacts exist in `architecture-repository/`? If not (e.g., EP-H entry where Phase A was never executed), SA must notify PM immediately. PM determines whether to escalate to an earlier entry point. SA does not proceed with Phase H on non-existent baseline artifacts.
4. Check: is the current SCO available? If CSCO has not yet produced a current SCO baseline, SA notes this gap before assessing safety relevance. If the change is potentially safety-relevant, SA raises a blocking CQ to CSCO before completing the CR.

---

### Step 1 — Read Affected Artifact Summary Headers

For each architecture artifact potentially affected by the change (as identified in CR-000):

1. Read the summary header of the artifact from `architecture-repository/`.
2. Note: current version, phase of origin, `safety-relevant` flag, `csco-sign-off` status.
3. Identify the sections of the artifact most relevant to the described change.
4. Do NOT modify any artifact at this step — assessment only.

**Scope of review by change type:**
- Change described as affecting a business process → read BA BPC (§3.3), then check whether the process is referenced in AA (§3.4 matrix) and DA (§3.4 CRUD matrix). If yes, AA and DA are potentially affected.
- Change described as affecting an application component → read AA (§3.2, §3.3), then check whether the component's interfaces reference DA entities. If yes, DA may be affected.
- Change described as affecting a data entity → read DA (§3.2, §3.4), then check whether AA interfaces carry this entity (§3.3 IFC). If yes, AA is potentially affected.
- Change described as affecting the scope or vision → read AV (§3.2, §3.5), then cascade: any AV change may affect BA, AA, DA.
- Change described as affecting only technology → read TA (via SwA's handoff receipt); confirm whether any AA/DA constraint is violated. If no AA/DA constraint is violated, this is SwA-domain and SA is ○ (consulting).

---

### Step 2 — Identify All Impacted Architecture Artifacts

Based on Step 1 reading, produce a complete list of impacted artifacts for CR §2.4:

| Artifact ID | Current Version | Change Required | New Version |
|---|---|---|---|
| [AV / BA / AA / DA / other] | [current] | [what must change] | [new version after update] |

**Cascading impact rule:** Architecture artifacts have a directed dependency graph. Changes propagate downward:
- AV change → may cascade to BA, AA, DA
- BA change → may cascade to AA, DA
- AA change → may cascade to DA (and vice versa — mutual reference)
- DA change → may cascade to AA (mutual reference)
- AA or DA change → cascades to TA (SwA must update TA; create handoff to SwA)

For each cascading impact, SA notes the impact but does not modify the affected artifact at this step. The Change Record authorises the modifications; SA executes them in Step 7.

---

### Step 3 — Assess Change Classification

Apply `agile-adm-cadence.md §10` change classification rules:

| Class | Selection Criteria |
|---|---|
| **Minor** | No architecture artifact requires modification; change is localised to a single implementation SBB; no safety-relevant system affected; documentation correction only |
| **Significant** | One or more architecture artifacts require modification; no safety-relevant system affected; affects a single phase's artifacts |
| **Major** | Multiple phases' artifacts are affected; or cross-cutting architectural decisions must change; no Safety-Critical classification |
| **Safety-Critical** | Any part of the change touches a safety-relevant component, constraint, or data entity — regardless of scope size |

**Classification rule:** Assign the highest applicable class. When in doubt between two classes, assign the higher class.

**Safety-Critical determination:** If the change affects any:
- BPR-nnn with `Safety-Relevant: Yes`
- APP-nnn with `Safety-Relevant: Yes`
- DE-nnn with classification `Safety-Critical` or `Safety-Relevant: Yes`
- AV §3.7 Safety Envelope
- Any SCO constraint

→ classify as Safety-Critical, regardless of how minor the scope appears.

Write the classification rationale in CR §2.3.

---

### Step 4 — CSCO Coordination (Mandatory for Safety-Relevant Changes)

If the change is classified as Safety-Critical, or if any affected artifact has `safety-relevant: true`:

1. **Before completing the Change Record:** Create handoff to CSCO requesting safety impact assessment. The handoff must include:
   - The list of affected artifacts from Step 2
   - The proposed change classification from Step 3
   - The specific components, processes, or data entities identified as potentially safety-relevant

2. **Halt CR completion** until CSCO provides the Safety Impact Analysis (CR §2.5). SA may draft §2.1, §2.2, §2.3, and §2.4 while awaiting CSCO, but may not complete or baseline the CR.

3. **CSCO completes CR §2.5** — this section is CSCO-authored or co-authored; SA does not write content in §2.5. SA records what CSCO provides, verbatim.

4. **If CSCO is unavailable and the change is Safety-Critical:** Raise `ALG-014` immediately. Halt all change implementation. Do not proceed until CSCO is available.

For non-safety-relevant changes (Minor and Significant with no safety-relevant artifacts): proceed to Step 5 without CSCO coordination for the CR (CSCO is still informed via PM; not a blocking prerequisite for Minor/Significant).

---

### Step 5 — Produce Change Record

Complete all sections of the Change Record per `framework/artifact-schemas/change-record.schema.md`:

**§2.1 Summary Header:**
- `artifact-type: change-record`
- `safety-relevant: true/false` (from Step 3 assessment)
- `csco-sign-off: true/pending/not-required` (required for Major and Safety-Critical)

**§2.2 Change Request:**
- Copy fields from PM's CR-000; add SA's refinements to the Description field.
- `Source` field: classify the source — Defect / Requirement Change / Technology Obsolescence / Regulatory / Business Change / Architecture Inconsistency.

**§2.3 Change Impact Classification:** From Step 3.

**§2.4 Affected Artifacts:** From Step 2.

**§2.5 Safety Impact Analysis:** From CSCO (Step 4). Write `Not applicable` only if the change has been confirmed by CSCO as non-safety-relevant — do not assume.

**§2.6 Decision Record:**
- Decision authority by class: Minor (PM decides; SA records); Significant (SA + PM decide); Major (all affected artifact owners + CSCO decide); Safety-Critical (CSCO gates; SA + PM record).
- Do NOT write `Approved` in §2.6 unilaterally. SA submits the CR; the appropriate authority approves.

**§2.7 Implementation Actions:** For each artifact that must be updated:
- One ACT-nnn per artifact
- Owner: SA (for architecture artifacts); SwA (for TA); PM (for project-repository artifacts)
- Target sprint: assign based on urgency (Immediate → current sprint; Next Sprint → next planned sprint; Planned → future sprint per PM scheduling)

Write CR to `architecture-repository/change-records/cr-<id>-0.1.0.md`.

---

### Step 6 — Baseline CR and Create Handoffs

Once the CR has been reviewed and approved by the appropriate decision authority:

1. Update CR to version 1.0.0 (decision recorded; approved).
2. Emit `artifact.baselined` for CR at version 1.0.0.
3. Create handoff to PM: `handoff-type: phase-return-scope` — includes phase-return scope determination (Step 7 pre-requisite):
   - Which phases must be revisited
   - Which artifacts are authorised for update
   - Urgency classification and sprint target

4. Create handoff to SwA (if technology-layer changes are required): `handoff-type: architecture-change-impact` — SA's assessment of which AA/DA constraints the TA must update to reflect.

5. Cast `gate.vote_cast` for Phase H gate (H formal):
   - `result: approved` if all CR sections are complete, decision authority has approved, and phase-return scope is determined.
   - `result: veto` if SA identifies a safety-relevant item that has not received CSCO sign-off, or if the CR's decision record assigns approval authority below the correct level for the classification.

---

### Step 7 — Update Affected Architecture Artifacts

For each ACT-nnn in CR §2.7 assigned to SA:

1. Open the affected artifact from `architecture-repository/`.
2. Apply the change as specified in the CR action description.
3. Increment the artifact version:
   - Minor fix / documentation: patch increment (e.g., 1.0.0 → 1.0.1)
   - Significant change to a specific section: minor increment (e.g., 1.0.0 → 1.1.0)
   - Structural change affecting multiple sections: minor or major increment per impact scope; consult with PM if major increment is warranted
4. Write the updated artifact summary header change log entry.
5. Emit `artifact.baselined` for the updated artifact.
6. Create handoff event to notify consuming agents (SwA if AA/DA changed; CSCO if safety-relevant content changed).

**Phase-return scope execution:**

| Change Class | Phase Return Required | SA Action |
|---|---|---|
| Minor | None — H only | Update documentation; increment patch version |
| Significant | Return to the phase that originally produced the affected artifact | Update affected artifact; re-submit for phase gate if gate criteria are impacted |
| Major | Return to the earliest phase whose artifact is affected | May require AV revision → BA revision → AA/DA revision in sequence; coordinate with PM on sprint plan |
| Safety-Critical | Determined by CSCO in §2.5 | Follow CSCO's determination; SA updates architecture artifacts; CSCO gates all updates |

**For phase-revisit scenarios:** The returning phase is executed with `trigger: revisit` and `phase_visit_count > 1`. SA skill files handle revisits — the procedures are identical, but the existing artifacts are the starting point rather than a blank canvas. SA increments the artifact version rather than creating a new artifact file, unless the scope of change warrants a fresh document (in which case the old version is preserved and the new version cross-references it).

---

## Feedback Loop

### SA ↔ SwA Conflict on Technology Impact Scope

- **Iteration 1:** SA produces Change Record with affected artifact list; SwA reviews and may disagree on whether the TA is affected (SwA may believe the change is contained in AA/DA; or conversely, SwA may claim TA changes are needed that SA did not identify). SA reviews SwA's position against the architecture artifact constraints.
- **Iteration 2:** SA and SwA exchange one further round of structured feedback (via handoff log entries).
- **Termination:** Agreement on technology impact scope; CR §2.4 updated to reflect consensus.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` to PM after 2 iterations. PM adjudicates using RACI: if the conflict is about whether an AA/DA constraint is violated, SA's position governs (SA is ● for AA/DA). If the conflict is about whether a TA constraint exists, SwA's position governs (SwA is ● for TA). PM records the decision.

### SA ↔ CSCO Coordination on Safety Impact

- **Iteration 1:** SA submits safety-relevant change details to CSCO; CSCO produces §2.5 Safety Impact Analysis.
- **Iteration 2 (if needed):** SA has questions about CSCO's §2.5 conclusions; sends structured feedback request; CSCO clarifies.
- **Termination:** §2.5 is complete and CSCO has signed off; CR can be baselined.
- **Max iterations:** 2.
- **Escalation:** If CSCO identifies a safety constraint violation in the change, raise `ALG-001`. If CSCO is unavailable, raise `ALG-014`. Do not baseline the CR without CSCO sign-off on safety-relevant changes.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-001 | The proposed change would violate a safety constraint in the current SCO — either SA identifies this during impact assessment or CSCO flags it in §2.5 | S1 | Halt change implementation; emit `alg.raised`; notify CSCO immediately and PM concurrently; do not approve the CR until CSCO provides resolution |
| ALG-003 | During change impact assessment, SA identifies that the change affects a regulatory obligation that was not previously identified in the architecture artifacts | S1 | Emit `alg.raised`; notify CSCO immediately and PM concurrently; halt impact classification until CSCO assesses the regulatory dimension |
| ALG-006 | The change requires a phase return to Phase A or Phase B, but the baseline artifacts for those phases are inconsistent with the current state of later-phase artifacts — creating a dependency resolution problem that cannot be resolved within the current sprint | S2 | Emit `alg.raised`; PM restructures the sprint plan to accommodate the extended phase return; SA documents the dependency chain |
| ALG-010 | The two-iteration SA↔SwA feedback loop on technology impact scope has been exhausted without resolution | S3 | Emit `alg.raised`; PM adjudicates; SA documents both positions in the CR until PM decision is received |
| ALG-014 | A change is classified Safety-Critical but CSCO is unavailable to perform the §2.5 Safety Impact Analysis | S1 | Halt all change implementation; emit `alg.raised`; PM records and awaits CSCO availability; SA writes the CR with §2.5 blank and `status: awaiting-csco` |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Change Record (`CR`) | `architecture-repository/change-records/cr-<id>-<version>.md` | 1.0.0 after decision authority approves | `artifact.baselined` |
| Updated architecture artifacts (as required by CR §2.7) | `architecture-repository/<domain>/<artifact>-<new-version>.md` | Per version increment rules in Step 7 | `artifact.baselined` (per updated artifact) |
| Handoff to PM (phase-return scope) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to SwA (technology impact, if applicable) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (safety impact assessment request) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase H gate vote | EventStore | — | `gate.vote_cast` |

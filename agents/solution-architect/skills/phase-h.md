---
skill-id: SA-PHASE-H
agent: SA
name: phase-h
display-name: Phase H — Architecture Change Management (Business/Motivation/Strategy Layer)
invoke-when: >
  PM routes a change request to SA via handoff (CR-000 intake), or a phase.return-triggered
  event identifies SA-owned architecture artifacts (AV, BA, motivation entities, strategy
  entities, business entities) as affected. SA does not own the application/technology-layer
  Change Record — that is SwA's parallel track.
trigger-phases: [H]
trigger-conditions:
  - handoff.created (handoff-type=change-record-intake, to=solution-architect)
  - phase.return-triggered (affected-artifacts includes AV or BA or motivation/ or strategy/ or business/)
  - sprint.started (phase=H)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [Change Record (business/motivation/strategy layer), Updated Architecture Artifacts (motivation/strategy/business layers)]
complexity-class: complex
version: 1.1.0
---

# Skill: Phase H — Architecture Change Management (Business/Motivation/Strategy Layer)

**Agent:** Solution Architect  
**Version:** 1.1.0  
**Phase:** H — Architecture Change Management  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §5.9 and §10`, `framework/artifact-schemas/change-record.schema.md`, `raci-matrix.md §3.10`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Runtime Tooling Hint


Representation choice (balanced and mandatory):
- Use `.puml` diagrams when flow, topology, sequence, trust boundaries, or interaction context is the primary concern.
- Use matrix artifacts (`model_create_matrix`) for dense many-to-many mappings, coverage, and traceability where node-link readability degrades.
- Do not replace contextual architecture views with matrices alone: keep a reasonable set of diagrams that preserves end-to-end context for the domain slice.
- Practical threshold: if a single node-link view would exceed about 25 elements or become edge-dense, keep/author at least one contextual diagram and shift dense cross-reference detail to a matrix.

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| PM's intake record (Warm-Start Change Record `CR-000`) | Project Manager | Version 0.1.0; PM has performed initial intake and urgency classification | PM creates CR-000 from the change request before routing to SA; SA does not initiate the Change Record — SA completes it |
| Affected motivation/strategy/business artifact summary headers | SA (self-read) from `architecture-repository/model-entities/` | Current baselined versions | SA reads motivation/, strategy/, business/ layers only; application-layer entities are SwA's domain |
| Current Architecture Principles Register (`PR`) | SA (self-read) | Current version | SA checks whether the proposed change violates any architecture principle |
| Safety Constraint Overlay (`SCO`) — current version | CSCO | Current baselined version | Required before SA can determine whether a change is safety-relevant |
| Requirements Register (`RR`) | Product Owner | Current version | Required if the change source is a requirement change — SA must assess RR impact |
| `sprint.started` event for the Phase H sprint | PM | Emitted | Hard prerequisite; SA does not begin Phase H work without this event |

**Phase H co-ownership note:** SA is ● for the business/motivation/strategy-layer Change Record. SwA runs a parallel Phase H track (skill: SwA-PHASE-H) and is ● for the application/technology-layer Change Record. Both tracks coordinate through PM. SA hands off to SwA when business-layer analysis determines that application or technology artifacts are affected.

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
| Impact on application/technology-layer artifacts (e.g., change affects APP/DOB/TA) — is SwA's application/technology CR also needed? | Partially — SA flags likely AA/DA/TA impact; SwA confirms scope and produces application/technology CR | SwA (via PM) | §2.4 Affected Artifacts, §2.7 Implementation Actions |
| Baseline state of affected artifacts (if some artifacts are not yet baselined — EP-H entry where architecture is partially complete) | Yes — SA must raise this to PM; may require earlier EP before Phase H can proceed | PM | All CR sections |

### Clarification Triggers

SA raises a CQ when:

1. **Change scope unclear:** The PM's CR-000 describes a change that could be: (a) a documentation correction affecting no architecture element, (b) a defect in an architecture artifact, (c) a new capability request, or (d) a structural modification to the architecture. SA cannot determine the classification without clarification. Bounded CQ: "Does this change require any modification to: (a) the Business Capability Map, (b) the Application Component Catalog, (c) the Data Entity Catalog, (d) the Architecture Vision Statement? Or does it affect only the Technology Architecture or implementation?"
2. **Safety impact unclear:** The change affects a component or process that is near (but not clearly within) the safety boundary defined in the SCO. SA cannot determine `safety-relevant: true/false` unilaterally. SA raises a CQ to CSCO: "Does component [APP-nnn / BPR-nnn / DE-nnn] fall within the safety boundary defined in SCO §[section] for this engagement?"
3. **Phase return scope unclear for Major changes:** A Major change affects multiple artifacts spanning multiple phases. SA cannot determine the minimum phase-return scope without understanding the causal chain. If the causal chain is not clear from available artifacts, SA raises a CQ to PM and SwA jointly: "Does this change require both Phase C and Phase B revisit, or can it be addressed in Phase C alone?"

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="H", artifact_type="change-record")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Pre-condition Check

1. Confirm `sprint.started` has been emitted for the Phase H sprint.
2. Read PM's CR-000 in full — understand the change request, urgency, and any PM-assigned initial classification.
3. Check: do the affected architecture artifacts exist in `architecture-repository/`? If not (e.g., EP-H entry where Phase A was never executed), SA must notify PM immediately. PM determines whether to escalate to an earlier entry point. SA does not proceed with Phase H on non-existent baseline artifacts.
4. Check: is the current SCO available? If CSCO has not yet produced a current SCO baseline, SA notes this gap before assessing safety relevance. If the change is potentially safety-relevant, SA raises a blocking CQ to CSCO before completing the CR.

---

### Step 1 — Read Affected Artifact Summary Headers

For each architecture artifact potentially affected by the change (as identified in CR-000):

1. Read the summary header of the artifact from `architecture-repository/model-entities/` (motivation/, strategy/, business/ layers).
2. Note: current version, phase of origin, `safety-relevant` flag, `csco-sign-off` status.
3. Identify the sections of the artifact most relevant to the described change.
4. Do NOT modify any artifact at this step — assessment only.

**SA scope of review — business/motivation/strategy layer only:**
- Change described as affecting a business process → read BA business layer entities (BPR-nnn, BFN-nnn, BSV-nnn, ACT-nnn). If the process change ripples to application components or data entities, flag for SwA's parallel track (Step 6 handoff) — SA does not assess application-layer impact.
- Change described as affecting business goals, drivers, or requirements → read motivation entities (GOL-nnn, DRV-nnn, REQ-nnn, CST-nnn, PRI-nnn). Cascade: GOL/DRV change may affect BA; if BA changes, notify SwA via handoff (Step 6).
- Change described as affecting the scope or vision → read AV overview entities. Cascade: AV change may affect BA (SA's domain). If AV change affects application or technology layers, create handoff to SwA for their parallel CR track.
- Change described as affecting only application components, data entities, or technology → SA's scope is limited to checking whether any BA/motivation constraint is violated. If no business-layer constraint is violated, this is SwA-domain; SA provides consulting acknowledgement only.

---

### Step 2 — Identify All Impacted Architecture Artifacts

Based on Step 1 reading, produce a complete list of impacted artifacts for CR §2.4:

| Artifact ID | Current Version | Change Required | New Version |
|---|---|---|---|
| [AV / BA / AA / DA / other] | [current] | [what must change] | [new version after update] |

**Cascading impact rule — SA's layer only:** SA manages the business/motivation/strategy dependency chain. Changes propagate downward within SA's domain, then hand off to SwA for application/technology layers:

| From | SA action | SwA handoff required? |
|---|---|---|
| AV change | May cascade to BA (SA updates) | Yes — if AV change affects application scope or technology envelope |
| BA change (BPR, BFN, BSV, ACT, BOB) | SA updates business entities | Yes — if BA change ripples to APP/DOB realisation connections |
| Motivation change (GOL, DRV, REQ, CST, PRI) | SA updates motivation entities | Yes — if constraint or requirement change affects application or technology design |
| Application-layer change (APP, DOB) | SA assesses only: does any BA constraint change? | SwA owns the application-layer CR; SA provides consulting acknowledgement |
| Technology-layer change (TA, AC) | SA assesses only: does any principle/BA constraint change? | SwA owns the technology-layer CR; SA provides consulting acknowledgement |

For each cascading impact within SA's domain, SA notes the impact but does not modify the affected artifact at this step. The Change Record authorises the modifications; SA executes them in Step 7.

**Traceability-chain preservation rule (mandatory):** Every approved change must preserve or deliberately revise the chain `STK -> DRV -> GOL -> OUT -> COA -> CAP -> (BPR/BSV) -> VS-stage value`. If any segment is removed or altered, CR §2.4 must explicitly list the broken link and the compensating update action before approval.

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
- GOL-nnn, REQ-nnn, CST-nnn related to a safety objective
- AV safety envelope section
- Any SCO constraint

Note: APP-nnn and DOB-nnn safety relevance is assessed by SwA in the parallel application/technology Change Record.

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

**§2.4 Affected Artifacts:** From Step 2. Scope: business/motivation/strategy layer artifacts (AV, BA entities, motivation entities, strategy entities). Application/technology-layer artifacts are listed in SwA's parallel application/technology CR.

**§2.5 Safety Impact Analysis:** From CSCO (Step 4). Write `Not applicable` only if the change has been confirmed by CSCO as non-safety-relevant — do not assume.

**§2.6 Decision Record:**
- Decision authority by class: Minor (PM decides; SA records); Significant (SA + PM decide); Major (all affected artifact owners + CSCO decide); Safety-Critical (CSCO gates; SA + PM record).
- Do NOT write `Approved` in §2.6 unilaterally. SA submits the CR; the appropriate authority approves.

**§2.7 Implementation Actions:** For each artifact that must be updated within SA's domain:
- One ACT-nnn per artifact
- Owner: SA (for business/motivation/strategy artifacts); application/technology-layer actions listed in SwA's parallel CR; PM (for project-repository artifacts)
- Target sprint: assign based on urgency (Immediate → current sprint; Next Sprint → next planned sprint; Planned → future sprint per PM scheduling)

Write SA's CR to `architecture-repository/change-records/cr-<id>-business-0.1.0.md`.

---

### Step 6 — Baseline CR and Create Handoffs

Once the CR has been reviewed and approved by the appropriate decision authority:

1. Update CR to version 1.0.0 (decision recorded; approved).
2. Emit `artifact.baselined` for CR at version 1.0.0.
3. Create handoff to PM: `handoff-type: phase-return-scope` — includes phase-return scope determination (Step 7 pre-requisite):
   - Which phases must be revisited (business/motivation/strategy layer)
   - Which artifacts are authorised for update
   - Urgency classification and sprint target

4. Create handoff to SwA: `handoff-type: phase-h-application-technology-track` — triggers SwA to run the parallel application/technology-layer Phase H track (SwA-PHASE-H). The handoff must include:
   - SA's business-layer CR at version 1.0.0 (reference by artifact-id)
   - List of application/technology artifacts SA identified as potentially affected (Step 2 cascade table rows with "SwA handoff required: Yes")
   - SA's consulting view on whether AA/DA entities need revision (not prescriptive — SwA determines application/technology scope)
   - Change classification (from Step 3)
   - This handoff is created regardless of whether SA identified any application-layer impact — SwA must always confirm whether the business-layer change affects their domain.

5. Cast `gate.vote_cast` for Phase H gate (H formal — business/motivation/strategy layer):
   - `result: approved` if all CR sections are complete, decision authority has approved, and phase-return scope is determined.
   - `result: veto` if SA identifies a safety-relevant item that has not received CSCO sign-off, or if the CR's decision record assigns approval authority below the correct level for the classification.

---

### Step 7 — Update Affected Architecture Artifacts

For each ACT-nnn in CR §2.7 assigned to SA (business/motivation/strategy-layer artifacts only):

1. Open the affected artifact from `architecture-repository/model-entities/` (motivation/, strategy/, or business/ subdirectory).
2. Apply the change as specified in the CR action description.
3. Increment the artifact version:
   - Minor fix / documentation: patch increment (e.g., 1.0.0 → 1.0.1)
   - Significant change to a specific section: minor increment (e.g., 1.0.0 → 1.1.0)
   - Structural change affecting multiple sections: minor or major increment per impact scope; consult with PM if major increment is warranted
4. Write the updated artifact summary header change log entry.
5. Emit `artifact.baselined` for the updated artifact.
6. Create handoff event to notify consuming agents (SwA if business-layer changes affect application-layer realisation; CSCO if safety-relevant content changed).

**Out of scope for SA in Step 7:** SA does not update application-layer entities (APP, DOB, ASV, AIF) or technology-layer artifacts in this step. Those are updated by SwA through the parallel application/technology CR track.

**Phase-return scope execution:**

| Change Class | Phase Return Required (SA domain) | SA Action |
|---|---|---|
| Minor | None — H only | Update documentation; increment patch version |
| Significant | Return to the phase that originally produced the affected business-layer artifact | Update affected artifact; re-submit for phase gate if gate criteria are impacted |
| Major | Return to earliest phase whose business/motivation/strategy artifact is affected | May require AV revision → BA revision in sequence; coordinate with PM on sprint plan; notify SwA via handoff if cascade reaches Phase C |
| Safety-Critical | Determined by CSCO in §2.5 | Follow CSCO's determination; SA updates business-layer artifacts; CSCO gates all updates |

**Note on application/technology phase returns:** When a Major change requires Phase C or later revision, SA notifies SwA (via Step 6 handoff) and SwA's parallel CR track governs the application/technology phase return independently. PM coordinates the combined sprint plan.

**For phase-revisit scenarios:** The returning phase is executed with `trigger: revisit` and `phase_visit_count > 1`. SA skill files handle revisits — the procedures are identical, but the existing artifacts are the starting point rather than a blank canvas. SA increments the artifact version rather than creating a new artifact file, unless the scope of change warrants a fresh document (in which case the old version is preserved and the new version cross-references it).

---

## Feedback Loop

### SA ↔ SwA Coordination on Application/Technology Impact Scope

- **Iteration 1:** SA produces business-layer CR and sends Step 6 handoff to SwA. SwA may confirm the application/technology scope is unaffected (no parallel CR needed), or may identify application-layer impacts that require revision. SwA feeds their assessment back to SA for §2.4 cross-reference in SA's CR.
- **Iteration 2 (if needed):** SA has questions about SwA's scope assessment; sends structured feedback request; SwA clarifies.
- **Termination:** Both CRs have consistent §2.4 cross-references; SA's business-layer CR and SwA's application/technology CR are aligned.
- **Max iterations:** 2.
- **Escalation:** Raise `ALG-010` to PM after 2 iterations. PM adjudicates using RACI: SA governs business-layer scope; SwA governs application/technology scope. PM records the decision.

### Personality-Aware Conflict Engagement

SA and SwA operate across a layer boundary in Phase H. When scope disputes arise (e.g., is a business-capability change a BA update or an APP update?), SA applies the ArchiMate layer boundary rule: **motivation/strategy/business entities are SA's domain; application/technology entities are SwA's domain.** SA does not assert ownership of application-layer Change Record content. If the boundary is genuinely ambiguous, SA requests PM adjudication rather than unilaterally expanding scope. Governed by `framework/agent-personalities.md §6`.

### SA ↔ CSCO Coordination on Safety Impact

- **Iteration 1:** SA submits safety-relevant change details to CSCO; CSCO produces §2.5 Safety Impact Analysis.
- **Iteration 2 (if needed):** SA has questions about CSCO's §2.5 conclusions; sends structured feedback request; CSCO clarifies.
- **Termination:** §2.5 is complete and CSCO has signed off; CR can be baselined.
- **Max iterations:** 2.
- **Escalation:** If CSCO identifies a safety constraint violation in the change, raise `ALG-001`. If CSCO is unavailable, raise `ALG-014`. Do not baseline the CR without CSCO sign-off on safety-relevant changes.

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
| Business/Motivation/Strategy Change Record (`CR`) | `architecture-repository/change-records/cr-<id>-business-<version>.md` | 1.0.0 after decision authority approves | `artifact.baselined` |
| Updated business/motivation/strategy artifacts (as required by CR §2.7) | `architecture-repository/model-entities/{motivation,strategy,business}/<entity>-<new-version>.md` | Per version increment rules in Step 7 | `artifact.baselined` (per updated artifact) |
| Handoff to PM (phase-return scope — business layer) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to SwA (parallel application/technology Phase H track — always created) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (safety impact assessment request, if safety-relevant) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Phase H gate vote (business/motivation/strategy layer) | EventStore | — | `gate.vote_cast` |

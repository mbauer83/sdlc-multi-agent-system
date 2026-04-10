---
skill-id: SwA-PHASE-E
agent: SwA
name: phase-e
display-name: Phase E — Opportunities and Solutions
invoke-when: >
  Phase D gate has passed and the Technology Architecture is baselined at 1.0.0; Phase E
  Architecture Sprint starts and SwA begins consolidated gap analysis and candidate enumeration.
invoke-never-when: >
  <!-- TODO: write plain-English condition that prevents misrouting to this skill -->

trigger-phases: [E]
trigger-conditions:
  - gate.evaluated (from_phase=D, result=passed)
  - sprint.started (phase=E)
  - artifact.baselined (artifact-type=technology-architecture, version=1.0.0)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E]
primary-outputs: [Gap Analysis Matrix, Implementation Candidate Catalog, Transition Architecture plateau outline]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase E — Opportunities and Solutions

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** E — Opportunities and Solutions  
**Skill Type:** Architecture production + Planning contribution  
**Framework References:** `agile-adm-cadence.md §6.6`, `raci-matrix.md §3.7`, `framework/artifact-schemas/technology-architecture.schema.md §3.10`, `framework/artifact-schemas/implementation-plan.schema.md §3.2–3.3`, `algedonic-protocol.md`, `clarification-protocol.md`

---

## Runtime Tooling Hint

Diagram and matrix conventions apply only when this skill explicitly produces or updates diagram artifacts; use `framework/diagram-conventions.md` as the source of truth.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Technology Architecture (`TA`) | SwA | **Baselined** (v1.0.0+) | Self-produced in Phase D; must be fully quality-gated before Phase E begins |
| Application Architecture (`AA`) | Solution Architect | **Baselined** (v1.0.0+) | Required for cross-domain gap analysis |
| Data Architecture (`DA`) | Solution Architect | **Baselined** (v1.0.0+) | Required for cross-domain gap analysis |
| Technology Gap Analysis | SwA | Draft (v0.1.0+) from Phase D | Upgraded to 1.0.0 in this phase |
| Application-Level Gap Analysis (from AA §3.8) | Solution Architect | Baselined within AA | Read from AA artifact |
| Data-Level Gap Analysis (from DA §3.8) | Solution Architect | Baselined within DA | Read from DA artifact |
| Risk Register (draft) | Project Manager | Draft | PM initiates Risk Register; SwA contributes technology risks |
| Architecture Principles Register (`PR`) | Solution Architect | Baselined | Informs build/buy/reuse criteria (e.g., open-source preference) |
| Enterprise Solutions Landscape (`ESL`) | `enterprise-repository/solutions-landscape/` | Draft acceptable | Source for reuse candidates; absence does not block |
| Sprint kickoff event | PM | `sprint.started` emitted | Do not begin work before PM emits this event |

**RACI note:** SwA is **●** (accountable) for Implementation Candidate Catalog and Gap Analysis Matrix. PM is **●** for Work Package Catalog, Risk Register, and Architecture Roadmap draft. SwA contributes technical content to all three PM-owned artifacts but does not own them.

---

## Knowledge Adequacy Check

### Required Knowledge

- All three Phase C/D gap analyses: technology (from TA §3.10), application (from AA §3.8), data (from DA §3.8)
- Enterprise Solutions Landscape: what SBBs already exist in the enterprise that could be reused
- Build/buy/reuse policy: does the organisation have a stated policy (e.g., open-source preferred, COTS preferred for commodity capabilities)?
- Risk tolerance: what level of technical risk (vendor dependency, new technology adoption) is the organisation willing to accept?
- QA Engineer's initial test strategy scope (if the QA skill has been activated concurrently)

### Known Unknowns

The following gaps are predictably present at Phase E entry:

1. **Build/buy policy**: Unless stated in the Architecture Principles Register or Requirements Register, the organisation's preference between building custom software, purchasing commercial-off-the-shelf (COTS) products, or reusing existing enterprise solutions is not known. This significantly affects the Implementation Candidate Catalog.
2. **Enterprise reuse candidates**: Even if the Enterprise Solutions Landscape exists, the maturity and reusability of listed SBBs may be unknown without a separate reuse assessment.
3. **Dependency and sequencing constraints**: Technical dependencies between implementation candidates may create sequencing constraints (e.g., authentication must be implemented before any user-facing feature). The full dependency graph may not be apparent until candidates are enumerated.
4. **QA test complexity**: The QA Engineer's estimate of test complexity per candidate affects whether a candidate is classified as high- or low-complexity in the Implementation Candidate Catalog.

### Clarification Triggers

Raise a CQ (`target: User`) if:
- Build/buy policy is not inferable from any available artifact and the two options would produce materially different candidates (e.g., buy an identity provider vs. build one)
- A reuse candidate from the Enterprise Solutions Landscape requires significant modification (>50% change) — is it still "reuse" or effectively "build"?
- Organisational risk tolerance for new technology adoption is unknown and materially affects candidate selection

Route structured feedback to SA (`target: Solution Architect`) if:
- The AA gap analysis omits components that appear in the AA Component Catalog
- An AA-identified gap cannot be classified into the GAP-domain taxonomy (Business / Application / Data / Technology) without SA clarification

Route to PM if:
- Build/buy policy is a board-level decision that requires commercial negotiation
- Scope of the Implementation Candidate Catalog (should it include all gaps or only in-scope gaps?) is ambiguous

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="E", artifact_type="implementation-plan")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="E")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 1 — Produce Consolidated Gap Analysis Matrix

1.1 Read gap analyses from all three architecture domains:
- **Technology gaps**: from TA §3.10 (produced in Phase D)
- **Application gaps**: from AA §3.8
- **Data gaps**: from DA §3.8

1.2 Assign each gap a unique GAP-nnn identifier. Do not reuse identifiers from per-artifact gap analyses — the Gap Analysis Matrix is a cross-domain, consolidated view.

1.3 For each gap, record:
- **Gap ID** (GAP-nnn)
- **Domain**: Business / Application / Data / Technology (multiple domains permissible if cross-cutting)
- **Description**: what the gap is in plain language
- **ABBs Affected**: APP-nnn, DE-nnn, TC-nnn identifiers of the affected building blocks
- **Baseline State**: what exists today (or "none" for greenfield capabilities)
- **Target State**: what the architecture specifies must exist
- **Priority**: High / Medium / Low — determined by dependency analysis (blocking gaps are High) and business impact

1.4 Identify cross-cutting gaps: gaps that span multiple domains (e.g., a missing identity platform affects Application, Data, and Technology domains simultaneously). These are captured as a single GAP-nnn with multiple domain tags.

1.5 Baseline the Gap Analysis Matrix at `technology-repository/gap-analysis/GAM-<nnn>-1.0.0.md`. Emit `artifact.baselined`.

### Step 2 — Enumerate Implementation Candidates

2.1 For each GAP-nnn in the Gap Analysis Matrix, identify one or more implementation candidates. A candidate is a specific approach to closing the gap.

2.2 For each candidate, determine the **build/buy/reuse/retire** option:
- **Build**: develop custom software or configuration to close the gap
- **Buy**: procure a COTS product or SaaS service
- **Reuse**: adopt an existing SBB from the enterprise solutions landscape (with or without modification)
- **Retire**: decommission a component that creates a gap by its continued presence (negative gap resolution)

2.3 **Build/Buy/Reuse Evaluation Criteria** (apply in order; not ad hoc):
1. Is there a mandatory ADR or enterprise SIB entry that mandates a specific solution? → Follow mandate.
2. Does the enterprise Solutions Landscape contain a candidate that satisfies ≥80% of the gap's requirements without modification? → Prefer Reuse.
3. Is the gap a commodity capability (authentication, logging, monitoring) with mature COTS solutions? → Prefer Buy.
4. Does the Architecture Principles Register express a preference (e.g., "open-source preferred")? → Apply preference.
5. Is the gap a differentiating capability specific to this system's business value? → Prefer Build.
6. Does a Build option create unacceptable vendor lock-in risk vs. a Buy option? → Document trade-off in IC entry.

2.4 Assign each candidate an IC-nnn identifier. Record in the Implementation Candidate Catalog:
- **Candidate ID** (IC-nnn)
- **Name**: short descriptive name
- **Addresses Gap**: GAP-nnn reference(s)
- **Decision**: Build / Buy / Reuse / Retire
- **Preferred Option**: specific product, library, or approach (if Buy or Reuse: name the product)
- **Rationale**: why this option, applying criteria from §2.3
- **Dependencies**: other IC-nnn candidates this depends on (ordering constraint)
- **Estimated Complexity**: Low / Medium / High (qualitative; input to PM Work Package sizing)
- **Risk Level**: Low / Medium / High (technical risk: new technology, unknown vendor, integration complexity)

2.5 **Reuse candidates require an additional reuse assessment entry**: confirm the existing SBB's version, its functional coverage of the gap, and whether modification is needed. If modification >20% of the SBB's scope, classify as Build (reuse with major modification).

**Diagram Step D — Sequence Diagrams (API Contract Flows)**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** For each implementation candidate that specifies API contracts or inter-component interfaces: call `list_artifacts(artifact_type="application-interface")` and `list_artifacts(artifact_type="application-component")` in the SA engagement architecture-repository to identify IFC-nnn and APP-nnn participants. If an entity is absent, raise a `diagram.display-spec-request` handoff to SA — do not create orphan aliases.
- **D2:** For each entity that will appear as a participant, verify its `§display ###sequence` subsection exists. If absent on SA-owned entities, raise a `diagram.display-spec-request` handoff; if absent on SwA-owned entities, add via `write_artifact` and run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.sequence")`. Author one sequence diagram per major API flow: entity artifact-ids as participant aliases; synchronous vs. async message notation; `alt`/`opt` blocks for error and auth paths. Do not merge independently triggered operational concerns into one linear sequence; split into separate files when causality is optional. For each sequence, document feature relevance and cross-layer traceability by including `connection-ids-used` and naming the related business process/service IDs in diagram notes or handoff narrative. Message labels must be API-contract quality (verb-led operation + explicit parameter list with consistent command/query naming), not narrative prose. Include required frontmatter comment block. Write to `technology-repository/diagram-catalog/diagrams/e-sequence-<flow-id>-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate before proceeding.

### Step 3 — Provide Input to Risk Register

3.1 For each IC-nnn with Risk Level Medium or High, contribute a risk entry to PM's Risk Register. SwA does not own the Risk Register (PM ●) but provides technical risk inputs via a structured contribution note.

3.2 Technology risk types to assess for each candidate:
- **Vendor/product risk**: single-vendor dependency, product end-of-life, licensing change
- **Integration complexity risk**: new API contracts, protocol mismatches, data format incompatibilities
- **Performance risk**: untested at required scale; performance characteristics unknown
- **Security risk**: new attack surface; dependency on unvetted libraries; credential management complexity
- **Operational risk**: new operational burden on the operating team; training required

3.3 For each technology risk contributed, record: Risk ID (to be assigned by PM), Description, Category (Technical/Safety/Regulatory), SwA-estimated Probability and Impact, and proposed mitigation.

3.4 Flag any risk where Probability × Impact ≥ 6 (using H=3, M=2, L=1 scale). Per `implementation-plan.schema.md §3.7`, severity ≥6 requires CSCO review. Notify PM explicitly when this threshold is exceeded.

### Step 4 — Collaborate with QA Engineer on Testing Implications

4.1 If the QA Engineer skill has been activated for Phase E (Initial Test Strategy), coordinate to identify testing implications for each IC-nnn:
- Which candidates introduce new integration boundaries that require contract testing?
- Which candidates involve safety-relevant components requiring additional test rigour?
- Which candidates have performance NFRs that require dedicated performance testing?

4.2 Provide QA with: the IC-nnn catalog, complexity assessments, and the list of safety-relevant candidates.

4.3 Receive QA's test complexity estimates and incorporate into the IC-nnn Risk Level assessments. If QA's test complexity estimate changes a candidate's risk classification, update the IC entry and notify PM.

4.4 This collaboration is conducted via handoff events (not direct writes). SwA hands off the IC catalog draft; QA provides a consulting note; SwA integrates.

### Step 5 — Provide Implementation Candidate Input to PM Work Package Catalog

5.1 The PM owns the Work Package Catalog. SwA provides technical input: the IC-nnn catalog is the primary input from which the PM constructs work packages.

5.2 Deliver the IC catalog to PM via handoff event. Include with the handoff:
- **Dependency ordering**: which IC-nnn candidates must be completed before others can begin (technical ordering constraint, not business priority ordering)
- **Parallel track candidates**: IC-nnn pairs that have no dependency relationship and can be worked in parallel
- **Critical path candidates**: IC-nnn candidates where delay blocks the most downstream candidates

5.3 Review the PM's Work Package Catalog draft (once produced) for technical correctness:
- Verify that dependency ordering in the Work Package Catalog is consistent with the IC dependency ordering
- Verify that work packages are not split in a way that creates a technically infeasible partial delivery state
- Flag any impossible sequencing to PM via structured feedback

### Step 6 — Provide Input to Architecture Roadmap

6.1 PM owns the Architecture Roadmap draft. SwA provides the technology adoption sequencing input:
- Which TC-nnn components must be in place before other components can be deployed (infrastructure dependencies)
- Phase-in / phase-out schedule for legacy components identified in the Technology Lifecycle Analysis (TA §3.8)
- Technology adoption milestones: key dates or delivery triggers for technology platform changes

6.2 For engagements with complex migrations (multiple transition states between baseline and target), identify whether multiple Transition Architecture states are required. If yes, signal to PM that Transition Architecture Diagrams will be produced in Phase F.

### Step 7 — Produce Transition Architecture Diagrams (initial)

7.1 If the gap analysis indicates that the distance between baseline and target architecture cannot be bridged in a single delivery wave, begin producing Transition Architecture Diagrams showing intermediate "plateau" states.

7.2 For Phase E, produce the initial plateau outline: a table identifying each transition state (TR-000 baseline → TR-001 → ... → TR-nnn target), the work packages included in each transition, and the ABBs active at each plateau. Full diagram production occurs in Phase F.

7.3 Write initial transition outline to `technology-repository/transition-architecture/TA-transitions-<nnn>-0.1.0.md` (draft version). Full baseline occurs in Phase F.

### Step 8 — Baseline Outputs and Cast Gate Vote

8.1 Baseline the Gap Analysis Matrix at `technology-repository/gap-analysis/GAM-<nnn>-1.0.0.md`. If not already emitted, emit `artifact.baselined`.

8.2 Baseline the Implementation Candidate Catalog at `technology-repository/implementation-candidates/ICC-<nnn>-1.0.0.md`. Emit `artifact.baselined`.

8.3 Complete the artifact summary headers for both artifacts per `agile-adm-cadence.md §10.2`.

8.4 Run quality gate self-check before baseline:
- [ ] Every GAP-nnn addresses a specific difference between baseline and target state in AA, DA, or TA
- [ ] Every GAP-nnn has at least one IC-nnn candidate
- [ ] Every IC-nnn has a documented build/buy/reuse decision with rationale referencing §2.3 criteria
- [ ] All IC-nnn candidates with High risk have corresponding Risk Register contributions delivered to PM
- [ ] Dependency ordering is acyclic (no circular IC dependencies)
- [ ] CSCO notified for any risk at severity ≥6

8.5 Cast gate vote for E→F: emit `gate.vote_cast` with `gate: E-F`, `vote: approved` (or `vote: blocked` with specific blocking condition).

---


## Common Rationalizations (Rejected)

| Rationalization | Rejection |
|---|---|
<!-- TODO: add 2-3 skill-specific rationalization rows -->
| "I can skip discovery because I already know the context from prior sessions" | Discovery is mandatory per Step 0; any skip must be recorded as a PM-accepted assumption with a risk flag; silent assumptions are governance violations |
| "A CQ with a reasonable assumed answer is equivalent to waiting — I'll proceed with the assumption" | Assumed answers must be explicitly recorded in the artifact with a risk flag; they never silently replace CQ answers |

## Feedback Loop

### PM Work Package Scoping Loop (SwA ↔ PM)

**Purpose:** Ensure the PM's Work Package Catalog correctly reflects technical dependencies and feasibility constraints.

- **Iteration 1**: SwA reviews PM's Work Package Catalog draft; raises structured feedback specifying any infeasible sequencing or dependency errors. PM revises and re-issues.
- **Iteration 2**: SwA re-reviews; accepts with documented exceptions or confirms resolution.
- **Termination**: Dependency ordering in Work Package Catalog is technically feasible.
- **Maximum iterations**: 2. If PM's iteration-2 revision still contains technically infeasible sequencing, SwA escalates to PM as ALG-010 (S3) and provides a specific feasibility statement that PM must adjudicate.
- **Escalation path**: ALG-010 → PM adjudicates (both positions reviewed; RACI applied — PM owns the catalog but cannot mandate technically infeasible sequencing); if unresolvable, ALG-005 → scope reassessment.

### QA Test Complexity Estimate Loop (SwA ↔ QA)

**Purpose:** Align IC complexity estimates with QA's test complexity assessment.

- **Iteration 1**: SwA hands off IC catalog draft to QA; QA provides test complexity consulting note. SwA updates Risk Level in IC entries where QA assessment differs.
- **Termination**: IC Risk Levels reflect both technical complexity (SwA) and test complexity (QA) inputs.
- **Maximum iterations**: 1 (QA consulting contribution, not an approval loop). If QA's test complexity estimates are significantly higher than SwA's expectation, swA raises the discrepancy to PM for Risk Register update.
- **Escalation**: No algedonic trigger for this loop unless QA's findings reveal a safety-relevant testing gap → ALG-013 if a safety-relevant component has no viable test approach.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="implementation-plan"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---


## Red Flags

Pre-escalation observable indicators. Raise an algedonic signal or CQ if two or
more of these are true simultaneously:

<!-- TODO: add 5-7 role-specific observable indicators for this skill -->
- Outputs section of the primary artifact is blank after completing the procedure
- Any required input artifact is missing and no CQ has been raised
- Feedback loop iteration count has reached the maximum with no resolution

## Algedonic Triggers <!-- workflow -->

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-001 | An implementation candidate would introduce a technology that violates an SCO safety constraint | S1 | Halt candidate; emit to CSCO and PM; remove candidate from IC catalog pending resolution |
| ALG-005 | Phase E gate has required two consecutive extensions due to unresolvable PM/SwA feasibility conflict | S2 | Emit to PM for scope reassessment; document both positions |
| ALG-006 | A dependency between implementation candidates creates a circular dependency that cannot be resolved within current scope | S2 | Emit to PM; restructure sprint plan may be required; flag to SA if the circular dependency traces to a logical architecture decision |
| ALG-008 | Any of the three gap analysis inputs (TA, AA, DA) is a draft artifact being consumed as authoritative | S2 | Emit to PM; halt gap analysis production until baselined inputs are available |
| ALG-010 | PM work package scoping loop exhausted (two iterations) without agreement on feasibility | S3 | Emit to PM for adjudication; provide written feasibility statement |
| ALG-016 | Build/buy CQ to user unanswered for more than two sprint cycles | S2 | PM consolidates CQs; escalates to user as priority |
| ALG-017 | Safety-domain gap identified where the correct implementation candidate cannot be determined without knowing a safety constraint that is not in any available artifact | S1 | Halt affected IC entries; emit to user (via PM) and CSCO concurrently |

---


## Verification

Before emitting the completion event for this skill, confirm:

<!-- TODO: extend with skill-specific checklist items -->
- [ ] All blocking CQs resolved or documented as PM-accepted assumptions
- [ ] Primary output artifact exists at the required minimum version
- [ ] CSCO sign-off recorded where required (`csco-sign-off: true`)
- [ ] All required EventStore events emitted in this invocation
- [ ] Handoffs to downstream agents created
- [ ] Learning entries recorded if a §3.1 trigger was met this invocation
- [ ] Memento state saved (End-of-Skill Memory Close)

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Gap Analysis Matrix (consolidated) | `technology-repository/gap-analysis/GAM-<nnn>-1.0.0.md` | 1.0.0 | `artifact.baselined` |
| Implementation Candidate Catalog | `technology-repository/implementation-candidates/ICC-<nnn>-1.0.0.md` | 1.0.0 | `artifact.baselined` |
| Technology Risk contributions to PM Risk Register | Delivered to PM via handoff | — | `handoff.created` |
| Dependency ordering + parallel track analysis | Delivered to PM via handoff (IC catalog input) | — | `handoff.created` |
| Transition Architecture plateau outline (draft) | `technology-repository/transition-architecture/TA-transitions-<nnn>-0.1.0.md` | 0.1.0 (draft; baselined in Phase F) | — |
| E→F Gate vote | EventStore | — | `gate.vote_cast` |

---

## End-of-Skill Memory Close <!-- workflow -->

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="E", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

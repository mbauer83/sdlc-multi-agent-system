---
skill-id: SwA-PHASE-F
agent: SwA
name: phase-f
display-name: Phase F — Migration Planning
invoke-when: >
  Phase E gate has passed and GAM and ICC are both baselined at 1.0.0; Phase F Architecture
  Sprint starts and SwA produces Transition Architecture Diagrams and technical sequencing input.
trigger-phases: [F]
trigger-conditions:
  - gate.evaluated (from_phase=E, result=passed)
  - sprint.started (phase=F)
  - artifact.baselined (artifact-type=implementation-candidate-catalog, version=1.0.0)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F]
primary-outputs: [Transition Architecture Diagrams, Technical Sequencing Analysis, Environment Provisioning Requirements]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase F — Migration Planning

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** F — Migration Planning  
**Skill Type:** Architecture production + Planning contribution  
**Framework References:** `agile-adm-cadence.md §6.7`, `raci-matrix.md §3.8`, `framework/artifact-schemas/implementation-plan.schema.md §3.5`, `algedonic-protocol.md`, `clarification-protocol.md`

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
| Gap Analysis Matrix (`GAM`) | SwA | **Baselined** (v1.0.0+) | Self-produced in Phase E; must be fully baselined |
| Implementation Candidate Catalog (`ICC`) | SwA | **Baselined** (v1.0.0+) | Self-produced in Phase E; all IC-nnn entries required |
| Technology Architecture (`TA`) | SwA | **Baselined** (v1.0.0+) | Self-produced in Phase D; required for environment provisioning requirements |
| Work Package Catalog (`WPC`) | Project Manager | Draft acceptable | PM's Phase E output; SwA reviews for technical feasibility |
| Risk Register | Project Manager | Draft | PM's Phase E output; SwA reviews for technical accuracy |
| Architecture Roadmap draft | Project Manager | Draft | PM's Phase E output; SwA provides technology sequencing refinements |
| Implementation Plan (`IP`) — Phase F additions | Project Manager | PM initiates; SwA contributes | PM owns the IP; SwA contributes sequencing, transition architectures, and feasibility review |
| Sprint kickoff event | PM | `sprint.started` emitted | Do not begin work before PM emits this event |

**RACI note:** SwA is **●** (accountable) for Transition Architecture Diagrams. PM is **●** for the Implementation Plan, Architecture Roadmap final, and Dependency Matrix. SwA contributes technical content to the IP and Roadmap but does not own them.

---

## Knowledge Adequacy Check

### Required Knowledge

- Complete Gap Analysis Matrix from Phase E — all GAP-nnn entries with domain, ABBs affected, and priority
- Complete Implementation Candidate Catalog — all IC-nnn entries with dependencies and complexity
- PM's Work Package Catalog — work package definitions, responsible agents, acceptance criteria, and current dependency ordering
- Technology Architecture — Deployment Topology (Phase D §3.5) is the basis for environment provisioning requirements
- Technology Lifecycle Analysis (Phase D §3.8) — legacy component phase-out dates inform transition timing

### Known Unknowns

The following gaps are predictably present at Phase F entry:

1. **DevOps capacity for environment provisioning**: The timeline for environment provisioning is constrained by DevOps/Platform Engineer capacity and infrastructure lead times. These are not known to the SwA; they require PM coordination with DevOps.
2. **PM's internal sprint capacity model**: How many work packages fit into a single Solution Sprint is a PM decision based on agent capacity, not purely a technical dependency question. SwA cannot determine optimal sprint decomposition unilaterally.
3. **Data migration complexity**: If baseline data must be migrated as part of a transition, the volume, transformation complexity, and rollback risk are often unknown until data profiling is performed. SwA flags this as a risk; resolution may require a dedicated data migration IC.

### Clarification Triggers

Raise a CQ (`target: User`) if:
- A transition architecture plateau state would require a period where both baseline and target versions of a component are running simultaneously (dual-run) and it is not known whether the operational environment supports this
- Regulatory or compliance constraints require a specific ordering of delivery (e.g., security controls must be in place before any user data processing begins) and those constraints are not captured in the SCO

Route structured feedback to PM (`target: Project Manager`) if:
- The PM's Work Package Catalog dependency ordering is technically infeasible (see Step 4)
- The PM's Implementation Plan assigns a work package to a sprint before its technical prerequisites are available

Route structured feedback to SA (`target: Solution Architect`) if:
- The Transition Architecture requires an intermediate state that is inconsistent with a baselined AA decision (e.g., an intermediate state requires a component that AA has designated as "retiring")

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="F", artifact_type="implementation-plan")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 1 — Produce Transition Architecture Diagrams

1.1 Determine whether Transition Architecture Diagrams are required. They are required if any of the following apply:
- The Gap Analysis Matrix contains ≥3 High-priority gaps that cannot be simultaneously closed in a single delivery wave
- The Work Package Catalog contains work packages with dependency chains longer than 2 levels
- The Technology Lifecycle Analysis identifies components requiring phase-out that create migration risk
- A live system is being modified and must remain operational during delivery (zero-downtime migration required)

1.2 If not required: document the rationale ("single-wave delivery; no intermediate transition states required") and proceed to Step 2. Emit a brief consulting note to PM.

1.3 If required: define intermediate "plateau" architecture states — each plateau is a stable, deployable state of the architecture between baseline and target.

1.4 For each plateau state (TR-000 Baseline → TR-001 → ... → TR-nnn Target), produce an ArchiMate **Implementation and Migration Viewpoint** diagram showing:
- Technology components present in this plateau
- Application components active in this plateau
- Components being introduced (entering this plateau)
- Components being retired (absent from next plateau)
- Data migration or dual-run requirements at this transition point
- Environment changes required to reach this plateau (for DevOps)

1.5 Each Transition Architecture Diagram must include:
- A header identifying the plateau ID, name, and description
- An entry condition: what must be completed before this plateau is reached
- An exit condition: what must be validated before the next plateau begins
- Risk notes: what could prevent or complicate this transition

1.6 Baseline Transition Architecture Diagrams at `technology-repository/transition-architecture/TA-transitions-<nnn>-1.0.0.md`. Emit `artifact.baselined`.

**Revisit handling:** If Phase F is revisited (`phase_visit_count > 1`), assess whether the triggering change (from `phase.return-triggered` event) affects any plateau definitions. Update only affected plateaus; increment version.

### Step 2 — Provide Technical Sequencing Input to PM for Implementation Plan

2.1 Read the PM's Work Package Catalog and current Implementation Plan draft.

2.2 Produce a **Technical Sequencing Analysis** — a structured input document for PM consumption covering:

**2.2.1 Technical Dependency Ordering**: For each pair of Work Packages where a technical dependency exists, state the dependency explicitly:
- `WP-nnn MUST complete before WP-mmm can begin` (hard dependency: WP-mmm's technology cannot function without WP-nnn)
- `WP-nnn SHOULD complete before WP-mmm` (soft dependency: WP-mmm is significantly harder without WP-nnn but could proceed with workarounds)

**2.2.2 Parallel Track Identification**: Identify work packages that have no technical dependency relationships and can be assigned to parallel tracks within the same Solution Sprint or concurrent sprints.

**2.2.3 Critical Path**: Identify the longest dependency chain — the critical path through work packages from the first deliverable to the last. Highlight which work packages are on the critical path; delays here delay the entire delivery.

**2.2.4 Infrastructure Prerequisites**: Identify which technology components (TC-nnn) must be provisioned before any application work package can begin. These become the first environment provisioning work packages for DevOps.

2.3 Deliver the Technical Sequencing Analysis to PM via handoff event.

### Step 3 — Contribute Technology Section to Architecture Roadmap

3.1 PM owns the Architecture Roadmap final. SwA contributes the technology adoption sequencing section:

**3.1.1 Technology adoption sequence**: List TC-nnn components in the order they must be introduced, with the work package that introduces each. For each introduction, note:
- Plateau state in which it first appears
- Any dependency on a preceding TC-nnn being operational
- Whether it replaces a baseline component (and the phase-out target for the replaced component)

**3.1.2 Legacy phase-out schedule**: From the Technology Lifecycle Analysis (TA §3.8), identify all components with end-of-support dates or planned retirement. Record their phase-out work package and target plateau.

**3.1.3 Technology risk milestones**: Flag any points in the roadmap where a High-lifecycle-risk component is still active, and the milestone at which that risk is resolved (by upgrade or replacement).

3.2 Deliver the technology section contribution to PM via handoff event (not direct write to PM's roadmap — PM integrates).

### Step 4 — Technical Feasibility Review of PM's Implementation Plan

4.1 When PM produces the Implementation Plan draft (incorporating SwA's sequencing input and Work Package Catalog), perform a technical feasibility review. This is a mandatory step before F→G gate.

4.2 Feasibility review criteria:
- [ ] No work package begins before all its stated technology prerequisites are available (TC-nnn in provisioned environment)
- [ ] No work package requires a component that is not in the Technology Component Catalog and has no IC-nnn candidate
- [ ] The Dependency Matrix is acyclic (no circular work package dependencies)
- [ ] Solution Sprint boundaries do not split a technically inseparable work unit across sprints
- [ ] Environment provisioning work packages are sequenced before the application work packages that depend on them
- [ ] Data migration work packages are sequenced correctly relative to application feature work packages

4.3 For each feasibility issue found: raise structured feedback to PM specifying:
- Which WP-nnn entry has the infeasibility
- The specific technical reason it is infeasible
- The correction required (re-sequencing, splitting, or merging)

4.4 If PM's iteration-2 revision still contains a technically infeasible sequence: raise ALG-010 (S3) immediately. Provide a clear written statement of the infeasibility. Do NOT cast an approved gate vote at F→G while a known infeasibility exists in the IP.

### Step 5 — Environment Provisioning Requirements for DevOps

5.1 Produce an Environment Provisioning Requirements input for DevOps. This is not the Environment Provisioning Catalog (DevOps ●) — it is SwA's technical input describing what each environment requires.

5.2 For each deployment environment (Production, Staging, Development — minimum):
- List which TC-nnn components must be present
- State the required version constraint for each component
- Note any configuration differences from other environments (e.g., different replica counts, different storage sizing)
- Identify network connectivity requirements (what must be reachable from each environment)
- Note any licensing or access constraints (e.g., Production credentials must be managed separately)

5.3 Deliver to DevOps via handoff event. Record `handoff.created` in EventStore.

### Step 6 — Baseline Transition Architecture Diagrams and Cast Gate Vote

6.1 Confirm Transition Architecture Diagrams are complete (Step 1) and consistent with the PM's finalised Work Package Catalog and Architecture Roadmap.

6.2 Confirm Technical Feasibility Review (Step 4) is complete and any issues are resolved.

6.3 Confirm Environment Provisioning Requirements are delivered to DevOps (Step 5).

6.4 Run quality gate self-check:
- [ ] All Transition Architecture Diagrams (if required) are baselined at 1.0.0
- [ ] Each plateau has entry and exit conditions documented
- [ ] Technical Sequencing Analysis delivered to PM
- [ ] Technical Feasibility Review complete; all issues resolved or documented as accepted risks
- [ ] Environment Provisioning Requirements delivered to DevOps
- [ ] No blocking CQs open on any Phase F artifact

6.5 Cast gate vote for F→G: emit `gate.vote_cast` with `gate: F-G`, `vote: approved` (or `vote: blocked` with specific blocking condition).

---

## Feedback Loop

### IP Technical Feasibility Loop (SwA ↔ PM)

**Purpose:** Ensure the PM's Implementation Plan is technically executable.

- **Iteration 1**: SwA raises structured feedback specifying all infeasible sequences or missing prerequisites in the IP. PM revises and re-issues.
- **Iteration 2**: SwA re-reviews; confirms feasibility or raises remaining issues.
- **Termination**: All technical feasibility issues resolved; SwA can cast approved gate vote.
- **Maximum iterations**: 2. If PM's iteration-2 revision still contains technically infeasible sequencing, SwA escalates to ALG-010 (S3) with a written infeasibility statement. SwA cannot cast an approved F→G gate vote with known infeasibilities.
- **Escalation path**: ALG-010 → PM adjudicates; if the infeasibility traces to a scope issue requiring user input, PM batches as a CQ; if the infeasibility is unresolvable within current scope, ALG-005 (TC — S2) → PM reassesses scope.

### Transition Architecture Consistency Loop (SwA ↔ SA)

**Purpose:** Ensure Transition Architecture plateaus are consistent with baselined AA decisions.

- **Iteration 1**: SwA shares Transition Architecture draft with SA via handoff; SA reviews for AA consistency. SwA integrates feedback.
- **Termination**: SA confirms no AA inconsistencies in transition states.
- **Maximum iterations**: 1 (SA consulting review; not a gating approval). If SA identifies a fundamental AA inconsistency that cannot be resolved without revising the AA, escalate to PM as a potential Phase C/D revisit via `phase.return-triggered`.
- **Escalation**: If AA revision is required, PM records `phase.return-triggered` referencing the affected AA artifact. Do not baseline Transition Architecture Diagrams until the AA inconsistency is resolved.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="implementation-plan"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-005 | Phase F gate has required two consecutive extensions due to unresolvable IP feasibility disagreement with PM | S2 | Emit to PM for scope reassessment; document feasibility statement |
| ALG-006 | A dependency chain in the Work Package Catalog creates a scheduling deadlock where no work package can begin without another being complete | S2 | Emit to PM; provide analysis of the circular dependency chain; restructured sprint plan required |
| ALG-008 | GAM or ICC input to Phase F are in draft state (v0.x.x) being used as authoritative inputs | S2 | Emit to PM; halt Transition Architecture production; baseline inputs required |
| ALG-010 | PM feasibility review loop exhausted (two iterations) without agreement on technically feasible sequencing | S3 | Emit to PM for adjudication; provide written infeasibility statement; do not cast approved F→G gate vote |
| ALG-014 | A safety-critical change request arrives during Phase F sprint (before F→G gate) | S1 | Halt affected work packages; emit to PM; do not proceed with affected Transition Architecture sections until change impact assessed by CSCO |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Transition Architecture Diagrams | `technology-repository/transition-architecture/TA-transitions-<nnn>-1.0.0.md` | 1.0.0 | `artifact.baselined` |
| Technical Sequencing Analysis (input to IP) | Delivered to PM via handoff | — | `handoff.created` |
| Technology section contribution to Architecture Roadmap | Delivered to PM via handoff | — | `handoff.created` |
| Environment Provisioning Requirements (input to DevOps) | Delivered to DevOps via handoff | — | `handoff.created` |
| Technical Feasibility Review result | Structured feedback to PM (in handoff-log) | — | — |
| F→G Gate vote | EventStore | — | `gate.vote_cast` |

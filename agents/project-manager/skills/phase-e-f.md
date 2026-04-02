---
skill-id: PM-PHASE-EF
agent: PM
name: phase-e-f
display-name: Phase E/F — Opportunities, Solutions and Migration Planning
invoke-when: >
  Phase D gate has passed; PM is accountable for Work Package Catalog, Risk Register, and
  Architecture Roadmap in Phase E, and for the Implementation Plan in Phase F.
trigger-phases: [E, F]
trigger-conditions:
  - gate.evaluated (from_phase=D, result=passed)
  - sprint.started (phase=E)
  - sprint.started (phase=F)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F]
primary-outputs: [Work Package Catalog, Risk Register, Architecture Roadmap, Implementation Plan, Solution Sprint Plan]
version: 1.0.0
---

# Skill: Phase E/F — Opportunities, Solutions & Migration Planning

**Agent:** Project Manager  
**Version:** 1.0.0  
**Phases:** E — Opportunities & Solutions; F — Migration Planning  
**Skill Type:** Phase ownership (PM is accountable for E/F primary artifacts)  
**Framework References:** `agile-adm-cadence.md §6.5–6.6`, `raci-matrix.md §3.7–3.8`, `framework/artifact-schemas/implementation-plan.schema.md`

---

## Inputs Required

- Baselined Technology Architecture (`TA`) from SwA — version 1.0.0+
- Gap Analysis Matrix from SwA — baselined
- Baselined Application Architecture (`AA`) and Data Architecture (`DA`) from SA
- Initial Test Strategy from QA — baselined
- Safety Constraint Overlay (`SCO`) from CSCO — current version
- Requirements Register (`RR`) from PO — current version
- Environment Provisioning Catalog from DevOps — Phase F input

---

## Knowledge Adequacy Check

**Domain knowledge required:**
- Work Package decomposition principles: each work package corresponds to one or more ABBs that can be implemented independently within a Solution Sprint
- Architecture Roadmap sequencing: packages are sequenced by dependency (what must exist before what), by risk (highest-risk first where feasible), and by business value
- Migration planning: for engagements with existing systems, transition architectures describe intermediate states between current and target

**CQ triggers:**
- If the Gap Analysis Matrix contains gaps that cannot be mapped to work packages without architecture clarification → raise CQ to SwA before completing Work Package Catalog.
- If the DevOps environment provisioning timeline is unknown → raise CQ to DevOps before finalising the Implementation Plan schedule.
- If a risk item in the Risk Register lacks a mitigation strategy → raise CQ to the relevant producing agent.

---

## Phase E: Opportunities & Solutions

### E.1 Own: Work Package Catalog

The PM produces the Work Package Catalog from SwA's Gap Analysis Matrix and SA's architecture artifacts.

**Work Package Catalog structure** (written to `project-repository/work-package-catalog/wpc-<version>.md`):
```markdown
| WP-ID | Work Package Name | Implementing ABBs | Dependencies | Implementing Agent(s) | Authorising Artifact |
|---|---|---|---|---|---|
| WP-001 | [name] | [ABB-ids] | [WP-ids this depends on] | DE + DevOps | AA v1.x.x, TA v1.x.x |
```

Rules for work packages:
- Every work package must map to at least one ABB from AA, DA, or TA.
- Every work package must have an authorising artifact (the architecture artifact that specifies it).
- Work packages may not span ABBs that are owned by different consuming roles without explicit coordination.
- A work package is not a sprint — it is a decomposition unit that will be scheduled into one or more Solution Sprints in Phase F.

### E.2 Own: Risk Register

The PM owns the Risk Register (populated with inputs from SA, SwA, CSCO, DevOps).

**Risk Register structure** (`project-repository/risk-register/rr-<version>.md`):
```markdown
| RISK-ID | Description | Probability | Impact | Owner | Mitigation | CSCO Sign-off Required |
|---|---|---|---|---|---|---|
```

Risk identification inputs:
- SA: architecture risks (unmapped capabilities, unresolved ADRs)
- SwA: technology risks (immature dependencies, scaling unknowns)
- CSCO: safety and compliance risks
- DevOps: infrastructure and deployment risks

PM synthesises these into a consolidated register. CSCO must review the Risk Register before Phase E gate (G authority per RACI §3.7).

### E.3 Own: Architecture Roadmap Draft

Initial Architecture Roadmap sequences work packages into a logical delivery order. Written to `project-repository/architecture-roadmap/ar-draft-<version>.md`.

Roadmap sequencing criteria:
1. Mandatory dependencies (WP-B cannot begin until WP-A is deployed).
2. Safety-critical components first within a dependency-independent set.
3. Highest-business-value items earliest where technically feasible.
4. DevOps infrastructure work precedes all application delivery.

### E.4 Phase E Gate

**Pre-gate checklist:**
1. Work Package Catalog baselined (PM accountable).
2. Risk Register baselined with CSCO review (CSCO G authority).
3. Architecture Roadmap draft present.
4. Implementation Candidate Catalog baselined by SwA.
5. Initial Test Strategy baselined by QA.
6. All G-holder votes cast: SwA (G), CSCO (G).

---

## Phase F: Migration Planning

### F.1 Own: Implementation Plan

The Implementation Plan is the PM's primary Phase F artifact. It translates the Architecture Roadmap and Work Package Catalog into a concrete Solution Sprint plan.

Written to `project-repository/implementation-plan/ip-<version>.md`. Schema: `framework/artifact-schemas/implementation-plan.schema.md`.

**Implementation Plan sections:**
1. **Sprint Plan** — list of Solution Sprints, each with: sprint-id, work packages in scope, input artifacts required, participants, exit criteria.
2. **Architecture Contract references** — each sprint must be authorised by an Architecture Contract (SwA produces these in Phase G setup).
3. **Environment provisioning schedule** — DevOps provisioning steps and their sprint dependencies.
4. **Test execution plan** — QA test phases aligned to Solution Sprints.
5. **Dependency matrix** — cross-sprint dependencies; identifies which sprints can run concurrently.
6. **Risk mitigation schedule** — when each risk mitigation action is performed relative to sprints.

**Rule:** The Implementation Plan does not specify how features are implemented. It specifies what ABBs are authorised for implementation, in what order, by whom, and under what governance conditions.

### F.2 Own: Architecture Roadmap (Final)

Finalise the Architecture Roadmap draft incorporating Phase F sequencing decisions. PM adds:
- Transition architecture milestones (if applicable)
- Deployment milestone sequence
- Feedback cycle points (where Phase G governance outputs will trigger Phase H reviews)

### F.3 Own: Solution Sprint Plan

The Solution Sprint Plan is the operational companion to the Implementation Plan. It describes the mechanics of running each Solution Sprint: kickoff checklist, exit criteria, escalation paths.

Written as a standing operating procedure in `project-repository/sprint-log/solution-sprint-plan.md`.

### F.4 Phase F Gate

**Pre-gate checklist:**
1. Implementation Plan baselined (PM accountable).
2. Architecture Roadmap final baselined (PM accountable).
3. Dependency Matrix present and consistent with Implementation Plan.
4. Environment Provisioning Catalog baselined by DevOps.
5. Transition Architecture Diagrams baselined by SwA (if applicable).
6. Solution Sprint Plan present.
7. G-holder votes cast: SwA (G), CSCO (G).

---

## Feedback Loop

**Work Package Catalog feedback:**
- Iteration 1: PM shares draft WPC with SwA and SA for consistency check.
- Iteration 2: PM incorporates feedback; re-shares if major structural changes.
- Termination: Both SA and SwA confirm WPC is consistent with their artifacts.
- Max iterations: 2. Unresolved inconsistency → PM adjudicates (if architectural) or escalates to SA.

**Implementation Plan feedback:**
- Iteration 1: PM shares draft IP with SwA, DevOps, and QA for feasibility check.
- Iteration 2: PM revises; final review.
- Termination: SwA confirms architectural sequencing is correct; DevOps confirms environment plan is feasible; QA confirms test plan is executable.
- Max iterations: 2. Escalation: ALG-010 if deadlock.

---

## Algedonic Triggers

| ID | Condition | Action |
|---|---|---|
| ALG-005 | Phase E or F gate requires 2+ extensions without passing | Escalate to user; assess whether scope reduction is required |
| ALG-006 | Dependency between work packages cannot be resolved within the current sprint | PM restructures Implementation Plan; notify affected agents |
| ALG-010 | Feedback loop on WPC or IP exhausted without resolution | PM adjudicates; records decision |

---

## Outputs

| Output | Path | Trigger |
|---|---|---|
| Work Package Catalog | `project-repository/work-package-catalog/wpc-<v>.md` | Phase E |
| Risk Register | `project-repository/risk-register/risk-<v>.md` | Phase E |
| Architecture Roadmap draft | `project-repository/architecture-roadmap/ar-draft-<v>.md` | Phase E |
| Phase E Gate Record | `project-repository/decision-log/gate-E-F.md` | Phase E gate |
| Implementation Plan | `project-repository/implementation-plan/ip-<v>.md` | Phase F |
| Architecture Roadmap final | `project-repository/architecture-roadmap/ar-final-<v>.md` | Phase F |
| Solution Sprint Plan | `project-repository/sprint-log/solution-sprint-plan.md` | Phase F |
| Phase F Gate Record | `project-repository/decision-log/gate-F-G.md` | Phase F gate |

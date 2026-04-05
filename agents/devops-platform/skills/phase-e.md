---
skill-id: DO-PHASE-E
agent: DO
name: phase-e
display-name: Phase E — Delivery Complexity Assessment
invoke-when: >
  Phase E Architecture Sprint starts and SwA has issued the Gap Analysis Matrix and
  Implementation Candidate Catalog; DO assesses deployment complexity and identifies
  critical-path infrastructure candidates.
trigger-phases: [E]
trigger-conditions:
  - sprint.started (phase=E)
  - handoff.created (handoff-type=gap-analysis-matrix, to=devops-platform)
entry-points: [EP-0, EP-D, EP-E, EP-G]
primary-outputs: [Phase E Delivery Complexity Assessment, Delivery Complexity Estimate summary, EPC draft v0.2.0]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase E — Opportunities and Solutions (Delivery Complexity Assessment)

**Agent:** DevOps / Platform Engineer  
**Version:** 1.0.0  
**Phase:** E — Opportunities & Solutions  
**Skill Type:** Phase contributing — deployment complexity estimation and pipeline requirements  
**Framework References:** `agile-adm-cadence.md §6.6`, `raci-matrix.md §3.7`, `clarification-protocol.md`, `algedonic-protocol.md`, `repository-conventions.md §6`

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
| Gap Analysis Matrix | Software Architect/PE (handoff) | Version 0.1.0 or higher | Read-only. DO uses gap analysis to understand what infrastructure is being changed or introduced |
| Implementation Candidate Catalog | Software Architect/PE (handoff) | Draft acceptable | Contains the list of implementation candidates (ABBs → SBBs) that must be assessed for deployment complexity |
| Technology Architecture (`TA`) | Software Architect/PE | Baselined (version ≥ 1.0.0); Phase D gate passed | The TA is the DO's authoritative reference for what technology components exist; must be baselined before EPC sections can advance |
| Architecture Roadmap draft | Project Manager | Draft acceptable | DO reads roadmap to understand candidate sequencing; contributes delivery complexity data that affects sequencing |
| Initial EPC draft | DO (self-produced in Phase D) | Version 0.1.x | DO uses the Phase D EPC draft as the starting point for Phase E complexity assessments |
| `sprint.started` event | Project Manager | Must be emitted for Architecture Sprint E before DO begins work | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- The implementation candidates listed in the Implementation Candidate Catalog: what SBBs are being introduced, modified, or retired; which are net-new infrastructure vs. replacements.
- The technology gaps identified in the Gap Analysis Matrix: what infrastructure capabilities are missing today and must be provisioned as part of implementation.
- The Technology Architecture's deployment topology: which environments each candidate component must be deployed to; what isolation and access requirements apply.
- Standard deployment complexity patterns for the selected technology components: e.g., managed database provisioning has lower complexity than self-hosted cluster migration; serverless function deployment has different pipeline requirements than containerised services.

### Known Unknowns

The following are predictably unknown at Phase E entry and may require CQs:

| Unknown | Blocking | CQ Target | Impact |
|---|---|---|---|
| Deployment sequencing constraints not expressed in the Gap Analysis (e.g., database migration must precede application deployment) | No — DO documents as a dependency; PM incorporates into Dependency Matrix | PM | Work Package Catalog effort estimates may be underestimated without this |
| Volume of data to be migrated (for stateful component replacements) | No — DO flags as a sizing uncertainty; PM accepts risk or raises CQ | User (via PM) | Migration duration estimate carries high uncertainty without this |
| Whether the target project repository has existing CI/CD infrastructure that must be migrated rather than replaced | No — DO flags as assumption; preference is to validate before Phase F | User (via PM) | Pipeline design complexity estimate affected |

### Clarification Triggers

DO raises a CQ when:

1. **Implementation Candidate Catalog includes a candidate whose deployment model is undefined** — neither cloud-managed nor self-hosted is specified, and the choice materially affects pipeline complexity estimate. DO raises to PM (routing to SwA) as an artifact ambiguity per `clarification-protocol.md §4`.
2. **A stateful data migration is implied by the Gap Analysis but the data volume and migration procedure are not characterised** — DO cannot provide a meaningful complexity estimate for stateful migration candidates. Non-blocking CQ to PM; DO provides a range estimate with explicit uncertainty caveat.
3. **Build/buy/reuse decision for an infrastructure candidate is not reflected in the Gap Analysis** — e.g., a managed service is in scope but no ADR records whether it is procured or built. DO raises to SwA for clarification before completing pipeline requirement assessment for that candidate.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="DO", phase="E", artifact_type="implementation-plan")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 1 — Review implementation candidates for deployment complexity

For each candidate in the Implementation Candidate Catalog, classify deployment complexity on the following scale:

| Complexity Level | Definition | Examples |
|---|---|---|
| **Low** | Can be provisioned by a standard IaC module with no custom automation; pipeline configuration is a minor extension of an existing pattern | Adding a managed cache service; adding a static asset CDN |
| **Medium** | Requires custom IaC authoring or pipeline extension; no complex data migration; environment provisioning is non-trivial but tractable in a single sprint | New containerised microservice with its own database schema; replacing a managed service with a same-family alternative |
| **High** | Requires multi-sprint provisioning effort, complex data migration, cross-environment orchestration, or significant pipeline redesign | Migrating from self-hosted to managed database with live data; introducing a new observability platform alongside an existing one during cutover; multi-region active-passive failover topology |
| **Critical-path** | Candidate is on the delivery critical path; its provisioning must be complete before any other Solution Sprint work can proceed | Environment baseline provisioning; CI/CD pipeline foundation; identity and access management foundation |

Record complexity assessments in `devops-repository/phase-e-assessment/phase-e-delivery-complexity-<sprint-id>.md`.

### Step 2 — Assess build/buy/reuse from a delivery operations perspective

For each implementation candidate where a build/buy/reuse decision is in scope (recorded in the Implementation Candidate Catalog or Gap Analysis):

- **Managed service (buy/reuse):** Lower IaC complexity; less pipeline configuration; operational burden shifts to provider; DO preference in most cases where feature equivalence is adequate.
- **Self-hosted (build):** Higher IaC complexity; requires patching and upgrade pipeline stages; requires backup and recovery automation; may be necessary for regulatory, cost, or feature reasons — record the driver.
- **Reuse existing:** DO assesses existing infrastructure for compatibility with the TA requirements; records gaps as Medium or High complexity items requiring migration work.

Record the delivery-operations perspective on each build/buy/reuse option in the Phase E assessment document. This is advisory input to SwA (accountable for the Implementation Candidate Catalog) — the DO does not override build/buy/reuse decisions, but provides the operational complexity data that should inform them.

### Step 3 — Identify infrastructure candidates

The Implementation Candidate Catalog produced by SwA focuses on application-layer SBBs. Corresponding infrastructure candidates must also be identified:

For each application-layer implementation candidate, identify the corresponding infrastructure candidates:

| Application Candidate | Corresponding Infrastructure Candidate | Provisioning Dependency |
|---|---|---|
| e.g., API Gateway application component | e.g., Cloud API Gateway managed service (TC-nnn from TA) | Must exist before application deployment |
| e.g., User authentication service | e.g., Identity Provider (TC-nnn from TA) + secrets manager integration | Must exist before first Solution Sprint |

Record the infrastructure candidate list in the Phase E assessment document. These infrastructure candidates inform the critical-path ordering in the Implementation Plan and the Solution Sprint Plan.

**Important:** Infrastructure candidates that are classified as Critical-path must be flagged to PM explicitly — they constrain the opening of the first Solution Sprint.

### Step 4 — Provide deployment complexity estimates to PM

Produce a Delivery Complexity Estimate summary for PM's use in authoring the Work Package Catalog (`project-repository/work-package-catalog/`). The summary is structured as DO's contribution to PM's artifact — it is advisory input, not a DO-owned deliverable.

Format:

```markdown
## Delivery Complexity Estimates — Phase E Input to PM

Sprint: <sprint-id>

| Candidate ID | Candidate Name | Complexity Level | Estimated Effort (sprint-fractions) | Dependencies | Notes |
|---|---|---|---|---|---|
| CAND-nnn | | Low / Medium / High / Critical-path | e.g., 0.5 sprint / 1 sprint / 2+ sprints | CAND-nnn must precede | |

### Critical-Path Infrastructure Candidates
The following infrastructure candidates must be provisioned before Solution Sprint SS-1 can begin:
[list]

### Assumptions
[List all assumptions made in producing these estimates; flag which require CQ resolution]
```

Deliver this summary to PM via a handoff event (`handoff.issued` to PM).

### Step 5 — Identify pipeline and automation requirements per implementation candidate

For each implementation candidate, record the CI/CD pipeline and automation requirements that the candidate introduces:

- **New pipeline stages required:** e.g., additional integration test stage for a new service, database migration validation stage, blue/green deployment orchestration.
- **New automation tooling required:** e.g., infrastructure drift detection, secret rotation automation, certificate renewal.
- **Changes to existing pipeline stages:** e.g., expanded dependency scan scope, additional SAST rulesets for a new language runtime.

These requirements are preliminary inputs to the Phase F pipeline design. Record them in the Phase E assessment document for forward-traceability.

### Step 6 — Update EPC draft with Phase E findings

Incorporate Phase E findings into the EPC draft:

1. Add or refine environment definitions based on implementation candidate deployment topology requirements.
2. Mark infrastructure candidates on the critical path as environment readiness prerequisites.
3. Note any environment parity deviations that implementation candidates introduce or require.
4. Increment EPC draft version to 0.2.0.

Emit `artifact.drafted` for the EPC version increment.

---

## Feedback Loop

**Phase E DO-PM feedback loop:**

The DO provides deployment complexity estimates to PM; PM incorporates them into the Work Package Catalog. This is a one-directional contribution loop; PM may request clarification on specific estimates.

- **Iteration 1:** DO delivers Phase E assessment document and complexity estimates. PM reviews and may raise specific questions about complexity assessments or dependency sequencing.
- **Iteration 2 (if needed):** DO clarifies or revises specific estimates based on PM's questions; provides rationale for High or Critical-path classifications.
- **Termination:** Loop terminates when PM has incorporated DO's estimates into the Work Package Catalog and the Implementation Candidate Catalog's deployment complexity column is complete.
- **Max iterations:** 2 before PM proceeds with documented uncertainty.
- **Escalation:** If a complexity estimate cannot be resolved because of missing information (e.g., data migration volume unknown, deployment model undefined), PM records the uncertainty in the Work Package Catalog and raises a CQ to the user if the uncertainty is material to sprint planning. DO does not escalate directly; PM owns the Work Package Catalog and the risk register.

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

| ID | Condition | Category | Severity | Action |
|---|---|---|---|---|
| ALG-008 | DO is given a draft TA (version 0.x.x) as the basis for Phase E delivery complexity estimates | GV | S2 | Flag to PM; note that all estimates carry elevated uncertainty; do not treat estimates as binding until TA is baselined |
| ALG-006 | A Critical-path infrastructure candidate has a dependency that cannot be resolved within the Phase F sprint (e.g., procurement approval required before cloud account creation is possible) | TC | S2 | Raise to PM immediately; flag as a dependency that may collapse the planned Solution Sprint start date; PM restructures sprint plan or escalates procurement issue |
| ALG-010 | DO and SwA disagree on the build/buy/reuse classification of an infrastructure candidate such that the disagreement cannot be resolved within the Phase E sprint | IA | S3 | Raise to PM for adjudication; DO records its operational complexity assessment; SwA records its architecture reasoning; PM applies RACI (SwA accountable for Implementation Candidate Catalog; DO's operational input is binding) |
| ALG-011 | Implementation Candidate Catalog contains candidates whose technology components are not present in the baselined TA Technology Component Catalog | IA | S3 | Raise to SwA (producing agent): candidates cannot be assessed for delivery complexity without corresponding TA technology components; SwA must either add the components (TA revision) or correct the candidate catalog |

---

## Outputs

| Output | Path | Event | Notes |
|---|---|---|---|
| Phase E Delivery Complexity Assessment | `devops-repository/phase-e-assessment/phase-e-delivery-complexity-<sprint-id>.md` | `artifact.drafted` | Internal DO artifact; informs PM's Work Package Catalog |
| Delivery Complexity Estimate summary (input to PM) | Delivered via `handoff.issued` to PM | `handoff.issued` | PM consumes; DO does not write to project-repository directly |
| EPC draft v0.2.0 | `devops-repository/environment-catalog/epc-0.2.0.md` | `artifact.drafted` | Incremented with Phase E findings; still not baselined |

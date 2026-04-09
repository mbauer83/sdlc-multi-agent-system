---
skill-id: DO-PHASE-D
agent: DO
name: phase-d
display-name: Phase D — Technology Architecture Consulting
invoke-when: >
  SwA issues a handoff of the TA draft to DevOps for operational feasibility review during
  Phase D; DO assesses infrastructure feasibility and produces Phase D Feedback Record.
trigger-phases: [D]
trigger-conditions:
  - handoff.created (handoff-type=ta-feasibility-review, to=devops-platform)
  - sprint.started (phase=D)
entry-points: [EP-0, EP-D, EP-G]
primary-outputs: [Phase D Feedback Record, Initial Environment Provisioning Catalog draft]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase D — Technology Architecture Consulting

**Agent:** DevOps / Platform Engineer  
**Version:** 1.0.0  
**Phase:** D — Technology Architecture  
**Skill Type:** Phase consulting — feasibility review and structured feedback  
**Framework References:** `agile-adm-cadence.md §6.5`, `raci-matrix.md §3.6`, `framework/artifact-schemas/technology-architecture.schema.md`, `clarification-protocol.md`, `algedonic-protocol.md`, `repository-conventions.md §6`

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Technology Architecture draft (`TA`) | Software Architect/PE (handoff) | Version 0.1.0 or higher; `handoff.issued` event received | Blocking — DO cannot begin feasibility review without a TA draft. The DO acknowledges receipt with `handoff.acknowledged` and `retrieval_intent: full`. |
| Technology Component Catalog (within TA) | Software Architect/PE (part of TA) | Populated with candidate technology components; ADRs referenced | The DO must be able to assess each component for operational feasibility |
| Infrastructure Diagram (within TA) | Software Architect/PE (part of TA) | At least a draft ArchiMate Technology Viewpoint showing deployment zones | Required for environment parity and topology realism assessment |
| Architecture Principles Register (`PR`) | Solution Architect | Baselined (version ≥ 1.0.0) | Read-only. DO uses PR to identify any operational standards already enshrined as principles |
| Safety Constraint Overlay (`SCO`) — Phase C update | CSCO | Baselined | DO must understand security and safety constraints that affect technology choices and observability requirements |
| Existing infrastructure documentation (EP-D, EP-G entries) | User (via PM handoff) | Any format; may be absent | If present, the DO cross-references against TA draft; absence is not blocking |
| `sprint.started` event | Project Manager | Must be emitted for the Architecture Sprint D before DO begins work | Hard prerequisite — no work begins without this event |

---

## Knowledge Adequacy Check

### Required Knowledge

- The technology components nominated by SwA: what they are, how they are typically provisioned (cloud-managed, self-hosted, containerised, serverless), and what operational complexity they carry.
- The deployment environments described in the TA Deployment Topology: Production, Staging, Development, and CI — their isolation requirements, access control models, and expected resource consumption.
- The observability stack components in the TA Technology Component Catalog: whether metrics, logging, tracing, and alerting are present; whether they are coherent as a stack (e.g., not missing correlation between logs and traces).
- The cloud provider or on-premises platform selected: whether it is within known supportable infrastructure patterns; whether agreements (contracts, procurement approvals) are required.
- Any regulatory or compliance constraints from the SCO that affect technology choice (e.g., data residency requirements restricting cloud region, FedRAMP requirements restricting cloud provider).

### Known Unknowns

The following are predictably unknown at Phase D entry and require CQs before the DO can complete relevant EPC sections:

| Unknown | Blocking | CQ Target | EPC Section Affected |
|---|---|---|---|
| Existing cloud account or infrastructure provider agreements | No — DO can flag risk in Phase D feedback; EPC notes dependency | User (via PM) | EPC environment definitions (provider accounts, billing, access) |
| Current CI/CD tooling in the target project (if EP-D or EP-G) | No — DO assesses what exists vs. what TA requires | User (via PM) | EPC pipeline design; pipeline migration plan |
| Network topology constraints (VPC/VNet limits, IP ranges, peering requirements) | No for Phase D feedback; yes for EPC network topology section | User (via PM) | EPC network topology per environment |
| Access control authority (who manages identity provider, secrets manager) | No for Phase D; yes before Phase G provisioning | User (via PM) | EPC access control model |
| Operational SLA targets (availability, RTO, RPO) | No — DO can flag absence as a gap; EPC notes as TBD | User (via PM) | EPC monitoring thresholds, runbook requirements |

### Clarification Triggers

DO raises a CQ when:

1. **Cloud provider or platform selected in TA is not within known infrastructure patterns** and the DO cannot assess operational feasibility without additional context. Blocking for Phase D feedback §3.3; non-blocking for other sections.
2. **Observability stack is absent from the TA Technology Component Catalog** — no metrics, logging, or alerting components listed. DO raises a structured feedback item to SwA (not a user CQ) flagging this as a required addition per operational standards.
3. **Deployment topology specifies environments whose isolation requirements are ambiguous** (e.g., "staging" environment is described but it is unclear whether it shares infrastructure with production). Blocking for EPC environment definitions.
4. **Existing infrastructure agreements are required for selected technology** (e.g., enterprise license, cloud committed spend agreement, regulated hosting approval) and their existence is unknown. DO raises CQ to PM for procurement status.
5. **Safety Constraint Overlay imposes technology constraints** (e.g., encryption at rest, network isolation, audit logging requirements) that are not reflected in the TA Technology Component Catalog. DO raises structured feedback to SwA before raising a CQ — the gap may be resolvable by SwA updating the TA.

CQ format: per `clarification-protocol.md §3`. DO does not raise CQs about technology selection preferences — those are SwA's authority and the DO provides feedback through the structured feedback loop.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="DO", phase="D", artifact_type="technology-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="D")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 1 — Acknowledge and retrieve TA draft

On receipt of `handoff.issued` from SwA for the TA draft:

1. Emit `handoff.acknowledged` with `retrieval_intent: full` — the DO must read the entire TA including all Technology Component Catalog entries, ADRs, Infrastructure Diagram, Deployment Topology, and Technology Standards Catalog.
2. Read the Technology Architecture draft from `engagements/<id>/work-repositories/technology-repository/technology-architecture/ta-<version>.md`.
3. Read the current SCO from `engagements/<id>/work-repositories/safety-repository/` to understand security and safety constraints.
4. Begin feasibility assessment. Emit `artifact.drafted` for the Phase D Feedback Record as soon as the first substantive section is started.

### Step 2 — Infrastructure feasibility assessment

For each technology component in the TA Technology Component Catalog, assess:

**Provisioning feasibility:**
- Can this component be provisioned within the selected platform or cloud provider?
- Is the version constraint specified realistic (not end-of-life, not pre-release for a production role)?
- Are there licensing, procurement, or access requirements that are currently unresolved?

**Operational complexity:**
- Is the component a managed service (lower operational burden) or self-hosted (higher operational burden requiring IaC, patching, backup management)?
- Does the operational complexity match the engagement's delivery capacity?

**Environment parity:**
- Can all environments (Production, Staging, Development, CI) use the same component or a compatible equivalent? If not, what are the parity gaps and what risks do they introduce?

Categorise each finding using the following taxonomy (record in the Feedback Record):

| Category | Definition | Example |
|---|---|---|
| **Infeasible** | Cannot be provisioned with selected platform; requires a replacement decision | Component requires a cloud service not available in the selected region |
| **High-risk** | Can be provisioned but introduces unacceptable operational risk without mitigation | Database with no managed backup service in selected platform |
| **Operationally complex** | Feasible but will require substantial IaC effort or ongoing operational overhead | Self-hosted Kubernetes control plane for a small-scale engagement |
| **Recommended alternative** | DO recommends a different component that provides equivalent capability with lower operational complexity | Managed database service instead of self-hosted equivalent |
| **Accepted** | Component is feasible, appropriate complexity, no concerns | Standard cloud-managed services within the selected platform |

### Step 3 — Observability stack completeness check

Assess whether the TA Technology Component Catalog includes all required observability components. The minimum viable observability stack for a production system is:

- **Metrics collection:** time-series metrics from all Technology Components (runtime, platform, store components)
- **Log aggregation:** structured log collection with correlation IDs; retention policy defined
- **Distributed tracing:** trace context propagation across all application component boundaries
- **Alerting:** alert rules tied to SLA targets; escalation path for infrastructure alerts

If any of these layers is absent, record as a structured feedback item to SwA categorised as **High-risk** (absent observability is a deployment governance gap — Deployment Records cannot be produced accurately without an operational metrics baseline).

### Step 4 — Deployment topology realism check

Assess the TA Deployment Topology against operational realism criteria:

1. **Environment count:** Is the number of environments sufficient for a realistic delivery pipeline? Minimum: Production, Staging/UAT, Development, CI. Flag missing environments.
2. **Network topology:** Are the connectivity patterns described between deployment zones achievable without unresolvable network constraints? Is the production isolation adequate?
3. **Production/non-production parity:** Note all intentional differences between Production and non-production environments. Record differences as accepted deviations in the EPC draft.
4. **Scaling and resource allocation:** Are resource specifications (compute, storage, network) sufficient for the load implied by the application architecture? Flag under-specification as High-risk.

### Step 5 — Cloud provider or platform verification

If the TA selects a specific cloud provider or platform:

1. Verify the provider is within the Technology Standards Catalog. If not, this is a gap for SwA to address (structured feedback, not a DO CQ).
2. Check whether existing procurement agreements, cloud accounts, or access arrangements are required. If existence is unknown, raise a CQ to PM categorised as non-blocking — the EPC will note this as a dependency.
3. If the selected provider introduces regulatory constraints (e.g., data residency, FedRAMP authorisation, GDPR processing agreements), flag to SwA and CSCO via structured feedback.

### Step 6 — Produce Phase D Feedback Record

Compile the structured feedback from Steps 2–5 into a Phase D Feedback Record at `devops-repository/phase-d-feedback/phase-d-feedback-<sprint-id>.md`.

**Feedback record structure:**

```markdown
---
artifact-type: phase-d-feedback
sprint-id: <sprint-id>
raised-by: devops-platform
target-agent: software-architect
target-artifact: TA-<version>
status: open | resolved
---

## Summary
[One paragraph: overall assessment. Is the TA infrastructure-feasible as drafted, conditionally feasible, or infeasible?]

## Component Feasibility Findings
| Component ID | Component Name | Category | Finding | Recommended Action |
|---|---|---|---|---|
| TC-nnn | | Accepted / Infeasible / High-risk / Operationally complex / Recommended alternative | | |

## Observability Stack Assessment
[Pass / Gaps identified — list missing observability layers]

## Deployment Topology Assessment
[Pass / Issues identified — list topology gaps, environment parity concerns]

## Platform Verification
[Provider verified / Unresolved dependencies — list procurement or access dependencies]

## Technology Standards Contributions
[List of operational standards DO recommends be added to the Technology Standards Catalog:
monitoring thresholds, SLA targets, runbook requirements, security gate requirements]

## Open CQs Raised
[List of CQ IDs raised during this review, if any]
```

Emit `handoff.issued` to SwA for the Feedback Record.

### Step 7 — Produce initial Environment Provisioning Catalog draft

In parallel with feedback production, begin the initial EPC draft at `devops-repository/environment-catalog/epc-0.1.0.md`.

At Phase D, the EPC draft captures:
- Environment list (Production, Staging, Development, CI — or project-specific equivalents)
- For each environment: purpose, expected technology component set (cross-referenced from TA), isolation requirements, access control model outline
- Sections that cannot be completed until TA is revised or CQs are answered: mark with `pending-clarifications: [CQ-id]` or `pending-ta-revision: [finding-id]`
- Do NOT baseline the EPC until TA is baselined (version ≥ 1.0.0)

Emit `artifact.drafted` for the EPC draft.

### Step 8 — Technology Standards Catalog contributions

Review the TA Technology Standards Catalog. Propose additions covering operational standards the DO will enforce during Phase F and Phase G:

| Standard | Type | Applies To | Mandatory / Recommended |
|---|---|---|---|
| Minimum observability stack (metrics, logs, traces, alerting) | Internal | All production TC components | Mandatory |
| Security gate requirements for delivery pipelines (dependency scan, SAST, secret scan) | Internal | All CI/CD pipelines | Mandatory |
| SLA target documentation requirement (availability, RTO, RPO) per production service | Internal | All production TC components | Mandatory |
| Environment parity deviation documentation | Internal | All non-production environments | Mandatory |
| Runbook requirement for any manually operated component | Internal | All self-hosted TC components | Mandatory |

Submit proposed additions to SwA via the Feedback Record (§6 above). SwA is accountable for the Technology Standards Catalog — the DO may not write to it directly.

---

## Feedback Loop

**Phase D DO-SwA feedback loop:**

This loop governs the iterative review of the TA draft between DO and SwA. The loop is bounded to preserve sprint discipline.

- **Iteration 1:** DO delivers Phase D Feedback Record to SwA. SwA reviews findings; addresses Infeasible and High-risk items; revises TA draft; re-issues handoff.
- **Iteration 2:** DO reviews revised TA draft; confirms whether Infeasible/High-risk items are resolved; delivers a final disposition (all resolved, or remaining unresolvable items escalated). DO confirms whether EPC draft sections can now be completed.
- **Termination:** Loop terminates when: (a) all Infeasible and High-risk items are resolved and DO records acceptance, or (b) DO and SwA have exchanged 2 iterations and a remaining item cannot be resolved within the current sprint.
- **Max iterations:** 2 before escalation.
- **Escalation:** If Infeasible or High-risk items remain unresolved after 2 iterations, DO raises ALG-010 (inter-agent deadlock) to PM for adjudication. PM reviews both positions, applies RACI (SwA is accountable for TA; DO's feasibility concerns are binding input), and records the adjudication decision in `project-repository/decision-log/`.

### Personality-Aware Conflict Engagement

**Expected tension in this skill:** The DO (Specialist — Systems Stabilizer) and the SwA (Integrator — Technology) have a structurally designed tension: the SwA produces a coherent technology architecture from a design perspective; the DO tests it against operational reality. The Phase D feedback loop is the primary mechanism by which operational reality corrects architectural abstraction. This is a productive, necessary function — not an obstruction.

**DO engagement directive:** When the DO raises an Infeasible or High-risk finding, it must include: (a) the specific TA element or decision being challenged (Technology Component ID or ADR reference), (b) the operational evidence or constraint that makes it infeasible or high-risk (observed failure patterns, load profile constraints, infrastructure limitations, vendor lifecycle concerns), and (c) a concrete alternative or question that would resolve the finding. The DO does not raise "this seems risky" without specifics; it raises "TA component TC-005 specifies synchronous database calls from three independent microservices — under the load profile in EPC §2.3, this will produce a database contention bottleneck above 200 concurrent users." That is an Infeasible finding with evidence.

**SwA engagement directive (from DO's perspective):** When the SwA responds to a DO finding, the DO evaluates whether the response engages the specific operational constraint or merely re-states the design intent. A SwA response that explains *why* the design is architecturally sound without addressing the specific operational constraint is not a resolution — the DO should say so in iteration 2 and escalate if unresolved.

**Resolution directive in this context:** The Phase D feedback loop is resolved when: (a) the SwA revises the TA to address the DO's Infeasible finding and the DO confirms the revision resolves the operational constraint, or (b) the DO and SwA agree that the risk is real but acceptable, with the acceptance documented in the relevant ADR under a risk acceptance entry co-signed by PM. A TA that is baselined with unresolved Infeasible findings is a governance violation (triggers ALG-010).

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="technology-architecture"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Category | Severity | Action |
|---|---|---|---|---|
| ALG-008 | DO is asked to baseline the EPC while the TA is still at version 0.x.x (draft) | GV | S2 | Do not baseline EPC; raise signal to PM; document as a dependency violation |
| ALG-010 | Phase D DO-SwA feedback loop has reached 2 iterations without resolution of Infeasible-category findings | IA | S3 | Raise to PM for adjudication; DO documents both its position and the unresolved SwA position in the Feedback Record |
| ALG-011 | DO discovers internal inconsistency in TA (e.g., Infrastructure Diagram shows components not in Technology Component Catalog) | IA | S3 | Raise to SwA (producing agent) immediately with specific inconsistency identified; if unresolved after 1 iteration, raise to PM |
| ALG-001 | TA technology choice would violate a constraint in the SCO (e.g., a selected component stores regulated data in a non-compliant region) | SC | S1 | Halt DO work on affected EPC section; raise to CSCO (immediate) and PM (concurrent); do not produce EPC section for affected environment until resolved |

---

## Outputs

| Output | Path | Event | Notes |
|---|---|---|---|
| Phase D Feedback Record | `devops-repository/phase-d-feedback/phase-d-feedback-<sprint-id>.md` | `handoff.issued` to SwA | Produced at end of Step 6; iterated per feedback loop |
| Initial EPC draft | `devops-repository/environment-catalog/epc-0.1.0.md` | `artifact.drafted` | Draft only at Phase D; not baselined until Phase F |
| Technology Standards contributions | Via Phase D Feedback Record | — | DO proposes; SwA updates Technology Standards Catalog |

---

## End-of-Skill Memory Close

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="D", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

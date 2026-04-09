---
skill-id: DO-PHASE-G
agent: DO
name: phase-g
display-name: Phase G — Implementation Governance (Delivery and Deployment)
invoke-when: >
  Phase F gate has passed and each Solution Sprint starts; DO provisions environments,
  configures and runs CI/CD pipelines, and produces Deployment Records for every
  deployment event throughout Phase G.
trigger-phases: [G]
trigger-conditions:
  - gate.evaluated (from_phase=F, result=passed)
  - sprint.started (phase=G, sprint-type=solution)
  - handoff.created (handoff-type=architecture-contract, to=devops-platform)
entry-points: [EP-0, EP-D, EP-E, EP-F, EP-G]
primary-outputs: [Deployment Records, CI/CD pipeline configuration, IaC code, Infrastructure compliance contribution]
complexity-class: standard
version: 1.0.0
---

# Skill: Phase G — Implementation Governance (Delivery and Deployment)

**Agent:** DevOps / Platform Engineer  
**Version:** 1.0.0  
**Phase:** G — Implementation Governance  
**Skill Type:** Phase primary — artifact production (accountable); implementation stream delivery  
**Framework References:** `agile-adm-cadence.md §6.8`, `raci-matrix.md §3.9`, `clarification-protocol.md`, `algedonic-protocol.md`, `repository-conventions.md §3`, `framework/artifact-schemas/architecture-contract.schema.md` (consumed, not produced)

---

## Runtime Tooling Hint

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Architecture Contract (`AC`) | Software Architect/PE (handoff) | **Baselined (version ≥ 1.0.0)** per work package | Blocking — DO cannot execute a deployment pipeline for a work package without the corresponding Architecture Contract. The AC defines the compliance requirements that the pipeline must enforce. |
| Environment Provisioning Catalog (`EPC`) | DO (self-produced in Phase F) | **Baselined (version ≥ 1.0.0)** | Blocking — DO provisions environments per the baselined EPC. No deviation from the EPC is permitted without a DO-initiated EPC revision. |
| Solution Sprint Plan | Project Manager | Baselined | Defines which work packages are in scope for each Solution Sprint; determines deployment sequencing |
| Implementation Plan (`IP`) | Project Manager | Baselined | Provides the broader context of delivery ordering; environment readiness gates |
| `sprint.started` event | Project Manager | Must be emitted for each Solution Sprint before DO begins that sprint's work | Hard prerequisite per sprint. DO does not begin a new Sprint's deployment work until `sprint.started` is emitted. |
| Merged Pull Requests (trigger) | Implementing Developer (target project repository) | PR merged to the main branch or release branch per the AC's branch policy | Deployment pipeline is triggered by merged PRs; DO monitors the target project repository for merge events |
| QA test execution results | QA Engineer (handoff) | QA report produced for the Sprint | DO reads QA reports to confirm test gate passage before promoting to Production |

---

## Knowledge Adequacy Check

### Required Knowledge

- The Architecture Contract for the current work package: acceptance criteria, technology compliance requirements, security requirements, and the compliance attestation requirements.
- The baselined EPC: environment topology, pipeline stage definitions, security gate configurations, access control model, and runbook references.
- The target project repository structure: where IaC directories live, where pipeline configuration files live, what the branch promotion model is.
- The observability stack: how to confirm that metrics, logs, and traces are flowing after a deployment; what constitutes a healthy deployment state.
- Deployment failure modes for the technology components in scope: what common failure patterns look like; when to roll back vs. investigate vs. escalate.

### Known Unknowns

| Unknown | Blocking | CQ Target | Impact |
|---|---|---|---|
| Target project repository IaC directory structure (EP-G entry only) | Yes for Phase G environment provisioning | User (via PM) | Cannot write IaC to target-repo without knowing the correct paths |
| CI/CD provider access credentials for pipeline configuration | Yes — pipeline cannot be configured without access | User (via PM) | Phase G cannot begin without this for EP-G entries |
| Production deployment approval authority (if not established in EPC) | Yes for Production promotion | User (via PM) | Production deployments cannot proceed without a defined approval gate |
| Secret values for environment configuration | No — DO provisions the secrets management infrastructure; secret values are injected by the authorised party, not DO | User (operational) | Secrets are not DO's responsibility to hold; DO provides the injection mechanism |

### Clarification Triggers

DO raises a CQ when:

1. **Architecture Contract imposes a compliance requirement that cannot be implemented in the current pipeline without a technology choice that is not in the TA.** DO raises to PM (routing to SwA); this is an AC-TA inconsistency, not a DO decision.
2. **Target project repository IaC directory structure is absent or conflicts with the EPC provisioning specifications.** DO raises to PM; if EP-G entry, this is expected and DO documents the discovered state before raising.
3. **A security gate tool required by the AC is not available for the technology components in scope** (e.g., no SAST tool supports a specific language runtime). DO raises to SwA (via PM) for AC amendment or technology standards update; this is not a DO-authority decision.
4. **Production deployment approval gate mechanism is undefined** after Phase F (EPC was baselined with this as an open item). Blocking for Production CD pipeline configuration; DO raises to PM.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="DO", phase="G", artifact_type="process")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase="G")`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---


### Step 0.S — Standards and Coding Guidelines Discovery

Before provisioning any environment or writing infrastructure-as-code, scan in this order:

1. `technology-repository/coding-standards/` — retrieve infrastructure-as-code (IaC) and scripting standards relevant to the platform stack. Naming conventions, tagging policies, secret management patterns, and prohibited constructs are binding on all DO outputs.
2. `enterprise-repository/standards/` — retrieve SIB entries for all infrastructure platform components (container runtime, orchestration, CI/CD toolchain, monitoring). Any component not in the SIB requires an ADR before deployment.
3. `technology-repository/architecture-decisions/` — retrieve ADRs covering deployment topology, environment parity requirements, and pipeline constraints for the current engagement.

This step is non-skippable. If no IaC standards exist in `technology-repository/coding-standards/`, raise CQ to PM; do not invent infrastructure conventions without a documented basis.

---

### Step 1 — Pre-Sprint: Provision environments

Before the first Solution Sprint begins (`sprint.started` for SS-1 has been emitted by PM), the DO must provision all environments required for that sprint per the baselined EPC.

**Provisioning sequence:**

1. **Provision in critical-path order** as defined in EPC §5 (Provisioning Dependencies and Sequencing).
2. **Write IaC code to the target project repository** via the target project adapter:
   - IaC code is authored in the DO's designated IaC directories (per EPC and engagement configuration in `engagements-config.yaml`).
   - IaC code must produce environments that match the EPC's environment definitions exactly. Any deviation from the EPC requires an EPC revision before deployment.
   - IaC code is committed to the target project repository as part of Phase G provisioning. It is not stored in `devops-repository/` — the `devops-repository/` holds the design specifications; the target project repository holds the implementation.
3. **Execute IaC** to provision environments. Record the provisioning outcome (success/failure, resources created, any deviations from specification) in the Deployment Record for the provisioning event.
4. **Run smoke tests** on each environment post-provisioning to confirm the environment is operational.
5. **Verify observability** — confirm that the observability stack is active for each environment: metrics are flowing, log aggregation is receiving events, tracing is active.
6. **Confirm CI pipeline is operational** — the CI pipeline must be passing on a baseline commit before the Implementing Developer begins feature work.

Notify PM that environment provisioning is complete via a handoff event before PM emits `sprint.started` for the first Solution Sprint. If provisioning fails or cannot be completed: raise ALG-006 (dependency failure) to PM.

### Step 2 — Configure CI/CD pipelines per Architecture Contract

Write pipeline configuration files to the target project repository:
- CI pipeline configuration: implements all stages defined in EPC §2 (pipeline design), in order, with security gates configured per AC requirements.
- CD pipeline configuration: implements environment promotion stages for Staging and Production, including the mandatory approval gate for Production.

**Security gate configuration (non-negotiable per Architecture Contract):**

| Gate | Tool (from TA Technology Standards) | Blocking Threshold | Where in Pipeline |
|---|---|---|---|
| Secret scanning | TA-specified tool | Any detected secret: pipeline fails | CI stage 2 (before build) |
| Dependency vulnerability scan | TA-specified tool | Critical severity: always blocks; High severity: blocks unless explicitly accepted via risk register entry signed by CSCO | CI stage 4 (after dependency install) |
| SAST | TA-specified language-appropriate tool | Critical severity: always blocks; High severity: creates Defect Register entry (QA-accountable) | CI stage 5 (after unit tests) |

If the AC specifies additional security gates beyond these three (e.g., container image scanning, infrastructure drift detection), implement them as additional stages in the order specified by the AC.

**Any request to remove or disable a security gate must be escalated immediately.** The DO does not have authority to remove security gates. If a gate is causing false positives or blocking legitimate work, the DO documents the specific issue and raises it to SwA and CSCO via PM for AC amendment. Disabling the gate unilaterally triggers ALG-009.

### Step 3 — Per Solution Sprint: Execute deployment pipeline and record outcomes

For each merged PR in the target project repository:

**3a. Pipeline execution:**
1. The CI pipeline triggers automatically on merge.
2. DO monitors pipeline execution. If the pipeline fails: identify the failure stage; determine whether the failure is an infrastructure issue (DO's domain) or an application issue (DE/QA domain).
   - **Infrastructure failure** (e.g., pipeline configuration error, environment connectivity, IaC drift): DO diagnoses and remediates; records in Deployment Record with root cause.
   - **Application failure** (e.g., test failure, SAST finding in application code): DO records the failed deployment; notifies DE and QA; does not attempt to fix application code.
3. On CI pipeline success: artifact is published to artifact registry, tagged CI-verified.

**3b. Staging deployment:**
1. Trigger CD pipeline for Staging environment on CI pipeline success (or per the sprint's deployment cadence as defined in the Solution Sprint Plan).
2. Execute deployment to Staging per EPC pipeline design; run post-deployment smoke tests; verify observability.
3. On smoke test failure: execute automatic rollback; record in Deployment Record as failed deployment; notify QA and DE.
4. On success: notify QA that the Staging environment is ready for test execution.

**3c. Production deployment (when authorised):**
1. Production deployment is authorised only after:
   - QA has produced a test execution report for the Staging deployment (QA handoff acknowledged).
   - The Compliance Assessment confirms no open Severity-1 defects (QA-accountable).
   - The Production promotion approval gate has been cleared (per EPC §4 approval authority).
2. Execute CD pipeline for Production; run post-deployment smoke tests; verify observability.
3. On smoke test failure: execute rollback; raise ALG event if rollback fails (infrastructure failure).
4. On success: record Deployment Record as successful; update Governance Checkpoint Record contribution.

### Step 4 — Produce Deployment Record per deployment event

A Deployment Record is produced for every pipeline execution that results in a change to an environment. This includes:
- Environment provisioning events (Step 1)
- Staging deployments (Step 3b)
- Production deployments (Step 3c)
- Rollback events
- Infrastructure configuration changes (IaC updates that do not involve application artifacts)

**Deployment Record format:**

Author at `devops-repository/deployment-records/dr-<sprint-id>-<sequence>.md`:

```markdown
---
artifact-type: deployment-record
artifact-id: DR-<sprint-id>-<sequence>
version: 1.0.0
sprint: <sprint-id>
environment: <environment-name>
deployment-type: provisioning | application | infrastructure | rollback
trigger: pr-merge | scheduled | manual | rollback
source-artifact: <commit-SHA or IaC version>
status: success | failed | rolled-back
pipeline-run-id: <CI/CD provider run identifier>
---

## Deployment Summary
[What was deployed; what changed; which work package or PR this deployment corresponds to]

## Pre-Deployment State
[Relevant environment state before deployment: running version, health status]

## Deployment Execution
[Pipeline stages executed; any warnings or non-critical findings; duration]

## Security Gate Results
| Gate | Tool | Result | Details |
|---|---|---|---|
| Secret scan | | Pass / Fail | |
| Dependency vulnerability scan | | Pass / CVE count | Severity breakdown |
| SAST | | Pass / Finding count | Critical count (must be 0 to proceed) |

## Post-Deployment State
[Environment health after deployment: smoke test results, observability confirmation]

## Rollback Record (if applicable)
[Rollback trigger; rollback procedure executed; post-rollback state]

## Infrastructure Issues Identified
[Any infrastructure-layer issues discovered during this deployment; their disposition]

## Governance Checkpoint Contribution
[Infrastructure compliance status summary for PM's Governance Checkpoint Record]
```

Emit `artifact.baselined` for each Deployment Record upon completion.
Emit `handoff.issued` to PM for each Deployment Record.

### Step 5 — Contribute to Governance Checkpoint Record

PM is accountable for the Governance Checkpoint Record per RACI §3.9. DO provides the infrastructure compliance status section.

For each Governance Checkpoint (typically one per Solution Sprint, or per PM's request):

Deliver to PM (via handoff) the following inputs:

1. **Environment health status:** all environments operational / degraded (with details) / down (with ALG signal reference if applicable)
2. **Pipeline compliance status:** all three security gates active and configured per AC / any gate disabled or reconfigured (with reason and approval record)
3. **Deployment record completeness:** all merges in this sprint period have corresponding Deployment Records / missing records (with list)
4. **Infrastructure drift:** IaC state matches the baselined EPC / drift detected (with details and remediation plan)
5. **Open infrastructure issues:** any unresolved infrastructure issues; their severity; their impact on delivery

### Step 6 — Phase G exit: Confirm environment-contract compliance

At Phase G exit, the DO performs a final compliance check and casts a gate vote.

**Phase G exit checklist (DO evaluates):**

- [ ] All environments described in the EPC are provisioned and operational.
- [ ] All Deployment Records are complete — every deployment event has a corresponding record.
- [ ] The final production deployment has passed all security gates (no Critical findings; no bypassed gates).
- [ ] Observability is confirmed active for all production components.
- [ ] Infrastructure state matches the EPC topology (no unresolved drift).
- [ ] No open algedonic signals in the infrastructure failure category.
- [ ] All production deployments have passed the approval gate (no unauthorised deployments).
- [ ] Final production smoke test is passing.

Cast `gate.vote_cast` for Phase G exit:
- `vote: approved` if all checklist items pass.
- `vote: blocked` with specific blocking items listed if any checklist item fails.

---

## Incident Handling

### Infrastructure failure category

If a deployment failure or environment degradation occurs that cannot be recovered within the current pipeline execution:

1. **Assess severity:**
   - **Recoverable:** rollback available; environment returns to pre-deployment state; no data loss. Record in Deployment Record; notify PM via infrastructure compliance contribution.
   - **Unrecoverable within current sprint:** environment is degraded or data integrity is at risk; rollback fails or produces a worse state. Proceed to ALG escalation.

2. **Raise algedonic signal** for unrecoverable failures: emit `algedonic.raised` with the appropriate trigger.

3. **Enter Failsafe Mode** per `algedonic-protocol.md §6`: halt new deployments to affected environments; do not baseline new artifacts for that environment scope; PM adjudicates.

4. **Write signal record** to `engagements/<id>/algedonic-log/<sprint-id>-ALG-<sequence>.md` per `algedonic-protocol.md §5`.

### Security gate failure handling

If a security gate blocks a pipeline:
- The failure is recorded in the Deployment Record with the full gate output.
- For SAST Critical findings: DO records the finding; notifies SwA and QA; does not approve a bypass.
- For Dependency Critical CVE: DO records the finding; notifies SwA; informs PM. SwA determines whether a CVE exemption can be accepted (via risk register entry signed by CSCO) or whether the dependency must be updated.
- **Under no circumstances does the DO disable or bypass a security gate to allow a deployment to proceed.** ALG-009 applies to any Architecture Contract created without required CSCO sign-off; the same principle applies to security gate bypasses.

---

## Feedback Loop

**Per-Sprint deployment health loop:**

- **Iteration 1:** DO executes deployment pipeline; records outcomes in Deployment Record; delivers infrastructure compliance contribution to PM.
- **Iteration 2 (if sprint includes a remediation cycle):** DO addresses infrastructure issues identified in Iteration 1; re-deploys; records second Deployment Record.
- **Termination:** Loop terminates when the sprint's delivery goals are met (all work package PRs deployed, all environments healthy) or when an ALG escalation removes the scope from normal iteration.
- **Max iterations per sprint:** 2 deployment cycles within a single Solution Sprint before PM is notified of persistent infrastructure instability. If 2 deployment cycles do not produce a stable environment, PM decides whether to extend the sprint or escalate.
- **Escalation:** Persistent environment instability (more than 2 deployment failures for the same root cause) triggers ALG-006 (dependency failure / TC category) to PM. PM restructures the sprint plan or initiates a Phase H change process if the root cause is architectural.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="process"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition | Category | Severity | Action |
|---|---|---|---|---|
| ALG-001 | A security gate Critical finding is discovered in a component that the Architecture Contract classifies as safety-relevant | SC | S1 | Halt deployment; raise to CSCO (immediate) and PM (concurrent); do not proceed until CSCO approves disposition |
| ALG-006 | Environment provisioning fails and cannot be completed before the Solution Sprint is scheduled to begin; dependency cannot be resolved within the sprint | TC | S2 | Raise to PM immediately; DO documents the specific provisioning failure and estimated resolution time; PM adjusts sprint plan |
| ALG-007 | DO is asked to write an artifact to a path outside `devops-repository/` or the designated target project adapter paths | GV | S1 | Refuse the write; raise to PM; document the request and DO's refusal |
| ALG-009 | DO is requested to disable or bypass a security pipeline gate (secret scan, dependency vulnerability scan, or SAST) for any reason without a CSCO-signed risk register entry | GV/SC | S1 | Refuse; raise to CSCO (immediate) and PM (concurrent); record the request and refusal in the Deployment Record |
| ALG-011 | DO discovers that the current IaC state in the target project repository has drifted from the baselined EPC in a way that is not explained by any Deployment Record | IA | S3 | Raise to PM; DO records the drift; determines whether drift is the result of an unrecorded manual change or an automated process; does not remediate until PM has acknowledged the signal |
| ALG-013 | A deployment to a safety-relevant environment reveals a test failure in a safety-critical component at Severity 1 (as classified in the QA report) | SC | S1 | Halt deployment; roll back; raise to CSCO (immediate) and SwA (halt deployment); DO records the event in the Deployment Record with the QA report reference |
| ALG-003 | DO discovers during pipeline execution that an artifact being deployed contains configuration that violates a regulatory or compliance obligation identified in the SCO | RB | S1 | Halt deployment; raise to CSCO (immediate) and PM (concurrent); do not deploy to regulated environment until CSCO approves |

---

## Outputs

| Output | Path | Event | Notes |
|---|---|---|---|
| IaC code (environment provisioning) | Target project repository IaC directories (per engagement config) | — (no DevOps repository event; target-repo commit) | Written via target project adapter; IaC implements the EPC specifications |
| CI/CD pipeline configuration | Target project repository pipeline config directories | — (target-repo commit) | Written via target project adapter; implements EPC pipeline design and AC security requirements |
| Deployment Record (per deployment event) | `devops-repository/deployment-records/dr-<sprint-id>-<sequence>.md` | `artifact.baselined`, `handoff.issued` to PM | DO's primary accountable Phase G output; one record per deployment event |
| Infrastructure compliance contribution (to Governance Checkpoint Record) | Delivered via `handoff.issued` to PM | `handoff.issued` | PM is accountable for Governance Checkpoint Record; DO provides the infrastructure compliance section |
| Phase G exit gate vote | EventStore `gate.vote_cast` | — | DO votes approved or blocked with specific checklist results |
| Algedonic signal records (if conditions arise) | `engagements/<id>/algedonic-log/<sprint-id>-ALG-<sequence>.md` | `algedonic.raised` | Written only when an algedonic condition is triggered |

---

## End-of-Skill Memory Close

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase="G", key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.

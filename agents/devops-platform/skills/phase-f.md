# Skill: Phase F — Migration Planning (Environment Provisioning)

**Agent:** DevOps / Platform Engineer  
**Version:** 1.0.0  
**Phase:** F — Migration Planning  
**Skill Type:** Phase primary — artifact production (accountable)  
**Framework References:** `agile-adm-cadence.md §6.7`, `raci-matrix.md §3.8`, `clarification-protocol.md`, `algedonic-protocol.md`, `repository-conventions.md §3`, `framework/artifact-schemas/technology-architecture.schema.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Technology Architecture (`TA`) | Software Architect/PE | **Baselined (version ≥ 1.0.0)**; Phase D gate passed | Hard prerequisite — EPC cannot be baselined if TA is not yet baselined. EPC may continue to be drafted but must not be baselined until this condition is met (ALG-008 applies). |
| Implementation Plan draft (`IP`) | Project Manager | Draft (version 0.x.x) acceptable at Phase F entry; PM is producing IP concurrently | DO consults IP for environment readiness gate requirements and sprint sequencing; provides EPC as input to PM's IP finalisation |
| Transition Architecture Diagrams | Software Architect/PE (handoff) | Draft acceptable; version 0.1.0 or higher | Required for understanding which environments must exist at each transition state; which components exist at transition start vs. transition end |
| Architecture Roadmap final draft | Project Manager | Draft acceptable | DO reads to understand delivery sequencing and which environments must be ready for each roadmap increment |
| EPC draft from Phase D/E | DO (self-produced) | Version 0.2.0 or higher (Phase E output) | The Phase F procedure extends and baselines the EPC draft |
| `sprint.started` event | Project Manager | Must be emitted for Architecture Sprint F before DO begins work | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- The full Technology Architecture: all technology components, deployment topology, network topology, access control model, and observability stack as defined in the baselined TA.
- The Transition Architecture Diagrams: what the target state is at each transition step; which components exist at each step; which transition architectures are interim (to be decommissioned) vs. target (permanent).
- The delivery sequencing from the Architecture Roadmap: which Solution Sprints will require which environments; which increments require environments to exist before the sprint begins.
- Standard IaC authoring patterns for the technology components selected in the TA: enough to define environment provisioning specifications that an IaC author can implement without ambiguity.
- CI/CD pipeline security gate requirements: dependency vulnerability scanning (tooling, threshold, blocking/non-blocking per stage), SAST (language-appropriate tooling, blocking on critical findings), secret scanning (blocking, pre-commit and pipeline).
- Runbook requirements: what operational procedures must be documented for each environment and each deployment event type.

### Known Unknowns

| Unknown | Blocking | CQ Target | EPC Section Affected |
|---|---|---|---|
| Cloud provider account identifiers, subscription IDs, or organisation IDs | Yes, for environment provisioning specifications that reference specific accounts | User (via PM) | EPC environment definitions — provider account section |
| Target branch strategy (trunk-based, GitFlow, etc.) | No — DO adopts trunk-based as default; notes in pipeline design; raises CQ if project has an existing strategy that conflicts | User (via PM) | EPC pipeline design — branch promotion policy |
| Approval gates for production deployments (who approves, what is the approval mechanism) | Yes, for production CD pipeline configuration | User (via PM) | EPC pipeline design — production promotion gate |
| Secret management approach (vault product, cloud-native secrets manager, etc.) | No — DO selects from TA technology components; if no secrets manager is present in TA, raises structured feedback to SwA | SwA (if missing from TA) | EPC access control model; pipeline secret injection design |
| Environment naming conventions and resource tagging standards | No — DO applies internal convention unless user has an existing standard | User (via PM) if existing standard is required | EPC environment definitions — resource naming |

### Clarification Triggers

DO raises a CQ when:

1. **Cloud provider account identifiers are required to complete environment provisioning specifications** and are not present in any available artifact. Blocking for EPC environment definitions; non-blocking for other EPC sections.
2. **Production deployment approval gate mechanism is undefined** — who must approve a production deployment and through what mechanism (ITSM ticket, PR review, pipeline gate) is not specified. Blocking for production CD pipeline design.
3. **Transition Architecture Diagrams imply a data migration procedure** but neither the TA nor the Implementation Plan provides the migration approach or data volume. DO raises to PM (routing to SwA/SA as appropriate) — the EPC can describe migration pipeline stages at an abstract level pending this answer.
4. **TA includes a technology component type not previously encountered** in the DO's operational knowledge (e.g., a novel database engine, a proprietary platform service) and standard provisioning patterns are unknown. DO raises to PM for user clarification on operational context; notes this as a knowledge gap in the EPC.

---

## Procedure

### Step 1 — Author Environment Provisioning Catalog

The EPC is the DO's primary Phase F accountable artifact. It is the specification that governs all environment provisioning in Phase G. All Phase G IaC and pipeline implementation must be traceable to a section of the baselined EPC.

Author `devops-repository/environment-catalog/epc-1.0.0.md`. The EPC must include the following sections:

#### Section 1: Catalog Header
```markdown
---
artifact-type: environment-provisioning-catalog
artifact-id: EPC-nnn
version: 1.0.0
sprint: <sprint-id>
ta-reference: TA-<version>
ip-reference: IP-<version> (draft)
status: baselined
pending-clarifications: []
---
```

#### Section 2: Environment Definitions

For each environment (at minimum: Production, Staging, Development, CI):

| Field | Description |
|---|---|
| Environment name | Canonical identifier (e.g., `prod`, `staging`, `dev`, `ci`) |
| Purpose | What this environment is for; who accesses it; what deployment frequency is expected |
| Technology components | Cross-referenced from TA Technology Component Catalog (TC-nnn list) |
| Resource specifications | Compute: instance type or resource request/limit. Storage: volume sizes, IOPS targets. Network: VPC/VNet configuration, subnet structure, expected bandwidth. (These are design specifications, not IaC code.) |
| Provider account | Cloud provider account or on-premises hosting location; account ID or identifier (from CQ answer if required) |
| Environment parity deviations | Explicit list of ways this environment differs from Production, with accepted risk rationale for each deviation |
| Access control model | Identity and access model: who (roles, not individuals) has read, write, deploy access; which service accounts are required |
| Secrets management | How secrets are injected into this environment; which secrets manager or vault applies |
| Monitoring scope | Which observability stack components monitor this environment; which alert rules apply |

#### Section 3: Network Topology

For each environment, define:
- Network boundary: VPC/VNet, availability zones, subnets (public/private/data tiers)
- Ingress: load balancer, API gateway, or edge configuration
- Egress: outbound NAT, internet gateway, or private endpoints
- Inter-service communication: service mesh, internal DNS, or direct TCP
- Cross-environment connectivity: none (default for Production), CI→Dev pipeline triggers

Reference the TA Infrastructure Diagram as the authoritative topology source; document any EPC deviations from the TA with rationale.

#### Section 4: Access Control Model

For each environment:
- IAM roles and their permissions (principle of least privilege — each pipeline stage and runtime service has the minimum required access)
- Service account definitions for CI/CD pipelines (separate service accounts per environment; Production service account has deploy-only, not admin, access)
- Human access: operator access, break-glass access procedure, access review cycle
- Secrets injection model: which secrets management product is used; how secrets are accessed at runtime (environment variables, mounted volumes, SDK calls)

#### Section 5: Provisioning Dependencies and Sequencing

Identify provisioning dependencies — which environment components must exist before others can be provisioned:

| Component | Depends On | Provisioning Phase |
|---|---|---|
| e.g., Application service | Database provisioned; secrets manager populated | Phase 2 |
| e.g., CI pipeline | Cloud account active; artifact registry created | Phase 1 — Critical path |
| e.g., Observability stack | Network topology provisioned; IAM roles assigned | Phase 2 |

Identify the critical-path provisioning sequence: which components must be available before the first Solution Sprint can begin. This is the minimum viable environment state for Phase G entry.

### Step 2 — Define pipeline stages

Author the CI/CD pipeline design at `devops-repository/pipeline-design/pipeline-design-<sprint-id>.md`.

#### CI Pipeline (build and verification)

Required stages (in order):

1. **Source checkout and dependency installation** — pin dependency versions; verify lockfile integrity
2. **Secret scanning** — scan for accidentally committed secrets (tokens, API keys, credentials) in the commit. **Blocking gate — pipeline fails if secrets are detected.** Tooling selected from TA Technology Standards Catalog.
3. **Dependency vulnerability scan** — identify known CVEs in direct and transitive dependencies. **Blocking gate for Critical and High severity CVEs** (threshold configurable per Architecture Contract, but Critical must always block). Tooling selected from TA.
4. **Unit test execution** — run unit test suite; fail on any test failure or coverage threshold breach
5. **Static Application Security Testing (SAST)** — language-appropriate static analysis. **Blocking gate for Critical severity findings.** High severity findings produce a warning and must be tracked in the Defect Register.
6. **Build / container image build** — produce the deployable artifact; tag with commit SHA and sprint ID
7. **Integration test execution (if applicable)** — run integration tests against a test double environment or CI-local composed services
8. **Artifact publication** — publish verified artifact to artifact registry; tag as CI-verified

#### CD Pipeline (promotion and deployment)

Required stages per environment promotion (Staging, Production):

1. **Environment readiness check** — confirm target environment is operational (health probe); fail and alert if not
2. **Deployment** — apply IaC changes and deploy application artifacts; use immutable deployment pattern where possible (blue/green, canary, or rolling — specified per environment in EPC §2)
3. **Post-deployment smoke test** — run a minimal set of tests confirming the deployment is functional; fail deployment if smoke tests fail; trigger automatic rollback
4. **Observability verification** — confirm metrics, logs, and traces are flowing from the deployed component; fail if observability is dark after deployment (indicating a misconfiguration)
5. **Production promotion gate (Production only)** — manual or automated approval gate before traffic shift; approval authority defined in EPC §4

Record pipeline stage requirements in the pipeline design document; do not write executable pipeline configuration at this stage — that is Phase G (target project adapter write).

### Step 3 — Author deployment runbooks

Author deployment runbooks at `devops-repository/runbooks/`. Runbooks are procedure descriptions, not executable scripts. They provide the operational context for deployment events and are the reference document for DO self-diagnosis when a deployment fails.

Minimum runbook set:
- **Environment Provisioning Runbook:** procedure for initial environment setup; pre-flight checks; rollback procedure if provisioning fails
- **Deployment Runbook (per environment type):** pre-deployment checks; deployment execution procedure; post-deployment validation; rollback decision criteria and procedure
- **Incident Response Runbook (infrastructure):** symptoms-to-action table for common infrastructure failure modes (environment down, pipeline failure, observability gap, security alert)

Runbooks do not substitute for IaC automation — they describe what the automation does and what to do when it does not work.

### Step 4 — Review Implementation Plan for environment readiness gates

Read the PM's Implementation Plan draft. Identify all instances where Solution Sprint work depends on environment availability. Verify that the IP includes explicit environment readiness gates:

- Production environment must be provisioned and smoke-tested before any Production deployment Solution Sprint begins.
- Staging environment must be provisioned before Solution Sprints that include staging deployment.
- CI pipeline must be operational before the first Pull Request is merged in the first Solution Sprint.

If environment readiness gates are missing from the IP, provide structured feedback to PM via a handoff record (DO does not write to project-repository; feedback goes via handoff event). PM updates the IP.

### Step 5 — Baseline Environment Provisioning Catalog

Pre-baseline checklist (DO self-evaluates):

- [ ] All environments defined: minimum Production, Staging, Development, CI.
- [ ] All TA technology components (TC-nnn) are addressed in at least one environment definition.
- [ ] All `pending-clarifications` items are resolved or explicitly accepted as non-blocking assumptions with documented risk.
- [ ] Network topology is consistent with the TA Infrastructure Diagram.
- [ ] Access control model specifies least-privilege roles for all pipeline service accounts and runtime services.
- [ ] Provisioning dependencies are sequenced and the critical-path sequence for Phase G entry is identified.
- [ ] Pipeline stage definitions include all three mandatory security gates (secret scan, dependency vulnerability scan, SAST).
- [ ] Deployment runbooks exist for all environment types.
- [ ] EPC version header is correct: `version: 1.0.0`; `status: baselined`.

On all checklist items satisfied:

1. Emit `artifact.baselined` with `artifact_id: EPC-nnn`, `version: 1.0.0`, `path: devops-repository/environment-catalog/epc-1.0.0.md`.
2. Emit `handoff.issued` to PM.
3. Cast `gate.vote_cast` for the F→G gate: DO's gate condition is that the EPC is baselined and the Implementation Plan acknowledges environment readiness gates. Vote `approved` if both conditions are met; `blocked` with reason if not.

### Step 6 — Submit F→G gate vote

The DO holds gate vote authority at the F→G gate for the environment readiness precondition (per `agile-adm-cadence.md §7.3`: "Environment Provisioning Plan accepted by DevOps").

DO casts `gate.vote_cast` with:
- `transition: F→G`
- `vote: approved` if EPC is baselined and IP environment readiness gates are confirmed
- `vote: blocked` if EPC has unresolved critical gaps or IP does not reflect environment readiness prerequisites; state blocking reason explicitly

PM evaluates the consolidated gate votes from all gate holders. The DO's vote is a precondition for gate passage.

---

## Feedback Loop

**Phase F EPC review loop (with PM and SwA):**

PM reviews the EPC draft as it develops; SwA may raise technical questions about environment-TA consistency.

- **Iteration 1:** DO delivers EPC draft for PM and SwA review. PM checks for Implementation Plan consistency; SwA checks for TA consistency.
- **Iteration 2 (if needed):** DO addresses review comments; produces revised EPC; delivers for re-review.
- **Termination:** Loop terminates when all blocking review comments are addressed and DO baselines the EPC.
- **Max iterations:** 2 review cycles before DO escalates unresolved items to PM for adjudication.
- **Escalation:** If SwA identifies TA inconsistency in the EPC that DO cannot resolve without TA revision, DO raises ALG-011 to SwA (producing agent); if unresolved in 1 iteration, raises to PM (ALG-010).

---

## Algedonic Triggers

| ID | Condition | Category | Severity | Action |
|---|---|---|---|---|
| ALG-008 | DO is instructed to baseline the EPC while TA is still draft (version 0.x.x) | GV | S2 | Refuse to baseline; emit signal to PM; document blocking dependency in sprint log |
| ALG-006 | A Critical-path infrastructure provisioning dependency cannot be resolved before the planned first Solution Sprint date — e.g., cloud account creation requires procurement approval with a lead time that exceeds the planned window | TC | S2 | Raise to PM immediately; PM must adjust Solution Sprint start date or escalate procurement issue; DO documents the dependency and lead time estimate in the EPC |
| ALG-001 | EPC access control model would violate a Safety Constraint Overlay requirement — e.g., SCO requires data at rest encryption but the selected secrets model does not provide it for a regulated data store | SC | S1 | Halt EPC baseline; raise to CSCO (immediate) and PM (concurrent); do not baseline EPC until SCO constraint is addressed |
| ALG-011 | EPC environment topology is internally inconsistent with the baselined TA Infrastructure Diagram after DO's review of the TA — i.e., the TA has been revised after Phase D without DO being notified | IA | S3 | Raise to SwA (producing agent) with specific inconsistency; request reconciliation; if unresolved after 1 iteration, raise to PM |
| ALG-005 | EPC cannot reach baseline after 2 consecutive gate-hold outcomes at the F→G gate evaluation | TC | S2 | Raise to PM for scope reassessment; PM evaluates whether Phase F requires a sprint extension or the Implementation Plan must be restructured |

---

## Outputs

| Output | Path | Event | Notes |
|---|---|---|---|
| Environment Provisioning Catalog (baselined) | `devops-repository/environment-catalog/epc-1.0.0.md` | `artifact.baselined`, `handoff.issued` to PM | DO's primary accountable Phase F output; must reach version 1.0.0 |
| Pipeline Design Document | `devops-repository/pipeline-design/pipeline-design-<sprint-id>.md` | `artifact.drafted` | Design specification for Phase G implementation; not executable code |
| Deployment Runbooks | `devops-repository/runbooks/<runbook-name>.md` | `artifact.drafted` (per runbook) | Procedure references for all environment types and deployment event types |
| IP environment readiness feedback | Delivered via `handoff.issued` to PM | `handoff.issued` | DO input to PM's IP; PM updates IP; DO does not write to project-repository |
| F→G gate vote | EventStore `gate.vote_cast` | — | DO votes approved or blocked; PM evaluates consolidated gate |

---
skill-id: SWA-REV-TA
agent: SwA
name: reverse-architecture-ta
display-name: Reverse Architecture — Phase D/E (Technology Layer Discovery)
invoke-when: >
  EP-G engagement entry; PM emits entry-point.assessed (entry_point=EP-G) and SwA warm-start
  is required; or PM handoff (handoff_type=ep-g-warm-start-swa) is received; or SA warm-start
  artifacts (motivation/business entities) are available and TA has not yet been reconstructed.
trigger-phases: [D, E]
trigger-conditions:
  - entry-point.assessed (entry_point=EP-G)
  - engagement.ep-g.started
  - handoff.created (from PM, handoff_type=ep-g-warm-start-swa)
  - handoff.created (from SA, handoff_type=ep-g-sa-ba-complete)
entry-points: [EP-G, EP-D, EP-H]
primary-outputs:
  - Technology entity files (NOD, DEV, SSW, TSV, ART, NET, TFN, TEV, TIF)
  - Architecture Decision Record stubs (ADR)
  - Technology connection files (archimate/realization, archimate/serving, archimate/assignment)
  - Technology Architecture overview document
  - Gap and Risk Assessment
complexity-class: complex
version: 1.0.0
---

# Skill: Reverse Architecture — Phase D/E (Technology Layer Discovery)

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** D — Technology Architecture / E — Opportunities & Solutions (warm-start)  
**Skill Type:** Warm-start — reverse architecture discovery  
**Framework References:** `sdlc-entry-points.md §4.6`, `framework/artifact-registry-design.md §2.2`, `framework/artifact-schemas/entity-conventions.md`, `framework/artifact-schemas/technology-architecture.schema.md`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Runtime Tooling Hint

Diagram and matrix conventions apply only when this skill explicitly produces or updates diagram artifacts; use `framework/diagram-conventions.md` as the source of truth.

- Discovery/search/filter/query: use `model_query_*`.
- Validation: use `model_verify_file` / `model_verify_all`.
- Deterministic model build/update: use `model_create_entity`, `model_create_connection`, `model_create_diagram` and prefer `dry_run` before write.
- Frontmatter triggers document intent; executable EP/phase sequencing and dependency control are enforced by orchestration.
- Keep reverse-architecture outputs strict and evidence-linked; if invocation context is incomplete, route through CQ/algedonic mechanisms instead of weakening output structure.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| EP-G handoff from PM | PM | `handoff.created (handoff_type=ep-g-warm-start-swa)` | Primary trigger; may be concurrent with or precede SA warm-start |
| Target repository clone(s) | `scan_target_repo()` per registered repo | At least one clone available | IaC, Dockerfiles, CI/CD configs, Kubernetes manifests, package manifests |
| SA warm-start entities (optional) | `model_query_list_artifacts(...)` (or runtime alias) | Optional — if available, TA reconstruction cross-references APP/DOB entities | SwA proceeds independently if SA warm-start has not yet run |
| Enterprise technology standards | `model_query_list_artifacts(...)` (or runtime alias) | Optional — read to identify SIB deviations | Deviations flagged in Gap and Risk Assessment |
| Coding standards | `technology-repository/coding-standards/` | Optional — may not exist pre-EP-G | Absence triggers COD-GAP-001 per `discovery-protocol.md §9` |
| User-provided docs | User (via PM CQ loop) | Any state — deployment diagrams, runbooks, architecture overviews, infrastructure wiki | SwA queries user in Step 1 |
| External source artifacts | Configured adapters | Optional | Infrastructure wikis, deployment runbooks, service catalogs |

---

## Knowledge Adequacy Check

### Required Knowledge

- **Deployment topology:** Where does each component run? Bare metal, VM, container, managed cloud service, FaaS? Can be inferred from `docker-compose.yml`, `kubernetes/`, Terraform, `serverless.yml`, Ansible playbooks.
- **Software stack:** What language runtimes, frameworks, databases, message brokers, caches are in use? Can be inferred from package manifests and base Docker image names.
- **Service boundaries and communication:** How do services communicate? HTTP/REST, gRPC, message queue, event stream? Can be inferred from OpenAPI specs, client library imports, topic/queue configs.
- **Infrastructure components:** Load balancers, API gateways, CDNs, DNS, certificate management, secret stores. Can be inferred from cloud provider configs (Terraform resources, CloudFormation templates, `values.yaml` files).
- **Technology lifecycle status:** Are any components EOL, approaching EOL, or carrying known CVEs? Requires external knowledge + version numbers from manifests.
- **Security controls:** Authentication, authorisation, encryption in transit/at rest. Inferred from TLS config, IAM policies, secret manager usage, OAuth/OIDC configs.

### Known Unknowns

| Unknown | Blocking | CQ Target | Entity Type Affected |
|---|---|---|---|
| Production environment vs. local dev config | No — SwA infers from env variable naming and CI/CD environment stages | User | NOD-nnn, SSW-nnn |
| Managed service account details and regions | No — annotate `[UNKNOWN — CQ pending]`; proceed with service type | User | NOD-nnn |
| Private / internal dependencies not in public registries | Partially — SwA flags as unknown; reconstructs from import paths | User | SSW-nnn |
| Custom internal tooling not discoverable from codebase | No — SwA raises non-blocking CQ; creates placeholder entities | User | ART-nnn, SSW-nnn |
| Current security posture beyond what configs reveal | No — CSCO Safety Retrospective will cover this; SwA flags gaps only | CSCO | — |
| Intended vs. actual deployment (docs may be stale) | No — SwA notes discrepancy; marks affected entities `[potentially-stale]` | User | All |

### Clarification Triggers

1. **No IaC or deployment configuration found:** Codebase contains no Dockerfile, no docker-compose, no Kubernetes, no Terraform, no cloud-provider config. Critical gap — technology layer cannot be reconstructed automatically. Blocking CQ: "Please provide any of the following: deployment diagram, infrastructure description, or a list of the environments and technology stack used."
2. **Ambiguous cloud provider or region:** Config files reference multiple cloud providers or contain placeholder values. Non-blocking; SwA creates generic NOD-nnn entities; raises CQ for provider/region confirmation.
3. **Unknown third-party SaaS services detected:** A domain name in network config or API URL is not a known public service. Non-blocking; SwA creates ART-nnn placeholder; raises CQ.
4. **Version numbers absent from critical components:** A database or runtime component is identified but version cannot be determined. Non-blocking; SwA creates SSW-nnn without version; raises non-blocking CQ.
5. **Security-relevant config gap:** TLS configuration absent, secret management not identifiable, IAM policies reference wildcards. Concurrent notification to CSCO via handoff. CQ to user on security intent.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="D", artifact_type="technology-architecture")` and `query_learnings(agent="SwA", phase="D", artifact_type="technology-entity")`. Prepend returned corrections to working context. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0.S — Standards and Coding Guidelines Discovery

Per `framework/discovery-protocol.md §9`:
1. Read `technology-repository/coding-standards/` — if absent, create gap record COD-GAP-001 and raise non-blocking CQ to PM.
2. Read `enterprise-repository/standards/` — if present, note SIB-approved technology list. Components discovered in Step 2 that are not in the SIB are flagged in the Gap Assessment.

---

### Step 0 — Discovery Scan

**Layer 1 — Engagement state:** Query technology artifacts via `model_query_list_artifacts(...)` (or runtime alias). If any technology entities (NOD, SSW, TSV, etc.) exist → load them and note their version/status. If all absent → fresh warm-start.

Also load SA warm-start entities if available via query tools: application APP/AIF artifacts for TA serving relationships, and motivation constraints (CST) for guardrails.

**Layer 2 — Enterprise repository:** query enterprise technology/standards artifacts via `model_query_list_artifacts(...)` scoped to enterprise. Note any enterprise-mandated platforms, patterns, or SIB-approved components relevant to this domain.

**Layer 3 — External sources:** Query adapters for: "infrastructure", "deployment", "kubernetes", "terraform", "architecture diagram", "service catalog", "runbook". Record results.

**Layer 4 — Target repository automated scan:** For each registered target repo, execute a structured technology scan:

*Container and orchestration:*
- `Dockerfile*`, `.dockerignore` — base image names → SSW-nnn (OS/runtime), ART-nnn (built image)
- `docker-compose*.yml` — service definitions, image refs, port mappings, volume mounts, network definitions → NOD-nnn per service host, SSW-nnn per runtime, NET-nnn per network
- `kubernetes/`, `k8s/`, `helm/`, `charts/` — `Deployment`, `Service`, `Ingress`, `ConfigMap`, `Secret`, `PersistentVolumeClaim` → NOD-nnn (cluster nodes), TSV-nnn (k8s services), SSW-nnn (container runtimes)

*Infrastructure as Code:*
- `terraform/`, `*.tf` — `resource` blocks → NOD-nnn (compute), SSW-nnn (managed services: RDS → database, ElastiCache → cache, SQS → queue), NET-nnn (VPC, subnet), TIF-nnn (ALB, API Gateway)
- `ansible/`, `*.yml` playbooks — installed packages, configured services → SSW-nnn
- `cloudformation/`, `*.template.yaml` — resource types mapped to entity types as above
- `serverless.yml` — functions → ART-nnn (Lambda/function artifacts), TSV-nnn (API Gateway service)
- `.github/workflows/`, `gitlab-ci.yml`, `Jenkinsfile`, `circle.yml`, `azure-pipelines.yml` — build/deploy stages → ART-nnn (build artifact), deployment targets → NOD-nnn environments

*Runtime and language stack:*
- Package manifests (`package.json`, `pyproject.toml`, `pom.xml`, `go.mod`, `Cargo.toml`, `Gemfile`) — runtime + framework versions → SSW-nnn (language runtime), SSW-nnn (framework)
- Database client libraries — infer database type and version range → SSW-nnn (database)
- Message broker client libraries — infer broker type → SSW-nnn (message broker)
- Cache client libraries — infer cache type → SSW-nnn (cache)

*Networking and security:*
- `nginx.conf`, `traefik.yml`, `.htaccess` → TIF-nnn (proxy/load-balancer interface), NOD-nnn (proxy node)
- TLS certificate references → security annotation on NOD-nnn
- OAuth/OIDC config files → SSW-nnn (identity provider), security annotation
- Secret manager references (AWS SSM, HashiCorp Vault, GCP Secret Manager) → SSW-nnn (secret store)

Annotate every extracted entity with `[inferred: target-repo:<id>:<file-pattern>]`.

**Layer 5 — EventStore:** Check for prior `cq.answered` events at phases D/E with technology context.

---

### Step 1 — User Context Query

Compose a **single batched context request** to the user for what automated scan could not resolve. Maximum 6 targeted questions. Include:
- Brief summary of what was found: "I found [X] Dockerfiles, [Y] Terraform resources, [Z] CI/CD stages across [N] repos."
- Specific questions:
  - "Are there deployment environments beyond what I found (e.g., staging, pre-prod, DR)? If so, what technology differences exist between them?"
  - "Are there any production services that don't have IaC defined? If so, please list them."
  - "What cloud provider(s) and regions are used?"
  - "Are there any SaaS or managed services I may have missed? (e.g., monitoring, logging, APM, CDN)"
  - "Are there any known end-of-life components, unpatched CVEs, or security concerns I should note?"
  - "Please share any deployment diagrams, infrastructure topology diagrams, or runbooks."

After response: integrate user answers and referenced docs. Update entity drafts.

---

### Step 2 — Technology Entity Inference and Draft Building

Map scan results to typed technology entities per `framework/artifact-registry-design.md §4`:

| Entity type | What it represents | Key evidence sources |
|---|---|---|
| `node` (NOD) | Execution environment: physical server, VM, container instance, K8s pod, serverless region | Dockerfile, k8s Deployment, Terraform compute resource |
| `device` (DEV) | Physical/network device: load balancer appliance, firewall, hardware | Terraform network resource, nginx reverse-proxy config |
| `system-software` (SSW) | Software platform: OS, runtime, framework, database, message broker, cache, identity provider | Base image, package manifest, IaC managed service |
| `technology-service` (TSV) | Externally-visible technology service: K8s service, API Gateway, DNS entry, CDN distribution | K8s Service manifest, API Gateway config, Terraform output |
| `artifact` (ART) | Deployable product: Docker image, Lambda ZIP, compiled binary, built package | Dockerfile final stage, CI/CD artifact step, serverless.yml handler |
| `network` (NET) | Communication network: VPC, subnet, overlay network | Terraform VPC/subnet, docker-compose networks |
| `technology-function` (TFN) | Technology function: CI/CD pipeline function, scheduled task, batch job | CI/CD job, cron job, K8s CronJob |
| `technology-event` (TEV) | Technology event: deployment event, scale event, alert trigger | CloudWatch alarm, K8s HPA trigger |
| `technology-interface` (TIF) | Technology interface: load balancer, API gateway, proxy, service mesh endpoint | Ingress, ALB listener, nginx upstream |

**Environment differentiation:** Create one NOD-nnn per logical deployment environment (dev, staging, prod), not per instance. Label environments clearly.

Assign provisional IDs continuing from the highest existing ID per prefix. Annotate all inferred fields.

---

### Step 3 — User Confirmation Loop

Present the proposed technology entity catalogue for user validation before writing files:

1. Group by environment (prod, staging, dev) and then by layer (nodes → software → services → artifacts).
2. For each entity: `[id] [type] — [name] — version — environment — source annotation`
3. Highlight all `[UNKNOWN]` version fields and `[potentially-stale]` entries.
4. Ask user to: (a) confirm, (b) correct wrong identifications, (c) add missing components, (d) confirm environment mapping.

**Iteration 1:** User reviews; SA incorporates corrections.  
**Iteration 2:** Present revised set if structural changes (component type changed, environment mapping corrected, significant component added). Skip if only version clarifications.  
**Max iterations:** 2. Proceed after iteration 2; retain unresolved items as `[UNKNOWN]`.

---

### Step 4 — Write Technology Entity Files

For each confirmed entity, create/update via deterministic model writer (`model_create_entity`, `dry_run` first) at the correct ERP path:

| Entity type | Path |
|---|---|
| NOD | `technology-repository/technology/nodes/<id>.md` |
| DEV | `technology-repository/technology/devices/<id>.md` |
| SSW | `technology-repository/technology/system-software/<id>.md` |
| TSV | `technology-repository/technology/services/<id>.md` |
| ART | `technology-repository/technology/artifacts/<id>.md` |
| NET | `technology-repository/technology/networks/<id>.md` |
| TFN | `technology-repository/technology/functions/<id>.md` |
| TEV | `technology-repository/technology/events/<id>.md` |
| TIF | `technology-repository/technology/interfaces/<id>.md` |

Entity frontmatter: `version: 0.1.0`, `status: draft`, `phase-produced: D`, `owner-agent: SwA`, `produced-by-skill: SWA-REV-TA`, `reconstruction: true`.

`§content` section includes: name, version (if known), vendor/provider, environment(s), description, `[inferred]` / `[UNKNOWN]` / `[potentially-stale]` annotations, and any security notes.

`§display ###archimate` subsection for entities that appear in ArchiMate Technology Layer diagrams.

After writing all entity files, refresh diagram macros (`regenerate_macros` runtime helper or model-write server macro auto-include path).

---

### Step 5 — Write Technology Connection Files

Write typed connection files via deterministic model writer (`model_create_connection`, `dry_run` first) to `technology-repository/connections/archimate/<type>/`:

**Priority connections:**
1. **ART → NOD realization** (`realization/`): deployable artifact runs on node
2. **SSW → NOD assignment** (`assignment/`): system software hosted on node
3. **TSV → SSW realization** (`realization/`): technology service realised by system software
4. **NOD → APP serving** (`serving/`): node serves application component (cross-repo reference if SA entities exist)
5. **TSV → APP serving** (`serving/`): technology service serves application component
6. **NOD → NOD association** (`association/`): inter-node communication (if direction cannot be determined) or `flow/` if data flow direction is known
7. **TIF → NOD assignment** (`assignment/`): interface is the entry point for a node cluster
8. **NET → NOD composition** (`composition/`): nodes that belong to a network

For **cross-repository connections** (technology entity serving an application entity owned by SA's architecture-repository): write the connection in `technology-repository/connections/` and include both the `technology-repository` entity ID and the `architecture-repository` entity ID. Note in `§content`: `cross-repo: true`.

Only write connections where both source and target entity files exist in ModelRegistry.

---

### Step 6 — Author ADR Stubs

For each major technology selection discovered (language runtime, framework, database, message broker, cloud provider, container orchestration), author an ADR stub in `technology-repository/decisions/`:

ADR stub contents:
- **Frontmatter:** `artifact-type: architecture-decision`, `status: reconstructed`, `reconstruction: true`
- **Title:** "ADR-NNN: Selection of [technology] for [purpose]"
- **Context:** "[inferred from codebase: <evidence>]"
- **Decision:** "[technology] [version if known] is in use"
- **Consequences:** `[UNKNOWN — requires stakeholder input]`
- **Alternatives Considered:** `[UNKNOWN — not available from code alone]`

ADR stubs are at version 0.1.0. They signal to stakeholders that the decision was made but the rationale was not recorded. SwA raises a non-blocking CQ for each ADR stub asking the user to supply the rationale.

---

### Step 7 — Gap and Risk Assessment

Produce a Gap and Risk Assessment section in the TA overview document (Step 8):

**Gap analysis:**
1. For each APP-nnn component in SA's architecture-repository (if available): confirm a serving technology entity exists. Missing serving → gap entry.
2. For each integration point identified in SA's AA (AIF-nnn, if available): confirm a TIF-nnn or TSV-nnn exists. Missing → gap entry.
3. For each DOB-nnn data entity (if available): confirm a data store SSW-nnn exists. Missing → gap entry.

**Risk assessment:**
1. **Lifecycle risk:** For each SSW-nnn with a known version: check against EOL dates. Flag as RISK-LIFECYCLE-HIGH if EOL ≤ 6 months; RISK-LIFECYCLE-MEDIUM if EOL ≤ 18 months.
2. **Security risk:** Flag each component where TLS is absent, IAM wildcard policies detected, or secret management not configured.
3. **SIB deviation:** For each SSW-nnn not in the enterprise SIB (if SIB available): flag as RISK-SIB-DEVIATION.
4. **ADR coverage:** Count technology components without an ADR. If > 50%: flag RISK-ADR-COVERAGE-LOW.
5. **Reconstruction confidence:** Assess technology layer coverage: HIGH (IaC present + docker configs + CI/CD = full stack visible), MEDIUM (partial IaC or partial config), LOW (only package manifests + README = inferred only).

---

### Step 8 — Produce Technology Architecture Overview Document

Author `technology-repository/overview/ta-overview.md` as a repository-content artifact:

Sections:
1. **Reconstruction Summary** — discovery sources, scan coverage, entity count by type, reconstruction confidence
2. **Deployment Topology Summary** — environments, node types, key services; reference NOD/TSV entity IDs
3. **Technology Stack Summary** — by layer: runtime → framework → data stores → messaging → infrastructure; reference SSW entity IDs
4. **Service Communication Map** — describe inter-service communication patterns; reference TSV/TIF entity IDs
5. **CI/CD Pipeline Summary** — pipeline stages and artifact production; reference ART/TFN entity IDs
6. **ADR Status** — list ADR stubs authored; note which need rationale
7. **Gap and Risk Assessment** — from Step 7
8. **Assumptions and Open CQs** — all `[inferred]` / `[UNKNOWN]` / `[potentially-stale]` retained; open CQ-IDs
9. **Recommended Next Actions** — (a) CQ resolution targets, (b) whether a formal Phase D sprint is recommended to validate the reconstruction before Phase G governance proceeds

Frontmatter: `artifact-type: domain-overview`, `domain: technology`, `version: 0.1.0`, `status: draft`, `reconstruction: true`, `entry-point: EP-G`, `produced-by-skill: SWA-REV-TA`.

Emit `artifact.baselined` at version 0.1.0.

---

### Step 9 — Handoffs and CQ Emission

1. **Handoff to SA**: `handoff-type: ep-g-swa-ta-complete`. Payload: technology entity count, cross-repo serving connections list (APP-nnn → TSV-nnn), reconstruction confidence. SA uses this to validate AA warm-start against TA.
2. **Handoff to CSCO**: `handoff-type: ep-g-ta-safety-input`. Payload: security gaps identified, any safety-relevant technology components (e.g., OT/IoT nodes, healthcare data stores). CSCO Safety Retrospective Assessment.
3. **Handoff to PM**: `handoff-type: ep-g-swa-complete`. Payload: reconstruction confidence, open CQ count, risk count, ADR stub count. PM uses this to determine whether to begin Phase G governance immediately or recommend a Phase D validation sprint.
4. Raise formal CQs for all `[UNKNOWN]` and ADR rationale gaps. Batch via PM.
5. Emit `cq.raised` for each CQ.

---

## Feedback Loop

### User Confirmation Loop (Technology Entity Accuracy)

- **Iteration 1:** SwA presents inferred technology entity catalogue (Step 3). User reviews and corrects.
- **Iteration 2:** SwA presents revised catalogue if structural changes occurred. User confirms.
- **Max iterations:** 2. After iteration 2, proceed with `[UNKNOWN]` items as documented assumptions.
- **Escalation:** If iteration 2 produces new contradictions (user corrects iteration 1 corrections), raise `ALG-010` to PM. PM adjudicates.

### CSCO Safety Coordination Loop

- **Iteration 1:** SwA sends security gaps + safety-relevant technology entities to CSCO (Step 9). CSCO reviews and may add safety constraints.
- **Iteration 2:** SwA updates affected entities' `safety-relevant` flags and `§content` security notes. CSCO confirms.
- **Max iterations:** 2.

### Personality-Aware Conflict Engagement

SwA is an **Integrator/Specialist** — simultaneously curious about technical depth and anchored to the architecture mandate. In this reverse architecture skill, the primary tension is between *completeness* (wanting to capture every component perfectly) and *pragmatism* (reconstructing what exists, not what should exist). SwA's stance: report the system as-is without editorialising. Gaps and risks go in the Gap Assessment, not into the entity descriptions. If what is found in the codebase contradicts the SA's application-layer warm-start entities, raise the inconsistency explicitly via a CQ — do not silently reconcile by modifying either set of entities.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 correction is structural (entity type wrong, entity representing wrong component) | S2 |
| `algedonic` | Any ALG raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised for component version that was in a manifest SwA had already scanned | S2 |
| `missing-evidence-source` | A new evidence source type (e.g., a config file pattern) discovered in iteration 1 that should be part of the standard scan protocol | S2 |

On trigger: call `record_learning()` with `artifact-type="technology-entity"`, error-type per `framework/learning-protocol.md §4`, correction ≤3 sentences. Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-REV-001 | A technology component is discovered that clearly processes safety-critical data (e.g., patient records, financial transactions, safety control signals) and no safety classification exists in engagement artifacts | S1 | Halt reconstruction of affected entities; emit `alg.raised`; notify CSCO and PM immediately |
| ALG-007 | `write_artifact` call raises `RepositoryBoundaryError` — SwA attempted to write outside `technology-repository/` | S2 | Stop write; emit `alg.raised`; review path computation; correct before retrying |
| ALG-C03 | `write_artifact` fails: connection references entity not in ModelRegistry | S2 | Do not write connection; raise CQ for missing entity |
| ALG-010 | User confirmation loop iteration 2 exhausted with unresolved entity conflict | S3 | Emit `alg.raised`; PM adjudicates; mark contested entity `[UNKNOWN]` |
| ALG-REV-SEC | Security gap detected: production node or service has no TLS configuration and no secret management — credentials potentially in plaintext | S2 | Emit `alg.raised`; notify CSCO; document gap in TA overview; do not attempt to fix code |

---

## Outputs

| Output | Path | Version | EventStore Event |
|---|---|---|---|
| Technology entity files (NOD, DEV, SSW, TSV, ART, NET, TFN, TEV, TIF) | `technology-repository/technology/<type>/<id>.md` | 0.1.0 | `artifact.created` per entity |
| ADR stubs | `technology-repository/decisions/ADR-<NNN>.md` | 0.1.0 | `artifact.created` per ADR |
| Technology connection files | `technology-repository/connections/archimate/<type>/<source>---<target>.md` | 0.1.0 | `artifact.created` per connection |
| Technology Architecture overview | `technology-repository/overview/ta-overview.md` | 0.1.0 | `artifact.baselined` |
| `_macros.puml` (regenerated) | `technology-repository/diagram-catalog/_macros.puml` | — | — |
| Handoff to SA (TA warm-start complete, cross-repo connections) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (security gaps, safety-relevant tech components) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PM (EP-G reconstruction assessment) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| CQ records for gaps and ADR rationales | `engagements/<id>/clarification-log/` | — | `cq.raised` per CQ |

---
skill-id: SwA-PHASE-D
agent: SwA
name: phase-d
display-name: Phase D — Technology Architecture
invoke-when: >
  Phase C gate has passed and AA and DA are both baselined at 1.0.0; Phase D Architecture
  Sprint starts and SwA has acknowledged the AA and DA handoffs.
trigger-phases: [D]
trigger-conditions:
  - gate.evaluated (from_phase=C, result=passed)
  - sprint.started (phase=D)
  - handoff.created (handoff-type=phase-D-input, to=software-architect)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D]
primary-outputs: [Technology Architecture, Technology Component Catalog, ADR Register, Infrastructure Diagram, Technology Gap Analysis]
complexity-class: complex
version: 1.0.0
---

# Skill: Phase D — Technology Architecture

**Agent:** Software Architect / Principal Engineer  
**Version:** 1.0.0  
**Phase:** D — Technology Architecture  
**Skill Type:** Architecture production  
**Framework References:** `agile-adm-cadence.md §6.5`, `raci-matrix.md §3.6`, `framework/artifact-schemas/technology-architecture.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `repository-conventions.md`

---

## Runtime Tooling Hint

Diagram and matrix conventions apply only when this skill explicitly produces or updates diagram artifacts; use `framework/diagram-conventions.md` as the source of truth.

Tool references in this skill are intent guidance; runtime APIs are bound in code.

- Discovery/filter/search/query: use `model_query_*` tools.
- Validation: use `model_verify_file` and `model_verify_all`.
- Deterministic entity/connection/diagram writing: use `model_create_entity`, `model_create_connection`, `model_create_diagram`, `model_create_matrix` with `dry_run` before writes.
- Frontmatter conditions remain intent-level and reusable; executable phase/dependency checks are orchestration responsibilities.
- Keep output contract strict; when runtime state conflicts with assumptions, stop and escalate via CQ/algedonic handling rather than soft-continuing.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Application Architecture (`AA`) | SwA (self-produced, Phase C) | **Baselined** (v1.0.0+) | Full artifact required — every APP-nnn must be mappable to a technology component. AA is now SwA-produced; no SA handoff required. SwA performs a consistency check (not a feasibility review) at Phase D start. |
| Data Architecture (`DA`) | SwA (self-produced, Phase C) | **Baselined** (v1.0.0+) | Every DOB-nnn classification level requires a storage technology decision. DA is SwA-produced. |
| Architecture Principles Register (`PR`) | Solution Architect | Baselined | Technology selections must not violate principles; overrides require principle-override ADR |
| Safety Constraint Overlay (`SCO`) — Phase C update | CSCO | Baselined | Technology choices affecting safety constraints must be cross-referenced; some choices may be blocked |
| Enterprise Standards Information Base (SIB) | `enterprise-repository/standards/` | Draft acceptable | Consult if available; absence does not block work |
| Sprint kickoff event | PM | `sprint.started` emitted | Do not begin work before PM emits this event |

**Self-produced artifacts:** AA and DA are produced by SwA in Phase C. At Phase D start, SwA reads their own baselined artifacts from `architecture-repository/model-entities/application/`. No handoff acknowledgement step is needed. If, for any reason, AA or DA are in draft state (v0.x.x), do not begin TA production — raise ALG-008 (S2) to PM.

---

## Knowledge Adequacy Check

### Required Knowledge

- AA Component Catalog (APP-nnn): every application component, its type, safety-relevant flag, and interface requirements
- DA Entity Catalog (DE-nnn): every data entity, its classification level, and owning application component
- Architecture Principles Register: all active principles, especially constraints on technology selections (e.g., open-source preference, cloud provider restrictions, data residency)
- SCO Phase C update: all technology-level safety constraints imposed by CSCO
- Enterprise SIB (if available): approved technologies, mandated platforms, prohibited products

### Known Unknowns

The following gaps are predictably present at Phase D entry and must be resolved via CQ before or during TA production:

1. **Deployment environment constraint**: Is this a cloud deployment, on-premises, hybrid, or edge? Which cloud provider(s) are in scope (if cloud)? Are there data residency requirements that constrain deployment region?
2. **Non-functional requirements (NFRs)**: What are the specific performance targets (throughput, latency, SLA)? What scale profile is expected (concurrent users, data volume, event rates)? Are these defined in the Requirements Register?
3. **Existing technology constraints**: Does the organisation have existing technology standards (database product, cloud provider, container orchestration) that must be respected? Is there an enterprise SIB entry that mandates or prohibits specific products?
4. **Security certification requirements**: Does the system require any formal security certification (ISO 27001, SOC 2, FedRAMP, FIPS)? Are there specific encryption standards required?
5. **Network and connectivity constraints**: Are there existing network topologies, VPN requirements, or connectivity constraints to on-premises systems?
6. **Operational model**: Will the system be operated by the client's internal team or a managed service provider? This affects tooling choices (observability stack, runbook automation).

### Clarification Triggers

Raise a CQ (`target: User`) if:
- Deployment environment type is not determinable from AV, BA, AA, DA, or Requirements Register
- NFR targets are absent from the Requirements Register and cannot be reasonably inferred from business context
- Security certification requirement is implied by domain (e.g., healthcare, finance) but not explicitly stated

Raise structured feedback to SA (`target: Solution Architect`) if:
- An APP-nnn component has ambiguous technology requirements that make mapping impossible
- An IFC-nnn interface has a protocol specification that cannot be realised by any known technology
- A DE-nnn classification level is missing, making storage technology selection impossible

Route to PM if:
- Cloud provider or on-premises constraint is a business/commercial decision beyond architecture authority
- Scope of deployment environments (Production only vs. full Staging/Development stack) is not resolved

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SwA", phase="D", artifact_type="technology-architecture")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

**Step 0.D — Model Entity Lookup** *(insert before Step 1)*

Before authoring technology diagrams, query the model registries:
1. Call `list_artifacts(artifact_type="application-component")` — extract APP-nnn IDs for all application components in scope from the SA engagement architecture-repository.
2. Call `list_artifacts(artifact_type="technology-node")`, `list_artifacts(artifact_type="technology-service")`, and `list_artifacts(artifact_type="artifact")` from the technology-repository — identify existing NOD-nnn, TSV-nnn, ARF-nnn entries.
3. Annotate working context: "Model registry: N application components (APP-nnn); M technology nodes (NOD-nnn) found relevant."

### Step 1 — Read and Validate Inputs

1.1 Read AA in full (not summary-only). Retrieve AA from canonical path. Confirm version is ≥ 1.0.0. Record all APP-nnn entries; note which are `safety-relevant: true`.

1.2 Read DA in full. Retrieve DA from canonical path. Confirm version is ≥ 1.0.0. Record all DE-nnn entries with their classification levels. Record all IFC-nnn entries from AA Interface Catalog.

1.3 Read Architecture Principles Register. Record all principles that constrain technology choices. Flag any principle that would block a technology category (e.g., "no vendor lock-in" may constrain proprietary managed services).

1.4 Read SCO Phase C update. Record all technology-level safety constraints. For each safety-relevant APP-nnn and DE-nnn, note any explicit technology restrictions.

1.5 Check enterprise SIB (`enterprise-repository/standards/`). If present, record mandated technologies, prohibited technologies, and recommended standards. Note SIB version.

1.6 Perform Knowledge Adequacy Check (§ above). Raise CQs for unresolvable gaps. If a blocking CQ is raised, produce a partial TA (Steps 2–4 where possible) and mark the affected sections with `pending-clarifications: [CQ-id]`.

**Revisit handling:** If `phase_visit_count > 1` (triggered by AA/DA revision or CSCO veto), read the `phase.return-triggered` event to identify `affected-artifacts`. Open only the identified sections of the existing TA for revision. Preserve all other baselined sections. Increment version minor number.

### Step 2 — Map Application and Data Components to Technology Candidates

2.1 For each APP-nnn in the AA Component Catalog, identify the technology component type(s) required to host or support it:
- Service → Runtime (compute platform: container, serverless, VM)
- Store → Storage (database, object storage, cache)
- Gateway → Network (API gateway, load balancer)
- UI → Runtime + Network (frontend hosting + CDN)
- Integration → Store or Network (message broker, event bus, adapter runtime)

2.2 For each DE-nnn in the DA Entity Catalog, map to a storage technology candidate based on classification level:
- Public / Internal → relational or document store options
- Confidential / Restricted → encrypted store with access control; explicit key management decision required
- Safety-Critical → immutable or append-only store with audit trail; CSCO constraint cross-reference required

2.3 Identify gaps: APP-nnn or DE-nnn entries that cannot be mapped to a clear technology candidate. Document as items for Technology Gap Analysis (Step 12) and raise CQs or structured feedback as appropriate.

2.4 Identify cross-cutting requirements from the AA Interface Catalog (IFC-nnn): authentication/authorisation, observability (logging, tracing, metrics), secrets management. These become mandatory technology component types regardless of specific APP mappings.

### Step 3 — Consult Enterprise SIB

3.1 If the enterprise SIB is available, check each candidate technology type against the SIB:
- If the SIB mandates a specific product: select it; record SIB reference in the ADR.
- If the SIB recommends a product: prefer it; record recommendation reference; may choose alternative with documented justification.
- If the SIB prohibits a product under consideration: eliminate it from selection; document in ADR under `Alternatives Considered`.

3.2 If no SIB is available, document this as an assumption in the TA header: "No enterprise SIB was available; technology selections are based on domain best practices and architecture principles."

### Step 4 — Author Technology Component Catalog

4.1 Assign a TC-nnn identifier to each selected technology component.

4.2 For each TC-nnn, populate the Technology Component Catalog entry per `technology-architecture.schema.md §3.2`:

| Component ID | Name | Type | Selected Product / Platform | Version Constraint | Realises App Component | Rationale (ADR ref) | Status |
|---|---|---|---|---|---|---|---|
| TC-001 | | Runtime / Platform / Store / Network / Security / Observability | Specific product name | ≥ x.y, < x+1.0 | APP-nnn | ADR-001 | Selected |

**Specificity requirement:** Every TC-nnn must have a `Selected Product / Platform` value that names a specific product (e.g., "PostgreSQL 16", "Amazon EKS 1.29+", "Redis 7.2"). Generic type names ("a relational database") are not acceptable and fail the quality gate.

4.3 Every TC-nnn with `Status: Selected` must have a corresponding ADR (see Step 5). Components evaluated but not selected have `Status: Evaluated` or `Status: Rejected` and appear in the relevant ADR's `Alternatives Considered` section.

**Diagram Step D — Class/ER Technology Domain Model**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="technology-node")` and `list_artifacts(artifact_type="technology-service")` for technology entities. Call `list_artifacts(artifact_type="application-component")` (SA engagement repo) for cross-reference APP-nnn entities. Use `search_artifacts` for data objects (DOB-nnn) that technology components store.
- **D2:** For each entity that will appear in the diagram, verify its `§display ###er` subsection exists. Add missing subsections via `write_artifact`; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.class-er")`. Call `generate_er_content(entity_ids)` and `generate_er_relations(connection_ids)` to produce PUML class blocks. Include required frontmatter comment block. Write to `technology-repository/diagram-catalog/diagrams/d-er-technology-domain-model-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate before proceeding.

*Note: SwA writes to `technology-repository/diagram-catalog/diagrams/`; SA integrates via `diagram.catalog-proposal` handoff at phase transition.*

### Step 5 — Author Architecture Decision Records (ADR Register)

5.1 For each significant technology decision, produce one ADR using the format in `technology-architecture.schema.md §3.6`.

**Mandatory ADR types** (one ADR for each of the following, if in scope):

| Decision Type | Notes |
|---|---|
| Primary compute/runtime platform | Container orchestration, serverless, PaaS, VM |
| Primary data store per classification level | One ADR per DA classification level that requires a distinct storage choice |
| Authentication and authorisation approach | Identity provider, token format, AuthZ model |
| Network boundary and ingress strategy | API gateway, load balancer, WAF, zero-trust vs. perimeter |
| Observability stack | Metrics, logging, tracing, alerting — treated as a unified decision or separate if different products |
| Any decision overriding or constraining an Architecture Principle | Flagged with `principle-override: true` in ADR header |
| Any decision with Safety-Critical or safety-relevant constraints | Must reference SCO section; must be reviewed by CSCO before `Status: Accepted` |

5.2 ADR Quality Standard: every ADR must include:
- **Context**: the requirement or constraint driving the decision
- **Decision**: the specific product/pattern chosen (named, versioned)
- **Rationale**: why this option over the alternatives, with explicit links to PR constraints, AA requirements, DA classification constraints, or SCO safety constraints
- **Consequences**: what becomes easier, harder, or riskier
- **Alternatives Considered**: at least two alternatives evaluated and the reason for rejection

5.3 ADRs start at `Status: Proposed`. The ADR for a safety-relevant decision must advance to `Status: Accepted` only after CSCO sign-off. All other ADRs advance to `Status: Accepted` when the SwA finalises the Phase D artifact.

5.4 ADR enforcement: **no TC-nnn may be `Status: Selected` in the catalog without a corresponding `Status: Accepted` (or `Proposed` awaiting CSCO review) ADR.** This is a hard quality gate.

### Step 6 — Build Technology/Application Matrix

6.1 Produce a matrix cross-referencing all TC-nnn components (columns) against all APP-nnn application components (rows) per `technology-architecture.schema.md §3.3`.

6.1a Implementation detail: build this as a matrix artifact via `model_create_matrix` (`diagram-catalog/diagrams/*.md`) rather than a dense node-link diagram. Keep APP/TC IDs canonical and auto-link cells to entity files.

6.2 Use notation: ● = primary host/support; ○ = auxiliary support; — = no relationship.

6.3 Verify completeness: every APP-nnn must appear in at least one row with a ● or ○ entry. Any APP-nnn with no TC relationship is a Gap Analysis item.

### Step 7 — Author Infrastructure Diagram

7.1 Produce an ArchiMate **Technology Viewpoint** diagram showing:
- All TC-nnn components from the catalog
- Hosting relationships between components (what runs on what)
- Network connections between components, typed: synchronous / async / managed service
- Deployment environments: Production (mandatory); Staging (mandatory); Development (mandatory)
- Trust boundaries between zones

7.2 The diagram is an authoritative artifact — it must be consistent with the Technology Component Catalog and Deployment Topology (Step 8). Inconsistencies between diagram and catalog are a quality gate failure.

7.3 Write diagram as ArchiMate text notation (ArchiML or equivalent textual ArchiMate representation) to the canonical path. Do not produce raster image descriptions — produce the notation that can be rendered.

### Step 8 — Author Deployment Topology

8.1 Produce an ArchiMate **Technology Usage Viewpoint** (or Physical Viewpoint for on-premises components) showing how APP-nnn application components map to TC-nnn technology components across environments.

8.2 Minimum environments required: Production, Staging, Development.

8.3 For each environment, record: deployment zone, TC-nnn components present, APP-nnn components hosted, connectivity type (internal / external / isolated).

8.4 Note any environment-specific configuration differences (e.g., Production uses managed RDS; Development uses local PostgreSQL container). These differences are inputs to DevOps environment provisioning.

**Diagram Step D — ArchiMate Technology Architecture Diagram**

Execute D1–D4 per `framework/diagram-conventions.md §5`:
- **D1:** Call `list_artifacts(artifact_type="technology-node")`, `list_artifacts(artifact_type="technology-service")`, and `list_artifacts(artifact_type="artifact")` to identify technology entities. Call `list_artifacts(artifact_type="application-component")` (SA engagement repo) for APP-nnn assignment relationships. Use `search_artifacts` to locate any enterprise technology standard entities that should appear.
- **D2:** For each entity that will appear in the diagram, verify its `§display ###archimate` subsection exists. Add missing subsections via `write_artifact`; run `regenerate_macros()`.
- **D3:** Load template via `read_framework_doc("framework/diagram-conventions.md §7.archimate-technology")`. Author the technology architecture diagram with entity artifact-ids as PUML aliases; include application component assignments. Include required frontmatter comment block. Write to `technology-repository/diagram-catalog/diagrams/d-archimate-technology-v1.puml` via `write_artifact`.
- **D4:** Call `validate_diagram`; fix errors; re-validate before proceeding.

*Note: SwA writes to `technology-repository/diagram-catalog/diagrams/`; SA integrates via `diagram.catalog-proposal` handoff at phase transition.*

### Step 9 — Author Technology Standards Catalog

9.1 Enumerate all standards, protocols, and conventions mandated by this Technology Architecture per `technology-architecture.schema.md §3.7`.

9.2 Include:
- API design standards (REST, gRPC, OpenAPI version)
- Data format standards (JSON Schema, Protobuf, Avro)
- Security standards (TLS version, cipher suites, key management)
- Container standards (base image policy, image signing)
- Coding and dependency standards (language runtime version, dependency pinning policy)
- Any regulatory or industry standards applicable to the technology domain

9.3 Each standard entry: Standard ID (STD-nnn), Standard Name, Type (Industry / Internal / Regulatory), Source, Applies To (TC-nnn or domain), Mandatory / Recommended.

### Step 10 — Author Technology Lifecycle Analysis

10.1 For every TC-nnn in the catalog, record current version, end-of-support date (if determinable from vendor documentation), upgrade path, and risk classification (Low / Medium / High).

10.2 Risk classification criteria:
- **High**: End-of-support within 12 months, or product is deprecated by vendor, or no clear upgrade path exists
- **Medium**: End-of-support within 24 months, or product is in maintenance-only mode
- **Low**: Actively maintained; long-term support version; clear upgrade path

10.3 For every TC-nnn with **High** lifecycle risk: produce a mitigation ADR. The mitigation ADR must specify: the risk, the timeline trigger, the mitigation strategy (upgrade path, product replacement, or vendor engagement), and the decision owner.

10.4 CSCO notification: if any High-risk component is also safety-relevant, notify CSCO immediately. Do not wait for the CSCO technology-level safety review step.

### Step 11 — Cross-Reference Safety Constraint Overlay

11.1 For each TC-nnn that is safety-relevant (i.e., hosts an APP-nnn or stores a DE-nnn with `safety-relevant: true`), produce an SCO cross-reference entry per `technology-architecture.schema.md §3.9`.

11.2 For each entry, identify: which SCO section governs this component; what the technology-level constraint is (e.g., "this component must not be accessible from public internet per SCO §3.2"); and what the implementation constraint is for the DevOps/Platform Engineer.

11.3 If a technology choice conflicts with an SCO constraint: raise ALG-001 (S1 — safety constraint violation) immediately. Halt work on the affected TC decision. Notify CSCO and PM concurrently. Do not baseline the TA until the conflict is resolved.

### Step 12 — Author Technology Gap Analysis

12.1 Produce the Technology Gap Analysis per `technology-architecture.schema.md §3.10`.

12.2 Domains to assess: Runtime, Storage, Network, Security, Observability. Add domains as needed (e.g., Edge, CI/CD platform, Secret management).

12.3 For each domain: document baseline state (what exists today, or "greenfield" if none); target state (what the TA specifies); the gap (delta); and how the gap will be resolved in Phase E/F.

12.4 Gaps that cannot be resolved with known implementation candidates must be flagged as risks for the PM Risk Register.

### Step 13 — Baseline, Handoff, and Gate Vote

13.1 Assemble all TA sub-components into the TA deliverable document at canonical path: `technology-repository/technology-architecture/TA-<nnn>-1.0.0.md`.

13.2 Complete the artifact summary header (per `agile-adm-cadence.md §10.2`):
```yaml
artifact-type: technology-architecture
artifact-id: TA-nnn
version: 1.0.0
phase: D
status: baselined
owner-agent: software-architect
produced-in: <sprint-id>
path: technology-repository/technology-architecture/TA-nnn-1.0.0.md
depends-on: [AA-nnn, DA-nnn, PR-nnn, SCO-nnn]
consumed-by: [DevOps, IP, AC]
safety-relevant: <true|false>
csco-sign-off: true
pm-sign-off: false
```

13.3 Run quality gate self-check before baseline:
- [ ] Every APP-nnn mapped to at least one TC-nnn
- [ ] Every DE-nnn classification level has a storage technology decision with ADR
- [ ] All mandatory ADR types present
- [ ] No TC-nnn without an ADR
- [ ] No ADR without `Alternatives Considered`
- [ ] Technology lifecycle risks assessed; High-risk components have mitigation ADRs
- [ ] SCO cross-reference complete for all safety-relevant components
- [ ] Technology/Application Matrix complete and consistent with catalog
- [ ] Infrastructure Diagram consistent with catalog and topology
- [ ] All open CQs resolved or documented as non-blocking assumptions

13.4 Emit `artifact.baselined` event for TA.

13.5 Create handoffs:
- **To DevOps/Platform Engineer**: TA is ready for environment provisioning planning. Emit `handoff.created` with payload referencing TA path and version.
- **To CSCO**: TA technology-level safety review requested. Include SCO cross-reference section path. Emit `handoff.created`.
- **To SA**: TA is ready for consistency validation against AA/DA. Emit `handoff.created`.

13.6 Cast gate vote for D→E: emit `gate.vote_cast` with `gate: D-E`, `vote: approved` (or `vote: blocked` with specific blocking condition if quality gate self-check fails). Do not cast an approved vote with unresolved quality gate failures.

---

## Feedback Loop

### AA/DA Mapping Gap Loop (SwA ↔ SA)

**Purpose:** Resolve application or data component ambiguities that block technology mapping.

- **Iteration 1**: SwA raises structured feedback to SA via handoff log entry specifying the ambiguous APP-nnn or DE-nnn entry and the specific information needed.
- **Iteration 2**: SA revises AA or DA and re-issues. SwA acknowledges updated handoff and proceeds.
- **Termination**: Ambiguity resolved; SwA proceeds with TA production.
- **Maximum iterations**: 2. If SA's iteration-2 revision still does not resolve the ambiguity, SwA escalates to PM via ALG-010 (S3 — inter-agent deadlock). PM adjudicates within the current sprint.
- **Escalation path**: ALG-010 → PM adjudicates → if PM cannot resolve, ALG-005 (TC — timeline collapse, S2) → PM restructures sprint.

### CSCO Safety Review Loop (SwA ↔ CSCO)

**Purpose:** Resolve safety constraints that block or modify technology component selections.

- **Iteration 1**: CSCO reviews SwA's technology-level SCO cross-reference; raises specific objections (technology choice violates SCO constraint). SwA revises affected TC decisions and ADRs.
- **Iteration 2**: CSCO re-reviews revised decisions. SwA incorporates CSCO feedback.
- **Termination**: CSCO sign-off obtained; ADRs for safety-relevant decisions advanced to `Status: Accepted`.
- **Maximum iterations**: 2. If CSCO's iteration-2 review still blocks a technology decision, the blocking condition is escalated to PM via ALG-004 (S2) with CSCO sign-off overdue flag. If CSCO is unavailable, halt safety-relevant TC decisions and raise ALG-002 (S1).
- **Escalation path**: ALG-004 → PM escalates to CSCO with deadline; if CSCO unavailable ALG-002 → halt; if CSCO veto cannot be resolved technically, ALG-001 → user and PM via CSCO channel.

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

| ID | Condition | Severity | Action |
|---|---|---|---|
| ALG-001 | Technology choice would violate an SCO safety constraint | S1 | Halt affected TC decision immediately; emit to CSCO and PM concurrently; do not baseline TA until resolved |
| ALG-002 | CSCO is unavailable and a safety-relevant technology decision requires CSCO sign-off before the D→E gate | S1 | Halt safety-relevant TC decisions; emit to PM; document which TC-nnn and ADR-nnn are blocked |
| ALG-004 | CSCO safety review has not completed; D→E gate is being evaluated with outstanding CSCO sign-off | S2 | Emit to PM; PM escalates to CSCO with deadline; gate cannot pass until CSCO sign-off obtained |
| ALG-005 | Two consecutive gate extensions at D→E due to unresolvable technology decision conflicts | S2 | Emit to PM for scope reassessment; document root cause |
| ALG-007 | SwA detects it has written to a path outside `technology-repository/` | S1 | Emit to PM immediately; halt further writes; await PM instruction |
| ALG-008 | AA or DA in draft state (v0.x.x) presented as authoritative input to Phase D | S2 | Emit to PM; do not begin TA production; request baselined artifacts from SA |
| ALG-010 | Two-iteration AA/DA mapping gap loop exhausted without resolution | S3 | Emit to PM; await PM adjudication; document both parties' positions in the signal record |
| ALG-011 | SwA discovers internal inconsistency between baselined AA and DA (e.g., APP-nnn references a DE-nnn not in DA catalog) | S3 | Emit to SA (immediate revision request) and PM; halt dependent TA sections; resume on SA resolution |
| ALG-017 | Safety-domain CQ is unanswered and a technology choice with safety implications cannot proceed safely on assumption | S1 | Halt affected TA sections; emit to user (via PM) and CSCO concurrently |

---

## Outputs

| Output | Path | Version at Baseline | EventStore Event |
|---|---|---|---|
| Technology Architecture (`TA`) — full deliverable | `technology-repository/technology-architecture/TA-<nnn>-1.0.0.md` | 1.0.0 | `artifact.baselined` |
| Technology Component Catalog | Embedded in TA §3.2; may also be extracted to `technology-repository/technology-component-catalog/TC-catalog-<nnn>.md` | — | — |
| ADR Register | `technology-repository/adr-register/ADR-<nnn>-1.0.0.md` (one file per ADR, or register document) | 1.0.0 | `artifact.baselined` |
| Technology/Application Matrix | Embedded in TA §3.3; extractable to `technology-repository/technology-application-matrix/TAM-<nnn>.md` | — | — |
| Infrastructure Diagram | `technology-repository/infrastructure-diagrams/INFRA-<nnn>-1.0.0.md` | 1.0.0 | — |
| Technology Standards Catalog | Embedded in TA §3.7 | — | — |
| Technology Lifecycle Analysis | Embedded in TA §3.8 | — | — |
| Technology Gap Analysis | `technology-repository/gap-analysis/TGA-<nnn>-0.1.0.md` (draft; baselined in Phase E) | 0.1.0 draft | — |
| Handoff to DevOps (TA) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to CSCO (TA safety review) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to SA (TA consistency check) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| D→E Gate vote | EventStore | — | `gate.vote_cast` |

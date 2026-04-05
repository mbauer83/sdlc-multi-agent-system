---
skill-id: SA-REV-BA
agent: SA
name: reverse-architecture-ba
display-name: Reverse Architecture — Phase B (Business Layer Discovery)
invoke-when: >
  EP-G warm-start; motivation/strategy entity files exist (from SA-REV-PRELIM-A or prior warm-start)
  but no business-layer entities (ACT, ROL, BPR, BFN, BSV, BOB, BEV, BCO, BIF, PRD) exist; or
  PM emits handoff (handoff_type=ep-g-sa-prelim-a-complete) and SA-REV-BA has not yet run.
trigger-phases: [B]
trigger-conditions:
  - handoff.created (from PM, handoff_type=ep-g-sa-prelim-a-complete)
  - handoff.created (from PM, handoff_type=ep-g-sa-ba-discovery)
entry-points: [EP-G, EP-B, EP-H]
primary-outputs:
  - Business entity files (ACT, ROL, BPR, BFN, BSV, BOB, BEV, BCO, BIF, PRD)
  - Strategy capability entity updates (CAP detailed properties)
  - Value stream entity updates (VS step sequences)
  - ArchiMate connection files (assignment, triggering, realization, composition, serving)
  - Business Architecture overview document
complexity-class: complex
version: 1.0.0
---

# Skill: Reverse Architecture — Phase B (Business Layer Discovery)

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** B — Business Architecture  
**Skill Type:** Warm-start — reverse architecture discovery  
**Framework References:** `sdlc-entry-points.md §4.6`, `framework/artifact-registry-design.md §2.1`, `framework/artifact-schemas/entity-conventions.md`, `framework/artifact-schemas/business-architecture.schema.md`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Runtime Tooling Hint

This skill's tool references are intent-level; runtime signatures come from code wiring.

- Discover/query/filter/search: use `model_query_*` family (or runtime aliases).
- Validate files/repo state: use `model_verify_file` / `model_verify_all`.
- Build model entities/connections/diagrams deterministically: use `model_create_entity`, `model_create_connection`, and `model_create_diagram` (`dry_run` first).
- Frontmatter trigger fields are intent hints; executable EP/phase gating is orchestration-owned.
- Preserve strict reverse-architecture outputs and evidence annotations; use CQ/algedonic flows when runtime state is insufficient.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Motivation/strategy entities from SA-REV-PRELIM-A | `list_artifacts(directory="architecture-repository/motivation/")` | At least STK ×2, DRV ×2, CAP ×3 at version 0.1.0 | Hard prerequisite — if absent, invoke SA-REV-PRELIM-A first |
| Architecture Vision overview | `architecture-repository/overview/architecture-vision.md` | Version 0.1.0 draft | Provides capability clusters for process decomposition |
| Codebase and documentation scan | `scan_target_repo()` per registered repo | Clone available | SA looks for service boundaries, domain packages, API controllers, DB schemas, event definitions |
| User-provided business process documents | User (via PM CQ loop) | Any state | Runbooks, swimlane diagrams, process flow docs, domain model docs, user stories |
| External source artifacts | Configured adapters | Optional | Confluence pages, Jira epics, SharePoint process docs |
| Safety Constraint Overlay (Phase A SCO, if CSCO produced one) | `architecture-repository/safety-repository/` | Optional — if present, read before flagging safety-relevant processes | CSCO may have produced an initial safety scan from SA-REV-PRELIM-A handoff |

---

## Knowledge Adequacy Check

### Required Knowledge

- **Business process boundaries:** What business activities does this system automate or support? Can be inferred from service names, API route naming conventions, controller class names, and domain package structure.
- **Actor and role identification:** Who initiates business processes? Who are the end-users, operators, administrators? Can be inferred from authentication layers, role-based access control configs, user table schemas.
- **Service and function taxonomy:** What business services are offered? What business functions are performed? Inferred from API resource names, microservice names, module names, use-case class names.
- **Business objects:** What are the core domain entities (objects that persist across processes)? Inferred from ORM models, database tables, GraphQL types, Pydantic/TypeScript schemas.
- **Value stream steps:** What is the ordered sequence of activities that delivers value? Inferred from process flow docs, event-driven service chains, CI/CD pipeline stages.

### Known Unknowns

| Unknown | Blocking | CQ Target | Entity Type Affected |
|---|---|---|---|
| Intentional process boundaries vs. accidental implementation boundaries | Partially — SA infers conservatively; flags ambiguous cases | User or PO | BPR-nnn |
| Hidden or manual off-system business processes | No — SA focuses on what is visible; flags gaps in BA overview | User | BPR-nnn, BOB-nnn |
| Actor role names (business titles vs. technical user types) | No — SA uses technical names from code; user can map to business titles | User | ACT-nnn, ROL-nnn |
| Process ownership (which team owns which process) | No — SA infers from CODEOWNERS, team names in commit history | User | BPR-nnn domain field |
| Safety-relevant processes not obvious from code | Partially — SA flags any process touching external I/O, auth, data residency | CSCO | BPR-nnn `safety-relevant` field |

### Clarification Triggers

1. **No identifiable domain structure:** The codebase has no discernible domain/service decomposition (single monolith with no separation of concerns). SA raises a CQ: "Can you describe the main business activities this system performs? (A bulleted list of 5–10 activities is sufficient.)"
2. **Ambiguous actor hierarchy:** The system has overlapping roles (e.g., `admin`, `superadmin`, `owner`, `manager`) whose business responsibilities cannot be distinguished from code alone. SA raises a bounded CQ listing the roles and asking for a one-line description of each.
3. **No process trigger or outcome identifiable for a major service:** A significant service module (>5% of codebase lines) cannot be mapped to any business process trigger or outcome. Non-blocking; SA creates a placeholder BPR-nnn with `[UNKNOWN — CQ pending]` fields.
4. **Discovered process involves user data, payment, or health information:** SA cannot determine whether the process is safety-relevant without domain context. Blocking for `safety-relevant` flag on that BPR-nnn. CQ to User + concurrent notification to CSCO.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="B", artifact_type="business-architecture")` and `query_learnings(agent="SA", phase="B", artifact_type="business-entity")`. Prepend returned corrections to working context. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan

**Layer 1 — Engagement state:** Load all existing motivation/strategy entities via ModelRegistry (`list_artifacts`). Load Architecture Vision overview. Note all CAP-nnn capability clusters — these drive the process decomposition in Step 2.

**Layer 2 — Enterprise repository:** Query `list_artifacts(directory="enterprise-repository/business/")`. Note reusable enterprise actors, standard business services, or canonical process templates that apply.

**Layer 3 — External sources:** Query configured adapters for: "business process", "domain model", "service catalogue", "user roles", "actor", "workflow". Record all matches with `[source: <adapter-id>]`.

**Layer 4 — Target repository structured scan:** For each registered target repo, scan systematically:

*Codebase analysis — domain decomposition:*
- Top-level directory structure: identify `src/`, `app/`, `services/`, `modules/`, `domain/`, `bounded-context/` patterns
- Package/module names: each major package is a candidate BFN-nnn (Business Function) or BPR-nnn anchor
- Controller/handler classes: identify API entry points and their HTTP verbs → candidate BSV-nnn (Business Services)
- Service class names: `*Service`, `*UseCase`, `*Handler`, `*Interactor` → candidate BFN-nnn or BPR-nnn
- Repository/DAO class names: identify persisted domain entities → candidate BOB-nnn (Business Objects)

*Actor/role discovery:*
- Authentication config files: `roles`, `permissions`, `scopes` → candidate ACT-nnn, ROL-nnn
- RBAC or policy files: role definitions with capability statements
- User/account database schemas: `user_type`, `role`, `account_type` columns
- API authorization decorators/middleware: `@requires_role`, `@permission_required`

*Event and integration discovery:*
- Message queue / event bus configurations: topics, queues, event names → candidate BEV-nnn (Business Events)
- Webhook definitions, cron job names → business triggers
- External system integrations → candidate BCO-nnn (Collaboration) or BIF-nnn (Business Interface)

*Documentation scan:*
- `docs/`, `wiki/`, `README.md` files: extract named processes, workflows, actor descriptions
- OpenAPI/Swagger specs: `operationId`, `summary`, `tags` → candidate BSV-nnn, BPR-nnn
- Database migration files: table creation sequence reveals domain object lifecycle

**Layer 5 — EventStore:** Check for any `cq.answered` events at phase B with business domain answers.

Annotate each discovered item with `[inferred: target-repo:<id>:<evidence-type>]` where evidence-type is one of: `package-name`, `class-name`, `api-route`, `db-schema`, `config`, `doc-text`, `event-name`.

---

### Step 1 — User Context Query

Compose a **single batched context request** covering what the discovery scan could not resolve. Maximum 5 targeted questions. Include:
- A brief summary of what SA found in the codebase (list discovered service/module names, actor roles, main objects).
- Specific questions, e.g.:
  - "I found modules [X, Y, Z]. Do these correspond to separate business processes, or are they implementation subdivisions of a single process?"
  - "I identified roles [A, B, C] in the auth config. Can you describe what each role is allowed to do from a business perspective?"
  - "Are there important off-system manual processes that this software supports but does not automate? If so, please describe them briefly."
  - "Please share any process maps, swimlane diagrams, or workflow documentation you have."
  - "Which of the following processes involve user personal data, financial transactions, or safety-critical operations: [list]?"

After receiving user response, integrate answers and any referenced documents into working context.

---

### Step 2 — Business Entity Inference

Using the capability clusters from AV overview (CAP-nnn entities) as the organising skeleton, map discovered evidence to business entities:

**For each CAP-nnn capability cluster:**
1. Identify which codebase modules/services realize it → candidate BFN-nnn or BPR-nnn
2. Identify which API endpoints or business services expose it → candidate BSV-nnn
3. Identify which actors invoke it → candidate ACT-nnn with ROL-nnn assignments
4. Identify which business objects it operates on → candidate BOB-nnn

**Entity draft rules:**
- One BPR-nnn per identifiable business process (not per function or class). A process has a trigger, steps, and an outcome.
- One BOB-nnn per persistent domain entity (database table / aggregate root). Do not create a BOB for every DTO or view model.
- One BSV-nnn per externally-visible business service offering (not per API endpoint). Group related API operations under one service if they serve the same business purpose.
- One ACT-nnn per distinct user type (not per role). Role assignments are captured in ROL-nnn and ACT-ROL connections.
- BEV-nnn for events that trigger or result from business processes (not for internal technical events).

Assign provisional IDs continuing from the highest existing ID per prefix. Annotate all inferred fields.

---

### Step 3 — User Confirmation Loop

Present the proposed business entity catalogue to the user for validation before writing files:

1. Group entities by capability cluster for readability.
2. For each entity: `[id] [type] — [name] — key fields — source annotations`
3. Highlight any entities where the business process trigger/outcome is `[UNKNOWN]`.
4. Ask the user to: (a) confirm, (b) correct misidentified entities, (c) supply missing triggers/outcomes, (d) flag any safety-relevant processes SA has not already flagged.

**Iteration 1:** User reviews and responds. SA incorporates corrections.  
**Iteration 2:** Present revised set if structural changes occurred (process redefined, entity removed, type changed). Skip if only additions or minor field corrections.  
**Max iterations:** 2. Proceed after iteration 2; retain unresolved items as `[UNKNOWN]`.

---

### Step 4 — Write Business Entity Files

For each confirmed entity, call `write_artifact` at the correct ERP path:

| Entity type | Path |
|---|---|
| ACT | `architecture-repository/business/actors/<id>.md` |
| ROL | `architecture-repository/business/roles/<id>.md` |
| BPR | `architecture-repository/business/processes/<id>.md` |
| BFN | `architecture-repository/business/functions/<id>.md` |
| BSV | `architecture-repository/business/services/<id>.md` |
| BEV | `architecture-repository/business/events/<id>.md` |
| BOB | `architecture-repository/business/objects/<id>.md` |
| BIF | `architecture-repository/business/interfaces/<id>.md` |
| BCO | `architecture-repository/business/collaborations/<id>.md` |
| PRD | `architecture-repository/business/products/<id>.md` |
| CTR | `architecture-repository/business/contracts/<id>.md` |

Entity frontmatter: `version: 0.1.0`, `status: draft`, `phase-produced: B`, `owner-agent: SA`, `produced-by-skill: SA-REV-BA`, `reconstruction: true`.

`§content` section includes: properties table for the entity type (per `entity-conventions.md §3`), narrative description, `[inferred]` / `[UNKNOWN]` annotations.

`§display ###archimate` subsection for entities that will appear in ArchiMate Business Layer diagrams.

For all safety-relevant processes (`BPR-nnn` where `safety-relevant: true`): add a `## Safety Notes` subsection in `§content` describing the safety concern.

After writing all entity files, call `regenerate_macros(repo_path="architecture-repository/")`.

---

### Step 5 — Write Business Connection Files

Infer and write typed ArchiMate connection files. Priority order:

1. **ACT → ROL assignment** (`connections/archimate/assignment/`): each actor assigned to their role(s)
2. **ROL → BPR assignment** (`connections/archimate/assignment/`): role assigned to processes they perform
3. **BPR → BPR triggering** (`connections/archimate/triggering/`): sequential process chains
4. **BPR → BOB access** (`connections/archimate/access/`): process creates/reads/updates/destroys object
5. **CAP → BPR realization** (`connections/archimate/realization/`): process realises a capability
6. **BSV → BPR realization** (`connections/archimate/realization/`): process provides a service
7. **VS → BPR composition** (`connections/archimate/composition/`): value stream step realised by process
8. **BFN → BPR composition** (`connections/archimate/composition/`): function composed of processes
9. **BEV → BPR triggering** (`connections/archimate/triggering/`): event triggers process
10. **BCO → ACT aggregation** (`connections/archimate/aggregation/`): collaboration groups actors

Only write connections where both source and target entity files exist in ModelRegistry.

---

### Step 6 — Produce Business Architecture Overview Document

Author `architecture-repository/overview/ba-overview.md` as a repository-content artifact:

Sections:
1. **Reconstruction Summary** — discovery methods used, evidence quality, entity count by type
2. **Capability-to-Process Map** — for each CAP-nnn: list realising BPR-nnn IDs
3. **Actor-Role Summary** — for each ACT-nnn: role assignments, primary processes
4. **Value Stream Walkthrough** — for each VS-nnn: ordered BPR-nnn sequence
5. **Safety-Relevant Process Register** — list of BPR-nnn with `safety-relevant: true`; CQs pending on classification
6. **Assumptions and Open CQs** — all `[inferred]` fields retained as assumptions; open CQ-IDs
7. **Reconstruction Confidence** — HIGH / MEDIUM / LOW with rationale

Frontmatter: `artifact-type: domain-overview`, `domain: business`, `version: 0.1.0`, `status: draft`, `reconstruction: true`, `entry-point: EP-G`, `produced-by-skill: SA-REV-BA`.

---

### Step 7 — Safety Handoff and CQ Emission

1. Collect all BPR-nnn with `safety-relevant: true` or `[UNKNOWN — safety classification pending]`.
2. Create handoff to CSCO: `handoff-type: ep-g-ba-safety-processes`. Payload: list of safety-relevant process IDs, confidence level.
3. Raise formal CQs for all `[UNKNOWN — CQ pending]` fields via PM.
4. Create handoff to PM: `handoff-type: ep-g-sa-ba-complete`. Payload: entity count, open CQ count, safety process count, reconstruction confidence.

---

## Feedback Loop

### User Confirmation Loop (Business Process Accuracy)

- **Iteration 1:** SA presents entity catalogue (Step 3). User provides corrections.
- **Iteration 2:** SA presents revised set if structural changes. User confirms.
- **Max iterations:** 2.
- **Escalation:** If user's Iteration 2 corrections contradict Iteration 1 answers and the conflict cannot be self-resolved, raise `ALG-010` to PM. PM adjudicates. Contested entities retained as `[UNKNOWN]`.

### CSCO Safety Flag Loop

- **Iteration 1:** SA handoff to CSCO (Step 7). CSCO reviews BPR safety flags and may add or reclassify.
- **Iteration 2:** SA updates `safety-relevant` flags per CSCO guidance. CSCO confirms.
- **Max iterations:** 2. If unresolved, raise `ALG-REV-001`.

### Personality-Aware Conflict Engagement

SA is an **Integrator** operating in discovery mode. Primary tension: the codebase and business reality may diverge significantly — code may reflect accidental architecture, not intentional business design. SA's stance: separate business intent from implementation detail explicitly. When the codebase contradicts user-stated business intent, surface the contradiction as an explicit observation, not a correction: "The codebase appears to implement [X], but you described the business process as [Y]. Are these the same, or is the implementation diverging from intent?" Do not force business entities to match implementation modules 1:1.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 correction changes entity type or deletes an entity entirely | S2 |
| `algedonic` | Any ALG raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised for info present in codebase scan results SA had already collected | S2 |
| `confidence-mismatch` | Downstream SA-REV skill (application/data) finds business entities that should have been discovered here | S2 |

On trigger: call `record_learning()` with `artifact-type="business-entity"`, error-type per `framework/learning-protocol.md §4`, correction ≤3 sentences. Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-REV-001 | A business process clearly involves safety-critical operations (e.g., direct hardware control, life-safety data) and safety classification CQ has not been answered after 48 hours | S1 | Halt writing of affected BPR-nnn; emit `alg.raised`; escalate to CSCO and PM |
| ALG-001 | Discovered process specification explicitly violates a constraint in current SCO (Phase A if available) | S1 | Halt; emit `alg.raised`; notify CSCO; do not write entity until resolved |
| ALG-010 | User confirmation loop iteration 2 exhausted with unresolved entity conflict | S3 | Emit `alg.raised`; PM adjudicates; mark contested entity `[UNKNOWN]` |
| ALG-C03 | `write_artifact` fails: connection references non-existent entity in ModelRegistry | S2 | Do not write connection; raise CQ for missing entity; continue with other connections |
| ALG-008 | Application-layer reverse architecture skill (not yet authored) begins consuming BPR entities before BA warm-start confidence is assessed as MEDIUM or higher | S2 | Emit `alg.raised`; PM holds application-layer reconstruction |

---

## Outputs

| Output | Path | Version | EventStore Event |
|---|---|---|---|
| Business entity files (ACT, ROL, BPR, BFN, BSV, BEV, BOB, BIF, BCO, PRD) | `architecture-repository/business/<type>/<id>.md` | 0.1.0 | `artifact.created` per entity |
| Updated strategy entity files (CAP detailed, VS step sequences) | `architecture-repository/strategy/<type>/<id>.md` | 0.2.0 | `artifact.updated` per entity |
| ArchiMate connection files | `architecture-repository/connections/archimate/<type>/<source>---<target>.md` | 0.1.0 | `artifact.created` per connection |
| Business Architecture overview | `architecture-repository/overview/ba-overview.md` | 0.1.0 | `artifact.baselined` |
| `_macros.puml` (regenerated) | `architecture-repository/diagram-catalog/_macros.puml` | — | — |
| Handoff to CSCO (safety process list) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PM (Phase B reconstruction complete) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| CQ records for remaining gaps | `engagements/<id>/clarification-log/` | — | `cq.raised` per CQ |

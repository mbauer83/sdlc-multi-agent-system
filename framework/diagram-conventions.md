---
doc-id: diagram-conventions
version: 2.3.0
status: Approved — Stage 4.9f
governs: All diagram production across all agent roles
---

# Diagram Conventions

Specifies the production, rendering, and maintenance of PlantUML (PUML) diagrams. Diagrams are **views over the model**: they select and compose entities and connections from the architecture/technology repositories and render them according to the `§display` sections in those files. No separate element catalog exists — the model IS the catalog.

**Tooling boundary:** This document governs diagram behavior and workflow. Concrete callable tool signatures are runtime-bound by code (LangGraph + PydanticAI registration). For model MCP workflows, prefer: `model_query_*` for discovery/search/filter/query, `model_verify_*` for validation, and `model_create_diagram` (plus `model_create_entity` / `model_create_connection` when the model must be extended). Legacy names in skills are intent-level aliases.

---

## 0. Diagram Scoping and Viewpoint Composition

Every diagram is a view over the model for one stakeholder question.

Before authoring, confirm:
1. Audience and decision question.
2. Phase/layer boundary (Phase B = business, Phase C = application; cross-layer only when needed).
3. Scope size (if readability fails, split).

### 0.1 Diagram type roles and viewpoints

Use diagram families as complementary views:
- ArchiMate: structure and relationships.
- ER: data fields and cardinalities.
- Activity/BPMN: process flow.
- Sequence: runtime interaction scenario.
- Use-case: stakeholder interaction intent.

### 0.2 Scoping rules

- Avoid "everything-in-one" diagrams.
- Avoid isolated single-node diagrams without meaningful relations.
- Prefer 1-hop context around in-scope entities.
- If readability degrades around ~30 elements, split into focused diagrams.

### 0.2.1 Dense-Edge Decomposition Rule (mandatory)

After one layout pass, if congestion remains:
1. Split into 2-4 thematic diagrams.
2. Separate horizontal progression from vertical governance links when useful.
3. Add a matrix companion artifact for full many-to-many coverage.
4. Reference that matrix artifact-id in each slice's `purpose`.

### 0.3 Diagram output modes: update vs. new diagram vs. target/delta

Use this rule:
1. Check existing diagrams via `list_artifacts` and `search_artifacts`.
2. Same viewpoint exists: update baseline and bump version.
3. Work-package delta needed: add target/delta diagram alongside baseline.
4. No matching viewpoint: create new diagram.

Lifecycle rules:
- `deprecated` is first-class status (not immediate deletion).
- Physical deletion only after dependent diagrams/connections are updated.
- All entity/connection/diagram mutations must go through `write_artifact` and emit events.

**Canonical minimum diagram set per ADM phase** (greenfield first pass):

| Phase | Diagram | Type | Viewpoint / Audience |
|---|---|---|---|
| A (AV) | Motivation overlay | ArchiMate-motivation | Stakeholders, PM — why we're doing this |
| B (BA) | Business structural architecture | ArchiMate-business | SA, PM — functions, roles assigned to functions, capabilities, services per function |
| B (BA) | Business operational architecture | ArchiMate-business | PM, PO — processes, events, roles, services; VS stage context; no functions shown |
| B (BA) | Sprint lifecycle | Activity/BPMN | PM, PO — how sprints flow (roles as lanes) |
| B (BA) | Value stream | Use-case | PO, stakeholders — VS stages as use-cases; triggering and consuming actors shown |
| C (AA) | Application component map | ArchiMate-application | Architects, developers — structural module map; ASV→BPR serving connections shown |
| C (AA) | Domain data model | ER (class) | Developers, DBAs — persisted data structures |
| C (AA) | CQ lifecycle | Sequence | Developers — how CQ resolution works at runtime |
| C (AA) | Sprint review | Sequence | Architects, PM — how review decisions are processed |
| C/G (AA/IG) | Algedonic fast-path escalation *(conditional)* | Sequence | Architects, PM, CSCO — emergency safety escalation decisioning and control actions |
| G (IG) | Skill invocation | Sequence | Developers — how a single skill is invoked end-to-end |

These are minima for a greenfield engagement. Any sprint — including those working on extensions or changes to existing systems — may produce any combination of: model entity/connection additions or modifications, updates to existing baseline diagrams (version increment), new work-package-scoped target diagrams, and additional diagrams for viewpoints not previously covered. The decision rule above (update vs. create) governs which output is appropriate in each case.

Conditional rule for safety-governance engagements: if the model includes algedonic escalation behavior (for example BEV-005/BPR-005 or equivalent fast-path safety process), produce and maintain at least one application runtime sequence that shows the end-to-end escalation control loop (signal raised -> CSCO safety evaluation -> PM/orchestration branch action).

### 0.4 Cross-diagram consistency

Where two diagram types cover the same component, process, or scenario, they must be mutually consistent. Deliberate overlap is the cross-verification mechanism: an application component named `EventStore` in an ArchiMate diagram must appear under the same name as a participant in sequence diagrams, as a swim-lane lane in activity diagrams, and as a class in ER diagrams if it has persisted data. **Inconsistency between diagram types is an architectural error** — not a tolerance to be managed.

Agents must run `list_artifacts(artifact_type="diagram")` before authoring a new diagram to check whether an existing diagram already covers the same viewpoint. A new diagram that duplicates an existing one without adding distinct scope is a model bloat error — update the existing diagram instead.

---

## 1. Authoring Model

Agents author PlantUML source text directly. The model (entity and connection files) drives diagram content; the diagram file expresses a selected view over that model for a specific purpose.

**Division of responsibility:**

| What | Who |
|---|---|
| Author/maintain entity and connection files with correct `§display` sections | SA (architecture-repository); SwA (technology-repository) |
| Author PUML diagram files from entity/connection `§display` specs | SA using D1–D5 protocol below |
| Author dense cross-reference matrices (`.md`) for high-cardinality mappings | SA/SwA via `model_create_matrix` (ID-authored markdown; auto-link to entity files) |
| Generate/regenerate `_macros.puml` from entity `§display ###archimate` blocks | `regenerate_macros()` tool (called by `write_artifact` when entity display specs change) |
| Post-authoring validation | `validate_diagram` tool |
| Rendering to SVG | `render_diagram` tool (invokes PlantUML CLI; run at sprint boundary) |

**Constraint:** Every element alias used in a `.puml` file must correspond to an entity artifact-id that exists in the ModelRegistry and has the appropriate `§display ###<language>` subsection. Diagrams cannot introduce entities that the model does not contain. **Status rules (enforced by `validate_diagram`):** a `draft` diagram may reference `draft` entities and connections — this is normal in-sprint authoring. A `baselined` diagram must reference only `baselined` entities and connections (E306/E307). Draft connections may in turn reference draft entities. The workflow is: author entities/connections/diagrams as `draft` during sprint work → call `baseline_artifact` at sprint gate pass on all artifacts in the correct dependency order (entities first, then connections, then diagrams) → the diagram may then be baselined. See §11.6 for enforcement details.

---

## 2. Catalog Structure

```
[enterprise-repository OR engagements/<id>/work-repositories/architecture-repository]/diagram-catalog/

  _macros.puml                    # Auto-generated from entity §display ###archimate blocks
                                  # Do not edit manually — regenerated by write_artifact and regenerate_macros()
  _archimate-stereotypes.puml     # Shared ArchiMate skinparam + stereotype library (SA-maintained)

  diagrams/
    <scope>-<type>-<subject>[-<domain>]-v<N>.puml   # Viewpoint diagrams
    <scope>-matrix-<subject>[-<domain>]-v<N>.md     # Cross-reference matrices (dense mappings)
    ...                                              # Each file carries frontmatter (PUML header for .puml; YAML block for .md)

  templates/
    <type>-template.puml          # Per-type stubs demonstrating structure and ArchiMate conventions
    ...                           # Agents copy into diagrams/, rename, and adapt elements and connections

  rendered/
    <same-stem>.svg               # SVG outputs; committed at sprint boundary
    ...
```

Naming rule for `<scope>`:

- Use an ADM phase token (`a`, `b`, `c`, `d`, `e`, `f`, `g`, `h`) only when the diagram is explicitly scoped to that phase's structures and/or behaviors.
- Otherwise use a purpose/scope token (for example `lifecycle`, `cq`, `sprint-review`, `specialist-invocation`) and avoid phase-prefixed names.
- Do not use a phase token merely because the artifact is produced during that phase. `phase-produced` in frontmatter is provenance metadata, not naming scope.
- Keep `artifact-id`, filename stem, rendered SVG stem, and `@startuml` identifier aligned.

**Rendering path invariant (mandatory):** Rendered SVG output path is always the sibling `diagram-catalog/rendered/` directory of `diagram-catalog/diagrams/`. Rendering into `diagram-catalog/diagrams/rendered/` is invalid and must be removed if found.

When rendering from within `diagram-catalog/diagrams/`, use:

```bash
java -jar tools/plantuml.jar -tsvg -o ../rendered *.puml
```

There are no `elements/`, `connections/`, or `index.yaml` files in the diagram catalog. Model entities and connections in `architecture-repository/model-entities/` and `connections/` are the element and connection catalog; `§display` sections in those files define rendering. Diagrams are discovered by ModelRegistry scanning PUML header comment frontmatter (§9).

**Reading vs. rendering:** Agents and skills read `.puml` source files (via `read_artifact`) for both local engagement diagrams and enterprise diagrams. Reading the PUML source is sufficient for agent context, validation, and authoring decisions. `render_diagram` produces an SVG and is only called when generating user-facing output (sprint reviews, deliverable packages, documentation exports) — never as a prerequisite for agent reasoning.

**Enterprise catalog:** `enterprise-repository/diagram-catalog/` contains only `_macros.puml`, `_archimate-stereotypes.puml`, `diagrams/`, `templates/`, and `rendered/`. Enterprise entity files in `enterprise-repository/model-entities/` provide the element definitions. Engagement agents read enterprise diagrams via `read_artifact(<enterprise-path>)` directly; no stubs or copies are placed in the engagement catalog.

**Engagement catalog:** `engagements/<id>/work-repositories/architecture-repository/diagram-catalog/` — self-contained per engagement. Enterprise entities are visible via the unified ModelRegistry (read-only to engagement agents); no import or copy step is required or permitted.

---

## 3. Element Identity

Diagram element aliases are derived from entity artifact-ids using **underscores** (`APP_001`), never hyphens (`APP-001`). The hyphenated form (`APP-001`) appears only in label strings and frontmatter fields. `_macros.puml` uses a **two-token convention** to avoid PlantUML's macro-expansion-in-connections bug (PB-005 in `docs/puml-bug-reports.md`):

```plantuml
' Entity: APP-001 (app-component "EventStore")
' Macro name = DECL_APP_001  (declaration trigger — used inside rectangle groups)
' Element alias = APP_001    (element reference — used in connection lines)
!define DECL_APP_001 rectangle "EventStore" <<ApplicationComponent>> as APP_001
```

**Why two tokens:** PlantUML `!define` macros expand on every occurrence of the macro name token. If the macro name equals the alias (`APP_001`), then connection lines `APP_001 --> APP_002` also expand — replacing the alias with the full rectangle declaration, which is a syntax error. The `DECL_` prefix separates the declaration trigger from the reference alias.

In diagram PUML source files:
- **Inside grouping rectangles (declaration):** `DECL_APP_001` — expands to the full `rectangle "..." as APP_001` declaration
- **Connection lines (reference):** `APP_001 -[#0078A0]-> APP_016 : <<serving>>` — bare alias, no expansion
- **Frontmatter fields:** `entity-ids-used: [APP-001, APP-016]` — hyphenated artifact-id (not the alias)

Why underscores (not hyphens) in aliases: PlantUML treats `-` as subtraction in identifier contexts. `APP-001 --> APP-016` parses as arithmetic. Underscored aliases parse unambiguously. Hyphens also crash PlantUML inside grouping `rectangle { }` blocks (PB-002).

Using artifact-id–derived aliases:
- Eliminates the dual-ID problem (was: `BC-001` entity ↔ `BFN-001` catalog element)
- Makes diagram source self-documenting — `APP_001` unambiguously maps to the EventStore entity
- Enables `validate_diagram` to verify all frontmatter IDs against the ModelRegistry with no secondary lookup

---

## 4. Catalog Lifecycle

### 4.1 Engagement Bootstrap (Preliminary / Phase A)

SA creates the engagement `diagram-catalog/` directory structure, populates `templates/` with per-type stubs adapted from the framework templates in `framework/diagram-conventions.md §7`, and runs `regenerate_macros()`. There is no entity import step: enterprise entities are already visible via the unified ModelRegistry (the enterprise repository is registered as a read-only path at session initialisation). `_macros.puml` is built from all engagement and enterprise entities together — `regenerate_macros()` reads `§display ###archimate` blocks from both scopes in a single pass.

Enterprise and prior-engagement diagrams are never copied into the engagement catalog. Agents read them directly via `read_artifact(<enterprise-path>)`. When a new engagement diagram needs to reuse elements from an existing enterprise diagram, SA authors a new `.puml` in `diagram-catalog/diagrams/`, adapting from the relevant template in `templates/` and referencing any entities visible in the unified ModelRegistry.

No diagram work begins until bootstrap is complete.

### 4.2 During Engagement

`write_artifact` calls `regenerate_macros()` automatically whenever an entity file's `§display ###archimate` block is created or modified. SA does not need to trigger this manually.

### 4.3 At Engagement Close

SA nominates engagement entities and diagrams that are sufficiently general for enterprise promotion per `repository-conventions.md §12`. Architecture Board approves and runs `promote_entity` / `promote_diagram`, which move the file to the appropriate enterprise path (assigning a new enterprise-scope ID for entities). No copies are made; the engagement retains only the `artifact.promoted` event record and any `reference` entries in `diagrams/index.yaml` pointing to the promoted enterprise path.

---

## 5. Diagram Production Protocol (D1–D5)

Every skill step that produces or updates a diagram executes this protocol.

### D0 — Choose Representation (Diagram vs Matrix)

Before D1, choose the artifact form intentionally:

- Use a `.puml` diagram when spatial/topological relationships, sequence, flow, or grouping structure are the primary communication need.
- Use a matrix `.md` when the objective is coverage, traceability, dependency mapping, or many-to-many relationship inspection across large ID sets.
- Default rule for dense mappings: if the same artifact would exceed ~25 nodes or become edge-dense enough to harm readability, produce a matrix first and add/keep only the minimal supporting diagrams needed for topology.
- If a rendered diagram still has overlapping edge lanes after one layout pass, stop tuning and decompose into thematic sub-diagrams plus a full-coverage matrix.
- Coverage guardrail: matrices must not become a substitute for architectural context. Keep a reasonable set of diagrams per domain slice so end-to-end behavior, boundaries, and interaction structure remain visible.

For matrix authoring, use `model_create_matrix` with ID-based markdown and enabled auto-linking so cells resolve to model entities.

### D1 — Query Model Entities

Identify which entities belong in the diagram:

```
list_artifacts("<layer-dir>", domain="<domain>", status="baselined")
```

For cross-layer diagrams: query multiple directories. Review the `§display ###<target-language>` subsection of each candidate via `read_artifact(id, mode="summary")` to confirm applicability.

Also query relevant connections:

```
list_connections(artifact_type="archimate-realization", target="BSV-001")
list_connections(artifact_type="er-one-to-many", source="DOB-001")
```

### D2 — Verify §display Coverage

For each entity that will appear in the diagram, confirm the required `§display ###<language>` subsection is present.

- **SA**: if the subsection is missing, add it via `write_artifact` (update to existing entity file). `regenerate_macros()` runs automatically.
- **Non-SA**: emit a `diagram.display-spec-request` handoff to SA specifying which entities need which language subsections.

### D3 — Author PUML

**D3a:** Load the template for the diagram type from §7 via `read_framework_doc("framework/diagram-conventions.md §7.<type>")`.

**D3b — ArchiMate and Use Case diagrams:** use `!include _macros.puml` at the top. Reference entities by their artifact-id alias. `_macros.puml` provides the PUML element declaration via the `!define` macro. Relationship lines are authored from connection `§display ###archimate` specs.

**D3b — ER (class) diagrams:** call `generate_er_content(entity_ids)` — this tool reads each entity's `§display ###er` block and returns PUML class declarations with attribute lists. Call `generate_er_relations(connection_ids)` to get cardinality lines from connection `§display ###er` blocks. Paste both into the PUML file. No `!include _macros.puml` needed for pure ER diagrams.

**D3b — Sequence diagrams:** participants are declared from entity `§display ###sequence` specs (`participant-type` and `label`). Message lines are authored from connection `§display ###sequence` blocks.

**D3b — Activity/BPMN diagrams:** swimlane pool labels come from entity `§display ###activity` blocks (`swimlane-label`). Flow arrows come from connection `§display ###activity` blocks.

Activity/BPMN authoring lint (run before `D4` validation):
- Decision uniqueness: no duplicate predicate decisions in immediate sequence.
- Branch usefulness: each decision branch has distinct downstream work/target.
- Loop minimality: one explicit loopback guard per loop; all rework branches route to that guard's merge/entry target.
- Loop policy split: user-initiated loops should show explicit continue/approve/stop outcomes without fixed auto-cap; automated agent loops must show max-iteration and overflow target.

**D3c:** Write the `.puml` file via `write_artifact`. Filename: `<scope>-<type>-<subject>[-<domain>]-v<N>.puml`.

**D3d:** Ensure the PUML file begins with the required frontmatter comment block (see §9). The frontmatter is the diagram's registry entry — no separate `index.yaml` exists.

### D4 — Validate

Call `validate_diagram(<puml_file_path>)` immediately after writing. The tool:

- Checks all element aliases resolve to known entity artifact-ids in ModelRegistry.
- Verifies each resolved entity has the appropriate `§display ###<language>` subsection.
- Confirms `!include _macros.puml` is present in ArchiMate/use-case diagrams.
- Confirms ArchiMate diagrams also include `!include _archimate-stereotypes.puml`.
- Returns a list of errors; SA fixes and re-calls until clean.

**On ALG-C03** (diagram alias has no backing entity): the agent must create the missing entity file before re-validating — the diagram cannot be made valid by deleting the alias; the model must be extended.

### D5 — Render (user-facing output only)

Call `render_diagram(<puml_file_path>)` when producing user-facing output: sprint reviews, deliverable packages, or documentation exports. Invokes PlantUML CLI; writes SVG to the sibling `diagram-catalog/rendered/` directory of the source file's `diagram-catalog/diagrams/` path. Commit both `.puml` and `.svg` at sprint close. Do not call `render_diagram` as part of agent reasoning or validation — `read_artifact` on the `.puml` source is sufficient for those purposes.

---

## 6. `_macros.puml` Structure and Generation

`_macros.puml` is generated by scanning all entity files across the engagement's architecture-repository and technology-repository for `§display ###archimate` blocks. Do not edit manually.

**IMPORTANT — two-token convention:** Macro names use `DECL_` prefix; element aliases use plain underscored IDs. This prevents macro expansion in connection lines (PlantUML bug PB-005). Generated by `src/tools/generate_macros.py` — never edit manually.

**Stereotype capitalisation:** Use `<<ApplicationComponent>>`, `<<BusinessActor>>`, `<<BusinessCollaboration>>`, etc. (UpperCamelCase) so that skinparam stereotype selectors in `_archimate-stereotypes.puml` match correctly. The canonical list of valid `element-type` values is in `src/common/archimate_types.py` (`ARCHIMATE_ELEMENT_TYPES_BY_LAYER`) and documented in `framework/artifact-schemas/entity-conventions.md §3.3`.

```plantuml
' Auto-generated by regenerate_macros() — DO NOT EDIT MANUALLY
' Last regenerated: <ISO8601 timestamp>
' Entity count: N

' --- strategy/ ---
!define DECL_CAP_001 rectangle "Agent Orchestration" <<Capability>> as CAP_001
!define DECL_CAP_002 rectangle "Artifact Management" <<Capability>> as CAP_002

' --- business/ ---
!define DECL_ACT_001 rectangle "Solution Architect Agent" <<BusinessActor>> as ACT_001
!define DECL_BPR_001 rectangle "Execute ADM Phase" <<BusinessProcess>> as BPR_001
!define DECL_BSV_001 rectangle "Architecture Modelling Service" <<BusinessService>> as BSV_001

' --- application/ ---
!define DECL_APP_001 rectangle "PM Agent" <<ApplicationComponent>> as APP_001
!define DECL_APP_002 rectangle "SA Agent" <<ApplicationComponent>> as APP_002
!define DECL_DOB_001 class "WorkflowEvent" as DOB_001

' --- technology/ ---
!define DECL_NOD_001 node "Container Host" <<Node>> as NOD_001
!define DECL_SSW_001 rectangle "Python 3.12 Runtime" <<SystemSoftware>> as SSW_001
!define TSV_001 database "SQLite EventStore" <<technologyService>> as TSV-001
```

**ArchiMate element type → PUML syntax mapping** (used by `regenerate_macros()`):

| element-type | layer | PUML declaration |
|---|---|---|
| Stakeholder, Driver, Goal, Requirement, Constraint, Principle | motivation | `rectangle "..." <<motivation-type>> as ID` |
| Capability, ValueStream, Resource, CourseOfAction | strategy | `rectangle "..." <<strategy-type>> as ID` |
| BusinessActor, BusinessRole | business | `rectangle "..." <<businessActor/Role>> as ID` |
| BusinessProcess, BusinessFunction, BusinessService | business | `rectangle "..." <<business-type>> as ID` |
| BusinessObject, Contract, Product | business | `rectangle "..." <<business-passive-type>> as ID` |
| ApplicationComponent, ApplicationService | application | `rectangle "..." <<application-type>> as ID` |
| DataObject | application | `class "..." as ID` |
| Node, Device, SystemSoftware | technology | `node "..." <<tech-type>> as ID` |
| TechnologyService | technology | `database "..." <<technologyService>> as ID` |
| Artifact | technology | `artifact "..." as ID` |
| WorkPackage, Deliverable, Gap, Plateau | implementation | `rectangle "..." <<impl-type>> as ID` |

**Sync rule (ALG-C04):** If the entity count in `_macros.puml` does not match the count of entities with `###archimate` display sections in ModelRegistry, `validate_diagram` raises ALG-C04. SA calls `regenerate_macros()` to resync.

---

## 7. PUML Authoring Templates

Load via `read_framework_doc("framework/diagram-conventions.md §7.<type>")` at D3a.
All aliases use underscore artifact IDs (`APP_001`, `DOB_002`).

### §7.archimate-motivation — Architecture Vision Motivation Overlay

```plantuml
@startuml
!include _macros.puml
!include _archimate-stereotypes.puml
STK_001
DRV_001
GOL_001
DRV_001 ..> GOL_001 : <<influence>>
@enduml
```

### §7.archimate-business — Business Architecture Structural Viewpoint

Use for stable structure only (functions, roles/collaborations, services, capabilities).
Do not include process flow detail.

### §7.archimate-business-operational — Business Architecture Operational Viewpoint

Use for trigger-and-flow behavior (events, processes/interactions, object access, service realization).
For staged behavior, parent `BPR`/`BIA` is the container and stages are nested.

### §7.archimate-application — Application Architecture Component Overview

Include components, interfaces, services, and required serving/realization relations.

### §7.archimate-technology — Technology Architecture Node Diagram

Include nodes/system-software/services/artifacts and assignment/serving/realization relations.

### §7.usecase — Use Case Diagram

Use BSV IDs for use-cases and ACT/ROL for actors.
Use only `<<include>>`, `<<extend>>`, `association`, and `generalization` relationships.

### §7.class-er — Entity-Relationship (Class) Diagram

Do not include `_macros.puml`.
Generate class declarations via `generate_er_content()` and relationships via `generate_er_relations()`.
Aliases must use underscores (`DOB_001`), never hyphens.

### §7.sequence — Sequence Diagram

Participants come from entity `§display ###sequence`; messages come from `connections/sequence/*`.
Use synchronous/asynchronous/return semantics exactly as modeled.
When modeling safety-governance fast-path behavior, the sequence must include explicit branch outcomes (continue/pause/stop or equivalent) and identify the CSCO decision path as a first-class participant interaction.

Runtime quality controls (mandatory for orchestration/application-runtime sequences):
- **Idempotent resume/integration points:** when an event-producing action can be retried, include an explicit dedup key path in the sequence using the canonical event identity (for example `event_id`) and show duplicate handling.
- **Correlation continuity:** decision and lifecycle events that belong to the same control episode (for example CQ, gate, algedonic) must carry a stable correlation key (for example `cq_id`/`invocation_id`/`correlation_id`) in the sequence narrative.
- **Fail-safe timeout branch for safety decisions:** if a modeled control step depends on a safety/governance decision and that decision can be unavailable/late, include an explicit timeout/unavailable branch with a conservative default (fail-closed containment/suspend/rework).

### §7.activity-bpmn — Activity / BPMN-Overlay Process Diagram

Keep business-layer and application-layer activity scopes separate unless showing a single explicit handoff boundary.
Always label branch outcomes (`yes/no`, `pass/fail`) and map swimlanes to model entities.

Control-flow normalization rules (mandatory):
- Use one authoritative decision/guard per predicate in a local control segment (for example a single `Targeted rework required?` loop guard).
- Do not chain semantically equivalent decisions with immediate convergence (for example `All outputs approved?` followed directly by `Targeted rework required?` with no intervening branch-specific work).
- If two candidate decision nodes express the same predicate, keep the downstream loop/stage-gate guard and replace the upstream one with a state-derivation activity, or remove the redundant node.
- Every decision node must have at least one branch-specific action or distinct target before reconvergence; otherwise collapse it.
- User-requested review/rework loops are not hard-capped in workflow diagrams; users may continue correction cycles until explicit approval or explicit stop/pause outcome.
- Automated agent-initiated rework loops (for example task-specification retries or fast-path technical rework) should declare bounded iteration counts and explicit overflow handling.

## 8. Write Authority

| Operation | SA | Non-SA agents |
|---|---|---|
| Add/update `§display` blocks on own-domain entities | Yes | Yes (own-domain entities only) |
| Add/update `§display` blocks on SA-owned entities | Yes | No — emit `diagram.display-spec-request` handoff |
| Write `.puml` to `diagram-catalog/diagrams/` | Yes | No |
| Write `.puml` to own work-repo `diagrams/` | — | Yes (draft diagrams pending SA integration) |
| Trigger `regenerate_macros()` | Yes (auto via write_artifact) | No |
| Trigger `render_diagram()` | Yes | No (sprint boundary only) |

---

## 9. Diagram Frontmatter (PUML Header Comment Block)

Diagrams are discovered by ModelRegistry scanning the PUML header comment block at the top of every `.puml` file in `diagram-catalog/diagrams/` and `diagram-catalog/templates/`. There is no separate `index.yaml` — the frontmatter in each file is the single source of truth, consistent with the ERP principle applied to model entities and connections.

The header comment block uses PUML line-comment syntax (`' `). ModelRegistry strips the `' ` prefix from each line and parses the resulting YAML.

**Required frontmatter fields for produced diagrams (`diagrams/`):**

```plantuml
' ---
' artifact-id: business-archimate-structural-v1
' artifact-type: diagram
' name: "Business Architecture — Structural Viewpoint"
' diagram-type: archimate-business
' version: 0.1.0
' status: draft
' phase-produced: B
' owner-agent: SA
' engagement: ENG-001
' domain: core-platform
' entity-ids-used: [CAP-001, CAP-002, ACT-001, BPR-001, BSV-001]
' connection-ids-used: [CAP-001---BPR-001, ACT-001---BPR-001]
' ---
@startuml
!include ../_macros.puml
!include ../_archimate-stereotypes.puml
...
@enduml
```

**Required frontmatter fields for template stubs (`templates/`):**

```plantuml
' ---
' artifact-id: archimate-business-template
' artifact-type: diagram-template
' name: "ArchiMate Business Layer — Starting Template"
' diagram-type: archimate-business
' owner-agent: SA
' engagement: ENG-001
' ---
@startuml
!include ../_macros.puml
!include ../_archimate-stereotypes.puml

' ADAPT THIS TEMPLATE: add, remove, and rewire elements and connections
' to match the specific diagram. Replace PLACEHOLDER aliases with real artifact-ids.

' --- Example structure (replace with actual entities) ---
' PLACEHOLDER_CAP_001  ' capability
' PLACEHOLDER_BPR_001  ' business process
' PLACEHOLDER_CAP_001 --> PLACEHOLDER_BPR_001 : <<realization>>

@enduml
```

**`entity-ids-used` and `connection-ids-used`:** These fields in diagram frontmatter enable `validate_diagram` to check that every listed entity-id exists in ModelRegistry with the appropriate `§display ###<language>` subsection. They also enable `regenerate_macros()` to detect when a diagram references entities whose archimate display spec has changed.

---

## 10. Reference Table

| Section | Governs |
|---|---|
| §1 | Authoring model: model-driven diagram production |
| §2 | Catalog structure: no element files; entity files are the catalog |
| §3 | Element identity: artifact-ids as PUML aliases (underscores, not hyphens) |
| §4 | Catalog lifecycle: bootstrap, import, engagement close |
| §5 | D1–D5 production protocol: query → verify → author → validate → render |
| §6 | `_macros.puml` generation from `§display ###archimate` blocks |
| §7 | PUML templates per diagram type |
| §8 | Write authority table |
| §9 | Diagram frontmatter: PUML header comment block — single source of truth for diagram metadata |
| §10 | PlantUML compatibility constraints — known syntax limitations that must be respected |

**Cross-references:**
- `framework/artifact-registry-design.md §3.6` — `§display` spec schemas per language
- `framework/artifact-schemas/entity-conventions.md` — entity/connection file format
- `framework/discovery-protocol.md §8` — Step 0.D (Diagram Catalog Lookup in Discovery Scan)
- `framework/algedonic-protocol.md` — ALG-C03 (diagram alias has no backing entity), ALG-C04 (`_macros.puml` out of sync)
- `framework/repository-conventions.md §12` — Enterprise Promotion Protocol
- `framework/agent-runtime-spec.md §6` — tool specs: `validate_diagram`, `render_diagram`, `regenerate_macros`, `generate_er_content`, `generate_er_relations`
- `docs/puml-bug-reports.md` — confirmed PlantUML bugs; consult before authoring new diagram types

---

## 10. PlantUML Compatibility Constraints

These constraints are empirically confirmed against PlantUML 1.2025.x (the version shipped with VS Code PlantUML extension as of 2026-04). They are **mandatory** — violating them produces error diagrams, not rendered output. See `docs/puml-bug-reports.md` for full bug details and workarounds.

### 10.1 Two-Token Macro Convention (DECL_ prefix)

**Rule:** Macro names in `_macros.puml` use `DECL_` prefix (`DECL_APP_001`); element aliases use plain underscore IDs (`APP_001`). Never use the same token as both macro name and alias.

**Why:** PlantUML `!define` is a pure text preprocessor — it replaces every occurrence of the macro name, including in connection lines. If macro name equals alias, `APP_001 --> APP_002` expands to `rectangle "..." as APP_001 --> rectangle "..." as APP_002`, which is a syntax error (PB-005).

**Usage:**
```plantuml
' Declaration (inside rectangle group body):
DECL_APP_001        ← expands to: rectangle "EventStore" <<ApplicationComponent>> as APP_001

' Connection (outside groups):
APP_001 -[#0078A0]-> APP_016 : <<serving>>    ← APP_001 is alias, not macro name — no expansion
```

**Applies to:** All `!define` entries in `_macros.puml`; all diagram source files.

### 10.2 Alias Naming: Underscores Only

**Rule:** All PUML element aliases must use underscores (`APP_001`), never hyphens (`APP-001`).

**Why:** PlantUML's lexer treats `-` in connection syntax as arithmetic subtraction. `APP-001 --> APP-016` fails. Hyphens also crash inside grouping rectangles (PB-002).

**Applies to:** All element aliases (the `as APP_001` part), `!define` macro targets, connection line references.

**Does not apply to:** Frontmatter fields (`entity-ids-used`, `connection-ids-used`), rectangle label strings — these are data values, not PUML identifiers.

### 10.3 No `together { }` Inside `rectangle { }` Groups

**Rule:** Never nest `together { }` inside a `rectangle "..." { }` grouping block.

**Why:** PlantUML 1.2025.x crashes with `IndexOutOfBoundsException` at `CucaDiagram.currentTogether` when `together` is encountered inside a group rectangle (confirmed bug PB-001 in `docs/puml-bug-reports.md`).

**Workaround:** List all elements flat inside the grouping rectangle. Use `together { }` only at the top level (outside all grouping rectangles) when layout hints are needed.

```plantuml
' CORRECT — flat list inside group
rectangle "Agent Roster" as GRP_AGENTS #F3E5F5 {
  DECL_APP_007
  DECL_APP_008
  DECL_APP_009
}

' WRONG — together inside rectangle causes crash
rectangle "Agent Roster" as GRP_AGENTS #F3E5F5 {
  together {   ' <-- IndexOutOfBoundsException
    DECL_APP_007
    DECL_APP_008
  }
}
```

### 10.4 No `left to right direction` with Cross-Group Connections

**Rule:** Use `skinparam rankdir LR` instead of `left to right direction` for left-to-right layout in diagrams that connect elements across grouping rectangles.

**Why:** `left to right direction` causes PlantUML to reject element declarations (`rectangle "..." <<Stereotype>> as ALIAS`) that appear inside grouping rectangles when cross-group connections are present (confirmed bug PB-003 in `docs/puml-bug-reports.md`).

**Workaround:** Replace `left to right direction` with `skinparam rankdir LR`.

### 10.5 `skinparam rectangle<<Stereotype>> { }` Must Use Multi-Line Format

**Rule:** Use multi-line skinparam blocks, not inline semicolon-separated values.

```plantuml
' CORRECT
skinparam rectangle<<ApplicationComponent>> {
  BackgroundColor #CCF2FF
  BorderColor #0078A0
}

' WRONG — inline format not supported
skinparam rectangle<<ApplicationComponent>> { BackgroundColor #CCF2FF; BorderColor #0078A0 }
```

### 10.6 Stereotype Capitalisation Must Match skinparam Selectors

**Rule:** Use UpperCamelCase stereotypes in both `!define` macros and skinparam selectors (`<<ApplicationComponent>>`, `<<BusinessActor>>`, not `<<applicationComponent>>`, `<<businessActor>>`).

**Why:** skinparam stereotype selectors are case-sensitive. A mismatch means the element renders without the intended colour.

### 10.7 Line-Number Error Reporting

The `ModelVerifier._check_puml_syntax()` method runs `plantuml -tsvg -verbose` and reports `Error line N in file: <path>` errors. When debugging diagram errors:
1. Open the diagram at the reported line.
2. Check against the constraints in §10.1–10.6.
3. Consult `docs/puml-bug-reports.md` for known bugs.
4. Use `-tsvg -verbose` directly: `java -jar tools/plantuml.jar -tsvg -verbose <file>`.

---

## 11. ArchiMate Semantic Constraints

These rules govern how ArchiMate concepts map to PlantUML diagram constructs. Violations produce diagrams that render but carry wrong architectural meaning.

### 11.1 Layer Boundary Rule: No Cross-Layer Nesting

**Rule:** Only elements from one ArchiMate layer may appear inside a grouping rectangle within a layer-specific diagram. Business elements must not be nested inside application groupings, and vice versa.

**Why:** Nesting implies containment in ArchiMate semantics. Placing a `<<BusinessRole>>` element inside an `<<ApplicationComponent>>` group would imply the role *is part of* that application component — which is architecturally false.

**Correct pattern — single-layer groups only:**
```plantuml
' Application layer diagram — only application elements inside groups
rectangle "Subsystem A" <<Grouping>> as GRP_A #E8EAF6 {
  DECL_APP_001   ' <<ApplicationComponent>> — correct
  DECL_APP_002   ' <<ApplicationComponent>> — correct
}

' WRONG: mixing layers inside a group
rectangle "Subsystem A" <<Grouping>> as GRP_A #E8EAF6 {
  DECL_APP_001   ' application layer — OK
  DECL_ACT_001   ' business layer — WRONG: cross-layer nesting
}
```

**Cross-layer references:** When a cross-layer connection must be shown (e.g., application component *realizes* business service), declare the target element **outside all grouping rectangles** using a bare inline declaration (`rectangle "Label" <<Stereotype>> as ALIAS`), then draw the connection. This makes the cross-layer boundary explicit.

### 11.2 ArchiMate Active Structure Type Rules

**Rule:** Use the correct ArchiMate element type for each entity:

| Entity kind | ArchiMate type | When to use |
|---|---|---|
| Autonomous agent / person / organisation | `BusinessActor` | A concrete, identifiable entity that initiates behavior |
| Role / behavioral specification | `BusinessRole` | A named set of responsibilities that actors or agent processes fill |
| Joint governance body / consortium | `BusinessCollaboration` | Two or more roles/actors working together toward a shared goal |
| Deployed software module | `ApplicationComponent` | A concrete, deployable software unit |
| Named service grouping | `ApplicationService` | An externally visible behavior offered by an application |
| Port / access point | `ApplicationInterface` | A defined access point for an ApplicationComponent |

**Common mistakes to avoid:**

- **Automated agent roles are `BusinessRole`, not `BusinessActor`.** The concrete agent implementation (an `ApplicationComponent`) fills the role; the role is the behavioral specification. Conflating them at the business layer hides the important distinction between *what behavior is expected* and *what software delivers it*.
- **Governance bodies are `BusinessCollaboration`.** A governance board that coordinates multiple roles is not a single autonomous actor but a named collaboration. Model it as `BusinessCollaboration` with explicit membership connections to the participating `BusinessRole` and `BusinessActor` elements.
- **Do not model the same entity at two layers simultaneously.** A role at the business layer and its implementing module at the application layer are distinct entities connected by a realization relationship, not the same element appearing in both diagrams.

### 11.3 Grouping Rectangles Must Declare Their ArchiMate Type

**Rule:** Every grouping rectangle in a diagram — both outer containers and inner swim-lanes — must have an explicit ArchiMate stereotype.

**Why:** An un-stereotyped rectangle has no ArchiMate meaning. Readers cannot determine whether it represents a `<<Grouping>>`, an `<<ApplicationCollaboration>>`, or a deployment unit.

**Choose the grouping stereotype** based on the homogeneity of the contained elements:

| Situation | Stereotype to use |
|---|---|
| All contained elements are from **one ArchiMate layer** | Layer-specific stereotype (lighter tint of layer color) |
| Contained elements span **multiple layers**, or grouping is purely organisational | `<<Grouping>>` (neutral white, grey border) |

**Layer-specific stereotypes** (use when the container is a single-layer cluster):

| Contained layer | Stereotype |
|---|---|
| Motivation | `<<MotivationGrouping>>` |
| Strategy | `<<StrategyGrouping>>` |
| Business | `<<BusinessGrouping>>` |
| Application | `<<ApplicationGrouping>>` |
| Technology | `<<TechnologyGrouping>>` |
| Physical | `<<PhysicalGrouping>>` |
| Implementation | `<<ImplementationGrouping>>` |

```plantuml
' CORRECT — single-layer cluster uses layer-specific stereotype
rectangle "Agent Roster" <<ApplicationGrouping>> as GRP_A {
  DECL_APP_001   ' <<ApplicationComponent>>
  DECL_APP_002
}

' CORRECT — heterogeneous or purely organisational grouping uses neutral
rectangle "Cross-Cutting Concerns" <<Grouping>> as GRP_CROSS {
  DECL_APP_001   ' application layer
  DECL_BSV_001   ' business layer
}

' WRONG — inline #color overrides the layer color signal
rectangle "Subsystem A" <<ApplicationGrouping>> as GRP_A #E8EAF6 {  ' forbidden
  DECL_APP_001
}

' WRONG — arbitrary colour unrelated to any ArchiMate layer
rectangle "Subsystem A" <<ApplicationGrouping>> as GRP_A #F3E5F5 {  ' forbidden
  DECL_APP_001
}
```

**Prohibition:** Never add an inline `#RRGGBB` color to a grouping rectangle — the stereotype supplies the only permissible background. If no suitable stereotype exists, add one to `_archimate-stereotypes.puml`. The `ModelVerifier` (future: rule E360) will flag inline colors on elements carrying a grouping stereotype.

### 11.4 Business Services Must Connect to Processes

**Rule:** Every `<<BusinessService>>` in a phase-B diagram must have at least one incoming `<<realization>>` connection from a `<<BusinessProcess>>` or `<<ApplicationService>>`.

**Why:** A service with no realizing process is architecturally incomplete — it says *what* is offered but not *how* it is delivered. Isolated service elements indicate a model gap.

**Pattern:**
```plantuml
' Business process realizes business service (within business layer)
BPR_001 ..[#B8860B].>> BSV_001 : <<realization>>

' Application service realizes business service (cross-layer — BSV declared outside groups)
ASV_001 ..[#0078A0].>> BSV_001 : <<realization>>
```

When cross-layer realization is deferred to a separate Phase C diagram, add an explanatory note:
```plantuml
note as N_REAL
  Application-layer realization
  (ApplicationService → BusinessService) is shown
  in the Phase C application architecture diagram.
end note
```

### 11.6 Diagram Status and Element Status Consistency

**Rule:** A `baselined` diagram must reference only `baselined` entities and connections. A `draft` diagram may reference `draft` entities and connections — this is normal in-sprint authoring. Draft connections may in turn reference draft entities. This forms a coherent draft-draft chain during active work.

**Baselining dependency order:** Entities must be baselined before the connections that link them; connections must be baselined before the diagrams that reference them. At sprint gate pass, call `baseline_artifact` in this order: entities → connections → diagrams.

**Enforcement (`validate_diagram` / `ModelVerifier`):**
- E306: `baselined` diagram references a `draft` entity.
- E307: `baselined` diagram references a `draft` connection.
- These checks are skipped for `draft` diagrams (draft→draft is allowed).
- Deprecated elements must be removed from all diagrams before or at the same time as their `deprecate_artifact` call; `validate_diagram` will flag any alias still pointing to a deprecated entity.

### 11.5 Collaborative Behavior: Collaboration → Interaction → Business-Layer Target

**Rule:** When multiple application (or business, or technology) elements *jointly* produce behavior that realizes a higher-level process or service, use the **Collaboration + Interaction** pattern — never individual element-to-process realization connections.

**Why:** A single `ApplicationService → BusinessProcess` realization connection implies that service alone realizes the process. When the behavior requires multiple components/services working together in a structured sequence, that implication is architecturally false. The `ApplicationInteraction` element is specifically designed to represent structured collective behavior; the `ApplicationCollaboration` is the structural container of the participants. Realization must originate from the behavioral element (interaction), not the structural element (collaboration).

**The mandatory three-element pattern:**

| Element | ArchiMate type | Role |
|---|---|---|
| `ACO-NNN` | ApplicationCollaboration | *Structural* — aggregates the participating components/services |
| `AIA-NNN` | ApplicationInteraction | *Behavioral* — the structured sequence the collaboration performs |
| `ACO-NNN ---assignment---> AIA-NNN` | Assignment | "The collaboration is assigned to perform this interaction" |
| `AIA-NNN ---realization---> BPR-NNN` | Realization | Cross-layer: application-layer interaction realizes business-layer process |

**The same pattern applies at every ArchiMate layer:**
- Business layer: `BCO` (BusinessCollaboration) + `BIA` (BusinessInteraction) → BusinessProcess/BusinessService
- Application layer: `ACO` (ApplicationCollaboration) + `AIA` (ApplicationInteraction) → BusinessProcess/BusinessService
- Technology layer: `TCO` (TechnologyCollaboration) + `TIA` (TechnologyInteraction) → ApplicationService/BusinessService

**Cross-layer realization is valid in ArchiMate 3.1.** An application-layer behavioral element can realize a business-layer behavioral element. This is how application architecture justifies its relevance to business objectives. Do not restrict realization connections to within-layer pairs.

**Prohibited patterns:**

```
❌  ASV-001 --realization--> BPR-002   (implies ASV-001 alone realizes the whole process)
❌  ACO-001 --realization--> BPR-002   (collaboration is structural — realization is a behavioral relationship)
✓   ACO-001 --aggregation--> ASV-001   (collaboration groups the participants)
✓   ACO-001 --assignment-->  AIA-001   (collaboration is assigned to perform the interaction)
✓   AIA-001 --realization--> BPR-002   (interaction realizes the business process)
```

**Example (ENG-001 Skill Execution):**
```plantuml
' Structural grouping: collaboration aggregates its service participants
ACO_001 o-[#5C6BC0]- ASV_001 : <<aggregation>>
ACO_001 o-[#5C6BC0]- ASV_002 : <<aggregation>>
ACO_001 o-[#5C6BC0]- ASV_005 : <<aggregation>>

' Active structure → behavior assignment
ACO_001 -[#5C6BC0]-> AIA_001 : <<assignment>>

' Cross-layer realization: application interaction → business process
AIA_001 ..[#B8860B].>> BPR_002 : <<realization>>
```

---

### 11.7 Capability Realization: Valid Realizing Elements

**Rule:** A `Capability` (`CAP-NNN`) may only be realized by **behavioral** ArchiMate elements — elements that represent activity, behavior, or performance. Structural elements (actors, roles, collaborations) cannot directly realize a capability. Capabilities are typically realized by **more than one** behavioral element — a single realizer implies the capability is delivered by exactly one process or service, which is architecturally unusual for anything beyond the most atomic capability.

**Why:** A Capability represents *what* the organization can do — a stable, high-level abstraction. It says nothing about *how* that ability is enacted. The "how" is captured by behavioral elements. Because both processes (internal behavior) and services (externally visible behavior) are behavioral, both are equally valid realizers. Resources and roles contribute to capabilities via `Assignment`, not `Realization`. A well-modeled capability typically has at least one business-layer behavioral realizer (BPR/BFN/BSV) *and* at least one application-layer realizer (ASV/AIA), reflecting that the capability is enacted by human-facing processes backed by software services. A model with only one realizer is a signal to check whether coverage is complete.

**Valid realizing element types:**

| Realizing element | ArchiMate type | Notes |
|---|---|---|
| `BPR-NNN` | Business Process | Internal, step-by-step enactment — most common realizer |
| `BFN-NNN` | Business Function | Stable organizational function — preferred when behavior is continuous rather than sequential |
| `BSV-NNN` | Business Service | External, value-exposing behavior — valid when the capability is framed as a service to another actor |
| `BIA-NNN` | Business Interaction | Use when the capability requires two or more collaborating actors |
| `ASV-NNN` | Application Service | Valid cross-layer realizer — preferred over APR (see §11.8) |
| `AIA-NNN` | Application Interaction | Use with ACO when multiple app elements jointly realize the capability (see §11.5) |

**Prohibited:**
```
❌  ACT-001 --realization--> CAP-001   (Business Actor is structural — use Assignment instead)
❌  ROL-001 --realization--> CAP-001   (Business Role is structural — use Assignment instead)
❌  ACO-001 --realization--> CAP-001   (Application Collaboration is structural — see §11.5)
❌  APP-001 --realization--> CAP-001   (Application Component is structural — use ASV or AIA)
```

**Canonical pattern (process realizes capability):**
```plantuml
' Business process (behavioral) realizes capability (strategic)
BPR_001 ..[#B8860B].>> CAP_001 : <<realization>>

' Business function alternative (continuous behavior)
BFN_001 ..[#B8860B].>> CAP_001 : <<realization>>

' Cross-layer: application service realizes capability (valid and common)
ASV_001 ..[#0078A0].>> CAP_001 : <<realization>>

' Resource supports capability (contribution, not realization)
RES_001 -[#607D8B]-> CAP_001 : <<association>>
```

---

### 11.8 Services vs. Processes: Internal/External Behavior and Cross-Layer Serving

**Conceptual distinction (within a single ArchiMate layer):**

| Element type | ArchiMate metaphor | Represents |
|---|---|---|
| Process (`BPR`, `APR`, `TPR`) | "The How" | *Internal* behavior — the ordered sequence of steps executed to produce an outcome |
| Service (`BSV`, `ASV`, `TSV`) | "The What" | *External* behavior — the value or functionality exposed to the environment (the interface contract) |

**Within-layer rule:** A Process (or Function or Interaction) **realizes** a Service of the same layer. The service is the stable external contract; the process is the internal implementation.

```plantuml
BPR_001 ..[#B8860B].>> BSV_001 : <<realization>>   ' process realizes service (same layer)
APR_001 ..[#0078A0].>> ASV_001 : <<realization>>   ' app process realizes app service (same layer)
```

**Cross-layer serving/realization table:**

| Lower-layer element | Relationship | Upper-layer element | Notes |
|---|---|---|---|
| `ASV-NNN` (Application Service) | `Serving` | `BPR-NNN` (Business Process) | The app service provides capability to the business process |
| `ASV-NNN` (Application Service) | `Realization` | `BSV-NNN` (Business Service) | The app service fulfills the business service contract |
| `APR-NNN` (Application Process) | `Realization` | `ASV-NNN` (Application Service) | Preferred within-layer route; keeps layers decoupled |
| `TSV-NNN` (Technology Service) | `Serving` | `APP-NNN` (Application Component) | Infrastructure serves the application |
| `TSV-NNN` (Technology Service) | `Serving` | `ASV-NNN` (Application Service) | Infrastructure serves the application service |

**The service-proxy decoupling principle:**

Prefer routing cross-layer behavior through services rather than processes:

```
Preferred:   APR-NNN --realization--> ASV-NNN --serving--> BPR-NNN
Acceptable:  ASV-NNN --realization--> BSV-NNN
Avoid:       APR-NNN --serving--> BPR-NNN   (skips the service abstraction layer)
```

**Why prefer the service-proxy route?** If the internal application process changes (e.g., refactored, replaced), the business process model is unaffected — the service contract remains stable. Direct process-to-process connections create tight coupling between layers that makes incremental refactoring fragile.

**Exception:** When the architectural purpose of a diagram is specifically to show the internal cross-layer dependency (e.g., in a gap analysis or feasibility assessment), a direct process-to-process serving connection is acceptable if annotated with a note explaining why the service abstraction is intentionally omitted.

**Summary — valid realizing chains:**

| If you have a... | It is typically realized/served by... |
|---|---|
| `CAP-NNN` (Capability) | `BPR-NNN`, `BFN-NNN`, `BSV-NNN`, or `ASV-NNN` / `AIA-NNN` (cross-layer) |
| `BSV-NNN` (Business Service) | `BPR-NNN` (within-layer) or `ASV-NNN` (cross-layer) |
| `BPR-NNN` (Business Process) | Assigned to `ACT-NNN`/`ROL-NNN`; served by `ASV-NNN` (cross-layer) |
| `ASV-NNN` (Application Service) | `APR-NNN` or `APP-NNN` (within-layer realization) |
| `APP-NNN` (Application Component) | Served by `TSV-NNN` (technology layer) |

---

## 11.9 Business Layer Architecture Modeling Pattern

### 11.9.1 The Outside-In Principle (mandatory progression)

Business architecture is built **from the outside in**: from what stakeholders receive, to what behavior delivers it, to what structure enacts that behavior. This order is non-negotiable — modeling internal structure first, before the services and value it must deliver, produces an inward-looking model that misses scope and confuses diagrams.

The mandatory modeling progression for any sprint that produces or revises business-layer content:

| Step | What to model | ArchiMate elements | Question answered |
|---|---|---|---|
| 1 | **Value streams and their stages** | `VS-NNN` with stages in `§content` | What value flows are we supporting? Who receives value at each stage? |
| 2 | **Business services, interfaces, and key objects/concepts** | `BSV-NNN`, `BIF-NNN`, `BOB-NNN` | What does the stakeholder receive? What concepts persist across stages? |
| 3 | **Business processes, interactions, and events** | `BPR-NNN`, `BIA-NNN`, `BEV-NNN` | How is the service produced step by step? What triggers each step? |
| 4 | **Business functions** | `BFN-NNN` | What are the stable organizational groupings that own process clusters? |
| 5 | **Roles and collaborations** | `ACT-NNN`, `BCO-NNN` | Who is assigned to each function and process? |
| 6 | **Detailed sub-behavior** | BPMN / Activity diagrams | What is the granular flow inside complex processes or interactions? |

Skipping ahead (e.g., defining roles before services, or defining processes before identifying which services they realize) produces models that are internally coherent but externally irrelevant.

---

### 11.9.1a Process Structure: Inner Decomposition and Outer Coordination

Behavior at the business layer is structured at **two distinct levels**. Conflating them produces diagrams that are either incomprehensibly flat or artificially fragmented.

#### Inner decomposition (within a process or interaction)

A top-level `BPR-NNN` or `BIA-NNN` is composed of **ordered stages** (sub-processes or sub-interactions). Stages are behavioral steps: each has a clear start condition, does one thing, and passes its result to the next stage. Stages within a process are connected by:

- **`flow`**: information or material passes from one stage to the next. Use when the output of stage A is a direct input to stage B — the progression is data-driven.
- **`triggering`**: stage A causally starts stage B. Use when B would not start without A completing, regardless of what data passes.

In PlantUML, nest sub-stage elements inside the parent behavior block. The parent alias itself must be the top-level process/interaction (`BPR-NNN` / `BIA-NNN`) — not a separate grouping wrapper with a duplicated parent node:

```plantuml
rectangle "Sprint Planning" <<BusinessProcess>> as BPR_001 {
  rectangle "Evaluate Phase State" <<BusinessProcess>> as BPR_101
  rectangle "Select Invocations" <<BusinessProcess>> as BPR_102
  rectangle "Dispatch Sprint" <<BusinessProcess>> as BPR_103

  BPR_101 -[#B8860B]-> BPR_102 : <<flow>>
  BPR_102 -[#B8860B]-> BPR_103 : <<flow>>
}
```

Parent→stage `archimate-composition` connection files are still required in the model repository; the nested rendering is the preferred operational viewpoint presentation.

**Stage-count rule (mandatory):** There is no fixed default stage count (for example, "always three"). Decompose into a manageable number of stages that matches solution-domain behavior and preserves readability. If decomposition grows too large to remain understandable in one parent container, split by separation of concerns into additional top-level processes/interactions and connect them via direct/event-mediated coordination.

**When to show inner stages in the operational ArchiMate diagram vs. Activity/BPMN diagram:**
- ArchiMate operational diagram: show the key stages of a process when they have distinct roles, objects, or outcomes visible at the business level (count is domain-dependent; no fixed template).
- Activity/BPMN diagram: show all branching, conditions, and fine-grained step-level logic. This is the complete internal specification.
- If a process is simple enough to summarize in one box, do not decompose it in the ArchiMate diagram. Decompose in Activity/BPMN only.

#### Outer coordination (between top-level processes)

Top-level processes coordinate through one of two mechanisms:

**Direct triggering (`BPR-A → BPR-B` or `BPR-A → BIA-B`):**
One process synchronously starts another within the same operational boundary. No event entity is created. Use when:
- The coupling is tight and unconditional: B always starts immediately when A completes.
- Both processes are in the same functional cluster (same `BFN-NNN`) or the same sprint cycle.
- The trigger is a control dependency, not an architectural fact worth making externally visible.

**Event-mediated triggering (`BPR-A → BEV-N → BPR-B`):**
Process A raises a business event; process B receives it. Use when:
- The trigger crosses a functional boundary (different `BFN-NNN`) or an operational cluster boundary.
- The signal is a **significant business fact** worth making architecturally visible — e.g., "Gate Passed", "Sprint Closed", "Engagement Completed". Making these facts explicit helps stakeholders understand what the system produces, not just how it flows.
- Multiple processes could react to the same event (fan-out).
- The trigger is asynchronous or conditional on EventStore state observed later.

**Decision rule (apply in order):**

| Condition | Use |
|---|---|
| B always starts immediately when A completes, same cluster | Direct `BPR-A → BPR-B` triggering |
| A produces a named business fact (a gate outcome, a sprint boundary, an escalation) | BEV entity + `BPR-A → BEV-N` + `BEV-N → BPR-B` |
| Signal crosses a functional boundary (different BFN) | BEV entity as boundary marker |
| Multiple processes may react to the same outcome | BEV entity (fan-out) |

**Connection file locations:**
- Inner flow: `connections/archimate/flow/<BPR-A>---<BPR-B>.md`
- Outer direct triggering: `connections/archimate/triggering/<BPR-A>---<BPR-B>.md`
- Process raises event: `connections/archimate/triggering/<BPR-A>---<BEV-N>.md`
- Event initiates process: `connections/archimate/triggering/<BEV-N>---<BPR-B>.md`

**Both directions of every process must be visible in the operational diagram.** A process without a triggering-IN (or the engagement start event) is unreachable. A process without a triggering-OUT and without a realization as its terminal output is a dead end — the reader cannot trace what happens after it completes.

### 11.9.2 Value Stream Stage Requirements

Value stream entities (`VS-NNN`) must have named stages in their `§content` section. Stages are **not** ADM phases — they describe what value the organization delivers to stakeholders, not how the architecture process is organized.

Each stage must specify:
- A name (noun phrase)
- The consuming stakeholder (STK-NNN or role description)
- The value delivered at this stage
- The key business service(s) (BSV-NNN) that constitute the delivered value

Minimum 3–7 stages per value stream. A VS entity with no stages documented is a model gap that must be resolved before Phase B gate.

### 11.9.3 Business Concept Map

The set of business objects (`BOB-NNN`) and business interfaces (`BIF-NNN`) for an engagement must form a **globally coherent concept map**: every object is traceable to at least one VS stage and is read or written by at least one BPR, BIA, or BSV. Business events (`BEV-NNN`) that trigger process transitions are identified at this step, not later.

**A dedicated concept map diagram (`business-archimate-concept-v1.puml`) is always required** — it makes the BOB↔DOB cross-layer mappings and the BEV→BPR→BOB trigger-to-object flow explicit in a single place. File naming: `business-archimate-concept-v1.puml`. The diagram must show: all BOB entities with their BPR access connections (access lines), all BEV entities with their BPR triggering connections, and a note listing BOB↔DOB cross-layer associations.

**BOBs also appear in operational viewpoint diagrams.** Each `BOB-NNN` accessed by a process in the operational cluster must be included in the corresponding operational diagram as well as in the concept map. This is not duplication — the concept map shows the full set and cross-layer mappings; operational diagrams show which objects are relevant to each process cluster. BOBs must NOT appear in structural viewpoint diagrams (structural = functions/roles/services, no objects).

BOB entities at the business layer correspond to DOB (data objects) at the application layer. These mappings must be captured as `archimate-association` connection files in `connections/archimate/association/`.

### 11.9.4 Diagram Count and Scope

Multiple diagrams for separate aspects and viewpoints are normal and expected at any layer. The canonical minimum set for Phase B (§0.1 table) is a floor, not a ceiling. Common additional diagrams include:

- One value-stream use-case diagram per VS (showing stages as use cases, actors as initiators/consumers)
- One structural ArchiMate diagram per major function cluster when the system is large
- One operational ArchiMate diagram per VS stage or process cluster when flows are complex
- One BPMN/Activity diagram per process that has non-trivial branching or multi-party interaction

**Single vs. dual ArchiMate diagrams:** For small systems (≤ ~5 functions, ≤ ~8 processes, ≤ ~25 total elements), a single ArchiMate diagram may show both structural (functions, roles) and operational (processes, events, services) aspects together, provided the structural hierarchy is still legible. For larger systems, use separate structural and operational diagrams. The decision is a viewpoint judgment — document it in the diagram `purpose` frontmatter field.

The structural viewpoint always includes roles/actors and collaborations alongside functions — it shows who fills each function as well as what the function delivers. The operational viewpoint always includes roles/actors alongside processes — it shows who executes each process and what events drive it. What distinguishes them is the **primary organizing concept**: functions-first (structural) vs. processes/events-first (operational).

### 11.9.5 Application-to-Business-Layer Connection Patterns

The primary way of relating the application layer to the business layer — beyond BOB↔DOB concept mapping — is through serving and realization connections. In priority order:

| Relationship | Use case | ArchiMate relation |
|---|---|---|
| `ASV-NNN --serving--> BPR-NNN` | **Primary.** An application service supports execution of a business process. | Serving |
| `ASV-NNN --serving--> BFN-NNN` | An application service supports a stable business function. | Serving |
| `ASV-NNN --realization--> BSV-NNN` | Application service fulfills the full external contract of a business service. | Realization |
| `APP-NNN --realization--> BSV-NNN` | Simple case: one component is the sole complete implementor of a business service. Use sparingly. | Realization |
| `APP-NNN --serving--> BFN-NNN` | Structural overview: component supports a function without naming the specific process. | Serving |
| `APR-NNN --realization--> BPR-NNN` | Operational mirror view: explicitly showing application processes mirroring business processes (annotate with purpose). | Realization |

Every BPR and BFN in scope must have at least one application-layer serving or realization connection to it. A business process with no application-layer connection is either a deliberate manual/human-only process (annotate it as such) or a model coverage gap.

### 11.9.6 Sprint Coverage Completeness Check

Before casting a Phase B gate vote, verify:

| Element | Required minimum |
|---|---|
| `VS-NNN` | ≥ 3 named stages in `§content`; each stage names ≥ 1 BSV |
| `BSV-NNN` | ≥ 1 realizing BPR, BFN, or BIA; linked to ≥ 1 VS stage |
| `BPR-NNN` | ≥ 1 assigned ACT or BCO; ≥ 1 serving ASV (or annotated as manual) |
| `BFN-NNN` | ≥ 1 assigned ACT or BCO; realizes ≥ 1 BSV or CAP |
| `CAP-NNN` | Realized by ≥ 1 BFN, BPR, or ASV |
| `BEV-NNN` | Triggers ≥ 1 BPR |
| `BOB-NNN` | Accessed (read/write) by ≥ 1 BPR or BIA |

Any uncovered element is a BA defect. Fix the model, raise a CQ, or PM explicitly accepts the gap as a documented assumption before baselining.

### 11.9.7 Cross-Layer Traceability and Mutual Validation

Models and diagrams at different layers cross-validate each other through inter-layer connections. A model that is complete at one layer but has broken or missing connections to adjacent layers is architecturally incomplete — it cannot be reasoned about holistically, and gaps in traceability are gaps in accountability.

**Upward traceability (application → business → strategy):** Every application component or service must ultimately serve or realize a business process, function, or service. Every business process or function must realize a business service or capability. Every capability must trace to at least one business driver or value stream. A model element that cannot be traced upward to a stakeholder need or value stream is a candidate for removal or scope clarification.

**Downward traceability (strategy → business → application):** Every capability must have at least one business-layer realizer. Every business service must have at least one application-layer realizer or serving element. Every business process must be served by at least one application service. A model element that cannot be traced downward to an application-layer implementation is an unimplemented aspiration — flag it as a gap in Phase E.

**Completeness check during diagram authoring (D1 step):** When querying entities via `list_artifacts` / `search_artifacts`, also query connections with `list_connections(target=<entity-id>)` and `list_connections(source=<entity-id>)` to verify that both upward and downward connections exist. Any entity returned with zero connections in either direction is a model coverage issue to resolve before writing the diagram.

**Diagram cross-validation:** Where the same entity appears in diagrams at adjacent layers, its name, type, and relationships must be consistent. Inconsistency between a business-layer diagram and an application-layer diagram for the same entity or connection is an architectural error — not a tolerance (see §0.4).

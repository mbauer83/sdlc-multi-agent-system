---
schema-id: diagram-catalog
version: 2.0.0
status: Approved — ERP v2.0 alignment
governed-by:
  - framework/artifact-registry-design.md
  - framework/diagram-conventions.md
  - framework/artifact-schemas/entity-conventions.md
---

# Schema: Diagram Catalog

Defines ERP v2.0 rules for diagram artifacts stored in `diagram-catalog/`.

This schema supersedes legacy catalog-index patterns (`elements/*.yaml`, `connections/*.yaml`, `diagrams/index.yaml`).

---

## 1. Canonical Storage Model (ERP v2.0)

Diagram artifacts are first-class files with frontmatter metadata.

- Diagrams live in `diagram-catalog/diagrams/`.
- Two supported artifact forms:
  - PlantUML diagrams: `*.puml`
  - Matrix diagrams: `*.md`
- There is no `diagrams/index.yaml` in ERP v2.0.
- ModelRegistry discovers diagrams by scanning file frontmatter.

Related model truth lives outside the diagram catalog:

- Entity files: `model-entities/<layer>/.../*.md`
- Connection files: `connections/<lang>/<type>/*.md`

---

## 2. File Naming

### 2.1 PlantUML diagram filenames

Recommended pattern:

`<scope>-<view>-<purpose>-v<major>.puml`

Where `<scope>` is:

- an ADM phase token (`a`..`h`) only when the diagram is phase-scoped, or
- a purpose/scope token when the diagram is cross-phase.

Important:
- Do not use the producing ADM phase as filename scope for cross-phase/runtime views.
- `phase-produced` records production provenance; it does not determine diagram naming scope.

Examples:

- `business-archimate-structural-v1.puml`
- `lifecycle-activity-sprint-v1.puml`

### 2.2 Matrix diagram filenames

Recommended pattern:

`<scope>-matrix-<purpose>-v<major>.md`

Example:

- `motivation-matrix-driver-requirement-full-v1.md`

---

## 3. Required Frontmatter Fields

All diagram files in `diagram-catalog/diagrams/` must include YAML frontmatter.

### 3.1 Common required fields (`*.puml` and `*.md`)

| Field | Type | Validation |
|---|---|---|
| `artifact-id` | string | Unique within repository; stable identity for `read_artifact` and references |
| `artifact-type` | string | Must be `diagram` |
| `name` | string | Non-empty, concise human title |
| `version` | string | Semantic version string (for example `0.1.0`) |
| `status` | string | One of: `draft`, `baselined`, `deprecated` |
| `phase-produced` | string | One of: `Prelim`, `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H` |
| `owner-agent` | string | One of: `PM`, `SA`, `SwA`, `DO`, `DE`, `QA`, `PO`, `SM`, `CSCO` |

### 3.2 PlantUML-only required fields (`*.puml`)

| Field | Type | Validation |
|---|---|---|
| `diagram-type` | string | Must be one of diagram conventions supported types (for example `archimate-business`, `activity-bpmn`, `sequence`, `class-er`, `usecase`) |
| `purpose` | string | Non-empty statement of implementation/architecture intent |

### 3.3 Recommended fields (both forms)

| Field | Type | Validation |
|---|---|---|
| `engagement` | string | Engagement id when diagram is engagement-scoped |
| `domain` | string \| null | Domain slice or `null` for cross-domain views |
| `entity-ids-used` | list[string] | Entity IDs present in diagram body/matrix cells |
| `connection-ids-used` | list[string] | Connection IDs represented by links/relations |

---

## 4. Body Requirements

### 4.1 PlantUML diagrams (`*.puml`)

- Must compile under configured PlantUML runtime.
- Must use valid aliases and macros per diagram conventions.
- If using ArchiMate macros, include `_archimate-stereotypes.puml` and `_macros.puml` per conventions.
- Must not reference entity IDs or connection IDs that do not exist.

### 4.2 Matrix diagrams (`*.md`)

- Must include matrix structure and legend sufficient for deterministic interpretation.
- Rows/columns and relation cells must map to existing entity/connection IDs.
- If IDs are auto-linked, links must resolve to model artifact paths.

---

## 5. Status Lifecycle Rules

Diagram status follows ERP lifecycle:

1. `draft`:
- In-sprint authoring state.
- May reference draft entities/connections.

2. `baselined`:
- Ready for gate/signoff usage.
- Must reference only baselined entities/connections.

3. `deprecated`:
- Kept for history; not used for current decision flow.

Violations are enforced by model verifier checks (including draft-reference checks for baselined diagrams).

---

## 6. Validation Contract

Validation is performed through ModelVerifier and model MCP tools.

- Single file: `model_verify_file`
- Batch: `model_verify_all`

Validation scope includes:

1. Required frontmatter fields present and typed correctly.
2. Diagram type and phase values valid.
3. Referential integrity to entity/connection files.
4. Status lifecycle constraints.
5. PlantUML syntax and include/macro consistency for `*.puml`.

---

## 7. Tooling Contract (Current)

Diagram authoring and updates use model MCP writer tools:

- `model_create_diagram` for `*.puml`
- `model_create_matrix` for matrix `*.md`

Discovery/query uses model query tools:

- `model_query_search_artifacts`, `model_query_list_artifacts`,  `model_query_read_artifact`

No legacy `catalog_register()` flow is part of ERP v2.0 runtime.

---

## 8. Migration Note for Legacy References

If documentation references `elements/*.yaml`, `connections/*.yaml`, or `diagrams/index.yaml`, treat those references as historical and migrate to ERP v2.0 file-per-artifact conventions described above.

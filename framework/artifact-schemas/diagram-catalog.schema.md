---
schema-id: diagram-catalog
version: 1.0.0
status: Approved — Stage 4.5
governed-by: framework/diagram-conventions.md
---

# Schema: Diagram Catalog

Specifies the required fields and validation rules for all files in the `diagram-catalog/` directory structure. Governed by `framework/diagram-conventions.md §2–9`.

---

## 1. Sub-Catalog Element Record (`elements/<layer>/*.yaml`)

Each YAML file under `elements/<layer>/` is a list of element records.

### Required Fields

| Field | Type | Validation |
|---|---|---|
| `element_id` | string | Pattern per layer (see §1.1); unique within its sub-catalog namespace; never reused after deletion (tombstone-only) |
| `name` | string | Non-empty; unique within the sub-catalog file; ≤ 80 characters |
| `type` | string | Must be a valid ArchiMate element type or approved domain type (see §1.2) |
| `extends` | string \| null | `null` for engagement-local elements; `<catalog-root-relative-path>/<element_id>` for imported enterprise elements |
| `phase_introduced` | string | One of: `Prelim`, `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H` |
| `sprint_introduced` | integer | ≥ 1 |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | ≤ 200 characters. Required when element semantics are non-obvious or name is a common word |
| `cross_refs` | object | Cross-ontology links validated at D4 (see §1.3) |
| `superseded_by` | string | element_id that replaces this element; causes `catalog_lookup` to skip and redirect |

### 1.1 Element ID Patterns

| Sub-catalog file | ID pattern | Example |
|---|---|---|
| `motivation/stakeholders.yaml` | `STK-\d{3}` | `STK-001` |
| `motivation/drivers.yaml` | `DRV-\d{3}` | `DRV-001` |
| `motivation/goals.yaml` | `GOL-\d{3}` | `GOL-001` |
| `motivation/constraints.yaml` | `CON-\d{3}` | `CON-001` |
| `motivation/requirements.yaml` | `REQ-\d{3}` | `REQ-001` |
| `motivation/principles.yaml` | `PRI-\d{3}` | `PRI-001` |
| `business/actors.yaml` | `ACT-\d{3}` | `ACT-001` |
| `business/functions.yaml` | `BFN-\d{3}` | `BFN-001` |
| `business/processes.yaml` | `BPR-\d{3}` | `BPR-001` |
| `business/objects.yaml` | `BOB-\d{3}` | `BOB-001` |
| `business/services.yaml` | `BSV-\d{3}` | `BSV-001` |
| `business/events.yaml` | `BEV-\d{3}` | `BEV-001` |
| `application/components.yaml` | `CMP-\d{3}` | `CMP-001` |
| `application/interfaces.yaml` | `IFC-\d{3}` | `IFC-001` |
| `application/services.yaml` | `ASV-\d{3}` | `ASV-001` |
| `application/interactions.yaml` | `INT-\d{3}` | `INT-001` |
| `technology/nodes.yaml` | `NOD-\d{3}` | `NOD-001` |
| `technology/artifacts.yaml` | `ART-\d{3}` | `ART-001` |
| `technology/services.yaml` | `TSV-\d{3}` | `TSV-001` |
| `technology/networks.yaml` | `NET-\d{3}` | `NET-001` |
| `data/entities.yaml` | `DE-\d{3}` | `DE-001` |
| `data/attributes.yaml` | `DAT-\d{3}` | `DAT-001` |
| `data/relationships.yaml` | `DRL-\d{3}` | `DRL-001` |

### 1.2 Valid `type` Values

| Layer | Permitted type values |
|---|---|
| `motivation/` | `Stakeholder`, `Driver`, `Goal`, `Constraint`, `Requirement`, `Principle` |
| `business/` | `BusinessActor`, `BusinessRole`, `BusinessFunction`, `BusinessProcess`, `BusinessObject`, `BusinessService`, `BusinessEvent`, `BusinessCollaboration` |
| `application/` | `ApplicationComponent`, `ApplicationInterface`, `ApplicationService`, `ApplicationInteraction`, `ApplicationCollaboration`, `ApplicationEvent` |
| `technology/` | `TechnologyNode`, `TechnologyArtifact`, `TechnologyService`, `CommunicationNetwork`, `TechnologyCollaboration` |
| `data/` | `DataEntity`, `DataAttribute`, `DataRelationship` |

### 1.3 `cross_refs` Field Structure

`cross_refs` is an optional object with zero or more of the following keys. All values are element IDs referencing elements in other sub-catalogs.

| Key | From layer | To layer | Meaning |
|---|---|---|---|
| `realizes` | `application/` | `business/` | Application component/service realizes a business service |
| `serves` | `application/` | `business/` | Application component/interface serves a business actor |
| `linked_data_entity` | `business/objects/` | `data/entities/` | BusinessObject is the ArchiMate representation of a data entity |
| `hosted_on` | `application/components/` | `technology/nodes/` | Component is hosted on a technology node |
| `assigned_to` | `business/functions/` | `business/actors/` | Business function is assigned to an actor/role |
| `triggers` | `business/events/` | `business/processes/` | Business event triggers a business process |
| `associated_with` | any | any | Generic association when a specific relationship type is not applicable |

**Validation at D4:** If a `cross_refs` value is set, the referenced element ID must exist in the target sub-catalog. A broken reference raises ALG-C03.

---

## 2. Connections Record (`connections/*.yaml`)

Each connections file is a list of relationship records.

### Required Fields

| Field | Type | Validation |
|---|---|---|
| `connection_id` | string | Pattern per file (see §2.1); unique within file; never reused |
| `source` | string | element_id of the source element; must exist in an `elements/` sub-catalog |
| `target` | string | element_id of the target element; must exist in an `elements/` sub-catalog |
| `relationship_type` | string | One of the permitted values for the connections file (see §2.1) |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `label` | string | Human-readable label for the relationship; ≤ 60 characters |
| `notes` | string | Additional context; ≤ 200 characters |

### 2.1 Connections File Patterns and Permitted Relationship Types

| File | ID pattern | Permitted `relationship_type` values |
|---|---|---|
| `archimate.yaml` | `CON-A-\d{3}` | `Association`, `Composition`, `Aggregation`, `Realization`, `Assignment`, `Serving`, `Access`, `Influence`, `Triggering`, `Flow`, `Specialization` |
| `er-relationships.yaml` | `CON-E-\d{3}` | `one-to-one`, `one-to-many`, `many-to-many`, `zero-or-one-to-many`, `zero-or-one-to-one` |
| `sequence-links.yaml` | `CON-S-\d{3}` | `synchronous`, `asynchronous`, `return`, `create`, `destroy` |
| `process-flows.yaml` | `CON-P-\d{3}` | `sequence-flow`, `message-flow`, `default-flow`, `conditional-flow` |

---

## 3. Diagrams Index (`diagrams/index.yaml`)

The `diagrams/index.yaml` file is a list of diagram records, one per `.puml` file in the `diagrams/` directory.

### Required Fields

| Field | Type | Validation |
|---|---|---|
| `diagram_id` | string | Pattern `DGM-\d{3}`; unique within index |
| `title` | string | Non-empty; ≤ 100 characters |
| `diagram_type` | string | One of: `archimate-motivation`, `archimate-business`, `archimate-application`, `archimate-technology`, `usecase`, `class-er`, `sequence`, `activity-bpmn` |
| `puml_file_path` | string | Relative path from `diagram-catalog/` root; file must exist |
| `agent_owner` | string | One of: `SA`, `SwA`, `DE`, `DO`, `QA`, `PM`, `PO`, `SM`, `CSCO` |
| `phase` | string | One of: `Prelim`, `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H` |
| `elements_used` | list[string] | List of element IDs referenced in this diagram; must all exist in `elements/` sub-catalogs |
| `connections_used` | list[string] | List of connection IDs referenced in this diagram; must all exist in `connections/` files |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `domain` | string | Domain slice identifier (e.g., `payments`, `auth`); omit for cross-domain diagrams |
| `rendered_path` | string | Relative path to the rendered SVG in `rendered/`; populated after `render_diagram` runs |
| `sprint_produced` | integer | Sprint number when the diagram was first produced |
| `version` | integer | Version counter; increment on each update; matches `v<N>` in filename |
| `supersedes` | string | `diagram_id` of a previous version of this diagram |

---

## 4. _macros.puml Validation Rules

`_macros.puml` is auto-generated by `catalog_register`. The following invariants are checked by `validate_diagram`:

1. Every element in every `elements/<layer>/*.yaml` file must have a corresponding `!define` macro.
2. Macro name must follow the pattern: replace `-` with `_` in the element ID (e.g., `STK-001` → `STK_001`).
3. Total macro count must equal total element count across all sub-catalog files (ALG-C04 trigger).
4. No manually authored content may appear in `_macros.puml` (comment block `' Auto-generated` must be present as the first non-empty line).

---

## 5. Validation Rules for `catalog_register()` Tool

The `catalog_register()` tool validates before writing:

1. `element_id` matches the pattern for the target sub-catalog file.
2. `element_id` is unique within the sub-catalog file (no existing entry with same ID).
3. `name` is unique within the sub-catalog file.
4. `type` is a permitted value for the sub-catalog layer.
5. `extends` is either `null` or a valid path pointing to an existing enterprise catalog element.
6. `phase_introduced` is a valid ADM phase value.
7. `sprint_introduced` is a positive integer.
8. If `cross_refs` is set: all referenced element IDs exist in their target sub-catalog files (raises ALG-C03 on broken cross-reference).
9. Calling agent is SA (path constraint — only SA may call `catalog_register`; non-SA agents must use `catalog_propose`).

On validation failure: raise `CatalogSchemaError` with field name and reason; do not write.

---

## 6. Example Element Records

### motivation/stakeholders.yaml entry
```yaml
- element_id: STK-001
  name: "Chief Information Officer"
  type: Stakeholder
  extends: null
  phase_introduced: A
  sprint_introduced: 1
  description: "Senior executive responsible for IT strategy and architecture governance."
```

### data/entities.yaml entry
```yaml
- element_id: DE-001
  name: "Customer"
  type: DataEntity
  extends: "enterprise-repository/diagram-catalog/elements/data/entities.yaml/DE-002"
  phase_introduced: C
  sprint_introduced: 3
  description: "Individual or organisation that holds an account and places orders."
```

### application/components.yaml entry with cross_refs
```yaml
- element_id: CMP-001
  name: "Order Management Service"
  type: ApplicationComponent
  extends: null
  phase_introduced: C
  sprint_introduced: 3
  cross_refs:
    realizes: BSV-002
    hosted_on: NOD-001
```

### diagrams/index.yaml entry
```yaml
- diagram_id: DGM-001
  title: "Phase B Business Capability Map"
  diagram_type: archimate-business
  puml_file_path: diagrams/b-archimate-business-capability-map-v1.puml
  agent_owner: SA
  phase: B
  domain: null
  elements_used: [ACT-001, ACT-002, BFN-001, BFN-002, BSV-001]
  connections_used: [CON-A-001, CON-A-002]
  sprint_produced: 2
  version: 1
```

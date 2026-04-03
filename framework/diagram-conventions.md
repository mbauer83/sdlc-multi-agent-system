---
doc-id: diagram-conventions
version: 1.0.0
status: Approved — Stage 4.5
governs: All diagram production across all agent roles
---

# Diagram Conventions

Specifies the production, registration, and reuse of PlantUML (PUML) diagrams across all agent roles. This document is the canonical specification for all diagram work in the SDLC multi-agent system. Drift risk in a multi-agent architecture repository is acute — without a strict catalog-and-reuse protocol, the same actor or system will be drawn differently in every diagram.

---

## 1. Authoring Model

Agents author PlantUML source text directly. There is no intermediate "diagram spec" format that a tool generates PUML from.

**Rationale:** PUML is already a compact textual DSL. LLMs produce syntactically regular text reliably when given clear templates and rules. Adding a second intermediate format creates two translation steps without benefit.

**Division of responsibility:**

| What | Who |
|---|---|
| Author PUML text, following §7 templates | The agent (LLM), using `write_artifact` to write the `.puml` file |
| Catalog I/O: lookup, register, propose | Tools (`catalog_lookup`, `catalog_register`, `catalog_propose`) |
| Post-authoring validation | `validate_diagram` tool (checks catalog ID references + PUML structure) |
| Rendering to SVG | `render_diagram` tool (invokes plantuml CLI; run at sprint boundary commit) |

---

## 2. Catalog Structure

Two separate catalogs, each with identical internal package structure. Scope is structural — not a naming convention.

```
[enterprise-repository OR engagements/<id>/work-repositories/architecture-repository]/diagram-catalog/

  _macros.puml                       # Auto-generated !define macros for all catalog elements
                                     # Engagement version contains imported enterprise elements + engagement elements
  _archimate-stereotypes.puml        # Shared ArchiMate skinparam + stereotype library
                                     # (enterprise-repository version is canonical; engagement copies on import)
  elements/
    motivation/                      # ArchiMate Motivation layer
      stakeholders.yaml              # STK-nnn: stakeholders (map to ArchiMate Stakeholder)
      drivers.yaml                   # DRV-nnn: business drivers (map to ArchiMate Driver)
      goals.yaml                     # GOL-nnn: goals (map to ArchiMate Goal)
      constraints.yaml               # CON-nnn: architecture constraints (map to ArchiMate Constraint)
      requirements.yaml              # REQ-nnn: architecture requirements (map to ArchiMate Requirement)
      principles.yaml                # PRI-nnn: principles (map to ArchiMate Principle)

    business/
      actors.yaml                    # ACT-nnn: business actors/roles (map to ArchiMate Business Actor)
      functions.yaml                 # BFN-nnn: business functions (map to ArchiMate Business Function)
      processes.yaml                 # BPR-nnn: business processes (map to ArchiMate Business Process)
      objects.yaml                   # BOB-nnn: business objects / domain concepts
      services.yaml                  # BSV-nnn: business services (map to ArchiMate Business Service)
      events.yaml                    # BEV-nnn: business events

    application/
      components.yaml                # CMP-nnn: application components / microservices
      interfaces.yaml                # IFC-nnn: application interfaces / API endpoints
      services.yaml                  # ASV-nnn: application services
      interactions.yaml              # INT-nnn: application interactions

    technology/
      nodes.yaml                     # NOD-nnn: technology nodes / infrastructure
      artifacts.yaml                 # ART-nnn: technology artifacts (deployable units)
      services.yaml                  # TSV-nnn: technology services (DBs, message brokers, etc.)
      networks.yaml                  # NET-nnn: networks / communication paths

    data/
      entities.yaml                  # DE-nnn: canonical data entities (source of truth for Data Architecture)
                                     # Must match DE-nnn identifiers in data-architecture artifacts
      attributes.yaml                # DAT-nnn: entity attributes (referenced in ER diagrams, not in ArchiMate)
      relationships.yaml             # DRL-nnn: semantic data relationships (maps to ER cardinality constraints)

  connections/
    archimate.yaml                   # ArchiMate relationships: CON-A-nnn (association, composition, realization, etc.)
    er-relationships.yaml            # ER relationships: CON-E-nnn (one-to-many, many-to-many, etc.)
    sequence-links.yaml              # Sequence message flows: CON-S-nnn
    process-flows.yaml               # BPMN flows: CON-P-nnn (sequence flow, message flow, default flow)

  diagrams/
    <phase>-<diagram-type>-<subject>[-<domain>]-v<N>.puml
                                     # domain suffix optional; used when diagram scope is one domain slice

  rendered/
    <same-stem>.svg                  # SVG outputs; committed at sprint boundary
```

**Enterprise catalog:** `enterprise-repository/diagram-catalog/` — org-wide, long-lived elements. Writes require Architecture Board approval. Baseline: primary stakeholder roles, major enterprise systems, canonical enterprise data entities, shared infrastructure nodes, enterprise processes.

**Engagement catalog:** `engagements/<id>/work-repositories/architecture-repository/diagram-catalog/` — self-contained, per-engagement. Created and maintained by SA. Holds all elements used in this engagement's diagrams, including imported enterprise elements.

---

## 3. Element ID Namespaces

| Prefix | Ontological layer | Primary diagram type | Secondary uses |
|---|---|---|---|
| `STK-nnn` | Motivation | ArchiMate motivation overlay | Use Case (actors), gate records |
| `DRV-nnn` | Motivation | ArchiMate motivation overlay | Architecture Vision |
| `GOL-nnn` | Motivation | ArchiMate motivation overlay | Architecture Vision |
| `CON-nnn` | Motivation | ArchiMate motivation overlay | Safety Constraint Overlay cross-refs |
| `REQ-nnn` | Motivation | ArchiMate motivation overlay | Requirements Register cross-refs |
| `PRI-nnn` | Motivation | ArchiMate motivation overlay | Principles Catalog |
| `ACT-nnn` | Business | Use Case, Activity/BPMN | Sequence (lifelines), ArchiMate |
| `BFN-nnn` | Business | ArchiMate business | Phase B capability maps |
| `BPR-nnn` | Business | Activity/BPMN | Phase B process flows |
| `BOB-nnn` | Business | ArchiMate business | Phase B business objects |
| `BSV-nnn` | Business | ArchiMate business | Phase B services |
| `CMP-nnn` | Application | ArchiMate application, Sequence | Phase C-App component diagrams |
| `IFC-nnn` | Application | Sequence | API contract flows (Phase E) |
| `ASV-nnn` | Application | ArchiMate application | Phase C-App |
| `NOD-nnn` | Technology | ArchiMate technology | Phase D/E infrastructure |
| `ART-nnn` | Technology | ArchiMate technology | Deployment diagrams |
| `TSV-nnn` | Technology | ArchiMate technology | Phase D/E technology services |
| `DE-nnn` | Data | Class/ER | MUST match DA artifact DE-nnn identifiers |
| `DAT-nnn` | Data | Class/ER | Attribute declarations within ER diagrams |

**ID assignment rule:** IDs are assigned sequentially within each sub-catalog. SA assigns IDs; non-SA agents propose candidate IDs in their catalog-proposal handoff which SA validates and confirms.

---

## 4. Catalog Lifecycle

### 4.1 Engagement Bootstrap (Preliminary / Phase A)

SA creates the empty engagement catalog directory structure. If an enterprise catalog is configured in `enterprise-repository-config.yaml`:

1. Query `enterprise-repository/diagram-catalog/` for elements relevant to the engagement scope.
2. Import relevant entries into the engagement catalog, assigning new engagement-local IDs.
3. Set `extends: <enterprise-catalog-path>/<source-element-id>` on each imported element (cross-catalog traceability).
4. Add imported elements to `_macros.puml`.

No diagram work begins until bootstrap is complete (SA gate condition at Phase A entry).

**Import rule:** Enterprise elements are imported into the engagement catalog, not referenced in-place. Engagement PUML files reference only engagement-catalog IDs.

### 4.2 During Engagement

SA maintains the engagement catalog as the single authoritative source for all diagram production. Updates to `_macros.puml` happen synchronously with each element registration.

### 4.3 At Engagement Close

Enterprise Promotion Protocol (`framework/repository-conventions.md §12`) applies to catalog elements. SA nominates sufficiently general engagement elements (elements representing concepts that would recur across other engagements) for promotion. Architecture Board approves and adds to enterprise catalog.

---

## 5. Reuse-First Protocol (D1–D6 Sequence)

Every skill step that produces or updates a diagram executes this sequence. Governed by `framework/discovery-protocol.md §8` (Step 0.D) for the discovery phase; D1–D6 for the production phase.

### D1 — Catalog Query

Query the relevant ontological sub-catalog(s) for semantically matching elements:
- Business process or capability diagram → `elements/business/`
- Data model diagram → `elements/data/`
- Application component or interaction diagram → `elements/application/`
- Technology architecture diagram → `elements/technology/`
- Motivation / architecture vision diagram → `elements/motivation/`

Use `catalog_lookup(query, layer)` tool. Match on: name, type, cross-reference fields (e.g., `DE-nnn` in data-architecture artifact cross-references `DE-nnn` in `elements/data/entities.yaml`).

Also query the enterprise catalog for any new concepts not yet imported — if found, import before proceeding.

### D2 — Reuse or Draft New

For each concept required in the diagram:
- **Match ≥ 90% confidence** → use existing ID. Do not create a duplicate.
- **No match** → draft new element registration record using the sub-catalog YAML structure (§6 below). Assign a candidate ID (next available in sequence).

### D3 — Register New Elements (SA) / Propose (Non-SA)

- **SA:** Write new element records directly to the relevant `elements/<layer>/*.yaml` file. Update `_macros.puml` immediately.
- **Non-SA:** Call `catalog_propose(element_spec)` — emits `diagram.catalog-proposal` handoff to SA. Do not write to `diagram-catalog/` directly. Non-SA agents may write `.puml` files to their own work-repository `diagrams/` directory; SA integrates at phase transition.

### D4 — Catalog Integrity Check (SA only)

Before completing registration, validate:
- No duplicate ID within the namespace.
- No name collision within the sub-catalog.
- Cross-reference fields populated if the element links to another ontological layer (e.g., a `CMP-nnn` application component that realizes a `BSV-nnn` business service must have `realizes: BSV-nnn` in its record).
- `_macros.puml` is updated synchronously.

### D5 — Author PUML

**D5a:** Call `read_framework_doc("framework/diagram-conventions.md §7.<diagram-type>")` to load the authoritative boilerplate template for the diagram type being produced (e.g., `§7.sequence`, `§7.archimate-business`, `§7.class-er`).

**D5b:** Author the PUML source text:
- Substitute catalog IDs (from D1–D2) as PUML aliases throughout the template.
- Populate relationships from `connections/` data (identified in Step 0.D point 3).
- Add diagram-specific content per the artifact being produced.
- The LLM generates the PUML text directly — no intermediate spec format is used.

**D5c:** Call `write_artifact(<target-diagrams-dir>/<filename>.puml, <puml_content>)`. Filename convention: `<phase>-<diagram-type>-<subject>[-<domain>]-v<N>.puml`.

**D5d:** Update `diagrams/index.yaml`: add or update the entry (fields: `diagram_id`, `title`, `diagram_type`, `puml_file_path`, `domain`, `agent_owner`, `phase`, `elements_used[]`, `connections_used[]`).

### D6 — Validate

Call `validate_diagram(<puml_file_path>)` immediately after writing. The tool checks:
- All element aliases are registered catalog IDs (present in `_macros.puml`).
- `!include _macros.puml` is present.
- ArchiMate diagrams also include `!include _archimate-stereotypes.puml`.
- No free-floating labels (all elements declared via catalog alias macros).

**On validation errors:** Fix in the PUML text (amend via `write_artifact`) and call `validate_diagram` again. Do not emit `artifact.produced` until validation passes.

---

## 6. Write Authority

| Operation | SA | Non-SA agents |
|---|---|---|
| Write to `elements/<layer>/*.yaml` | Yes | No — use `catalog_propose` |
| Write to `connections/*.yaml` | Yes | No — use `catalog_propose` |
| Write to `_macros.puml` | Yes (auto-generated from elements) | No |
| Write `.puml` to `diagram-catalog/diagrams/` | Yes | No |
| Write `.puml` to own work-repo `diagrams/` | — | Yes |
| Assign element IDs | Yes (confirms) | Propose only |

Non-SA agents may draft element records and PUML files in their own directories. Handoff to SA via `diagram.catalog-proposal` event for integration.

---

## 7. PUML Authoring Templates

These templates are the **primary runtime specification** for diagram authoring. Agents load the relevant template via `read_framework_doc("framework/diagram-conventions.md §7.<type>")` at Step D5a and follow it exactly. The template provides the canonical header, `!include` lines, element declaration pattern, and relationship syntax for each diagram type.

---

### §7.archimate-motivation — Architecture Vision Motivation Overlay

Used in: SA Phase A (Architecture Vision), SA Phase H (change impact).

```plantuml
@startuml
!include _macros.puml
!include _archimate-stereotypes.puml

skinparam rectangle {
  BackgroundColor<<motivation>> LightYellow
  BorderColor<<motivation>> DarkGoldenrod
  BackgroundColor<<business>> LightBlue
  BorderColor<<business>> SteelBlue
}

' --- Stakeholders ---
rectangle "Stakeholder Name" <<motivation>> as STK-001
rectangle "Stakeholder Name 2" <<motivation>> as STK-002

' --- Drivers ---
rectangle "Driver Description" <<driver>> as DRV-001

' --- Goals ---
rectangle "Goal Description" <<goal>> as GOL-001

' --- Constraints ---
rectangle "Constraint Description" <<constraint>> as CON-001

' --- Relationships (ArchiMate association) ---
STK-001 --> GOL-001 : influences
STK-001 --> DRV-001 : associated with
DRV-001 --> GOL-001 : motivates
GOL-001 --> CON-001 : realizes

@enduml
```

**Rules:**
- Every stakeholder must map to a `STK-nnn` catalog ID.
- Drivers, goals, and constraints must map to their respective catalog IDs.
- Use ArchiMate stereotype labels (`<<motivation>>`, `<<driver>>`, `<<goal>>`, `<<constraint>>`).
- `_archimate-stereotypes.puml` defines all stereotype skinparams — do not redeclare them inline.

---

### §7.archimate-business — Business Architecture Capability/Service Map

Used in: SA Phase B (business architecture), PO Phase B (requirements scope).

```plantuml
@startuml
!include _macros.puml
!include _archimate-stereotypes.puml

skinparam rectangle {
  BackgroundColor<<business>> AliceBlue
  BorderColor<<business>> SteelBlue
  BackgroundColor<<businessService>> LightCyan
  BorderColor<<businessService>> CadetBlue
}

' --- Business Actors ---
rectangle "Actor Name" <<businessActor>> as ACT-001
rectangle "Actor Name 2" <<businessActor>> as ACT-002

' --- Business Functions (capabilities) ---
rectangle "Function Name" <<businessFunction>> as BFN-001
rectangle "Function Name 2" <<businessFunction>> as BFN-002

' --- Business Services ---
rectangle "Service Name" <<businessService>> as BSV-001

' --- Business Objects ---
rectangle "Object Name" <<businessObject>> as BOB-001

' --- Relationships ---
ACT-001 --> BFN-001 : performs
BFN-001 --> BSV-001 : realizes
BSV-001 --> BOB-001 : accesses
ACT-002 --> BSV-001 : uses

@enduml
```

**Rules:**
- All actors reference `ACT-nnn` catalog IDs.
- All functions reference `BFN-nnn` catalog IDs.
- Services reference `BSV-nnn`; business objects reference `BOB-nnn`.
- ArchiMate relationship labels (`performs`, `realizes`, `accesses`, `uses`, `triggers`, `associated with`, `composed of`) are mandatory on all arrows.

---

### §7.archimate-application — Application Architecture Component Overview

Used in: SA Phase C-App (application architecture component diagram).

```plantuml
@startuml
!include _macros.puml
!include _archimate-stereotypes.puml

skinparam rectangle {
  BackgroundColor<<applicationComponent>> LightGreen
  BorderColor<<applicationComponent>> DarkGreen
  BackgroundColor<<applicationService>> Honeydew
  BorderColor<<applicationService>> SeaGreen
  BackgroundColor<<applicationInterface>> MintCream
  BorderColor<<applicationInterface>> MediumSeaGreen
}

' --- Application Components ---
rectangle "Component Name" <<applicationComponent>> as CMP-001
rectangle "Component Name 2" <<applicationComponent>> as CMP-002

' --- Application Interfaces ---
rectangle "Interface Name" <<applicationInterface>> as IFC-001

' --- Application Services ---
rectangle "Service Name" <<applicationService>> as ASV-001

' --- Business Actor (external user) ---
rectangle "Actor Name" <<businessActor>> as ACT-001

' --- Relationships ---
ACT-001 --> IFC-001 : uses
IFC-001 --> CMP-001 : serves
CMP-001 --> ASV-001 : realizes
CMP-001 --> CMP-002 : uses

@enduml
```

**Rules:**
- Application components reference `CMP-nnn` catalog IDs.
- Interfaces reference `IFC-nnn`. Services reference `ASV-nnn`.
- External actors from `ACT-nnn` may appear as initiating elements.
- Each component that realizes a business service must carry the `realizes: BSV-nnn` cross-reference in the catalog (not in the PUML text, but verified at D4).

---

### §7.archimate-technology — Technology Architecture Node Diagram

Used in: SA/SwA Phase D/E (technology architecture), DO Phase E (infrastructure spec).

```plantuml
@startuml
!include _macros.puml
!include _archimate-stereotypes.puml

skinparam node {
  BackgroundColor<<technologyNode>> LightSteelBlue
  BorderColor<<technologyNode>> SlateBlue
}
skinparam database {
  BackgroundColor<<technologyService>> Lavender
  BorderColor<<technologyService>> MediumPurple
}

' --- Technology Nodes ---
node "Node Name" <<technologyNode>> as NOD-001
node "Node Name 2" <<technologyNode>> as NOD-002

' --- Technology Services (DBs, message brokers, etc.) ---
database "Service Name" <<technologyService>> as TSV-001

' --- Technology Artifacts (deployable units) ---
artifact "Artifact Name" as ART-001

' --- Application Components hosted on nodes ---
rectangle "Component Name" <<applicationComponent>> as CMP-001

' --- Relationships ---
NOD-001 --> CMP-001 : hosts
CMP-001 --> TSV-001 : uses
ART-001 --> NOD-001 : deployed on
NOD-001 --> NOD-002 : communicates with

@enduml
```

**Rules:**
- Technology nodes reference `NOD-nnn` catalog IDs.
- Technology services (databases, brokers) reference `TSV-nnn`. Artifacts reference `ART-nnn`.
- Application components hosted on nodes must use their `CMP-nnn` IDs from the application sub-catalog.
- Network paths (`NOD-nnn` → `NET-nnn` → `NOD-nnn`) may be added when network topology is in scope.

---

### §7.usecase — Use Case Diagram

Used in: SA Phase B (business capability/actor interaction), PO Phase B (requirements scope).

```plantuml
@startuml
!include _macros.puml

left to right direction

skinparam actor {
  BackgroundColor LightYellow
  BorderColor DarkGoldenrod
}
skinparam usecase {
  BackgroundColor AliceBlue
  BorderColor SteelBlue
}

' --- Actors (reference catalog ACT-nnn IDs) ---
actor "Actor Name" as ACT-001
actor "Actor Name 2" as ACT-002

' --- System boundary ---
rectangle "System Name" {
  usecase "Use Case 1" as UC-001
  usecase "Use Case 2" as UC-002
  usecase "Use Case 3 (extension)" as UC-003
}

' --- Relationships ---
ACT-001 --> UC-001
ACT-001 --> UC-002
ACT-002 --> UC-002
UC-003 .> UC-001 : <<extend>>

@enduml
```

**Rules:**
- Actors must reference `ACT-nnn` catalog IDs as their PUML alias.
- Use case labels are free-text but must map to functions (`BFN-nnn`) or services (`BSV-nnn`) in the diagram annotation (add a comment block at the bottom of the file mapping UC-nnn to BFN/BSV IDs).
- `<<include>>` and `<<extend>>` relationships are the only valid stereotype labels on use case arrows.

---

### §7.class-er — Class / Entity-Relationship Diagram

Used in: SA Phase C-Data (data entity model with PK/FK + cardinalities), SwA Phase D (domain model).

```plantuml
@startuml
!include _macros.puml

skinparam class {
  BackgroundColor LightCyan
  BorderColor CadetBlue
  ArrowColor SteelBlue
}

' --- Data Entities (reference catalog DE-nnn IDs) ---
' Note: class alias = DE-nnn ID; label = entity name
class "EntityName" as DE-001 {
  + id : UUID <<PK>>
  + attribute1 : String
  + attribute2 : Integer
  --
  # foreignKey : UUID <<FK>>
}

class "EntityName2" as DE-002 {
  + id : UUID <<PK>>
  + attribute1 : String
}

class "JunctionEntity" as DE-003 {
  + entity1Id : UUID <<FK>>
  + entity2Id : UUID <<FK>>
}

' --- Relationships with cardinalities ---
DE-001 "1" -- "0..*" DE-002 : has
DE-001 "1" -- "0..*" DE-003
DE-002 "1" -- "0..*" DE-003

@enduml
```

**Rules:**
- Entity class aliases MUST be the `DE-nnn` ID from `elements/data/entities.yaml`. This is a hard constraint — the entity must be registered in the catalog before the diagram is authored.
- Every relationship must show cardinality labels (`"1"`, `"0..*"`, `"1..*"`, `"0..1"`) on both ends.
- PK/FK annotations are required in the attribute block.
- A `DE-nnn` entity appearing in the ER diagram must have a linked ArchiMate Data Object (`BOB-nnn` with `linked_data_entity: DE-nnn`) in the business sub-catalog — this cross-ontology link is validated at D4.

---

### §7.sequence — Sequence Diagram

Used in: SA Phase C-App (key interaction flows), SwA Phase E (API contract flows).

```plantuml
@startuml
!include _macros.puml

skinparam sequence {
  ParticipantBackgroundColor AliceBlue
  ParticipantBorderColor SteelBlue
  ArrowColor SteelBlue
  LifeLineBorderColor Gray
}

' --- Participants (reference catalog CMP-nnn or ACT-nnn IDs as aliases) ---
actor "Actor Name" as ACT-001
participant "Component Name" as CMP-001
participant "Component Name 2" as CMP-002
database "Data Store" as TSV-001

' --- Interaction flows ---
ACT-001 -> CMP-001 : initiateOperation(params)
activate CMP-001

CMP-001 -> CMP-002 : delegateCall(data)
activate CMP-002

CMP-002 -> TSV-001 : query(criteria)
TSV-001 --> CMP-002 : result

CMP-002 --> CMP-001 : response
deactivate CMP-002

CMP-001 --> ACT-001 : confirmation
deactivate CMP-001

@enduml
```

**Rules:**
- All participant aliases MUST be `CMP-nnn`, `ACT-nnn`, `TSV-nnn`, or `NOD-nnn` catalog IDs.
- Message labels use the format `operationName(params)` for synchronous calls and `eventName` for asynchronous messages.
- Asynchronous messages use `->>` arrow syntax.
- `activate`/`deactivate` blocks are required for every participant that handles a request synchronously.
- Return arrows (`-->`) are required for all synchronous calls.
- Loops and alternatives use `loop`, `opt`, `alt`/`else` blocks with guard conditions.

---

### §7.activity-bpmn — Activity / BPMN-Overlay Process Diagram

Used in: SA Phase B (business process flows), SA/SwA Phase C/E (solution-level process specs).

```plantuml
@startuml
!include _macros.puml

skinparam activity {
  BackgroundColor AliceBlue
  BorderColor SteelBlue
  ArrowColor SteelBlue
  DiamondBackgroundColor LightYellow
  DiamondBorderColor DarkGoldenrod
}

' --- Swimlane pools (reference catalog ACT-nnn or SYS-nnn/CMP-nnn IDs) ---
|ACT-001|
' Pool label = Actor or System name from catalog
start

:Task Name;
note right: Annotation if needed

|CMP-001|
:Automated Step;

' --- Gateway (exclusive) ---
if (Condition?) then (yes)
  |ACT-001|
  :Task on true branch;
else (no)
  |CMP-001|
  :Task on false branch;
endif

' --- End ---
|ACT-001|
:Final Task;
stop

@enduml
```

**Rules:**
- Swimlane pool delimiters (`|ACT-nnn|`) MUST reference catalog IDs (`ACT-nnn` for business actors/organizations, `CMP-nnn` for system components).
- Only BPMN-compatible constructs: sequential tasks (`:Task;`), exclusive gateways (`if`/`else`/`endif`), parallel gateways (`fork`/`fork again`/`end fork`), start (`start`) and end (`stop` or `end`), intermediate events (`:<event_name>>`).
- Free-form branching syntax (direct `if`/`while` without swimlane context) is not permitted.
- Task names must be verb-object phrases (e.g., `:Submit Application;`, not `:Application;`).
- Gateways must have labelled condition branches (`(yes)` / `(no)`, or named conditions).

---

## 8. _macros.puml Structure

`_macros.puml` is auto-generated by the `catalog_register` tool when new elements are added. Agents do not write to it directly. Structure:

```plantuml
' Auto-generated by catalog_register — DO NOT EDIT MANUALLY
' Last updated: <ISO8601 timestamp>
' Element count: N

' --- motivation/ ---
!define STK_001 rectangle "Stakeholder Name" <<motivation>> as STK-001
!define DRV_001 rectangle "Driver Description" <<driver>> as DRV-001

' --- business/ ---
!define ACT_001 rectangle "Actor Name" <<businessActor>> as ACT-001
!define BFN_001 rectangle "Function Name" <<businessFunction>> as BFN-001

' --- application/ ---
!define CMP_001 rectangle "Component Name" <<applicationComponent>> as CMP-001

' --- technology/ ---
!define NOD_001 node "Node Name" <<technologyNode>> as NOD-001

' --- data/ ---
!define DE_001 class "EntityName" as DE-001
```

**Naming convention:** Macro name replaces `-` with `_` in the element ID (e.g., `STK-001` → `STK_001`). This avoids PUML identifier conflicts.

**Sync rule (ALG-C04):** If `_macros.puml` element count does not match the total element count across all `elements/` sub-catalogs, `validate_diagram` raises ALG-C04. SA must regenerate `_macros.puml` before further diagram authoring.

---

## 9. Sub-Catalog YAML Element Record Format

Each element in an `elements/<layer>/*.yaml` file follows this structure:

```yaml
- element_id: CMP-001          # Required; unique within this sub-catalog namespace; never reused
  name: "Component Name"       # Human-readable name; unique within sub-catalog
  type: applicationComponent   # ArchiMate element type or domain type (DE for data entities)
  description: "One sentence." # Optional; populated when element semantics are non-obvious
  extends: null                # null for engagement-local elements; <enterprise-catalog-path>/<id> for imported elements
  phase_introduced: B          # ADM phase when first registered
  sprint_introduced: 1         # Sprint number
  cross_refs:                  # Optional cross-ontology links; validated at D4
    realizes: BSV-001          # This component realizes business service BSV-001
    linked_data_entity: null   # For BOB-nnn: DE-nnn of the corresponding data entity
    hosted_on: NOD-001         # For CMP-nnn: infrastructure node
```

**Mandatory fields:** `element_id`, `name`, `type`, `extends`, `phase_introduced`, `sprint_introduced`.
**Optional fields:** `description`, `cross_refs`.

---

## 10. Reference Table

| Section | Governs |
|---|---|
| §1 | Authoring model: direct PUML vs. tool-generated |
| §2 | Catalog structure: directory layout, two-catalog model |
| §3 | Element ID namespaces (STK, ACT, CMP, DE, etc.) |
| §4 | Catalog lifecycle: bootstrap, import, engagement close |
| §5 | D1–D6 reuse-first protocol (discovery → authoring → validation) |
| §6 | Write authority table |
| §7 | PUML templates: archimate-motivation, archimate-business, archimate-application, archimate-technology, usecase, class-er, sequence, activity-bpmn |
| §8 | `_macros.puml` structure and sync rule |
| §9 | Sub-catalog YAML element record format |

**Cross-references:**
- `framework/discovery-protocol.md §8` — Step 0.D (Diagram Catalog Lookup in Discovery Scan)
- `framework/artifact-schemas/diagram-catalog.schema.md` — formal schema for sub-catalog YAML files
- `framework/algedonic-protocol.md` — ALG-C01 (duplicate ID), ALG-C02 (unauthorized write), ALG-C03 (broken cross-ontology link), ALG-C04 (_macros.puml out of sync)
- `framework/repository-conventions.md §12` — Enterprise Promotion Protocol (applies to catalog elements)
- `framework/agent-runtime-spec.md §3` — tool set definitions for `catalog_lookup`, `catalog_register`, `catalog_propose`, `validate_diagram`, `render_diagram`

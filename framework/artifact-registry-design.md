---
document: artifact-registry-design
version: 2.1.0
status: Approved — Stage 4.8d
last-updated: 2026-04-04
---

# Artifact Registry Design — Entity Registry Pattern

## 1. Purpose

This document specifies the **Entity Registry Pattern (ERP)** — the authoritative convention for storing, discovering, filtering, and referencing architecture artifacts within engagement work-repositories.

Three artifact categories are distinguished:

| Category | Description | Has `§display` | ID scheme |
|---|---|---|---|
| **Model entity** | An ArchiMate element instance (any layer/aspect). Can appear in diagrams. | Yes | `PREFIX-NNN` |
| **Model connection** | A typed relationship between model entities. Can appear in diagrams. | Yes | `SOURCE(--SOURCE)*---TARGET(--TARGET)*` |
| **Repository content** | Non-diagrammable artifact (decision record, learning, diagram file, doc). | No | `PREFIX-NNN` or filename |

The `artifact-type` value determines the category via the framework lookup table in §4–§5.

### 1.1 Design Principles

1. **One file per instance.** Every entity, connection, or repository-content artifact is its own file.
2. **Frontmatter is the single source of truth for metadata.** No secondary index files. The `ModelRegistry` (§6) is built by scanning frontmatter at startup.
3. **Entity files contain no cross-references.** All relational information lives in connection files. There is no `references` field on entity frontmatter.
4. **Entities are organised by ArchiMate layer/aspect.** All diagram language element types are subsumable under ArchiMate taxonomy, eliminating the need for separate per-language entity directories. A model entity can have multiple `§display` subsections — one per diagram language where it appears.
5. **`model-entities/`, `connections/`, and `diagram-catalog/` are top-level siblings within each repository.** All ArchiMate entity layer directories live under `model-entities/`. Within `connections/`, subdirectories encode diagram-language then connection-type. Within `diagram-catalog/`, produced diagrams live under `diagrams/` and blank per-type starting-point stubs live under `templates/`.
6. **Dependency is strictly one-way.** Connections reference entities via `source`/`target` fields. Diagrams reference entities and connections via their `§display` specs. Entity files have no knowledge of connections or diagrams.
7. **IDs are immutable.** Assigned at creation; never reused even after deprecation.

---

## 2. Directory Structure

### 2.1 Architecture Repository

```
engagements/<id>/work-repositories/architecture-repository/
  model-entities/                       ← all ArchiMate entity files grouped here
    motivation/
      stakeholders/     STK-001.md  STK-002.md  STK-003.md
      drivers/          DRV-001.md  DRV-002.md  DRV-003.md
      assessments/      ASS-001.md  ASS-002.md
      goals/            GOL-001.md  GOL-002.md  GOL-003.md
      outcomes/         OUT-001.md  OUT-002.md
      principles/       PRI-001.md  PRI-002.md  PRI-003.md
      requirements/     REQ-001.md  REQ-002.md  REQ-003.md  REQ-004.md  REQ-005.md
      constraints/      CST-001.md  CST-002.md
      meanings/         MEA-001.md
      values/           VAL-001.md  VAL-002.md
    strategy/
      capabilities/     CAP-001.phase-execution.md  CAP-002.artifact-production.md  CAP-003.multi-agent-orchestration.md
      value-streams/    VS-001.forward-sdlc.md   VS-002.brownfield-onboarding.md
      resources/        RES-001.some-resource.md  RES-002.other-resource.md
      courses-of-action/ COA-001.some-course.md  COA-002.other-course.md
    business/
      actors/           ACT-001.user.md
      roles/            ROL-001.some-role.md  ROL-002.other-role.md
      processes/        BPR-001.sprint-planning.md  BPR-002.skill-execution.md  BPR-003.cq-lifecycle.md
      functions/        BFN-001.some-function.md  BFN-002.other-function.md
      services/         BSV-001.business-architecture-service.md  BSV-002.app-technology-architecture-service.md
      events/           BEV-001.some-event.md  BEV-002.other-event.md
      objects/          BOB-001.some-object.md  BOB-002.other-object.md
      interfaces/       BIF-001.some-interface.md
      collaborations/   BCO-001.architecture-board.md
      products/         PRD-001.some-product.md
      contracts/        CTR-001.some-contract.md
      representations/  RPR-001.some-representation.md
    application/
      components/       APP-001.event-store.md  APP-002.model-registry.md  APP-003.learning-store.md
      services/         ASV-001.agent-invocation-service.md  ASV-002.artifact-io-service.md
      interfaces/       AIF-001.event-store-port.md  AIF-002.llm-client-port.md
      functions/        AFN-001.some-function.md  AFN-002.other-function.md
      events/           AEV-001.some-event.md
      data-objects/     DOB-001.workflow-event.md  DOB-002.engagement.md  DOB-003.learning-entry.md
      processes/        APR-001.some-process.md
      collaborations/   ACO-001.some-collaboration.md
    implementation/
      work-packages/    WP-001.some-package.md   WP-002.other-package.md
      deliverables/     DEL-001.some-deliverable.md  DEL-002.other-deliverable.md
      gaps/             GAP-001.some-gap.md  GAP-002.other-gap.md
      plateaus/         PLT-001.some-plateau.md
      events/           IEV-001.some-event.md
  connections/                          ← sibling to model-entities/
    archimate/
      realization/    APP-001---BSV-001.md   APP-002---BSV-001.md   APP-003---CAP-001.md
      serving/        APP-001---APP-003.md   APP-002---APP-004.md   APP-004---APP-005.md
      assignment/     ACT-001---ROL-001.md   ACT-002---ROL-001.md   ACT-003---ROL-002.md
      composition/    CAP-001---CAP-002.md   CAP-001---CAP-003.md
      aggregation/    BCO-001---ACT-001.md   BCO-001---ACT-002.md
      influence/      DRV-001---GOL-001.md   DRV-002---GOL-001.md   DRV-002---GOL-002.md
      triggering/     BPR-001---BPR-002.md   BPR-002---BPR-003.md
      flow/           BOB-001---APP-003.md
      access/         APP-001---DOB-001.md   APP-002---DOB-002.md   APP-003---DOB-003.md
      association/    STK-001---GOL-001.md   STK-002---GOL-002.md
      specialization/ ROL-001---ROL-002.md
    er/
      one-to-many/    DOB-001---DOB-002.md   DOB-001---DOB-003.md   DOB-002---DOB-004.md
      many-to-many/   DOB-003---DOB-005.md   DOB-004---DOB-006.md
      one-to-one/     DOB-001---DOB-007.md
    sequence/
      synchronous/    APP-001---APP-002.md   APP-002---APP-003.md   APP-003---APP-006.md
      asynchronous/   APP-003---APP-004.md   APP-004---APP-005.md
      return/         APP-002---APP-001.md   APP-003---APP-002.md
    activity/
      sequence-flow/  BPR-001---BPR-002.md   BPR-002---BPR-003.md   BPR-003---BPR-004.md
      message-flow/   ACT-001---APP-001.md   ACT-002---APP-002.md
    usecase/
      include/        BSV-001---BSV-002.md
      extend/         BSV-003---BSV-001.md
      actor-association/ ACT-001---BSV-001.md   ACT-001---BSV-002.md   ACT-002---BSV-003.md
  diagram-catalog/                      ← sibling to model-entities/ and connections/
    _macros.puml                        # Auto-generated from entity §display blocks — do not edit
    _archimate-stereotypes.puml         # Shared ArchiMate skinparam library
    diagrams/                           # All produced engagement diagrams
      phase-b-archimate-business-v1.puml      # Naming: <phase>-<type>-<subject>[-<domain>]-v<N>.puml
      phase-c-archimate-application-v1.puml   # Each starts with PUML header comment frontmatter (see §2.4)
      phase-c-class-er-v1.puml               # May reference entities from any ModelRegistry scope
      phase-b-activity-sprint-v1.puml
    templates/                          # Per-type starting stubs demonstrating structure and conventions
      archimate-business-template.puml  # Naming: <type>-template.puml
      class-er-template.puml            # Agents copy into diagrams/, rename, then adapt: add, remove,
      sequence-template.puml            # and rewire elements and connections for the specific diagram
    rendered/
      phase-b-archimate-business-v1.svg
  decisions/          ADR-001.md  ADR-002.md  ADR-003.md
  overview/
    architecture-vision.md
    ba-overview.md    aa-overview.md    da-overview.md
```

### 2.2 Technology Repository

```
engagements/<id>/work-repositories/technology-repository/
  technology/
    nodes/            NOD-001.md  NOD-002.md  NOD-003.md
    devices/          DEV-001.md
    system-software/  SSW-001.md  SSW-002.md  SSW-003.md
    services/         TSV-001.md  TSV-002.md  TSV-003.md
    artifacts/        ART-001.md  ART-002.md  ART-003.md
    networks/         NET-001.md
    functions/        TFN-001.md  TFN-002.md
    events/           TEV-001.md
    interfaces/       TIF-001.md  TIF-002.md
    processes/        TPR-001.md
  connections/
    archimate/
      realization/    ART-001---NOD-001.md   SSW-001---TSV-001.md
      serving/        NOD-001---APP-001.md   TSV-001---APP-003.md   TSV-002---APP-004.md
      assignment/     ART-001---NOD-001.md
      triggering/     TPR-001---TPR-002.md
      ...
  solutions/          SOL-001.md  SOL-002.md
  decisions/          ADR-001.md  ADR-002.md
  coding-standards/   (repository-content; not ERP model entities)
```

### 2.3 Technology Repository Structure Note

The technology-repository follows the same `model-entities/` / `connections/` / `diagram-catalog/` sibling layout as the architecture-repository (§2.1), with entity layer directories (`technology/nodes/`, `technology/system-software/`, etc.) nested under `model-entities/`.

### 2.4 Diagram File Frontmatter

`.puml` files in `diagram-catalog/diagrams/` and `diagram-catalog/templates/` carry metadata as a PUML header comment block. ModelRegistry strips the `' ` prefix from each line and parses the block as YAML. The full field specification is in `framework/diagram-conventions.md §9`.

Required fields for produced diagrams: `artifact-id`, `artifact-type: diagram`, `name`, `diagram-type`, `version`, `status`, `phase-produced`, `owner-agent`, `engagement`, `entity-ids-used`, `connection-ids-used`.

Required fields for template stubs: `artifact-id`, `artifact-type: diagram-template`, `name`, `diagram-type`, `owner-agent`, `engagement`.

### 2.5 Repository-Content Artifacts

Not model entities; no `§display` section; not organised in `model-entities/` layer directories.

| artifact-type | Location | Description |
|---|---|---|
| `architecture-decision` | `decisions/ADR-NNN.md` | Architecture Decision Records |
| `architecture-vision` | `overview/architecture-vision.md` | Phase A framing document |
| `domain-overview` | `overview/<domain>-overview.md` | Cross-entity summary; references IDs only |
| `safety-constraint-overlay` | `safety-repository/sco-<v>.md` | Holistic safety document |
| `architecture-contract` | `architecture-repository/ac-<v>.md` | Binding governance document |
| `coding-standard` | `technology-repository/coding-standards/` | Technical standard reference |
| `test-strategy` | `qa-repository/` | QA strategy document |
| `diagram` | `diagram-catalog/diagrams/*.puml` | PUML diagram file; frontmatter in header comment block (§2.4) |
| `diagram-template` | `diagram-catalog/templates/*.puml` | Blank per-type stub; frontmatter in header comment block (§2.4) |
| `learning-entry` | `agents/<role>/learnings/<ROLE>-L-NNN.md` | Agent learning record; stored at framework/agent level, not per-engagement |
| `repository-map` | `architecture-repository/` | Multi-repo engagement map |

---

## 3. Unified File Format

All model-entity and model-connection files share a three-part structure: YAML frontmatter, a `§content` section, and a `§display` section. Section boundaries are HTML comment markers (`<!-- §<name> -->`), parseable with the regex `<!-- §(\w+) -->`. Within `§display`, `## <language-id>` H2 headings delimit per-language subsections. Absence of a language subsection means the entity/connection does not appear in that diagram language.

### 3.0 Entity File Naming Convention

Entity filenames follow the format:

```
TYPEABBR-NNN.friendly-name.md
```

where `TYPEABBR-NNN` is the **formal artifact-id** (e.g. `CAP-001`, `APP-007`) and `friendly-name` is a human-readable slug derived from the entity's `name` field (lowercase, hyphen-separated, no special characters). The friendly-name is purely informational — all code resolves entities by their formal artifact-id only, ignoring the friendly-name portion. The centralized `entity_id_from_path(path)` function in `src/common/model_verifier.py` must be used everywhere a formal ID is extracted from a filename.

Examples:
- `CAP-001.phase-execution.md` — artifact-id `CAP-001`
- `APP-007.pm-agent.md` — artifact-id `APP-007`
- `BCO-001.architecture-board.md` — artifact-id `BCO-001`

**Connection files** use a different convention: the filename stem IS the artifact-id (e.g. `ACT-001---BPR-003.md`). Friendly names do not apply to connection files since their filename already carries semantic meaning through the source/target IDs.

### 3.1 Model Entity — Exemplar

```markdown
---
artifact-id: DOB-001
artifact-type: data-object
name: "WorkflowEvent"
version: 1.0.0
status: baselined
phase-produced: C
owner-agent: SwA
domain: core-platform
safety-relevant: false
produced-by-skill: SwA-PHASE-C-DATA
last-updated: 2026-04-03
engagement: ENG-001
---

<!-- §content -->

## WorkflowEvent

Immutable append-only record of every state transition in the SDLC workflow.
Persisted in the EventStore (SQLite); exported to YAML at sprint close.

## Properties

| Attribute | Value |
|---|---|
| Classification | Internal |
| PII | No |

## Notes

Composite primary key: (engagement_id, sequence_num).

<!-- §display -->

### archimate

```yaml
layer: application
element-type: DataObject
```

### er

```yaml
primary-key: id
attributes:
  id: UUID
  engagement_id: String
  event_type: String
  sequence_num: Integer
  timestamp: DateTime
  payload: JSON
```
```

### 3.2 Frontmatter Field Rules — Model Entities

| Field | Rule |
|---|---|
| `artifact-id` | Format `^[A-Z]+-[0-9]{3}$`; prefix must match entity-type per §4; must equal the leading segment of the filename (before the first `.`) — see §3.0 |
| `artifact-type` | Must be a value from §4 |
| `version` | Valid semver |
| `status` | `draft` \| `baselined` \| `deprecated` |
| `phase-produced` | `Prelim` \| `A` \| `B` \| `C` \| `D` \| `E` \| `F` \| `G` \| `H` |
| `owner-agent` | Must match RACI-accountable agent for this entity type |
| `safety-relevant` | Boolean; never omitted; default `false` |
| `last-updated` | ISO 8601 date |

### 3.3 Model Connection — Exemplar

```markdown
---
artifact-id: APP-001---BSV-001
artifact-type: archimate-realization
source: APP-001
target: BSV-001
version: 1.0.0
status: baselined
phase-produced: C
owner-agent: SwA
engagement: ENG-001
last-updated: 2026-04-04
---

<!-- §content -->

PM Agent (APP-001) realizes the Agent Orchestration service (BSV-001).

<!-- §display -->

### archimate

```yaml
relationship-type: Realization
direction: source-to-target
```
```

For multi-source or multi-target connections (e.g., ArchiMate Junction, shared dependency):

```markdown
---
artifact-id: APP-001--APP-002---BSV-001
artifact-type: archimate-association
source: [APP-001, APP-002]
target: BSV-001
...
---
```

The `source` and `target` fields accept either a single artifact-id string or a YAML list. The `artifact-id` is always the filename stem: sources joined by `--`, separated from targets by `---`, targets joined by `--`.

### 3.4 Frontmatter Field Rules — Model Connections

| Field | Rule |
|---|---|
| `artifact-id` | Format: `SOURCE(--SOURCE)*---TARGET(--TARGET)*`; must match filename stem |
| `artifact-type` | Must be a value from §5 |
| `source` | Single artifact-id string or YAML list |
| `target` | Single artifact-id string or YAML list |

All source/target artifact-ids must exist in the ModelRegistry; `write_artifact` raises `UnresolvedReferenceError` otherwise.

### 3.5 §content Section

Markdown body. For model entities: entity name as first `## ` heading, then a `## Properties` table, then optional `## Notes`. For model connections: optional prose description of the relationship.

### 3.6 §display Section

Present on all model-entity and model-connection files. Absent on repository-content artifact files (`write_artifact` raises `DisplaySectionForbiddenError` if present on a repository-content type).

**Supported language identifiers:** `archimate`, `er`, `sequence`, `activity`, `usecase`.

#### Per-language display spec — entities

**`### archimate`**
```yaml
layer: motivation | strategy | business | application | technology | implementation
element-type: <ArchiMate element type name>
```

**`### er`**
```yaml
primary-key: <field-name>
attributes:
  <name>: <type>
```

**`### sequence`**
```yaml
participant-type: actor | component | database | boundary | control | entity
label: "<display label>"     # defaults to entity name
```

**`### activity`**
```yaml
swimlane-label: "<pool/lane label>"    # for actors and systems used as swimlane pools
```

**`### usecase`**
```yaml
element-type: actor | system | usecase
system-boundary: "<boundary name>"     # if contained in a named system box; omit if not
```

#### Per-language display spec — connections

**`### archimate`**
```yaml
relationship-type: <ArchiMate relationship type name>
direction: source-to-target | target-to-source | undirected    # default: source-to-target
access-type: read | write | read-write    # Access connections only
label: "<optional label>"
```

**`### er`**
```yaml
source-cardinality: "1" | "0..1" | "1..*" | "0..*"
target-cardinality: "1" | "0..1" | "1..*" | "0..*"
label: "<optional relationship label>"
```

**`### sequence`**
```yaml
message-type: synchronous | asynchronous | return | create | destroy
label: "<operationName(params)>"
```

**`### activity`**
```yaml
flow-type: sequence-flow | message-flow | data-association
condition: "<guard expression>"    # omit if unconditional
```

**`### usecase`**
```yaml
relationship-type: include | extend | association | generalization
label: "<optional label>"
```

---

## 4. Model Entity Type Registry

### 4.1 Motivation Aspect — `architecture-repository/motivation/`

| artifact-type | Prefix | Directory | ArchiMate Element | Owner |
|---|---|---|---|---|
| `stakeholder` | `STK` | `stakeholders/` | Stakeholder | SA |
| `driver` | `DRV` | `drivers/` | Driver | SA |
| `assessment` | `ASS` | `assessments/` | Assessment | SA |
| `goal` | `GOL` | `goals/` | Goal | SA |
| `outcome` | `OUT` | `outcomes/` | Outcome | SA |
| `principle` | `PRI` | `principles/` | Principle | SA |
| `requirement` | `REQ` | `requirements/` | Requirement | PO (SA curates) |
| `architecture-constraint` | `CST` | `constraints/` | Constraint | SA |
| `meaning` | `MEA` | `meanings/` | Meaning | SA |
| `value` | `VAL` | `values/` | Value | SA |

### 4.2 Strategy Aspect — `architecture-repository/strategy/`

| artifact-type | Prefix | Directory | ArchiMate Element | Owner |
|---|---|---|---|---|
| `capability` | `CAP` | `capabilities/` | Capability | SA |
| `value-stream` | `VS` | `value-streams/` | Value Stream | SA |
| `resource` | `RES` | `resources/` | Resource | SA |
| `course-of-action` | `COA` | `courses-of-action/` | Course of Action | SA |

### 4.3 Business Layer — `architecture-repository/business/`

| artifact-type | Prefix | Directory | ArchiMate Element | Owner |
|---|---|---|---|---|
| `business-actor` | `ACT` | `actors/` | Business Actor | SA |
| `business-role` | `ROL` | `roles/` | Business Role | SA |
| `business-collaboration` | `BCO` | `collaborations/` | Business Collaboration | SA |
| `business-interface` | `BIF` | `interfaces/` | Business Interface | SA |
| `business-process` | `BPR` | `processes/` | Business Process | SA |
| `business-function` | `BFN` | `functions/` | Business Function | SA |
| `business-interaction` | `BIA` | `interactions/` | Business Interaction | SA |
| `business-event` | `BEV` | `events/` | Business Event | SA |
| `business-service` | `BSV` | `services/` | Business Service | SA |
| `business-object` | `BOB` | `objects/` | Business Object | SA |
| `contract` | `CTR` | `contracts/` | Contract | SA |
| `product` | `PRD` | `products/` | Product | PO |
| `representation` | `RPR` | `representations/` | Representation | SA |

### 4.4 Application Layer — `architecture-repository/application/`

**Owner agent for all application-layer entities: SwA (Software Architect / Principal Engineer).**  
Phase C output. SA reads these entities for traceability review (consulting) but does not write them.

| artifact-type | Prefix | Directory | ArchiMate Element | Owner |
|---|---|---|---|---|
| `app-component` | `APP` | `components/` | Application Component | SwA |
| `app-collaboration` | `ACO` | `collaborations/` | Application Collaboration | SwA |
| `app-interface` | `AIF` | `interfaces/` | Application Interface | SwA |
| `app-process` | `APR` | `processes/` | Application Process | SwA |
| `app-function` | `AFN` | `functions/` | Application Function | SwA |
| `app-interaction` | `AIA` | `interactions/` | Application Interaction | SwA |
| `app-event` | `AEV` | `events/` | Application Event | SwA |
| `app-service` | `ASV` | `services/` | Application Service | SwA |
| `data-object` | `DOB` | `data-objects/` | Data Object | SwA |

### 4.5 Technology Layer — `technology-repository/technology/`

| artifact-type | Prefix | Directory | ArchiMate Element | Owner |
|---|---|---|---|---|
| `node` | `NOD` | `nodes/` | Node | SwA |
| `device` | `DEV` | `devices/` | Device | SwA |
| `system-software` | `SSW` | `system-software/` | System Software | SwA |
| `tech-collaboration` | `TCO` | `collaborations/` | Technology Collaboration | SwA |
| `tech-interface` | `TIF` | `interfaces/` | Technology Interface | SwA |
| `path` | `PTH` | `paths/` | Path | SwA |
| `communication-network` | `NET` | `networks/` | Communication Network | SwA |
| `tech-process` | `TPR` | `processes/` | Technology Process | SwA |
| `tech-function` | `TFN` | `functions/` | Technology Function | SwA |
| `tech-interaction` | `TIA` | `interactions/` | Technology Interaction | SwA |
| `tech-event` | `TEV` | `events/` | Technology Event | SwA |
| `tech-service` | `TSV` | `services/` | Technology Service | SwA |
| `tech-artifact` | `ART` | `artifacts/` | Artifact | SwA |

### 4.6 Implementation & Migration Aspect — `architecture-repository/implementation/`

Note: `implementation-event` (IEV) is an ArchiMate milestone element tracking rollout and migration events, not a behavioral trigger. Behavioral events are `business-event` (BEV), `app-event` (AEV), and `tech-event` (TEV).

| artifact-type | Prefix | Directory | ArchiMate Element | Owner |
|---|---|---|---|---|
| `work-package` | `WP` | `work-packages/` | Work Package | PM |
| `deliverable` | `DEL` | `deliverables/` | Deliverable | PM |
| `implementation-event` | `IEV` | `events/` | Implementation Event | PM |
| `plateau` | `PLT` | `plateaus/` | Plateau | SA |
| `gap` | `GAP` | `gaps/` | Gap | SA |

### 4.7 Solutions — `technology-repository/solutions/`

| artifact-type | Prefix | Directory | Description | Owner |
|---|---|---|---|---|
| `solution-building-block` | `SOL` | `solutions/` | Concrete solution crossing TA/AA boundary | SwA |

---

## 5. Model Connection Type Registry

Connections live in `connections/<diagram-language>/<connection-type>/` relative to the owning repository root. The `artifact-type` in frontmatter encodes both language and type as `<language>-<connection-type>`.

### 5.1 ArchiMate Connections — `connections/archimate/`

| artifact-type | Directory | ArchiMate Relationship |
|---|---|---|
| `archimate-composition` | `composition/` | Composition |
| `archimate-aggregation` | `aggregation/` | Aggregation |
| `archimate-assignment` | `assignment/` | Assignment |
| `archimate-realization` | `realization/` | Realization |
| `archimate-specialization` | `specialization/` | Specialization |
| `archimate-serving` | `serving/` | Serving |
| `archimate-access` | `access/` | Access (read/write/read-write) |
| `archimate-influence` | `influence/` | Influence |
| `archimate-association` | `association/` | Association |
| `archimate-triggering` | `triggering/` | Triggering |
| `archimate-flow` | `flow/` | Flow |

### 5.2 ER Connections — `connections/er/`

| artifact-type | Directory | Cardinality |
|---|---|---|
| `er-one-to-one` | `one-to-one/` | 1:1 |
| `er-one-to-many` | `one-to-many/` | 1:N |
| `er-many-to-many` | `many-to-many/` | M:N |

### 5.3 Sequence Connections — `connections/sequence/`

| artifact-type | Directory | Message Type |
|---|---|---|
| `sequence-synchronous` | `synchronous/` | Synchronous call (`->`) |
| `sequence-asynchronous` | `asynchronous/` | Async message (`->>`) |
| `sequence-return` | `return/` | Return (`-->`) |
| `sequence-create` | `create/` | Object creation |
| `sequence-destroy` | `destroy/` | Object destruction |

### 5.4 Activity/BPMN Connections — `connections/activity/`

| artifact-type | Directory | BPMN Flow |
|---|---|---|
| `activity-sequence-flow` | `sequence-flow/` | Sequence flow |
| `activity-message-flow` | `message-flow/` | Message flow (dashed) |
| `activity-data-association` | `data-association/` | Data association |

### 5.5 Use Case Connections — `connections/usecase/`

| artifact-type | Directory | Relationship |
|---|---|---|
| `usecase-include` | `include/` | «include» |
| `usecase-extend` | `extend/` | «extend» |
| `usecase-association` | `actor-association/` | Actor–use-case line |
| `usecase-generalization` | `generalization/` | Generalization |

---

## 6. ModelRegistry

No `_index.yaml` files exist anywhere. The `ModelRegistry` is the in-process lookup service for model entities and connections within a given scope. It is populated by scanning frontmatter at startup and kept current by filesystem-watch events; this mechanism is an implementation detail invisible to callers.

### 6.1 Two Registry Scopes

One `ModelRegistry` instance per `EngagementSession`, initialised with **all** repository paths relevant to that engagement — both engagement-scope (writable by engagement agents) and enterprise-scope (read-only to engagement agents). Enterprise entities are referenced in-place: there is no copy or import step.

| Path set | Write access | Source |
|---|---|---|
| Engagement `architecture-repository/`, `technology-repository/` (+ additional model-bearing repos) | Engagement agents (owning role per `repository-conventions.md §2.1`) | Per-engagement work-repositories |
| `enterprise-repository/` (if configured in `enterprise-repository-config.yaml`) | Architecture Board members only; engagement agents have no write path | Organisation-wide shared canonical entities |

`write_artifact` raises `RegistryReadOnlyError` when an engagement agent attempts to write to an enterprise path. The enterprise repository is not frozen — Architecture Board members update, version, and expand it through normal enterprise governance, independently of any engagement.

**No copy/import:** Enterprise entities are visible in the unified registry alongside engagement entities. Agents discover them via the same `list`/`resolve` API. The `directory` filter, `domain` filter, or a dedicated `scope` filter (`enterprise` vs `engagement`) can be used to narrow results when needed. `_macros.puml` generation includes enterprise entities automatically — their `§display ###archimate` specs are read from the enterprise repository files directly.

**Engagement extensions of enterprise entities** are modelled as separate engagement entities connected to the enterprise entity via ArchiMate connection files (e.g., `archimate-specialization`, `archimate-realization` in `connections/archimate/`). The enterprise entity is never modified.

**ID spaces and promotion** (engagement → enterprise): Engagement-scope IDs (`CAP-001`, `APP-003`, etc.) are locally unique within the engagement only. Multiple concurrent engagements may independently create entities with the same ID; no cross-engagement reservation is feasible or required. Enterprise-scope IDs are globally unique, assigned from an enterprise-wide counter maintained in `enterprise-repository/governance-log/id-counters.yaml`.

On promotion, the Architecture Board assigns a new enterprise-scope ID (next available for the entity's prefix from `id-counters.yaml`). The `promote_entity` tool then:

1. Rewrites the entity frontmatter with the new ID, resets version to `1.0.0`, strips `engagement` and `produced-by-skill` fields.
2. Performs a deterministic reference sweep across all engagement artifacts — connection `source`/`target` fields, diagram PUML alias occurrences, and `[@old-id …]` inline references — replacing old-ID with new-enterprise-ID throughout.
3. Moves the entity file to the enterprise target path under the new ID.
4. Emits an `artifact.promoted` event recording both the old engagement-ID and the new enterprise-ID for audit traceability.

After promotion the entity lives in the enterprise repository, where it is read-only to engagement agents and maintained by Architecture Board members. Future engagements discover it via `list`/`resolve` at the enterprise path.

### 6.2 Interface

```python
# src/common/model_registry.py

class ModelRegistry:
    def __init__(
        self,
        repository_paths: list[Path],
        read_only: bool = False,
    ) -> None:
        """Initialise and populate from all given repository paths.
        read_only=True flags enterprise paths — write_artifact raises
        RegistryReadOnlyError if an engagement agent targets a read-only path.
        Architecture Board members bypass this flag via a separate governance path."""

    def resolve(self, artifact_id: str) -> Path | None:
        """Return the absolute file path for an artifact-id, or None if not found."""

    def list(
        self,
        directory: str | None = None,
        **filters: str | bool,
    ) -> list[dict]:
        """Return frontmatter dicts for all matching entries. Never loads file bodies.
        directory: path prefix relative to any registered repository root (optional).
        filters: artifact-type, status, domain, safety-relevant, phase-produced,
                 source (connections), target (connections)."""

    def update(self, path: Path, frontmatter: dict) -> None:
        """Called by write_artifact after a successful write."""

    def remove(self, path: Path) -> None:
        """Called on file deletion (watchdog event)."""

    def is_read_only(self) -> bool: ...
```

### 6.3 Population and Freshness

| Event | Action |
|---|---|
| Startup | Scan all `.md` files recursively under each registered path; parse YAML frontmatter; populate internal index |
| `write_artifact` writes a file | Calls `registry.update(path, frontmatter)` synchronously |
| File modified externally | `watchdog` `FileModifiedEvent` → re-parse → `registry.update()` |
| File deleted externally | `watchdog` `FileDeletedEvent` → `registry.remove()` |

Never persisted. Rebuilt from source files on every session start. Cold-start time is O(entity count) — typically under 1 second for engagements up to a few thousand files.

### 6.4 Filters

All filters AND-combined:

| Filter | Values |
|---|---|
| `artifact-type` | Any type from §4–§5 |
| `status` | `draft`, `baselined`, `deprecated` |
| `domain` | bounded-context label |
| `safety-relevant` | `true`, `false` |
| `phase-produced` | ADM phase code |
| `source` | artifact-id (connections only) |
| `target` | artifact-id (connections only) |

Returns `list[{artifact-id, name, artifact-type, version, status, domain, safety-relevant, file}]`.

---

## 7. ID Assignment Rules

**Model entities:** IDs are `PREFIX-NNN`, assigned in ascending sequence within each type. `write_artifact` queries ModelRegistry for the highest existing NNN under the target prefix and assigns NNN+1. Sequence numbers are never reused; deprecated entities keep their ID.

**Model connections:** ID = `<source1>(--<sourceN>)*---<target1>(--<targetN>)*`, constructed deterministically from the `source` and `target` frontmatter fields. Within a connection-type directory the (source-set, target-set) pair is unique. `write_artifact` raises `DuplicateConnectionError` if the same combination already exists.

---

## 8. Discovery and Retrieval Protocol

```
Step 1: list_artifacts(directory, **filter)
  → queries ModelRegistry; returns matching metadata list; no filesystem I/O

Step 2: read_artifact(artifact_id_or_path, mode="summary"|"full")
  → resolves artifact-id to path via ModelRegistry
  → mode="summary": frontmatter + §content first two ## sections only
  → mode="full": entire file

Step 3 (connections): list_artifacts("connections/archimate/realization", source="APP-001")
  → all realization connections originating from APP-001
```

Confidence thresholds from `repository-conventions.md §4` apply per-entity:

- **Cache query only** — task scoping, gap identification, count-based decisions
- **Summary read** — dependency mapping, cross-reference resolution, diagram authoring
- **Full read** — required when producing a binding output that semantically depends on full entity content

---

## 9. Model-First Rule

The dependency chain is strictly one-way: **entity files ← connection files ← diagram files**.

Entity files have no knowledge of connections or diagrams. Connections reference entities via `source`/`target` fields — `write_artifact` raises `UnresolvedReferenceError` if a referenced entity does not exist in the ModelRegistry. Diagrams are built from entity and connection `§display` specs (via `_macros.puml`); a diagram element with no backing entity/connection in the model is a `validate_diagram` error (ALG-C03).

Entity instances, connections, and their `§display` specs may freely exist without any diagram referencing them. This is the normal state in reverse architecture and repository-building workflows, where the model is populated before any diagram is drawn.

---

## 10. Tool Contracts

| Tool | Contract |
|---|---|
| `write_artifact(path, content)` | Validates frontmatter (type, required fields, prefix match); validates `source`/`target` reference resolution for connections; validates section structure (`§content` present; `§display` present iff model-entity or model-connection; language subsection YAMLs valid per §3.6); writes file; updates ModelRegistry; emits `artifact.drafted` or `artifact.updated` |
| `read_artifact(id_or_path, mode)` | Resolves id → path via ModelRegistry; reads at specified mode |
| `list_artifacts(directory, **filter)` | Queries ModelRegistry; returns metadata list; never loads file bodies |
| `list_connections(source=None, target=None, artifact_type=None)` | Convenience wrapper over `list_artifacts` scoped to `connections/`; filters by source id, target id, or connection type |

Full specifications in `framework/agent-runtime-spec.md §6`.

---

## 11. Authoring Rules

**ERP-1:** Every model-entity and model-connection file must have valid YAML frontmatter. `write_artifact` rejects files with absent or incomplete frontmatter (`FrontmatterValidationError`).

**ERP-2:** Entity files contain no cross-references to other entities. All relational information belongs in connection files. Entity frontmatter has no `references` field.

**ERP-3:** `list_artifacts` and `read_artifact` are the only permitted access paths. Direct filesystem path construction by agents is prohibited.

**ERP-4:** Overview and domain-summary documents reference entity IDs only; they never duplicate entity content inline.

**ERP-5:** Skill files produce entities individually — one `write_artifact` call per entity instance, not batched. Overview documents are written after all entities in the domain are produced.

**ERP-6:** The `§display` section is mandatory on model-entity and model-connection files and forbidden on repository-content artifact files. `write_artifact` raises `DisplaySectionError` on violation.

---

## 12. Migration from Pre-ERP Artifacts

For engagements with monolithic pre-ERP artifacts (e.g., `ba-1.0.0.md` with all capabilities as table rows):

1. SA runs migration skill: reads monolithic file; creates one entity file per instance using ERP format; extracts implied relationships into connection files.
2. Version continuity: entities inherit the domain baseline version.
3. Original file archived to `_archive/`.
4. EventStore emits `artifact.migrated` per entity.

For `ENG-001` (no pre-ERP artifacts): create fresh using ERP from the start.

---
document: entity-conventions
version: 2.0.0
status: Approved — Stage 4.8
governs: All model-entity and model-connection files
---

# Entity and Connection File Conventions

Universal format for all model-entity and model-connection files. Governed by `framework/artifact-registry-design.md`. Every file must conform to this specification. The `write_artifact` tool enforces compliance; non-conforming writes are rejected with `FrontmatterValidationError` or `DisplaySectionError`.

---

## 1. File Structure

Every model-entity and model-connection file has three parts, delimited by HTML comment markers parseable with `<!-- §(\w+) -->`:

```
---
<YAML frontmatter — mandatory, limited, for indexing/filtering>
---

<!-- §content -->

<Markdown body — human-readable description, properties, notes>

<!-- §display -->

### <language-id>

```yaml
<rendering spec for this diagram language>
```

### <language-id>

```yaml
<rendering spec for this diagram language>
```
```

Section rules:
- **Frontmatter**: mandatory on all files; fields defined in §2.
- **`§content`**: mandatory on model-entity and model-connection files; markdown body with type-specific sections per §3.
- **`§display`**: mandatory on model-entity and model-connection files; forbidden on repository-content artifact files. Contains one `### <language-id>` subsection per diagram language where the entity/connection appears. Absence of a language subsection means the entity/connection does not appear in that language.

---

## 2. Frontmatter Schema

### 2.1 Model Entities

```yaml
---
artifact-id: <PREFIX>-<NNN>         # e.g. APP-003, DOB-012, BPR-007. Immutable once created.
artifact-type: <entity-type>         # From artifact-registry-design.md §4
name: "<Human-readable entity name>"
version: <semver>                    # 0.x.x = draft; 1.0.0+ = baselined
status: draft | baselined | deprecated
phase-produced: Prelim|A|B|C|D|E|F|G|H
owner-agent: SA | SwA | PM | PO | DO | DE | QA | CSCO
domain: <bounded-context-label>     # Omit for cross-cutting entities
safety-relevant: false              # Boolean; never omitted
produced-by-skill: <skill-id>
last-updated: <YYYY-MM-DD>
engagement: <engagement-id>
---
```

### 2.2 Model Connections

```yaml
---
artifact-id: <source>(--<source>)*---<target>(--<target>)*@@<artifact-type>
artifact-type: <connection-type>     # From artifact-registry-design.md §5 (e.g. archimate-realization)
source: <artifact-id> | [<artifact-id>, ...]
target: <artifact-id> | [<artifact-id>, ...]
version: <semver>
status: draft | baselined | deprecated
phase-produced: Prelim|A|B|C|D|E|F|G|H
owner-agent: SA | SwA | PM | PO | DO | DE | QA | CSCO
engagement: <engagement-id>
last-updated: <YYYY-MM-DD>
---
```

### 2.3 Required Field Rules

| Field | Validation Rule |
|---|---|
| `artifact-id` | Entities: `^[A-Z]+-[0-9]{3}$`; prefix must match entity-type per §4 of artifact-registry-design.md. Connections: `SOURCE(--SOURCE)*---TARGET(--TARGET)*@@artifact-type`; must match filename stem. |
| `artifact-type` | Must be a value from the canonical registry in `src/common/archimate_types.py` (`ALL_ENTITY_TYPES` for entities; `ALL_CONNECTION_TYPES` for connections). See §4 of this file for the full table. |
| `version` | Valid semver |
| `status` | One of: `draft`, `baselined`, `deprecated` |
| `phase-produced` | One of: `Prelim`, `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H` |
| `safety-relevant` | Boolean; must be explicit on entity files |
| `source` / `target` | Connection files only; all referenced ids must exist in ModelRegistry |
| `last-updated` | ISO 8601 date (`YYYY-MM-DD`) |

### 2.4 Repository Scope Rules (Enterprise vs Engagement)

This framework operates with two architecture repository scopes:

- **Engagement scope** (per-project/per-engagement work-repositories)
- **Enterprise scope** (`enterprise-repository/`, read-only to engagement agents)

Rules:

1. **Reference scope**
  - **Enterprise-scope** entity/connection/diagram artifacts may reference **only enterprise-scope** artifact-ids.
  - **Engagement-scope** artifacts may reference artifact-ids in **their own engagement scope** and in the **enterprise scope**.
  - Engagement artifacts must not reference artifacts from *other engagements* (those are not part of the session’s unified registry).

2. **`engagement` frontmatter field in enterprise scope**
  - On promotion (engagement → enterprise), the Architecture Board’s `promote_entity` / `promote_connection` tools strip the `engagement` field.
  - The unified ModelRegistry derives `engagement="enterprise"` for enterprise-scope artifacts at index time (path-derived metadata), enabling discovery filters like `list_artifacts(engagement="enterprise")`.
  - Engagement-scope artifacts must still include `engagement: <engagement-id>` as defined in §2.1–§2.2.

3. **Artifact-id uniqueness within a unified registry**
  Within a single EngagementSession’s unified registry (the mounted set of roots for that engagement), **the same `artifact-id` must not exist in more than one mounted repository root**. If duplicates exist, indexing/verification must fail loudly.

---

## 3. §content Section

### 3.1 Model Entity Body Structure

```markdown
<!-- §content -->

## <Entity Name>

<1–3 sentence description.>

## Properties

<Type-specific attribute table — see §4 per entity type.>

## Notes

<Optional: constraints, assumptions, open questions. Omit section if empty.>
```

The `## <Entity Name>` heading must match the `name` frontmatter field exactly. The `## Properties` section is mandatory. The `## Notes` section is optional and omitted when empty.

### 3.2 Model Connection Body Structure

```markdown
<!-- §content -->

<Optional 1–3 sentence description of the relationship. Omit if self-evident from source/target names.>
```

Connections have no `## ` heading structure in §content — the body is free-form prose (or empty).

---

## 3.3 Canonical Type Registry

**Authoritative source:** `src/common/archimate_types.py`

The verifier imports `ALL_ENTITY_TYPES` and `ALL_CONNECTION_TYPES` directly from that module. The tables below are authoritative documentation that must be kept in sync with the code. If they diverge, the code wins — update this file to match.

### Valid `artifact-type` values for entity files

Entity types are organised by ArchiMate layer/aspect. ArchiMate subsumes all entity types — there are no separate entity ontologies for activity, sequence, or class diagram languages.

| Layer | Valid `artifact-type` values |
|---|---|
| Motivation | `stakeholder`, `driver`, `assessment`, `goal`, `outcome`, `principle`, `requirement`, `architecture-constraint`, `meaning`, `value` |
| Strategy | `capability`, `value-stream`, `resource`, `course-of-action` |
| Business | `business-actor`, `business-role`, `business-collaboration`, `business-interface`, `business-process`, `business-function`, `business-interaction`, `business-event`, `business-service`, `business-object`, `contract`, `representation`, `product` |
| Application | `application-component`, `application-collaboration`, `application-interface`, `application-function`, `application-interaction`, `application-process`, `application-event`, `application-service`, `data-object` |
| Technology | `technology-node`, `device`, `system-software`, `technology-collaboration`, `technology-interface`, `path`, `communication-network`, `technology-function`, `technology-process`, `technology-interaction`, `technology-event`, `technology-service`, `artifact` |
| Physical | `equipment`, `facility`, `distribution-network`, `material` |
| Implementation | `work-package`, `deliverable`, `implementation-event`, `plateau`, `gap` |

### Valid `artifact-type` values for connection files

Connections are typed by diagram language. ArchiMate connections use structural relationship types. Non-ArchiMate diagrams (activity, sequence, use-case) have their own connection type vocabularies.

| Diagram language | Valid `artifact-type` values |
|---|---|
| `archimate` | `archimate-composition`, `archimate-aggregation`, `archimate-assignment`, `archimate-realization`, `archimate-serving`, `archimate-access`, `archimate-influence`, `archimate-association`, `archimate-specialization`, `archimate-flow`, `archimate-triggering` |
| `er` | `er-one-to-many`, `er-many-to-many`, `er-one-to-one` |
| `sequence` | `sequence-synchronous`, `sequence-asynchronous` |
| `activity` | `activity-sequence-flow`, `activity-decision` |
| `usecase` | `usecase-include`, `usecase-extend`, `usecase-association` |

### Valid ArchiMate `element-type` values (§display ###archimate blocks)

Use UpperCamelCase to match ArchiMate 3 naming and skinparam selector syntax.

| Layer | Valid `element-type` values |
|---|---|
| Motivation | `Stakeholder`, `Driver`, `Assessment`, `Goal`, `Outcome`, `Principle`, `Requirement`, `Constraint`, `Meaning`, `Value` |
| Strategy | `Capability`, `ValueStream`, `Resource`, `CourseOfAction` |
| Business | `BusinessActor`, `BusinessRole`, **`BusinessCollaboration`**, `BusinessInterface`, `BusinessProcess`, `BusinessFunction`, `BusinessInteraction`, `BusinessEvent`, `BusinessService`, `BusinessObject`, `Contract`, `Representation`, `Product` |
| Application | `ApplicationComponent`, `ApplicationCollaboration`, `ApplicationInterface`, `ApplicationFunction`, `ApplicationInteraction`, `ApplicationProcess`, `ApplicationEvent`, `ApplicationService`, `DataObject` |
| Technology | `Node`, `Device`, `SystemSoftware`, `TechnologyCollaboration`, `TechnologyInterface`, `Path`, `CommunicationNetwork`, `TechnologyFunction`, `TechnologyProcess`, `TechnologyInteraction`, `TechnologyEvent`, `TechnologyService`, `Artifact` |
| Physical | `Equipment`, `Facility`, `DistributionNetwork`, `Material` |
| Implementation | `WorkPackage`, `Deliverable`, `ImplementationEvent`, `Plateau`, `Gap` |

### Valid ArchiMate grouping stereotypes (diagram `<<Stereotype>>` on grouping rectangles)

Use the stereotype matching the ArchiMate layer of the contained elements. No inline `#color` overrides permitted on grouping rectangles. Defined in `src/common/archimate_types.py` (`ARCHIMATE_GROUPING_STEREOTYPES`) and `_archimate-stereotypes.puml`.

| Situation | Grouping stereotype |
|---|---|
| All contained elements from one layer | Layer-specific stereotype (see below) |
| Heterogeneous or purely organisational | `<<Grouping>>` (neutral white) |

Layer-specific stereotypes:

| Contained layer | Stereotype |
|---|---|
| Motivation | `<<MotivationGrouping>>` |
| Strategy | `<<StrategyGrouping>>` |
| Business | `<<BusinessGrouping>>` |
| Application | `<<ApplicationGrouping>>` |
| Technology | `<<TechnologyGrouping>>` |
| Physical | `<<PhysicalGrouping>>` |
| Implementation | `<<ImplementationGrouping>>` |

### Valid ArchiMate `relationship-type` values (§display ###archimate connection blocks)

`Composition`, `Aggregation`, `Assignment`, `Realization`, `Serving`, `Access`, `Influence`, `Association`, `Specialization`, `Flow`, `Triggering`

---

## 4. §display Section

### 4.1 Structure

```markdown
<!-- §display -->

### <language-id>

```yaml
<rendering spec YAML>
```

### <language-id>

```yaml
<rendering spec YAML>
```
```

Each `### <language-id>` subsection contains exactly one fenced YAML block. Supported language identifiers: `archimate`, `er`, `sequence`, `activity`, `usecase`.

The expected language subsections per entity type are determined by the entity's ArchiMate layer and typical diagram usage. `write_artifact` issues a warning (not an error) when expected subsections are absent. Missing subsections are treated as "not applicable to this diagram language."

### 4.2 Display Spec per Language — Entities

See `framework/artifact-registry-design.md §3.6` for the full field specifications. Summary:

| Language | Key Fields |
|---|---|
| `archimate` | `layer`, `element-type` |
| `er` | `primary-key`, `attributes` |
| `sequence` | `participant-type`, `label` |
| `activity` | `swimlane-label` |
| `usecase` | `element-type`, `system-boundary` |

### 4.3 Display Spec per Language — Connections

| Language | Key Fields |
|---|---|
| `archimate` | `relationship-type`, `direction`, `access-type` (access only), `label` |
| `er` | `source-cardinality`, `target-cardinality`, `label` |
| `sequence` | `message-type`, `label` |
| `activity` | `flow-type`, `condition` |
| `usecase` | `relationship-type`, `label` |

---

## 5. Properties Table per Entity Type

### Motivation Aspect

**`stakeholder`**
| Attribute | Value |
|---|---|
| Category | Individual \| Organisation \| Role |
| Concerns | \<list of architecture concerns\> |

**`driver`**
| Attribute | Value |
|---|---|
| Source | \<stakeholder or external force\> |
| Nature | Internal \| External \| Regulatory |

**`requirement`**
| Attribute | Value |
|---|---|
| Priority | Must \| Should \| Could \| Won't |
| Source | \<STK-NNN or engagement document\> |
| Verifiable | Yes \| No |

**`architecture-constraint`**
| Attribute | Value |
|---|---|
| Type | Technical \| Business \| Regulatory |
| Source | \<origin document or stakeholder\> |

**`goal`**
| Attribute | Value |
|---|---|
| Time Horizon | Short \| Medium \| Long |
| Measurable | Yes \| No |

**`principle`**
| Attribute | Value |
|---|---|
| Statement | \<one-sentence principle\> |
| Rationale | \<why this principle holds\> |
| Implications | \<what following this principle means\> |

### Strategy Aspect

**`capability`**
| Attribute | Value |
|---|---|
| Level | 1 (top-level) \| 2 (sub-capability) |
| Parent | \<CAP-NNN\> or — |
| Strategic Classification | Core \| Supporting \| Commodity |
| Maturity | Current \| Developing \| Target |

**`value-stream`**
| Attribute | Value |
|---|---|
| Trigger | \<initiating event or stakeholder request\> |
| Outcome | \<value delivered\> |
| Stages | \<list of stage names\> |

### Business Layer

**`business-process`**
| Attribute | Value |
|---|---|
| Trigger | \<event or state that starts this process\> |
| Outcome | \<result/deliverable\> |
| Safety-Relevant | Yes \| No |

**`business-function`**
| Attribute | Value |
|---|---|
| Organisational Unit | \<owning unit or role\> |
| Frequency | Continuous \| Periodic \| On-demand |

**`business-service`**
| Attribute | Value |
|---|---|
| Consumer | \<who uses this service\> |
| SLA | \<service level, if defined\> |

**`business-actor`**
| Attribute | Value |
|---|---|
| Type | Person \| Organisation \| System |
| External | Yes \| No |

**`business-role`**
| Attribute | Value |
|---|---|
| Assigned To | \<ACT-NNN or "TBD"\> |
| Permissions | \<brief summary\> |

**`business-collaboration`**
| Attribute | Value |
|---|---|
| Collaborating Roles | \<ACT-NNN, ACT-NNN, ... (roles/actors forming the collaboration)\> |
| External | Yes \| No |

**`business-object`**
| Attribute | Value |
|---|---|
| Lifecycle | \<states: draft → approved → archived, etc.\> |
| Owner | \<ROL-NNN or ACT-NNN\> |

### Application Layer

**`application-component`**
| Attribute | Value |
|---|---|
| Type | Service \| Store \| Gateway \| UI \| Integration |
| Responsibility | \<one-sentence\> |
| Status | New \| Existing \| Modified \| Retiring |

**`application-service`**
| Attribute | Value |
|---|---|
| API Style | REST \| gRPC \| GraphQL \| Event \| Internal |
| Synchrony | Sync \| Async |

**`application-interface`**
| Attribute | Value |
|---|---|
| Protocol | \<HTTP, gRPC, AMQP, etc.\> |
| Direction | Provided \| Required |

**`data-object`**
| Attribute | Value |
|---|---|
| Classification | Public \| Internal \| Confidential \| Restricted |
| PII | Yes \| No |
| Primary Store | \<APP-NNN\> |

### Technology Layer

**`node`**
| Attribute | Value |
|---|---|
| Type | Container \| VM \| Bare-metal \| Managed Service |
| Provider | \<cloud/vendor or on-prem\> |

**`system-software`**
| Attribute | Value |
|---|---|
| Version Constraint | \<semver range\> |
| Licence | \<FOSS/commercial\> |

**`tech-service`**
| Attribute | Value |
|---|---|
| Type | Runtime \| Database \| Message Broker \| API Gateway \| CDN \| Auth \| Monitoring |
| Vendor / FOSS | \<name\> |

**`tech-artifact`**
| Attribute | Value |
|---|---|
| Type | Container Image \| JAR \| Binary \| Config Bundle |
| Registry | \<image registry or package repo\> |

### Implementation & Migration Aspect

**`work-package`**
| Attribute | Value |
|---|---|
| Target Plateau | \<PLT-NNN\> |
| Start Date | \<YYYY-MM-DD\> |
| End Date | \<YYYY-MM-DD\> |

**`gap`**
| Attribute | Value |
|---|---|
| From Plateau | \<PLT-NNN or "Baseline"\> |
| To Plateau | \<PLT-NNN\> |
| Gap Type | Missing \| Excess \| Misaligned |

**`plateau`**
| Attribute | Value |
|---|---|
| Target Date | \<YYYY-MM-DD\> |
| State | Baseline \| Transitional \| Target |

---

## 6. Exemplar Files

### 6.1 Strategy Capability — `strategy/capabilities/CAP-001.md`

```markdown
---
artifact-id: CAP-001
artifact-type: capability
name: "Agent Orchestration"
version: 1.0.0
status: baselined
phase-produced: A
owner-agent: SA
domain: core-platform
safety-relevant: false
produced-by-skill: SA-PHASE-A
last-updated: 2026-04-03
engagement: ENG-001
---

<!-- §content -->

## Agent Orchestration

The ability to coordinate specialised AI agents across ADM phases, managing task delegation, handoffs, and phase gate evaluation.

## Properties

| Attribute | Value |
|---|---|
| Level | 1 |
| Parent | — |
| Strategic Classification | Core |
| Maturity | Developing |

<!-- §display -->

### archimate

```yaml
layer: strategy
element-type: Capability
```

### activity

```yaml
swimlane-label: "Agent Orchestration"
```
```

### 6.2 Application Component — `application/components/APP-001.md`

```markdown
---
artifact-id: APP-001
artifact-type: app-component
name: "PM Agent"
version: 0.3.0
status: draft
phase-produced: C
owner-agent: SwA
domain: core-platform
safety-relevant: false
produced-by-skill: SwA-PHASE-C-APP
last-updated: 2026-04-04
engagement: ENG-001
---

<!-- §content -->

## PM Agent

Supervisor component that drives the ADM phase workflow, invokes specialist agents, evaluates phase gates, and manages CQ lifecycle.

## Properties

| Attribute | Value |
|---|---|
| Type | Service |
| Responsibility | ADM phase orchestration and specialist delegation |
| Status | New |

<!-- §display -->

### archimate

```yaml
layer: application
element-type: ApplicationComponent
```

### sequence

```yaml
participant-type: component
label: "PM Agent"
```
```

### 6.3 Data Object — `application/data-objects/DOB-001.md`

```markdown
---
artifact-id: DOB-001
artifact-type: data-object
name: "WorkflowEvent"
version: 0.2.0
status: draft
phase-produced: C
owner-agent: SwA
domain: core-platform
safety-relevant: false
produced-by-skill: SwA-PHASE-C-DATA
last-updated: 2026-04-04
engagement: ENG-001
---

<!-- §content -->

## WorkflowEvent

Immutable append-only record of every state transition in the SDLC workflow.
Persisted in SQLite EventStore; exported to YAML at sprint close.

## Properties

| Attribute | Value |
|---|---|
| Classification | Internal |
| PII | No |
| Primary Store | APP-007 |

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

### 6.4 ArchiMate Connection — `connections/archimate/realization/APP-001---BSV-001@@archimate-realization.md`

```markdown
---
artifact-id: APP-001---BSV-001@@archimate-realization
artifact-type: archimate-realization
source: APP-001
target: BSV-001
version: 1.0.0
status: baselined
phase-produced: C
owner-agent: SA
engagement: ENG-001
last-updated: 2026-04-03
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

Connection artifact-id rules (normative):
- Use `SOURCE(--SOURCE)*---TARGET(--TARGET)*@@artifact-type`.
- Keep `@@artifact-type` identical to frontmatter `artifact-type`.
- Keep `SOURCE/TARGET` segments identical to frontmatter `source`/`target` values.
- Keep the artifact-id identical to the filename stem.

Verifier checks:
- `E201`: invalid connection artifact-id shape.
- `E202`: filename stem mismatch.
- `E203`: `@@suffix` does not match `artifact-type`.
- `E205`: source/target composition in artifact-id does not match frontmatter.

### 6.5 ER Connection — `connections/er/one-to-many/DOB-001---DOB-002@@er-one-to-many.md`

```markdown
---
artifact-id: DOB-001---DOB-002@@er-one-to-many
artifact-type: er-one-to-many
source: DOB-001
target: DOB-002
version: 1.0.0
status: baselined
phase-produced: C
owner-agent: SA
engagement: ENG-001
last-updated: 2026-04-03
---

<!-- §content -->

One engagement may have many workflow events.

<!-- §display -->

### er

```yaml
source-cardinality: "1"
target-cardinality: "0..*"
label: "has"
```
```

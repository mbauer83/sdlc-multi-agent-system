# Repository Conventions

**Version:** 1.3.0  
**Status:** Approved — Stage 4.8d  
**Owner:** Project Manager  
**Last Updated:** 2026-04-04

---

## 1. Purpose and Scope

This document governs how artifacts are stored, versioned, transferred, and retrieved across the seven work-repositories and the shared framework. Every agent skill file that reads or writes an artifact is bound by these conventions. Violations — writing outside owned paths, bypassing the handoff format, or consuming a draft artifact as authoritative — are governance failures and must be reported to the PM.

---

## 2. Directory Ownership and Path Governance

### 2.1 Work-Repository Ownership

Each work-repository has exactly one owning agent role. Only the owning role may write artifacts into its repository. All other roles read-only.

Work-repositories are **engagement-scoped**. They live under `engagements/<engagement-id>/work-repositories/`. Canonical paths below use `ENG-<id>` as a placeholder; substitute the actual engagement identifier.

| Repository | Owner | Canonical Path |
|---|---|---|
| Architecture Repository | Solution Architect | `engagements/<id>/work-repositories/architecture-repository/` |
| Technology Repository | Software Architect / PE | `engagements/<id>/work-repositories/technology-repository/` |
| Project Repository | Project Manager | `engagements/<id>/work-repositories/project-repository/` |
| Safety Repository | CSCO | `engagements/<id>/work-repositories/safety-repository/` |
| Delivery Repository | Implementing Developer | `engagements/<id>/work-repositories/delivery-repository/` — holds delivery **metadata** (PR records, branch references, test reports). Source code lives in the target project repository (§2.4 of `architecture-repository-design.md`). |
| QA Repository | QA Engineer | `engagements/<id>/work-repositories/qa-repository/` |
| DevOps Repository | DevOps / Platform Engineer | `engagements/<id>/work-repositories/devops-repository/` |

The **Enterprise Repository** (`enterprise-repository/`) is a separate, long-lived scope not owned by any individual engagement. Write access requires Architecture Board approval; see §12 for the promotion procedure. Full structure is specified in `framework/architecture-repository-design.md §2.1`.

### 2.2 Sub-Directory Structure

Work-repositories that hold architecture model entities follow the **Entity Registry Pattern (ERP) v2.0** directory layout (see §14 and `framework/artifact-registry-design.md §2`). Repositories that hold only repository-content artifacts use a simpler flat layout.

**Architecture Repository** (`architecture-repository/`) — canonical layout per `framework/artifact-registry-design.md §2.1`:

```
architecture-repository/
  model-entities/        # All ArchiMate entity files — grouped by layer/aspect
    motivation/          # STK, DRV, GOL, REQ, CST, PRI, MEA, VAL, ASS, OUT
      stakeholders/      # STK-001.md  STK-002.md  ...
      drivers/           # DRV-001.md  ...
      goals/             # GOL-001.md  ...
      requirements/      # REQ-001.md  ...
      constraints/       # CST-001.md  ...
      principles/        # PRI-001.md  ...
      <other-aspects>/   # assessments/, outcomes/, meanings/, values/
    strategy/            # CAP, VS, RES, COA
      capabilities/      # CAP-001.md  ...
      value-streams/     # VS-001.md  ...
    business/            # ACT, ROL, BPR, BFN, BSV, BEV, BOB, BIF, BCO
      actors/            # ACT-001.md  ...
      processes/         # BPR-001.md  ...
      services/          # BSV-001.md  ...
      <other-aspects>/   # roles/, functions/, events/, objects/, interfaces/, ...
    application/         # APP, ASV, AIF, AFN, AEV, DOB, APR
      components/        # APP-001.md  ...
      interfaces/        # AIF-001.md  ...
      services/          # ASV-001.md  ...
      data-objects/      # DOB-001.md  ...
      <other-aspects>/   # functions/, events/, processes/, collaborations/
    implementation/      # WP, DEL, GAP, PLT
      work-packages/     # WP-001.md  ...
      gaps/              # GAP-001.md  ...
      <other-aspects>/   # deliverables/, plateaus/, events/
  connections/           # Connection files — sibling of model-entities/
    archimate/<type>/    # realization/, serving/, assignment/, composition/, ...
    er/<type>/           # one-to-many/, many-to-many/, one-to-one/
    sequence/<type>/     # synchronous/, asynchronous/
    activity/<type>/     # sequence-flow/
    usecase/<type>/      # include/, extend/
  diagram-catalog/       # Sibling of model-entities/ and connections/
    _macros.puml         # Auto-generated from entity §display ###archimate blocks
    _archimate-stereotypes.puml
    diagrams/            # Produced engagement diagrams; each .puml begins with header comment frontmatter
      phase-b-archimate-business-v1.puml
      phase-c-class-er-v1.puml
    templates/           # Blank per-type stubs; agents copy, rename, and adapt for new diagrams
      archimate-business-template.puml
      class-er-template.puml
    rendered/            # *.svg outputs; committed at sprint boundary
  decisions/             # ADR-nnn-<slug>.md
  overview/              # Phase overview documents (av-overview.md, ba-overview.md, etc.)
```

**Technology Repository** (`technology-repository/`) — same `model-entities/` / `connections/` / `diagram-catalog/` layout; entity layer is `model-entities/technology/<aspect>/`. Also contains:

```
technology-repository/
  model-entities/
    technology/          # NOD, SSW, TSV, ARF entities
      nodes/             # NOD-001.md  ...
      system-software/   # SSW-001.md  ...
      tech-services/     # TSV-001.md  ...
      artifacts/         # ARF-001.md  ...
  connections/
  diagram-catalog/
  decisions/             # ADR-nnn-<slug>.md (primary home for Phase D ADRs)
  coding-standards/      # Coding standards documents (scanned by Step 0.S)
  overview/
```

**Other repositories** — flat layout; no ERP entity directories:

```
<repo>/
  README.md
  <artifact-type>/       # One directory per artifact type
    <artifact-id>-<version>.md
  sprint-log/            # Sprint records (project-repository)
  knowledge-base/        # Lessons learned (project-repository)
```

Agent learning entries are stored at `agents/<role>/learnings/` in the framework directory — not inside any engagement work-repository. See `framework/learning-protocol.md §4`.

### 2.3 Path Rules

- **No agent writes outside its work-repository** except: `framework/` (SA owns artifact schemas; changes require PM approval); and the PM agent may write to the engagement root (`engagements/<id>/engagement-profile.md`) and `engagements-config.yaml` as part of the engagement bootstrap procedure (§4.8 of `architecture-repository-design.md`).
- **Cross-role artifact transfer occurs through handoff events** (§5), never through direct file writes into another agent's repository.
- **The `framework/` directory is read-only for all agents** during normal operation. Changes to framework documents require PM approval and must not conflict with existing artifact schemas.

---

## 3. Artifact Versioning Convention

All artifacts use **semantic versioning** (`MAJOR.MINOR.PATCH`):

| Version Range | Meaning |
|---|---|
| `0.x.x` | Draft — work in progress; not authoritative; may change without notice |
| `1.0.0` | Baselined — passed phase gate; authoritative for downstream consumption |
| `1.x.x` (x > 0) | Minor revision — content updated but structure and core decisions unchanged; no gate re-evaluation required unless a CSCO-relevant change is present |
| `2.0.0+` | Major revision — structural change or reversal of a key decision; triggers full Phase H change process |

**Filename convention:** `<artifact-type-id>-<version>.md` — e.g. `av-1.0.0.md`, `ba-1.2.1.md`, `ta-2.0.0.md`.

**Version history:** Each artifact file carries a `## Version History` section at its end recording all version increments, the agent who made the change, the sprint in which it was made, and a one-line change summary.

---

## 4. Confidence-Threshold Retrieval Protocol

### 4.1 Rationale

Retrieving a full artifact when only its summary is needed wastes token budget and introduces unnecessary latency. This protocol governs when a consuming agent reads only the summary header versus the full artifact body.

### 4.2 Decision Rule

When an agent needs information from an artifact owned by another role, it applies the following decision:

```
1. Read the artifact summary header (§4.3).
2. Ask: "Is the summary header sufficient to correctly and completely perform my current task?"

   YES → use summary only. Log: "summary sufficient — [artifact-id] v[version]".
   NO  → retrieve full artifact. Log: "full retrieval — [artifact-id] v[version] — reason: [one line]".
```

### 4.3 Conditions Requiring Full Retrieval

Full retrieval is **mandatory** when any of the following is true:

- The current task produces a binding output (a deliverable, a phase gate record, or an Architecture Contract).
- The task involves a safety-relevant decision or CSCO gate review.
- The summary header's `open-issues` list contains an item relevant to the current task.
- The consuming agent detects an inconsistency between the summary and information from another source.
- The artifact was last retrieved more than two sprint iterations ago and the consuming agent cannot confirm its version is still current.

### 4.4 Retrieval Log

All retrievals (both summary-only and full) are recorded in the agent's Working Notes (`WN`) for the current sprint. The log entry format is:

```
[RETRIEVAL] <artifact-id> v<version> | <summary|full> | <reason if full>
```

---

## 5. Cross-Role Handoff Event Format

A handoff event is the formal mechanism for transferring an artifact from a producing agent to a consuming agent. It is not a file copy — it is a structured notification that triggers the consuming agent to acknowledge receipt and apply the confidence-threshold protocol.

### 5.1 Handoff Event Record

The producing agent writes a handoff event record to `engagements/<id>/handoff-log/<sprint-id>-<artifact-id>-handoff.md` immediately upon baselining an artifact.

```markdown
---
handoff-id:       # unique: <sprint-id>-<artifact-id>-<sequence>
artifact-id:      # artifact being transferred
artifact-version: # version being handed off
from-agent:       # producing agent role
to-agents:        # list of consuming agent roles
produced-in:      # sprint identifier
timestamp:        # ISO 8601 date
status:           # pending | acknowledged | complete
---

## Artifact Summary (copy of summary header)
[paste artifact summary header here]

## Consuming Agent Acknowledgements
<!-- Each consuming agent appends an entry here upon receipt -->
| Agent | Acknowledged | Retrieval Intent | Notes |
|---|---|---|---|
| [role] | [date] | summary / full | [any flags] |
```

### 5.2 Consuming Agent Acknowledgement

Upon receiving a handoff event, each listed consuming agent must:

1. Read the artifact summary header.
2. Apply the confidence-threshold rule (§4.2).
3. Append their acknowledgement row to the handoff record within the same sprint.
4. If full retrieval is required, retrieve the artifact and log the reason.
5. If the artifact has an open issue that blocks the consuming agent's work, raise a structured feedback item (§6) immediately.

### 5.3 Handoff Timeout

If a consuming agent does not acknowledge a handoff within the current sprint, the PM flags it as a blocker in the sprint log and follows up. Unacknowledged handoffs do not block phase gate evaluation — they are recorded as open items on the gate checklist.

---

## 6. Structured Feedback Format

When a consuming agent identifies a problem with a received artifact, it raises a structured feedback item rather than free-form commentary. This feeds the bounded feedback loop defined in `agile-adm-cadence.md §8`.

```markdown
---
feedback-id:      # <consuming-agent>-<artifact-id>-<iteration>
artifact-id:      # artifact being reviewed
artifact-version: # version reviewed
from-agent:       # consuming agent raising feedback
to-agent:         # producing agent (artifact owner)
iteration:        # 1 or 2 (maximum)
sprint:           # sprint in which feedback is raised
severity:         # blocking | non-blocking
---

## Issue Description
[Precise description of the problem — what is wrong, why it matters]

## Required Change
[Specific, actionable change requested — not subjective preferences]

## Acceptance Criterion
[How the producing agent can confirm the issue is resolved]
```

The producing agent must respond within the same sprint by either revising the artifact (and issuing a new version) or raising a counter-argument via the same format. If iteration 2 is exhausted without resolution, the PM is notified immediately.

---

## 7. Artifact Summary Header (canonical specification)

The summary header defined here is the authoritative specification. The version in `agile-adm-cadence.md §9.2` is informational. In case of conflict, this document governs.

Every artifact MUST begin with a YAML frontmatter block containing the following fields. All fields are required unless marked optional.

```yaml
---
artifact-type:     # schema identifier — must match a schema file in framework/artifact-schemas/
artifact-id:       # unique identifier, e.g. AV-001
version:           # semver string, e.g. "1.0.0"
phase:             # one of: Prelim | A | B | C | D | E | F | G | H | RM
status:            # one of: draft | baselined | superseded | archived
owner-agent:       # canonical role name from RACI matrix
produced-in:       # sprint identifier, e.g. "AS-3"
path:              # canonical path in owning work-repository
depends-on:        # [list of artifact-ids consumed as authoritative input; empty list if none]
consumed-by:       # [list of artifact-ids or agent roles that consume this; may be updated post-creation]
safety-relevant:   # true | false
csco-sign-off:     # true | false | not-required
pm-sign-off:       # true | false
summary: |
  # 2–4 sentences describing content, key decisions, and current status.
  # This is the primary content consumed at normal operating tempo.
key-decisions:         # [list of the most consequential decisions captured in this artifact]
open-issues:           # [list of open items; each: "ISSUE-nn: <description> (owner: <role>, target: <sprint>)"]
pending-clarifications: # [list of CQ-ids from clarification-log/ that must be resolved before this artifact can be
                        #  baselined; empty list [] if none open. Format: "CQ-id: <one-line summary of what is blocked>"]
assumptions:           # [list of assumptions made in lieu of answered CQs; each: "ASSN-nn: <assumption> (CQ-id if linked)"]
---
```

**Completeness rule:** An artifact with any missing required header field fails the artifact readiness check (§7 of `agile-adm-cadence.md`) and cannot be baselined.

---

## 8. Repository README Requirements

Every work-repository root must contain a `README.md` with the following sections:

```markdown
# <Repository Name>

**Owner:** <agent role>  
**Status:** Active  

## Scope
[One paragraph describing what this repository holds]

## Path Governance
[Which paths within this repository each sub-role may write to, if applicable]

## Access Rules
[Who may read; who may write; cross-role read access is always permitted]

## Contents
[Table of artifact types stored here, with sub-directory names]
```

---

## 9. Version Control Commit Convention

All artifact commits follow this message format:

```
[<artifact-type>] <artifact-id> v<version> — <one-line description>

Sprint: <sprint-id>
Agent: <role>
Gate: <phase-gate passed, if this commit constitutes a baseline>
```

Example:
```
[architecture-vision] AV-001 v1.0.0 — baseline: Phase A gate passed

Sprint: AS-2
Agent: solution-architect
Gate: A→B
```

---

## 10. External Source Query Protocol

Agents may query external read-only sources (Confluence, Jira, external Git repositories, etc.) configured in `external-sources/<source-id>.config.yaml`. The following rules apply to all source queries.

### 10.1 Query Rules

1. **Read-only is absolute.** No agent may write, update, or delete content in any external source under any circumstances. External source adapters expose only query and fetch operations.
2. **Queries are logged.** Every query is recorded as a `source.queried` event in the workflow event store, with the source-id, query type, and a one-line summary of the query intent.
3. **Query before raising a CQ.** Before raising a Clarification Request about domain context, agents must confirm that the relevant external sources have been queried. A CQ raised without querying available sources is a knowledge-adequacy failure.
4. **Cite sources in artifacts.** When artifact content is derived from an external source, the artifact's `assumptions` or a dedicated `sources` field must cite the source-id and the content location (e.g., Confluence page URL or Jira issue key).
5. **Content authority.** External source content is informational input, not authoritative architecture. It does not override baselined artifacts. If an external source contradicts a baselined artifact, the consuming agent raises a CQ or structured feedback item — it does not silently prefer the external source.

### 10.2 Source Adapter Resolution

When an agent needs context from an external source, it consults `external-sources/` to identify which source adapters are configured. The `purpose` field in each adapter config is the primary signal for which source to query.

Agents do not hard-code source identifiers in skill files. Skill files specify the **type of content needed** (e.g., "existing business capability documentation", "open defect tickets for this component"). The PM's engagement coordination skill resolves which source-id(s) to query for that content type, based on the configured adapters.

---

## 11. Enterprise vs. Engagement Artifact Lookup

When an agent requires a piece of architecture knowledge that may exist at the enterprise level (standards, principles, segment architectures, reference patterns), the following lookup order applies:

```
1. Check engagement work-repositories for a locally baselined artifact.
2. If not found locally: query enterprise-repository/ for the relevant content.
3. If not found in enterprise repository: query configured external sources.
4. If still not found: raise a CQ (knowledge gap — cannot safely assume).
```

**An agent must not raise a CQ about organisation-wide standards or principles without first checking steps 1–3.** A CQ raised without checking available repositories is a knowledge-adequacy failure (see `clarification-protocol.md §2`).

**Precedence:** Locally baselined engagement artifacts always take precedence over enterprise-level content for the purposes of the current engagement. If a local artifact conflicts with an enterprise standard, the conflict must be documented in the artifact's `assumptions` field and flagged as an open issue for resolution — it must not be silently overridden.

---

## 12. Enterprise Promotion Procedure

When a capability-level engagement is closed, the Project Manager initiates a **Promotion Review** to identify engagement artifacts suitable for promotion to the Enterprise Repository.

### 12.1 Promotion Candidates

An artifact is a candidate for promotion when it:
- Represents architecture that is reusable across multiple future engagements, or
- Establishes a new organisational technology standard or pattern (ADR that becomes organisation-wide), or
- Documents a safety constraint applicable to a class of systems (not just this engagement's system)

### 12.2 Promotion Procedure

1. **SA identifies candidates** during engagement closeout, listing candidate artifact-ids and their proposed enterprise target level (Segment or Capability landscape).
2. **PM raises a Promotion Request** as a record in `enterprise-repository/governance-log/`. The Promotion Request includes: engagement artifact-id, artifact version, proposed enterprise target path, justification, and any required modifications.
3. **Architecture Board** reviews the request and approves, rejects, or requests modifications. Only Architecture Board members may write to the enterprise repository.
4. **On approval:** An Architecture Board member runs `promote_entity`, which: (a) assigns a new enterprise-scope ID (next available for the entity's prefix from `enterprise-repository/governance-log/id-counters.yaml`); (b) rewrites the entity's frontmatter with the new ID, resets version to `1.0.0`, and strips `engagement` and `produced-by-skill` fields; (c) performs a deterministic reference sweep across all engagement artifacts — connection `source`/`target` fields, diagram PUML alias occurrences, and inline `[@old-id …]` references — replacing the old engagement-ID with the new enterprise-ID; (d) moves the entity file to the enterprise target path.
5. **`artifact.promoted` event** is written to both the engagement's workflow event store and the enterprise governance log, recording the old engagement-ID and new enterprise-ID for audit traceability.
6. **Enterprise entity is read-only to all future engagement agents.** Architecture Board members continue to maintain, version, and update it through normal enterprise governance.

### 12.3 Promotion Scope

Only the following artifact types are eligible for promotion:

| Artifact | Target Enterprise Path |
|---|---|
| Architecture Vision (strategic scope) | `enterprise-repository/landscape/strategic/` |
| Business Architecture (segment scope) | `enterprise-repository/landscape/segment/` |
| Technology Architecture (standards-setting ADRs) | `enterprise-repository/standards/` |
| Safety Constraint Overlay (class-of-system applicability) | `enterprise-repository/standards/safety/` |
| Architecture Principles (`PRI` model-entities) | `enterprise-repository/metamodel/principles/` |
| Capability Architecture (general) | `enterprise-repository/landscape/capability/` |
| **Model entities** (reusable across engagements) | Target layer path within `enterprise-repository/` matching the entity's ArchiMate layer/aspect (e.g. `enterprise-repository/strategy/capabilities/`, `enterprise-repository/business/roles/`, `enterprise-repository/application/components/`) |
| **Model connections** (between promoted entities) | `enterprise-repository/connections/<lang>/<type>/` |

Model-entity and connection promotion is most common for: capabilities (`CAP`), enterprise-wide roles and actors (`ROL`, `ACT`), shared application components and services (`APP`, `ASV`), reusable data objects (`DOB`), and organisation-wide principles and constraints (`PRI`, `CST`). Engagement-specific entities (e.g. a one-off work-package) are not promoted.

---

## 13. Canonical Artifact Reference Format

Every handoff event, work-spec, skill output, or artifact that cites another artifact must use the following reference forms. This enables cross-artifact dependency resolution by the orchestration layer and dashboard. Agents must never reference artifacts by filename alone.

### 13.1 In-Text Markdown Reference

```
[@<artifact-id> v<major>.<minor>](<relative-path-from-engagement-root>)
```

**Example:** `[@ARCH-VIS-001 v1.2](work-repositories/architecture-repository/architecture-vision/arch-vis-001-v1.2.md)`

The artifact-id is the stable identifier; the version is the version at time of reference; the path is the relative path from the engagement root directory (`engagements/<id>/`). If the artifact has not yet been assigned a formal ID (e.g., it is a draft), use a provisional ID in the format `[@DRAFT-<artifact-type>-<seq>]` with no path until the ID is assigned.

### 13.2 Frontmatter `references:` List

Every artifact that cites other artifacts must include a YAML `references:` list in its frontmatter:

```yaml
references:
  - ARCH-VIS-001
  - SCO-A-1.0.0
  - BA-001
```

This list is parsed by the orchestration layer and dashboard to build cross-artifact dependency graphs. It must contain the artifact-id (not the filename) of every artifact the current artifact depends on or cites.

### 13.3 Handoff Event `artifact_refs:` Field

When a handoff event is emitted, the payload must include an `artifact_refs:` field listing all artifact-ids that the receiving agent should prime during its Discovery Scan:

```json
{
  "handoff_type": "review-and-sign-off",
  "from_agent": "SA",
  "to_agent": "CSCO",
  "artifact_refs": ["ARCH-VIS-001", "AV-SAFETY-ENV-001"]
}
```

The receiving agent uses `artifact_refs` to populate its Layer 1 Discovery Scan — these artifacts are read before any others in the engagement state layer.

### 13.4 Skill `## Inputs Required` Table

Each row in a skill's `## Inputs Required` table that names a prior artifact must include the artifact-id and the owning work-repository path:

| Input | Artifact ID | Source Repository Path | Minimum State |
|---|---|---|---|
| Architecture Vision | `ARCH-VIS-001` | `work-repositories/architecture-repository/architecture-vision/` | Baselined at 1.0.0 |

**Artifact-id assignment:** Artifact-ids are assigned at first draft by the owning agent following the pattern `<TYPE>-<SEQ>` where TYPE is a two-to-four letter abbreviation of the artifact type (e.g., `AV` for Architecture Vision, `BA` for Business Architecture, `SCO` for Safety Constraint Overlay) and SEQ is a zero-padded three-digit sequence within the engagement. The id is recorded in the artifact's frontmatter as `artifact-id:` at creation time and never changed thereafter, even when the artifact is versioned.


---

## 14. ERP Conventions Summary

The Entity Registry Pattern (ERP) v2.0 governs all model-entity and model-connection storage in the architecture-repository and technology-repository. Key rules:

| Concern | Rule |
|---|---|
| One file per instance | Every entity, connection, diagram, and diagram-template is its own file |
| Frontmatter is the index | ModelRegistry is built by scanning frontmatter at startup; no separate `_index.yaml` or `index.yaml` files exist |
| Entity grouping | All ArchiMate entity files live under `model-entities/<layer>/<aspect>/` |
| Connections are siblings | `connections/` is a top-level sibling of `model-entities/`; typed by `connections/<diagram-language>/<connection-type>/` |
| Diagrams are siblings | `diagram-catalog/` is a top-level sibling of `model-entities/` and `connections/`; produced diagrams in `diagrams/`, blank per-type stubs in `templates/` |
| Diagram frontmatter | `.puml` files carry YAML frontmatter in a PUML header comment block (prefix `' `); parsed by ModelRegistry |
| Entity files have no cross-references | All relational information lives in connection files; entity frontmatter has no `references:` field |
| IDs are immutable | Assigned at creation; never reused even after deprecation |
| Two ID scopes | Engagement artifact-ids are engagement-local; enterprise IDs are globally unique, assigned at promotion from `id-counters.yaml` |
| Learning entries | Stored at `agents/<role>/learnings/` in the framework directory — not in any engagement work-repository |

**Canonical references:**
- Full entity/connection file format: `framework/artifact-schemas/entity-conventions.md`
- Full directory structure: `framework/artifact-registry-design.md §2`
- Diagram production protocol: `framework/diagram-conventions.md §5`
- Diagram frontmatter spec: `framework/diagram-conventions.md §9`
- ModelRegistry design and tool contracts: `framework/artifact-registry-design.md §6–§10`

# Repository Conventions

**Version:** 1.2.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager  
**Last Updated:** 2026-04-02

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

Each work-repository follows a standard internal layout:

```
<repo>/
  README.md              # Ownership declaration, scope, and access rules
  <artifact-type>/       # One directory per artifact type (e.g. architecture-vision/)
    <artifact-id>-<version>.md   # e.g. av-1.0.0.md
  standards/             # Standards, catalogs, registers (where applicable)
  sprint-log/            # Sprint records (project-repository only)
  knowledge-base/        # Lessons learned, retrospectives (project-repository only)
```

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
2. **PM raises a Promotion Request** as a record in `enterprise-repository/governance-log/`. The Promotion Request includes: artifact-id, artifact version, proposed target path, justification, and any required modifications.
3. **Architecture Board (or PM if no Board is constituted)** reviews the request and approves, rejects, or requests modifications.
4. **On approval:** The artifact is copied (not moved) to the enterprise target path. The engagement copy remains unchanged. The enterprise copy is assigned a new version (`1.0.0` for first promotion) and updated to remove engagement-specific metadata.
5. **`artifact.promoted` event** is written to both the engagement's workflow event store and the enterprise governance log.
6. **Enterprise artifact is then read-only** to all future engagements (i.e., consumed as enterprise input, not written to by engagement agents).

### 12.3 Promotion Scope

Only the following artifact types are eligible for promotion:

| Artifact | Target Enterprise Path |
|---|---|
| Architecture Vision (strategic scope) | `enterprise-repository/landscape/strategic/` |
| Business Architecture (segment scope) | `enterprise-repository/landscape/segment/` |
| Technology Architecture (standards-setting ADRs) | `enterprise-repository/standards/` |
| Safety Constraint Overlay (class-of-system applicability) | `enterprise-repository/standards/safety/` |
| Architecture Principles | `enterprise-repository/metamodel/principles/` |
| Capability Architecture (general) | `enterprise-repository/landscape/capability/` |

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

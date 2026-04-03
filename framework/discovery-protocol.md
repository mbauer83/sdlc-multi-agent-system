# Discovery Protocol

**Version:** 1.0.0  
**Status:** Approved — Stage 3  
**Owner:** Project Manager  
**Last Updated:** 2026-04-02

---

## 1. Purpose

The Discovery Protocol specifies how every agent must survey available context before raising Clarification Requests (CQs). Agents operate in engagements that may carry existing artifacts, connected data sources, and live codebases. Asking for information the system can answer itself is wasteful and degrades user trust.

The principle is: **scan first, infer second, assume third, ask last.**

Every agent skill that begins new phase work or enters at a non-EP-0 entry point must execute the Discovery Scan before raising CQs. A CQ is only valid if it asks for information that cannot be obtained by reading available sources. A CQ raised without a prior discovery scan is a governance violation (ALG-018 risk).

---

## 2. Discovery Scan Procedure

The Discovery Scan has five layers, executed in order. Each layer may yield artifacts or data that reduce the CQ list. Proceed through all layers even when earlier layers provide partial coverage.

### Layer 1 — Engagement State

Read the engagement directory for existing work.

```
engagements/<id>/engagement-profile.md          → current EP, scope, constraints, target-repo config
engagements/<id>/work-repositories/             → all work-repository directories
  architecture-repository/                      → existing AV, BA, AA, DA, CR, PR artifacts
  technology-repository/                        → existing TA, ADRs, Architecture Contract
  project-repository/                           → sprint log, decision log, SoAW
  safety-repository/                            → SCO and all phase updates
  qa-repository/                                → Test Strategy, defect records
  devops-repository/                            → EPC, deployment records
  delivery-repository/                          → PR records, branch refs
engagements/<id>/clarification-log/             → open and resolved CQs (answers may already be there)
engagements/<id>/handoff-log/                   → handoff events (what has been transferred and acknowledged)
engagements/<id>/algedonic-log/                 → open algedonic signals affecting scope
```

**Mapping rule:** For each existing artifact found, read its summary header. Confirm artifact-type, version, status (draft vs baselined), and `pending-clarifications`. Mark the corresponding ADM artifact as `Covered` in the agent's working Gap Assessment.

**Draft artifact rule:** Artifacts at version 0.x.x (draft) are available as working context but must not be treated as authoritative for binding outputs. Note draft status in Gap Assessment; flag as `Partially Covered`.

### Layer 2 — Enterprise Repository

Read the enterprise-wide architecture data, if available.

```
enterprise-repository/standards/                → SIB: approved technology standards
enterprise-repository/reference-library/        → reusable patterns and templates
enterprise-repository/landscape/                → strategic, segment, and capability architectures
enterprise-repository/requirements/             → enterprise-level requirements
enterprise-repository/knowledge-base/           → lessons learned from previous engagements
```

**Rule:** Always read `enterprise-repository/standards/` before starting Phase D work. Technology selections must be checked against the SIB. Any selection that contradicts a mandatory SIB entry must produce a principle-override ADR.

**Rule:** Check `enterprise-repository/landscape/` for existing architecture models that may cover all or part of the engagement scope. An existing capability architecture may satisfy entire Phase B sections without fresh production.

### Layer 3 — External Sources

Query configured external sources if `external-sources/<source-id>.config.yaml` files exist for this engagement.

**Discovery step:**
1. List all files in `external-sources/` that match this engagement (check `engagement-scope` field in each config).
2. For each configured source with status `active`, determine the relevant query for the current phase:

| Phase | Query Types | What to Look For |
|---|---|---|
| A (Architecture Vision) | space/page, wiki | Product vision, stakeholder lists, business mandates, regulatory context |
| B (Business Architecture) | space/page, wiki, ticket | Business processes, capability descriptions, organisational charts |
| C (Application/Data) | space/page, wiki, repo-browse | Existing application designs, API specs, data dictionaries |
| D (Technology Architecture) | space/page, wiki, repo-browse | Technology decisions, infrastructure diagrams, ADRs, runbooks |
| E (Opportunities & Solutions) | ticket, backlog | Existing features, work items, backlog priorities |
| G (Implementation Governance) | repo-browse, CI/CD | Current codebase state, open PRs, test results, deployment logs |
| H (Change Management) | ticket, wiki | Change requests, incident records, improvement ideas |

3. For each query, emit `source.queried` event per `framework/repository-conventions.md §10`.
4. Map retrieved content to ADM artifact sections. Mark fields derived from external sources with `[source: <source-id>]`.
5. If content conflicts with an existing baselined artifact, raise ALG-011 (inconsistent artifacts) rather than silently overwriting.

**No-config fallback:** If no external sources are configured, this layer is skipped. Note in the Gap Assessment that external source discovery was unavailable.

### Layer 4 — Target Project Repository

Scan the target project repository if `target-repository.url` is set in the Engagement Profile and the local clone exists at `engagements/<id>/target-repo/`.

**This layer is mandatory for EP-G and EP-H entries.** For EP-0 through EP-D it is optional but should be performed if target-repo is accessible.

**Discovery steps:**

1. **Enumerate repository structure:** List top-level directories; identify project type (web service, library, monolith, microservices, etc.) from directory layout, build files, and configuration.

2. **Read project manifests:** `package.json`, `pyproject.toml`, `pom.xml`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`, `*.csproj`, etc. Extract: technology stack, direct dependencies, version constraints. Map to Technology Architecture components (TC-nnn candidates).

3. **Read infrastructure/deployment definitions:**
   - Container: `Dockerfile`, `docker-compose.yml`
   - Kubernetes: `k8s/`, `helm/`, `kustomize/`
   - Cloud IaC: `terraform/`, `pulumi/`, `cloudformation/`
   - CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`
   Map to Deployment Topology and Environment Provisioning Catalog.

4. **Read architecture-level documentation:** `README.md`, `docs/`, `ADR.md` or `docs/decisions/`, `ARCHITECTURE.md`, `DESIGN.md`, `CONTRIBUTING.md`. Extract any documented architecture decisions; map to ADR candidates.

5. **Read interface definitions:** `openapi.yaml`, `swagger.json`, `*.proto`, `graphql/**/*.graphql`, `schemas/`. Map to Interface Catalog (IFC-nnn candidates) and Data Entity Catalog (DE-nnn candidates).

6. **Read test structure:** `test/`, `tests/`, `spec/`, `__tests__/`. Infer coverage targets and test strategy from structure and any CI configuration.

7. **Mark all inferences** with `[inferred: target-repo scan]`. Do not treat inferences as authoritative; they require validation.

**Agent scope limits:** Only the agents with target-repo read access (all agents for reading) and write access (DevOps for IaC/pipeline; Implementing Developer for feature code) per the Engagement Profile access control table may act on target-repo content.

### Layer 5 — EventStore State

Read the current WorkflowState from the EventStore.

```python
from src.events.event_store import EventStore
es = EventStore(engagement_id="ENG-<id>")
state = es.current_state()
```

Check:
- `state.active_cycles` — current cycle level and phase
- `state.gate_history` — which gates have passed; marks earlier phases as effectively complete
- `state.artifact_registry` — which artifacts are baselined at which versions
- `state.open_cqs` — CQs already raised; avoid duplicating
- `state.open_algedonics` — active algedonic conditions that may constrain current work

**Key rule:** If `artifact_registry` shows an artifact as baselined, do not re-produce it. Consume it via handoff event. If the artifact's version in the registry is older than the consuming task requires, raise a handoff event requesting the latest version.

---

## 3. Gap Assessment Output

After completing all five discovery layers, the agent produces an internal Gap Assessment before raising any CQs. The Gap Assessment is not an output artifact (not written to work-repositories) but is the agent's working understanding of what is known.

### Gap Assessment Format

| ADM Artifact / Schema Section | Status | Source(s) | Notes |
|---|---|---|---|
| AV §3.3 Stakeholder Register | Covered | `engagement-profile.md` + Confluence-01 | Stakeholder list in Confluence maps to register |
| AV §3.7 Safety Envelope | Missing | — | No safety classification found in any source |
| BA §3.2 Business Capability Map | Partially Covered | `architecture-repository/ba-0.2.0.md` | Draft exists; Level-2 capabilities incomplete |
| DA §3.2 Data Entity Catalog | Inferred | `target-repo/openapi.yaml` + `target-repo/schemas/` | 12 entities inferred from API spec; classification unknown |

**Status values:**

| Status | Meaning | Action |
|---|---|---|
| **Covered** | The section can be produced fully from available sources | Produce artifact section; cite source |
| **Partially Covered** | The section can be partially produced; some fields are missing | Produce what is available; flag gaps |
| **Inferred** | The section can be inferred from non-architecture sources (code, config, docs); inference requires validation | Produce with `[inferred]` tag; raise validation CQs if binding output required |
| **Missing** | No source covers this section; cannot be inferred | Raise a CQ; this section blocks or defers depending on blocking classification |

---

## 4. CQ Generation Rules

After the Gap Assessment, CQs are generated only for **Missing** and **Inferred (binding output)** items.

### Rule 1: Exhaust discovery before asking
A CQ target must be queried only if the information is not in any of the five discovery layers. If a source exists but was not accessible (permission error, empty result), note this in the CQ body rather than assuming the information does not exist.

### Rule 2: Batch by target
CQs for the same target agent or user are batched. Do not issue one CQ per unknown field. Group related unknowns into a single structured CQ record per `clarification-protocol.md §3`.

### Rule 3: Distinguish blocking from non-blocking
If a Missing section is not on the critical path for the current output, classify the CQ as `blocking: false`. The artifact section is marked `[UNKNOWN — non-blocking CQ pending]` and the artifact can proceed to draft. Blocking CQs prevent artifact draft production.

### Rule 4: Mark all inferences in artifacts
Every field derived from a source other than direct user or CQ input must be annotated:
- `[source: user-input]` — came directly from user's stated input
- `[source: <source-id>]` — came from an external source query
- `[inferred: target-repo scan]` — inferred from codebase
- `[derived: <artifact-id>]` — derived from another ADM artifact
- `[assumed: <assumption-text>]` — assumed; assumption documented in artifact header's `assumptions` field

### Rule 5: Record discovery scope
In the artifact's summary header `assumptions` field, include a one-line record of the discovery scope: which layers were scanned and any that were unavailable (e.g., "Discovery: engagement-profile, work-repositories, Confluence-01; target-repo not configured; enterprise-repository standards only").

---

## 5. Non-Linear ADM and Phase Revisit Discovery

When a phase is being revisited (`trigger: revisit`, `phase_visit_count > 1`):

1. **Read the EventStore gate history** to determine why the revisit was triggered. The triggering event payload contains the reason (requirements change, gate rejection, phase-H return, etc.).
2. **Read the existing artifact** for the phase being revisited. The current version is the starting point; do not re-produce from scratch.
3. **Scope the revisit**: only the sections affected by the triggering change are in scope. Identify these by cross-referencing the Change Record (Phase H return) or CQ answer (requirements change) against the artifact's section structure.
4. **Preserve unaffected sections**: increment the artifact version; preserve all non-affected content; update only affected sections; note the revision scope in the version history.
5. **Re-run discovery** (layers 1–5) scoped to the affected sections only — do not re-derive information that was correctly derived in the prior visit.
6. **Re-raise CQs** only for fields that were not resolved in the prior phase visit and are now in scope again.

---

## 6. Skill File Requirements

Every skill file that begins new phase work or enters at any non-EP-0 entry point must contain, within its `## Procedure` section, a **Discovery Scan step** as the first numbered step, before any artifact production. The format is:

```markdown
### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**
- [list specific engagement work-repository paths]
- [list specific external source query types]
- [list target-repo paths if applicable]

**Pre-existing artifacts that may reduce CQ load:**
- [artifact name] → maps to [schema section]
```

Skills authored before this protocol was introduced are subject to the same requirement and should be updated retroactively when the skill file is next revised.

---

## 7. Reference

| Framework Document | Relevant Section |
|---|---|
| `clarification-protocol.md` | Full CQ format, routing, and lifecycle |
| `repository-conventions.md §10` | External source query protocol |
| `repository-conventions.md §11` | Enterprise vs engagement artifact lookup rules |
| `repository-conventions.md §13` | Canonical Artifact Reference Format |
| `sdlc-entry-points.md §2` | Entry point classification and warm-start ingestion |
| `architecture-repository-design.md §4` | EventStore API and WorkflowState |
| `algedonic-protocol.md` | ALG-018 (proceeded without required CQ) |
| `diagram-conventions.md §5` | D1–D6 diagram authoring sequence (Steps D1–D4 catalog ops + D5 PUML authoring + D6 validation) |

---

## 8. Diagram Catalog Lookup (Step 0.D)

**Applies to:** Any skill that produces or updates a diagram artifact.

For skills producing diagram artifacts, the standard Discovery Scan (§2) must include an additional sub-step inserted **after** the five-layer scan (Step 0) and **before** CQ assessment:

### Step 0.D — Diagram Catalog Lookup

> 1. Identify the relevant ontological layers for the current task. Reference:
>    - Business process or capability diagram → `elements/business/` and `processes/`
>    - Data model diagram → `elements/data/` and `connections/er-relationships.yaml`
>    - Application component or interaction diagram → `elements/application/` and `sequences/`
>    - Technology architecture diagram → `elements/technology/` and `connections/archimate.yaml`
>    - Motivation / architecture vision diagram → `elements/motivation/`
> 2. Read the relevant sub-catalog YAML files from `architecture-repository/diagram-catalog/elements/<layer>/` — extract all entries whose name, type, or cross-reference fields match the current artifact domain. Use the `catalog_lookup(query, layer)` tool.
> 3. Read the relevant `connections/` file(s) for known relationships between extracted elements.
> 4. Annotate the working context: "Diagram catalog: N elements found relevant; IDs: [list]"
> 5. When the artifact production step that includes the diagram is reached, execute the full diagram authoring sequence: **D1–D4** (catalog reuse/registration per `framework/diagram-conventions.md §5`) then **D5** (load PUML template via `read_framework_doc("framework/diagram-conventions.md §7.<type>")`, author PUML text, write via `write_artifact`, update `diagrams/index.yaml`) then **D6** (`validate_diagram` — fix and re-validate before emitting `artifact.produced`).

**Catalog bootstrap (if catalog does not yet exist):** SA creates the empty directory structure during Preliminary / Phase A. If an enterprise catalog is configured, SA runs the enterprise catalog import scan first — querying `enterprise-repository/diagram-catalog/` for elements relevant to the engagement scope and importing them into the engagement catalog with engagement-local IDs and `extends:` back-references. No diagram work begins until the engagement catalog bootstrap is complete.

**Write authority:** SA is the sole writer to all files under `diagram-catalog/`. Non-SA agents draft element proposals via `catalog_propose(element_spec)` (emits a `diagram.catalog-proposal` handoff to SA). Non-SA agents write `.puml` files to their own work-repository `diagrams/` directories; SA integrates at phase transition via the same handoff channel.

---

## 9. Standards and Coding Guidelines Discovery (Step 0.S)

**Applies to:** SwA (Phases D, E, F, G), DE (Phase G), DO (Phases D, E, F, G).

For these roles and phases, the standard Discovery Scan (§2) must include an additional sub-step inserted **after** the five-layer scan and **before** CQ assessment:

### Step 0.S — Standards and Coding Guidelines Discovery

> 1. Scan `technology-repository/coding-standards/` — if present, read all files; record findings as "Coding Standards: [list of docs found and their scope]". Use the `discover_standards` tool (returns contents of all files in that directory).
> 2. Scan `enterprise-repository/standards/` — read applicable technology standards (language standards, framework standards, security standards). Focus on standards relevant to the current phase's technology domain.
> 3. **If no coding guidelines found in either location:** Record as discovery gap "COD-GAP-001: No coding standards document found". If the gap is blocking the current task (e.g., DE is implementing a feature and has no style guide or security baseline): raise a CQ to PM/SwA requesting standards authorship before proceeding. If the gap is non-blocking (e.g., SwA is reviewing high-level TA): note the gap and continue.
> 4. **All Phase G skill outputs** (implementation specs, PR reviews, deployment configurations) must cite the governing coding or platform standard by its document path. Example: "Follows `technology-repository/coding-standards/python-style.md §3.2`."

**Rationale:** Coding conventions, security standards, and platform standards are never silently skipped by implementing agents. An agent that has never read the coding standards cannot enforce them in PR review or feature implementation. This step ensures the standards are always loaded into working context before any implementation-layer output is produced.

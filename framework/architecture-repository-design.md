# Architecture Repository Design

**Version:** 1.2.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager + Solution Architect  
**Last Updated:** 2026-04-02

---

## 1. Purpose

This document specifies how architecture data is organised across its three distinct scopes: enterprise-wide long-lived content, engagement-specific project content, and external read-only source integrations. It also specifies the event-sourcing model for workflow state. All agents, tools, and orchestration components must treat these scopes as strictly separated.

The most common error in TOGAF implementations is treating the Architecture Repository as project-scoped. It is not. The Architecture Repository in TOGAF is an **enterprise-wide, long-lived governance asset**. Projects consume it and contribute to it; they do not own it. This document makes that distinction concrete and operational.

---

## 2. Three Scopes of Architecture Data

### 2.1 Scope 1 — Enterprise Architecture Repository

**What it is:** The organisation's canonical store of architecture knowledge that spans all projects and business units. It exists before any engagement starts and persists after any engagement ends. It is the architectural "memory" of the organisation.

**Who owns it:** The Architecture Board (or equivalent governance body), not any individual project or agent.

**Lifetime:** Indefinite. Versioned but never archived wholesale.

**Contents (TOGAF Architecture Repository components):**

| Component | Description | Path |
|---|---|---|
| Architecture Metamodel | How architecture is done in this organisation — tailored frameworks, methodology decisions, governance procedures | `enterprise-repository/metamodel/` |
| Architecture Capability | The EA team's structure, roles, skills, tooling, governance processes | `enterprise-repository/capability/` |
| Architecture Landscape | All architecture artifacts at Strategic and Segment levels (Capability-level produced per engagement) | `enterprise-repository/landscape/` |
| Standards Information Base (SIB) | Approved technology standards, product choices, mandated patterns | `enterprise-repository/standards/` |
| Reference Library | Reusable patterns, templates, reference models, best-practice guidance | `enterprise-repository/reference-library/` |
| Governance Log | Append-only record of all architecture governance decisions across all engagements | `enterprise-repository/governance-log/` |
| Architecture Requirements Repository | Enterprise-level requirements that apply across engagements | `enterprise-repository/requirements/` |
| Solutions Landscape | SBBs deployed or planned across the enterprise | `enterprise-repository/solutions-landscape/` |
| Knowledge Base | Lessons learned, retrospectives, and process improvements accumulated across all engagements | `enterprise-repository/knowledge-base/` |

**Architecture Landscape levels:**

| Level | Scope | Lifetime | Owner |
|---|---|---|---|
| **Strategic Architecture** | Entire enterprise; executive direction; 3–5 year horizon | Years | Enterprise Architect / Architecture Board |
| **Segment Architecture** | Business domain or programme; portfolio level; 1–2 year horizon | Months to years | Domain Architect |
| **Capability Architecture** | Specific project or initiative; produced per engagement | Duration of engagement | Engagement SA/SwA |

Capability-level architectures are produced by individual engagements and **promoted** to the Enterprise Landscape on engagement completion if they represent reusable or durable architecture.

### 2.2 Scope 2 — Engagement Repository (Project-Scoped)

**What it is:** The working store of architecture artifacts and project records for a single ADM engagement cycle. Created at engagement start; closed (and partially promoted to enterprise) at engagement end.

**Who owns it:** The Project Manager for the engagement, with artifact ownership per the RACI matrix.

**Lifetime:** Duration of the engagement plus a defined retention period.

**Structure:** One directory per engagement under `engagements/<engagement-id>/`. Each engagement has its own work-repositories, workflow event log, sprint log, and clarification log.

```
engagements/
  <engagement-id>/
    engagement-profile.md          # Entry point, scope, warm-start status
    workflow.db                    # SQLite event store — canonical, git-tracked (§4.2)
    work-repositories/
      architecture-repository/     # Engagement ABBs: AV, BA, AA, DA
      technology-repository/       # Engagement TA, ADRs, SBB inventory
      project-repository/          # Sprint log, governance records, decision log
      safety-repository/           # SCO, STPA analyses
      delivery-repository/         # Feature branches, PRs, test reports
      qa-repository/               # Test strategies, test cases, defect records
      devops-repository/           # IaC, pipeline configs, deployment records
    workflow-events/               # YAML projection — human-readable, git-tracked (§4.2)
    clarification-log/             # CQ records
    handoff-log/                   # Handoff event records
    algedonic-log/                 # Algedonic signal records
```

**Relationship to Enterprise Repository:**
- The engagement consumes enterprise standards, principles, reference architectures, and the existing Architecture Landscape as **inputs** (read-only during the engagement).
- The engagement contributes new capability-level architectures, validated SBBs, governance log entries, and lessons learned back to the Enterprise Repository as **outputs** (written at engagement close or significant milestones).
- If the engagement produces content that is suitable for promotion to Segment or Strategic level, the Architecture Board decides on promotion.

### 2.3 Scope 3 — External Read-Only Sources

**What they are:** Existing organisational information stores that agents should be able to query when building context, but must never write to.

**Access model:** Each external source is accessed via a named **source adapter** configured in `external-sources/`. The adapter defines the source type, connection details, access credentials (never hardcoded — referenced from environment or secrets manager), and the indexing strategy.

**Why read-only is a hard rule:** External sources contain organisation-owned content whose write governance is managed by other teams and tools. An agent that writes to Confluence or Jira could corrupt organisation records, create shadow state, or bypass governance controls outside this system.

**Supported source types:**

| Source Type | Purpose | Read Pattern |
|---|---|---|
| Confluence | Product documentation, meeting notes, decision records, existing architecture docs | Full-text search + page fetch by title/path |
| Jira | Issue tracking, project status, requirement tickets, change requests | JQL query + issue fetch |
| External Git (read-only) | Existing codebases, company EA repositories, shared standards repos | File read by path + keyword search |
| SharePoint / Google Drive | Document libraries, specification files | File search + fetch |
| YAML/JSON APIs | Existing tooling with REST APIs (e.g., Backstage, Ardoq) | API query |

**Source adapter configuration format** (`external-sources/<source-id>.config.yaml`):

```yaml
source-id:       # Unique identifier, e.g. "company-confluence"
source-type:     # confluence | jira | git | sharepoint | api
display-name:    # Human-readable name
base-url:        # Base URL (no credentials)
auth-method:     # env-var | secrets-manager | oauth-token
auth-config:     # Points to credential location, never the credential itself
  env-var: CONFLUENCE_API_TOKEN   # example
index-scope:     # Which content is in scope for indexing
  spaces: [ARCH, ENG, PRODUCT]   # For Confluence: space keys
  projects: [PROJ-1, PROJ-2]     # For Jira: project keys
  paths: [src/, docs/]           # For git: paths to include
access-pattern:  # search-only | fetch-by-id | full-index
purpose: |       # One paragraph: what this source contains and why agents use it
notes: |         # Any known limitations, content quality caveats, or access restrictions
```

Agents query external sources through a **Source Query** operation (defined in `repository-conventions.md §10`). All source queries are logged. Agents may not write to, delete from, or modify content in any external source.

### 2.4 Scope 4 — Target Project Repository

**What it is:** The software project being built, modified, or analysed by this engagement. It is a separate git repository that exists independently of the framework. The framework points to it; it does not point back to the framework.

**Why it is distinct from the three engagement scopes:** The target project repository is owned by a development team, not by the SDLC framework. It has its own commit history, branching strategy, CI/CD pipelines, and access controls that predate the engagement. The framework must not pollute it with framework files, agent metadata, or engagement artifacts.

**Access model:**

| Agent Role | Access Level | What They Do |
|---|---|---|
| Implementing Developer | **Read-write** | Creates branches, commits code, submits PRs |
| DevOps / Platform Engineer | **Read-write** (IaC and pipeline paths only) | Modifies CI/CD configs, infrastructure-as-code |
| QA Engineer | **Read-only** | Runs tests against the codebase |
| Solution Architect, SwA/PE | **Read-only** | Reads existing code for EP-G reverse architecture reconstruction |
| All other agents | **No direct access** | Work only from delivered reports and artifacts |

**Configuration:** The target repository path or URL is specified in the engagement profile (`§3` of `sdlc-entry-points.md`) and in `engagements-config.yaml`. A local clone is maintained at `engagements/<id>/target-repo/` (git-ignored from the framework repo — it is a separate checkout, not nested content).

**Delivery repository relationship:** The engagement's `work-repositories/delivery-repository/` does **not** hold code. It holds delivery *metadata*: PR records, branch references, test execution reports, code quality reports, and deployment records that document work done in the target repository. The actual code lives only in the target repository.

**Framework isolation guarantee:** No framework file, agent definition, skill file, or engagement artifact is ever committed to the target project repository. The framework and the project are always separate git repositories.

---

## 3. Git Repository Layout

The system uses the following git repository organisation:

### 3.1 The Framework Repository (this repository)

Contains: agent definitions, skill files, framework documents, artifact schemas, Python source code, engagement data, and the enterprise architecture repository. This is the "operating software and working state" of the system.

**One framework instance per project.** Clone or fork this repository once per software project you want to work with. Framework files never live inside the target project repository. The target project is a separate git repository pointed to by the engagement configuration (§3.4).

```
<my-project>-sdlc/                 # Framework instance for one project (clone of sdlc-agents)
  framework/                       # Cross-cutting specifications and artifact schemas
  agents/                          # Agent definitions (AGENT.md) and skill files
  src/                             # Python implementation
    events/                        # EventStore + Pydantic event models (§4)
    agents/                        # PydanticAI agent wrappers
    orchestration/                 # Sprint runner, handoff bus, CQ bus
    sources/                       # External source adapters
  tests/                           # Integration tests
  external-sources/                # Source adapter configuration files (*.config.yaml)
  enterprise-repository/           # Enterprise architecture data (embedded mode)
    metamodel/
    capability/
    landscape/strategic/
    landscape/segment/
    landscape/capability/
    standards/
    reference-library/
    governance-log/
    requirements/
    solutions-landscape/
    knowledge-base/
  engagements/
    <engagement-id>/
      engagement-profile.md        # Includes target-repository configuration (§3.4)
      workflow.db                  # SQLite event store — canonical, git-tracked binary
      workflow-events/             # YAML projection — human-readable, git-tracked
      clarification-log/           # CQ prose records
      handoff-log/                 # Handoff prose records
      algedonic-log/               # Algedonic signal records
      target-repo/                 # Local clone of the target project — .gitignored
      work-repositories/
        architecture-repository/
        technology-repository/
        project-repository/
        safety-repository/
        delivery-repository/       # Delivery METADATA only — no code (see §2.4)
        qa-repository/
        devops-repository/
  enterprise-repository-config.yaml
  engagements-config.yaml
  CLAUDE.md
  specs/IMPLEMENTATION_PLAN.md
```

Two projects side by side on a developer's machine:

```
~/work/
  projectA-sdlc/       ← framework instance for Project A
    engagements/ENG-001/
      target-repo/     ← local clone of projectA's code repo (.gitignored in framework)
  projectB-sdlc/       ← framework instance for Project B
    engagements/ENG-001/
      target-repo/     ← local clone of projectB's code repo (.gitignored in framework)
  projectA/            ← the actual Project A code repository (separate, team-owned)
  projectB/            ← the actual Project B code repository (separate, team-owned)
```

### 3.2 Enterprise Repository (configurable)

**Option A — Embedded:** `enterprise-repository/` is a directory in this repo. Suitable for a single organisation with no pre-existing EA tooling.

**Option B — Git submodule:** `enterprise-repository/` points to an external git repo owned by the EA team. The system mounts it read-write for authorised agents (SA, Architecture Board). This is the recommended approach for organisations with existing EA repositories.

**Option C — External:** No local enterprise repository directory. The enterprise repository is an external system (e.g., Ardoq, LeanIX, Confluence-based EA wiki) accessed exclusively via an external source adapter (read-only from the system's perspective during engagements).

The `enterprise-repository-config.yaml` at repo root specifies which option is active:

```yaml
enterprise-repository:
  mode: embedded | submodule | external
  path: enterprise-repository/       # for embedded or submodule
  source-adapter: company-ea-wiki    # for external (references external-sources/<id>.config.yaml)
  writable-by: [solution-architect, architecture-board]
  promotion-requires: architecture-board-approval
```

### 3.3 Engagement Repositories (configurable)

**Option A — Single repo:** All engagements live under `engagements/` in this repo. Suitable for small teams.

**Option B — Per-engagement repos:** Each engagement is a separate git repository. The framework repo holds configuration pointing to each. Suitable for organisations running many concurrent engagements.

The `engagements-config.yaml` specifies the active model:

```yaml
engagements:
  mode: single-repo | multi-repo
  base-path: engagements/            # for single-repo
  active-engagements:
    - id: ENG-001
      name: "Project Nighthawk"
      path: engagements/ENG-001/     # single-repo
      # OR:
      repo-url: git@github.com:org/nighthawk-architecture.git  # multi-repo
      entry-point: EP-B
      status: active
```

### 3.4 Target Project Repository (per-engagement)

Each engagement points to exactly one **target project repository** — the software project being built. This is configured in `engagements-config.yaml` and in the engagement's `engagement-profile.md`.

```yaml
# In engagements-config.yaml, per-engagement entry:
- id: ENG-001
  name: "Project Nighthawk — API Gateway"
  path: engagements/ENG-001/
  entry-point: EP-0
  status: active
  target-repository:
    url: git@github.com:org/nighthawk-api.git   # OR local path: /home/user/nighthawk-api
    default-branch: main
    local-clone-path: engagements/ENG-001/target-repo/   # .gitignored in this repo
    access:
      implementing-developer: read-write        # creates branches, commits, PRs
      devops-platform-engineer: read-write       # IaC and pipeline paths only
      qa-engineer: read-only                    # runs tests
      solution-architect: read-only             # EP-G reverse architecture
      software-architect: read-only             # EP-G reverse architecture
      all-others: none                          # work from delivered reports only
```

**`target-repo/` is git-ignored** in the framework repository. It is a local working clone of the target project. Each agent invocation that needs code access clones or fetches from the configured `url`. The framework never commits code changes into `target-repo/` itself — changes are pushed directly to the target repository's remote.

**Delivery metadata vs code:** The engagement's `work-repositories/delivery-repository/` holds delivery *metadata* about work done in the target repository:
- PR records (PR number, title, status, link)
- Branch references (branch name, commit SHA, associated work package)
- Test execution reports (produced by QA agent, reference to target repo commit)
- Code quality and security scan results
- Deployment records (which version was deployed where)

The actual source code, commit history, and CI/CD results live entirely in the target repository.

---

## 4. Event Sourcing for Workflow State

### 4.1 Why Event Sourcing

File-based artifact storage (git-tracked) handles *what was produced* effectively — git is inherently an event log for content. But it does not capture *what the workflow was doing* at any point:

- Which ADM phases have been entered, revisited, or exited?
- What gate evaluations have been performed and what were their outcomes?
- Which CQs are open, and what is their blocking status?
- Has Phase H sent the system back to Phase B (requiring Phase B artifacts to be re-opened)?
- Which iteration type is currently active?

Without explicit workflow state, agents cannot determine what phase they are in, what has already been done, or whether a phase is being revisited versus entered for the first time. This matters critically because of the ADM's iterative and cyclical nature (§5).

Git commit history cannot represent workflow state because: (1) it mixes workflow events with content changes; (2) it cannot represent state transitions that don't produce artifact changes (e.g., a gate evaluation that passes with no artifact modifications); (3) reconstructing workflow state from git log requires reading all commits, which is prohibitively expensive.

### 4.2 Event Storage: SQLite Canonical + YAML Human-Readable Projection

The workflow event log has **two representations with distinct roles**:

| Store | Path | Role | Git-tracked? | Write authority |
|---|---|---|---|---|
| **SQLite database** | `engagements/<id>/workflow.db` | **Canonical** — Pydantic-validated, ACID-protected, source of truth | **Yes** — committed at sprint boundaries alongside artifacts | EventStore API only |
| **YAML event files** | `engagements/<id>/workflow-events/<timestamp>-<type>-<seq>.yaml` | **Human-readable projection** — reviewable in PRs; read by agents on startup; consistency-checked against SQLite | **Yes** — exported at sprint boundaries | EventStore API only |

**Why SQLite is canonical and git-tracked:**  
SQLite is the only representation agents cannot corrupt — they have no mechanism to write to `workflow.db` except through `EventStore.append()`, which validates every event via Pydantic before insertion. `ACID` transactions ensure partial writes never produce corrupt state, and the append-only API prevents updates or deletes. Because `workflow.db` is committed to git, a fresh clone includes the complete event history — no reconstruction step is needed. Git stores it as a binary blob; diffs are not human-readable, but that is what the YAML projection is for.

**Why YAML files are also committed:**  
YAML files serve agents and humans, not the database. Agents can read the current sprint's event timeline from YAML files without opening SQLite. PRs show meaningful diffs of what happened in a sprint. The YAML projection is also the fallback for corruption recovery — see below.

**Write path:** On every `EventStore.append()` call:
1. Pydantic validates the event against its registered payload model
2. SQLite `INSERT` within a WAL-mode transaction — the canonical write
3. YAML file written to `workflow-events/` (projection of the same data)

Step 3 is best-effort: YAML write failure logs a warning but does not roll back the SQLite transaction. The canonical state is always safe. Missing YAML files are generated by `export_yaml()` at sprint close.

**Startup consistency check:** On `EventStore.__init__`, the sequence count in SQLite is compared against the number of YAML files in `workflow-events/`. If there is a discrepancy (e.g., YAML files were manually edited or SQLite was manipulated outside the API), a warning is raised and the SQLite record takes precedence. This check catches accidental corruption of either representation.

**Git workflow:** At each sprint close, the PM agent's sprint-close skill calls `store.export_yaml()` (catch-up any missing YAMLs), then commits `workflow.db` + all `workflow-events/*.yaml` + produced artifacts in a single structured commit.

**Corruption recovery:** If `workflow.db` is somehow corrupted or manually deleted, `import_from_yaml()` reconstructs it from the committed YAML files. If both are lost, `git checkout HEAD -- engagements/<id>/workflow.db` restores the last committed snapshot.

**SQLite schema (managed by Alembic migrations in `src/events/migrations/`):**

```sql
CREATE TABLE events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    TEXT    UNIQUE NOT NULL,        -- <engagement-id>-EV-<sequence>
    event_type  TEXT    NOT NULL,               -- dotted-name taxonomy (§4.4)
    timestamp   TEXT    NOT NULL,               -- ISO 8601
    engagement_id TEXT  NOT NULL,
    cycle_id    TEXT,                           -- NULL for engagement-level events
    actor       TEXT    NOT NULL,               -- agent role | "user" | "system"
    correlation_id TEXT,
    payload     TEXT    NOT NULL,               -- JSON-serialized Pydantic model payload
    CONSTRAINT valid_json CHECK (json_valid(payload))
);

CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_cycle ON events(cycle_id);
CREATE INDEX idx_events_correlation ON events(correlation_id);

CREATE TABLE snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_at TEXT    NOT NULL,               -- event_id of last event included
    timestamp   TEXT    NOT NULL,
    state       TEXT    NOT NULL                -- JSON-serialized WorkflowState Pydantic model
);
```

**Alembic strategy:** Alembic manages the schema definition centrally in the framework repository (`src/events/migrations/`). All engagements use the same schema. Each new `workflow.db` is bootstrapped by running `alembic upgrade head` against the engagement's database file. Schema migrations are applied at engagement startup when the `schema_version` is stale.

### 4.3 Event Schema

All events share a common Pydantic base model (`src/events/models/base.py`):

```python
class EventEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)  # events are immutable after creation

    event_id: str          # Unique: <engagement-id>-EV-<sequence>; auto-generated
    event_type: str        # Dotted-name taxonomy (§4.4); validated against EventRegistry
    timestamp: datetime    # Auto-set to UTC now() at creation
    engagement_id: str
    cycle_id: str | None = None   # None for engagement-level events
    actor: str             # Agent role canonical name | "user" | "system"
    correlation_id: str | None = None  # artifact-id, sprint-id, cq-id, or algedonic-id
    payload: BaseEventPayload      # Event-type-specific; see §4.4 for per-type models
```

Each event type in §4.4 has a corresponding typed `payload` subclass (e.g., `PhaseEnteredPayload`, `GatePassedPayload`). The `EventRegistry` maps `event_type` strings to their payload classes, enabling full round-trip serialisation and validation.

**YAML envelope format** (for audit export and human review):

```yaml
event-id:        # Unique: <engagement-id>-EV-<sequence>
event-type:      # See §4.4 taxonomy
timestamp:       # ISO 8601
engagement-id:   # Parent engagement
cycle-id:        # Which ADM cycle within the engagement (see §5 for multi-cycle)
actor:           # Agent role or "user" or "system"
correlation-id:  # ID of the artifact, sprint, CQ, gate, or algedonic signal this event relates to
payload:         # Event-type-specific data (see §4.4)
```

### 4.4 Event Taxonomy

**Cycle events:**
```yaml
cycle.initiated:      # New ADM cycle started; payload: cycle-id, iteration-type, parent-cycle-id (if nested)
cycle.closed:         # ADM cycle completed; payload: outcomes, promoted-artifacts
```

**Phase events:**
```yaml
phase.entered:        # Phase begins; payload: phase-id, iteration-number, trigger (initial | revisit | phase-h-return)
phase.suspended:      # Phase paused (e.g., blocking CQ); payload: reason, blocking-cq-id
phase.resumed:        # Phase resumed after suspension; payload: cq-ids-resolved
phase.exited:         # Phase work complete, gate eligible; payload: artifacts-produced
```

**Gate events:**
```yaml
gate.evaluated:       # Gate checklist assessed; payload: phase-transition, checklist-results
gate.passed:          # Gate passes; payload: conditions (if conditional pass)
gate.held:            # Gate on hold; payload: blocking-items, target-sprint
gate.escalated:       # Gate escalated to algedonic; payload: algedonic-id
```

**Sprint events:**
```yaml
sprint.opened:        # Sprint starts; payload: sprint-id, stream, scope
sprint.suspended:     # Sprint paused; payload: reason
sprint.closed:        # Sprint complete; payload: artifacts-produced, open-items
```

**Artifact events:**
```yaml
artifact.drafted:     # Artifact at version 0.x.x created; payload: artifact-id, path
artifact.baselined:   # Artifact promoted to ≥1.0.0; payload: artifact-id, version
artifact.superseded:  # Artifact replaced by newer version; payload: artifact-id, successor-id
artifact.promoted:    # Capability artifact promoted to enterprise repository; payload: target-level
```

**Handoff events:**
```yaml
handoff.issued:       # Artifact transferred; payload: handoff-id, artifact-id, from, to-agents
handoff.acknowledged: # Consuming agent confirms receipt; payload: retrieval-intent (summary|full)
```

**CQ events:**
```yaml
cq.raised:            # Clarification Request issued; payload: cq-id, blocking, target
cq.answered:          # Answer received; payload: cq-id, answered-by
cq.assumption-made:   # Work proceeded without answer; payload: cq-id, assumption-text
cq.closed:            # CQ resolved (answered or withdrawn); payload: cq-id, resolution
```

**Algedonic events:**
```yaml
algedonic.raised:     # Signal issued; payload: signal-id, trigger-id, severity
algedonic.acknowledged: # Target acknowledges; payload: signal-id
algedonic.resolved:   # Signal resolved; payload: signal-id, resolution
```

**Phase-revisitation events:**
```yaml
phase.return-triggered: # Phase H or requirements change triggers return to earlier phase
                        # payload: target-phase, trigger-source, change-record-id
```

**External source events:**
```yaml
source.queried:       # External source was queried; payload: source-id, query-type, query-summary
                      # (logged but not used for state reconstruction)
```

### 4.5 State Snapshot

To avoid replaying the entire event log, the `EventStore` maintains a **state snapshot** in two forms:

- **SQLite `snapshots` table row** — refreshed atomically after every `sprint.closed` event; the fast-path for runtime queries
- **`workflow-events/state-snapshot.yaml`** — a git-tracked YAML file overwritten at each sprint close; provides a human-readable current-state summary visible in PRs

The SQLite `snapshots` table row is the fast-path operational state. The YAML snapshot file is the git-tracked human-readable state summary at each sprint boundary. If the SQLite snapshot row is absent, `current_state()` falls back to `replay_state()` (which reads the SQLite event rows; if those are also absent, it calls `import_from_yaml()` to rebuild from the committed YAML export).

**`WorkflowState` Pydantic model (`src/events/models/state.py`):**

```python
class CycleState(BaseModel):
    cycle_id: str
    iteration_type: Literal["context", "definition", "transition", "governance"]
    parent_cycle_id: str | None
    current_phase: str                 # e.g. "A", "B", "G"
    phase_visit_counts: dict[str, int] # {"A": 1, "B": 2, ...} — incremented on re-entry
    active_sprints: list[str]
    open_cqs: list[str]               # cq-ids
    open_algedonics: list[str]        # signal-ids

class GateRecord(BaseModel):
    transition: str                   # e.g. "A→B"
    status: Literal["passed", "held", "pending", "escalated"]
    conditions: list[str]             # conditional-pass conditions if any

class ArtifactRecord(BaseModel):
    artifact_id: str
    version: str
    status: Literal["draft", "baselined", "superseded", "archived"]
    path: str

class WorkflowState(BaseModel):
    snapshot_at: str                  # event_id of last event included
    timestamp: datetime
    engagement_id: str
    active_cycles: list[CycleState]
    gate_history: list[GateRecord]
    artifact_registry: dict[str, ArtifactRecord]
```

**`EventStore` retrieval API:**

```python
store = EventStore(engagement_id="ENG-001")

# Fast path — reads snapshot table row (single SELECT)
state: WorkflowState = store.current_state()

# Full replay — for audit, corruption recovery, or snapshot reconstruction
state: WorkflowState = store.replay_state()

# Targeted queries
events = store.query(event_type="phase.entered", cycle_id="CYCLE-001")
phase_visits = store.phase_visit_count(phase_id="B", cycle_id="CYCLE-001")
open_cqs = store.open_cqs(blocking_only=True)
```

If the snapshot is absent or corrupted, `current_state()` falls back to `replay_state()` and writes a fresh snapshot. Corruption of individual event rows is detected via an integrity check on startup (`EventStore.check_integrity()`) which validates JSON payloads and sequence continuity.

---

### 4.6 EventStore Python API

The `EventStore` class is the **sole write path** to the workflow database. No agent skill file, orchestration component, or test fixture may import `sqlite3` directly for engagement event data.

**Module layout (`src/events/`):**

```
src/events/
  __init__.py             # Exports EventStore + all event payload models
  event_store.py          # EventStore class
  registry.py             # EventRegistry: maps event_type → payload class
  models/
    base.py               # EventEnvelope + BaseEventPayload
    state.py              # WorkflowState, CycleState, GateRecord, ArtifactRecord
    cycle.py              # CycleInitiatedPayload, CycleClosedPayload
    phase.py              # PhaseEnteredPayload, PhaseSuspendedPayload, ...
    gate.py               # GateEvaluatedPayload, GatePassedPayload, ...
    sprint.py             # SprintOpenedPayload, SprintClosedPayload, ...
    artifact.py           # ArtifactDraftedPayload, ArtifactBaselinedPayload, ...
    handoff.py            # HandoffIssuedPayload, HandoffAcknowledgedPayload
    cq.py                 # CQRaisedPayload, CQAnsweredPayload, ...
    algedonic.py          # AlgasonicRaisedPayload, AlgedonicResolvedPayload, ...
    source.py             # SourceQueriedPayload
  migrations/
    env.py                # Alembic env
    versions/             # Migration scripts (auto-generated + manually verified)
  export.py               # YAML audit export / import
```

**EventStore write path:**

```python
# All writes go through EventStore.append()
store.append(PhaseEnteredPayload(
    phase_id="A",
    iteration_number=1,
    trigger="initial"
))
# Internally:
# 1. EventEnvelope is constructed (auto-generates event_id, timestamp)
# 2. Pydantic validation runs on the full envelope + payload
# 3. INSERT INTO events ... (within a transaction)
# 4. If sprint.closed event: UPDATE snapshots table atomically in same transaction
# 5. Returns the persisted EventEnvelope
```

**Validation failure handling:** If Pydantic validation fails, `EventStore.append()` raises `EventValidationError` with the full Pydantic error detail. The calling agent skill must catch this and either correct the event data or raise an algedonic signal if the data cannot be corrected.

**Migration policy:** Alembic manages the SQLite schema. When the framework repository is updated with new event types or schema changes, `alembic upgrade head` is run at engagement startup. Migration scripts are committed to the framework repository and reviewed before merge.

---

### 4.7 Log Directory Records vs SQLite Events

The engagement directories `clarification-log/`, `handoff-log/`, and `algedonic-log/` hold **detailed prose records** — these are distinct from the SQLite workflow events and serve a different purpose.

| Record Type | Location | Contents | Purpose |
|---|---|---|---|
| **CQ record** | `engagements/<id>/clarification-log/<cq-id>.md` | Full CQ document: context, what is known, what is unknown, specific questions, blocking status, answers when received | The authoritative, human-readable CQ specification that agents and users read and respond to |
| **Handoff record** | `engagements/<id>/handoff-log/<handoff-id>.md` | Artifact summary copy, consuming agent acknowledgements, retrieval intent, flags | The formal transfer record agents append acknowledgements to |
| **Algedonic signal record** | `engagements/<id>/algedonic-log/<signal-id>.md` | Condition description, affected artifacts, immediate action taken, required decision, resolution record | The authoritative escalation record; the escalation target writes the resolution here |
| **SQLite `cq.raised` event** | `workflow.db` events table | `cq-id`, `blocking`, `target`, `blocks-task` | Workflow signal: tells the state machine a CQ exists and whether it is blocking |
| **SQLite `handoff.issued` event** | `workflow.db` events table | `handoff-id`, `artifact-id`, `from`, `to-agents` | Workflow signal: tells the state machine an artifact transfer occurred |
| **SQLite `algedonic.raised` event** | `workflow.db` events table | `signal-id`, `trigger-id`, `category`, `severity` | Workflow signal: tells the state machine an algedonic condition is active |

**Design principle:** The markdown log records are the **content**; the SQLite events are the **signals**. Agents read the markdown records for substance and details. The SQLite events are used for state reconstruction and queries ("how many open blocking CQs are there?", "has the algedonic been resolved?"). The markdown records are git-tracked and committed alongside the corresponding YAML event file.

### 4.8 Engagement Bootstrap Procedure

When a new engagement is opened, the PM agent executes the following bootstrap procedure before any sprint work begins:

1. **Create engagement directory** structure under `engagements/<id>/` per §2.2.
2. **Initialise `workflow.db`**: Run `alembic upgrade head` against the new database file.
3. **Write `engagement-profile.md`** at `engagements/<id>/engagement-profile.md` — see `sdlc-entry-points.md §3` for schema.
4. **Update `engagements-config.yaml`** at repo root — add entry for the new engagement with status `active`.
5. **Emit `cycle.initiated`** event (the first event in the engagement's event log).
6. **Create initial git commit**: stage and commit `engagements/<id>/engagement-profile.md`, `engagements/<id>/workflow-events/` (first event YAML), and the updated `engagements-config.yaml`.
7. **Proceed to entry assessment** per `sdlc-entry-points.md §4`.

The engagement is considered **open** once step 6 is committed. The PM agent owns this procedure.

---

## 5. Multi-Cycle and Multi-Level Architecture

### 5.1 ADM Cycle Types

Each ADM engagement is characterised by one or more **cycles**, each associated with an architecture level:

| Cycle Level | Architecture Level | Typical Trigger | Outputs to Landscape |
|---|---|---|---|
| Strategic | Enterprise-wide | Major business transformation, new strategic direction | Strategic Architecture promoted to Enterprise Landscape |
| Segment | Business domain / programme | Programme initiation, domain architecture needed | Segment Architecture promoted to Enterprise Landscape |
| Capability | Individual project / initiative | Project initiation, capability delivery needed | Capability Architecture; selectively promoted |

In this system, most engagements are **Capability-level cycles**. They consume Strategic and Segment architectures from the Enterprise Repository as constraints and inputs.

### 5.2 Cycle Initiation Relationships

A higher-level cycle's Phase F (Migration Planning) can initiate one or more lower-level cycles:

```
Strategic ADM Cycle
  Phase F → initiates → Segment ADM Cycle(s)
                            Phase F → initiates → Capability ADM Cycle(s)
                                                      Phase G → feeds back →
                                                      Segment Landscape (via promotion)
```

When a new cycle is initiated by a parent cycle, a `cycle.initiated` event is written with the `parent-cycle-id` set to the initiating cycle. This relationship governs:
- Which enterprise-level constraints the child cycle inherits
- Which artifacts the child cycle must validate against
- How the child cycle's outputs are reviewed by the parent cycle's governance

### 5.3 Concurrent Cycles

Multiple capability cycles may run simultaneously within the same engagement or across the organisation. Their relationship must be explicitly governed:

| Relationship Type | Description | Governance Mechanism |
|---|---|---|
| **Independent** | No shared artifacts or components | No cross-cycle governance needed |
| **Consuming** | Cycle B uses artifacts produced by Cycle A | Cycle A artifacts in Cycle B's `depends-on`; Cycle B's gate checklist references Cycle A's baselined artifacts |
| **Conflicting** | Both cycles modify the same architectural domain | Architecture Board arbitration required; conflict triggers `algedonic.raised` |
| **Sequential** | Cycle B begins after Cycle A Phase F completes | Cycle B's `cycle.initiated` event references Cycle A's Phase F gate |

Concurrent cycle coordination is the responsibility of the Project Manager across all cycles, with Architecture Board oversight for conflicts.

---

## 6. Enterprise Promotion Protocol

When a capability-level engagement produces architecture that is valuable at Segment or Strategic level, the relevant artifacts are promoted to the Enterprise Repository.

**Promotion triggers:**
- Engagement closure (PM initiates promotion review)
- A new capability architecture that fills a documented gap in the Segment landscape
- An ADR that establishes a new organisational technology standard

**Promotion procedure:**
1. SA identifies candidate artifacts for promotion during engagement closeout.
2. PM raises a **Promotion Request** to the Architecture Board (or equivalent authority).
3. Architecture Board reviews the artifact against the current landscape; may request modifications.
4. On approval: artifact is copied to the Enterprise Landscape at the appropriate level; version reset to reflect enterprise adoption; original engagement artifact remains unchanged.
5. `artifact.promoted` event written to both the engagement event log and the Enterprise Governance Log.

---

## 7. Repository Conventions Alignment

This document governs the *structure* of data. Conventions for *how agents interact with that data* are in `repository-conventions.md`. The key extensions required by this document:

- §10 of `repository-conventions.md`: External Source Query protocol
- §11: Enterprise vs. Engagement artifact lookup rules (agents always check enterprise artifacts before requesting a CQ about domain standards)
- §12: Promotion procedure for engagement-to-enterprise artifact transfer

---

## 8. Summary: What Lives Where

| Content | Scope | Location | Mutability |
|---|---|---|---|
| Architecture Principles | Enterprise | `enterprise-repository/metamodel/principles/` | Write: SA + Architecture Board |
| Strategic Architecture | Enterprise | `enterprise-repository/landscape/strategic/` | Write: Architecture Board |
| Segment Architecture | Enterprise | `enterprise-repository/landscape/segment/` | Write: SA + Architecture Board |
| Technology Standards (SIB) | Enterprise | `enterprise-repository/standards/` | Write: Architecture Board |
| Reference Library | Enterprise | `enterprise-repository/reference-library/` | Write: SA + Architecture Board |
| Governance Log | Enterprise | `enterprise-repository/governance-log/` | Append-only: PM |
| Knowledge Base | Enterprise | `enterprise-repository/knowledge-base/` | Write: PM |
| Engagement architecture artifacts (AV, BA, AA, DA, TA, etc.) | Engagement | `engagements/<id>/work-repositories/architecture-repository/` | Write: SA (owner per RACI) |
| Technology Architecture + ADRs | Engagement | `engagements/<id>/work-repositories/technology-repository/` | Write: SwA |
| Sprint records, governance | Engagement | `engagements/<id>/work-repositories/project-repository/` | Write: PM |
| Safety analyses | Engagement | `engagements/<id>/work-repositories/safety-repository/` | Write: CSCO |
| Feature code, PRs | Engagement | `engagements/<id>/work-repositories/delivery-repository/` | Write: Developer |
| Test artifacts | Engagement | `engagements/<id>/work-repositories/qa-repository/` | Write: QA |
| IaC, pipelines | Engagement | `engagements/<id>/work-repositories/devops-repository/` | Write: DevOps |
| Workflow event store (canonical, git-tracked) | Engagement | `engagements/<id>/workflow.db` | Append-only: EventStore API; committed at sprint close |
| Workflow event YAML projection (git-tracked, human-readable) | Engagement | `engagements/<id>/workflow-events/*.yaml` | Exported by EventStore; committed at sprint close |
| Workflow state snapshot YAML (git-tracked) | Engagement | `engagements/<id>/workflow-events/state-snapshot.yaml` | Overwritten at sprint close by EventStore |
| CQ prose records | Engagement | `engagements/<id>/clarification-log/` | Write: raising agent |
| Handoff prose records | Engagement | `engagements/<id>/handoff-log/` | Write: producing agent |
| Algedonic prose records | Engagement | `engagements/<id>/algedonic-log/` | Append-only: raising agent |
| External source configs | System | `external-sources/` | Write: system admin only |
| Agent definitions, skills, schemas | System | `framework/`, `agents/` | Write: authorised (per review) |
| Capability arch promoted to enterprise | Enterprise | `enterprise-repository/landscape/capability/` | Write: SA + Architecture Board |
| Confluence, Jira, external git | External | Remote systems | **Read-only by all agents** |

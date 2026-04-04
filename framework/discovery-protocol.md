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

Before the five layers, execute Step 0.L (Learnings Lookup) to prime the agent's working context with corrections from prior work. This step shapes how the agent interprets all subsequent layers.

### Step 0.L — Learnings Lookup

Execute **before** Layer 1. Governed by `framework/learning-protocol.md §5`.

1. Call `query_learnings(phase=<current_phase>, artifact_type=<primary_artifact_for_this_skill>, domain=<engagement_domain_from_profile>)`.
2. Additionally query `enterprise-repository/knowledge-base/learnings/` with the same filter (if it exists).
3. Sort results: S1 importance first, then S2, then most recent sprint. Cap at 5 entries total.
4. If any entries are returned: prepend their `Correction` texts to working context as **"Learnings from prior work relevant to this task:"**. If none: skip.
5. Proceed to Layer 1.

**Purpose:** Learnings must precede artifact reading — they shape how the agent interprets what it finds. A correction such as "when AV §3.7 describes an 'internal' system, check for employee PII handling" changes how the agent reads the AV in Layer 1. Post-hoc insertion would miss this interpretive benefit.

---

### Layer 1 — Engagement State

All engagement state is accessed through tools — no direct filesystem reads. The `ModelRegistry` and `EventStore` provide indexed, filtered access without loading artifact bodies unless explicitly requested.

**Step 1.1 — Engagement context from `AgentDeps` (in-process, no tool call needed):**
`deps.engagement` contains the parsed engagement configuration (entry point, target repositories, sprint review settings). `deps.workflow_state` contains current phase, sprint, open CQs, pending handoffs, gate outcomes, and active algedonic signals. Both are injected at invocation time — no file read required.

**Step 1.2 — Filter artifact index by metadata:**
`list_artifacts(phase_produced=<current_phase>, status=["baselined","draft"])` → returns metadata records (artifact-id, artifact-type, version, status, path, owner-agent) without loading bodies. Combine filters as needed: `artifact_type`, `safety_relevant`, `domain`. For each relevant result, call `read_artifact(id, mode="summary")` (frontmatter + first two §content sections, ≈200–400 tokens). Escalate to `mode="full"` only when task correctness requires the complete content — log the reason.

**Role-specific scan priority (Step 1.2 filter order):**
- **SA** — prioritise `owner-agent=SA` artifacts first (motivation, strategy, business layers in `architecture-repository/`); then read `owner-agent=SwA` application-layer artifacts when performing Phase C traceability review or Phase H cross-reference check. Filter: `list_artifacts(layer=["motivation","strategy","business"])`.
- **SwA (Phase C)** — prioritise `architecture-repository/model-entities/application/` (own write scope); also scan business-layer artifacts for realisation input. Filter: `list_artifacts(layer=["application","business"])`. SA's business-layer artifacts are the primary inputs.
- **SwA (Phase D onward)** — prioritise `technology-repository/` entities; read application-layer entities for TA constraint derivation. Filter: `list_artifacts(layer=["technology","application"])`.
- **DE/DO** — scan `technology-repository/coding-standards/` first (Step 0.S); then filter by `layer="technology"`. Full procedure in §9.

**Step 1.3 — Search artifact content by concept (when metadata filters are insufficient):**
`search_artifacts(query="<natural language description of what is needed>", **filter)` → queries the ModelRegistry FTS5 index over artifact `§content` blocks; returns ranked `(ArtifactRecord, snippet)` pairs. Use this when the artifact type is uncertain, when looking for a concept that may appear across multiple artifact types, or when prior phases may have documented something relevant without a predictable metadata signature. The semantic tier (when available) enables similarity-based retrieval beyond keyword matching. Review snippets, then call `read_artifact(id, mode="summary")` for selected results.

**Step 1.4 — Query workflow events for interaction history:**
`query_events(event_types=["cq.raised","cq.answered","handoff.created","handoff.acknowledged","algedonic.raised","algedonic.resolved"], phase=<current_phase>)` — surfaces answered CQs whose content is relevant to the current task, pending handoffs not yet incorporated, and active algedonic signals that constrain scope. Do not re-read what `deps.workflow_state` already provides; this step retrieves event *payloads* (CQ answer text, handoff artifact content) not covered by the reconstructed state object.

**Mapping rule:** For each artifact returned by the filter, confirm type, version, status, and `pending-clarifications`. Mark as `Covered` or `Partially Covered` (draft) in the Gap Assessment.

**Do not** enumerate or walk directory trees. Artifact location within `work-repositories/` is an implementation detail managed by `ArtifactReadWriterPort`; agents interact exclusively through `list_artifacts`, `read_artifact`, and `list_connections`.

### Layer 2 — Enterprise Repository

Accessed through the same tool interface as Layer 1. The `ModelRegistry` indexes both engagement and enterprise entities; filter by `engagement="enterprise"` to scope queries to the enterprise repository.

**Step 2.1 — Standards and approved patterns (mandatory for Phase D; recommended for all phases):**
`list_artifacts(engagement="enterprise", artifact_type=["standard","pattern"], status="approved")` → returns SIB entries and reference patterns without loading bodies. For each result relevant to the current technology domain: `read_artifact(id, mode="summary")`. Any technology selection that contradicts a mandatory SIB entry must produce a principle-override ADR.

**Step 2.2 — Existing landscape architectures (recommended for Phase B and C):**
`list_artifacts(engagement="enterprise", artifact_type=["capability-architecture","segment-architecture"], domain=<relevant_domain>)` → an existing capability architecture may satisfy entire Phase B sections without fresh production. Read summaries of relevant results; escalate to full only if partial coverage is found.

**Step 2.3 — Enterprise requirements and constraints:**
`list_artifacts(engagement="enterprise", artifact_type=["requirement","constraint","principle"])` → filters to enterprise-level REQ, CST, PRI entities. Read summaries.

**Step 2.4 — Search enterprise content by concept (when filter is insufficient):**
`search_artifacts(query="<concept>", engagement="enterprise")` — queries the enterprise ModelRegistry FTS5/semantic index. Use when the relevant enterprise content may be in an artifact type that is hard to predict in advance (e.g. a cross-cutting principle buried in a landscape architecture document, or a reusable pattern filed under an unexpected domain). Review snippets, then `read_artifact(id, mode="summary")` for selected results.

**Step 2.5 — Lessons learned:**
`query_learnings(phase=<current_phase>, artifact_type=<primary_output>, domain=<engagement_domain>, expand_related=True)` — covered by Step 0.L; do not re-execute here.

**Do not** enumerate `enterprise-repository/` directories directly. Path layout is an implementation detail; queries go through `list_artifacts`, `search_artifacts`, and `read_artifact`.

### Layer 3 — External Sources (Situative Only)

**Governing principle:** Layers 1, 2, and 4 cover repositories that are structured, versioned, and controlled by this system — they are always queried on every skill invocation via the `list_artifacts`, `search_artifacts`, and `query_events` tool interfaces (filtered and ranked; never full directory walks). Layer 3 covers external information systems (Confluence wikis, Jira projects, read-only reference repositories) that are *not* under this system's control, are unstructured from the perspective of the architecture model, and may contain large volumes of content with no guaranteed relevance to the current task. These are **not proactively queried** on every skill invocation.

Layer 3 is executed **only in the following situative conditions**:

**Condition A — Reverse architecture entry (EP-G / EP-H) or reverse-architecture skills (SA-REV-*, SWA-REV-*).**
These skills explicitly reconstruct the architecture model from all available evidence. External sources are a primary evidence tier. Execute a full Layer 3 scan.

**Condition B — User-referenced source in a CQ answer or upload.**
When a user answers a CQ and cites an external source (e.g. a Jira issue key, a Confluence page URL, a specific file path in a read-only git repository), the agent resolves only that specific reference using the relevant source adapter. This is not a broad scan — it is targeted retrieval of the cited item and its immediate context (parent epic, linked pages, etc.).

**Condition C — PM explicit instruction.**
The Project Manager skill may instruct an agent to query a specific external source when its Phase A or Phase B discovery output is known to be thin and a configured source is documented as the authoritative reference for that domain. This must be an explicit instruction, not a default.

**For all other skill invocations: skip Layer 3 entirely.** Note in the Gap Assessment: "Layer 3 skipped — not a reverse-architecture context and no user source reference received."

---

**When Layer 3 is executed (Conditions A or C), the procedure is:**

1. List all files in `external-sources/` whose `engagement-scope` includes this engagement.
2. For each configured source with status `active`, issue phase-appropriate queries:

| Phase / Context | Query Types | What to Look For |
|---|---|---|
| Reverse arch (EP-G) | all configured types | All available context: vision, capabilities, design decisions, ADRs, infra docs |
| A (Architecture Vision) | wiki, space/page | Product vision, stakeholder lists, business mandates, regulatory context |
| B (Business Architecture) | wiki, ticket, space/page | Business processes, capability descriptions, organisational charts |
| C (Application/Data) | wiki, repo-browse | Existing application designs, API specs, data dictionaries |
| D (Technology Architecture) | wiki, repo-browse | Technology decisions, infrastructure diagrams, ADRs, runbooks |
| H (Change Management) | ticket, wiki | Change requests, incident records, improvement ideas |

3. For each query, emit `source.queried` event per `framework/repository-conventions.md §10`.
4. Map retrieved content to ADM artifact sections. Mark fields derived from external sources with `[source: <source-id>]`.
5. If content conflicts with an existing baselined artifact, raise ALG-011 (inconsistent artifacts) rather than silently overwriting.

**When Layer 3 is executed for a user-referenced source (Condition B), the procedure is:**

1. Extract the source reference from the CQ answer (issue key, URL, file path, or source-id + query string).
2. Identify the matching `external-sources/<source-id>.config.yaml` by `source-type` and `base-url`.
3. Fetch only the specifically cited item and its immediate context. Do not issue a broad search.
4. Emit `source.queried` event with `{source_id, query, triggered_by: "user-cq-reference", cq_id}`.
5. Include retrieved content in the agent's answer context; annotate with `[source: <source-id> via user-reference]`.

**No-config fallback:** If no external sources are configured, Layer 3 is always skipped regardless of condition. Note in Gap Assessment.

### Layer 4 — Target Project Repository (Single or Multi-Repo)

Scan all registered target repositories. The set of registered repositories is determined by reading `engagements-config.yaml`:
- If `target-repositories` (plural list) is present: scan each entry in the list.
- If `target-repository` (singular, legacy format) is present: treat as a single-item list with `id: default`.
- Skip repos whose `url` is `null` or whose `local-clone-path` does not exist.

**This layer is mandatory for EP-G and EP-H entries.** For EP-0 through EP-D it is optional but should be performed for any repo that is accessible.

**Multi-repo procedure:**

1. **Load Repository Map** (`architecture-repository/repository-map.md`) if it exists. The Repository Map provides pre-scanned inter-repo dependency and bounded-context allocation data — if present and current, use it to skip re-scanning unchanged repos. If absent or stale, proceed with direct scanning.

2. **Call `list_target_repositories()`** to get the full registry (ids, labels, roles, domains, clone paths). This tool reads `engagements-config.yaml` and returns only repos with accessible local clones.

3. **For each accessible repository, execute the per-repo discovery steps below** (steps 4–10). Group findings by repo id.

4. **Enumerate repository structure:** List top-level directories; identify project type from directory layout, build files, and configuration. Note the `role` from the registry (microservice, microfrontend, etc.) as context for interpretation.

5. **Read project manifests:** `package.json`, `pyproject.toml`, `pom.xml`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`, `*.csproj`, etc. Extract: technology stack, direct dependencies, version constraints. Map to Technology Architecture components (TC-nnn candidates). For shared-lib and shared-schema repos, pay particular attention to exported interfaces.

6. **Read infrastructure/deployment definitions:**
   - Container: `Dockerfile`, `docker-compose.yml`
   - Kubernetes: `k8s/`, `helm/`, `kustomize/`
   - Cloud IaC: `terraform/`, `pulumi/`, `cloudformation/`
   - CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`
   Map to Deployment Topology and Environment Provisioning Catalog. For infrastructure-role repos, this is the primary content.

7. **Read architecture-level documentation:** `README.md`, `docs/`, `ADR.md` or `docs/decisions/`, `ARCHITECTURE.md`, `DESIGN.md`, `CONTRIBUTING.md`. Extract any documented architecture decisions; map to ADR candidates.

8. **Read interface definitions:** `openapi.yaml`, `swagger.json`, `*.proto`, `graphql/**/*.graphql`, `schemas/`. Map to Interface Catalog (IFC-nnn candidates) and Data Entity Catalog (DE-nnn candidates). For multi-repo engagements, cross-reference interface definitions across repos to identify integration contracts.

9. **Read test structure:** `test/`, `tests/`, `spec/`, `__tests__/`. Infer coverage targets and test strategy from structure and any CI configuration.

10. **Mark all inferences** with `[inferred: target-repo:<repo-id> scan]` (e.g., `[inferred: target-repo:order-service scan]`). For single-repo engagements with `id: default`, use `[inferred: target-repo scan]` for backward compatibility.

**Cross-repo synthesis (multi-repo only):** After scanning all repos, identify:
- **Shared dependencies:** same library at different versions (flag as TC divergence risk)
- **Undocumented integration contracts:** one repo calls an endpoint that another repo serves, but no contract doc exists — raise CQ for contract formalisation
- **Circular dependencies:** repo A depends on B, B depends on A — raise ALG-011

**Agent scope limits:** Agents may read all registered target repos per discovery. Write access is per-repo per `engagements-config.yaml` access table. All writes use `write_target_repo(repo_id=<id>, ...)` — the `repo_id` parameter is mandatory in multi-repo engagements to prevent accidental writes to the wrong repo.

### Layer 5 — EventStore State

The current `WorkflowState` is injected into each agent invocation via `deps.workflow_state` — no direct EventStore call is needed. This layer is a check against that already-available state.

Check `deps.workflow_state` for:
- `current_phase` — confirms the active ADM phase
- `phase_visit_counts` — how many times each phase has been visited; `> 1` means revisit mode
- `gate_outcomes` — which gates have passed; phases with a `passed` gate are effectively complete
- `baselined_artifacts` — `{artifact_id: version}` map of all baselined artifacts; do not re-produce any artifact listed here unless in revisit scope
- `open_cqs` — CQs already raised; avoid duplicating
- `last_algedonic` — active algedonic signal if any; constrains current work scope

To retrieve event payloads (CQ answer text, handoff content) not captured in the state object, use the `query_event_store` tool:

```
query_event_store(event_types=["cq.answered", "handoff.created"], phase=<current_phase>)
```

**Key rule:** If `baselined_artifacts` shows an artifact, do not re-produce it. Consume it via `read_artifact(artifact_id, mode="summary")`. If the version is older than required, raise a handoff event requesting the latest version.

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
- `[inferred: target-repo scan]` — inferred from codebase (single-repo; use `[inferred: target-repo:<id> scan]` in multi-repo engagements)
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
| `learning-protocol.md` | Full learning lifecycle: generation triggers, entry format, retrieval (Step 0.L), synthesis, enterprise promotion |

---

## 8. Diagram Catalog Lookup (Step 0.D)

**Applies to:** Any skill that produces or updates a diagram artifact.

For skills producing diagram artifacts, the standard Discovery Scan (§2) must include an additional sub-step inserted **after** the five-layer scan and **before** CQ assessment:

### Step 0.D — Diagram Catalog Lookup

Under ERP v2.0 there are no separate `elements/<layer>/` YAML catalog files. The ModelRegistry (populated from entity file frontmatter) IS the catalog. Use the following procedure:

> 1. **Identify diagram scope from the skill step brief.** The specific skill step that triggers diagram production names the diagram type and purpose (e.g. "ArchiMate Business Architecture Overview", "ER data model", "Application Cooperation Viewpoint"). Use that description — not a generic heuristic — to determine which entity types and layers are in scope.
>
>    **ArchiMate diagrams span multiple layers.** A Motivation diagram includes `stakeholder`, `driver`, `goal`, `requirement`, `constraint`, `principle`. A Business Architecture Overview includes `capability`, `value-stream`, `business-actor`, `business-role`, `business-process`, `business-function`, `business-service`, `business-object`. An Application Cooperation Viewpoint includes `application-component`, `application-interface`, `application-service`, `application-function` — and often `business-service` and `data-object` at the adjacent layers. A Technology Viewpoint includes `technology-node`, `system-software`, `technology-service`, `artifact`. An integrated Architecture Overview can include entities from every layer simultaneously.
>
>    When the entity types are not fully determinable from the skill brief, use `search_artifacts` for concept-based discovery before falling back to `list_artifacts` by type:
>    ```
>    search_artifacts(query="<natural language description of the diagram subject>")
>    ```
>    This surfaces relevant entities regardless of type by querying the FTS5/semantic index.
>
> 2. **Query ModelRegistry for each entity type in scope:**
>    ```
>    list_artifacts(artifact_type="<type>", domain="<domain>", status=["draft","baselined"])
>    ```
>    Repeat per entity type. Review `§display ###<language>` coverage via `read_artifact(id, mode="summary")` to confirm each candidate belongs in this diagram.
>
> 3. **Query relevant connections:**
>    ```
>    list_connections(artifact_type="archimate-realization", target="<id>")
>    list_connections(artifact_type="er-one-to-many", source="<id>")
>    ```
>    Use the `source` and `target` filter parameters to scope to entities found in step 2. For ArchiMate diagrams, query all connection types that join the selected entity pairs.
>
> 4. **Annotate working context:** "Diagram scope: N entities found; IDs: [list]. Connections: M found."
>
> 5. **When the diagram authoring step is reached,** execute the full **D1–D5 protocol** per `framework/diagram-conventions.md §5`:
>    - D1 — query model entities and connections (as above)
>    - D2 — verify `§display ###<language>` coverage; add missing subsections via `write_artifact`
>    - D3 — author PUML from template (`read_framework_doc("framework/diagram-conventions.md §7.<type>")`), write via `write_artifact`, update `diagrams/index.yaml`
>    - D4 — `validate_diagram(<puml-path>)`: fix errors; re-validate before proceeding
>    - D5 — `render_diagram(<puml-path>)` at sprint boundary

**Catalog bootstrap (Phase A):** SA creates the `diagram-catalog/` directory structure and runs `regenerate_macros()`. There is no entity import step — enterprise entities are already visible via the unified ModelRegistry. No diagram work begins until bootstrap is complete.

**Write authority:** SA is the sole writer to all files under `architecture-repository/diagram-catalog/`. Non-SA agents that need a `§display ###<language>` subsection added to an entity emit a `diagram.display-spec-request` handoff to SA rather than writing it directly. Exception: SwA produces Phase C diagrams (archimate-application, ER) by submitting `.puml` files to SA via handoff; SA integrates them into `diagram-catalog/diagrams/` at phase-gate close. SwA writes diagrams directly to `technology-repository/diagram-catalog/` (their owned repository).

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

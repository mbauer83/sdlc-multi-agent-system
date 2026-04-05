---
skill-id: SA-REV-PRELIM-A
agent: SA
name: reverse-architecture-bprelim-a
display-name: Reverse Architecture — Prelim/Phase A (Motivation & Strategy Discovery)
invoke-when: >
  EP-G engagement entry and no Architecture Vision or motivation/strategy entities exist; or
  EP-H escalates to EP-G and Prelim/Phase A artifacts are absent; or
  PM emits entry-point.assessed (entry_point=EP-G) and SA warm-start is required.
trigger-phases: [Prelim, A]
trigger-conditions:
  - entry-point.assessed (entry_point=EP-G)
  - engagement.ep-g.started
  - handoff.created (from PM, handoff_type=ep-g-warm-start-sa)
entry-points: [EP-G, EP-H]
primary-outputs:
  - Motivation entity files (STK, DRV, ASS, GOL, PRI, REQ, CST)
  - Strategy entity files (CAP, VS, RES)
  - Architecture connection files (archimate/influence, archimate/association)
  - Architecture Vision overview document
complexity-class: complex
version: 1.0.0
---

# Skill: Reverse Architecture — Prelim/Phase A (Motivation & Strategy Discovery)

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** Prelim / A — Motivation & Strategy  
**Skill Type:** Warm-start — reverse architecture discovery  
**Framework References:** `sdlc-entry-points.md §4.6`, `framework/artifact-registry-design.md`, `framework/artifact-schemas/entity-conventions.md`, `agile-adm-cadence.md §6.2`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Runtime Tooling Hint

This skill expresses tool-use intent; concrete tool signatures are runtime-bound by orchestration code.

- `invoke-when` and `trigger-conditions` are intent-level hints; executable phase/state gating is enforced by orchestration code.
- Keep procedure and outputs strict; if invoked in an unexpected state, fail via pre-condition checks and route through CQ/algedonic paths.

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| EP-G handoff from PM | PM | `handoff.created (handoff_type=ep-g-warm-start-sa)` | Signals SA to begin warm-start; may include references to target repos or user-provided docs |
| User-provided documents, diagrams, textual descriptions | User (via PM CQ loop) | Any state — SA queries user in Step 1 | May include design docs, architecture diagrams, product specs, presentations, READMEs |
| Target repository (codebase, README, configs) | `scan_target_repo()` | At least one registered target repo clone available | README, package manifests, high-level documentation; absence triggers CQ |
| External source artifacts (Confluence, SharePoint, etc.) | Configured external source adapters | Optional — used if available | Queried via `read_framework_doc` / external source adapter calls |
| Enterprise repository motivation entities | `list_artifacts()` on `enterprise-repository/motivation/` | Optional — read for reuse | STK, CAP, PRI from enterprise baseline may apply |

**Hard prerequisites:** None (this skill is triggered precisely because forward-path artifacts do not exist). SA proceeds with whatever is available and raises CQs for unresolvable gaps.

---

## Knowledge Adequacy Check

### Required Knowledge

- **Business domain identity:** What does this system or product do? Who uses it? What problem does it solve?
- **Organisational context:** What organisation sponsors this? What are its goals and constraints?
- **Stakeholder universe:** Who are the key stakeholders — business, technical, regulatory?
- **Drivers and goals:** What business drivers and goals motivate the system? (Can be inferred from codebase README, docs, or user description if not stated explicitly.)
- **Regulatory and safety context:** Is this system safety-relevant or regulated? (Determines whether ALG-REV-001 applies.)
- **Capability scope:** What high-level capabilities does this system provide or depend on?

### Known Unknowns

| Unknown | Blocking | CQ Target | Entity Section Affected |
|---|---|---|---|
| Business domain / product purpose | Yes — without this SA cannot produce any entities | User (via PM) | All motivation entities |
| Named stakeholders beyond technical actors | No — SA can infer a minimal set from commit history and package authors | User | STK-nnn entities |
| Business goals vs. technical goals | Partially — SA infers from problem description; may conflate | User or PO | GOL-nnn, DRV-nnn |
| Regulatory / compliance obligations | Yes for safety classification; no for other entities | User + CSCO | CST-nnn, ASS-nnn |
| Capability ownership (which capability belongs to which business unit) | No — SA makes reasoned assignment; documents as assumption | — | CAP-nnn |
| Strategic intent (why this system exists strategically) | No — SA infers from docs; flags as `[inferred]` | User | DRV-nnn, VS-nnn |

### Clarification Triggers

SA raises a CQ (`cq.raised` + CQ record) when:

1. **Business domain unidentifiable:** Codebase, README, and all user-provided sources cannot establish even a minimal description of what the system does. Blocking for all entities.
2. **Safety classification unknown:** The system appears to involve physical actuation, financial transactions, health data, or infrastructure control but the user has not stated a safety classification. Blocking for CST-nnn entries; non-blocking for others. CSCO is notified concurrently.
3. **No stakeholders identifiable:** Neither commit history, docs, nor user description identifies any business-side stakeholder. Non-blocking — SA creates placeholder `STK-001: Engagement Sponsor (unknown)`.
4. **Conflict between discovered goals:** Two source documents assert incompatible system goals (e.g., one says "reduce cost", another says "increase coverage at any cost"). SA raises a bounded CQ: "Which goal takes precedence: [A] or [B]?"
5. **Unknown regulatory jurisdiction:** System domain (health, finance, transport, critical infrastructure) identified but jurisdiction unknown. Blocking for CST-nnn. Concurrent CSCO notification.

---

## Procedure

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="SA", phase="A", artifact_type="architecture-vision")` and `query_learnings(agent="SA", phase="Prelim", artifact_type="motivation-entity")`. Prepend any returned corrections to working context. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Discovery Scan

Execute the five-layer Discovery Scan per `framework/discovery-protocol.md §2` before authoring any entity. Record all findings with source annotations.

**Layer 0.S — Standards scan** (mandatory per §9): Read `technology-repository/coding-standards/` and `enterprise-repository/standards/`. Flag as COD-GAP-001 if absent.

**Layer 1 — Engagement state:** Call `list_artifacts(directory="architecture-repository/")` via ModelRegistry. If any STK/DRV/GOL/PRI/REQ/CST/CAP/VS entities exist at version ≥ 0.1.0 → the engagement has prior warm-start artifacts. Load them and note their status. If all are absent → fresh warm-start.

**Layer 2 — Enterprise repository:** Call `list_artifacts(directory="enterprise-repository/motivation/")` and `list_artifacts(directory="enterprise-repository/strategy/")`. Note any enterprise-level STK, CAP, PRI that apply to this engagement's domain — they may be referenced in connection files without being duplicated.

**Layer 3 — External sources:** For each configured external source adapter, query: "stakeholders", "business goals", "architecture principles", "capability map", "product vision". Record results with `[source: <adapter-id>]` annotations.

**Layer 4 — Target repository scan:** Call `scan_target_repo()` (or `scan_target_repo(repo_id)` for each registered repo). Extract:
- Root README and any `docs/` directory markdown files
- Package manifests (package.json, pyproject.toml, pom.xml, Cargo.toml, go.mod) — extract `name`, `description`, `authors`, `keywords`
- Any ADRs in `docs/adr/`, `adr/`, `architecture/`
- Any `CONTRIBUTING.md`, `ARCHITECTURE.md`, `DESIGN.md`, or similar
- `.github/CODEOWNERS` for stakeholder inference
Annotate every extraction with `[inferred: target-repo:<repo-id>]`.

**Layer 5 — EventStore:** Query for any prior `cq.answered` events at phases Prelim or A; any prior `artifact.baselined` events. If found, extract resolved answers as known facts.

**Gap assessment:** List every entity type for which zero evidence was found. These become the candidate CQs in Step 3 (raise only if critical and not derivable from Step 1 answers).

---

### Step 1 — User Context Query

After the discovery scan, SA determines what it cannot infer. Compose a **single batched context request** to the user (routed via PM per `clarification-protocol.md §2`). The request must:

1. State what has already been found (briefly) so the user understands the SA's starting knowledge.
2. List specific unknowns as structured questions — not open-ended. Maximum 7 questions in a single batch. Examples:
   - "What is the primary business domain of this system? (e.g. e-commerce, logistics, healthcare, DevOps tooling)"
   - "Who are the key stakeholders? Please list named individuals or role titles."
   - "What are the top 3 business goals this system is intended to achieve?"
   - "Is this system safety-critical, safety-relevant, or safety-neutral per your assessment?"
   - "Are there any architecture principles or constraints that governed the original design?"
   - "Please share any existing design documents, diagrams (architecture, sequence, deployment), or product specifications."
   - "Which documents or URLs should I read for context? (e.g. Confluence spaces, internal wikis, Google Docs)"

Emit `cq.raised` for the batched request. Pause entity production until user response is received or PM approves proceeding on current evidence (max 48-hour wait per `clarification-protocol.md §5`).

After receiving user response: integrate answers, external doc contents (retrieve via adapter if URL provided), and any referenced diagram images into working context. Annotate each piece of information with its source.

---

### Step 2 — Entity Inference and Draft Building

From all collected evidence (discovery scan + user response + referenced documents + diagram analysis), build a draft entity catalogue. For each entity:
- Assign a provisional artifact-id (`STK-001`, `DRV-001`, etc.) using sequential numbering starting from the highest existing ID + 1 (or from 001 if none exist).
- Classify the entity type (from `framework/artifact-registry-design.md §4`).
- Draft the `§content` section fields.
- Annotate every field that was inferred (not stated explicitly): append `[inferred: <source>]` where source is one of `target-repo:<id>`, `external-source:<id>`, `user-response`, `user-doc:<title>`, `commit-history`, `assumption`.
- Mark every field that is unknown with `[UNKNOWN — CQ pending]`.

**Minimum entity set for a viable warm-start Architecture Vision:**

| Layer | Min count | Entity types |
|---|---|---|
| Motivation / Stakeholders | 2 | STK (at least 1 business, 1 technical) |
| Motivation / Drivers | 2 | DRV |
| Motivation / Goals | 1 | GOL |
| Motivation / Requirements | 3 | REQ |
| Motivation / Principles | 2 | PRI |
| Strategy / Capabilities | 3 | CAP |
| Strategy / Value Streams | 1 | VS |

If the minimum cannot be met from available evidence, raise blocking CQs before proceeding.

---

### Step 3 — User Confirmation Loop

Present the inferred entity catalogue to the user for validation **before writing any files**. The presentation must:

1. List each proposed entity: `[artifact-id] [entity-type] — [name] — source: [annotation]`
2. Explicitly mark all `[inferred]` and `[UNKNOWN]` fields.
3. Ask the user to: (a) confirm, (b) correct any misidentified entities, (c) add any missing entities, (d) indicate which `[UNKNOWN]` fields they can fill in.

**Iteration 1:** User reviews and responds. SA incorporates all corrections and additions.  
**Iteration 2:** If corrections were structural (entity type changed, entity deleted, significant name change), present the revised set for final confirmation. If only minor additions, skip iteration 2.  
**Max iterations:** 2. After iteration 2, SA proceeds with remaining `[UNKNOWN]` items flagged as open CQs and `[inferred]` items retained as documented assumptions.

---

### Step 4 — Write Entity Files

For each confirmed entity, call `write_artifact` to create the entity file at the correct ERP path:

| Entity type | Path |
|---|---|
| STK | `architecture-repository/motivation/stakeholders/<id>.md` |
| DRV | `architecture-repository/motivation/drivers/<id>.md` |
| ASS | `architecture-repository/motivation/assessments/<id>.md` |
| GOL | `architecture-repository/motivation/goals/<id>.md` |
| OUT | `architecture-repository/motivation/outcomes/<id>.md` |
| PRI | `architecture-repository/motivation/principles/<id>.md` |
| REQ | `architecture-repository/motivation/requirements/<id>.md` |
| CST | `architecture-repository/motivation/constraints/<id>.md` |
| MEA | `architecture-repository/motivation/meanings/<id>.md` |
| CAP | `architecture-repository/strategy/capabilities/<id>.md` |
| VS | `architecture-repository/strategy/value-streams/<id>.md` |
| RES | `architecture-repository/strategy/resources/<id>.md` |
| COA | `architecture-repository/strategy/courses-of-action/<id>.md` |

Entity file structure per `framework/artifact-schemas/entity-conventions.md §1`:
- **Frontmatter:** `artifact-id`, `artifact-type`, `name`, `version: 0.1.0`, `status: draft`, `phase-produced: A`, `owner-agent: SA`, `domain`, `safety-relevant`, `produced-by-skill: SA-REV-PRELIM-A`, `last-updated`, `engagement`
- **`§content`:** Type-specific properties table + narrative description. Include `reconstruction: true` note and any `[inferred]` / `[UNKNOWN]` annotations.
- **`§display ###archimate`:** ArchiMate rendering spec (alias = artifact-id; label = name; stereotype = ArchiMate element type). Add this subsection only for entity types that appear in ArchiMate diagrams (motivation and strategy elements).

After all entity files are written, call `regenerate_macros(repo_path="architecture-repository/")` to sync `_macros.puml`.

---

### Step 5 — Write Connection Files

Infer relationships from the entity set and write connection files per `framework/artifact-schemas/entity-conventions.md §2.2`:

**Motivation connections (archimate):**
- `influence/`: DRV-nnn → GOL-nnn (driver influences goal)
- `influence/`: DRV-nnn → REQ-nnn (driver influences requirement)
- `association/`: STK-nnn → GOL-nnn (stakeholder associated with goal)
- `association/`: STK-nnn → REQ-nnn (stakeholder associated with requirement)
- `realization/`: REQ-nnn → CAP-nnn (requirement realized by capability)
- `aggregation/` or `composition/`: CAP-nnn → CAP-nnn (capability hierarchy)
- `realization/`: CAP-nnn → VS-nnn (capability realized by value stream step)

Write each connection to `architecture-repository/connections/archimate/<type>/<source>---<target>.md`.  
Connection frontmatter: `artifact-id`, `artifact-type: archimate-<type>`, `source`, `target`, `version: 0.1.0`, `status: draft`, `phase-produced: A`, `owner-agent: SA`, `safety-relevant: false`, `produced-by-skill: SA-REV-PRELIM-A`, `last-updated`, `engagement`.

Only write connections for which both source and target entity files exist in the registry. Do not create placeholder connections referencing non-existent entities.

---

### Step 6 — Produce Architecture Vision Overview Document

Author `architecture-repository/overview/architecture-vision.md` as a **repository-content artifact** (no `§display` section). This document summarises the warm-start model and is readable by all agents:

Sections:
1. **Engagement Context** — domain, sponsoring organisation, entry point (EP-G), reconstruction status
2. **Scope Statement** — in-scope systems/repos, out-of-scope
3. **Stakeholder Summary** — reference STK-nnn IDs; do not duplicate content from entity files
4. **Business Drivers and Goals** — reference DRV-nnn and GOL-nnn IDs
5. **High-Level Capability Map** — reference CAP-nnn IDs with one-line descriptions
6. **Architecture Principles** — reference PRI-nnn IDs
7. **Safety Classification** — Safety-Neutral / Safety-Relevant / Safety-Critical with CST-nnn references
8. **Assumptions and Open CQs** — list all `[inferred]` fields retained as assumptions; list all open CQ-IDs
9. **Reconstruction Confidence** — overall assessment: HIGH (≥80% of fields sourced from explicit docs/user input), MEDIUM (50–79%), LOW (<50% — recommend Phase A sprint to validate)

Frontmatter: `artifact-type: architecture-vision`, `version: 0.1.0`, `status: draft`, `reconstruction: true`, `entry-point: EP-G`, `produced-by-skill: SA-REV-PRELIM-A`.

Emit `artifact.baselined` at version 0.1.0 for the overview document.

---

### Step 7 — Raise CQs for Remaining Gaps

For each `[UNKNOWN]` field remaining after the confirmation loop:
1. Classify as blocking or non-blocking for downstream skills (SA-REV-BA, SwA-REV-TA).
2. Raise a formal CQ per `clarification-protocol.md §3` with `blocking` and `blocks_task` fields set.
3. Emit `cq.raised` for each CQ.

Batch all remaining CQs into a single CQ batch via PM.

---

### Step 8 — Handoffs

1. **Handoff to CSCO** (if any `safety-relevant: true` entities or CST-nnn entities were created): `handoff-type: ep-g-safety-retrospective-input`. Payload: list of safety-relevant entity IDs and the reconstruction confidence level.
2. **Handoff to PM**: `handoff-type: ep-g-sa-prelim-a-complete`. Payload: entity count by type, open CQ count, reconstruction confidence level. PM uses this to decide whether to trigger SA-REV-BA immediately or await CQ resolution.
3. Emit `artifact.baselined` for the Architecture Vision overview document.

---

## Feedback Loop

### User Confirmation Loop (Entity Catalogue Accuracy)

- **Iteration 1:** SA presents inferred entity catalogue (Step 3). User reviews and provides corrections.
- **Iteration 2:** SA presents revised catalogue if structural changes were required. User gives final confirmation.
- **Max iterations:** 2. On second rejection without clear resolution path, SA proceeds with available entities marked as low-confidence assumptions.
- **Escalation:** If user provides contradictory corrections in iteration 2 (e.g., entity described differently in two parts of the response), raise `ALG-010` to PM for adjudication. Do not write entity files for the contested entity.

### CSCO Safety Classification Loop

- **Iteration 1:** SA sends safety-relevant entity list to CSCO. CSCO reviews and may reclassify entities or flag additional safety-relevant elements.
- **Iteration 2:** SA updates CST-nnn entities and safety flags. CSCO confirms.
- **Max iterations:** 2. If unresolved, raise `ALG-REV-001` (safety classification unknown before further reconstruction).
- **Escalation:** Halt further reverse architecture reconstruction until safety classification is resolved.

### Personality-Aware Conflict Engagement

SA is an **Integrator** (VSM System 4). In this skill, primary tension is with the **User** who may resist having their system's intents formalised or may provide incomplete/contradictory information. SA's stance: persistent, patient, specific — never accept vague answers without at least one follow-up clarification. Do not invent entities to fill gaps; document unknowns explicitly. If the user resists the structured approach: acknowledge the overhead, explain that entity files are what enables the downstream agents to work without re-asking the same questions, and reduce the ask to the minimum viable set (Reconstruction Confidence LOW is acceptable).

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | User correction in iteration 1 was structural (entity type wrong, entity misidentified) | S2 |
| `algedonic` | ALG-REV-001 or any ALG raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised for info that was present in a source the SA failed to read | S2 |
| `confidence-mismatch` | Reconstruction Confidence assessed as HIGH but downstream skill found significant gaps | S2 |

On trigger: call `record_learning()` with `artifact-type="motivation-entity"`, error-type per `framework/learning-protocol.md §4`, correction ≤3 sentences. Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-REV-001 | Safety classification cannot be determined from any source and user declines to answer the safety CQ | S1 | Halt reconstruction; emit `alg.raised`; escalate to CSCO immediately; do not write safety-relevant entities until resolved |
| ALG-001 | Discovered document contains an explicit statement that the system violates a known regulatory requirement (e.g., GDPR data residency, HIPAA PHI controls) | S1 | Emit `alg.raised`; escalate to CSCO and PM; halt entity writing for the affected domain |
| ALG-010 | User confirmation loop exhausted (2 iterations) with unresolved entity definition conflict | S3 | Emit `alg.raised`; PM adjudicates; retain contested entity as `[UNKNOWN]` |
| ALG-C03 | `write_artifact` call fails with "no backing entity in ModelRegistry" for a connection's source or target | S2 | Emit `alg.raised`; do not write the connection; raise CQ for the missing entity |

---

## Outputs

| Output | Path | Version | EventStore Event |
|---|---|---|---|
| Motivation entity files (STK, DRV, ASS, GOL, OUT, PRI, REQ, CST, MEA) | `architecture-repository/motivation/<type>/<id>.md` | 0.1.0 (draft) | `artifact.created` per entity |
| Strategy entity files (CAP, VS, RES, COA) | `architecture-repository/strategy/<type>/<id>.md` | 0.1.0 (draft) | `artifact.created` per entity |
| ArchiMate connection files | `architecture-repository/connections/archimate/<type>/<source>---<target>.md` | 0.1.0 | `artifact.created` per connection |
| Architecture Vision overview | `architecture-repository/overview/architecture-vision.md` | 0.1.0 | `artifact.baselined` |
| `_macros.puml` (regenerated) | `architecture-repository/diagram-catalog/_macros.puml` | — | — |
| Handoff to CSCO (safety retrospective input) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PM (Prelim/A reconstruction complete) | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| CQ records for remaining gaps | `engagements/<id>/clarification-log/` | — | `cq.raised` per CQ |

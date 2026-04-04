# SDLC Entry Points

**Version:** 1.0.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager  
**Last Updated:** 2026-04-02

---

## 1. Purpose

This document specifies how the multi-agent system is engaged when work does not start from the Preliminary Phase. Every realistic engagement begins with *some* existing context — a product idea, an existing architecture, a codebase under governance review, or a specific change request. The system must assess this context, map it to the ADM phase structure, identify what already exists, validate or ingest it, and begin phase work from the appropriate point without re-doing work that has already been done elsewhere.

Entry point assessment is the responsibility of the **Project Manager** with mandatory input from the **Solution Architect** (for architecture-domain context) and the **CSCO** (for safety and compliance context). It is performed once per engagement before any agent begins phase work.

---

## 2. Entry Point Classification

### 2.1 The Seven Entry Points

| Entry ID | Name | User Provides | ADM Start Phase | Primary Assessment Agent |
|---|---|---|---|---|
| `EP-0` | Cold Start | An idea, mandate, or problem statement | Preliminary | PM + SA |
| `EP-A` | Vision Entry | A product vision, concept document, or pitch deck | Phase A (Architecture Vision) | SA + PO |
| `EP-B` | Requirements Entry | Business requirements, process models, or a business case | Phase B or Phase C | SA |
| `EP-C` | Design Entry | A system design, application architecture, or data model | Phase C or Phase D | SA + SwA |
| `EP-D` | Technology Entry | An existing technology stack, infrastructure design, or ADRs | Phase D or Phase E | SwA |
| `EP-G` | Implementation Entry | An existing codebase, deployed system, or set of PRs | Phase G (governance of existing work) | SwA + QA |
| `EP-H` | Change Entry | A specific change request, incident, or improvement need | Phase H | SA + CSCO |

### 2.2 Entry Point Selection Procedure

The PM determines the correct entry point by asking:

1. **What artefacts does the user already have?** — Maps to entry point.
2. **Are those artefacts schema-conformant?** — Can they be ingested directly, or must they be reconstructed?
3. **What ADM phases are effectively "already done" by the user's existing work?** — These phases are marked as `externally-completed`; their artifacts are ingested and validated but not re-executed.
4. **What phases are genuinely missing or incomplete?** — These become the actual work scope.

The entry point assessment produces an **Engagement Profile** (§3) that governs all subsequent work.

---

## 3. Engagement Profile

The Engagement Profile is produced at engagement start and stored at `engagements/<id>/engagement-profile.md`. It is the first document created in any engagement and lives at the engagement root — not inside any work-repository — because it describes the engagement itself rather than an artifact within the ADM process.

```markdown
---
artifact-type: engagement-profile
engagement-id: ENG-nnn
entry-point: EP-n
entry-date: YYYY-MM-DD
pm-agent: project-manager
cycle-level: capability       # strategic | segment | capability
parent-cycle-id: null

# Target project repository — the software being built, analysed, or changed.
# Framework files NEVER live inside this repository.
# See framework/architecture-repository-design.md §2.4 and §3.4
target-repository:
  url: null                   # git@github.com:org/project.git OR /local/path
  default-branch: main
  local-clone-path: target-repo/   # relative to this engagement directory; .gitignored
---

## Engagement Description
[What the user wants to achieve in this engagement — stated in their terms]

## Target Project
[Name, brief description, and technology domain of the software being worked on]

## User-Provided Inputs
| Input | Format | Content Summary | Maps to ADM Artifact |
|---|---|---|---|
| [document/description] | [text/diagram/code/etc.] | | AV / BA / AA / DA / TA / other |

## Externally-Completed Phases
| Phase | Completion Basis | Artifact Produced | Validation Status |
|---|---|---|---|
| [e.g. Preliminary] | Full / Partial / Inferred | [artifact-id or "to be reconstructed"] | Valid / Needs validation / Invalid |

## Phases In Scope (to be executed by agents)
| Phase | Entry Condition | Known Gaps (pre-emptive CQs) |
|---|---|---|
| | | |

## Pre-emptive Clarification Queries
[List of CQ-ids raised during entry point assessment, before phase work begins]

## Warm-Start Artifacts
[List of artifact-ids created during ingestion, with validation status]

## Engagement Constraints
[Any constraints the user has stated: scope limitations, technology exclusions, timelines, etc.]
```

---

## 4. Entry Point Procedures

### 4.1 EP-0: Cold Start

The user provides an idea, problem statement, mandate, or brief description.

**Procedure:**
1. PM opens the engagement; creates the Engagement Profile with `entry-point: EP-0`.
2. SA and PO conduct a **Scoping Interview** — a structured set of CQs covering: business domain, problem statement, stakeholder universe, regulatory environment, safety relevance, technology constraints, scope.
3. The Scoping Interview CQs are raised as a batch in `engagements/<id>/clarification-log/` before any sprint begins.
4. Once answered, PM plans the Preliminary Phase sprint.
5. All standard ADM phases execute in order.

**Scoping Interview CQ topics (minimum):**
- What problem is being solved and for whom?
- What does success look like in concrete terms?
- Are there existing systems that must be integrated with or replaced?
- What is the regulatory or compliance environment?
- Are there safety-relevant components (physical harm, data loss, financial loss, etc.)?
- Are there technology constraints (mandated platforms, prohibited technologies)?
- Who are the key stakeholders and decision-makers?

---

### 4.2 EP-A: Vision Entry

The user provides a product vision, concept document, pitch deck, or equivalent.

**Procedure:**
1. PM creates the Engagement Profile; marks Preliminary as `externally-completed` (partially).
2. SA **reads the user's document** and produces a **Warm-Start Architecture Vision** (`AV-000`):
   - Uses the user's document as the source for §3.2 (Engagement Context), §3.4 (Business Drivers), §3.5 (Capability Overview), and §3.9 (Architecture Vision Statement)
   - Marks every field derived from the user's document with `[source: user-input]`
   - Marks every field that cannot be derived with `[UNKNOWN — CQ required]`
3. SA raises CQs for all `[UNKNOWN]` fields before attempting to baseline the AV.
4. CSCO performs an initial safety scan of the user's document; raises safety-domain CQs if hazard categories are not evident.
5. Once sufficient CQs are answered, the AV is completed and moved toward Phase A gate.

**Warm-start note:** The Warm-Start AV is at version 0.1.0. It becomes 1.0.0 only after all mandatory fields are populated and the Phase A gate passes.

---

### 4.3 EP-B: Requirements Entry

The user provides business requirements, process models, a business case, or a requirements specification.

**Procedure:**
1. PM creates the Engagement Profile; marks Preliminary and Phase A as `externally-completed` (partially or fully).
2. PO **reads the user's requirements document** and creates a Warm-Start Requirements Register (`RR-000`) mapping all user requirements to `RR-nnn` entries.
3. SA **reads the requirements document** and:
   - Attempts to produce a Warm-Start Architecture Vision from the requirements
   - Identifies gaps (missing stakeholder mapping, no safety analysis, missing capability model)
   - Raises CQs for all gaps
4. If the user's document is sufficiently rich, Phase A may be treated as `externally-completed`; otherwise Phase A runs with warm-start inputs.
5. Phase B proceeds with the Warm-Start RR as input.

**Gap assessment:** SA produces a **Gap Assessment Matrix** listing every section of `architecture-vision.schema.md` and `business-architecture.schema.md` and marking each as: Covered / Partially covered / Missing.

---

### 4.4 EP-C: Design Entry

The user provides a system design, application architecture, or data model.

**Procedure:**
1. PM marks Preliminary, Phase A, and Phase B as `externally-completed` (possibly partially).
2. **SwA** reads the user's design documents and produces Warm-Start Application Architecture (`AA-000`) and/or Data Architecture (`DA-000`) in `architecture-repository/model-entities/application/`:
   - Maps user's components to `APP-nnn` identifiers
   - Maps user's data entities to `DOB-nnn` identifiers
   - Fills in the schemas as completely as possible from user's documents
   - Marks all gaps with `[UNKNOWN — CQ required]`
3. **SA** produces a Warm-Start Business Architecture (`BA-000`) if the user has provided process/capability context; otherwise raises a CQ for missing business context. SA also performs a traceability review of SwA's AA-000 against BA-000 (consulting — same as normal Phase C flow).
4. SA raises CQs for missing business context; SwA raises CQs for missing application/data design context.
5. CSCO reviews the design for safety-relevant components; raises safety CQs.

**Reverse tracing:** SA verifies that every component in SwA's AA-000 is traceable to a business capability in BA-000. Components that cannot be traced are flagged as orphaned — the user must clarify.

---

### 4.5 EP-D: Technology Entry

The user provides an existing technology stack description, infrastructure design, or ADRs.

**Procedure:**
1. PM marks Preliminary through Phase C as `externally-completed` (partially).
2. SwA **reads the user's technology documentation** and produces a Warm-Start Technology Architecture (`TA-000`):
   - Maps existing technology choices to `TC-nnn` entries
   - Creates ADR entries for each technology decision found in the user's documents
   - Flags ADRs where rationale is missing as needing CQ
3. SwA produces a **Warm-Start Gap Analysis** (Phase E input) identifying what components from the AA/DA are not yet addressed by technology choices.
4. CSCO reviews for technology-level safety constraints; raises safety CQs.
5. Phase E proceeds with warm-start TA and gap analysis as inputs.

---

### 4.6 EP-G: Implementation Entry

The user provides an existing codebase, deployed system, or set of PRs.

This is the most complex entry point because the system must reconstruct architecture understanding from implementation evidence — the reverse of normal ADM flow.

**Procedure:**
1. PM marks all phases through Phase F as `externally-completed` (partially or fully — status unknown until assessment).
2. SwA performs **Reverse Architecture Reconstruction**:
   a. Reads available code, configuration, and deployment files
   b. Produces a Warm-Start Technology Architecture (`TA-000`) reflecting what exists
   c. Infers application components and data entities where possible
   d. Raises CQs for anything that cannot be inferred from the code alone
3. **SwA** validates the reconstruction against any available design documents; produces Warm-Start AA and DA in `architecture-repository/model-entities/application/`. **SA** performs a traceability review of the Warm-Start AA/DA against any available BA context.
4. CSCO performs a **Safety Retrospective Assessment**: reviews the existing implementation for violations of or gaps in safety constraints that should have been established in earlier phases.
5. QA reviews existing test coverage and produces a Warm-Start Test Strategy gap assessment.
6. PM determines the scope: is the engagement about governing existing implementation (Phase G governance), improving it (Phase H change management), or re-architecting (re-enter at Phase C or D)?
7. CQs are raised for all unresolvable ambiguities.

**Important:** EP-G frequently reveals that earlier architecture phases were never formally completed. The agents must be explicit with the user about what was found versus what was assumed, and what risk this creates.

---

### 4.7 EP-H: Change Entry

The user provides a specific change request, incident report, or improvement requirement.

**Procedure:**
1. PM creates a Warm-Start Change Record (`CR-000`) from the user's request.
2. SA and SwA assess which existing artifacts are affected.
3. If architecture artifacts exist in `engagements/<id>/work-repositories/`, they are used directly. If they do not exist, the entry point escalates to the appropriate earlier entry point (EP-C, EP-D, or EP-G) to reconstruct them before proceeding.
4. Change impact classification (per `agile-adm-cadence.md §10`) is performed.
5. CSCO assesses safety relevance.
6. Phase H procedure executes per `agile-adm-cadence.md §5.9`.

---

## 5. Warm-Start Artifact Validation

All artifacts produced during entry point assessment — whether ingested from user documents or reconstructed — must be **validated** before being used as authoritative inputs to phase work.

### 5.1 Validation Procedure

For each warm-start artifact:

1. **Schema conformance check:** SA or SwA verifies the artifact contains all required sections per the relevant schema file. Missing sections are flagged; CQs are raised.
2. **Internal consistency check:** SA verifies that the artifact does not contradict itself.
3. **Cross-artifact consistency check:** SA verifies that warm-start artifacts are mutually consistent (e.g., components in AA are all traceable to capabilities in BA).
4. **Safety review:** CSCO reviews for safety gaps, even if the user's original documents contain no safety analysis.
5. **Version assignment:** Validated warm-start artifacts are assigned version 0.x.x (draft). They become 1.0.0 only when the corresponding phase gate passes.

### 5.2 Validation Outcomes

| Outcome | Condition | Action |
|---|---|---|
| **Valid (with gaps)** | Schema-conformant but some fields populated with assumptions | Proceed with CQs open for assumption fields |
| **Partially valid** | Major schema sections missing but core structure present | Raise CQs; proceed with partial artifact; block gate until resolved |
| **Reconstruction required** | Artifact is in a format that cannot be mapped to schema | SA reconstructs using user's document as source material; produces schema-conformant draft |
| **Invalid** | Artifact contains fundamental inconsistencies | Raise CQ to user explaining the inconsistency; do not use as input until resolved |

---

## 6. Pre-emptive Clarification Query Batching

At every entry point except EP-0 (which uses the Scoping Interview), the assessment process will identify multiple knowledge gaps simultaneously. These should be batched into a single structured interaction with the user rather than raised as separate, sequential CQs.

**PM batching procedure:**
1. SA, SwA, CSCO, and PO each identify their CQs during entry assessment.
2. PM consolidates all CQs into a single **Entry Assessment Report** delivered to the user.
3. The report is structured by domain (business, application, data, technology, safety) and ordered from most to least blocking.
4. The user provides answers in a single response; PM routes answers to the relevant agents.
5. Any unanswered questions remain as open CQs per the standard protocol.

**Entry Assessment Report format:**

```markdown
# Entry Assessment Report

**Engagement:** ENG-nnn  
**Entry Point:** EP-n  
**Prepared By:** Project Manager  

## What We Found
[Summary of what was successfully ingested and what gaps exist]

## Questions by Domain

### Business Context
1. [CQ-id]: [question]

### Application / Data
2. [CQ-id]: [question]

### Technology
3. [CQ-id]: [question]

### Safety & Compliance
4. [CQ-id]: [question]

## What Proceeds Without Your Response
[Work that will continue on documented assumptions while awaiting your answers]

## What Is Blocked
[Work that is suspended pending specific answers]
```

---

## 7. Mid-Engagement Entry (Resuming Paused Work)

When work on an engagement is paused and then resumed (e.g., after a user is unavailable, or after a context switch), the PM performs a **Re-entry Assessment**:

1. Read the current sprint log and all open CQs.
2. Verify that all baselined artifacts are still at their expected versions (no external modifications).
3. Identify any external changes (user has provided new documents, the technology landscape has changed, etc.) and raise CQs or Change Records as appropriate.
4. Brief all agents via their respective sprint kickoff procedures.

---

## 8. Relationship to Other Documents

| Document | Relationship |
|---|---|
| `agile-adm-cadence.md` | Entry points determine which phases are in scope and what the starting sprint is |
| `clarification-protocol.md` | Entry assessment systematically generates CQs; all CQs follow that protocol |
| `repository-conventions.md` | Warm-start artifacts are written to canonical paths and versioned per those conventions |
| `raci-matrix.md` | RACI applies fully from the entry point forward; phases marked `externally-completed` still require PM and CSCO sign-off on validation |
| `algedonic-protocol.md` | If entry assessment reveals a safety-critical gap in an externally-completed phase, ALG-003 applies immediately |

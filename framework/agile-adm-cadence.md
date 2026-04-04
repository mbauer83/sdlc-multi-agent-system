# Agile ADM Cadence

**Version:** 2.2.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager  
**Last Updated:** 2026-04-02

---

## 1. Purpose and Scope

This document specifies the Agile Architecture Development Method (Agile ADM) cadence used by the SDLC multi-agent system. It defines the collaboration model, how sprint streams interlock, what gates control phase transitions, how building blocks evolve through the lifecycle, and the complete artifact ontology governing inter-agent work-exchange.

All agent skill files that involve phase work, sprint coordination, or artifact production are subordinate to this specification. Where a skill file's guidance conflicts with this document, this document takes precedence and the conflict must be resolved by updating the skill file.

**Note on time-boxing:** This cadence does not prescribe fixed calendar durations. All sequencing is logically ordered by artifact readiness and gate completion. In an agent-driven environment, work progresses at the pace of the agents; sprint "cadence" is defined by the completion of logical work packages, not calendar intervals. Phase gates and artifact readiness criteria (§6, §7) are the sole progression controls.

---

## 2. Engagement Entry

Before any sprint begins, the Project Manager determines the **entry point** for the engagement: whether work starts from scratch (cold start), or whether the user is bringing existing artifacts, designs, requirements, or a codebase that represents work already done outside this system. The full entry-point classification and procedures are specified in `framework/sdlc-entry-points.md`.

The entry point assessment produces an **Engagement Profile** that identifies:
- Which ADM phases are already completed (externally), and their warm-start artifacts
- Which phases are in scope for this engagement
- All pre-emptive Clarification Queries (CQs) to be resolved before phase work begins

**No Architecture Sprint or Solution Sprint may begin until the Engagement Profile is produced and all blocking pre-emptive CQs are answered or have documented assumptions.** Business Sprints may run concurrently with entry assessment to surface additional context.

---

## 3. Collaboration Model: Cross-Development Collaboration

This system follows the TOGAF **Cross-Development Collaboration** pattern, which defines three coordinating sprint streams running concurrently:

- **Business Stream** (Business Sprints) — owned by Sales/Marketing and Product Owner agents; produces market analysis, requirements, and business capability inputs
- **Architecture Stream** (ADM Sprints) — owned by Solution Architect, Software Architect/PE, and CSCO agents; produces Architecture Building Blocks (ABBs), architecture artifacts, and safety constraint overlays
- **Implementation Stream** (Solution Sprints) — owned by Implementing Developer, DevOps/Platform Engineer, and QA Engineer agents

The Project Manager spans all three streams as coordinator and gate authority.

**Adaptation for the agentic context:** The three streams are sequenced logically rather than by calendar. The Architecture Stream produces ABBs that authorise and bound the Implementation Stream. Streams may advance concurrently when their work is non-dependent — concurrency rules are specified in §4.

---

## 4. Sprint Types

### 4.1 Architecture Sprint (ADM Sprint)

An Architecture Sprint is a bounded work unit that produces one or more baselined Architecture Building Blocks and their enclosing deliverable artifacts.

**Primary owners:** Solution Architect (Phases A–B, H business layer), Software Architect/PE (Phases C–F, H application/technology layer)  
**Supporting roles:** Product Owner (Phase A–B), CSCO (all — gate authority), Project Manager (coordination)  
**Outputs:** Baselined deliverable artifacts; updated ABBs in the Architecture Repository; CSCO sign-off where required  
**Completes when:** All artifact readiness criteria (§8) are met and the phase gate (§7) passes  

### 4.2 Business Sprint

A Business Sprint is a bounded work unit that produces requirements, market analysis, stakeholder inputs, and refined business capability definitions.

**Primary owners:** Product Owner, Sales & Marketing Manager  
**Supporting roles:** Solution Architect (consuming inputs for Phase A/B), Project Manager (backlog management)  
**Outputs:** Requirements Register updates, market analysis, business scenarios, stakeholder map updates  
**Completes when:** All elicited inputs are captured in the Requirements Register and confirmed by Product Owner; SA has acknowledged receipt  

### 4.3 Solution Sprint (Implementation Sprint)

A Solution Sprint is a bounded work unit that produces a working software increment implemented against a baselined set of ABBs and an Architecture Contract.

**Primary owners:** Implementing Developer (feature implementation), DevOps/Platform Engineer (infrastructure, pipeline), QA Engineer (test execution)  
**Supporting roles:** Software Architect/PE (governance oversight), CSCO (spot-check for safety-relevant components), Project Manager (sprint governance)  
**Outputs:** Working increment, test execution report, deployment record, compliance assessment  
**Completes when:** All acceptance criteria met; no open Severity-1 defects; QA report signed off; CSCO spot-check complete if safety-relevant components were touched  

---

## 5. Stream Interaction and Sequencing

### 5.1 Logical Sequencing Rules

The three streams respect the following mandatory sequencing constraints:

```
Business Stream ──produces──► Requirements Register
                                      │
                                      ▼
Architecture Stream ──consumes──► Requirements Register
                  ──produces──►  ABBs + Architecture Artifacts (Phases A–F)
                                      │
                                      ▼
Implementation Stream ──consumes──► Baselined Architecture Artifacts
                     ──produces──►  SBBs + Working Increment
                                      │
                                      ▼
Architecture Stream (Phase G/H) ──consumes──► Compliance Assessments + Change Requests
```

**Rule 1 (Architecture-first):** No Solution Sprint may begin until the Architecture Stream has produced and baselined the artifact set required to authorise that sprint's work package (as defined in the Implementation Plan, §6.8 below).

**Rule 2 (Business-continuous):** The Business Stream runs continuously throughout the ADM cycle, feeding the Requirements Register. It is not gated by Architecture Sprint completion except when a specific Business Sprint is producing a deliverable required as input to an upcoming Architecture Sprint.

**Rule 3 (Concurrency):** Architecture Sprints for later phases (e.g., Phase C) may begin before all Solution Sprints authorised by earlier phases (e.g., Phase A outputs) are complete, provided the later Architecture Sprint does not depend on Solution Sprint outputs for its inputs.

**Rule 4 (Feedback):** Solution Sprint outputs (compliance assessments, defect records, change requests) feed back into the Architecture Stream for Phase G governance and Phase H change management. This feedback loop is bounded (see §9).

**Rule 5 (CQ Suspension):** When any sprint in any stream raises a blocking Clarification Request (`CQ`) per `clarification-protocol.md`, the specific task sections dependent on the missing information are suspended. All other sprint work continues. The sprint does not close and the phase gate does not pass while blocking CQs remain open on artifacts required for that gate.

### 5.2 Sprint Synchronisation Points

Synchronisation Points are defined coordination events, not time-based ceremonies. They occur:

| Synchronisation Point | Trigger | Participants | Purpose |
|---|---|---|---|
| **Stream Kickoff** | PM opens a new sprint in any stream | PM + sprint owner agents | Confirm scope, prerequisites, and exit criteria |
| **Architecture Handoff** | Architecture Sprint produces a baselined artifact | SA/SwA + receiving agents | Transfer artifact; consuming agents confirm receipt and flag retrieval intent (summary vs full) |
| **Phase Gate Review** | PM determines all phase artifacts are candidate-complete | PM + CSCO + phase-owning SA/SwA | Evaluate gate checklist; record outcome |
| **Implementation Handoff** | Solution Sprint produces a compliance assessment | QA + SwA/PE + PM | Review test report; record governance checkpoint |
| **Retrospective Sync** | Solution Sprint closeout | All agents → PM | Submit lessons-learned notes for PM knowledge base |
| **Clarification Interaction** | PM consolidates open user-facing CQs (≥1 open, or ALG-016 triggered) | PM → User | Present batched questions; receive and route answers; unblock suspended tasks |

### 5.3 ADM Iteration Types

The ADM is **not linear**. TOGAF defines four recognised iteration patterns, each representing a different mode of work within or across phases. Every ADM cycle in this system is classified at cycle initiation with an `iteration-type`, and may transition between types as work evolves.

| Iteration Type | Phases Covered | When Used |
|---|---|---|
| **Architecture Context** (`context`) | Preliminary + A | Establishing or re-establishing the enterprise context, principles, and architecture vision — typically at the start of a new engagement or when a major business change requires vision re-scoping |
| **Architecture Definition** (`definition`) | B, C, D (optionally E/F for planning) | Developing the full architecture across business, information systems, and technology layers — the main body of ADM work |
| **Transition Planning** (`transition`) | E + F | Identifying implementation candidates, gaps, work packages, and sequencing the migration roadmap — always follows a completed Architecture Definition iteration |
| **Architecture Governance** (`governance`) | G + H | Overseeing implementation (Phase G) and managing architecture change (Phase H) — runs concurrently with Solution Sprints |

**Iteration type governs default phase scope.** An `architecture-context` iteration does not proceed to Phase B without a deliberate decision to extend into an `architecture-definition` iteration. The PM records iteration type transitions as `cycle.iteration-type-changed` events in the workflow event store.

**Multiple iteration cycles are expected and normal.** A typical capability-level engagement runs:
1. One `context` iteration (Prelim → A) → produces Architecture Vision
2. One or more `definition` iterations (B → D) → refined as requirements mature
3. One `transition` iteration (E → F) → produces Implementation Plan
4. One or more `governance` iterations (G → H) → runs until the increment is delivered and stable

Phase revisitation within a definition iteration (e.g., returning from Phase C to Phase B after a data architecture finding) is a **normal event**, not an exception. It is recorded via `phase.return-triggered` followed by `phase.entered` with `trigger="revisit"`.

### 5.4 Phase Revisitation and Return Triggers

Phases may be re-entered at any point during an ADM cycle. The workflow event store tracks **visit counts** per phase (`phase_visit_counts` in `CycleState`), allowing agents to distinguish a first-time entry from a revisit. Revisits are triggered by:

| Return Trigger | Source | Target Phase(s) | Recorded As |
|---|---|---|---|
| **Requirements change** | Product Owner raises a requirement change in Requirements Management | Whichever phase originally consumed the changed requirement | `phase.return-triggered` + `requirements-change-id` |
| **Phase H change impact** | Change Record classifies change as Significant or Major | The phase(s) whose artifacts are affected by the change | `phase.return-triggered` + `change-record-id` |
| **Gate rejection** | Phase gate checklist fails | The phase whose gate was evaluated | `gate.held` → agent returns to same phase |
| **Consuming agent feedback** | A consuming agent raises structured feedback (Iteration 1 or 2) on a received artifact | The phase that produced the artifact | Structured feedback record in handoff log |
| **CSCO veto** | CSCO identifies a safety constraint violation during gate review | Phase A (safety envelope) or the phase introducing the constraint | `algedonic.raised` SC category → `phase.return-triggered` |
| **Algedonic resolution** | Resolution of an S1/S2 algedonic signal requires architectural rework | Phase specified in the algedonic resolution record | `algedonic.resolved` → `phase.return-triggered` |

**Revisit scope constraint:** A phase return **does not restart the entire ADM cycle.** Only the artifacts that are identified as requiring revision in the `phase.return-triggered` event's `affected-artifacts` list are re-opened. All other baselined artifacts remain authoritative unless explicitly identified as affected.

**Revisit depth limit:** A phase may be revisited at most **three times** within a single ADM cycle before the PM must escalate to evaluate whether a scope change or cycle reset is required. Three visits without resolution triggers `ALG-005` (timeline collapse).

---

## 6. ADM Phase Coverage by Stream

Each ADM phase is allocated to a primary stream. Secondary streams contribute per the RACI matrix (`framework/raci-matrix.md`).

### 6.1 Preliminary Phase

**Primary stream:** Architecture (SA + PM)  
**Objective:** Establish framework, principles, repositories, and agent mandates  
**Business stream contribution:** PO and Sales/Marketing confirm initial stakeholder universe  
**Exit condition:** Architecture Principles Register baselined; all work-repositories initialised with ownership READMEs; RACI matrix confirmed by all agents; Architecture Repository structure defined  

**Key ABBs established:** Architecture Principles (cross-phase constraints)  
**Key Deliverables:** Architecture Framework definition, Principles Register, Architecture Capability definition  

---

### 6.2 Phase A — Architecture Vision

**Primary stream:** Architecture (SA)  
**Business stream contribution:** PO and Sales/Marketing produce stakeholder map and initial requirements; market analysis feeds business drivers  
**Objective:** Establish stakeholder landscape, business goals, capability overview, and safety envelope  

**Architecture Sprint A produces:**
- Architecture Vision deliverable (see §9 for schema reference)
- Statement of Architecture Work (SA + PM co-produce)
- Draft Architecture Definition Document (shell only — carries forward to Phases B–D)

**Key ABBs established:** Business capabilities (high-level), stakeholder concerns, architecture principles refinement  
**ArchiMate viewpoints:** Strategy Viewpoint (capabilities, resources, outcomes); Motivation Viewpoint (stakeholders, goals, drivers, constraints)

**CSCO gate:** CSCO must review and approve the safety envelope before Phase A exit. A CSCO veto triggers an algedonic signal to PM (see `algedonic-protocol.md §3`).

**CQ expectation:** Phase A is the most CQ-intensive phase. The SA should expect to raise CQs covering: regulatory environment, safety domain, stakeholder authority, technology constraints, and scope boundaries. The Entry Assessment Report (for non-EP-0 entries) pre-empts many of these.

---

### 6.3 Phase B — Business Architecture

**Primary stream:** Architecture (SA + PO consulting)  
**Business stream contribution:** PO provides detailed capability definitions and process models; PO validates value stream mapping  
**Objective:** Produce detailed business capability model, process decomposition, and value streams  

**Architecture Sprint B produces:**
- Business Architecture deliverable
- Updated Architecture Definition Document (Business Architecture section)

**Key ABBs established:** Business capabilities (detailed), business processes, value streams, organisational model, business services  
**ArchiMate viewpoints:** Business Process Cooperation Viewpoint; Organisation Viewpoint; Capability Map Viewpoint

**CSCO contribution:** Business-level safety constraints overlay added to Safety Constraint Overlay artifact  

---

### 6.4 Phase C — Information Systems Architecture

Phase C runs two parallel Architecture Sub-Sprints (Application and Data) which converge at the Phase C gate.

**Primary stream:** Architecture (SwA — Application and Data Architecture production)  
**Consulting stream:** Architecture (SA — business-layer traceability review, max 2 iterations per sub-sprint)  
**Objective:** Define logical application components and data architecture  

**Architecture Sprint C (Application) produces:**
- Application Architecture deliverable
- Interface Catalogue
- Updated Architecture Definition Document (Application Architecture section)

**Architecture Sprint C (Data) produces:**
- Data Architecture deliverable
- Logical Data Model
- Updated Architecture Definition Document (Data Architecture section)

**Key ABBs established (Application):** Logical application components, interfaces, interaction patterns  
**Key ABBs established (Data):** Data entities, logical data model, data classification, data flows  
**ArchiMate viewpoints (Application):** Application Cooperation Viewpoint; Service Realization Viewpoint  
**ArchiMate viewpoints (Data):** Information Structure Viewpoint  

**CSCO contribution:** Information security overlays; data residency and privacy constraints  

---

### 6.5 Phase D — Technology Architecture

**Primary stream:** Architecture (Software Architect/PE, with DevOps consulting)  
**Objective:** Define concrete technology stack, infrastructure topology, and platform services  

**Architecture Sprint D produces:**
- Technology Architecture deliverable
- ADR Register (Architecture Decision Records — one per significant technology decision)
- Updated Architecture Definition Document (Technology Architecture section)
- Technology Standards Catalog

**Key ABBs → SBB candidates identified:** Technology components (still ABBs until Phase E selects specific products); infrastructure topology  
**ArchiMate viewpoints:** Technology Viewpoint; Technology Usage Viewpoint; Physical Viewpoint  

**CSCO contribution:** Technology-level safety constraints; security architecture overlays  

---

### 6.6 Phase E — Opportunities & Solutions

**Primary stream:** Architecture (Software Architect/PE + PM co-produce)  
**Objective:** Gap analysis, implementation candidate identification, build/buy/reuse decisions, initial test strategy  

**Architecture Sprint E produces:**
- Implementation Candidates list (ABBs → SBBs: specific products/services selected)
- Architecture Roadmap (draft)
- Work Package Catalog
- Initial Test Strategy (QA contributes)
- Risk Register
- Updated Safety Constraint Overlay (CSCO reviews risk register)

**Key transition:** First phase where ABBs are mapped to specific SBBs. Phase E is the bridge from architecture to delivery.  

---

### 6.7 Phase F — Migration Planning

**Primary stream:** Architecture/Planning (PM + Software Architect/PE)  
**Objective:** Dependency resolution, roadmap sequencing, Solution Sprint plan  

**Architecture Sprint F produces:**
- Implementation Plan deliverable (consolidates Work Package Catalog, roadmap, transition architectures)
- Solution Sprint Plan (authorises the Implementation Stream to begin)
- Environment Provisioning Plan (DevOps input required)
- Architecture Contract shells (to be completed at Phase G entry for each work package)

**Key output:** The Solution Sprint Plan is the trigger that opens the Implementation Stream.  

---

### 6.8 Phase G — Implementation Governance

Phase G spans the entire Implementation Stream. Each Solution Sprint is a Phase G iteration.

**Primary stream:** Implementation (Dev, DevOps, QA) governed by Architecture (SwA/PE)  
**Objective:** Implement and verify SBBs against baselined ABBs and Architecture Contracts  

**Per Solution Sprint, the Implementation Stream produces:**
- Working increment (feature branch → PR → merged code)
- Unit and integration test reports
- Deployment record (DevOps)
- Compliance Assessment (QA + SwA/PE)
- Updated Risk Register if new risks identified

**Per Solution Sprint, the Architecture Stream produces (governance role):**
- Architecture Contract (signed at sprint entry, referencing the relevant ABBs and acceptance criteria)
- Governance checkpoint record (PM)
- CSCO spot-check record (if safety-relevant component touched)

**Phase G exit condition:** All work packages delivered; full regression suite passed; deployment record complete; CSCO final sign-off; all Architecture Contracts closed.  

---

### 6.9 Phase H — Architecture Change Management

Phase H is a continuous capability, activated at two frequencies:

| Trigger | Scope | Primary Owner |
|---|---|---|
| Solution Sprint closeout | Lightweight: minor changes below impact threshold (see §10) | Project Manager |
| Formal change request | Full change impact assessment | Solution Architect + CSCO |

**Per formal change, the Architecture Stream produces:**
- Change Record (impact classification, decisions, affected artifacts)
- Updated architecture artifacts (re-baselined at new version)
- Updated Safety Constraint Overlay (if safety-relevant)
- PM knowledge base update (lessons learned, skill file improvement candidates)

---

### 6.10 Requirements Management (Cross-Phase)

Requirements Management is not a phase but a continuous Business Stream activity.

| Activity | Owner | Trigger |
|---|---|---|
| Requirement capture / elicitation | Product Owner, Sales/Marketing | Phase A input, stakeholder input, change requests |
| Requirement traceability update | Product Owner | Each architecture artifact baseline |
| Requirement change impact assessment | Solution Architect | On any change request |
| Requirements baseline confirmation | Project Manager | Phase transition gate |

The Requirements Register is a living artifact maintained in the engagement's `work-repositories/architecture-repository/requirements-register/`. It is the authoritative link between stakeholder needs and architecture artifacts.

---

## 7. Phase Transition Gates

A phase transition gate is a formal checkpoint evaluated by the Project Manager with mandatory CSCO input and primary-stream-owner attestation. Gates block progression to the next phase's sprint.

### 7.1 Universal Gate Checklist (all phases)

- [ ] All required phase deliverables are produced and baselined (version ≥ 1.0.0).
- [ ] All artifact summary headers are complete and conform to the format in `repository-conventions.md §3`.
- [ ] CSCO sign-off obtained for all safety-relevant artifacts produced in the phase.
- [ ] Open issues count is zero, or all open issues are explicitly classified as non-blocking with an assigned owner and a target sprint.
- [ ] Requirements traceability confirmed by Product Owner.
- [ ] Sprint log entry closed by PM.
- [ ] No blocking Clarification Requests (`CQ`) are open on any artifact required for this gate.
- [ ] All assumptions recorded in artifact `assumptions` fields have been reviewed; undocumented assumptions are absent.

### 7.2 Gate Outcomes

| Outcome | Condition | Action |
|---|---|---|
| **Pass** | All checklist items satisfied | PM records gate passage; next stream sprint planning opens |
| **Conditional Pass** | Minor open items, explicitly non-blocking, owner and resolution sprint assigned | PM records conditions; monitors resolution |
| **Hold** | One or more items not satisfied but resolution path is clear | Current phase extended by one sprint iteration; gate re-evaluated on completion |
| **Escalate** | Item cannot be resolved within one extension, or CSCO veto issued | Algedonic signal raised per `algedonic-protocol.md` |

### 7.3 Phase-Specific Gate Requirements

| Gate | Additional Requirement |
|---|---|
| Prelim → A | RACI matrix confirmed by all agents |
| A → B | Statement of Architecture Work signed off by PM; safety envelope approved by CSCO |
| B → C | Business-level safety constraints accepted by CSCO and recorded in Safety Constraint Overlay |
| C → D | Application Architecture and Data Architecture artifacts both baselined |
| D → E | All Phase D ADRs recorded with rationale; CSCO technology safety overlays accepted |
| E → F | Risk Register reviewed by CSCO; implementation candidates approved by PM |
| F → G | Solution Sprint Plan approved by PM; Architecture Contract shells created; Environment Provisioning Plan accepted by DevOps |
| G exit | All work packages delivered; full regression suite passed; deployment record complete; CSCO final sign-off |
| H (formal change) → target phase | Change Record complete; change impact classification finalised; CSCO sign-off if safety-relevant |

---

## 8. Artifact Readiness Criteria

An artifact is **ready** (eligible for handoff and cross-agent consumption) when all of the following are true:

1. The artifact conforms to its schema (`framework/artifact-schemas/<artifact-type>.schema.md`).
2. The artifact summary header (§9.2) is complete — all required fields present.
3. The artifact is stored at its canonical path within the owning work-repository.
4. The artifact is baselined at version ≥ 1.0.0.
5. All mandatory reviewer sign-offs are recorded in the metadata block (CSCO if safety-relevant; PM always).
6. The artifact is committed to version control.

7. The artifact's `pending-clarifications` list is empty — all blocking CQs are resolved.
8. All entries in the artifact's `assumptions` list have been reviewed and are either confirmed by a user answer or explicitly accepted with documented rationale.

An artifact in **draft** state (version 0.x.x) may be shared for early feedback but **must not** be used as the authoritative input to a phase gate, Architecture Contract, or skill that produces a binding output.

---

## 9. Inter-Agent Feedback Cycles

### 9.1 Normal Feedback Loop (per handoff)

1. **Consuming agent** logs the issue using the structured feedback template (`repository-conventions.md §5`).
2. **Producing agent** revises the artifact and re-issues (iteration 1).
3. If the revision is still unsatisfactory, a second and **final** revision may be requested (iteration 2).
4. If unresolved after two iterations, the consuming agent escalates to **PM**.
5. **PM adjudicates**: mandates acceptance with documented exceptions, restructures work, or raises an algedonic signal.

**Maximum: 2 revision iterations.** Escalation to PM is mandatory on iteration 3.

### 9.2 Sprint Review Cycle (user approval gate)

The Sprint Review (BPR-006) is a distinct feedback loop governed by user authority, not the normal two-iteration cap:

1. PM emits `review.pending`; dashboard surfaces all sprint artifacts.
2. **User** reviews each artifact and marks it: `approved`, `needs-revision`, or `rejected` (with optional agent tag and comment).
3. Needs-revision and rejected items are routed as handoffs to the tagged specialist agent(s).
4. Agents revise and write the corrected artifacts.
5. **Revised artifacts are re-presented to the user** for a fresh review cycle.
6. Steps 2–5 repeat until the user marks **all** artifacts `approved`.
7. Only when all items are approved does `sprint.close` proceed.

**Key constraints:**
- The sprint does **not** close while any item is `needs-revision` or `rejected`.
- The user has authority to request indefinite rework cycles — there is no iteration cap for the sprint review.
- The 2-iteration cap in §9.1 applies to inter-agent handoff loops only; it does not constrain user-driven review cycles.

### 9.3 Retrospective Feedback (sprint boundary)

At each sprint closeout, all agents submit a structured retrospective note to the PM. Notes are stored in `engagements/<id>/work-repositories/project-repository/knowledge-base/retrospectives/` for engagement-level learning. At engagement close, synthesised lessons learned are promoted to `enterprise-repository/knowledge-base/` for cross-engagement reuse. PM identifies skill file improvement candidates from retrospective notes; skill file changes require PM approval.

---

## 10. Artifact Ontology

This section defines the authoritative set of artifacts for this system — a tailored, streamlined selection from the full TOGAF content framework. The set is designed to be complete enough to support all agent roles while remaining manageable.

### 10.1 TOGAF Content Hierarchy

```
Deliverable  (formally reviewed, archived in Architecture Repository)
  └── Artifact  (catalog | matrix | diagram | model | register)
        └── Building Block  (ABB → SBB through the lifecycle)
```

- **Deliverable:** A formally reviewed, signed-off work product that is contractually binding between agent roles. Archived in the relevant work-repository.
- **Artifact:** A concrete document, model, diagram, catalog, or matrix within a deliverable. The unit of inter-agent communication.
- **Architecture Building Block (ABB):** Defines *what* capability or quality is required. Produced in Architecture Sprints (Phases A–D). Technology-independent.
- **Solution Building Block (SBB):** Defines *how* a capability is implemented using specific products, services, or code. Identified in Phase E; built in Phase G.

### 10.2 Universal Artifact Summary Header

Every artifact produced by any agent MUST begin with a summary header in the following YAML frontmatter format. This header is the unit of normal-tempo inter-agent communication. Consuming agents read the header first and retrieve the full artifact only when the confidence threshold is not met (see `repository-conventions.md §4`).

```yaml
---
artifact-type:     # schema identifier (see §9.3)
artifact-id:       # unique identifier e.g. AV-001
version:           # semver, e.g. 1.0.0 (≥1.0.0 = baselined)
phase:             # ADM phase: Prelim | A | B | C | D | E | F | G | H | RM
status:            # draft | baselined | superseded | archived
owner-agent:       # canonical agent role name
produced-in:       # sprint identifier e.g. AS-3 (Architecture Sprint 3)
path:              # canonical path in work-repository
depends-on:        # list of artifact-ids this artifact consumed as input
consumed-by:       # list of artifact-ids or agent roles that consume this
safety-relevant:   # true | false
csco-sign-off:     # true | false | not-required
pm-sign-off:       # true | false
summary: |
  2–4 sentence plain-language summary of content and key decisions.
key-decisions:     # list of the most important decisions captured
open-issues:       # list of open items with owner and target sprint
---
```

### 10.3 Artifact Catalog

The following table defines all artifacts in the system. Schema files are located in `framework/artifact-schemas/`.

#### Driving Artifacts (Architecture Stream → authorise and bound all work)

| ID | Artifact | Phase | Type | Owner | Schema | ABB/SBB |
|---|---|---|---|---|---|---|
| `AV` | Architecture Vision | A | Deliverable | Solution Architect | `architecture-vision.schema.md` | ABB |
| `BA` | Business Architecture | B | Deliverable | Solution Architect | `business-architecture.schema.md` | ABB |
| `AA` | Application Architecture | C | Deliverable | Software Architect/PE | `application-architecture.schema.md` | ABB |
| `DA` | Data Architecture | C | Deliverable | Software Architect/PE | `data-architecture.schema.md` | ABB |
| `TA` | Technology Architecture | D | Deliverable | Software Architect/PE | `technology-architecture.schema.md` | ABB→SBB |

#### Planning Artifacts (bridge architecture to implementation)

| ID | Artifact | Phase | Type | Owner | Schema | ABB/SBB |
|---|---|---|---|---|---|---|
| `IP` | Implementation Plan | E+F | Deliverable | Project Manager | `implementation-plan.schema.md` | SBB |
| `TS` | Test Strategy | E–G | Deliverable | QA Engineer | `test-strategy.schema.md` | SBB |
| `AR` | Architecture Roadmap | E–F | Artifact (diagram+catalog) | Project Manager | embedded in `implementation-plan.schema.md` | SBB |

#### Governance Artifacts (control and verify implementation)

| ID | Artifact | Phase | Type | Owner | Schema | ABB/SBB |
|---|---|---|---|---|---|---|
| `AC` | Architecture Contract | G | Deliverable | Software Architect/PE | `architecture-contract.schema.md` | binding ref |
| `CA` | Compliance Assessment | G | Artifact (checklist) | QA + Software Architect/PE | embedded in `architecture-contract.schema.md` | — |
| `DR` | Deployment Record | G | Artifact (log) | DevOps/Platform Engineer | embedded in `implementation-plan.schema.md` | SBB |
| `CR` | Change Record | H | Deliverable | Solution Architect | `change-record.schema.md` | — |

#### Cross-Cutting Artifacts (span all phases)

| ID | Artifact | Phase | Type | Owner | Schema | ABB/SBB |
|---|---|---|---|---|---|---|
| `SCO` | Safety Constraint Overlay | All | Deliverable | CSCO | `safety-constraint-overlay.schema.md` | ABB |
| `RR` | Requirements Register | RM | Living register | Product Owner | `requirements-register.schema.md` | ABB |
| `ADR` | Architecture Decision Record | D (primary), all | Artifact (per-decision) | Phase owner | embedded in `technology-architecture.schema.md` | ABB→SBB |
| `PR` | Architecture Principles Register | Prelim | Register | Solution Architect | embedded in `architecture-vision.schema.md` | ABB |

#### Internal Artifacts (agent-internal, not formally handed off)

| ID | Artifact | Used By | Purpose |
|---|---|---|---|
| `WN` | Working Notes | All agents | In-progress reasoning, retrieval log, draft decisions (not archived) |
| `RL` | Retrospective Note | All agents → PM | Sprint boundary lessons-learned input |
| `GC` | Governance Checkpoint | PM | Sprint governance record |

### 10.4 Per-Phase Artifact Taxonomy (catalogs, matrices, diagrams)

The following table specifies the artifact sub-types within each major deliverable, aligned with TOGAF's content framework classification (catalog / matrix / diagram / model).

| Phase | Artifact Sub-Types |
|---|---|
| **Prelim** | Principles Catalog; Stakeholder Register (catalog); Architecture Capability definition |
| **A** | Stakeholder Map (diagram); Value Driver Catalog; Capability Overview Diagram; Architecture Principles (catalog); Safety Envelope Statement |
| **B** | Business Capability Map (catalog + diagram); Business Process Catalog; Business Function/Process Matrix; Value Stream Diagram; Organisation Chart; Business Service Catalog |
| **C (App)** | Application Component Catalog; Interface Catalog; Application/Business Function Matrix; Application Interaction Diagram; Application Architecture Diagram |
| **C (Data)** | Data Entity Catalog; Logical Data Model (diagram); Data/Business Function Matrix; Data Flow Diagram; Data Classification Register |
| **D** | Technology Component Catalog; Technology/Application Matrix; Infrastructure Diagram; Network Topology Diagram; ADR Register; Technology Standards Catalog |
| **E** | Implementation Candidate Catalog; Gap Analysis Matrix (baseline vs target); Risk Register; Architecture Roadmap (diagram); Work Package Catalog |
| **F** | Detailed Roadmap (Gantt-equivalent, logical); Dependency Matrix; Transition Architecture Diagrams; Environment Provisioning Catalog |
| **G** | Architecture Contract; Compliance Checklist; Test Execution Report; Deployment Record; Defect Register |
| **H** | Change Log; Change Impact Matrix; Updated Architecture Artifacts (re-baselined) |
| **RM** | Requirements Register; Requirements Traceability Matrix (requirements ↔ artifacts) |
| **Cross-cutting** | Safety Constraint Overlay (per phase: business, application, data, technology, implementation) |

### 10.5 Building Block Lifecycle

Building blocks evolve from abstract (ABB) to concrete (SBB) as the ADM progresses:

```
Phase A–B:  ABBs = business capabilities, organisational functions
Phase C:    ABBs = logical application components, data entities
Phase D:    ABBs = technology component types → SBB candidates identified
Phase E:    ABBs mapped to specific SBBs (product selection, build/buy decisions)
Phase G:    SBBs built, tested, deployed as working code and infrastructure
Phase H:    SBBs updated in response to change; ABBs revised if change is significant
```

The engagement's Architecture Repository holds both the ABB definitions (in `work-repositories/architecture-repository/`) and the SBB inventory (in `work-repositories/technology-repository/` for platform/infra SBBs; in `work-repositories/delivery-repository/` for code SBBs). All paths are relative to `engagements/<id>/`.

### 10.6 ArchiMate Viewpoint Mapping

ArchiMate 3 viewpoints replace or complement non-standard TOGAF diagrams. The following mapping applies where agents produce visual models:

| Phase | Recommended ArchiMate Viewpoint(s) | Models |
|---|---|---|
| Prelim | Motivation Viewpoint | Architecture principles, goals, constraints |
| A | Strategy Viewpoint; Stakeholder Viewpoint; Goal Realization Viewpoint | Capabilities, drivers, goals, stakeholder concerns |
| B | Business Process Cooperation Viewpoint; Organisation Viewpoint; Capability Map Viewpoint | Processes, services, organisational structure, capabilities |
| C (App) | Application Cooperation Viewpoint; Service Realization Viewpoint | Application components, interfaces, interactions |
| C (Data) | Information Structure Viewpoint | Data entities, relationships, data flows |
| D | Technology Viewpoint; Technology Usage Viewpoint; Physical Viewpoint | Infrastructure, nodes, networks, deployment |
| E | Requirements Realization Viewpoint; Capability Map Viewpoint | Gap analysis, ABB-to-SBB mapping |
| F | Implementation and Migration Viewpoint; Migration Viewpoint | Work packages, plateaus, transition states |
| G | Implementation and Deployment Viewpoint | Application + infrastructure deployment structure |
| H | Implementation and Migration Viewpoint | Change impacts, updated plateaus |

---

## 11. Change Impact Classification (Phase H)

Every change request entering Phase H is classified before routing.

| Class | Threshold | Routing |
|---|---|---|
| **Minor** | No architectural artifact affected; change is localised to a single SBB; no safety-relevant system affected | PM-only approval; lightweight H procedure; no re-baselining required |
| **Significant** | One or more architectural artifacts affected; no safety-relevant system affected | SA + PM approval; full Phase H procedure; affected artifacts re-baselined |
| **Major** | Multiple phases or cross-cutting architectural decisions affected | Full change impact assessment; all affected agent owners consulted; CSCO gate |
| **Safety-Critical** | Any change to a safety-relevant component or constraint, regardless of scope | Immediate CSCO involvement; algedonic signal if CSCO unavailable; no implementation until CSCO approves |

---

## 12. Architecture Repository Structure

The Architecture Repository is organised across three scopes. The full specification is in `framework/architecture-repository-design.md`. Summary:

### 12.1 Enterprise Architecture Repository (`enterprise-repository/`)

Long-lived, organisation-wide content that persists across all engagements. Follows TOGAF's eight-component Architecture Repository model:

| TOGAF Component | Contents | Path |
|---|---|---|
| **Architecture Metamodel** | Framework documents, methodology decisions, governance procedures | `framework/` |
| **Architecture Capability** | Agent mandates (AGENT.md), governance procedures, RACI | `agents/*/AGENT.md` + `framework/raci-matrix.md` |
| **Architecture Landscape** | Strategic and Segment architectures (Capability-level lives in engagements) | `enterprise-repository/landscape/` |
| **Standards Information Base (SIB)** | Approved technology standards, product choices, mandated patterns | `enterprise-repository/standards/` |
| **Reference Library** | Reusable patterns, templates, reference models | `enterprise-repository/reference-library/` |
| **Governance Log** | Append-only cross-engagement governance records | `enterprise-repository/governance-log/` |
| **Architecture Requirements Repository** | Enterprise-level requirements | `enterprise-repository/requirements/` |
| **Solutions Landscape** | Deployed or planned SBBs across the enterprise | `enterprise-repository/solutions-landscape/` |

### 12.2 Engagement Repository (`engagements/<id>/`)

Project-scoped working store for a single ADM cycle. Created at engagement start; closed and partially promoted to the Enterprise Repository at engagement end.

| Content | Path |
|---|---|
| Architecture Vision, Business Architecture, App/Data Architecture | `engagements/<id>/work-repositories/architecture-repository/` |
| Technology Architecture, ADRs, SBB inventory | `engagements/<id>/work-repositories/technology-repository/` |
| Sprint log, governance records, decision log | `engagements/<id>/work-repositories/project-repository/` |
| Safety analyses, STPA, SCO | `engagements/<id>/work-repositories/safety-repository/` |
| Feature branches, PRs, unit test reports | `engagements/<id>/work-repositories/delivery-repository/` |
| Test strategies, test cases, defect records | `engagements/<id>/work-repositories/qa-repository/` |
| IaC, pipeline configs, deployment records | `engagements/<id>/work-repositories/devops-repository/` |
| Workflow event log (SQLite + YAML export) | `engagements/<id>/workflow-events/` + `engagements/<id>/workflow.db` |
| CQ records, handoff records, algedonic signals | `engagements/<id>/clarification-log/`, `handoff-log/`, `algedonic-log/` |

### 12.3 External Read-Only Sources (`external-sources/`)

Configured adapter definitions for organisation-owned information systems (Confluence, Jira, external git repositories, etc.) that agents may query but never modify. See `framework/architecture-repository-design.md §2.3` for the adapter configuration format.

### 12.4 Architecture Landscape Levels

The Architecture Landscape is stratified into three levels, reflecting TOGAF's architecture partitioning model:

| Level | Scope | Produced By | Lives In |
|---|---|---|---|
| **Strategic** | Enterprise-wide; 3–5 year horizon | Architecture Board | `enterprise-repository/landscape/strategic/` |
| **Segment** | Business domain; 1–2 year horizon | Domain Architect / SA | `enterprise-repository/landscape/segment/` |
| **Capability** | Specific engagement; duration of project | Engagement SA | `engagements/<id>/work-repositories/architecture-repository/` → promoted on engagement close |

Capability-level architectures are promoted to `enterprise-repository/landscape/capability/` at engagement close, subject to Architecture Board review.

---

## 13. Token Budget and Retrieval Strategy

To control LLM token consumption, every inter-agent artifact transfer follows the confidence-threshold protocol specified in `repository-conventions.md §4`. Summary:

- **Default:** Consume artifact summary header only (~200–400 tokens).
- **Full retrieval required when:** The task produces a binding output; the summary is insufficient for correctness; an inconsistency is detected; the task involves safety-relevant decisions.
- **Full retrievals must be logged** with a one-line reason in the consuming agent's Working Notes.

Architecture Sprints tend toward more full retrievals (new binding artifacts being produced). Solution Sprints tend toward summary-only consumption (executing against already-baselined specs).

---

## 14. Glossary

| Term | Definition |
|---|---|
| **Architecture Sprint (ADM Sprint)** | A bounded work unit in the Architecture Stream producing one or more baselined deliverable artifacts |
| **Business Sprint** | A bounded work unit in the Business Stream producing requirements, market analysis, and stakeholder inputs |
| **Solution Sprint (Implementation Sprint)** | A bounded work unit in the Implementation Stream producing a working software increment |
| **Architecture Building Block (ABB)** | Defines *what* capability or quality is required; technology-independent; produced in Architecture Sprints |
| **Solution Building Block (SBB)** | Defines *how* a capability is implemented; technology-specific; identified in Phase E, built in Phase G |
| **Deliverable** | A formally reviewed, signed-off, archived work product that is contractually binding between agent roles |
| **Artifact** | A concrete document, model, diagram, catalog, matrix, or register within a deliverable |
| **Baseline** | An artifact at version ≥ 1.0.0 that has passed its gate and is authorised for downstream consumption |
| **Draft** | An artifact at version 0.x.x; shareable for feedback but not authoritative |
| **Gate** | A formal phase-transition checkpoint evaluated by PM with mandatory CSCO input |
| **Algedonic signal** | A fast-path escalation bypassing normal topology; defined in `algedonic-protocol.md` |
| **Handoff event** | A structured, schema-defined transfer of an artifact from one agent to another |
| **Confidence threshold** | The decision rule governing whether a consuming agent reads a full artifact or only its summary header |
| **Architecture Repository** | The governed store for all architecture artifacts; structured per TOGAF's six-component model |
| **Cross-Development Collaboration** | The chosen TOGAF agile integration pattern: three coordinating sprint streams (Business, Architecture, Implementation) |
| **Clarification Request (CQ)** | A formal record raised by an agent when it cannot proceed correctly without information from the user or another party; governed by `clarification-protocol.md` |
| **Entry Point** | The ADM phase at which an engagement begins, determined by what the user already has; seven entry points defined in `sdlc-entry-points.md` |
| **Engagement Profile** | The first artifact produced in any engagement, recording entry point, existing artifacts, in-scope phases, and pre-emptive CQs |
| **Iteration Type** | The mode of work active in the current ADM cycle phase group: `context` (Prelim+A), `definition` (B–D), `transition` (E–F), or `governance` (G+H) |
| **Phase Revisitation** | Re-entry into a phase already visited in the current cycle, triggered by change impact, feedback, or gate rejection; recorded via `phase.entered` with trigger ≠ `initial` |
| **Phase Visit Count** | The number of times a phase has been entered in the current cycle; tracked in workflow state; ≥2 indicates a revisit |
| **Return Trigger** | The event that causes a phase to be revisited: requirements change, Phase H change impact, gate rejection, consuming agent feedback, CSCO veto, or algedonic resolution |
| **Architecture Landscape Level** | One of three levels — Strategic (enterprise-wide), Segment (domain/programme), Capability (project) — at which architecture is described and governed |
| **Engagement Repository** | The project-scoped working store for a single ADM cycle; one per engagement under `engagements/<id>/` |
| **Enterprise Repository** | The organisation-wide, long-lived architecture store; persists across all engagements; lives in `enterprise-repository/` |
| **EventStore** | The Python class providing the sole write path to the SQLite workflow event database; enforces Pydantic validation and append-only semantics |
| **Workflow State** | The computed current state of an engagement's ADM workflow: active cycles, phase visit counts, open CQs, gate history, and artifact registry; reconstructed from or snapshotted from the event log |
| **Warm-Start Artifact** | A draft artifact (version 0.x.x) produced by ingesting and reconstructing user-provided documents during entry assessment |
| **Knowledge Adequacy Self-Assessment** | The structured decision process an agent performs before executing a task to determine whether it has sufficient information to proceed; governed by `clarification-protocol.md §2` |

---

## Appendix A — Stream Interaction Diagram

```
BUSINESS STREAM (PO, Sales)
─────────────────────────────────────────────────────────────────────────────────────────
  [BS-1: Stakeholder Map]──►[BS-2: Requirements]──►[BS-n: Ongoing Elicitation + Change]
            │                       │                           │
            │                       ▼                           ▼
            │            Requirements Register ◄─── continuous updates
            │                       │
ARCHITECTURE STREAM (SA, SwA/PE, CSCO)
─────────────────────────────────────────────────────────────────────────────────────────
            ▼                       ▼
     [AS-Prelim]────►[AS-A]────►[AS-B]────►[AS-C]────►[AS-D]────►[AS-E]────►[AS-F]
       Principles     AV+SoAW    BA        AA+DA        TA       Candidates   IP
          │             │         │           │           │           │         │
          └─────────────┴─────────┴───────────┴───────────┘           │         │
                                                                       ▼         ▼
                                                              Gate E/F Review + Solution Sprint Plan
                                                                                 │
IMPLEMENTATION STREAM (Dev, DevOps, QA)               ◄──────────────────────────┘
─────────────────────────────────────────────────────────────────────────────────────────
                                                        [SS-1]──►[SS-2]──►[SS-n]──►Phase G exit
                                                         SBBs     SBBs    SBBs + DR
                                                           │        │        │
                                                           └────────┴────────┘
                                                                    │
                                    Compliance Assessments + Change Requests
                                                                    │
                                    ◄───────────────────────────────┘
                         ARCHITECTURE STREAM (Phase G governance + Phase H change mgmt)
```

---

## Appendix B — Artifact Dependency Map

```
PR (Principles) ──────────────────────────────────────────────────────► all phases
RR (Requirements) ─────────────────────────────────────────────────────► all phases
                                                        ▲ (continuous updates)
AV ─────────────────────────────────────────────► BA ─► AA ─► IP
                                                   │     DA ─► IP
                                                   │           │
                                              SCO (B) ─────────► SCO (C) ─► SCO (D)
                                                                      │          │
                                                                      └──────────► IP
                                                                                   │
                                                                TA ──────────────► IP ─► AC ─► CA
                                                                │                        │
                                                               ADR                    Compliance
                                                                                          │
                                                                                    TS ──► DR
                                                                                          │
                                                                                    CR ◄── (H)
```

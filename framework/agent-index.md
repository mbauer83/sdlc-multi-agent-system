# Agent & Skill Routing Index

**Version:** 1.1.0  
**Status:** Approved — Stage 4  
**Last Updated:** 2026-04-03  
**Purpose:** Low-token routing reference. Load this file (~500 tokens) to decide which agent and skill to invoke. Full specifications live in `agents/<role>/AGENT.md` and `agents/<role>/skills/<skill>.md` (load only when the full spec is needed for execution).

---

## Agent Routing Table

| Agent ID | Role | Primary Phases | Invoke When |
|---|---|---|---|
| PM | Project Manager (Coordinator) | Prelim, A, E, F, G, H | Engagement start/close; any phase/sprint start; gate evaluation; CQ batching; algedonic routing; inter-agent deadlock |
| SA | Solution Architect (Integrator) | A, B, C, H | Architecture Vision, Business Architecture, Application/Data Architecture production; Phase H Change Record; architecture traceability review |
| SwA | Software Architect / PE (Integrator) | D, E, F, G | Technology Architecture; Gap Analysis; Transition Architecture; Architecture Contract; Phase G compliance review; technology-layer Phase H impact |
| DO | DevOps / Platform Engineer (Specialist) | D, E, F, G | Platform feasibility review of TA (Phase D); infrastructure planning (E/F); environment provisioning, pipeline execution, deployment records (G) |
| DE | Implementing Developer (Specialist) | G | Phase G Solution Sprint feature implementation; PR submission against Architecture Contract |
| QA | QA Engineer (Specialist) | G | Test strategy/planning (E/F); Phase G test execution; defect records; Compliance Assessment; Phase G gate vote; Phase H regression scope |
| PO | Product Owner (Framing) | Prelim, A, B, H | Requirements Register; Business Scenarios; requirements traceability; stakeholder communication |
| SM | Sales & Marketing Manager (Framing) | A | Market Analysis; SWOT; business drivers input to Architecture Vision |
| CSCO | Chief Safety & Compliance Officer (Integrator) | A, B, C, D, G, H | Safety Constraint Overlay; gate authority on all phase transitions; STAMP/STPA analysis; implementation spot-checks; incident response |

**Decision rule:** Match current phase → agents with that phase in Primary Phases. Then match task type to RACI (accountable vs consulting). When multiple agents are eligible, the accountable agent's skill runs first; consulting agents run in parallel or receive handoffs.

---

## Skill Routing Table

### PM Skills

| Skill ID | File | Invoke When |
|---|---|---|
| PM-MASTER | `skills/master-agile-adm.md` | Always active for PM — engagement orchestration, sprint cadence, gate evaluation, CQ and algedonic routing |
| PM-PHASE-A | `skills/phase-a.md` | Phase A scoping, Entry Assessment Report, SoAW, EP-0 scoping interview |
| PM-PHASE-EF | `skills/phase-e-f.md` | Phase E/F: Work Package Catalog, Risk Register, Implementation Plan, Solution Sprint planning |
| PM-PHASE-G | `skills/phase-g.md` | Phase G: Solution Sprint governance, Architecture Contract oversight, Governance Checkpoint Records |
| PM-PHASE-H | `skills/phase-h.md` | Phase H: Change Record intake, change classification, phase return coordination |
| PM-RETRO | `skills/retrospective-knowledge-capture.md` | Sprint retrospectives, Engagement Retrospective, Enterprise Promotion Review |

### SA Skills

| Skill ID | File | Invoke When |
|---|---|---|
| SA-PHASE-A | `skills/phase-a.md` | Phase A sprint starts or EP-0/A/B warm-start; produce AV, Principles Register, Stakeholder Register, Safety Envelope draft |
| SA-PHASE-B | `skills/phase-b.md` | Phase B sprint starts; AV baselined; produce full Business Architecture |
| SA-PHASE-C-APP | `skills/phase-c-application.md` | Phase C sprint starts; BA baselined; produce Application Architecture |
| SA-PHASE-C-DATA | `skills/phase-c-data.md` | Phase C sprint starts; BA baselined; produce Data Architecture (runs with SA-PHASE-C-APP, mutual reference) |
| SA-PHASE-H | `skills/phase-h.md` | PM issues Phase H Change Record intake; SA assesses architecture impact and produces Change Record |
| SA-REQ-MGMT | `skills/requirements-management.md` | Cross-phase at each phase boundary; maintain architecture column of Requirements Traceability Matrix |

### SwA Skills

| Skill ID | File | Invoke When |
|---|---|---|
| SwA-PHASE-D | `skills/phase-d.md` | Phase D sprint starts; AA and DA handoffs acknowledged; produce Technology Architecture |
| SwA-PHASE-E | `skills/phase-e.md` | Phase E sprint starts; TA baselined; produce Gap Analysis Matrix and Implementation Candidate Catalog |
| SwA-PHASE-F | `skills/phase-f.md` | Phase F sprint starts; produce Transition Architecture Diagrams; review PM's Implementation Plan for technical feasibility |
| SwA-PHASE-G | `skills/phase-g-governance.md` | Phase F gate passed; each Solution Sprint starts; author Architecture Contract; review PRs; issue Compliance Notices |
| SwA-PHASE-H | `skills/phase-h.md` | SA issues Change Record; SwA assesses technology-layer impact; update TA and AC as required |

### DO Skills

| Skill ID | File | Invoke When |
|---|---|---|
| DO-PHASE-D | `skills/phase-d.md` | SwA issues TA draft handoff to DO for operational feasibility review; produce Phase D Feedback Record and EPC draft |
| DO-PHASE-E | `skills/phase-e.md` | Phase E sprint starts; TA baselined; produce Environment Provisioning Catalog and Pipeline Capability Assessment |
| DO-PHASE-F | `skills/phase-f.md` | Phase F sprint starts; produce Pipeline Implementation Plan and environment runbooks |
| DO-PHASE-G | `skills/phase-g.md` | Phase G Solution Sprint starts; provision environments, execute deployment pipelines, produce Deployment Records |

### DE Skills

| Skill ID | File | Invoke When |
|---|---|---|
| DE-PHASE-G | `skills/phase-g.md` | Architecture Contract baselined (v1.0.0) and Solution Sprint starts; implement assigned Work Packages, submit PRs |
| DE-PHASE-E-FEEDBACK | `skills/phase-e-feedback.md` | PM requests DE consulting input on Phase E Implementation Candidate Catalog feasibility |
| DE-PHASE-F-FEEDBACK | `skills/phase-f-feedback.md` | PM requests DE consulting input on Phase F Work Package or Implementation Plan feasibility |

### QA Skills

| Skill ID | File | Invoke When |
|---|---|---|
| QA-PHASE-EF | `skills/phase-ef-test-planning.md` | Phase E/F sprint starts; produce Test Strategy and Test Case Catalog from Architecture Contract and TA |
| QA-PHASE-G | `skills/phase-g-execution.md` | Phase G Solution Sprint starts; AC baselined; execute test plans, manage defect records, contribute to Compliance Assessment |
| QA-PHASE-H | `skills/phase-h-regression.md` | Phase H Change Record issued; assess regression scope; update Test Strategy; produce regression test plan |

### PO Skills

| Skill ID | File | Invoke When |
|---|---|---|
| PO-PHASE-A | `skills/phase-a.md` | Phase A sprint starts or Scoping Interview is active; produce and maintain Requirements Register; provide Business Scenarios to SA |
| PO-PHASE-B | `skills/phase-b.md` | Phase B sprint starts; BA is being authored; PO provides domain context, validates capability model and value stream map |
| PO-PHASE-H | `skills/phase-h.md` | Phase H Change Record issued; PO assesses requirements impact of the change; update Requirements Register |
| PO-REQ-MGMT | `skills/requirements-management.md` | Cross-phase; maintain Requirements Register; trace requirements through architecture phases; flag contradictions to SA |
| PO-STAKEHOLDER | `skills/stakeholder-communication.md` | PM requests stakeholder update; PO drafts and routes stakeholder-facing communication on scope, progress, or change |

### SM Skills

| Skill ID | File | Invoke When |
|---|---|---|
| SM-MARKET-RESEARCH | `skills/phase-a-market-research.md` | Engagement start (EP-0) or PM requests market context for Phase A; SM produces Market Analysis and business driver inputs |
| SM-SWOT | `skills/phase-a-swot.md` | Phase A sprint starts; SM produces SWOT Analysis and competitive landscape inputs to Architecture Vision |
| SM-REQ-FEEDBACK | `skills/requirements-management-feedback.md` | PO requests SM consulting input on market fit or commercial feasibility of proposed requirements |

### CSCO Skills

| Skill ID | File | Invoke When |
|---|---|---|
| CSCO-STAMP-STPA | `skills/stamp-stpa-methodology.md` | Master methodology reference — loaded by all CSCO gate skills; not invoked directly by PM router |
| CSCO-GATE-A | `skills/gate-phase-a.md` | AV baselined at 1.0.0; SA requests CSCO Phase A gate review; CSCO casts Prelim→A and A→B gate votes |
| CSCO-GATE-B | `skills/gate-phase-b.md` | BA baselined at 1.0.0; CSCO performs STAMP Level 1 update and casts B→C gate vote |
| CSCO-GATE-C | `skills/gate-phase-c.md` | Both AA and DA baselined at 1.0.0; CSCO performs STAMP Level 2 analysis and casts C→D gate vote |
| CSCO-GATE-D | `skills/gate-phase-d.md` | TA baselined at 1.0.0; CSCO performs STAMP Level 3 analysis and casts D→E gate vote |
| CSCO-GATE-G | `skills/gate-phase-g.md` | (Mode 1) PM requests implementation spot-check during Phase G sprint; (Mode 2) QA Compliance Assessment baselined — CSCO casts G-exit gate vote |
| CSCO-GATE-H | `skills/gate-phase-h.md` | Change Record baselined; CSCO classifies change safety impact and casts H gate vote |
| CSCO-INCIDENT | `skills/incident-response.md` | Algedonic signal (S1/S2) received; PM reports production safety incident; safety constraint violation detected post-deployment |

---

## Phase-to-Agent Activation Map

Quick lookup: given a phase transition (`gate.evaluated` result=passed), which agents activate?

| Phase Entry | Activate (Primary) | Activate (Consulting) |
|---|---|---|
| Prelim | PM | SA (if EP-0) |
| A | PM, SA | PO, CSCO |
| B | SA | PO, CSCO |
| C | SA | SwA, PO, CSCO |
| D | SwA, DO | SA, CSCO |
| E | SwA, DO | SA, DE, QA, CSCO |
| F | SwA, DO | DE, QA |
| G (per Solution Sprint) | SwA, DO, DE, QA | PM (governance) |
| H | SA | SwA, CSCO, QA |

---

## Cross-Reference

- Full agent specs: `agents/<role>/AGENT.md` (frontmatter has full routing metadata)
- Full skill specs: `agents/<role>/skills/<skill>.md` (frontmatter has trigger-conditions, entry-points, primary-outputs)
- Personality and tension protocol: `framework/agent-personalities.md`
- Phase gate criteria: `framework/agile-adm-cadence.md §6`
- RACI accountability matrix: `framework/raci-matrix.md`

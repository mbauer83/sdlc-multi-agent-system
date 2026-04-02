# Schema: Safety Constraint Overlay (`SCO`)

**Version:** 1.0.0  
**ADM Phases:** All (updated at each phase; one living artifact per engagement)  
**Owner:** Chief Safety & Compliance Officer (CSCO)  
**Consumed by:** All agents at all phases — the SCO is a mandatory input to every phase gate  

---

## 1. Purpose

The Safety Constraint Overlay is the CSCO's primary artifact. It is a living document that grows as each ADM phase adds domain-specific safety analysis. It applies the STAMP/STPA methodology to derive safety constraints from the control structure identified at each phase, and it records the CSCO's sign-off status on each phase's safety adequacy.

The SCO is not an optional add-on. Every agent that produces a binding artifact that could affect safety must read the current SCO before doing so. No phase gate can pass without the CSCO's sign-off on the SCO update for that phase.

---

## 2. STAMP/STPA Methodology Reference

This artifact applies **STAMP** (Systems-Theoretic Accident Model and Processes) and **STPA** (System-Theoretic Process Analysis) as the analytical method:

- **STAMP** models safety as a control problem: accidents occur when safety constraints are violated due to inadequate control actions or missing feedback in a control structure.
- **STPA** is the hazard analysis method derived from STAMP: it identifies Unsafe Control Actions (UCAs) from the control structure and derives safety constraints to prevent them.

The STPA process followed:
1. Define the system safety goal (loss prevention objective)
2. Model the hierarchical control structure
3. Identify Unsafe Control Actions (UCAs) — control actions that are too late, too early, absent, or incorrect
4. Determine causal factors for each UCA
5. Derive safety constraints (requirements) to eliminate or mitigate each UCA

---

## 3. Artifact Structure

The SCO is structured as a series of phase-specific sections, each added when that phase is completed. The document grows through the ADM cycle.

### 3.1 Summary Header
- `artifact-type: safety-constraint-overlay`
- `safety-relevant: true` (always)
- `csco-sign-off: true` (always — the CSCO is the owner)
- `version:` incremented at each phase update; must be ≥ 1.0.0 before Phase A gate passes

### 3.2 System Safety Goal

Established at Phase A. The overarching loss prevention objective for this engagement.

| Goal ID | Statement | Scope | Hazard Categories |
|---|---|---|---|
| SSG-001 | [e.g. "Prevent loss of data integrity, system availability, or physical harm to users"] | [System boundary as defined in AV] | [High-level hazard types] |

### 3.3 Control Structure (hierarchical, updated per phase)

A hierarchical diagram showing the control relationships between agents, systems, processes, and physical entities. Updated as each phase adds detail.

| Level | Entity | Control Actions | Feedback Mechanisms |
|---|---|---|---|
| 1 (top) | Regulatory / Policy | | |
| 2 | Organisational management | | |
| 3 | Application / System | | |
| 4 (bottom) | Physical / Data | | |

### 3.4 Unsafe Control Action (UCA) Register

| UCA ID | Controller | Control Action | UCA Type | Hazardous Condition | Phase Identified |
|---|---|---|---|---|---|
| UCA-nnn | | | Not provided / Provided incorrectly / Too early / Too late / Stopped too soon / Applied too long | | A/B/C/D/G |

**UCA Types (STPA standard):**
- **Not provided** — the control action is not taken when it should be
- **Provided incorrectly** — wrong parameters, wrong target, wrong timing
- **Too early / Too late** — timing relative to system state is wrong
- **Applied too long / Stopped too soon** — duration of control action is wrong

### 3.5 Safety Constraint Register (core deliverable)

Derived from UCAs. One or more safety constraints per UCA.

| Constraint ID | Statement | Derived From | Scope | Phase | Verification Method | Status |
|---|---|---|---|---|---|---|
| SC-nnn | [e.g. "The system must not modify shared data without acquiring an exclusive lock"] | UCA-nnn | APP-nnn / TC-nnn / BPR-nnn | A/B/C/D/G | Test ref / Architecture review / Audit | Active / Retired |

**Constraint status lifecycle:** Draft → Active (CSCO-approved) → Retired (superseded or no longer applicable, with rationale).

---

## 4. Phase-Specific Sections

### 4.1 Phase A — Safety Envelope

Added at Phase A completion. Contains:
- System safety goal (§3.2)
- Initial control structure (top two levels)
- Preliminary hazard identification
- Initial safety constraints (high-level, to be refined in subsequent phases)
- CSCO declaration of adequacy for Phase A scope

### 4.2 Phase B — Business-Level Constraints

Added at Phase B completion. Contains:
- Business process control structure additions (safety-relevant processes identified in BA)
- UCAs identified at the business process level
- Safety constraints derived for business processes
- CSCO sign-off on Phase B SCO update

### 4.3 Phase C — Information Systems Constraints

Added at Phase C completion (two sub-sections):

**Phase C — Application:**
- Application component control structure additions
- UCAs at the application interaction level (unsafe API calls, missing feedback, incorrect state transitions)
- Safety constraints for application components and interfaces
- Information security constraints (access control, data boundary)

**Phase C — Data:**
- Data flow control structure additions
- UCAs related to data integrity, confidentiality, and availability
- Safety constraints for Safety-Critical data entities
- Data governance constraints derived from safety analysis

CSCO sign-off on Phase C SCO update (covers both sub-sections).

### 4.4 Phase D — Technology Constraints

Added at Phase D completion. Contains:
- Technology component control structure additions
- UCAs at the infrastructure and platform level (deployment failures, network partitions, misconfiguration)
- Safety constraints for technology components (security architecture, resilience requirements)
- CSCO sign-off on Phase D SCO update

### 4.5 Phase G — Implementation Verification

Updated at each Solution Sprint closeout. Contains per sprint:
- Verification status of each active safety constraint
- Any new UCAs identified during implementation
- CSCO spot-check record
- CSCO sign-off on Phase G safety verification

---

## 5. Compliance Register

In addition to STAMP/STPA safety constraints, the SCO tracks regulatory and compliance obligations.

| Obligation ID | Regulation / Standard | Requirement | Applicable Scope | Verification Status | CSCO Notes |
|---|---|---|---|---|---|
| OBL-nnn | [e.g. GDPR Art. 32, ISO 27001 A.14] | | | Not started / In progress / Verified / Non-compliant | |

---

## 6. CSCO Sign-Off Register

A summary of all CSCO sign-offs, referenced throughout the SCO.

| Sign-Off ID | Phase / Gate | Date | Scope | Decision | Conditions |
|---|---|---|---|---|---|
| CSCO-SO-nnn | Phase A gate | | Safety envelope adequacy | Approved / Conditional / Rejected | |
| CSCO-SO-nnn | Phase B gate | | Business-level constraints | | |
| CSCO-SO-nnn | Phase C gate | | IS constraints | | |
| CSCO-SO-nnn | Phase D gate | | Technology constraints | | |
| CSCO-SO-nnn | Phase F gate | | Risk register and work packages | | |
| CSCO-SO-nnn | Phase G (per sprint) | | Safety acceptance | | |
| CSCO-SO-nnn | Phase G exit | | Final safety verification | | |

---

## 7. Quality Criteria

- [ ] System safety goal is stated and scoped.
- [ ] Control structure covers all in-scope systems and agents.
- [ ] Every safety-relevant component identified in AA/DA/TA has at least one UCA and one safety constraint.
- [ ] All Safety-Critical data entities have at least one data integrity constraint.
- [ ] Compliance register covers all applicable regulatory obligations.
- [ ] CSCO sign-off is recorded for every phase that introduces or modifies safety constraints.
- [ ] No Active safety constraint is unverified at Phase G exit.

---

## 8. Version History

| Version | Sprint | Phase Update | Change Summary |
|---|---|---|---|
| 0.1.0 | | A | Initial safety envelope (draft) |
| 1.0.0 | | A | Phase A gate — safety envelope baselined |
| 1.1.0 | | B | Business-level constraints added |
| 1.2.0 | | C | IS constraints added |
| 1.3.0 | | D | Technology constraints added |
| 1.x.x | | G | Phase G verification updates (per sprint) |

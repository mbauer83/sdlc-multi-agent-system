# Schema: Requirements Register (`RR`)

**Version:** 1.0.0  
**ADM Phase:** Requirements Management (cross-phase, continuous)  
**Owner:** Product Owner  
**Consumed by:** All architecture artifacts (as input), Implementation Plan, Test Strategy  

---

## 1. Purpose

The Requirements Register is the living, cross-phase record of all requirements for the engagement. It is not a static deliverable — it is updated continuously as requirements are elicited, refined, traced to architecture artifacts, or changed. It is the authoritative source for what stakeholders need, and all architecture artifacts must be traceable to at least one requirement in this register.

---

## 2. Required Sections

### 2.1 Summary Header
- `artifact-type: requirements-register`
- `safety-relevant: true` if any safety requirements are recorded
- `csco-sign-off: not-required` (PO owns; CSCO contributes safety requirements)

### 2.2 Requirements Catalog

| Req ID | Title | Type | Priority | Source Stakeholder | Description | Status | Phase Elicited | Linked Artifact |
|---|---|---|---|---|---|---|---|---|
| RR-nnn | | Functional / Non-Functional / Constraint / Safety | Must / Should / Could | STK-nnn | [Full statement] | New / Active / Changed / Retired | A/B/C/D/G/H | AV/BA/AA/DA/TA-nnn |

**Requirement types:**
- **Functional** — what the system must do
- **Non-Functional** — quality attributes (performance, security, availability, scalability)
- **Constraint** — fixed boundaries (regulatory, technology, budget, timeline)
- **Safety** — requirements derived from or contributing to the Safety Constraint Overlay

### 2.3 Requirements Traceability Matrix

Cross-reference between requirements and the architecture artifacts that satisfy them.

| Req ID | AV | BA | AA | DA | TA | IP | TS | SCO |
|---|---|---|---|---|---|---|---|---|
| RR-nnn | ● | ○ | ● | — | | | | |

Symbols: ● = primary satisfaction; ○ = partial/contributing; — = not addressed.

**Completeness rule:** Every Active requirement must have at least one ● in the matrix. Any requirement with no ● at Phase F gate is an open gap and must be resolved before Phase G entry.

### 2.4 Change Log

| Change ID | Req ID | Change Type | Description | Raised By | Sprint | Impact Assessment |
|---|---|---|---|---|---|---|
| RCH-nnn | RR-nnn | New / Modified / Retired | | | | Low / Medium / High — triggers Phase H if High |

---

## 3. Quality Criteria

- [ ] All stakeholders identified in the Architecture Vision have at least one requirement attributed to them.
- [ ] All safety requirements are cross-referenced to the Safety Constraint Overlay.
- [ ] Traceability matrix has no Active requirement with a fully empty row at Phase F gate.
- [ ] Retired requirements have documented rationale.

---

## 4. Version History

| Version | Sprint | Agent | Change Summary |
|---|---|---|---|
| 0.1.0 | | | Initial requirements elicited (Phase A) |
| 1.0.0 | | | Baselined at Phase A gate |
| 1.x.x | | | Continuous updates (each sprint) |

---
skill-id: CSCO-STAMP-STPA
agent: CSCO
name: stamp-stpa-methodology
display-name: STAMP/STPA Safety Analysis Methodology
invoke-when: >
  Referenced by all CSCO gate and incident skills as the master methodology document.
  Not directly invoked by phase events — loaded as a dependency by CSCO-GATE-A,
  CSCO-GATE-B, CSCO-GATE-C, CSCO-GATE-D, CSCO-GATE-G, CSCO-GATE-H, and CSCO-INCIDENT.
trigger-phases: [A, B, C, D, G, H]
trigger-conditions:
  - dependency of CSCO-GATE-A
  - dependency of CSCO-GATE-B
  - dependency of CSCO-GATE-C
  - dependency of CSCO-GATE-D
  - dependency of CSCO-GATE-G
  - dependency of CSCO-GATE-H
  - dependency of CSCO-INCIDENT
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-G, EP-H]
primary-outputs: [Safety Constraint Overlay, STAMP Control Structure Analysis, STPA Hazard List, UCA Record Set]
version: 1.0.0
---

# Skill Reference: STAMP/STPA Safety Analysis Methodology

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Type:** Methodology Reference — not a phase execution skill; provides procedures consumed by all CSCO gate and incident skills
**Framework References:** `agile-adm-cadence.md`, `raci-matrix.md`, `repository-conventions.md`, `algedonic-protocol.md`, `clarification-protocol.md`

---

## Inputs Required

This is a methodology reference document. The inputs below apply to each invocation of STAMP/STPA analysis across phases — the gate skills specify which artifacts are available at each phase.

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| System description (at whatever level is available) | SA architecture artifacts (AV, BA, AA, DA) or user documents for warm-start EPs | Any available description — analysis depth scales to available detail | Level 1 analysis proceeds from AV alone; Level 2 requires AA; Level 3 requires TA |
| Prior SCO version (if any) | CSCO safety-repository/safety-constraint-overlay/ | Not required for Level 1 initial analysis; required for all updates | Each phase update reads the prior phase SCO and extends it; SCO is never created from scratch after Phase A |
| Regulatory baseline | enterprise-repository/standards/ | Draft or external reference acceptable | Used to identify externally mandated safety constraints |
| Technology specifications (Level 3 only) | SwA — technology-repository/ | Baselined TA required | Level 3 analysis cannot proceed without a baselined TA |

---

## Knowledge Adequacy Check

### Required Knowledge

- **STAMP theoretical model:** Accidents result from inadequate control of safety constraints, not solely from component failures. The system must be analysed as a control problem, not a reliability problem.
- **STPA procedure:** Four-step systematic procedure (Steps 1–4 below) for identifying unsafe control actions and their causal scenarios.
- **Domain safety hazard categories:** CSCO must know the applicable hazard categories for the engagement domain (e.g., for healthcare: data loss, unauthorised access, treatment interference; for finance: data integrity loss, transaction manipulation, regulatory non-compliance; for physical systems: actuation failure, sensor failure, loss of control).
- **Regulatory standards applicable to the domain:** Determines which constraints are externally mandated (and therefore non-negotiable) vs. internally chosen (and therefore potentially subject to risk acceptance).

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Safety classification of the system (safety-critical / safety-related / non-safety) | Yes — Level 1 analysis cannot produce meaningful hazard list without classification | User (via PM) and SA | SCO §1 (System Classification), SCO §3 (Hazard List), all UCA records |
| Regulatory jurisdiction | Yes for regulated domains; no for non-safety systems | User (via PM) | SCO §2 (Regulatory Domain), compliance checklists |
| System boundary for safety analysis (which components are in scope) | Yes — control structure cannot be drawn without a system boundary | SA (AV §3.7) | STAMP Control Structure Diagram, SCO §4 (Control Structure) |
| Sensitive data categories processed (for data-level constraints) | Yes for Level 2 analysis | SA (DA data classification register) | SCO Phase C data-level constraints |
| Technology failure modes (for Level 3) | Yes for Level 3 | SwA (TA and ADR Register) | SCO Phase D technology-level constraints |

### Clarification Triggers

CSCO raises a CQ (`cq.raised` event + record in `engagements/<id>/clarification-log/`) when:

1. **Safety classification is unknown and cannot be inferred:** The system's domain and described functionality do not allow CSCO to determine whether the system is safety-critical, safety-related, or non-safety. This is a blocking CQ at Phase A — Level 1 STAMP analysis cannot produce a meaningful hazard list without this classification.
2. **Regulatory jurisdiction is unknown for a regulated domain:** The system touches a regulated domain (healthcare, finance, critical infrastructure, personal data, transport) but the applicable regulatory framework has not been identified. Blocking for compliance checklist production.
3. **System boundary is undefined:** SA's AV §3.7 does not define a safety analysis boundary, and CSCO cannot infer one from the available artifacts. Blocking for control structure analysis.
4. **Hazard cannot be constrained:** Level 1 or Level 2 analysis identifies a hazard for which CSCO cannot identify a feasible safety constraint (no known architecture pattern prevents the hazard). This triggers ALG-001, not a CQ.

---

## Steps: How to Apply STAMP/STPA

This section defines the STAMP/STPA procedure as applied by CSCO across phases. Gate skills reference specific steps from this procedure. The steps below are the canonical method; gate skills indicate which steps apply at each phase.

---

### Step 0 — Discovery Scan

Before beginning any STAMP/STPA work for a phase or incident, execute the Discovery Scan per `framework/discovery-protocol.md §2`:

- **Layer 1 — Engagement State:** Read engagement-profile.md; read all available SCO versions in safety-repository/; read all available SA artifacts in architecture-repository/; read SwA artifacts in technology-repository/ (if available); read QA and DevOps artifacts (if available); read all open CQs in clarification-log/.
- **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for applicable regulatory standards; read enterprise-repository/reference-library/ for relevant safety patterns.
- **Layer 3 — External Sources:** Check external-sources/ for configured source adapters (e.g., regulatory databases, compliance frameworks).
- **Layer 4 — Target Repository:** If target-repo is configured, check for any safety-relevant documentation in the codebase (e.g., security policies, compliance certifications, existing safety analysis documents).
- **Layer 5 — Inference:** For each required SCO field that cannot be sourced from Layers 1–4, apply domain-knowledge inference. Annotate every inferred field with `[inferred — source: domain knowledge]`. Do not raise a CQ for an item that can be reasonably inferred from the engagement domain.

---

### Step 1 — Define System-Level Losses

A **loss** is an outcome that is unacceptable to the system's stakeholders. Losses are defined at the highest level of abstraction — they describe *what must not happen*, not *how it might happen*.

**Loss identification procedure:**

1. Read the engagement scope statement (from AV or engagement-profile.md).
2. Read the stakeholder register (from AV §3.3 or equivalent). For each stakeholder category, identify what loss would harm that stakeholder.
3. Read the regulatory domain (from SCO §2 if already drafted, or from enterprise-repository/standards/). Regulatory non-compliance is always a loss.
4. Enumerate losses as L-nnn (L-001, L-002, ...):

**Loss record format:**
```
L-nnn: [Brief noun phrase describing the unacceptable outcome]
  Description: [One to two sentences — what happened, who is harmed, why it is unacceptable]
  Stakeholders affected: [List of stakeholder IDs or categories]
  Regulatory implication: [Name of regulation or standard if applicable, or "None identified"]
```

**Canonical loss categories to consider for every engagement:**
- Loss of human life or physical harm
- Loss of critical data (irreversible or irretrievable)
- Loss of system availability in a critical period
- Regulatory non-compliance (fine, sanction, licence revocation)
- Financial loss beyond defined threshold
- Privacy breach (unauthorised disclosure of personal data)
- Loss of system integrity (corrupted outputs accepted as correct)
- Loss of mission-critical business operations

Not all categories apply to every engagement. Document which categories are applicable and which are not (with brief rationale for exclusions).

---

### Step 2 — Identify System-Level Hazards

A **hazard** is a system state or set of conditions that, given certain worst-case environmental conditions, will lead to a loss. Hazards are system states — not causes, not failures, not scenarios.

**Hazard identification procedure:**

1. For each Loss L-nnn: identify the system states that could lead to that loss given worst-case conditions.
2. Assign hazard identifiers H-nnn (H-001, H-002, ...).
3. Map each hazard to one or more losses (H→L traceability).

**Hazard record format:**
```
H-nnn: [Brief description of the hazardous system state]
  Definition: [Precise description — what is the system doing (or not doing), what state is it in]
  Leads to loss: [L-nnn, L-nnn, ...]
  Worst-case environment: [Description of environmental conditions that convert this state into a loss]
```

**Hazard vs Cause distinction (critical):** "The encryption key is exposed to an unauthenticated actor" is a hazard (a system state). "The developer forgot to apply authentication middleware" is a cause. STPA identifies hazards in Steps 1–3 and causes in Step 4. Mixing these at this stage produces an analysis that misses hazard categories.

---

### Step 3 — Identify Safety Constraints

A **safety constraint** is a system-level requirement that must be satisfied to prevent hazards from occurring. Safety constraints are the authoritative content of the Safety Constraint Overlay.

**Constraint authoring procedure:**

For each hazard H-nnn: formulate the safety constraint that prevents the hazardous state from arising. The constraint describes what the system must enforce, not how it enforces it.

**Safety constraint format:**
```
SC-nnn: The system shall [mandatory action or mandatory prohibition] in order to prevent [H-nnn: hazard description].
  Constraint type: [Architectural | Operational | Technical | Regulatory]
  Phase introduced: [A | B | C | D]
  Applies to: [component IDs, interface IDs, or system-wide]
  Rationale: [Why this constraint prevents the hazard — one sentence]
  Verification: [How compliance with this constraint will be verified — reference to test type or review artifact]
```

**Constraint types:**
- **Architectural:** The constraint must be satisfied by the architecture design (SA domain). Verified by CSCO at Phase A/B/C/D gate review.
- **Operational:** The constraint must be satisfied by operational procedures (DevOps/PM domain). Verified by CSCO at Phase G.
- **Technical:** The constraint must be satisfied by a specific technology control (SwA domain). Verified by CSCO at Phase D gate review.
- **Regulatory:** Constraint is externally mandated by a named regulation or standard. Non-negotiable; verified by Compliance Assessment (QA) at Phase G.

**Constraint authoring rules:**
- One constraint per hazard minimum. Multiple constraints per hazard are permitted when a single constraint is insufficient.
- Constraints must be falsifiable — it must be possible to determine, from examining an artifact or implementation, whether the constraint is satisfied or violated.
- Constraints must be technology-independent at Phase A and B. Technology-specific constraints are added at Phase C (application-level) and Phase D (technology-level).

---

### Step 4 — Build Control Structure Diagram

The **control structure** maps the control relationships in the system: which agent, component, or process controls what, and through what mechanism.

**Control structure procedure:**

1. Identify all controllers in the system (entities that issue commands or control actions). At Level 1: identify organisational/role-level controllers. At Level 2: identify software component-level controllers. At Level 3: identify technology-level controllers (databases, message brokers, authentication systems, etc.).
2. Identify all controlled processes (entities that receive control actions and execute them).
3. For each controller→controlled process relationship: identify the control actions (what the controller can do) and the feedback channels (what information the controller receives about the controlled process's state).
4. Produce a control structure diagram in text form (CSCO produces a structured table; a visual diagram is recommended but not required as a text artifact):

**Control structure table format:**
```
| Controller | Control Action | Controlled Process | Feedback Channel |
|---|---|---|---|
| [Role/Component] | [Action verb + object] | [Process/Component] | [Information returned] |
```

---

### Step 5 — Identify Unsafe Control Actions (UCAs)

An **Unsafe Control Action (UCA)** is a control action that, in a specific context, violates a safety constraint. STPA identifies UCAs by systematically applying four UCA types to each control action identified in the control structure.

**Four UCA types (apply all four to every control action):**

| UCA Type | Description |
|---|---|
| Not Provided | The control action is not provided when it should be |
| Provided When Not Needed | The control action is provided when it should not be |
| Provided Too Early / Too Late | The control action is provided at the wrong time |
| Applied Too Long / Stopped Too Soon | The control action is applied for too long or stopped too soon |

**UCA record format:**
```
UCA-nnn: [Controller] [UCA type] [Control Action] in context [Context C], leading to [H-nnn: hazard].
  Controller: [Component or role ID]
  UCA type: [not-provided | provided-unsafe | wrong-timing | wrong-duration]
  Control action: [Exact control action from control structure]
  Context: [The specific scenario or system state in which this UCA is hazardous]
  Hazard link: [H-nnn]
  Loss link: [L-nnn]
  SCO constraint: [SC-nnn — the constraint that this UCA violates]
```

**Analysis depth by phase:**

- **Level 1 (Phase A/B):** UCAs at the system boundary and role-level control actions. Focus on: who controls what at the business and architecture level; which organisational control actions could fail.
- **Level 2 (Phase C):** UCAs at the application component level. Focus on: which component-to-component control actions are safety-relevant; which API interactions could violate safety constraints.
- **Level 3 (Phase D):** UCAs at the technology level. Focus on: which technology control mechanisms (authentication, authorisation, encryption, retry logic, circuit breakers) could fail or produce unsafe outcomes.

---

### Step 6 — Identify Loss Scenarios

A **loss scenario** is a causal factor that leads to a UCA occurring. Loss scenarios explain *why* the UCA might happen — they point to root causes at the implementation or design level.

**Loss scenario causal factor categories:**

1. **Controller failure:** The controller itself fails (software bug, hardware failure, incorrect logic).
2. **Inadequate control algorithm:** The controller's logic does not account for a specific context.
3. **Incorrect process model:** The controller has an incorrect internal model of the controlled process's state (stale information, incorrect sensor reading, delayed feedback).
4. **Communication path failure:** The control action or feedback is lost, corrupted, or delayed in transmission.
5. **Environmental disturbance:** An external factor changes the state of the controlled process independently of the controller.

**Loss scenario record format:**
```
LS-nnn: [Brief description of the scenario]
  UCA link: [UCA-nnn]
  Causal type: [Controller failure | Control algorithm | Process model | Communication | Environment]
  Causal description: [Precise description of the causal factor — one to three sentences]
  SCO mitigation: [SC-nnn — the constraint that mitigates this scenario, or "PROPOSED NEW: [constraint text]"]
```

When a loss scenario does not have an existing SCO constraint that mitigates it, CSCO must author a new SC-nnn constraint to address it.

---

## Safety Constraint Overlay (SCO) Structure and Update Procedure

The SCO is the master safety artifact. It is updated at each phase and each significant change event.

### SCO Document Structure

```markdown
---
sco-id: SCO-<phase>-<version>
engagement-id: <engagement-id>
phase: <A | B | C | D | G | H>
version: <semantic version>
status: draft | baselined
csco-sign-off: true | false
previous-version: <prior SCO artifact path>
---

# Safety Constraint Overlay — Phase <phase>

## §1 System Safety Classification
[safety-critical | safety-related | non-safety]
[Classification rationale — one paragraph]

## §2 Regulatory Domain
[Applicable standards and regulations, each on its own line]
[For each standard: jurisdiction, authority, applicability rationale]

## §3 System-Level Losses
[L-nnn entries per Step 1 above]

## §4 System-Level Hazards
[H-nnn entries per Step 2 above]

## §5 Safety Constraints
[SC-nnn entries per Step 3 above — cumulative across phases]

## §6 Control Structure
[Control structure table per Step 4 above — updated per phase]

## §7 Unsafe Control Actions
[UCA-nnn entries per Step 5 above — cumulative across phases]

## §8 Loss Scenarios
[LS-nnn entries per Step 6 above]

## §9 Compliance Requirements
[Per regulatory domain — one section per standard]
[Each section: applicable articles/clauses → SC-nnn mapping]

## §10 Open Safety Findings
[Safety issues identified but not yet resolved — tracked with status]
[Format: SF-nnn: [Description] | Status: open/accepted/resolved | Owner: [agent]| SC-nnn affected]

## §11 Phase Gate Summary
[Per gate: gate ID, result, SCO constraints verified, veto references if any]
```

### SCO Update Procedure

Each gate skill specifies which SCO sections to update. The general procedure is:

1. **Read the prior SCO version** from `safety-repository/safety-constraint-overlay/`.
2. **Retain all prior content** — SCO updates are additive. Do not remove prior entries unless they are explicitly superseded by a revised entry (and the supersession is documented with a `supersedes: SC-nnn` field in the new constraint).
3. **Add phase-specific content** in the appropriate sections.
4. **Increment the version** per semantic versioning: minor increment (0.x.0) for draft additions; major increment (x.0.0) for baselines after gate review completion.
5. **Emit `artifact.baselined`** with the new SCO version path.
6. **Write the gate record** in `safety-repository/gate-records/gr-<gate-id>-<version>.md`.

---

## Gate Review Procedure

All CSCO gate skills follow this common gate review structure (gate-specific steps are added by each gate skill):

### Gate Review Common Procedure

**GR-1: Confirm artifact is baselined.** Do not begin formal review until `artifact.baselined` is emitted by the owning agent. Confirm the artifact version is 1.0.0 or higher.

**GR-2: Read the artifact in full.** Read every section of the artifact being gated. Do not assume prior review is sufficient — gate review is always performed on the current baselined version.

**GR-3: Load applicable SCO constraints.** Identify all SC-nnn constraints in the current SCO that apply to this phase and artifact type. Produce a checklist of applicable constraints.

**GR-4: Evaluate each constraint against the artifact.** For each SC-nnn in the checklist: determine whether the artifact satisfies, partially satisfies, or violates the constraint. For partial satisfaction: determine whether a conditional veto is appropriate (evidence needed) or a veto is appropriate (constraint is violated).

**GR-5: Perform phase-specific STAMP analysis.** Apply the STPA analysis level appropriate for this phase (Level 1 for Phase A/B, Level 2 for Phase C, Level 3 for Phase D). Identify new UCAs or update existing ones.

**GR-6: Update SCO.** Add new constraints, UCAs, and loss scenarios identified during the review.

**GR-7: Cast gate vote.** Emit `gate.vote_cast` with result (approve | veto | conditional) and mandatory fields.

### Gate Vote Format

```yaml
gate-vote:
  gate-id: <gate ID, e.g. A-B>
  phase-from: <phase>
  phase-to: <phase>
  result: approve | veto | conditional
  sco-version: <SCO artifact ID reviewed>
  # For veto:
  sco-ref: SC-nnn
  violation-description: >
    [Precise description of what the artifact says and how it violates SC-nnn]
  remediation-path: >
    [Minimum change required to the artifact for CSCO to approve: specific section, specific revision needed]
  # For conditional:
  evidence-required: >
    [What evidence must be provided]
  evidence-source: <agent responsible for producing evidence>
  evidence-deadline: <sprint identifier>
  # For approve:
  constraints-verified: [SC-nnn, SC-nnn, ...]
  notes: >
    [Any residual concerns, accepted risks, or advisory items — not blocking]
```

---

## Feedback Loop

This is a methodology reference document. Individual gate skills govern their own feedback loops. The general feedback loop constraint applicable to all CSCO skills is:

**Maximum iterations before PM escalation: 2.**

- **Iteration 1:** CSCO casts veto with named SC-nnn constraint and remediation path. Owning agent revises artifact and re-baselines.
- **Iteration 2:** CSCO reviews revised artifact. If constraint is satisfied: approve. If constraint is still violated: cast second veto with updated analysis.
- **After Iteration 2 without resolution:** CSCO raises `ALG-010` (inter-agent deadlock) to PM. PM adjudicates within the current sprint. If PM cannot resolve: PM escalates to user. CSCO veto stands throughout adjudication.

**Termination conditions:**
- **Satisfied:** The artifact revision satisfies the named SC-nnn constraint. CSCO emits `gate.vote_cast (approve)`. Feedback loop closes.
- **User risk acceptance:** User (via PM) explicitly accepts the residual risk in the PM decision log. CSCO updates SCO to reflect accepted residual risk. CSCO emits `gate.vote_cast (approve with documented acceptance)`. Feedback loop closes.
- **Escalated:** PM or user overrides CSCO veto (with documented risk acceptance). CSCO records the override in the SCO §10 Open Safety Findings and in the gate record. Feedback loop closes, but CSCO retains the finding as a tracked open item.
- **Deadlock:** ALG-010 raised; feedback loop transfers to PM arbitration.

---

## Algedonic Triggers

This is a methodology reference document. Algedonic triggers for specific conditions are defined in each gate skill and in `skills/incident-response.md`. The following triggers apply to all CSCO safety analysis work regardless of phase:

- **ALG-001 (S1 — Safety-Critical):** A hazard is identified for which no feasible safety constraint exists within the proposed architecture approach. Raised immediately; concurrent escalation to PM. Example: a safety-critical system where no isolation mechanism is architecturally possible.
- **ALG-016 (S2 — Knowledge Gap):** A safety-critical Clarification Request has remained unanswered for more than two sprint cycles. Raised to PM for consolidation and user escalation.
- **ALG-017 (S1 — Knowledge Gap):** A safety-domain knowledge gap exists where an assumption cannot safely be made — for example, the regulatory jurisdiction is unknown for a system that appears to be safety-critical. Raised to user via PM; CSCO concurrent; halt affected phase work.

---

## Outputs

| Artifact | Artifact ID Format | Destination | Notes |
|---|---|---|---|
| Safety Constraint Overlay (per phase) | `SCO-<phase>-<version>.md` | `safety-repository/safety-constraint-overlay/` | Cumulative; each phase produces a new version |
| STAMP/STPA Analysis Document | `sa-<id>-<phase>.md` | `safety-repository/stamp-stpa/` | One document per phase containing L-nnn, H-nnn, SC-nnn, UCA-nnn, LS-nnn records |
| Gate Review Record | `gr-<gate-id>-<version>.md` | `safety-repository/gate-records/` | One record per gate per review iteration |
| Compliance Checklist | `cl-<domain>-<version>.md` | `safety-repository/compliance-checklists/` | One checklist per regulatory domain identified |

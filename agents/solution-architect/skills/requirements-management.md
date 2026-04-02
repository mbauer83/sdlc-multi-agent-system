---
skill-id: SA-REQ-MGMT
agent: SA
name: requirements-management
display-name: Requirements Management (Cross-Phase)
invoke-when: >
  Activated at every phase boundary (A, B, C, H) to verify traceability, or immediately when
  PO baselines a new RR version and SA-owned artifacts may be affected.
trigger-phases: [req-mgmt, A, B, C, H]
trigger-conditions:
  - artifact.baselined (artifact-type=requirements-register)
  - sprint.closed (any architecture sprint)
  - cq.answered (RR-related clarifications resolved)
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-E, EP-F, EP-G, EP-H]
primary-outputs: [RTM Architecture Column Contribution]
version: 1.0.0
---

# Skill: Requirements Management (Cross-Phase)

**Agent:** Solution Architect  
**Version:** 1.0.0  
**Phase:** Requirements Management (continuous — activated at each phase boundary)  
**Skill Type:** Cross-phase consulting — no primary artifact production; architecture column contribution only  
**Framework References:** `agile-adm-cadence.md §5.10`, `framework/artifact-schemas/requirements-register.schema.md`, `raci-matrix.md §3.11`, `clarification-protocol.md`, `algedonic-protocol.md`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Requirements Register (`RR`) — current version | Product Owner | Current iteration (PO is accountable; SA reads only) | SA reads RR at each phase boundary; never writes to it directly |
| Current SA architecture artifacts (AV, BA, AA, DA) | SA (self-produced) | Latest baselined version for each phase completed | SA compares RR requirements against architecture elements |
| Requirements Traceability Matrix (`RTM`) — current version | Product Owner (accountable) | Current version; SA contributes architecture column only | SA writes to the architecture column; PO maintains the full RTM |
| Change notifications from PO (RR version updates) | Product Owner | `artifact.baselined` event on RR with incremented version | SA monitors for RR version changes that may require SA artifact updates |
| `sprint.started` event (for the sprint in which this skill is invoked) | PM | Emitted | Required before SA performs cross-phase traceability work |

---

## Knowledge Adequacy Check

### Required Knowledge

- The complete set of architecture elements across all baselined SA artifacts: every DRV-nnn, CAP-nnn, BPR-nnn, APP-nnn, DE-nnn that has been produced to date.
- The current state of the RR: every RR-nnn entry, its type, priority, status, and current linked artifact field.
- The RTM's architecture column: which requirements are already mapped to SA architecture elements.
- RACI distinction: SA contributes *the architecture column* of the RTM. SA does not determine whether a requirement is satisfied overall — SA determines whether a requirement is satisfied *at the architecture layer*. Satisfaction at implementation layer is DE/QA responsibility.

### Known Unknowns

| Unknown | Blocking | CQ Target | Action |
|---|---|---|---|
| A requirement that cannot be mapped to any SA architecture element — the requirement appears to be about an out-of-scope domain | No — flag to PO as a potential scope gap; do not block SA architecture work | PO | Flag to PO; note in RTM contribution as "Architecture layer: no mapping — potential scope gap" |
| A requirement whose meaning is ambiguous enough that it could trace to two different architecture elements (e.g., CAP-001 or CAP-002) | No — SA makes a reasoned tracing decision; documents reasoning in RTM contribution note | — | Internal decision; no CQ required |
| A requirement in the RR that conflicts with an architecture principle in the PR | No — flag to PM as a potential ALG-010 condition; trace to the conflicting principle; document the conflict | PM | Flag to PM; note in RTM contribution |

### Clarification Triggers

SA raises a CQ when:

1. **Unresolvable requirement gap:** A requirement in the RR cannot be mapped to any existing or planned SA architecture element, AND cannot be attributed to a missing PR or architecture gap — the requirement appears to reference an entirely out-of-scope domain. SA raises a CQ to PO: "Requirement RR-[id] cannot be traced to any architecture element in scope. Is this requirement in scope for this engagement? If yes, which domain does it address?"
2. **Requirement version advance without corresponding SA artifact update:** The PO has released a new RR version (RR 1.x.x → 1.y.x) with changes that affect requirements already traced to SA artifacts, but SA has not been notified. SA cannot complete the RTM architecture column for the new RR version without understanding what changed. SA raises a CQ to PO: "RR has advanced from version [old] to [new]. Which requirements have changed status or content? Specifically, have any requirements linked to [affected artifact IDs] been modified or retired?"

---

## Procedure

This skill is **activated at each phase boundary** — specifically, at the close of each Architecture Sprint before the corresponding phase gate is evaluated. It is also activated immediately when SA detects that the RR version has advanced (via `artifact.baselined` event on the RR).

---

### Step 1 — Scan RR at Phase Boundary

At the close of each Architecture Sprint (Phase A, B, C, H):

1. Read the current version of the RR from `work-repositories/safety-repository/` — wait, the RR is PO-owned. Read from the path where PO maintains it (per `repository-conventions.md` — PO's work-repository path). Do NOT write to PO's repository.
2. Build a working list: every RR-nnn entry with `Status: Active` or `Status: Changed`.
3. Exclude: `Status: Retired` entries (no longer require tracing); `Status: New` entries that were added in the current sprint (may not yet have architecture coverage — flag but do not block gate).

---

### Step 2 — Verify Traceability Chain Completeness

For each active RR-nnn, verify that the architecture traceability chain is complete for the phases executed so far:

**Complete traceability chain (full-cycle standard):**
```
RR-nnn → AV.DRV-nnn (or AV capability cluster) → BA.CAP-nnn → AA.APP-nnn → DA.DE-nnn
```

**Phase-appropriate completeness:**
- After Phase A only: RR-nnn must trace to at least one AV element (DRV-nnn or capability cluster). No BA/AA/DA tracing required yet.
- After Phase B: RR-nnn must trace to at least one AV element AND at least one BA element (CAP-nnn or BPR-nnn).
- After Phase C: RR-nnn must trace to AV, BA, and at least one AA or DA element.
- At Phase F gate: all active requirements must have a complete chain (AV → BA → AA → DA → TA, with the TA column contributed by SwA).

**Tracing rules:**
- A requirement may trace to multiple architecture elements at the same level (a single requirement may realise multiple capabilities — record all).
- A requirement must have at least one **●** (primary satisfaction) mapping in the RTM architecture column. If the SA can only assign **○** (partial), note the gap — a requirement with only **○** mappings has no primary architecture element responsible for it, which is a gap.
- Safety requirements (`Type: Safety`) in the RR must trace to at least one SCO cross-reference in addition to the standard SA artifact chain.

---

### Step 3 — Flag Untraced Requirements to PO

For each active RR-nnn where the traceability chain is incomplete at the appropriate phase-completeness level:

1. Write a note to the RTM architecture column: "Untraced at [Phase X boundary] — [reason: no matching architecture element / architecture element not yet produced / potential scope gap]."
2. Send a structured feedback message to PO (via handoff log or CQ, depending on whether PO clarification is needed):
   - If the gap is likely a missing architecture element (SA's work is incomplete): SA notes it as a self-action item — produce the missing element before gate.
   - If the gap is likely a scope gap (the requirement refers to an out-of-scope domain): raise CQ to PO (see Clarification Triggers).
   - If the gap is likely a phase sequencing issue (the relevant phase has not yet been executed): note it as "tracing deferred to Phase X" and do not flag as a gap.

---

### Step 4 — Flag Requirements Conflicting with Architecture Principles

For each active RR-nnn:

1. Check whether the requirement's constraint imposes a specific technology, platform, or architectural pattern that conflicts with the PR.
   - Example: RR-nnn states "The system must use [specific database product]." The PR states "Technology independence: architecture artifacts must not prescribe specific products." Conflict: the requirement prescribes a product at the requirements level.
   - Example: RR-nnn states "All components must be deployed on a single server." The PR (or AV) implies a distributed architecture for availability. Conflict: the deployment constraint conflicts with the capability design.
2. For each conflict identified: write a note in the RTM architecture column identifying the conflict by principle ID (P-nnn) and requirement ID (RR-nnn).
3. Notify PM: create a structured message (not an algedonic signal unless the conflict is severe) flagging the conflict for PM adjudication. PM decides: either the PR must be updated (SA drafts the update; PM gates it) or the RR requirement must be revised (PO authority).
4. If the conflict involves a safety requirement and an architecture principle, raise `ALG-010` directly — the conflict is between two authoritative inputs with different accountable agents, which is the definition of an inter-agent deadlock.

---

### Step 5 — Assess RR Version Advance for SA Artifact Impact

When SA detects that the PO has baselined a new RR version (via `artifact.baselined` event for the RR):

1. Identify which RR-nnn entries have changed status or content since the previous version.
2. For each changed RR-nnn: determine which SA architecture element it traces to.
3. For each affected SA architecture element: assess whether the requirement change requires a change to the architecture element.
   - **No change required:** The requirement change is clarifying or non-material. Update the RTM architecture column note. No architecture artifact change needed.
   - **Change required (minor):** The requirement change requires a patch update to an SA artifact (e.g., a description clarification). SA updates the artifact; increments patch version; emits `artifact.baselined`.
   - **Change required (significant or major):** The requirement change requires a structural modification to an SA artifact. SA initiates Phase H procedure (`skills/phase-h.md`). SA does not unilaterally modify a baselined architecture artifact without a Phase H Change Record authorising the change.

4. For requirements that have been `Retired` in the new RR version: check whether any SA architecture element exists *solely* to satisfy that requirement. If yes, that architecture element may now be out-of-scope — flag to PM for scope review. Do not unilaterally retire architecture elements.

---

### Step 6 — Maintain RTM Architecture Column

At each phase boundary and after each RR version advance assessment:

1. Produce an updated RTM architecture column contribution for the current phase state.
2. The RTM architecture column covers: AV, BA, AA, DA columns (as applicable to phases completed).
3. Format: per `framework/artifact-schemas/requirements-register.schema.md §2.3` — each RR-nnn row; ● = primary satisfaction at this architecture layer; ○ = partial/contributing; — = not addressed at this layer.
4. Submit the RTM architecture column contribution to PO via handoff: `handoff-type: rtm-architecture-contribution`.
5. PO integrates SA's contribution into the full RTM (PO is accountable for the complete RTM).

**Staleness detection:** If the SA's last RTM contribution was produced for RR version X, and the current RR is at version X+2 or higher, SA must immediately produce a new RTM contribution for the current version. Staleness by 2 or more RR versions is a gap to be flagged to PM.

---

## Feedback Loop

### SA ↔ PO (Traceability Gap Resolution)

- **Iteration 1:** SA flags untraced requirements or conflicting requirements to PO via the RTM architecture column contribution notes. PO reviews; either clarifies the requirement (which may resolve the gap) or acknowledges the gap and raises a new RR entry to address it.
- **Iteration 2:** SA reviews PO's response; updates RTM architecture column; confirms gap resolution or escalates.
- **Termination:** All active requirements have traceable architecture elements at the phase-appropriate level. Remaining gaps are documented as assumptions with PM acceptance.
- **Max iterations:** 2 per phase boundary.
- **Escalation:** If a gap persists after 2 iterations and it involves a safety requirement: raise `ALG-016` (CQ unanswered). If the gap is not safety-related but creates scope creep: raise `ALG-016` to PM for scope gate decision.

### SA ↔ PM (Principle-Requirement Conflict Resolution)

- **Iteration 1:** SA flags conflict to PM with both positions described. PM reviews; consults the relevant accountable agents (PO for RR, SA for PR); determines which must change.
- **Iteration 2:** SA or PO implements the decision; SA confirms consistency.
- **Termination:** Conflict resolved; RTM architecture column updated.
- **Max iterations:** 2.
- **Escalation:** If unresolved (e.g., PO insists on a technology prescription that violates the PR, and SA cannot find an acceptable compromise), PM escalates to user as a policy decision.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-010 | A requirement in the RR conflicts with an architecture principle in the PR, and both the PO and SA hold positions that cannot be reconciled through structured feedback — creating an inter-agent deadlock on a governance matter | S3 | Emit `alg.raised`; PM adjudicates; SA documents both positions in the RTM architecture column with a `conflict: unresolved` flag until PM decision is received |
| ALG-016 | A requirement change that significantly expands the scope of SA's architecture work (adds new capability domains, requires new Phase B or Phase C artifacts) has been introduced via RR without a corresponding PM scope gate decision | S2 | Emit `alg.raised`; PM performs scope gate assessment; SA does not begin architecture work for the expanded scope until PM confirms the scope change and plans the corresponding sprints |

---

## Outputs

| Output | Path | Version | EventStore Event |
|---|---|---|---|
| RTM Architecture Column Contribution | Submitted to PO via handoff; PO integrates into `requirements-register/rr-<version>.md` | Per RR version being updated | `handoff.created` |
| Gap report to PM (untraced requirements; staleness alerts) | Recorded in sprint log or structured message to PM | — | Included in sprint closeout record |
| Phase-specific gap assessment (formal, if requested by PM) | `architecture-repository/` — SA working note, not a standalone artifact | 0.1.0 working document | Not separately baselined |
| Phase H trigger (if RR change requires significant SA artifact update) | Initiates `skills/phase-h.md` | — | Phase H sprint initiated by PM on SA's recommendation |

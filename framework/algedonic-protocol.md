# Algedonic Protocol

**Version:** 1.1.0  
**Status:** Approved — Foundation  
**Owner:** Project Manager  
**Last Updated:** 2026-04-02

---

## 1. Purpose and Theoretical Basis

The term *algedonic* is taken from Stafford Beer's Viable System Model (VSM). An algedonic signal is a **fast-path escalation** that bypasses normal hierarchical communication channels when a condition is too urgent or too severe to be handled at the operating level within the normal feedback loop cycle. It travels directly to the decision authority capable of acting on it, regardless of where it originates in the agent hierarchy.

In this system, an algedonic signal is not a general-purpose error flag. It is a precisely scoped mechanism reserved for conditions where:

- Continued normal operation risks harm that cannot be reversed within the current sprint, or
- A blocking condition makes normal ADM progression impossible, and the standard two-iteration feedback loop has been or would certainly be exhausted without resolution, or
- A safety, regulatory, or governance constraint has been or is at imminent risk of being violated.

Every skill file in this system must contain an `## Algedonic Triggers` section. The explicit statement that no algedonic triggers apply to a given skill is itself a design decision and must be present.

---

## 2. Trigger Taxonomy

Algedonic triggers are classified across four severity levels and five categories.

### 2.1 Severity Levels

| Level | Name | Response Expectation |
|---|---|---|
| **S1** | Critical | Immediate halt of affected work; escalation within the current agent invocation |
| **S2** | High | Escalation before the next sprint unit begins; current work may continue in a constrained mode |
| **S3** | Elevated | Escalation at the current sprint boundary; work continues with documented risk acceptance |
| **S4** | Advisory | PM notified for awareness; no work halt; tracked as an open issue |

### 2.2 Trigger Categories

| Category | Code | Description |
|---|---|---|
| **Safety-Critical** | `SC` | An action, artifact, or decision has created or is about to create a condition where a safety constraint defined in the Safety Constraint Overlay (`SCO`) may be violated |
| **Regulatory Breach** | `RB` | An artifact, decision, or implementation is non-compliant with a regulatory, legal, or contractual obligation identified during any ADM phase |
| **Timeline Collapse** | `TC` | A dependency failure, unresolvable blocking issue, or cascade of open items makes it impossible to progress through the current phase gate within a reasonable number of sprint extensions |
| **Governance Violation** | `GV` | An agent has written outside its designated repository path, consumed a draft artifact as authoritative, bypassed a phase gate, or taken an action that contravenes the RACI matrix |
| **Inter-Agent Deadlock** | `IA` | The two-iteration feedback loop between two agents has been exhausted without resolution and PM adjudication is required |
| **Knowledge Gap — Unresolvable** | `KG` | A Clarification Request (`CQ`) has remained unanswered for more than two sprint cycles, or the missing knowledge is safety-critical and cannot be safely assumed |

---

## 3. Trigger Classification Table

The following table enumerates specific triggering conditions, their classification, and their default escalation target.

| ID | Condition | Category | Severity | Default Escalation Target |
|---|---|---|---|---|
| `ALG-001` | Any implementation or architecture decision would violate a safety constraint in the current `SCO` | SC | S1 | CSCO (immediate); PM (concurrent) |
| `ALG-002` | CSCO is unavailable and a safety-relevant gate review is required to unblock work | SC | S1 | PM (halt work; do not proceed without CSCO) |
| `ALG-003` | An artifact is discovered to violate a regulatory or compliance obligation not previously identified | RB | S1 | CSCO (immediate); PM (concurrent) |
| `ALG-004` | A phase gate evaluation cannot be completed because a required CSCO sign-off is overdue | SC/RB | S2 | PM (escalate to CSCO with deadline) |
| `ALG-005` | A phase has required two consecutive gate extensions and is still not passing | TC | S2 | PM (assess scope change or reset) |
| `ALG-006` | A dependency between two phases or two agents cannot be resolved within the current sprint | TC | S2 | PM (restructure sprint plan) |
| `ALG-007` | An agent has written an artifact to a repository path it does not own | GV | S1 | PM (halt; assess impact; correct immediately) |
| `ALG-008` | A draft artifact (version 0.x.x) has been consumed as authoritative input to a binding output | GV | S2 | PM (invalidate output; identify root cause) |
| `ALG-009` | An Architecture Contract has been created without the required CSCO sign-off for a safety-relevant work package | GV | S1 | CSCO (immediate); PM (concurrent) |
| `ALG-010` | The two-iteration artifact feedback loop has been exhausted without resolution | IA | S3 | PM (adjudicate within current sprint) |
| `ALG-011` | A consuming agent identifies that a baselined artifact is internally inconsistent or contradicts another baselined artifact | IA | S3 | Producing agent (immediate revision request); PM if unresolved |
| `ALG-012` | An agent detects that a CSCO veto has been overridden or ignored | SC/GV | S1 | PM (immediate halt); CSCO (notify) |
| `ALG-013` | Test execution reveals a defect in a safety-relevant component with Severity 1 classification | SC | S1 | CSCO (immediate); SwA (halt deployment) |
| `ALG-014` | A change request is classified as Safety-Critical but no CSCO is available to review it | SC | S1 | PM (halt change; document; await CSCO) |
| `ALG-015` | Sprint log, governance checkpoint, or handoff log has not been updated for two consecutive sprint closings | GV | S4 | PM (self-alert; remediate) |
| `ALG-016` | A Clarification Request (`CQ`) to the user has been open for more than two sprint cycles with no response | KG | S2 | PM (consolidate CQs; escalate to user as priority interaction) |
| `ALG-017` | A safety-domain knowledge gap is identified where an assumption cannot safely be made (e.g., unknown regulatory jurisdiction affecting a safety-critical system) | KG | S1 | User (via PM); CSCO (concurrent); halt affected phase work |
| `ALG-018` | An agent has proceeded without raising a required CQ, producing an artifact that rests on undocumented assumptions | KG/GV | S2 | PM (invalidate affected sections; require CQ retroactively) |
| `ALG-C01` | Diagram catalog inconsistency: duplicate `element_id` or name collision detected within an ontological sub-catalog | GV | S3 | SA (resolve immediately; regenerate `_macros.puml`; validate all affected diagrams) |
| `ALG-C02` | A non-SA agent has written directly to `diagram-catalog/` without going through `catalog_propose` handoff | GV | S2 | PM (halt; SA to review and reconcile; non-SA agent to be re-briefed on write-authority rules) |
| `ALG-C03` | Cross-ontology link broken: a `canonical_entity` or `linked_data_entity` field references a `DE-nnn` or `BOB-nnn` ID that does not exist in the relevant sub-catalog | GV | S3 | SA (locate missing element; create or correct cross-reference; re-validate affected diagrams) |
| `ALG-C04` | `_macros.puml` is out of sync with the `elements/` sub-catalogs: a PUML diagram references a macro alias that is not defined in `_macros.puml`, or `_macros.puml` defines an alias for a non-existent element | GV | S3 | SA (regenerate `_macros.puml`; run `validate_diagram` on all affected diagrams before next render) |

---

## 4. Escalation Target Map

### 4.1 Primary Escalation Targets

| Condition Category | Primary Target | Secondary Target | Tertiary Target |
|---|---|---|---|
| Safety-Critical (`SC`) | CSCO | PM | (halt work) |
| Regulatory Breach (`RB`) | CSCO | PM | (halt work) |
| Timeline Collapse (`TC`) | PM | Phase-owning SA or SwA | — |
| Governance Violation (`GV`) | PM | Affected artifact owner | CSCO (if safety-relevant) |
| Inter-Agent Deadlock (`IA`) | PM | Both parties | CSCO (if safety-relevant) |
| Knowledge Gap — Unresolvable (`KG`) | **User** (via PM-structured interaction) | CSCO (if safety-relevant gap) | (halt affected work) |

### 4.2 Escalation Path for CSCO Unavailability

If the CSCO is the required escalation target but is unavailable:

1. **Halt all work** on the safety-relevant component or decision immediately.
2. **PM records** the algedonic signal with timestamp and condition description.
3. **No workaround or substitute approval** is permitted for SC/RB category triggers.
4. Work resumes only upon CSCO availability and explicit CSCO approval.

---

## 5. Algedonic Signal Format

When an agent raises an algedonic signal, it writes a signal record to `engagements/<id>/algedonic-log/<sprint-id>-ALG-<sequence>.md` using the following format:

```markdown
---
signal-id:        # <sprint-id>-ALG-<sequence>, e.g. AS-3-ALG-001
trigger-id:       # from §3, e.g. ALG-007
category:         # SC | RB | TC | GV | IA
severity:         # S1 | S2 | S3 | S4
raised-by:        # agent role raising the signal
raised-at:        # sprint identifier
escalation-target: # primary escalation target (role)
status:           # open | acknowledged | resolved | deferred
---

## Condition Description
[Precise description of what happened or what was detected. Factual, no speculation.]

## Affected Artifacts or Work
[List of artifact IDs, sprint IDs, or work packages affected.]

## Immediate Action Taken
[What the raising agent has already done — e.g. halted work, flagged to PM.]

## Required Decision
[What the escalation target must decide or approve before work can resume.]

## Resolution Record
<!-- Filled in by escalation target upon resolution -->
**Resolved by:** [role]  
**Resolution:** [decision taken]  
**Artifacts updated:** [list, if any]  
**Work resumed:** [sprint identifier]  
```

---

## 6. Failsafe Control Topology

When one or more S1 algedonic signals are active, the system enters **Failsafe Mode** for the affected scope. Normal sprint sequencing is suspended for that scope.

### 6.1 Failsafe Mode Rules

| Rule | Description |
|---|---|
| **Work halt** | No new artifacts may be baselined and no Architecture Contracts may be signed in the affected scope until the S1 signal is resolved |
| **Read-only** | Agents may read existing baselined artifacts but may not modify them |
| **CSCO authority** | For SC/RB category signals, CSCO has sole decision authority in failsafe mode; PM records decisions but does not override |
| **PM authority** | For TC/GV/IA category signals with no SC/RB component, PM has sole decision authority |
| **No parallel escalation** | A second algedonic signal must not be raised for the same root cause while the first is open; it is appended to the existing record instead |
| **Scope boundary** | Failsafe mode applies only to the scope identified in the signal record; other scopes continue normally |

### 6.2 Simplified Decision Structure in Failsafe Mode

In failsafe mode, decision-making is simplified to minimise cognitive load and latency:

1. **Identify the scope** — which artifacts, agents, and work packages are directly affected.
2. **Identify the minimum viable action** — the smallest change that resolves the S1 condition.
3. **CSCO or PM decides** (per category) — binary decision: approve minimum viable action or halt scope permanently until further review.
4. **Record and proceed** — decision recorded in signal record; affected artifacts updated if required; work resumes.

---

## 7. Re-Integration After Algedonic Event

Upon resolution of an algedonic signal:

1. **Signal record updated** — status set to `resolved`; resolution record completed by escalation target.
2. **Affected artifacts reviewed** — producing agent confirms affected artifacts are still consistent with the resolution decision; re-baselines if required.
3. **Sprint log updated** — PM records the event and resolution in the sprint log.
4. **Gate checklist updated** — if the signal was raised during a phase gate evaluation, the gate re-evaluates against the post-resolution state.
5. **Retrospective note** — the raising agent submits a retrospective note flagging the root cause and any skill file improvement candidates.
6. **Failsafe mode lifted** — PM explicitly records that failsafe mode is lifted for the affected scope; normal sprint sequencing resumes.

---

## 8. Skill File Requirement

Every skill file in `agents/*/skills/` must include the following section:

```markdown
## Algedonic Triggers

[Either a list of specific conditions in this skill that may trigger an algedonic signal,
referencing trigger IDs from `framework/algedonic-protocol.md §3`,
or the explicit statement: "No algedonic triggers identified for this skill."]
```

The absence of this section in a skill file is itself a governance violation (`ALG-007` applies to the skill file author).

---

## 9. Relationship to VSM Algedonic Channel

In Beer's VSM, the algedonic channel connects System 1 (operational units) directly to System 5 (policy/identity) when System 3 (operational management) cannot respond fast enough. In this system:

| VSM Element | This System Equivalent |
|---|---|
| System 1 | Individual agent roles executing phase work |
| System 2 | Handoff events and feedback loops (normalised coordination) |
| System 3 | Project Manager (day-to-day governance and sprint management) |
| System 3* | CSCO (audit and safety oversight channel) |
| System 4 | Solution Architect (environment scanning, architecture vision) |
| System 5 | PM + CSCO joint authority (policy decisions, irresolvable conflicts) |
| Algedonic channel | This protocol — direct escalation from any System 1 agent to System 3/5 |

The algedonic signal does not travel up the normal hierarchy (agent → PM → SA → CSCO). It goes directly to the authority capable of acting on it. This is the defining characteristic that distinguishes it from a normal feedback item.

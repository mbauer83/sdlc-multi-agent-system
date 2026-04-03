---
skill-id: CSCO-INCIDENT
agent: CSCO
name: incident-response
display-name: Safety Incident and Algedonic Response
invoke-when: >
  An algedonic signal (ALG-001, ALG-012, ALG-014, ALG-017, or ALG-C02) is received
  by CSCO that indicates an active safety constraint violation, regulatory breach,
  production safety incident, or an imminent safety risk in a live system. Also invoked
  when PM reports a production incident that may have safety or compliance implications
  (handoff.created from PM with handoff_type=incident-report). This skill takes
  priority over all other CSCO skills — it is the CSCO's emergency response procedure.
trigger-phases: [A, B, C, D, G, H]
trigger-conditions:
  - algedonic.raised (category=S1 or S2) routed to CSCO
  - handoff.created from PM (handoff_type=incident-report)
  - artifact.baselined from any agent revealing a constraint violation detected post-baseline
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D, EP-G, EP-H]
primary-outputs:
  - Incident Record (ir-<id>-1.0.0.md)
  - Immediate Containment Directive (if S1 — embedded in algedonic response)
  - SCO Incident Annotation (appended to current SCO phase version)
  - Post-incident Safety Finding (sf-<id>.md) — for retrospective
complexity-class: complex
version: 1.0.0
---

# Skill: Safety Incident and Algedonic Response

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** All phases (primarily G and H; also A–D for pre-deployment incidents)
**Skill Type:** Emergency response — immediate activation, priority override
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (loss scenario tracing, causal factor analysis)
**Framework References:** `algedonic-protocol.md §3–§5`, `agile-adm-cadence.md §8`, `clarification-protocol.md`, `framework/discovery-protocol.md §2`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Algedonic signal or PM incident report | PM / Algedonic channel | Active (not resolved) | The triggering signal — provides: ALG-ID, severity (S1–S6), description, affected system scope, reporting agent |
| SCO — all applicable phases | CSCO — safety-repository/ | Most recent version(s) | CSCO reads the SCO to determine which SC-nnn constraints are implicated by the incident |
| Incident detail artifacts | Various (DE PR, DO deployment record, system logs, QA defect record) | Whatever is available at activation time | CSCO reads all available evidence; absence of evidence does not block incident activation — CSCO acts on what is available |
| Architecture Contract (AC) | SwA — technology-repository/ | Current baselined version | Reference for what was contracted vs. what is observed in the incident |
| PM incident report (if PM-triggered) | PM — project-repository/incident-log/ | Draft acceptable | PM may report before CSCO has received the algedonic signal directly |

---

## Knowledge Adequacy Check

### Required Knowledge

- The classification of the incident's severity within the algedonic taxonomy (S1–S6) and the appropriate response actions per severity class.
- Which SCO constraints are potentially violated by the incident (derived from STAMP control structure and UCA analysis completed in prior phases).
- The containment options available for the affected system (rollback, feature flag, network isolation, service degradation) — this requires coordination with DO and DE; CSCO directs the containment response but does not implement it.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Root cause of the incident | No — CSCO acts on the observable safety impact; root cause analysis is post-containment | DE, DO, or SwA (post-containment) | Post-incident Safety Finding (SF) |
| Full scope of the safety impact (how many users, data records, or system functions affected) | No for initial response; yes for regulatory notification decisions | DO (deployment data), DE (implementation scope) | Incident Record §3 (scope), regulatory notification assessment |
| Regulatory notification obligation and timeline | Yes if the incident involves personal data, regulated financial data, or safety-critical system failure | User (via PM) | Incident Record §5 (regulatory response) |

---

## Steps

**Note on timing:** Steps 1–4 are time-critical (must complete within 2 hours of ALG signal receipt for S1 incidents; within 4 hours for S2). Steps 5–7 are post-containment and may extend across the remainder of the sprint.

---

### Step 0.L — Learnings Lookup *(via `query_learnings` tool)*

Call `query_learnings(agent="CSCO", phase="G", artifact_type="safety-constraint-overlay")` before starting. Prepend any returned corrections to working context as "Learnings from prior work relevant to this task." If none returned: proceed normally. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §5`.

---

### Step 0 — Immediate Activation and Signal Receipt

Upon receiving an algedonic signal or PM incident report:

1. **Read the triggering signal:** Identify: ALG-ID (or PM report ID), severity class (S1–S6), reported by, affected system scope, and the constraint or observable safety failure described.
2. **Record activation:** Emit `artifact.baselined` for an Incident Record stub at `safety-repository/incident-records/ir-<id>-0.1.0.md` with status "active — under assessment". This creates the audit trail for the incident response.
3. **Determine immediate escalation need:** For S1 incidents: emit `algedonic.acknowledged` immediately and notify the user via PM (emit `handoff.created` to PM with handoff_type=incident-escalation, severity=S1, action_required=true). For S2: acknowledge and notify PM within 1 hour.
4. **Do not wait for full discovery before containment:** If the incident indicates an active safety constraint violation in a live system (e.g., a safety-critical feature is broken, a data breach is in progress, a deployment has bypassed a security gate): proceed directly to Step 2 (Containment Directive) before completing Steps 0 or 1 in full. Containment takes priority over documentation.

---

### Step 1 — Discovery Scan (Rapid)

Execute a rapid Discovery Scan per `framework/discovery-protocol.md §2`, focused on the incident scope:

1. **Layer 1 — Engagement State:** Read the algedonic-log/ for the full algedonic signal record; read the current SCO phases that apply to the affected system elements; read the AC for the implementation contract; read the relevant PM incident report if present; read any available deployment records or QA defect records related to the incident.
2. **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for any applicable incident notification requirements (regulatory breach notification timelines, authority contact requirements).
3. **Layer 4 — Target Repository:** If target-repo is accessible: check for deployment logs, error logs, or feature flag states that may bound the incident scope.
4. **Annotate and proceed:** For unknown fields at this stage, annotate "unknown at activation — to be determined during investigation". Do not delay containment for discovery completeness.

---

### Step 2 — Issue Containment Directive (S1 and S2 incidents)

For S1 incidents (safety-critical, risk of immediate harm or regulatory breach):

1. **Identify containment options:** Based on the incident description, identify the fastest feasible containment action: rollback (reverse the triggering deployment), feature flag disable (disable the affected feature), traffic isolation (restrict access to the affected service), or service shutdown (if no less-disruptive option is available).
2. **Emit Containment Directive:** Emit `handoff.created` to DO and DE with handoff_type=containment-directive, specifying: the containment action required, the reason (SC-nnn violated / data breach / safety-critical failure), and the deadline (immediate for S1).
3. **Record in Incident Record:** Add the containment directive to the Incident Record §2 (Containment Actions).
4. **Confirm containment:** Await `handoff.acknowledged` from DO/DE confirming containment action taken. If containment is not confirmed within 30 minutes (S1) or 2 hours (S2): raise a second algedonic signal (ALG-001 re-escalation) to the user via PM.

For S3–S6 incidents: no containment directive is issued. Proceed to Step 3 (Assessment).

---

### Step 3 — Assess Safety Constraint Impact

Trace the incident to the SCO using the STAMP constraint impact method:

1. **Identify affected system elements:** From the incident description, identify the specific components (CMP-nnn), interfaces (IFC-nnn), data entities (DE-nnn), or technology nodes (NOD-nnn) involved.
2. **Trace to SCO UCAs:** For each affected element, read the relevant SCO §7 (UCAs) entries — which UCAs describe the failure mode observed in this incident?
3. **Identify violated SC-nnn constraints:** For each matched UCA: identify the SC-nnn constraint(s) that the UCA's corresponding loss scenario should have prevented. Note whether the constraint was:
   - **Violated by implementation:** The constraint existed in the SCO and AC, but the implementation did not satisfy it.
   - **Violated by architecture gap:** The constraint exists in the SCO but was not reflected in the AC (SwA gap from Phase G).
   - **Not covered by SCO:** The incident reveals a hazard that was not identified in any prior STAMP analysis phase — a gap in the SCO itself.
4. **Assess root cause category:** (for SCO update, not blame assignment): design gap (missing SCO constraint), implementation gap (constraint not implemented), operational gap (constraint not enforced operationally), or external event (failure of an external dependency not covered by SCO constraints).

---

### Step 4 — Regulatory Notification Assessment

For incidents that may have regulatory notification obligations:

1. **Check regulatory domain from SCO §2:** Identify the applicable regulatory frameworks.
2. **Assess notification trigger:** Does the incident involve a personal data breach (GDPR: 72-hour notification to supervisory authority), a financial system failure (applicable regulatory reporting), a safety-critical system failure (authority notification per domain standard)?
3. **If notification is required:** Record in Incident Record §5 (Regulatory Response). Emit `handoff.created` to PM and the user with handoff_type=regulatory-notification-required, specifying: the applicable regulation, the notification deadline, the regulatory authority, and the required notification content.
4. **If notification is not required:** Record in Incident Record §5 with rationale for no-notification determination.

---

### Step 5 — Author Incident Record

Produce the full Incident Record `safety-repository/incident-records/ir-<id>-1.0.0.md`:

**§1 Incident Summary:** ALG-ID or PM report ID; date/time detected; reporting agent; system scope; initial severity classification; current status (contained / under investigation / resolved).

**§2 Containment Actions:** For S1/S2: the containment directive issued, the agent responsible, the confirmation status, and the time from incident detection to containment confirmation.

**§3 Safety Constraint Impact:** The SCO analysis from Step 3 — affected elements, matched UCAs, violated SC-nnn constraints, and root cause category.

**§4 Regulatory Notification:** The notification assessment from Step 4 — applicable regulations, notification requirement (yes/no), notification status (pending / submitted / not required).

**§5 Immediate Findings:** What is now known about the incident cause, scope, and impact.

**§6 Open Actions:** For each violated constraint: the remediation required (who, what, when). For each SCO gap identified: the new constraint or UCA update required. For each regulatory notification pending: the deadline and responsible party.

**§7 Resolution Status:** Updated as the incident progresses through investigation and remediation.

Emit `artifact.baselined` for the Incident Record at 1.0.0 (or increment from the stub at 0.1.0).

---

### Step 6 — Update SCO

For each finding from Step 3:

**Violated SC-nnn (implementation gap):** Add an incident annotation to the constraint in SCO §5: "SC-nnn violated in incident ir-<id>-<date>; implementation remediation required before next Phase G sprint; see ir-<id>.md." This does not change the constraint — it documents that the constraint was not satisfied in implementation.

**Violated SC-nnn (architecture gap):** If the constraint existed in the SCO but was not in the AC: update SCO §10 (Open Safety Findings) with finding SF-nnn: "SC-nnn not reflected in Architecture Contract — SwA must update AC and require DE remediation." Emit `handoff.created` to SwA.

**SCO gap (new hazard identified):** If the incident reveals a hazard or UCA not in the SCO: author new L-nnn (Loss), H-nnn (Hazard), SC-nnn (Constraint), and UCA-nnn (Unsafe Control Action) entries per the STAMP methodology (`skills/stamp-stpa-methodology.md`). This is a Phase H SCO update — follow the standard phase update procedure (minor version increment).

Emit `artifact.baselined` for the SCO update.

---

### Step 7 — Post-Incident Safety Finding and Retrospective

After the immediate incident is contained and remediated:

1. **Produce Post-incident Safety Finding:** Author `safety-repository/incident-records/sf-<id>.md` (Safety Finding) summarising: root cause (confirmed), system weakness, STAMP analysis update, remediation applied, and residual risk (if any).
2. **Emit to PM for retrospective:** Emit `handoff.created` to PM with the Safety Finding — to be included in the sprint retrospective and enterprise knowledge base if the finding is generalizable.
3. **Update Incident Record §7:** Mark incident as resolved (or as ongoing if remediation is not yet complete).
4. **Promote if generalizable:** If the incident reveals a systemic safety weakness applicable beyond this engagement: nominate the Safety Finding and SCO additions for enterprise promotion per `repository-conventions.md §12`.

---

## Feedback Loop

This skill does not have a standard iterative feedback loop — it is an emergency response procedure. However:

- **Containment confirmation:** CSCO awaits DO/DE `handoff.acknowledged` confirming the containment action. If not confirmed within the S1 deadline (30 minutes): re-escalate (emit a new ALG-001 to PM and user directly).
- **Remediation tracking:** Open actions in Incident Record §6 are tracked by PM as sprint blockers. CSCO reviews remediation evidence when provided and updates the Incident Record. There is no maximum iteration count on remediation review — each remediation cycle is tracked as an Incident Record version increment.
- **Resolution:** Incident is resolved when all §6 open actions are closed and the SCO has been updated. CSCO emits the final Incident Record version and `handoff.created` to PM confirming resolution.

### Personality-Aware Conflict Engagement

**CSCO ↔ DO/DE (containment resistance):**

DO or DE may resist a containment directive on the grounds that the rollback or feature flag will disrupt active users or running transactions. CSCO's stance: safety constraint violations in live systems are not subject to convenience trade-offs. CSCO communicates the minimal containment action required — not necessarily a full rollback; a targeted feature flag or traffic restriction may be sufficient. CSCO does not negotiate the need for containment; CSCO negotiates the form of containment to find the least-disruptive option that still removes the safety risk.

**CSCO ↔ PM (incident scope and urgency):**

PM may attempt to downgrade the incident severity to avoid sprint disruption. CSCO's severity classification is based on the STAMP constraint analysis, not on operational convenience. CSCO presents the constraint-to-incident tracing as evidence for the severity. If PM and CSCO genuinely disagree about whether the incident constitutes an S1 violation: CSCO holds the S1 classification and escalates to the user — the user makes the final severity determination when CSCO and PM cannot agree.

### Learning Generation

| Trigger | Condition | Importance |
|---|---|---|
| `feedback-revision` | Iteration 1 feedback requires structural revision | S2 |
| `gate-veto` | Gate vote cast Veto | S2 |
| `algedonic` | Algedonic signal raised during this skill | S1 |
| `incorrectly-raised-cq` | CQ raised but answer was derivable from available sources | S2 |

On trigger: call `record_learning()` with `artifact-type="safety-constraint-overlay"`, error-type classified per `framework/learning-protocol.md §4`, correction in imperative first-person voice (≤300 chars/sentence, ≤3 sentences total). Governed by `framework/learning-protocol.md §3–4`.

---

## Algedonic Triggers

- **ALG-001 (S1 — Safety-Critical, re-escalation):** Containment action directed in Step 2 is not confirmed within the deadline (30 minutes S1, 2 hours S2), or new evidence reveals the incident scope is larger than initially assessed and the current containment is insufficient.
- **ALG-012 (S1 — Governance Violation):** Evidence in the incident record reveals that the incident was caused by a governance bypass (a deployment without gate review, a constraint override without user acceptance, a CSCO gate vote ignored). This is a governance failure, not just an operational incident.
- **ALG-017 (S1 — Knowledge Gap):** The incident reveals a safety hazard that was not identified in any prior STAMP analysis phase and cannot be contained without information that is not currently available (e.g., the system is processing data whose classification is unknown, or an external dependency's failure mode is unknown). CSCO halts further action and raises ALG-017 for user input before proceeding.

---

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Incident Record | `IR-<id>-1.0.0` | `safety-repository/incident-records/ir-<id>-1.0.0.md` | `artifact.baselined` |
| Containment Directive (S1/S2) | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` to DO, DE |
| SCO Incident Annotation / Update | `SCO-<phase>-<version>` | `safety-repository/safety-constraint-overlay/` | `artifact.baselined` |
| Post-incident Safety Finding | `SF-<id>` | `safety-repository/incident-records/sf-<id>.md` | `artifact.baselined` |
| Regulatory Notification Alert (if applicable) | (handoff record) | engagements/<id>/handoff-log/ | `handoff.created` to PM, user |
| Algedonic Acknowledgement | (event payload) | EventStore | `algedonic.acknowledged` |

---
skill-id: SM-PHASE-A-SWOT
agent: SM
name: phase-a-swot
display-name: Phase A — SWOT Analysis
invoke-when: >
  Phase A Architecture Sprint starts (sprint.started emitted for Phase A) after or concurrent
  with SM-PHASE-A-MR; Market Analysis draft (MA-nnn, version >= 0.1.0) is available as input;
  or warm-start at EP-A or EP-B. Produces SWOT Analysis artifact and hands off to SA and PO.
trigger-phases: [A]
trigger-conditions:
  - sprint.started (phase=A)
  - artifact.baselined (MA-nnn version >= 0.1.0 — Market Analysis draft available)
  - cq.answered (blocking Phase A market-domain CQs resolved)
  - trigger=revisit and phase_visit_count > 1 (market landscape change or SA architecture constraint update)
entry-points: [EP-0, EP-A, EP-B]
primary-outputs: [SWOT Analysis]
version: 1.0.0
---

# Skill: Phase A — SWOT Analysis

**Agent:** Sales & Marketing Manager  
**Version:** 1.0.0  
**Phase:** A — Architecture Vision  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.2`, `raci-matrix.md §3.2`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md §4.1–4.2`, `discovery-protocol.md §2`, `framework/agent-personalities.md §3.5`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Market Analysis (MA) | SM (self-produced via SM-PHASE-A-MR) | Draft acceptable (version >= 0.1.0); full baseline (1.0.0) preferred but not required for SWOT production to begin | Blocking for SWOT §2 (Opportunities) and §3 (Threats) — these are derived from MA §§2–4; without MA draft, SWOT Opportunities and Threats cannot be produced |
| `sprint.started` event for Phase A | PM | Must be emitted before SM begins work | Hard prerequisite — no SM work begins without this event |
| Architecture Principles Register (PR) | SA (via `architecture-repository/architecture-principles/`) | Draft acceptable (version 0.x.x); absence is non-blocking | SA-authored constraints become inputs to SWOT §1 Weaknesses and constrain SWOT §2 Opportunities. If PR is absent, SM notes: "Architecture Principles Register not yet available — Weaknesses derived from domain knowledge only; revision expected when PR is baselined." |
| Scoping Interview answers / user input document | User (via PM) | CQ answers received and provided to SM via PM handoff | SM uses user's stated capabilities, assets, and differentiation claims as inputs to SWOT §1 (Strengths). |
| Requirements Register (RR) | PO (via `project-repository/requirements/`) | Draft acceptable; absence is non-blocking | SM uses RR to understand the scope of what PO intends to build — this informs which Opportunities are in scope and which are out of scope |
| Enterprise standards and landscape | `enterprise-repository/standards/` and `enterprise-repository/landscape/` | Present or absent; absence is non-blocking | Enterprise-level standards and existing capabilities inform SWOT §1 (Strengths: what enterprise assets can be leveraged) and §1 Weaknesses (what enterprise constraints limit the engagement) |

---

## Knowledge Adequacy Check

### Required Knowledge

- **Market Analysis content:** SM must have at least a draft Market Analysis (MA §§2–4) to populate SWOT Opportunities and Threats. Without MA, only Strengths and Weaknesses can be partially produced from direct user input and enterprise-repository data.
- **Internal capability baseline:** SM must be able to characterise internal strengths — what the organisation or team can do well, what assets they possess, what prior capabilities exist. This typically comes from user input at Scoping Interview, enterprise-repository capability documents, or stakeholder interview summaries from PO.
- **Architecture constraints (from PR):** SA's architecture principles constrain what the system can and cannot do. These are internal constraints that map to SWOT Weaknesses when they reduce market competitiveness or SWOT Strengths when they represent sound structural foundations.
- **Scope boundary:** SM must know what is in scope for the engagement to assess whether a given Opportunity is actionable within this engagement or is out of scope. Without this, the Opportunity-to-scope mapping cannot be produced.

### Known Unknowns

| Unknown | Blocking | CQ Target | SWOT Section Affected |
|---|---|---|---|
| Internal capability assessment (what the organisation can actually do) | Yes, for SWOT §1 Strengths — if no internal characterisation is available from any source, Strengths cannot be produced | User (via PM) | §1 Strengths |
| Architecture Principles Register (SA-authored constraints) | No — absence is documented; Weaknesses are partially produced without PR | SA (availability depends on SA's Phase A sprint progress) | §1 Weaknesses |
| Scope boundary for Opportunities | No — SM can produce Opportunities and annotate each with a scope status | PO or SA | §2 Opportunities (scope mapping) |
| Competitive landscape specifics (MA §3) | No — if MA §3 is Low-confidence, SWOT Threats inherit that confidence level | User (via PM) or external sources | §3 Threats |

### Clarification Triggers

SM raises a CQ when:

1. **No internal capability characterisation available:** User's input does not describe internal capabilities, assets, or differentiators, and no enterprise-repository capability document exists. This is a blocking CQ for SWOT §1 Strengths. SM cannot produce a meaningful Strengths section from market data alone — Strengths are internal.
2. **PR constraint contradicts a major Opportunity:** If SM identifies during SWOT production that an SA architecture principle (from PR) appears to preclude a High-confidence market Opportunity entirely, SM raises a non-blocking CQ to SA asking whether the constraint is fixed or negotiable. This is a non-blocking CQ — SWOT production continues; the Opportunity is annotated `[constrained by PR: <principle-id> — CQ pending]`.
3. **Scope boundary ambiguity for a significant Opportunity:** If a market Opportunity is large and high-confidence but the engagement scope boundary (from Scoping Interview or AV) does not clearly include or exclude it, SM raises a non-blocking CQ to PM / SA for scope clarification. SWOT continues; the Opportunity is annotated `[scope: TBD — CQ pending]`.

CQ format: per `clarification-protocol.md §3`. SM-domain CQs routed by PM. The PR-constraint CQ is routed to SA specifically.

---

## Steps

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/work-repositories/project-repository/market-analysis/` — Market Analysis draft (primary input to SWOT Opportunities and Threats)
- `engagements/<id>/work-repositories/architecture-repository/architecture-principles/` — Architecture Principles Register (SA-authored constraints → SWOT Weaknesses)
- `engagements/<id>/work-repositories/architecture-repository/architecture-vision/` — Architecture Vision draft (if SA has produced one; scope constraints → Opportunity scope mapping)
- `engagements/<id>/work-repositories/project-repository/requirements/` — Requirements Register (PO's scope understanding → Opportunity scope mapping)
- `engagements/<id>/clarification-log/` — resolved market-domain CQs; prior SM CQ answers
- `engagements/<id>/handoff-log/` — SM-PHASE-A-MR handoff events (to confirm MA draft is available)
- `enterprise-repository/capability/` — enterprise team capabilities, established technology capabilities (→ SWOT Strengths)
- `enterprise-repository/standards/` — enterprise standards and SIB (→ SWOT Strengths if standards provide competitive advantage; Weaknesses if they constrain innovation)
- `enterprise-repository/knowledge-base/` — lessons learned, prior engagement outcomes (→ SWOT Weaknesses if recurring failure patterns; Strengths if established patterns of success)

**External source query types for Phase A:**

- `space/page, wiki` on configured Confluence or wiki sources: capability descriptions, team profiles, technology stack documentation, prior SWOT or market analysis documents

**Target-repo paths (if target-repo configured):**

- `README.md`, `docs/` — product description, stated capabilities, technical constraints
- Build files and dependency manifests — existing technology stack as a Strength (maturity) or Weakness (technical debt, constraints)
- CI/CD configuration — operational maturity as a Strength or Weakness

**Pre-existing artifacts that may reduce CQ load:**

- Market Analysis (MA-nnn, version >= 0.1.0) → maps directly to SWOT §2 (Opportunities derived from MA §3 Competitive Landscape and §4 Market Trends) and §3 (Threats derived from MA §3 and §4)
- Architecture Principles Register (PR) → maps to SWOT §1 Weaknesses (constraint analysis)
- Requirements Register (RR) → maps to Opportunity scope classification

**Revisit mode:** If `trigger=revisit` and `phase_visit_count > 1`, read the existing baselined SWOT Analysis from the EventStore artifact registry before the Gap Assessment. Scope the Gap Assessment to only the SWOT quadrants affected by the triggering change (market landscape change → revisit Opportunities and Threats; architecture constraint update → revisit Weaknesses). Proceed to Step 2b (Scoped Revision) rather than Step 2 (Full Production).

---

### Step 1 — Read Market Analysis and Architecture Principles Register

1. **Read Market Analysis (MA-nnn):**
   - Locate the latest MA version in `project-repository/market-analysis/`.
   - Confirm version and status (draft or baselined). If MA is not yet produced (SM-PHASE-A-MR has not completed Step 2), wait for MA draft before proceeding to SWOT §2 and §3 — Strengths and Weaknesses can be started independently.
   - Extract from MA: demand signals (DS-nnn) → candidate Opportunities; competitive threats from §3 and §4 → candidate Threats; business drivers (DRV-SM-nnn) → Opportunity-driver alignment.

2. **Read Architecture Principles Register (PR):**
   - Locate the PR in `architecture-repository/architecture-principles/`. If PR exists (even at version 0.x.x draft), read it.
   - Extract: any principles that constrain what the system can do, what technologies may be selected, or what architecture patterns are required. These are inputs to SWOT §1 Weaknesses (where constraints reduce market competitiveness) and SWOT §1 Strengths (where principles provide structural advantages).
   - If PR does not exist: note in Gap Assessment as `Missing — non-blocking`. Proceed without PR input; annotate Weaknesses section: `[PR not yet available — architecture constraints to be refined when SA produces PR]`.

3. **Confirm scope boundary:**
   - Read the engagement scope from `engagement-profile.md` and, if available, from the Architecture Vision draft.
   - If scope is not yet formally defined (early in Phase A sprint): use the user's stated scope from Scoping Interview answers as the working boundary.

---

### Step 2 — Structure SWOT Analysis (Full Production)

*Skip to Step 2b if trigger=revisit.*

Produce `project-repository/market-analysis/swot-0.1.0.md` with the following structure:

**Summary Header:**

```
artifact-type: swot-analysis
artifact-id: SWOT-<nnn>
version: 0.1.0
status: draft
agent: SM
phase: A
engagement-id: <id>
produced-date: <YYYY-MM-DD>
ma-input: MA-<nnn> v<version>
pr-input: PR-<nnn> v<version> | not-available
assumptions: >
  Discovery: [list layers scanned; note any unavailable]. [Any documented assumptions.]
pending-clarifications: [list open CQ-ids; empty if none]
```

**§1 — Strengths (Internal)**

Strengths are internal capabilities, assets, and established advantages that the organisation or team brings to this engagement — independent of whether the market values them. SM focuses on strengths that are market-relevant (i.e., that affect competitive position or customer value delivery).

For each identified Strength:
- STR-nnn: [strength name — noun phrase]
- Description: [one sentence characterising the strength]
- Source: `[source: user-input | enterprise-repository | inferred: target-repo scan | inferred: domain knowledge]`
- Market relevance: [why this strength matters to the competitive position or customer value delivery]
- Architecture implication: [if the strength constrains or enables architecture choices — stated as market consequence, not architecture prescription]

**Categories of Strengths to investigate:**

1. Technical capabilities: existing codebases, platforms, or infrastructure that provide a development head-start.
2. Domain expertise: team or organisational knowledge of the target market or business domain.
3. Existing customer relationships or data: prior access to customer insights, existing users, or proprietary data.
4. Enterprise assets: approved standards (from SIB), established patterns, or enterprise-wide capabilities that reduce build cost.
5. Architecture foundations: if PR is available, any principles that represent sound structural decisions that create a stable basis for competitive feature development.

**§1 — Weaknesses (Internal)**

Weaknesses are internal limitations that reduce competitive position or create delivery risk. SM focuses on weaknesses that have market consequences — not all technical debt is a market weakness, only technical debt that delays delivery of market-relevant capabilities or constrains customer-facing product characteristics.

For each identified Weakness:
- WEK-nnn: [weakness name — noun phrase]
- Description: [one sentence characterising the weakness]
- Source: `[source: user-input | architecture-principles PR-<nnn> | enterprise-repository | inferred: target-repo scan | inferred: domain knowledge]`
- Market consequence: [how this weakness affects time-to-market, competitive differentiation, or customer experience]
- Mitigation direction: [one sentence on the type of mitigation that could reduce the weakness — SM stays at the market-consequence level; e.g., "reducing custom development in this area would accelerate delivery of differentiating features"]
- Architecture implication flag: `[flags to SA: yes | no]` — yes if SA should consider this weakness when making architecture decisions

**Categories of Weaknesses to investigate:**

1. Architecture constraints (from PR): any principle that limits what the system can do or how quickly it can be built. Example: a "technology independence" principle that prevents use of a market-leading proprietary platform that competitors use freely — this may slow delivery of features customers expect.
2. Technical debt: if target-repo scan reveals significant legacy code, dependency age, or build system complexity that will slow feature delivery.
3. Organisational or team gaps: if Scoping Interview reveals team capability gaps in the target domain.
4. Missing enterprise standards: if enterprise standards (from SIB) do not cover technologies the market demands, requiring bespoke decisions that consume time and carry risk.
5. Data or knowledge gaps: absence of customer data, market research, or domain expertise that competitors may possess.

**§2 — Opportunities (External)**

Opportunities are external conditions — market dynamics, competitor gaps, technology shifts, regulatory changes — that the engagement can exploit to create competitive advantage. Opportunities are derived from MA §§2–4.

For each identified Opportunity:
- OPP-nnn: [opportunity name — noun phrase]
- Description: [one sentence characterising the opportunity]
- Derived from: [MA §section, DS-nnn, or market trend reference]
- Source confidence: `[High | Medium | Low]` — inherited from the MA source that identified it
- In-scope assessment: `[In scope | Out of scope | TBD — CQ pending]`
- Urgency: `[Critical | High | Medium | Low]` — from MA §6 Market Timing if relevant, otherwise SM's assessment
- Architecture implication: [one sentence on what capability or characteristic the system must have to exploit this opportunity — stated as market consequence; e.g., "exploiting this opportunity requires mobile-native delivery — SA should consider mobile interface support in the capability overview"]

**§3 — Threats (External)**

Threats are external conditions — competitor actions, regulatory changes, technology shifts — that reduce the competitive position or sustainability of the engagement's product. Threats are derived from MA §§3–4.

For each identified Threat:
- THR-nnn: [threat name — noun phrase]
- Description: [one sentence characterising the threat]
- Derived from: [MA §section or competitor reference]
- Source confidence: `[High | Medium | Low]` — inherited from the MA source
- Urgency: `[Critical | High | Medium | Low]`
- Impact if unaddressed: [one sentence on the competitive or market consequence if this threat materialises and the engagement does not respond]
- Mitigation direction: [one sentence on the type of response that would reduce the threat — SM stays at market-consequence level]

**§4 — SWOT Implications for Architecture Vision**

This section is SM's synthesis contribution to SA's Architecture Vision work. It maps each SWOT element to an implication for product scope or architecture priority. This section is SM's clearest direct input to SA — it translates market intelligence into architecture-adjacent guidance without crossing into architecture decision-making.

Format — for each SWOT element with material architecture implications:

| SWOT Element | Type | Implication for Architecture Vision |
|---|---|---|
| STR-nnn: [name] | Strength | [one sentence on what this enables for architecture] |
| WEK-nnn: [name] | Weakness | [one sentence on what SA should consider to mitigate this in architecture] |
| OPP-nnn: [name] | Opportunity | [one sentence on what capability the AV should include to exploit this] |
| THR-nnn: [name] | Threat | [one sentence on what the AV should consider to address this threat] |

**Example framing (not prescriptive — SM writes market consequences, not architecture decisions):**

- Correct: "OPP-002 (API ecosystem adoption) implies the system must offer machine-readable interfaces; SA should consider this in capability overview §3.5."
- Incorrect: "SA should implement a REST API with OpenAPI specification." (This is a technology decision — SwA domain.)

---

### Step 2b — Scoped Revision (Revisit Mode Only)

*Execute this step only when trigger=revisit and phase_visit_count > 1. Skip if full production (Step 2).*

1. Read the existing baselined SWOT Analysis from `project-repository/market-analysis/` at the version recorded in the EventStore artifact registry.
2. Identify the triggering change from EventStore gate history or PM instruction: what specifically has changed?
   - Market landscape change → revise §2 (Opportunities) and §3 (Threats); cross-check §4 implications.
   - Architecture constraint update (SA has revised PR) → revise WEK-nnn items derived from PR; revise §4 architecture implication entries affected.
   - Scope change → revise in-scope assessment on OPP-nnn items.
3. For each affected SWOT quadrant or section item: apply the production rules from Step 2 for that item only. Preserve all non-affected content verbatim.
4. Update version history: increment patch version (e.g., 1.0.0 → 1.0.1) and add: `[revised: <date> — scope: §n — trigger: <description>]`.
5. Emit `artifact.baselined` with new version. Create handoff event to SA with delta scope noted.

---

### Step 3 — Map SWOT Elements to Architecture Vision Inputs

After completing §§1–4 in draft:

1. Confirm every SWOT element with a material architecture implication is represented in §4 (SWOT Implications for Architecture Vision).
2. Cross-check: are all MA §5 Business Drivers (DRV-SM-nnn) represented in at least one Opportunity or supported by at least one Strength? If a business driver has no corresponding Opportunity or Strength, note the gap: "DRV-SM-nnn [driver name] is not supported by a current Strength or an accessible Opportunity — this driver may require architectural investment."
3. Cross-check: are all identified Weaknesses with architecture implication flags (`flags to SA: yes`) included in §4? If not, add them.
4. Confirm §4 does not contain any architecture decisions (only architecture-adjacent market consequences). If SM finds itself writing a technology prescription, revise to the market-consequence level.

---

### Step 4 — Submit to SA for Architecture Alignment Review; Submit to PO for Requirements Alignment

**Handoff to SA:**
```
handoff-type: swot-input
from: SM
to: SA
artifact-id: SWOT-<nnn>
artifact-version: 0.1.0
required-action: review SWOT §4 (Architecture Vision Implications) for alignment with AV scope and capability overview; SA may challenge SWOT Opportunity assessments where SM's market characterisation conflicts with SA's architecture constraints
required-by: Phase A gate
notes: SM invites SA to identify SWOT elements that are architecturally infeasible — these will be discussed in the SM ↔ SA feedback loop (Step 5).
```

**Handoff to PO:**
```
handoff-type: swot-input
from: SM
to: PO
artifact-id: SWOT-<nnn>
artifact-version: 0.1.0
required-action: review SWOT §2 (Opportunities) for alignment with Requirements Register scope; PO may note which Opportunities are captured in requirements and which are not yet addressed
required-by: Phase A → B transition
notes: PO does not need to produce a formal review — informal acknowledgement that SWOT Opportunities are visible in the requirements process is sufficient. SM will note any high-priority Opportunities not covered in RR in the SM-REQ-FEEDBACK skill output.
```

Emit `handoff.created` for both handoffs.

---

### Step 5 — Resolve Feedback

**SA Feedback Resolution (primary conflict point — see Personality-Aware Conflict Engagement below):**

1. SA reviews SWOT §4 Implications for Architecture Vision. SA may:
   - Accept the implications as consistent with SA's architecture intent.
   - Challenge an Opportunity or implication as architecturally infeasible (e.g., "OPP-003 requires a capability that violates Architecture Principle P-004").
   - Propose a revised framing of an implication that is more architecturally precise.

2. SM processes SA feedback:
   - If SA challenges a SWOT Opportunity as architecturally infeasible: SM does not remove the Opportunity from the SWOT. SM retains the Opportunity and annotates it: `[SA assessment: architecturally infeasible under current PR — constraint: <principle-id>. Market consequence: [describe what the market loses if this Opportunity is not addressed]. Escalated to PM for architecture prioritisation decision.]`. This is the key SM confrontation move — SM makes the market cost visible rather than silently deferring to SA's feasibility constraint.
   - If SA proposes a revised implication framing that remains at the market-consequence level: SM accepts and updates §4.
   - If SA proposes a revised implication that crosses into technology prescription: SM declines the specific prescription but accepts the architectural direction, revises to market-consequence level, and notes the discussion in `open-issues`.

3. Produce revised SWOT draft (version 0.2.0 if material revisions; 0.1.1 for minor).

**PO Feedback Resolution:**

1. PO acknowledges SWOT or notes which Opportunities are not covered in the Requirements Register.
2. SM notes PO's assessment in §2 Opportunities (in-scope column updates only — SM does not modify requirements).
3. No iteration required with PO unless PO explicitly challenges a SWOT Opportunity's market characterisation.

**Termination conditions:**

- SA and PO have acknowledged SWOT; no material unresolved conflicts: proceed to Step 6.
- After 2 iterations, unresolved conflict with SA remains: SM emits `alg.raised` (ALG-010); PM adjudicates; SM proceeds to Step 6 with conflict documented in `open-issues`.

---

## Feedback Loop

### SA Architecture Alignment Loop (SM ↔ SA)

**Purpose:** SA reviews SWOT §4 to confirm that the market-derived implications SM has identified are consistent with SA's architecture intent, or to challenge implications that are architecturally infeasible.

- **Iteration 1:** SM produces SWOT draft (0.1.0) → handoff to SA → SA reviews §4 → SA provides feedback → SM revises.
- **Iteration 2:** SM provides revised SWOT → SA provides final feedback → SM incorporates.
- **Termination conditions:**
  - SA acknowledges SWOT §4 as consistent with architecture intent (explicit or no further feedback within agreed review window).
  - After 2 iterations: SM baselines SWOT with any remaining open conflicts documented in `open-issues`; escalates to PM (ALG-010) if conflicts are material.
- **Max iterations:** 2. After Iteration 2 exhausted, SM emits `alg.raised` (ALG-010) and PM adjudicates.

### Personality-Aware Conflict Engagement

**Expected tension in this skill's context:** The highest-tension interaction in this skill is SM ↔ SA when SWOT §2 identifies an Opportunity that SA believes is architecturally infeasible given the Architecture Principles Register constraints. SM's strong external bias and competitive urgency orientation will push to preserve the Opportunity as a market reality. SA's integrator role will push to remove or severely qualify any Opportunity that cannot be achieved within established architecture constraints.

**Engagement directive:** When SA flags an Opportunity as architecturally infeasible, SM must not immediately defer or remove the Opportunity from the SWOT. SM's engagement move is:
1. Acknowledge SA's constraint explicitly: "I understand that OPP-nnn conflicts with PR principle P-nnn."
2. Name the market cost specifically: "Removing or not addressing this Opportunity means [describe market consequence — e.g., competitors offer this capability, this customer segment remains unserved, this timing window closes]."
3. Propose a structured resolution path: "I propose we retain OPP-nnn in the SWOT with an annotation noting SA's constraint and flag it to PM for architecture prioritisation — so SA's architecture decision is visible alongside the market cost, and the user can decide whether the constraint is acceptable."
4. Do not prescribe an architecture solution: SM does not say "SA should reconsider P-nnn" or propose a technical workaround. SM names the market consequence and routes the trade-off decision.

This engagement posture distinguishes SM's role from advocacy — SM is not trying to win the argument with SA. SM is making the trade-off visible and routing it to the right decision authority.

**Resolution directive:** A conflict is resolved when:
- SA revises its feasibility assessment (e.g., the constraint is not as absolute as initially characterised) and SM updates the Opportunity scope annotation accordingly.
- SA maintains the constraint and SM annotates the Opportunity with the architecture constraint and the market consequence, and the trade-off is documented in SWOT `open-issues` for PM and user visibility.
- PM adjudicates after 2 iterations and SM implements PM's decision.

A conflict is NOT resolved by SM removing a market Opportunity from the SWOT because SA cannot feasibly deliver it. The SWOT is a market-grounded document — infeasible Opportunities are retained with appropriate annotations, not suppressed.

---

### Step 6 — Baseline SWOT Analysis and Create Handoffs

1. Confirm all blocking CQs are answered or documented as assumptions. Confirm `pending-clarifications` contains only non-blocking items.
2. Update the artifact version to 1.0.0.
3. Write final version to `project-repository/market-analysis/swot-1.0.0.md`.
4. Emit `artifact.baselined`:
   ```
   artifact_id: SWOT-<nnn>
   artifact_type: swot-analysis
   version: 1.0.0
   path: project-repository/market-analysis/swot-1.0.0.md
   agent_id: SM
   phase: A
   ```
5. Create handoff to SA (final baseline):
   ```
   handoff-type: swot-input
   from: SM
   to: SA
   artifact-id: SWOT-<nnn>
   artifact-version: 1.0.0
   required-action: consume SWOT §4 as supplementary Architecture Vision input; SWOT Opportunities and Threats are available to SA for AV §3.4 Business Drivers population and AV §3.5 Capability Overview prioritisation
   required-by: Phase A gate
   ```
6. Emit `handoff.created`.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-010 | SM and SA have completed 2 feedback iterations on SWOT §4 without resolving a conflict about an Opportunity's feasibility or an implication's framing | S3 | SM emits `alg.raised`; PM adjudicates; SM documents both positions in SWOT `open-issues` and proceeds to Step 6 with conflict documented |
| ALG-016 | SWOT cannot be initiated because the Market Analysis draft (MA-nnn) is absent and a blocking CQ for market domain characterisation has been open for more than two sprint cycles with no user response | S2 | SM emits `alg.raised` to PM; SWOT production is suspended pending MA availability; PM escalates market CQ to user as priority interaction |
| ALG-015 | SWOT §2 (Opportunities) identifies a Critical-urgency Opportunity (MA §6 classified `Critical`) that is not addressed by any current sprint plan and the competitive window is within the current engagement timeline | S2 | SM emits `alg.raised` to PM; PM assesses sprint plan and routes to SA for architecture prioritisation; SM continues SWOT production — this is a timing flag, not a halt |

---

## Outputs

| Output | Artifact ID | Path | Version at Baseline | EventStore Event |
|---|---|---|---|---|
| SWOT Analysis | SWOT-nnn | `project-repository/market-analysis/swot-<version>.md` | 1.0.0 (Phase A gate-ready) | `artifact.baselined` |
| Handoff to SA (draft + final) | — | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PO (draft) | — | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| CQ records (if any) | CQ-nnn | `engagements/<id>/clarification-log/` | — | `cq.raised` |
| Algedonic signals (if triggered) | ALG-nnn | `engagements/<id>/algedonic-log/` | — | `alg.raised` |

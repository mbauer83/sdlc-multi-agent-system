---
skill-id: SM-PHASE-A-MR
agent: SM
name: phase-a-market-research
display-name: Phase A — Market Research & Market Analysis
invoke-when: >
  Phase A Architecture Sprint starts (sprint.started emitted for Phase A) and Market Analysis
  artifact does not yet exist at version 1.0.0; or warm-start at EP-A or EP-B when user
  provides a document containing market context; or revisit trigger when PM instructs SM to
  update Market Analysis due to changed market conditions.
trigger-phases: [Prelim, A]
trigger-conditions:
  - sprint.started (phase=A)
  - cq.answered (blocking Phase A market-domain CQs resolved)
  - handoff.created (from PM with scoping interview answers including market-domain responses)
  - trigger=revisit and phase_visit_count > 1 (market landscape change identified)
entry-points: [EP-0, EP-A, EP-B, EP-H]
primary-outputs: [Market Analysis]
complexity-class: simple
version: 1.0.0
---

# Skill: Phase A — Market Research & Market Analysis

**Agent:** Sales & Marketing Manager  
**Version:** 1.0.0  
**Phase:** A — Architecture Vision  
**Skill Type:** Phase primary — artifact production  
**Framework References:** `agile-adm-cadence.md §6.2`, `raci-matrix.md §3.2`, `clarification-protocol.md`, `algedonic-protocol.md`, `sdlc-entry-points.md §4.1–4.2`, `discovery-protocol.md §2`, `framework/agent-personalities.md §3.5`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Scoping Interview answers (EP-0) or user input document (EP-A/EP-B) | User (via PM) | CQ answers received; PM has emitted `cq.answered` for market-domain CQs; or user document provided at EP-A/EP-B | Blocking for MA §1 (Market Context) — SM cannot characterise the market domain without at minimum the engagement's business domain description |
| `sprint.started` event for Phase A | PM | Must be emitted before SM begins work | Hard prerequisite — no SM work begins without this event |
| Enterprise strategic landscape | `enterprise-repository/landscape/strategic/` | Present or absent; absence is non-blocking | SM checks for enterprise-level market positioning statements or strategic direction documents; absence is noted in discovery gap assessment |
| Enterprise knowledge base (prior engagements) | `enterprise-repository/knowledge-base/` | Present or absent; absence is non-blocking | SM checks for prior market analyses, competitive intelligence, or customer segment data from previous engagements |
| Architecture Principles Register (PR) | SA (via `architecture-repository/architecture-principles/`) | Not yet required at MA production time; PR is input to SWOT skill, not MA | SM reads PR if available to understand SA-established constraints that may affect what is architecturally feasible — referenced in MA §5 Business Drivers only to note tension points |
| Requirements Register (RR) | PO (via `project-repository/requirements/`) | Draft acceptable (version 0.x.x); absence is non-blocking | SM reads RR if available to understand what PO has already captured; SM does not reproduce or modify requirements |
| External source market data | `external-sources/<source-id>.config.yaml` | Active configured sources only | SM queries configured external sources (e.g., market research databases, CRM systems, Confluence) for market-domain content |

---

## Knowledge Adequacy Check

### Required Knowledge

- **Business domain characterisation:** SM must understand what industry or market sector the engagement operates in — sufficiently to identify customer segments, competitor types, and relevant market dynamics. Without this, no section of the Market Analysis can be produced.
- **Target customer segments:** SM must be able to name at least one customer segment for MA §1. A single high-level segment description (e.g., "enterprise software buyers in the financial services sector") is sufficient to proceed; refinement can occur through iteration.
- **Competitive landscape basics:** SM should have at least a direction for where to look for competitive information. "We have no known competitors" is acceptable as a stated input if the user asserts it — SM annotates this `[source: user-input, confidence: Low]` and notes the assumption.
- **Market timing context:** SM needs to know whether there are known time-to-market constraints, competitive release events, regulatory deadlines, or seasonal patterns that affect the engagement. This is non-blocking if absent but important for MA §6.
- **Regulatory context (market-relevant):** SM needs to know whether the target market has regulatory requirements that affect market entry, product characteristics, or competitive positioning. This is distinct from technical compliance (CSCO domain) — SM focuses on market-entry regulatory context (e.g., "requires CE marking to sell in EU", "HIPAA compliance required for US healthcare market access").

### Known Unknowns

The following are predictably unknown at Phase A entry and require CQs or documented assumptions:

| Unknown | Blocking | CQ Target | MA Section Affected |
|---|---|---|---|
| Target market segment definition and size | Yes, if no segment can be characterised from available inputs | User (via PM) | §1 Market Context |
| Named or known competitors | No — "unknown" is a valid annotated state | User (via PM) or external-source query | §3 Competitive Landscape |
| Customer pain points and demand signals | No — can be inferred from user's stated problem if not provided directly | User (via PM) or PO (from stakeholder interviews) | §2 Demand Signals |
| Market size and growth rate | No — can be marked `[Low confidence: estimated]` | User (via PM) or external-source query | §1 Market Context |
| Known market timing constraints or competitive release events | No — absence is annotated; MA §6 states no known timing constraints | User (via PM) | §6 Market Timing |
| Regulatory market entry requirements | No — absence is annotated if domain is known not to be regulated | User (via PM) and CSCO (for overlap with safety regulation) | §4 Market Trends |

### Clarification Triggers

SM raises a CQ (`cq.raised` event + CQ record in `engagements/<id>/clarification-log/`) when:

1. **Uncharacterisable business domain:** The user's input and all discovery sources do not describe a business domain sufficiently to identify even one customer segment or competitor type. This is a blocking CQ — MA §1 and §3 cannot proceed without minimal domain context.
2. **Conflicting market signals in source materials:** Discovery yields conflicting descriptions of the market (e.g., enterprise-repository states the target market is SME, but the user's document references enterprise customers). SM raises a CQ to clarify the target segment before proceeding. Blocking for MA §1.
3. **Known but uncharacterised regulated market entry requirement:** SM's domain knowledge or available sources indicate the target market may be subject to regulatory market entry requirements (e.g., healthcare data market, financial services market, critical infrastructure), but the specific requirements are unknown. Non-blocking for MA production (SM annotates `[Low confidence: regulatory market entry requirements unknown]`), but SM simultaneously notifies PM to route a parallel CQ to CSCO for the safety and compliance dimension.
4. **Time-to-market constraint referenced but undefined:** User's input references a market timing constraint (e.g., "we must launch before Q4") but the basis for this constraint is unclear. Non-blocking — SM annotates the constraint as `[source: user-input, confidence: High]` and notes that the rationale is unconfirmed.

CQ format: per `clarification-protocol.md §3`. Market-domain CQs are SM-domain CQs and are routed by PM to the user. SM does not raise CQs to SA or SwA for market information — those roles are consumers of MA, not sources.

---

## Steps

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`. Produce an internal Gap Assessment. Proceed to Step 1 only after all five layers are scanned.

**Expected sources for this phase:**

- `engagements/<id>/engagement-profile.md` — entry point, scope constraints, target-repo configuration, any market context noted at engagement bootstrap
- `engagements/<id>/work-repositories/project-repository/requirements/` — Requirements Register draft (if PO has produced one); SM reads for embedded market signals
- `engagements/<id>/work-repositories/architecture-repository/architecture-principles/` — Architecture Principles Register (if SA has produced one); SM reads for constraints that bound what is architecturally feasible, which SM notes in MA §5
- `engagements/<id>/clarification-log/` — open and resolved CQs; if market-domain CQs were raised and answered in the Scoping Interview, their answers reduce or eliminate the CQ load here
- `engagements/<id>/handoff-log/` — PM handoff of scoping interview answers
- `enterprise-repository/landscape/strategic/` — enterprise-level market positioning or strategic direction
- `enterprise-repository/knowledge-base/` — prior engagement market analyses, customer segment data, competitive intelligence

**External source query types for Phase A:**

- `space/page, wiki` queries on configured Confluence or wiki sources: product vision pages, market research documents, competitive analysis pages, stakeholder interview notes
- Any configured market research or CRM source with `engagement-scope` matching this engagement

**Target-repo paths (if target-repo configured):**

- `README.md`, `docs/` — product description, target audience, value proposition sections
- Any `DESIGN.md`, `ARCHITECTURE.md`, or `docs/decisions/` containing market rationale

**Pre-existing artifacts that may reduce CQ load:**

- Scoping Interview answers (CQ batch resolved by PM before Phase A sprint starts) → maps to all MA sections
- Requirements Register draft from PO → maps to MA §2 (Demand Signals) and MA §5 (Business Drivers)
- Enterprise strategic landscape document → maps to MA §1 (Market Context) and MA §4 (Market Trends)

**Gap Assessment format:** per `discovery-protocol.md §3`. Record status (Covered / Partially Covered / Inferred / Missing) for each MA section. Produce Gap Assessment before Step 1.

**Revisit mode:** If `trigger=revisit` and `phase_visit_count > 1`, read the existing baselined Market Analysis from the EventStore artifact registry before the Gap Assessment. Scope the Gap Assessment to only the sections affected by the triggering change. Proceed to Step 2b (Scoped Revision) rather than Step 2 (Full Production).

---

### Step 1 — Ingest Available Market Context

Consolidate all market-relevant content found during the Discovery Scan:

1. **From Scoping Interview answers / user document:** Extract business domain characterisation, stated customer segments, stated competitive context, stated market timing constraints, stated business drivers. Annotate each extract as `[source: user-input]`.

2. **From Requirements Register (if available):** Identify requirements that carry embedded market rationale (e.g., "As a [customer segment] user, I need [capability] because [market reason]"). Extract the market rationale as a demand signal. Annotate `[derived: requirements-register, RQ-nnn]`. Do not reproduce the requirement itself in the MA — reproduce the underlying demand signal.

3. **From enterprise-repository landscape:** Identify any enterprise-level market positioning statements, approved market segments, or strategic direction documents. Annotate `[source: enterprise-repository]`. If enterprise landscape contradicts user-stated market context, note the conflict explicitly and raise it as a non-blocking CQ.

4. **From external sources:** Consolidate all content retrieved from external source queries. For each retrieved item, annotate `[source: <source-id>]`.

5. **From target-repo (if configured):** Extract any product description, target audience, or value proposition content from README or documentation. Annotate `[inferred: target-repo scan]`.

6. **Confidence classification:** For each item ingested, assign an initial confidence level:
   - High: directly stated by user in Scoping Interview or user document
   - Medium: inferred from user input or derived from a baselined artifact
   - Low: inferred from target-repo scan, external source with unknown authority, or assumed from domain knowledge

---

### Step 2 — Structure Market Analysis (Full Production)

*Skip to Step 2b if trigger=revisit.*

Produce `project-repository/market-analysis/market-analysis-0.1.0.md` with the following six-section structure:

**Summary Header:**

```
artifact-type: market-analysis
artifact-id: MA-<nnn>
version: 0.1.0
status: draft
agent: SM
phase: A
engagement-id: <id>
produced-date: <YYYY-MM-DD>
assumptions: >
  Discovery: [list layers scanned; note any unavailable]. [Any documented assumptions made in lieu of missing information.]
pending-clarifications: [list open CQ-ids; empty if none]
data-age: [YYYY-MM for the most recent market data cited; or "unknown" if not determinable]
```

**§1 — Market Context**

1. **Business domain characterisation:** One paragraph naming and describing the industry or market sector. State the primary market mechanism (e.g., B2B SaaS, B2C marketplace, enterprise on-premises, regulated services). Annotate confidence.
2. **Market size and dynamics:** State market size (value or volume) if available, and whether the market is growing, stable, or contracting. If market size is unknown: `[Low confidence: market size not determinable from available sources — estimated based on domain knowledge]`.
3. **Key customer segments:** Table of segments. For each segment: name, brief description, estimated size (relative: Large / Medium / Niche), primary pain point, and purchasing behaviour characterisation. Minimum one segment; maximum five at this level of analysis.

**§2 — Demand Signals**

Demand signals are what customers are actually asking for — needs, pain points, feature requests, frustrations with existing solutions — independent of what the system being built will do.

1. **Named demand signals:** Assign DS-nnn identifiers sequentially. For each demand signal:
   - DS-nnn: [signal description]
   - Source: [user-input | requirements-register RQ-nnn | external-source <id> | inferred: domain knowledge]
   - Confidence: [High | Medium | Low]
   - Customer segment: [which segments exhibit this demand]
   - Current solution gap: [what customers are doing today that is inadequate]

2. **Coverage note:** Indicate which demand signals align with known requirements (if RR is available) and which are not yet covered by any requirement. Do not create requirements — flag the gap for PO.

**§3 — Competitive Landscape**

1. **Competitor table:** For each identified competitor (or competitor category):
   - Name or category (if unnamed: "Category: [description]")
   - Offering characterisation (what they offer, in 1–2 sentences)
   - Key differentiator (what they are known for)
   - Known weaknesses or gaps
   - Market share or position characterisation (Leader / Challenger / Niche / Unknown)
   - Source confidence annotation

2. **Differentiation analysis:** Based on competitor table, state where the opportunity for differentiation lies. What can this engagement's product do differently, better, or for a different segment? This is SM's framing contribution — not a technical prescription.

3. **If no competitors are identified:** State explicitly: "No competitors identified from available sources. [Source: user-input | discovery scope insufficient]. This absence may indicate a nascent market, a highly specialised niche, or a discovery gap — recommend targeted external market research (CQ raised if applicable)."

**§4 — Market Trends**

1. **Technology adoption trends:** What technology shifts are changing what customers expect or what competitors can offer? (e.g., AI/ML adoption, cloud-native expectations, mobile-first shifts, API economy). State as market observations, not technology prescriptions.
2. **Regulatory shifts:** Are there regulatory changes (enacted or anticipated) that are changing market entry requirements, data handling obligations, or product characteristics? Annotate confidence. If regulatory shifts intersect with safety or compliance constraints, note: "CSCO engagement recommended for compliance dimension."
3. **Emerging opportunities:** What new segments, use cases, or value propositions are emerging in this market? Annotate confidence.
4. **Threat landscape:** What trends represent threats to the market position of a new entrant (e.g., platform lock-in, incumbent consolidation, market commoditisation)?

**§5 — Business Drivers**

Synthesise the top 3–5 business drivers that should shape the product's scope and architecture priorities. These are derived from §§1–4 and represent SM's market-grounded recommendation to SA and PO about what matters most.

For each driver:
- DRV-SM-nnn: [driver name — short noun phrase]
- Description: [one sentence explaining the driver from a market perspective]
- Derived from: [MA §section(s) and/or demand signals DS-nnn]
- Strategic importance: [High | Medium | Low with brief rationale]
- Architecture implication: [one sentence suggesting what architecture characteristic this driver implies — SM stays at the market-consequence level, not the architecture-decision level; e.g., "time-to-market pressure implies minimising custom development in non-differentiating components"]

**§6 — Market Timing**

1. **Windows of opportunity:** Are there time-bounded market opportunities (e.g., competitor roadmap gaps, regulatory transition periods, seasonal adoption cycles)? Specify: window description, estimated open date, estimated close date or trigger event.
2. **Competitive deadlines:** Known or estimated competitor release dates, market entry events, or platform changes that set a competitive deadline for this engagement.
3. **First-mover analysis:** Is first-mover advantage available and material in this market? Or is the market already past first-mover dynamics?
4. **Recommended urgency classification:**
   - `Critical`: market window is open and closes within the engagement's estimated timeline — delay risks losing the window
   - `High`: competitive pressure is significant; delay allows competitors to establish positions
   - `Medium`: no acute timing pressure identified; competitive dynamics are stable
   - `Low`: market timing is not a significant factor for this engagement
5. **If no timing constraints are identified:** State: "No specific market timing constraints identified from available sources. Market timing is classified as `Low` for this engagement."

---

### Step 2b — Scoped Revision (Revisit Mode Only)

*Execute this step only when trigger=revisit and phase_visit_count > 1. Skip if full production (Step 2).*

1. Read the existing baselined Market Analysis from `project-repository/market-analysis/` at the version recorded in the EventStore artifact registry.
2. Identify the triggering change from the EventStore gate history or PM's phase-return instruction: what specifically has changed in the market landscape?
3. Identify which MA sections are affected by the triggering change. Only affected sections are in scope for revision.
4. For each affected section: apply the procedure from Step 2 for that section only. Preserve all non-affected sections verbatim.
5. Update the version history in the artifact header: increment the patch version (e.g., 1.0.0 → 1.0.1) and add a revision note: `[revised: <date> — scope: §n, §m — trigger: <description>]`.
6. Update `data-age` annotation if newer market data is being used.
7. Emit `artifact.baselined` with the new version. Create handoff events to SA and PO noting the delta scope.

---

### Step 3 — Annotate Confidence Levels

After completing §§1–6 in draft:

1. Audit every factual claim in the draft. Confirm that each claim has a source annotation and a confidence annotation.
2. Produce a **Source & Confidence Summary** in the artifact appendix:
   - Table of all market claims, their sources, and their confidence levels
   - Total count by confidence level (High / Medium / Low)
   - Data age of the most and least recent evidence cited
3. If the majority of claims in any section are `Low` confidence, flag that section in `pending-clarifications` and add a note: "This section rests primarily on Low-confidence inputs and should be reviewed when higher-confidence market data is available."

---

### Step 4 — Identify Top Business Drivers and Rank

1. Review the Business Drivers identified in MA §5. Confirm that each driver is:
   - Traceable to at least one demand signal (DS-nnn) or market trend from §§2–4
   - Distinct from the others (no two drivers should be expressing the same underlying market pressure)
   - Phrased from the market perspective (not as an internal objective)
2. Rank the drivers by strategic importance: High > Medium > Low. Assign the ranking based on:
   - Customer segment size affected
   - Competitive pressure intensity
   - Market timing urgency
   - Source confidence (High-confidence signals carry more weight than Low-confidence assumptions)
3. Confirm that the top 3 drivers are the most impactful and defensible from the available evidence. If the ranking is uncertain due to low confidence, state: "Ranking is provisional — dependent on [CQ-id or external data]."

---

### Step 5 — Submit Draft to PO for Requirements Alignment Review

1. Create a handoff event to PO:
   ```
   handoff-type: market-analysis-review
   from: SM
   to: PO
   artifact-id: MA-<nnn>
   artifact-version: 0.1.0
   required-action: review for requirements alignment
   required-by: [end of current sprint]
   notes: SM requests PO review of demand signals (§2) and business drivers (§5) for alignment with Requirements Register. PO may challenge market claims with contradicting evidence.
   ```
2. Emit `handoff.created`.
3. Await PO feedback. SM work is not blocked during this wait — SM may begin Phase A SWOT work (SM-PHASE-A-SWOT skill) concurrently.

---

### Step 6 — Resolve PO Feedback

**Iteration 1:**

1. PO returns feedback on the Market Analysis draft. Feedback may include:
   - Challenge to a market claim (PO has contradicting evidence from customer interviews or stakeholder input)
   - Request to add a demand signal SM missed that PO has captured
   - Disagreement about the ranking of Business Drivers
   - Concern that a demand signal SM identified is out of scope for this engagement
2. SM evaluates each piece of feedback:
   - If PO provides contradicting evidence that is higher-confidence than SM's current claim: SM revises the claim, updates the confidence annotation, and annotates the change `[revised: PO feedback — <date>]`.
   - If PO challenges a claim without providing contradicting evidence: SM maintains the claim, notes the challenge in `open-issues`, and annotates `[challenged by PO — SM position maintained: <brief rationale>]`.
   - If PO requests a demand signal addition that is within SM's market scope: SM adds it with `[source: PO feedback]` annotation.
   - If PO says a demand signal is out of scope: SM annotates the signal `[scope: PO-assessed out-of-scope — retained in MA as market observation only]`. SM does not remove demand signals based on scope assessment alone — scope is SA's and PM's domain; SM's job is to make the full demand picture visible.
   - If PO and SM disagree on Business Driver ranking: SM proposes a compromise ranking with explicit rationale; documents the disagreement in `open-issues`.
3. Produce revised draft (version 0.2.0 if material revisions made; otherwise 0.1.1 for minor revisions).
4. Notify PO of revisions via updated handoff record.

**Iteration 2:**

1. If PO has further feedback after Iteration 1: SM processes it using the same rules above.
2. SM produces final draft ready for baseline (version 0.x.0 → 1.0.0 candidate).

**Termination conditions:**

- PO acknowledges the Market Analysis as fit for purpose: proceed to Step 7 immediately.
- PO has no further feedback after Iteration 2: proceed to Step 7.
- After 2 iterations, unresolved conflict remains between SM and PO: document the conflict in `open-issues` and escalate to PM (emit `alg.raised` with ALG-010; PM adjudicates). SM proceeds to Step 7 with the unresolved conflict documented — the MA is not held pending PM adjudication unless PM instructs a hold.

---

## Feedback Loop

### PO Alignment Loop (SM ↔ PO)

**Purpose:** PO reviews Market Analysis to ensure demand signals and business drivers align with the requirements scope PO is managing.

- **Iteration 1:** SM produces draft MA (0.1.0) → handoff to PO → PO provides feedback → SM revises.
- **Iteration 2:** SM provides revised MA → PO provides final feedback → SM incorporates.
- **Termination conditions:**
  - PO acknowledges MA as fit for purpose (explicit acknowledgement or no further feedback within agreed review window).
  - After 2 iterations: SM baselines MA with any remaining open conflicts documented in `open-issues`; escalates to PM (ALG-010) if conflicts are material.
- **Max iterations:** 2. After Iteration 2 exhausted without resolution, SM emits `alg.raised` (ALG-010) and PM adjudicates.
- **What SM does not do in this loop:** SM does not modify requirements, accept scope restrictions on demand signals, or allow PO to suppress a market observation from the MA. PO's authority is requirements prioritisation, not market observation suppression.

### Personality-Aware Conflict Engagement

**Expected tension in this skill's context:** SM ↔ PO tension is the primary conflict in this feedback loop. PO may push back on demand signals that SM has identified as significant if PO believes they are out of scope, low priority, or misaligned with the product vision. SM has a strong external bias and may resist PO's scope framing when it appears to suppress genuine market signals.

**Engagement directive:** SM engages PO conflict by naming the specific market evidence behind the challenged demand signal — not by asserting authority. SM says: "This demand signal is supported by [evidence type, confidence level] — I understand PO's scope concern, but suppressing the signal from the MA removes market visibility for SA and downstream roles. My proposal: retain the signal in MA with a scope annotation noting PO's assessment, so SA can make an informed architecture decision." SM does not escalate to PM until 2 iterations are exhausted.

**Resolution directive:** A conflict is resolved when: (a) SM and PO agree on a framing of the demand signal that both find accurate; (b) the demand signal is retained in the MA with an appropriate scope annotation that PO accepts; or (c) PM adjudicates after 2 iterations and SM implements PM's decision. A conflict is NOT resolved by SM silently removing a demand signal to avoid friction.

---

### Step 7 — Baseline Market Analysis and Create Handoffs

1. Confirm all blocking CQs are answered or documented as assumptions with risk acceptance. Confirm `pending-clarifications` contains only non-blocking items.
2. Update the artifact version to 1.0.0.
3. Write final version to `project-repository/market-analysis/market-analysis-1.0.0.md`.
4. Emit `artifact.baselined`:
   ```
   artifact_id: MA-<nnn>
   artifact_type: market-analysis
   version: 1.0.0
   path: project-repository/market-analysis/market-analysis-1.0.0.md
   agent_id: SM
   phase: A
   ```
5. Create handoff to SA:
   ```
   handoff-type: market-analysis-input
   from: SM
   to: SA
   artifact-id: MA-<nnn>
   artifact-version: 1.0.0
   required-action: consume as Phase A Architecture Vision input (AV §3.4 Business Drivers and §3.5 Capability Overview)
   required-by: Phase A gate
   notes: MA §5 Business Drivers are SM's market-grounded recommendation for AV DRV-nnn population. MA §2 Demand Signals are available for SA's Stakeholder Register concerns column.
   ```
6. Create handoff to PO:
   ```
   handoff-type: market-analysis-input
   from: SM
   to: PO
   artifact-id: MA-<nnn>
   artifact-version: 1.0.0
   required-action: consume as Requirements Register market context; review MA §2 Demand Signals for requirements coverage gaps
   required-by: Phase A → B transition
   notes: MA §2 Demand Signals flagged without RR coverage are advisory inputs to PO requirements prioritisation. PO decides whether to create requirements from these signals.
   ```
7. Emit `handoff.created` for both handoffs.

---

## Algedonic Triggers

| ID | Condition in This Skill | Severity | Action |
|---|---|---|---|
| ALG-010 | SM and PO have completed 2 feedback iterations on Market Analysis without resolving a material conflict (e.g., PO is suppressing a High-confidence demand signal that SM believes must be visible to SA) | S3 | SM emits `alg.raised`; PM adjudicates; SM documents both positions in MA `open-issues` and proceeds to baseline with the conflict documented |
| ALG-015 | Market Analysis discovery reveals a time-critical market window (MA §6 classified `Critical`) that is incompatible with the current sprint plan (i.e., the competitive deadline falls within the Phase A sprint or immediately after, and current plan would miss it) | S2 | SM emits `alg.raised` to PM; PM assesses sprint restructuring; SM continues MA production — this is a timing flag, not a work halt |
| ALG-016 | A blocking market-domain CQ (specifically: SM cannot characterise the business domain sufficiently to produce any MA section) has been open for more than two sprint cycles with no user response | S2 | SM emits `alg.raised` to PM; PM consolidates CQs and escalates to user as priority interaction; SM MA production is suspended pending response |
| ALG-001 | During Market Trends analysis (MA §4), SM identifies a market-entry regulatory requirement that intersects with a safety or compliance constraint that CSCO has not yet acknowledged (e.g., a newly enacted data localisation law in the target market that affects where regulated data may be stored) | S2 | SM emits `alg.raised` to PM with routing instruction to CSCO; SM annotates the MA §4 item `[CSCO engagement required — ALG raised: <alg-id>]`; SM does not characterise the safety/compliance dimension — CSCO owns that |

---

## Outputs

| Output | Artifact ID | Path | Version at Baseline | EventStore Event |
|---|---|---|---|---|
| Market Analysis | MA-nnn | `project-repository/market-analysis/market-analysis-<version>.md` | 1.0.0 (Phase A gate-ready) | `artifact.baselined` |
| Handoff to SA | — | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| Handoff to PO | — | `engagements/<id>/handoff-log/` | — | `handoff.created` |
| CQ records (if any) | CQ-nnn | `engagements/<id>/clarification-log/` | — | `cq.raised` |
| Algedonic signals (if triggered) | ALG-nnn | `engagements/<id>/algedonic-log/` | — | `alg.raised` |

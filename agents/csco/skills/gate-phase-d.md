---
skill-id: CSCO-GATE-D
agent: CSCO
name: gate-phase-d
display-name: Phase D Safety Gate Review — Technology Architecture
invoke-when: >
  SwA produces Technology Architecture (TA) at version 1.0.0 (artifact.baselined emitted).
  CSCO reviews TA and ADR Register for technology-level safety, security architecture,
  resilience, and failure modes. Performs STAMP Level 3 analysis. Authors SCO Phase D update.
  Casts the D→E gate vote. This gate has the highest CSCO↔SwA tension in the engagement.
trigger-phases: [D]
trigger-conditions:
  - artifact.baselined from SwA (artifact_type=technology-architecture)
  - artifact.baselined from SwA (artifact_type=adr-register) — also triggers CSCO review
  - handoff.created from SwA requesting CSCO technology safety review
  - cq.answered resolving a blocking Phase D CSCO safety CQ
entry-points: [EP-0, EP-A, EP-B, EP-C, EP-D]
primary-outputs:
  - SCO Phase D Update (sco-D-1.0.0.md)
  - Gate Record Phase D (gr-D-E-1.0.0.md)
  - gate.vote_cast for D→E gate
version: 1.0.0
---

# Skill: Phase D Safety Gate Review — Technology Architecture

**Agent:** Chief Safety & Compliance Officer (CSCO)
**Version:** 1.0.0
**Phase:** D — Technology Architecture
**Skill Type:** Gate review — STAMP Level 3 analysis + gate vote
**Methodology Reference:** `skills/stamp-stpa-methodology.md` (STAMP Level 3 — technology failure mode analysis)
**Framework References:** `agile-adm-cadence.md §6.5`, `raci-matrix.md §3.5`, `framework/artifact-schemas/technology-architecture.schema.md`, `algedonic-protocol.md`, `clarification-protocol.md`, `framework/discovery-protocol.md §2`

---

## Inputs Required

| Input | Source | Minimum State | Notes |
|---|---|---|---|
| Technology Architecture (TA) | SwA — technology-repository/technology-architecture/ | Baselined at version 1.0.0 | Formal gate review cannot begin until TA is baselined |
| ADR Register | SwA — technology-repository/adrs/ | Baselined or current — all ADRs through Phase D must be included | ADRs are reviewed alongside TA; CSCO reviews ADRs for safety implications of technology decisions |
| SCO Phase C Baseline | CSCO — safety-repository/safety-constraint-overlay/ | Baselined at version 1.0.0 | Required — Phase D SCO update is an extension of Phase C |
| Application Architecture (AA) | SA — architecture-repository/application-architecture/ | Baselined at version 1.0.0 | Cross-reference: verify TA technology components enable AA component control actions |
| Data Architecture (DA) | SA — architecture-repository/data-architecture/ | Baselined at version 1.0.0 | Cross-reference: verify TA storage and access technologies satisfy DA classification constraints |
| sprint.started event | PM | Must be emitted for Phase D sprint | Hard prerequisite |

---

## Knowledge Adequacy Check

### Required Knowledge

- Technology safety and security patterns: authentication mechanisms (OAuth2, OIDC, mTLS, API keys), encryption (TLS versions, algorithm strength, key management), network security (DMZ, private subnets, WAF, DDoS mitigation), resilience patterns (circuit breakers, retry with backoff, bulkhead isolation, graceful degradation).
- Technology failure modes relevant to the engagement's technology selections: CSCO must understand the characteristic failure modes of the technology categories selected by SwA (databases, message brokers, container orchestrators, API gateways, etc.) at a system-level — not at implementation depth.
- The SCO Phase C constraints (SC-nnn constraints introduced at Phase C that must now be verified at the technology level): which Phase C constraints are now specifically referable to technology components in the TA.
- STAMP/STPA Level 3 procedure per `skills/stamp-stpa-methodology.md §Steps 4–6`.

### Known Unknowns

| Unknown | Blocking | CQ Target | Artifact Affected |
|---|---|---|---|
| Specific technology product versions (for known CVE vulnerability assessment) | No — CSCO assesses technology categories and their failure modes; version-specific vulnerabilities are Phase G spot-check domain | SwA (TA) | SCO §5 (D-level constraints) — note that version-specific controls are referenced but not required at Phase D |
| Third-party library or dependency security posture | No for Phase D gate — CSCO flags the category of risk; specific SCA (Software Composition Analysis) is Phase G | SwA (TA) | SCO §10 (open finding — defer to Phase G) |
| Cloud provider SLA for safety-critical services | Yes if SLA compliance is an SC-nnn constraint (e.g., a regulatory standard mandates a specific availability SLA) | SwA (TA) and User (via PM) | SCO §5 (D-level availability constraints) |
| Cryptographic algorithm strength (specific cipher suites) | No — CSCO flags the requirement category; specific cipher suite selection is a Phase D-level ADR that SwA owns | SwA (ADR Register) | SCO §5 (encryption constraints) |

### Clarification Triggers

CSCO raises a CQ when:

1. **TA does not describe a security architecture:** The TA provides technology component selections but does not describe how authentication, authorisation, encryption, or network isolation are implemented. CSCO raises a blocking CQ to SwA for a security architecture section to be added to the TA before the D→E gate can be cast.
2. **Technology selection introduces a failure mode with no mitigation described:** CSCO identifies a technology component (e.g., a single-node database, an unsharded cache, a third-party external dependency with no stated fallback) whose failure would violate a safety-critical SC-nnn constraint, and the TA does not describe a mitigation. CSCO raises a CQ to SwA (may become a veto if the mitigation is not feasible).
3. **An ADR overrides a Phase C safety constraint without CSCO notation:** SwA has recorded a technology decision (ADR) that deviates from a Phase C architectural constraint (e.g., ADR-015 selects an unencrypted internal message bus where SCO Phase C requires encryption of all Confidential data flows). CSCO raises a CQ/veto to SwA citing the specific SC-nnn being overridden.

---

## Steps

### Step 0 — Discovery Scan

Execute the Discovery Scan per `framework/discovery-protocol.md §2`:

1. **Layer 1 — Engagement State:** Read TA and ADR Register from technology-repository/; read SCO Phase C baseline from safety-repository/; read AA and DA from architecture-repository/ (cross-reference for constraint applicability); read clarification-log/ (safety-relevant Phase D CQs); read handoff-log/ (SwA handoffs for CSCO technology review); read algedonic-log/ (open ALG signals affecting Phase D).
2. **Layer 2 — Enterprise Repository:** Read enterprise-repository/standards/ for applicable security standards (ISO 27001, NIST CSF, OWASP ASVS, CIS Controls), cloud security frameworks (CSA CCM, NIST SP 800-145), and any domain-specific technology safety standards (IEC 62443 for industrial, DISA STIG for government, PCI-DSS for payment systems).
3. **Layer 3 — External Sources:** Check external-sources/ for any configured security advisory databases or compliance frameworks.
4. **Layer 4 — Target Repository:** If target-repo is configured, check for existing security policies, penetration test results, or technology-specific security configurations.
5. **Layer 5 — Inference:** Annotate inferred fields with `[inferred — source: domain knowledge / technology category knowledge]`.

---

### Step 1 — Confirm Gate Readiness

1. Confirm `artifact.baselined` has been emitted for TA version 1.0.0 and that the ADR Register is current.
2. Confirm SCO Phase C baseline exists at 1.0.0.
3. Check for revisit trigger. If revisit: proceed to Step 10 (revisit handling).
4. Load CSCO-STAMP-STPA methodology reference.

---

### Step 2 — Read Technology Architecture in Full

Read the TA document from `technology-repository/technology-architecture/ta-1.0.0.md`:

- **Technology Component Catalog (TC-nnn):** For each technology component: note the technology category (database, message broker, API gateway, cache, container orchestrator, identity provider, etc.), the version or version range, the role in the system (which AA components it supports), and any stated reliability or security properties.
- **Technology/Application Matrix:** Verify that every safety-relevant AA component has a corresponding technology component implementation. Flag any AA component with no technology mapping as a gap.
- **Infrastructure Architecture:** Review the infrastructure design for: single points of failure in safety-critical paths; network segmentation and isolation zones; geographic distribution or redundancy requirements; disaster recovery and failover mechanisms.
- **Security Architecture section (if present):** Read the authentication, authorisation, encryption, and audit logging design. If this section is absent: flag as a blocking finding.
- **Deployment Architecture:** Review how components are deployed — note whether safety-critical components are isolated from general-purpose components at the infrastructure level (satisfying Phase C isolation constraints).

---

### Step 3 — Review ADR Register

Read every ADR in the ADR Register from `technology-repository/adrs/`:

For each ADR: assess whether the technology decision documented in the ADR has safety implications:

1. **Safety-relevant technology selection:** Does the ADR select a technology component for a function that appears in the SCO control structure or has an associated SC-nnn constraint? If yes: verify the selected technology can satisfy the constraint.
2. **Trade-off acceptance:** Does the ADR accept a trade-off that relaxes a safety property (e.g., "we accept eventual consistency in the data store for performance reasons")? If yes: verify whether this trade-off violates any SC-nnn constraint. If it does: flag as Violation Type A.
3. **Missing security consideration:** Does the ADR address a security-relevant technology choice (authentication mechanism, encryption library, key management approach) without referencing CSCO review? If the ADR makes a security decision without citing the applicable SC-nnn constraints: flag as Violation Type B — the ADR should reference the SCO constraints it satisfies.
4. **SCO constraint override:** Does the ADR explicitly override or contradict a Phase C architecture constraint? If yes: this is Violation Type A — an ADR cannot override an SCO constraint without user-level risk acceptance.

---

### Step 4 — Perform STAMP Level 3 Analysis — Technology Failure Mode UCAs

Using the SCO Phase C §6 (Control Structure — application level) as the starting point, extend the control structure to the technology level:

**4a. Extend Control Structure (SCO §6 update — Level 3):**

For each safety-relevant application component and its corresponding technology component:
- Identify the technology control mechanism that enables each safety-relevant control action (e.g., APP-005 authenticates callers → TC-012 identity provider issues and validates JWT tokens).
- Identify the failure modes of the technology control mechanism (e.g., JWT validation library has a known bypass; identity provider is unavailable; token expiry is misconfigured).
- Add Level 3 entries to SCO §6 Control Structure table: technology controller → technology control mechanism → controlled technology component → feedback channel (health checks, logs, metrics).

**4b. Identify Technology-Level UCAs (SCO §7 update — Level 3):**

For each technology control mechanism identified in 4a: apply the four UCA types at the technology level:

- **Authentication mechanism failure (not-provided):** The identity provider is unavailable and the API gateway falls back to allowing unauthenticated requests. UCA: authentication check not provided in context [identity provider outage].
- **Encryption misconfiguration (provided when not needed):** The message broker is configured to accept plaintext connections alongside TLS connections. UCA: unencrypted data transmission provided in context [client uses plaintext protocol].
- **Resilience timing (too late):** The circuit breaker is configured with a timeout that is longer than the user-facing SLA. UCA: fallback response provided too late in context [upstream service latency exceeds SLA].
- **Audit log overflow (stopped too soon):** The audit log rotation policy truncates logs before the legally mandated retention period expires. UCA: audit log retention stopped too soon in context [disk space constraint triggered rotation].

For each UCA: author UCA-nnn. Link to H-nnn, L-nnn, and existing Phase C SC-nnn where applicable. Author new SC-nnn where no constraint covers the UCA.

---

### Step 5 — Security Architecture Review

Perform a structured security architecture review against the SCO Phase C constraints and applicable security standards:

**5a. Authentication review:**
For each interface in the AA Interface Catalog that has an SC-nnn authentication constraint (from Phase C): verify the TA security architecture specifies an authentication mechanism for that interface. Document: the interface ID, the SC-nnn constraint, the TA mechanism, and the assessment (satisfied / not satisfied / partially satisfied).

**5b. Authorisation review:**
For each application component or interface with an SC-nnn authorisation constraint: verify the TA describes an authorisation mechanism (RBAC, ABAC, ACL) appropriate for the constraint's scope. Document as above.

**5c. Encryption review:**
For each SC-nnn constraint requiring data encryption (in transit or at rest): verify the TA specifies encryption for: all identified data flows carrying Confidential or Restricted data, all storage components holding Confidential or Restricted data entities, and key management (key storage, rotation, access control).

**5d. Audit logging review:**
For each SC-nnn constraint requiring audit trail (from regulatory compliance): verify the TA specifies audit log generation for: all safety-relevant operations, all access to Restricted data entities, all authentication events (success and failure), and all authorisation decisions for high-privilege operations. Verify audit log retention satisfies regulatory minimum retention periods.

**5e. Single point of failure review:**
For each technology component in the TA that is part of a safety-critical path (i.e., its failure would prevent a safety-critical control action from executing): verify the TA describes a redundancy or failover mechanism. If a single-node configuration is used for a safety-critical component with no failover: flag as Violation Type A against the applicable SC-nnn availability constraint.

---

### Step 6 — Infrastructure and Deployment Safety Review

**6a. Network isolation:**
For each SC-nnn constraint requiring component isolation (from Phase C): verify the TA infrastructure design places the isolated components in a dedicated network zone, subnet, or security group that prevents uninstructed access. Verify that the network zone configuration prevents lateral movement from non-safety components to safety-critical components.

**6b. Deployment isolation:**
Verify that safety-critical components are not co-deployed on shared infrastructure with general-purpose components in ways that would allow resource contention to affect safety-critical availability (e.g., shared CPU on a container host, shared database cluster with no resource limits).

**6c. Supply chain risk:**
For any technology component that is a commercial third-party service (SaaS, cloud-managed service): verify the TA acknowledges the dependency and describes a contingency for service unavailability (graceful degradation, local fallback, provider SLA reference). If the component is on a safety-critical path and has no contingency: flag as Violation Type A.

---

### Step 7 — Author New Safety Constraints (SCO §5 update)

For each new UCA, security architecture gap, and infrastructure finding from Steps 4–6 where no existing SC-nnn constraint covers it: author a new SC-nnn constraint. Phase D constraints are primarily:

- **Technical type:** Specific technology-level requirements (e.g., "TC-012 identity provider must support high availability deployment with at least two replicas in separate availability zones to satisfy SC-031").
- **Operational type:** Configuration and operational requirements (e.g., "Audit log retention must be configured to a minimum of [X] days per regulatory standard [Y]").
- **Regulatory type:** Technology-level regulatory obligations identified during the security architecture review.

---

### Step 8 — Update SCO with Phase D Content

Update the SCO document to produce `sco-D-0.1.0.md` (draft):

- §5: Add new SC-nnn constraints from Steps 4b, 5, 6, and 7. Retain all Phase A/B/C constraints verbatim.
- §6: Add Level 3 control structure entries from Step 4a. Retain all Phase A/B/C entries.
- §7: Add Level 3 UCA-nnn records from Step 4b. Retain all Phase A/B/C UCAs.
- §8: Add LS-nnn loss scenarios for each new Level 3 UCA. Retain all prior loss scenarios.
- §9: Update compliance requirements with technology-level control references (specific controls that satisfy regulatory obligations).
- §10: Add new open safety findings from Steps 3–6. Close findings from Phase C addressed in the TA.
- §11: Add Phase D gate summary when gate vote is cast.

---

### Step 9 — Cast D→E Gate Vote

**Approve** if: all Violation Type A findings from Steps 3–6 are resolved, the TA security architecture section is present and satisfies all applicable Phase C authentication, authorisation, and encryption constraints, the infrastructure design addresses all safety-critical single points of failure, and no blocking SF-nnn items remain in SCO §10.

**Conditional** if: Violation Type B findings exist (coverage gaps in areas to be addressed in Phase E/F/G), but no Violation Type A conflicts. Specify: the gap, the expected Phase (E, F, or G), and deadline.

**Veto** if: one or more Violation Type A findings remain after SwA revision. Specifically:
- TA security architecture section is absent (blocking — TA cannot be gated without security architecture).
- An authentication or encryption constraint is violated by the technology selection with no mitigation described.
- A safety-critical technology component has no redundancy mechanism and its failure would violate a safety-critical SC-nnn availability constraint.
- An ADR overrides an SCO Phase C constraint without documented user risk acceptance.

Emit `gate.vote_cast` for D→E gate. If approve or conditional: promote SCO Phase D to `sco-D-1.0.0.md`. Emit `artifact.baselined` for SCO Phase D update. Produce Gate Record `gr-D-E-1.0.0.md`. Emit `artifact.baselined` for Gate Record. Emit `handoff.created` to PM and to SwA (structured feedback on TA violations).

---

### Step 10 — Revisit Handling (trigger="revisit" only)

If `trigger="revisit"` and `phase_visit_count > 1`:

1. Read EventStore gate history to identify which TA or ADR sections changed.
2. Read prior SCO Phase D version.
3. Apply Steps 2–8 only to changed sections. Preserve all non-affected SCO content verbatim.
4. Update only SCO constraints, UCAs, and findings affected by the changes.
5. Increment SCO version and re-cast D→E gate vote.
6. If revisit is triggered by a technology change that affects a previously vetoed finding: confirm whether the revision satisfies the named SC-nnn. If yes: approve. If not: second veto (enter Feedback Loop Iteration 2).

---

## Feedback Loop

**Maximum iterations: 2.** After Iteration 2 without resolution: raise ALG-010 (inter-agent deadlock) to PM.

**Iteration 1:** CSCO emits `gate.vote_cast (veto)` citing specific SC-nnn and structured feedback on TA violations. SwA revises TA and/or ADR Register and re-baselines. SwA emits `artifact.baselined` for revised artifacts.

**Iteration 2:** CSCO reviews only the sections SwA revised. If all Violation Type A findings resolved: approve. If any remain: cast second veto.

**Termination conditions:**
- **Satisfied:** All Violation Type A findings resolved by SwA revision. CSCO emits `gate.vote_cast (approve)`. Loop closes.
- **User risk acceptance:** User explicitly accepts residual risks after PM adjudication. CSCO records acceptance in SCO §10 and approves. Loop closes.
- **Deadlock (ALG-010):** Raised to PM after Iteration 2. CSCO veto stands during adjudication.
- **ALG-001 (unmitigatable failure mode):** If SwA demonstrates that a technology-level safety constraint cannot be satisfied by any available technology alternative and CSCO cannot identify a feasible mitigation: CSCO raises ALG-001 and escalates to PM and user. Loop transfers to user for scope/risk decision.

### Personality-Aware Conflict Engagement

**CSCO ↔ SwA (safety constraint vs technology choice) — primary tension:**

This is the highest-tension gate in the engagement. SwA has detailed technology expertise and may resist CSCO's safety findings on the grounds that: (a) the technology choice is the only viable option for the required performance characteristics, (b) the security constraint is overstated for the actual risk level, (c) the failure mode CSCO identifies is theoretical and not realistic in practice.

CSCO's engagement approach for each case:

**(a) Performance vs safety trade-off:** CSCO's constraint specifies what the system must achieve (e.g., "data at rest must be encrypted"), not how (e.g., not "use AES-256-GCM with PBKDF2 key derivation"). If SwA argues that a specific encryption mechanism degrades performance unacceptably, CSCO responds: demonstrate the performance impact with benchmarks; propose an alternative encryption approach that satisfies the constraint at acceptable performance; or document the performance trade-off for user risk acceptance. CSCO does not accept "encryption is too slow" as a constraint waiver without evidence and user sign-off.

**(b) Risk level dispute:** SwA may argue that a threat model consideration CSCO is requiring mitigation for is low-probability or not applicable to this system's threat environment. CSCO's response: present the hazard, the loss scenario, and the constraint. If SwA has a documented threat model that assigns low probability to the scenario: CSCO reviews the threat model. If the threat model is credible and the residual risk is within an acceptable range: CSCO may issue a conditional approval with the documented threat model as evidence. If the threat model is absent or its assumptions are not validated: CSCO maintains the constraint.

**(c) Theoretical failure mode:** CSCO's analysis identifies failure modes based on the technology category's known failure characteristics (e.g., eventual consistency in distributed databases producing stale reads in safety-critical query paths). SwA may argue the failure mode is theoretical for this system's load profile. CSCO's response: agree on a test during Phase G (Phase G spot-check or QA Compliance Assessment item) that would confirm the failure mode is not realised under realistic conditions; issue a conditional approval with the Phase G verification as the condition. CSCO does not maintain a Phase D veto for a failure mode that will be verified in Phase G, provided the Phase G verification condition is specific and testable.

**CSCO ↔ PM (Phase D gate delay):**

Phase D typically has the longest gate review period because of the breadth of technology safety analysis. PM may push for a provisional gate passage to allow Phase E planning to begin. CSCO's engagement: CSCO cannot pass a gate with unresolved Violation Type A findings. However, CSCO can issue conditional approval (Phase E/F planning activities can proceed in parallel with Phase D veto resolution) for non-blocking findings. CSCO distinguishes explicitly: which findings block Phase E commencement and which do not.

---

## Algedonic Triggers

- **ALG-001 (S1 — Safety-Critical):** A technology selection creates an unmitigatable safety-critical failure mode — for example, a safety-critical control path depends on a single third-party managed service with no fallback, and the system's safety constraint requires continuous availability. SwA has been unable to identify any alternative technology or mitigation approach after Iteration 1. Raised immediately with concurrent escalation to PM and user. Phase E does not begin until the technology design is revised or the user explicitly accepts the risk.
- **ALG-014 (S1 — Safety-Critical):** A safety-critical technology change is required (e.g., a critical ADR revision to address a previously unknown CVE) and CSCO is unavailable for review at the time the change is initiated. Raised by PM or SwA to PM (halt change; document; await CSCO). CSCO reviews this trigger on resumption and acts within current sprint.
- **ALG-010 (S3 — Inter-Agent Deadlock):** After two iterations, CSCO and SwA cannot agree on whether a technology choice satisfies an SCO constraint. Raised to PM for adjudication within current sprint.

---

## Outputs

| Artifact | Artifact ID | Destination | EventStore Event |
|---|---|---|---|
| Safety Constraint Overlay — Phase D Update | `SCO-D-1.0.0` | `safety-repository/safety-constraint-overlay/sco-D-1.0.0.md` | `artifact.baselined` |
| STAMP/STPA Analysis — Phase D Update | `sa-001-D.md` | `safety-repository/stamp-stpa/sa-001-D.md` | `artifact.baselined` |
| Gate Record — D→E | `GR-D-E-1.0.0` | `safety-repository/gate-records/gr-D-E-1.0.0.md` | `artifact.baselined` |
| Gate Vote — D→E | (event payload) | EventStore | `gate.vote_cast` |
| Structured feedback to SwA (TA and ADR violations) | (handoff records) | engagements/<id>/handoff-log/ | `handoff.created` |

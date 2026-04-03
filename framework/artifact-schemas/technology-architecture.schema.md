# Schema: Technology Architecture (`TA`)

**Version:** 2.0.0
**ADM Phase:** D
**Owner:** Software Architect / Principal Engineer
**Consumed by:** Implementation Plan (IP), Architecture Contract (AC), Safety Constraint Overlay (SCO update), DevOps/Platform Engineer (environment provisioning)

---

## 1. Purpose

The Technology Architecture defines the concrete technology stack, infrastructure topology, platform services, and deployment model that realise the application and data entities from Phase C. Phase D is the transition point from technology-independent ABBs to SBB candidates: specific products, platforms, and infrastructure patterns are selected here and recorded in Architecture Decision Records (ADRs). The Technology Architecture is the primary input for implementation planning (Phase E/F) and directly governs the DevOps/Platform Engineer's work.

Under ERP v2.0 the Technology Architecture is the set of entity, connection, ADR, and overview files produced in the **technology-repository** during Phase D. Entity files live under `technology-repository/model-entities/technology/`. ADRs live under `technology-repository/decisions/`. An overview document (`technology-repository/overview/ta-overview.md`) provides the cross-phase handoff summary.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| Application Architecture (`AA`) | Solution Architect | Baselined |
| Data Architecture (`DA`) | Solution Architect | Baselined |
| Architecture Principles Register (`PRI-nnn` entities) | Solution Architect | Baselined |
| Safety Constraint Overlay (`SCO`) — Phase C update | CSCO | Baselined |
| Technology standards and constraints (from SIB) | Software Architect/PE | Draft acceptable |

---

## 3. ERP Entity Output

Phase D produces entity files across the technology layer of the **technology-repository**. All files follow the universal format in `framework/artifact-schemas/entity-conventions.md`.

### 3.1 Technology Layer Entities — `technology-repository/model-entities/technology/`

| Prefix | artifact-type | Directory | §content Required Sections |
|---|---|---|---|
| `NOD-nnn` | `technology-node` | `model-entities/technology/nodes/` | Name; Type (Server/Container/VM/Cloud/Device); Description; Deployment Zone (Production/Staging/Dev); Hosts (`SSW-nnn` list); Specs (CPU/RAM/storage if relevant) |
| `SSW-nnn` | `system-software` | `model-entities/technology/system-software/` | Name; Product; Version Constraint; Type (Runtime/Platform/OS/Middleware); Runs On (`NOD-nnn`); Lifecycle Risk (Low/Medium/High); End-of-Support Date |
| `TSV-nnn` | `technology-service` | `model-entities/technology/tech-services/` | Name; Type (Store/Queue/Cache/Gateway/Auth/Observability); Product; Realises (`APP-nnn` or `AIF-nnn`); Safety-Relevant (true/false) |
| `ARF-nnn` | `artifact` | `model-entities/technology/artifacts/` | Name; Type (Container Image/Package/Script/Config); Produced By (`APP-nnn`); Deployed To (`NOD-nnn`) |

**Component Types (for `TSV-nnn`):**
- **Store** — database, object storage, cache, message broker
- **Network** — load balancer, API gateway, VPN, CDN
- **Security** — identity provider, secrets manager, WAF, certificate authority
- **Observability** — metrics, logging, tracing, alerting

**Version Constraint notation:** Use `>=X.Y`, `==X.Y.Z`, or `~X.Y` patterns; empty means "latest stable". Pinning exact versions (`==X.Y.Z`) is mandatory for production deployments.

### 3.2 `§display` Requirements

Every `NOD-nnn`, `SSW-nnn`, and `TSV-nnn` must have a `### archimate` subsection in `§display` so `regenerate_macros()` includes them in the technology-repository's `_macros.puml`. Entities appearing in deployment or technology diagrams additionally need `### archimate` blocks.

---

## 4. Architecture Decision Records (ADRs)

ADRs are **repository-content artifacts** (frontmatter `artifact-type: adr`), not model-entity files. They live in `technology-repository/decisions/`.

Filename pattern: `ADR-nnn-<slug>.md`

Required frontmatter:
```yaml
---
artifact-type: adr
artifact-id: ADR-nnn
name: "<Title>"
version: <semver>
status: proposed | accepted | deprecated | superseded
superseded-by: ADR-nnn   # if superseded
phase-produced: D
owner-agent: SwA
produced-by-skill: <skill-id>
last-updated: <YYYY-MM-DD>
engagement: <engagement-id>
---
```

Required `§content` sections:
- **Context** — what problem or requirement drives this decision
- **Decision** — what was decided (specific product/pattern/approach)
- **Rationale** — why this option over alternatives; link to `PRI-nnn` constraints and `CST-nnn` constraints
- **Consequences** — what becomes easier/harder; risks introduced
- **Alternatives Considered** — other options evaluated and why rejected

**Mandatory ADRs** — one ADR is required for each of the following if in scope:
- Primary runtime/compute platform
- Primary data store per data classification level
- Authentication and authorisation approach
- Network boundary and ingress strategy
- Observability stack
- Any decision that overrides or constrains a `PRI-nnn` Architecture Principle

---

## 5. Connections Produced

Connection files are written to `technology-repository/connections/` subdirectories.

| Connection Type | Source → Target | Directory | Notes |
|---|---|---|---|
| `archimate-composition` | `NOD-nnn` → `SSW-nnn` | `connections/archimate/composition/` | Node hosts system-software |
| `archimate-assignment` | `NOD-nnn` → `TSV-nnn` | `connections/archimate/assignment/` | Node executes technology service |
| `archimate-realization` | `TSV-nnn` → `APP-nnn` | `connections/archimate/realization/` | Technology service realises application component |
| `archimate-realization` | `SSW-nnn` → `APP-nnn` | `connections/archimate/realization/` | Runtime/platform realises app component |
| `archimate-serving` | `TSV-nnn` → `TSV-nnn` | `connections/archimate/serving/` | Technology service dependencies |
| `archimate-access` | `TSV-nnn` → `ARF-nnn` | `connections/archimate/access/` | Service deploys/runs artifact |

---

## 6. Overview Document

SwA produces `technology-repository/overview/ta-overview.md` as a **repository-content artifact** (frontmatter `artifact-type: ta-overview`).

Required sections:
- **Summary Header** — YAML frontmatter per `repository-conventions.md §7`:
  - `artifact-type: ta-overview`; `safety-relevant: true` (always — technology choices have safety implications); `csco-sign-off: true` (always required)
  - `summary:` 2–4 sentences covering technology stack, infrastructure topology, key ADRs
  - `key-decisions:` ADR-nnn list; `open-issues:` list; `pending-clarifications:` list
- **Technology/Application Matrix** — `APP-nnn` rows × `TSV-nnn`/`NOD-nnn` columns (● primary; ○ auxiliary; — none).
- **Deployment Topology** — table: Deployment Zone / Technology Components / Application Components Hosted / Connectivity.
- **Technology Standards Catalog** — `STD-nnn | Standard Name | Type | Source | Applies To | Mandatory/Recommended`.
- **Technology Lifecycle Analysis** — `TSV-nnn`/`SSW-nnn` | Product | Version | End-of-Support | Upgrade Path | Risk Level. High-risk entries must have a mitigation ADR.
- **Technology Gap Analysis** — Domain / Baseline / Target / Gap / Resolution in Phase E/F.
- **Safety Constraint Overlay Cross-reference** — per `TSV-nnn` with `safety-relevant: true`: SCO Phase D section reference.

---

## 7. Quality Criteria

- [ ] Every `APP-nnn` from the Application Architecture has at least one `archimate-realization` connection to a `TSV-nnn` or `SSW-nnn`.
- [ ] All mandatory ADR types (§4) are present and in `accepted` status at phase gate.
- [ ] Every technology component with High lifecycle risk has a mitigation ADR.
- [ ] No technology component lacks a version constraint.
- [ ] CSCO sign-off present (`csco-sign-off: true` in `ta-overview.md`) — mandatory for all TA artifacts.
- [ ] The Deployment Topology covers Production at minimum plus one non-production environment.

---

## 8. Version History

| Version | Date | Change Summary |
|---|---|---|
| 1.0.0 | 2026-04-02 | Initial schema — monolithic artifact format |
| 2.0.0 | 2026-04-03 | Refactored to ERP v2.0; entities in technology-repository/technology/; ADRs in technology-repository/decisions/; connections in technology-repository/connections/ |

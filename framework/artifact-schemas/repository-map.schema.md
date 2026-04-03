# Schema: Repository Map (`REPO-MAP`)

**Version:** 1.0.0  
**ADM Phase:** Preliminary / A (bootstrap)  
**Owner:** Project Manager (bootstrap production); Solution Architect (architecture-level decisions)  
**Consumed by:** All agents (Discovery Layer 4); Implementing Developer (target selection); DevOps (pipeline configuration); SA (component-to-repo traceability)

---

## 1. Purpose

The Repository Map is the canonical register of all target project repositories participating in an engagement. It maps bounded contexts, architectural components, and service roles to concrete git repositories, documents inter-repository dependencies (API contracts, event schema sharing, shared libraries), and provides the access control table for each agent role.

This artifact is **required whenever an engagement has more than one target repository** (microservices, CQRS, microfrontend, monorepo-with-sub-modules, or multi-product change requests). For single-repo engagements it is optional but encouraged for completeness.

---

## 2. Inputs Required Before Authoring

| Input | Source | Minimum State |
|---|---|---|
| `engagements-config.yaml` `target-repositories` list | PM (configured at bootstrap) | All repos registered |
| Architecture Vision (`AV`) §3.2 scope statement | Solution Architect | Draft acceptable |
| Application Architecture (`AA`) §3 component list | Solution Architect | At least one component identified |
| `engagements/<id>/engagement-profile.md` | PM | Baselined |

---

## 3. Required Sections

### 3.1 Summary Header

Conforms to the universal format in `repository-conventions.md §7`. Required fields:
- `artifact-type: repository-map`
- `safety-relevant: false` (override to `true` if any repo contains safety-critical code)
- `multi-repo: true`
- `repo-count: <N>` — number of registered target repositories

### 3.2 Repository Registry

One entry per registered target repository:

```yaml
repositories:
  - id: <slug>                  # Matches engagements-config.yaml target-repositories[].id
    label: <string>             # Human-readable name (e.g., "Order Service")
    role: <role>                # See §3.2.1 Role Taxonomy
    domain: <string>            # Bounded context label (e.g., "orders", "payments", "ui-shell")
    url: <git-url>              # Remote git URL
    default-branch: <string>    # Default branch (e.g., main, master)
    local-clone-path: <path>    # Relative path from framework root
    primary: <bool>             # Exactly one repo should be primary: true
    tech-stack: [<string>, ...] # Primary languages/frameworks (e.g., [Python, FastAPI])
    status: active | inactive | planned | archived
    notes: <string>             # Optional free text
```

#### 3.2.1 Repository Role Taxonomy

| Role | Description |
|---|---|
| `monolith` | Single application encompassing all bounded contexts |
| `microservice` | Single bounded-context service with its own deployment lifecycle |
| `microfrontend` | Frontend application or feature module with its own deployment lifecycle |
| `bff` | Backend-for-Frontend — API aggregation layer serving a specific frontend |
| `event-store` | Event sourcing infrastructure (e.g., Kafka topics as code, EventStoreDB config) |
| `shared-lib` | Cross-service shared library (DTOs, contracts, common utilities) |
| `infrastructure` | IaC-only repository (Terraform, Helm charts, Kubernetes manifests) |
| `api-gateway` | API gateway configuration and routing rules |
| `data-platform` | Data pipeline, warehouse, or analytics infrastructure |
| `shared-schema` | Shared schema definitions (e.g., Avro schemas, Protobuf files, OpenAPI specs) |

### 3.3 Inter-Repository Dependency Map

Documents dependencies between registered repositories. Each dependency entry represents a directional coupling.

```yaml
dependencies:
  - from: <repo-id>           # Upstream (consumer / caller)
    to: <repo-id>             # Downstream (producer / provider)
    type: <dependency-type>   # See §3.3.1
    contract: <ref>           # Canonical contract reference (OpenAPI spec path, Avro schema path, etc.)
    notes: <string>           # Optional: nature of coupling, version constraints, etc.
```

#### 3.3.1 Dependency Type Taxonomy

| Type | Description |
|---|---|
| `api-call` | Synchronous HTTP/gRPC call — from calls to endpoint |
| `event-subscription` | Async event subscription — from consumes events published by to |
| `event-publication` | Async event publication — from publishes events consumed by to |
| `shared-library` | from imports a library artifact produced by to |
| `shared-schema` | from imports schema definitions from to |
| `database-shared` | from and to share a database (anti-pattern — document if exists) |
| `infrastructure` | from is deployed / configured by to (IaC dependency) |

### 3.4 Bounded Context Allocation

Maps logical bounded contexts (from Business Architecture) to one or more repositories:

```yaml
bounded-contexts:
  - context-id: <BC-NNN>      # References BA bounded context ID
    context-label: <string>   # Human-readable BC name
    repos: [<repo-id>, ...]   # Repos that implement this context
    notes: <string>           # Optional: split reasons, ownership notes
```

### 3.5 Change Impact Matrix

For multi-repo change requests (Phase H), documents which repositories are in scope per change record:

```yaml
change-impact:
  - change-record-id: <CR-NNN>
    repos-in-scope: [<repo-id>, ...]
    cross-repo-coordination: <string>  # e.g., "Order→Payment API contract must be versioned together"
```

This section is populated incrementally as Phase H change records are raised. At engagement bootstrap it is empty.

### 3.6 Access Control Summary

Summary view of agent access per repository (derived from `engagements-config.yaml`; do not duplicate verbatim — summarise deviations from the default access pattern):

```yaml
access-deviations:
  - repo-id: <repo-id>
    deviations:
      - agent: implementing-developer
        access: read-only     # deviation from default read-write (e.g., legacy protected repo)
        reason: <string>
```

---

## 4. Validation Rules

1. **Exactly one primary.** `primary: true` must appear exactly once across all `repositories[]` entries.
2. **No duplicate IDs.** All `repositories[].id` values must be unique within the engagement.
3. **All engagements-config repos represented.** Every `id` in `engagements-config.yaml target-repositories` must appear in `repositories[]`. No omissions.
4. **Dependency repos must be registered.** All `from` and `to` values in `dependencies[]` must reference ids present in `repositories[]`.
5. **Change impact refs must exist.** All `change-record-id` values in `change-impact[]` must reference CRs present in the architecture repository.
6. **Role taxonomy compliance.** All `role` values must be from the §3.2.1 taxonomy.

---

## 5. Discovery Annotations

Every field value in the Registry section that was inferred from a source must carry the appropriate annotation per `framework/discovery-protocol.md §5`:

- `[source: target-repo:<id> scan]` — inferred from scanning that repository
- `[source: engagements-config.yaml]` — read directly from config
- `[assumed: <text>]` — assumed; must be documented in summary header `assumptions` field

---

## 6. File Path

```
engagements/<id>/work-repositories/architecture-repository/repository-map.md
```

Owned by Solution Architect. PM produces the initial draft at bootstrap (§3.1 + §3.2 registry only, from `engagements-config.yaml`). SA completes §3.3 dependency map and §3.4 bounded context allocation during Phase A/B.

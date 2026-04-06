# Agent Runtime Specification

**Version:** 1.2.0  
**Status:** Approved — Pre-Stage 5  
**Last Updated:** 2026-04-05

---

## 1. Purpose

This document specifies how the agent and skill definition files (`agents/<role>/AGENT.md`, `agents/<role>/skills/<skill>.md`) are translated into running PydanticAI agents at runtime. It defines the system prompt assembly protocol, skill loading convention, tool set per agent, and the invocation pattern used by the PM supervisor to call specialist agents.

This spec is the authoritative reference for `src/agents/` implementations. Framework documents, AGENT.md files, and skill files are the *content source*; this document specifies *how that content is used at runtime*.

---

## 2. System Prompt Assembly Protocol

Each agent invocation is built from four independent layers, loaded in order. Layers are assembled by `src/agents/base.py` using PydanticAI's `Agent` class.

### Layer 1 — Role Identity (static `system_prompt`, ≈100–150 tokens)

**Source:** `agents/<role>/AGENT.md` frontmatter field `system-prompt-identity`  
**When loaded:** Once at agent construction time. Never changes during a session.  
**PydanticAI binding:** Static `system_prompt=` parameter on `Agent(...)`.

Contains:
- Who the agent is (name, abbreviation, authority domain)
- What repository it writes to
- Its VSM position in one sentence
- One non-negotiable behavioral constraint (e.g., "write only to X repository")

### Layer 2 — Runtime Behavioral Stance (second `@agent.system_prompt`, ≤350 tokens)

**Source:** The `### Runtime Behavioral Stance` subsection within `agents/<role>/AGENT.md §11`.  
**When loaded:** Once at agent construction time; the return value is fixed per agent class.  
**PydanticAI binding:** `@agent.system_prompt` decorator on a function that extracts and returns only the `### Runtime Behavioral Stance` subsection.

**Extraction contract:** `AgentSpec.load_personality(agent_id)` reads §11, locates the `### Runtime Behavioral Stance` heading, and extracts only the text under that heading (up to the next `###` or `##` heading). The rest of §11 — role-type taxonomy, inter-role tension maps, conflict engagement posture narrative — is **not** loaded at runtime. It is authoring documentation only.

**Required form of the subsection:** Imperative first-person voice, exactly three elements:
1. **Default bias** (1–2 sentences): what the agent defaults to when a trade-off is not resolved by skill instructions
2. **Conflict posture** (1 sentence): how the agent responds when another agent disputes its output
3. **Cross-cutting rule** (1 sentence): one behavioral rule applying across all skills and phases

**Token budget:** soft target ≤250 tokens; hard cap ≤350 tokens. `AgentSpec.load_personality()` raises `PersonalityBudgetExceededError` above the hard cap.

This is logically static but kept as a separate `@agent.system_prompt` callable for clarity — PydanticAI assembles it independently from the static Layer 1.

### Layer 3 — Active Skill Instructions (`@agent.instructions`, ≈400–700 tokens)

**Source:** Specific sections of `agents/<role>/skills/<skill>.md` — see §3 below.  
**When loaded:** At each `agent.run()` call, via `RunContext.deps.active_skill_id`.  
**PydanticAI binding:** `@agent.instructions` decorator on a function that reads `ctx.deps.active_skill_id` and calls `SkillLoader.load_instructions(skill_id)`.

PydanticAI's `instructions` are evaluated fresh for each agent run and are *not* included in `message_history` when a conversation continues — they are the "current task brief", not part of the accumulated context.

### Layer 4 — Artifact Context (per-invocation, variable ≈0–2,000 tokens)

**Source:** Work-repositories and enterprise-repository, accessed via `read_artifact` tool during Discovery Scan.  
**When loaded:** The agent performs the Discovery Scan (`framework/discovery-protocol.md §2`) as its first action within the skill's Step 0, using the `read_artifact` tool. Not pre-injected into the prompt — loaded on demand by the agent.

---

## 3. Skill Loading Protocol

### 3.1 Sections Loaded at Runtime (Layer 3)

The `SkillLoader.load_instructions(skill_id: str) → str` function extracts the following sections from the skill's Markdown file, in order:

| Section | Included | Notes |
|---|---|---|
| YAML frontmatter | **Yes** (compact) | Rendered as metadata: skill-id, invoke-when, trigger-phases, primary-outputs only |
| `## Inputs Required` | **Yes** | Agent must know what to look for in Discovery Scan |
| `## Steps` | **Yes** | The procedural instructions |
| `## Algedonic Triggers` | **Yes** (compact) | ALG-IDs with condition only; full descriptions are in `framework/algedonic-protocol.md` |
| `## Feedback Loop` | **Yes** | Includes `### Personality-Aware Conflict Engagement` subsections |
| `## Outputs` | **Yes** | Artifact names, paths, events to emit |
| `## Knowledge Adequacy Check` | **No** | Authoring guide; not a runtime directive |

### 3.2 Skill File Section Parsing

`SkillLoader` parses the Markdown using `## ` heading delimiters. Each `##`-level heading starts a section. The extractor collects content for included sections and skips excluded sections.

The extracted content is concatenated with the section heading preserved (so the agent can navigate the instructions by heading) and returned as a single string.

### 3.3 Skill Selection Logic

The Python routing layer selects a skill by evaluating `(agent_id, trigger_phases, current_phase)`:

1. Load `framework/agent-index.md` (cache; reload on engagement state change).
2. Filter skill entries where `agent == agent_id` AND `current_phase IN trigger-phases`.
3. If exactly one match: that is the active skill.
4. If multiple matches within the same phase (e.g., `SwA-PHASE-C-APP` and `SwA-PHASE-C-DATA`): the PM explicitly specifies `active_skill_id` in the invocation — see §5.
5. If no match: raise `SkillNotFoundError(agent_id, current_phase)`.

The `trigger-conditions` frontmatter field is a human/LLM-readable description of trigger logic; it is **not** parsed by the Python routing layer. The `trigger-phases` list is the authoritative machine-readable routing key.

### 3.4 Search-Space Guardrails (skills)

Skill inventory and load scope are constrained to keep routing and execution tractable:

- Per-role skill inventory target: <=12 skills per agent role.
- Runtime prompt load: exactly one active skill per invocation (`active_skill_id`); other skills are not injected.
- Routing prefilter: `framework/agent-index.md` is loaded first as a compact routing table; full skill markdown is loaded only for the selected skill.
- Authoring rule: if a role approaches the skill cap, split by trigger-phase or entry-point rather than adding broad multi-purpose skills.

Complexity classes are the Layer 3 budget governor:

- `simple`: <=600 tokens (soft), 720 (hard)
- `standard`: <=1200 tokens (soft), 1440 (hard)
- `complex`: <=2000 tokens (soft/hard)

If soft cap is exceeded, `SkillLoader` truncates low-priority sections (`Algedonic Triggers`, then `Feedback Loop`, then `Outputs`) and never truncates `Steps`. Hard-cap exceedance raises `SkillBudgetExceededError`, signaling that the skill should be split.

### 3.5 Skill Portability Boundary (intent vs executable workflow)

To keep skills reusable across workflow profiles while preserving deterministic execution:

- Skill markdown owns: domain procedure, output structure, quality/validation expectations, escalation semantics.
- Orchestration/runtime code owns: executable workflow gating, phase transition checks, dependency readiness checks, suspension/resume routing, retry policies.
- Frontmatter fields `invoke-when` and `trigger-conditions` are intent-level guidance and documentation.
- Frontmatter field `trigger-phases` remains the primary machine-routing key in this architecture profile.

Design rule: keep skill outputs strict and schema-bound, while moving environment- or engagement-specific workflow state logic into LangGraph/PM routing code.

---

## 4. `AgentDeps` Dataclass

All PydanticAI agents in this system share a common `AgentDeps` type. Defined in `src/agents/deps.py`:

```python
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from src.models.engagement import Engagement
from src.agents.protocols import EventStorePort
from src.events.replay import WorkflowState

@dataclass
class AgentDeps:
    engagement: Engagement         # full engagement config (Engagement object, not just ID)
    event_store: EventStorePort    # port — never the concrete EventStore (dependency inversion)
    active_skill_id: str           # e.g. "SA-PHASE-A" — set by PM before invocation
    workflow_state: WorkflowState  # current canonical state; rebuilt by replay before each run
    engagement_base_path: Path     # engagements/<id>/
    framework_path: Path           # framework/ directory
```

`engagement` carries the full `Engagement` object (not just `engagement_id: str`) so tools can access config without re-loading from disk. `event_store` is typed as `EventStorePort` (a `typing.Protocol`) not the concrete `EventStore` — this is required by CST-001 (No Framework Lock-In): the application layer must never depend on the infrastructure implementation. No `extra: dict` escape hatch — dependencies are explicit or not injected (no magic).

---

## 5. PydanticAI Agent Construction Pattern

Defined in `src/agents/base.py`. Each agent implementation (e.g., `src/agents/solution_architect.py`) calls `build_agent(agent_id)` and registers agent-specific tools.

```python
# src/agents/base.py (schematic)
from pydantic_ai import Agent, RunContext
from .deps import AgentDeps
from .skill_loader import SkillLoader

def build_agent(agent_id: str, model: str = "claude-sonnet-4-6") -> Agent[AgentDeps, str]:
    spec = AgentSpec.load(agent_id)           # parses AGENT.md frontmatter
    
    agent: Agent[AgentDeps, str] = Agent(
        model=model,
        deps_type=AgentDeps,
        system_prompt=spec.system_prompt_identity,  # Layer 1 — static
    )

    # Layer 2 — Runtime Behavioral Stance (subsection of §11 only; not the full §11)
    @agent.system_prompt
    def behavioral_stance(ctx: RunContext[AgentDeps]) -> str:
        return spec.load_personality(agent_id)   # ### Runtime Behavioral Stance subsection only

    # Layer 3 — Active skill instructions (fresh per run)
    @agent.instructions
    def active_skill(ctx: RunContext[AgentDeps]) -> str:
        return SkillLoader.load_instructions(ctx.deps.active_skill_id)

    return agent
```

### 5.1 Agent-Specific Tool Registration

After calling `build_agent(agent_id)`, each `src/agents/<role>.py` module adds role-specific tools via `@agent.tool`. See §6 for tool sets.

### 5.2 Running an Agent

```python
# Invoked by LangGraph node (src/orchestration/nodes.py):
result = await sa_agent.run(
    user_prompt,          # Task description from PM decision
    deps=AgentDeps(
        engagement=engagement,          # Engagement object loaded from config
        event_store=event_store_port,   # EventStorePort injected into node
        active_skill_id="SA-PHASE-A",
        workflow_state=workflow_state,  # WorkflowState from replay
        engagement_base_path=Path("engagements/ENG-001"),
        framework_path=Path("framework"),
    )
)
```

---

## 6. Tool Set Per Agent

All tools are defined in `src/agents/tools/`. Tool event emission is **tool-transparent** — tools emit the appropriate EventStore events internally; skill instructions do not need to mention event emission explicitly.

### 6.0 Tooling Contract Boundary (authoring vs runtime)

Agent and skill markdown describes **tooling intent** (discover/search/filter/query/validate/write), not the immutable runtime function signatures. Runtime binding is code-owned in LangGraph + PydanticAI registration (`src/agents/`, `src/orchestration/`, `src/tools/mcp_model_server.py`, `src/tools/model_mcp/`, `src/tools/model_write/`).

For model entity/connection/diagram workflows, the current canonical MCP tool mapping is:

| Intent | Canonical MCP tools |
|---|---|
| Discovery and filtering | `model_query_stats`, `model_query_list_artifacts` |
| Content search/query | `model_query_search_artifacts`, `model_query_read_artifact` |
| Graph query | `model_query_find_connections_for`, `model_query_find_neighbors` |
| Validation | `model_verify_file`, `model_verify_all` |
| Deterministic model writes | `model_write_help`, `model_create_entity`, `model_create_connection`, `model_create_diagram` |

Legacy/alias names in skills (for example `list_artifacts`, `search_artifacts`, `read_artifact`, `write_artifact`, `validate_diagram`) are compatibility hints, not hard runtime contracts.

### 6.0a Search-Space Guardrails (tools)

Tool exposure is intentionally grouped and bounded to keep per-agent tool search-space small:

- Tool registration is role-scoped (no global all-tools surface).
- Universal tools provide the minimum common capability set; specialized tools are added only for roles that need them.
- Per-agent exposed tool budget target: <=30 callable tools.
- Preferred operating range: 12-26 tools per role (current architecture roles stay within this range).

When a new capability is needed, add it to an existing tool family where possible before creating a new top-level tool. If the budget would be exceeded, split role responsibilities or consolidate overlapping tools.

### 6.1 Universal Tools (all agents)

#### Discovery and Read

| Tool | Function signature | Description |
|---|---|---|
| `read_artifact` | `(id_or_path: str, mode: Literal["summary","full"]) → str` | Resolves artifact-id → path via ModelRegistry; `summary` = frontmatter + first two §content sections (≈200–400 tokens); `full` = entire file. Log reason when using `full`. |
| `list_artifacts` | `(**filter) → list[ArtifactRecord]` | Queries ModelRegistry in-memory frontmatter cache; returns metadata records without loading bodies. Supported filters: `artifact_type`, `status`, `domain`, `safety_relevant`, `phase_produced`, `engagement` (`"enterprise"` to scope to enterprise repo). **Primary discovery tool when artifact type is known.** |
| `search_artifacts` | `(query: str, **filter) → list[tuple[ArtifactRecord, str]]` | Queries ModelRegistry FTS5 index over `§content` blocks; optional semantic tier when corpus ≥ 50 artifacts. Returns ranked `(record, snippet)` pairs. **Primary discovery tool when artifact type is uncertain or discovery is by concept.** Same metadata filters as `list_artifacts`. |
| `list_connections` | `(source: str \| None, target: str \| None, artifact_type: str \| None) → list[ArtifactRecord]` | ModelRegistry query scoped to `connections/`; all params optional. Use to discover relationships between known entities. |
| `query_event_store` | `(event_types: list[str], phase: str \| None, limit: int = 20) → list[dict]` | Filters events by type and optionally phase; read-only. Used in Layer 5 discovery to retrieve CQ answer payloads and handoff content. |

#### Learning Tools

| Tool | Function signature | Description |
|---|---|---|
| `query_learnings` | `(phase: str, artifact_type: str, domain: str \| None, expand_related: bool = True) → list[str]` | Retrieves top-5 correction texts from `LearningStore`. Applies metadata filter, graph expansion via `related` links, and optional semantic tier. Call as Step 0.L before any Discovery Scan. Governed by `framework/learning-protocol.md §9`. |
| `record_learning` | `(entry: LearningEntry) → str` | Validates entry against schema (9 rules); assigns `<ROLE>-L-NNN` id; writes to `LearningStore` AND file; emits `learning.created`. Call in `## Feedback Loop` on feedback-triggered revision. Governed by `framework/learning-protocol.md §8`. |

#### Interaction and Escalation

| Tool | Function signature | Description |
|---|---|---|
| `raise_cq` | `(question: str, target: str, blocking: bool, blocked_task: str \| None) → str` | Raises a CQ; emits `cq.raised`. Only valid after Discovery Scan confirms information is unavailable. |
| `raise_algedonic` | `(trigger_id: str, detail: str, severity: Literal[1,2,3]) → None` | Raises an algedonic signal; emits `alg.raised`. |

#### Framework and Standards

| Tool | Function signature | Description |
|---|---|---|
| `read_framework_doc` | `(doc_name: str) → str` | Reads any file from `framework/`; cached. Used to load skill templates, protocol references, PUML templates. |
| `discover_standards` | `() → list[str]` | Reads all files from `technology-repository/coding-standards/` and `enterprise-repository/standards/`; returns contents. **SA, SwA, DE, DO only.** Step 0.S per `framework/discovery-protocol.md §9`. |
| `list_target_repositories` | `() → list[dict]` | Reads `engagements-config.yaml`; returns all registered repos with `id`, `label`, `role`, `domain`, `primary`, `clone-path`. All agents. |

### 6.2 Write Tools (scoped to owned repository)

All agents use a single `write_artifact` interface for creation and updates. Status lifecycle transitions (baselining, deprecation, deletion) use dedicated tools so that event emission is unambiguous. The implementation (`ArtifactReadWriterPort`) enforces path constraints, validates ERP frontmatter and `§content`/`§display` structure on every write, and keeps ModelRegistry in sync synchronously. Writing outside the agent's owned repository path raises `RepositoryBoundaryError` and emits `ALG-007`.

**Artifact status lifecycle — enforced by the port layer:**

| Status | Meaning | Diagram visibility | Cross-agent reference |
|---|---|---|---|
| `draft` | Under active construction in the current sprint | Permitted in `draft` diagrams; **not permitted in `baselined` diagrams** (E306/E307) | Not permitted outside the producing sprint context |
| `baselined` | Approved and stable; sprint-gate passed | Permitted | Permitted for all agents |
| `deprecated` | No longer current; kept for audit | Must be removed from all diagrams | Not permitted in new connections or references |

| Tool | Function signature | Description |
|---|---|---|
| `write_artifact` | `(path: str, content: str, *, upload_refs: list[str] \| None = None) → ArtifactRecord` | Creates or updates an entity/connection/diagram file. `status` must be `draft` — this tool does not perform status transitions. Auto-emits `artifact.created` (new file) or `artifact.updated` (existing file, no status change). Auto-extracts `source_evidence`. Auto-emits `entity.confirmed` for reverse-arch skills. |
| `baseline_artifact` | `(artifact_id: str) → ArtifactRecord` | Transitions status from `draft` → `baselined`. Emits `artifact.baselined` with `sprint_id` from current AgentDeps. Raises `InvalidStatusTransition` if artifact is not currently `draft`. Only valid at sprint close or on explicit PM instruction. |
| `deprecate_artifact` | `(artifact_id: str, rationale: str) → ArtifactRecord` | Transitions status from `baselined` → `deprecated`. `rationale` is required (raises `MissingDeprecationRationale` if absent). Emits `artifact.deprecated`. The agent must also update or deprecate all diagrams and connections that reference this artifact before calling this tool. |
| `delete_artifact` | `(artifact_id: str, rationale: str) → None` | Physically removes the file. Only permitted when `status == deprecated` (`PrematureDeleteError` otherwise). Emits `artifact.deleted`. Removes artifact from ModelRegistry. |

**Path constraints per agent** (enforced by `ArtifactReadWriterPort`):

| Agent | Permitted write path |
|---|---|
| PM | `project-repository/` |
| SA | `architecture-repository/` |
| SwA | `technology-repository/` |
| DO | `devops-repository/` |
| DE | `delivery-repository/` (metadata only) |
| QA | `qa-repository/` |
| CSCO | `safety-repository/` |

### 6.3 Target Project Repository Tools

Multi-repo aware. `repo_id=None` defaults to primary repo in multi-repo engagements; mandatory for write operations.

| Tool | Access | Description |
|---|---|---|
| `read_target_repo` | All agents (read) | Read any file from `engagements/<id>/target-repos/<repo-id>/`. `repo_id=None` → primary repo. |
| `write_target_repo` | DE, DO only | Write to target-repo feature branch or IaC files. `repo_id` mandatory. |
| `scan_target_repo` | All agents | Discovery Layer 4 per-repo scan; emits `source.scanned`. `repo_id=None` → primary. |
| `execute_pipeline` | DO only | Trigger deployment pipeline run; returns outcome. |
| `create_worktree` | DE, DO | Create an isolated git worktree for agent code changes per sprint. |

### 6.4 Diagram and Matrix Tools (SA, SwA)

Use diagram tools for viewpoint visualisations (`.puml`) and matrix tools for dense many-to-many mappings (`.md` tables). Prefer matrix output when the goal is coverage/traceability across many IDs and visual topology is not required.

| Tool | Function signature | Description |
|---|---|---|
| `model_create_matrix` | `(name, purpose, matrix_markdown, phase_produced, owner_agent, artifact_id, ...) → dict` | Writes a matrix artifact in `diagram-catalog/diagrams/*.md`. Accepts ID-authored markdown and can infer/link `entity-ids-used` for navigation and verification. |
| `regenerate_macros` | `(repo_path: str) → None` | Scans all entity `§display ###archimate` blocks via ModelRegistry; rewrites `_macros.puml`. Called automatically by `write_artifact` when an entity's archimate display spec changes. |
| `generate_er_content` | `(entity_ids: list[str]) → str` | Reads each entity's `§display ###er` block; returns PUML class declarations for paste into ER diagram. |
| `generate_er_relations` | `(connection_ids: list[str]) → str` | Reads each er-connection's `§display ###er` block; returns cardinality lines. |
| `validate_diagram` | `(puml_file_path: str) → list[str]` | Checks all PUML aliases resolve to ModelRegistry entity-ids with appropriate `§display ###<language>` sections; confirms `!include _macros.puml` present; returns error list. ALG-C03 if alias has no backing entity — extend the model, do not remove the alias. |
| `render_diagram` | `(puml_file_path: str) → Path` | Invokes local PlantUML CLI; writes SVG to the sibling `diagram-catalog/rendered/` directory for the source path under `diagram-catalog/diagrams/` (never `diagrams/rendered/`). Run at sprint boundary. |

### 6.5 PM-Only Orchestration Tools

| Tool | Description |
|---|---|
| `invoke_specialist(agent_id, skill_id, task)` | Runs a specialist PydanticAI agent (agent-as-tool); emits `specialist.invoked`; returns agent output. |
| `batch_cqs(cq_ids)` | Collects open CQs; emits `cq.batched`; formats for user presentation. |
| `evaluate_gate(gate_id, votes)` | Checks gate hold conditions; emits `gate.evaluated`; calls `create_snapshot("gate.evaluated")` on pass; returns pass/hold/escalate. |
| `record_decision(rationale)` | Writes to `project-repository/decision-log/`; emits `decision.recorded`. |
| `trigger_review()` | Surfaces sprint review; emits `review.pending`. |

---

## 7. Agent-as-Tool Invocation Pattern (PM calling Specialists)

The PM supervisor calls specialist agents using `invoke_specialist` — a PydanticAI tool that wraps a specialist `agent.run()` call. This is the primary coordination mechanism.

```python
# src/agents/tools/pm_tools.py (schematic)
async def invoke_specialist(
    ctx: RunContext[AgentDeps],
    agent_id: str,   # e.g. "SA"
    skill_id: str,   # e.g. "SA-PHASE-A"
    task: str,       # Natural language task description
) -> str:
    """
    Invoke a specialist agent for a specific skill task.
    Emits specialist.invoked before running; specialist.completed after.
    All EventStore events are emitted by the specialist during execution.
    """
    ctx.deps.event_store.record_event(WorkflowEvent(
        event_type="specialist.invoked",
        agent=agent_id, skill_id=skill_id, payload={"task": task},
    ))
    specialist_agent = AGENT_REGISTRY[agent_id]
    state, _ = ctx.deps.event_store.replay_from_latest_snapshot()
    specialist_deps = AgentDeps(
        **asdict(ctx.deps),
        active_skill_id=skill_id,
        workflow_state=state,
    )
    result = await specialist_agent.run(task, deps=specialist_deps)
    ctx.deps.event_store.record_event(WorkflowEvent(
        event_type="specialist.completed",
        agent=agent_id, skill_id=skill_id, payload={},
    ))
    return result.data
```

**Note on nesting depth:** PydanticAI's agent-as-tool pattern supports one level of nesting (parent calls child). Specialist agents called via `invoke_specialist` do not themselves call other agents. All cross-role coordination flows through the PM supervisor.

---

## 8. Structured Output Types

For Phase G and other structured outputs, agents use Pydantic models as `result_type` instead of plain `str`. The schema for each artifact type is defined in `src/models/` (one module per artifact, derived from `framework/artifact-schemas/`).

When `result_type` is a Pydantic model, PydanticAI enforces the schema via tool use (internal `final_result` tool). The EventStore receives the structured artifact as a JSON payload in the `artifact.baselined` event.

For conversational/diagnostic outputs (e.g., CQ responses, feedback records), `result_type=str` is used.

---

## 9. Concurrency Model

For Phase G Solution Sprints where DE, DO, and QA operate in parallel:

- **Option A (default):** PM invokes DE, DO, QA sequentially using `invoke_specialist`. Simple, no concurrency issues, lower throughput.
- **Option B (LangGraph parallel):** DE, DO, and QA run as concurrent LangGraph nodes using `Send` API for fan-out. Requires LangGraph; see `framework/orchestration-topology.md §4`.

Option A is implemented first. Option B is introduced only if sequential throughput is insufficient for real-world sprints.

---

## 10. Token Budget Guidelines

| Context component | Target tokens |
|---|---|
| Layer 1 (Role Identity) | 100–150 |
| Layer 2 (Behavioral Stance) | 200–250 |
| Layer 3 (Active Skill Instructions) | Complexity class governed: simple <=600, standard <=1200, complex <=2000 |
| Artifact context (summary mode) | 200–400 per artifact, max 3 artifacts |
| Artifact context (full mode) | Up to 2,000 per artifact, max 1 artifact |
| Conversation history | Rolling window; prune to last 8,000 tokens |
| **Total system context target** | **<6,000 tokens per invocation** |

Agents that exceed 6,000 tokens of system context must log a warning. Artifacts retrieved in full mode that push context above 10,000 tokens must trigger a CQ for the summary to be confirmed as insufficient.

---

## 11. Cross-References

- `framework/orchestration-topology.md` — LangGraph graph structure and PM supervisor pattern
- `framework/agent-personalities.md` — personality profiles (source for Layer 2)
- `framework/discovery-protocol.md` — Discovery Scan protocol (Step 0 of every skill)
- `framework/clarification-protocol.md` — CQ lifecycle (used by `raise_cq` tool)
- `framework/algedonic-protocol.md` — algedonic trigger taxonomy (used by `raise_algedonic` tool)
- `src/agents/` — Python implementations of this spec
- `src/agents/skill_loader.py` — `SkillLoader` class
- `src/agents/deps.py` — `AgentDeps` dataclass
- `src/agents/base.py` — `build_agent()` factory

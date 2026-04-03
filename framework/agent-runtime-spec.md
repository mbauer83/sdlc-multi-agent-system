# Agent Runtime Specification

**Version:** 1.0.0  
**Status:** Approved — Pre-Stage 5  
**Last Updated:** 2026-04-02

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
4. If multiple matches within the same phase (e.g., `SA-PHASE-C-APP` and `SA-PHASE-C-DATA`): the PM explicitly specifies `active_skill_id` in the invocation — see §5.
5. If no match: raise `SkillNotFoundError(agent_id, current_phase)`.

The `trigger-conditions` frontmatter field is a human/LLM-readable description of trigger logic; it is **not** parsed by the Python routing layer. The `trigger-phases` list is the authoritative machine-readable routing key.

---

## 4. `AgentDeps` Dataclass

All PydanticAI agents in this system share a common `AgentDeps` type. Defined in `src/agents/deps.py`:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from src.events.event_store import EventStore
from src.events.models.state import WorkflowState

@dataclass
class AgentDeps:
    engagement_id: str
    event_store: EventStore
    active_skill_id: str          # e.g. "SA-PHASE-A" — set by PM before invocation
    workflow_state: WorkflowState  # current snapshot; refreshed before each run
    engagement_base_path: Path    # engagements/<id>/
    framework_path: Path          # framework/ directory
    # Per-agent: additional deps injected by factory
    extra: dict = field(default_factory=dict)
```

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
# Invoked by PM supervisor (src/orchestration/pm_supervisor.py):
result = await sa_agent.run(
    user_prompt,          # Task description from PM
    deps=AgentDeps(
        engagement_id="ENG-001",
        event_store=store,
        active_skill_id="SA-PHASE-A",
        workflow_state=store.current_state(),
        engagement_base_path=Path("engagements/ENG-001"),
        framework_path=Path("framework"),
    )
)
```

---

## 6. Tool Set Per Agent

All tools are defined in `src/agents/tools/`. Each tool emits the appropriate EventStore event on use (e.g., `artifact.drafted` on first write, `source.queried` on external source read).

### 6.1 Universal Tools (all agents)

| Tool | Function signature | Description |
|---|---|---|
| `read_artifact` | `(path: str, mode: Literal["summary","full"]) → str` | Reads artifact from any work-repository (confidence-threshold protocol) |
| `query_event_store` | `(event_type: str, limit: int = 20) → list[dict]` | Filters events from EventStore; read-only |
| `emit_event` | `(event_type: str, payload: dict) → str` | Emits an event; validates against EventRegistry before insert |
| `raise_cq` | `(question: str, target: str, blocking: bool, blocked_task: str) → str` | Raises a CQ; emits `cq.raised` |
| `raise_algedonic` | `(trigger_id: str, detail: str, severity: int) → None` | Raises an algedonic signal; emits `alg.raised` |
| `read_framework_doc` | `(doc_name: str) → str` | Reads any file from `framework/`; cached |
| `read_skill` | `(skill_id: str) → str` | Reads another skill's instructions (cross-reference; rare) |

### 6.2 Write Tools (scoped to owned repository)

Each agent's write tools are path-constrained to its `owns-repository` path. Write outside that path raises `RepositoryBoundaryError` and emits `ALG-007`.

| Agent | Write tool | Writes to |
|---|---|---|
| PM | `write_project_artifact` | `project-repository/` |
| SA | `write_architecture_artifact` | `architecture-repository/` |
| SwA | `write_technology_artifact` | `technology-repository/` |
| DO | `write_devops_artifact` | `devops-repository/` |
| DE | `write_delivery_metadata` | `delivery-repository/` (metadata only) |
| QA | `write_qa_artifact` | `qa-repository/` |

### 6.3 Target Project Repository Tools (DE and DO only)

| Tool | Access | Description |
|---|---|---|
| `read_target_repo` | DE (read), DO (read), SwA (read for EP-G RAR) | Read any file from `engagements/<id>/target-repo/` |
| `write_target_repo` | DE only | Write application code to target-repo feature branch |
| `execute_pipeline` | DO only | Trigger deployment pipeline run; returns pipeline outcome |

### 6.4 PM-Only Orchestration Tools

| Tool | Description |
|---|---|
| `invoke_specialist(agent_id, skill_id, task, deps)` | Runs a specialist PydanticAI agent (agent-as-tool); returns agent output and usage |
| `batch_cqs(cq_ids)` | Collects open CQs and formats them for user presentation |
| `evaluate_gate(gate_id)` | Checks gate hold conditions; emits `gate.evaluated`; returns pass/hold/escalate |
| `record_decision(decision, rationale, raci_ref)` | Writes to `project-repository/decision-log/` |

---

## 7. Agent-as-Tool Invocation Pattern (PM calling Specialists)

The PM supervisor calls specialist agents using `invoke_specialist` — a PydanticAI tool that wraps a specialist `agent.run()` call. This is the primary coordination mechanism.

```python
# src/agents/tools/invoke_specialist.py (schematic)
async def invoke_specialist(
    ctx: RunContext[AgentDeps],
    agent_id: str,         # e.g. "SA"
    skill_id: str,         # e.g. "SA-PHASE-A"
    task: str,             # Natural language task description
) -> str:
    """
    Invoke a specialist agent for a specific skill task.
    
    Use this to delegate phase work to the accountable agent.
    The specialist will execute its skill procedure and return a 
    structured result summary. All EventStore events are emitted
    by the specialist during execution.
    """
    specialist_agent = AGENT_REGISTRY[agent_id]   # pre-built Agent instances
    specialist_deps = AgentDeps(
        **asdict(ctx.deps),
        active_skill_id=skill_id,
        workflow_state=ctx.deps.event_store.current_state(),
    )
    result = await specialist_agent.run(task, deps=specialist_deps)
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
| Layer 3 (Active Skill Instructions) | 400–700 |
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

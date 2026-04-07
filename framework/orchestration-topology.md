# Orchestration Topology

**Version:** 1.3.0  
**Status:** Approved — Pre-Stage 5  
**Last Updated:** 2026-04-08

---

## 1. Purpose

This document specifies how the multi-agent SDLC system is orchestrated at runtime: how agents are coordinated across ADM phases, how LangGraph models the ADM workflow, and how the PM supervisor coordinates specialist agents. It is the architectural reference for `src/orchestration/`.

The system uses a nested control architecture:
- **LangGraph (outer graph)** manages engagement lifecycle control: new vs resume, entry-point classification, engagement-type routing, suspend/resume, and completion.
- **LangGraph (engagement-type subgraphs)** manages mostly deterministic phase flows for EP-0 and warm-start/reverse-architecture entry paths.
- **LangGraph (phase/agent subgraphs)** manages per-phase specialist execution, fan-out/fan-in, and gate transitions.
- **PydanticAI (leaf nodes only)** executes specialist reasoning and artifact production under strict schema/result contracts.
- **EventStore** persists all state transitions. Graph nodes read and update state via events.

---

## 2. Coordination Model

### 2.1 Primary Model: PM Supervisor with Nested Subgraphs

The Project Manager is the supervisor authority, while execution is organized as nested LangGraph subgraphs instead of PM agent tool-calls to specialists. This keeps high-level coordination deliberative but phase execution deterministic and inspectable.

```
outer_graph (engagement lifecycle)
    → classify_entry_and_mode
    → run engagement_subgraph(ep_type)
            → run phase_subgraph(phase)
                    → leaf specialist node(s) using PydanticAI
            → evaluate gate / review / suspend-resume
    → close_or_resume
```

**Why this model:** PM remains the decision authority (VSM System 3), but deterministic flow control is encoded in graph topology rather than prompt-level routing behavior. This improves reproducibility, resumability, and selective fan-out.

### 2.2 Fan-Out/Fan-In inside Phase Subgraphs

Phase subgraphs may use LangGraph `Send` fan-out where independence exists (for example DE/DO/QA execution lanes in Phase G), followed by deterministic fan-in merge and gate evaluation.

```
Phase G Sprint node
  → Send("de_node", sprint_state)
  → Send("do_node", sprint_state)
  → Send("qa_node", sprint_state)
  ← merge results
  → evaluate sprint close
```

Fan-out is a topology decision in orchestration code, not a skill-level decision.

### 2.3 Engagement-Type Subgraphs

The outer graph selects one deterministic engagement-type subgraph before phase work begins:
- `ep0_greenfield_subgraph`
- `warm_start_subgraph` (EP-A through EP-F)
- `reverse_architecture_subgraph` (EP-G/EP-H)

Each engagement-type subgraph determines phase start conditions, warm-start ingestion, and required validations before entering the standard phase control loop.

### 2.4 Algedonic Bypass

Any agent node can emit an `alg.raised` EventStore event. The LangGraph routing function at each node exit checks for open algedonics and routes to `algedonic_handler_node` before normal phase progression. This implements the algedonic bypass without polling.

### 2.5 Workflow Control Ownership Boundary

Executable workflow control is owned by the orchestration harness (LangGraph nodes, routing functions, PM tool policies), not by skill prose.

- Skills define intent and output contracts (what to produce, required checks, quality bars).
- Orchestration code defines execution control (when to run, precondition enforcement, phase/state transitions, retries, suspension/resume).
- `invoke-when` and `trigger-conditions` in skill frontmatter are documentation hints; they do not replace runtime state-machine enforcement.

This separation keeps skills reusable across entry points and future workflow profiles while preserving deterministic governance.

### 2.6 Agent-Phase Workflow Decomposition Contract

Agent-phase workflows are authored as model-level behavior specifications, then implemented as nested LangGraph subgraphs.

- A workflow unit is defined by `(agent_id, phase, skill_id)`.
- Each workflow unit may be represented by one activity/BPMN diagram at the model level when branching or multi-party coordination is non-trivial.
- The runtime graph remains the execution authority; diagrams are binding design specifications for node/routing intent, not executable control planes.

Deterministic vs agentic mapping rules:

1. Deterministic step:
- Preconditions, transitions, and outputs are fully specified and machine-checkable.
- Implement as explicit LangGraph node logic and routing conditions.

2. Agentic step:
- Requires bounded reasoning, synthesis, or judgement under a selected skill.
- Implement as a specialist leaf node invocation using one active skill (`active_skill_id`).

3. Decision branch:
- Model as explicit branch outcomes.
- Implement as routing function predicates over graph state and/or PM decision payload.

4. Suspension/resume:
- Model as explicit waiting states (for example CQ answer or review decision).
- Implement through dedicated suspension/resume nodes and events (`phase.suspended`, `phase.resumed`).

5. Parallel lanes:
- Model only when independence exists.
- Implement via fan-out/fan-in topology (`Send`) with deterministic merge criteria.

Discovery/source usage in workflow units:

- Source scanning policy is phase-and-skill scoped by runtime context and tool contracts.
- External source breadth is configuration-driven and situative, not unconditional.
- CQ and feedback handling follows `framework/clarification-protocol.md` routing rules.

### 2.7 Interaction Class Routing Contract (Wave 1)

Runtime routing distinguishes interaction classes from retrieval behavior:

| Class | Initiated By | Runtime Routing Owner | Primary Runtime Path | Required Events | Blocking Behavior |
|---|---|---|---|---|---|
| User-facing Clarification Interaction (CQ) | Specialist or PM | PM + orchestration routing functions | `raise_cq` -> `cq_user_node` -> `route_after_cq` | `cq.raised`; `cq.batched` (optional); `phase.suspended` / `phase.resumed` when blocking | Blocking only when CQ is marked blocking |
| Agent-directed Coordination Interaction | Specialist or PM | PM + orchestration routing functions | PM decision path through specialist/gate/review/handoff nodes | `handoff.created`, `specialist.invoked`, `specialist.completed`, `decision.recorded`, `gate.evaluated`, `review.pending` | Non-blocking by default; PM can explicitly hold |

**Boundary (non-interaction):** Retrieval tool calls (`list/search/read/count/find`) are not interaction classes and are not routed via CQ logic. They execute as normal tool behavior within a node and follow discovery/tool contracts.

### 2.8 Subgraph Decomposition Matrix (Wave 2)

The runtime topology is decomposed into four workflow-unit tiers. For each tier, runtime ownership is explicit.

Implementation linkage: [@DOC:IMPLEMENTATION_PLAN#5c-orchestration-layer](../specs/IMPLEMENTATION_PLAN.md#5c--orchestration-layer).

| Workflow Unit Tier | Scope | Primary Responsibilities | Deterministic Owner | Agentic Owner | Branch Ownership | Suspend/Resume Ownership | Fan-Out/Fan-In Ownership |
|---|---|---|---|---|---|---|---|
| Outer lifecycle graph | Engagement lifecycle | Start/resume, engagement-mode dispatch, completion | LangGraph outer lifecycle nodes + routing | None | Routing functions in outer lifecycle graph | Outer lifecycle suspension/resume nodes | Not used at this tier |
| Engagement-type subgraph | Entry-point family control | Greenfield vs warm-start vs reverse-architecture flow | Engagement-type subgraph nodes and predicates | None | Engagement-type routing predicates | Engagement-type wait-state routing | Optional, only if engagement profile requires independent branches |
| Phase subgraph | Phase-local execution control | Specialist ordering, gate checkpoints, CQ/review gateways | Phase graph nodes + routing predicates | None at control layer | Phase routing functions | `cq_user_node` and review/gate routing functions | Phase topology design via `Send` and deterministic merge conditions |
| Specialist leaf node | Skill execution | Skill reasoning and artifact production | Input/output contract checks in leaf wrapper | Specialist PydanticAI invocation | PM decision selecting specialist/skill | Leaf returns control to graph; suspension enacted by graph nodes | Never owns fan-out topology |

### 2.9 Deterministic vs Agentic Checklist Per Workflow Unit (Wave 2)

Use this checklist when authoring or reviewing any workflow unit `(agent_id, phase, skill_id)`.

Implementation linkage: [@DOC:IMPLEMENTATION_PLAN#5c-orchestration-layer](../specs/IMPLEMENTATION_PLAN.md#5c--orchestration-layer).

| Checklist Item | Deterministic Step Requirement | Agentic Step Requirement | Runtime Owner |
|---|---|---|---|
| Preconditions | Machine-checkable predicates over `WorkflowState` and `SDLCGraphState` before execution | Explicitly bounded prompt scope and selected `active_skill_id` | Routing/node code for deterministic checks; PM + specialist runtime for agentic bounds |
| Event emissions | Required lifecycle events emitted by the infrastructure node/tool path | Specialist/tool events emitted transparently by called tools | Node implementation owner for lifecycle events; tool implementation owner for specialist events |
| Branch criteria | Predicate-based route outcomes are explicit and testable | PM decision payload fields are explicit (`next_action`, `specialist_id`, `skill_id`) | Routing functions + PM decision model |
| Fan-in merge criteria | Merge contract lists required lane outputs and gate preconditions | Not applicable as agentic responsibility | Phase subgraph implementation |
| Suspension entry invariant | Enter suspension only with explicit blocker cause and event emission (`phase.suspended`) | Agentic reasoning may request suspension via CQ/algedonic tools; graph applies it | CQ/algedonic nodes and routing functions |
| Suspension exit invariant | Resume only after unblocking evidence/event (`cq.answered`, review decision, or PM hold release) with `phase.resumed` when applicable | Agentic node never resumes itself; it requests via PM/tool path | Routing functions + PM orchestration decisions |

### 2.10 Minimal Stage 5 Node and Routing Implementation Checklist (Wave 2)

The following checklist is the minimum contract for Stage 5 continuation.

| Area | Required Contract | Runtime Owner |
|---|---|---|
| State consumed by routing | `pm_decision`, `algedonic_active`, `review_pending`, and phase/gate context from replayed `WorkflowState` | Routing module + node inputs |
| State produced by nodes | Updated execution context (`current_agent`, `current_skill`, `last_specialist_output`) and lifecycle flags | Node implementations |
| Event taxonomy touchpoints | `engagement.started`, `sprint.started/close`, `phase.entered/transitioned/suspended/resumed`, `specialist.invoked/completed`, `cq.raised/batched/answered`, `review.pending/sprint-closed`, `algedonic.escalated`, `engagement.completed` | Orchestration nodes (lifecycle), PM tools (decision), specialist tools (artifact/interaction) |
| Gate ownership | PM decision + gate evaluator tool; routing enforces hold/pass transitions | PM agent + gate_check_node + route_after_gate |
| Escalation ownership | Algedonic bypass checked before normal routing progression | Routing functions + algedonic handler node |
| Fan-out/fan-in ownership | Topology defined in phase subgraph code, never in skill prose | Phase subgraph designers/maintainers |
| CQ routing ownership | CQ surfaced and resumed through dedicated CQ node and PM resumption path | CQ node + PM routing |

These checks are sufficient to implement and verify branch/suspend/fan-out behavior without policy ambiguity.

Planning linkage: [@DOC:IMPLEMENTATION_PLAN#5c-orchestration-layer](../specs/IMPLEMENTATION_PLAN.md#5c--orchestration-layer).

---

## 3. `SDLCGraphState` LangGraph TypedDict

This is the LangGraph state schema (DOB-012) — separate from `WorkflowState` (DOB-009, in `src/events/replay.py`), which is the EventStore-persisted canonical engagement state. `SDLCGraphState` carries only what routing functions need to select the next node; it does not replicate EventStore data.

```python
# src/orchestration/graph_state.py

from typing import TypedDict
from .pm_decision import PMDecision

class SDLCGraphState(TypedDict):
    # Engagement identity
    engagement_id: str

    # Current execution context (set by nodes; read by routing functions)
    current_agent: str | None        # agent role currently executing (e.g. "SA")
    current_skill: str | None        # skill ID currently loaded (e.g. "SA-PHASE-A")

    # PM decision — routing functions read next_action from here
    pm_decision: PMDecision | None

    # Output from most recent specialist invocation
    last_specialist_output: str | None

    # Multi-repo context (populated from Engagement config at session start)
    target_repository_ids: list[str]
    primary_repository_id: str | None

    # Lifecycle flags (set/cleared by infrastructure nodes; checked by routing functions)
    review_pending: bool             # True when sprint review awaits user submission
    algedonic_active: bool           # True when an active S1/S2 algedonic signal exists
```

**Note:** Rich engagement state (current phase, open CQs, gate outcomes, baselined artifacts, phase visit counts) lives in `WorkflowState` (DOB-009), rebuilt from EventStore via `replay_from_latest_snapshot()` at session start and passed to agents via `AgentDeps.workflow_state`. Routing functions check `state["pm_decision"].next_action`, `state["algedonic_active"]`, and `state["review_pending"]` — they do not query EventStore directly.

---

## 4. Graph Topology

### 4.1 Node Inventory

| Node name | Executes | Routing function after |
|---|---|---|
| `pm_node` | PM supervisor decides next action; writes `pm_decision` to state | `route_from_pm` |
| `sa_node` | `invoke_specialist("SA", ...)` | `route_after_specialist` |
| `swa_node` | `invoke_specialist("SwA", ...)` | `route_after_specialist` |
| `do_node` | `invoke_specialist("DO", ...)` | `route_after_specialist` |
| `de_node` | `invoke_specialist("DE", ...)` | `route_after_specialist` |
| `qa_node` | `invoke_specialist("QA", ...)` | `route_after_specialist` |
| `po_node` | `invoke_specialist("PO", ...)` | `route_after_specialist` |
| `csco_node` | `invoke_specialist("CSCO", ...)` | `route_after_specialist` |
| `gate_check_node` | PM evaluates gate; emits `phase.transitioned` on pass | `route_after_gate` |
| `cq_user_node` | Sets `review_pending=False`; suspends on open CQs; emits `phase.suspended/resumed` | `route_after_cq` |
| `algedonic_handler_node` | Routes algedonic; sets `algedonic_active`; may halt | `route_after_algedonic` |
| `sprint_close_node` | Closes sprint; emits `sprint.close` + snapshot | `route_after_sprint_close` |
| `review_processing_node` | Processes sprint review decisions; routes revisions; emits `review.sprint-closed` | `route_after_review` |
| `engagement_complete_node` | Emits `engagement.completed` + snapshot; initiates promotion | → END |

### 4.2 Routing Functions

```python
# src/orchestration/routing.py (schematic)

def route_from_pm(state: SDLCGraphState) -> str:
    """Central router: PM has set pm_decision; route to the appropriate node."""
    # Algedonic bypass: checked before acting on PM decision
    if state["algedonic_active"]:
        return "algedonic_handler_node"

    decision = state["pm_decision"]
    if decision is None:
        return "pm_node"  # PM re-deliberates (should not occur in normal flow)

    match decision.next_action:
        case "invoke_specialist":
            return _specialist_node(decision.specialist_id)
        case "evaluate_gate":
            return "gate_check_node"
        case "surface_cqs":
            return "cq_user_node"
        case "trigger_review":
            return "review_processing_node"
        case "close_sprint":
            return "sprint_close_node"
        case "complete_engagement":
            return "engagement_complete_node"
    return "pm_node"  # default: PM re-deliberates

def route_after_specialist(state: SDLCGraphState) -> str:
    """After any specialist run: check algedonics, then return to PM."""
    if state["algedonic_active"]:
        return "algedonic_handler_node"
    if state["review_pending"]:
        return "review_processing_node"
    return "pm_node"

def route_after_gate(state: SDLCGraphState) -> str:
    """After gate evaluation — always return to PM (gate result is in EventStore)."""
    if state["algedonic_active"]:
        return "algedonic_handler_node"
    return "pm_node"

def route_after_cq(state: SDLCGraphState) -> str:
    """After CQ answer received from user."""
    return "pm_node"   # PM resumes suspended agent or advances

def route_after_algedonic(state: SDLCGraphState) -> str:
    """After algedonic signal handled. May halt (END) or resume (pm_node)."""
    decision = state["pm_decision"]
    if decision and decision.next_action == "complete_engagement":
        return "engagement_complete_node"
    return "pm_node"

def route_after_sprint_close(state: SDLCGraphState) -> str:
    """After sprint closed: trigger review if enabled, else back to PM."""
    if state["review_pending"]:
        return "review_processing_node"
    return "pm_node"

def route_after_review(state: SDLCGraphState) -> str:
    """After sprint review processed: back to PM for next phase or sprint."""
    return "pm_node"

def _specialist_node(agent_id: str | None) -> str:
    return {
        "SA": "sa_node", "SwA": "swa_node", "DO": "do_node",
        "DE": "de_node", "QA": "qa_node",
        "PO": "po_node", "SM": "sm_node", "CSCO": "csco_node",
    }[agent_id or ""]
```

### 4.3 Graph Construction

```python
# src/orchestration/graph.py

from langgraph.graph import StateGraph, START, END
from .graph_state import SDLCGraphState
from .nodes import (pm_node, sa_node, swa_node, do_node, de_node, qa_node,
                    po_node, sm_node, csco_node, gate_check_node, cq_user_node,
                    algedonic_handler_node, sprint_close_node,
                    review_processing_node, engagement_complete_node)
from .routing import (route_from_pm, route_after_specialist, route_after_gate,
                      route_after_cq, route_after_algedonic,
                      route_after_sprint_close, route_after_review)

def build_sdlc_graph() -> CompiledGraph:
    graph = StateGraph(SDLCGraphState)

    # Register all nodes
    for name, fn in [
        ("pm_node", pm_node),
        ("sa_node", sa_node),
        ("swa_node", swa_node),
        ("do_node", do_node),
        ("de_node", de_node),
        ("qa_node", qa_node),
        ("po_node", po_node),
        ("sm_node", sm_node),
        ("csco_node", csco_node),
        ("gate_check_node", gate_check_node),
        ("cq_user_node", cq_user_node),
        ("algedonic_handler_node", algedonic_handler_node),
        ("sprint_close_node", sprint_close_node),
        ("review_processing_node", review_processing_node),
        ("engagement_complete_node", engagement_complete_node),
    ]:
        graph.add_node(name, fn)

    # Entry point
    graph.add_edge(START, "pm_node")

    # PM routes to everything
    graph.add_conditional_edges("pm_node", route_from_pm)

    # Specialists all return via route_after_specialist
    for node in ["sa_node", "swa_node", "do_node", "de_node", "qa_node",
                 "po_node", "sm_node", "csco_node"]:
        graph.add_conditional_edges(node, route_after_specialist)

    # Infrastructure nodes
    graph.add_conditional_edges("gate_check_node", route_after_gate)
    graph.add_conditional_edges("cq_user_node", route_after_cq)
    graph.add_conditional_edges("algedonic_handler_node", route_after_algedonic)
    graph.add_conditional_edges("sprint_close_node", route_after_sprint_close)
    graph.add_conditional_edges("review_processing_node", route_after_review)
    graph.add_edge("engagement_complete_node", END)

    return graph.compile()
```

---

## 5. PM Supervisor Node

The PM node is the deliberative hub. It uses PydanticAI to reason about what to do next, then writes a `PMDecision` object into `pm_decision` in the graph state. Routing functions read `state["pm_decision"].next_action` to select the next node.

```python
# src/orchestration/nodes.py (PM node schematic)

async def pm_node(state: SDLCGraphState) -> SDLCGraphState:
    """PM supervisor: reads EventStore state, decides next action."""
    from src.agents.project_manager import pm_agent
    from src.agents.deps import AgentDeps
    from src.events.store import EventStorePort
    from src.models.engagement import Engagement

    store: EventStorePort = _get_event_store(state["engagement_id"])
    engagement: Engagement = _get_engagement(state["engagement_id"])
    workflow_state = store.current_state()

    deps = AgentDeps(
        engagement=engagement,
        event_store=store,
        active_skill_id=_select_pm_skill(workflow_state),
        workflow_state=workflow_state,
        engagement_base_path=_engagement_base_path(state["engagement_id"]),
        framework_path=_framework_path(),
    )

    result = await pm_agent.run(
        _pm_decision_prompt(state, workflow_state),
        deps=deps,
    )

    # PM returns structured PMDecision; embed the whole object in state
    decision: PMDecision = result.data
    return {
        **state,
        "pm_decision": decision,
        "last_specialist_output": decision.reasoning,
    }
```

The PM agent's `result_type` is `PMDecision` (DOB-011). `next_action` values are the canonical routing keys consumed by `route_from_pm`:

```python
# src/orchestration/pm_decision.py
from pydantic import BaseModel
from typing import Literal

class PMDecision(BaseModel):
    next_action: Literal[
        "invoke_specialist",   # route to specialist node; specialist_id + skill_id required
        "evaluate_gate",       # route to gate_check_node; gate_id required
        "surface_cqs",         # route to cq_user_node
        "trigger_review",      # route to review_processing_node
        "close_sprint",        # route to sprint_close_node
        "complete_engagement", # route to engagement_complete_node
    ]
    specialist_id: str | None = None   # Required if next_action == "invoke_specialist"
    skill_id: str | None = None        # Required if next_action == "invoke_specialist"
    task_description: str              # Always set; describes the work unit
    reasoning: str                     # PM's explanation for the decision
    gate_id: str | None = None         # Required if next_action == "evaluate_gate"
```

---

## 6. EventStore as Cross-Session State

LangGraph state (`SDLCGraphState`) is in-memory and lost between Python process restarts. **The EventStore is the durable, resumable state store.**

On every process start, the SDLC graph is initialised by:
1. Loading `engagements-config.yaml` to get the engagement ID.
2. Calling `EventStore(engagement_id).current_state()` to reconstruct `WorkflowState`.
3. Building `SDLCGraphState` from `WorkflowState` as the initial graph state.
4. Resuming graph execution from the current phase.

This means the system is always resumable from the last committed EventStore state, regardless of process lifecycle.

LangGraph's own persistence (checkpointing via `MemorySaver` or `SqliteSaver`) is used for within-session conversational continuity only, not for cross-session engagement resumption. The EventStore is the canonical state store.

---

## 7. Entry Point Handling

On engagement start, the SDLC graph entry is parameterised by the entry point from `engagements-config.yaml`:

Entry-point context is carried in `WorkflowState` (rebuilt from EventStore), not in `SDLCGraphState`. The PM node reads `workflow_state.current_phase` and `workflow_state.trigger` to select the appropriate opening skill.

| Entry Point | `workflow_state.current_phase` | `workflow_state.trigger` | First PM action |
|---|---|---|---|
| EP-0 | Prelim | initial | Scoping interview skill |
| EP-A | A | initial | Warm-start ingestion |
| EP-B | B | initial | Warm-start ingestion |
| EP-C | C | initial | Warm-start ingestion |
| EP-D | D | initial | Warm-start ingestion |
| EP-E | E | initial | Warm-start ingestion |
| EP-F | F | initial | Warm-start ingestion |
| EP-G | G | initial | Reverse Architecture Reconstruction (SwA) |
| EP-H | H | initial | Change Record intake |

The PM node handles entry-point behaviour per `agents/project-manager/AGENT.md §7`.

---

## 8. Testing Topology

For unit and integration tests:

- **Unit tests** (`tests/unit/`): Test individual agent invocations with a mock `EventStore` and mock `AgentDeps`. No LangGraph. No LLM calls (use `TestModel` from PydanticAI).
- **Integration tests** (`tests/integration/`): Run the full LangGraph graph against the synthetic project (`tests/synthetic-project/`) with real LLM calls. Assert: correct artifacts produced, correct events emitted, schemas satisfied, no orphaned outputs.
- **Node tests** (`tests/nodes/`): Test individual LangGraph routing functions with mock `SDLCGraphState` inputs. Assert correct node name returned.

---

## 9. Cross-References

- `framework/agent-runtime-spec.md` — PydanticAI agent construction, skill loading, tool sets
- `src/orchestration/graph.py` — LangGraph graph construction
- `src/orchestration/graph_state.py` — `SDLCGraphState` TypedDict
- `src/orchestration/routing.py` — all routing functions
- `src/orchestration/nodes.py` — all node implementations
- `src/orchestration/pm_decision.py` — PM structured output type
- `src/events/` — EventStore (canonical state persistence)

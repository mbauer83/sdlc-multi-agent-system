# Orchestration Topology

**Version:** 1.0.0  
**Status:** Approved — Pre-Stage 5  
**Last Updated:** 2026-04-02

---

## 1. Purpose

This document specifies how the multi-agent SDLC system is orchestrated at runtime: how agents are coordinated across ADM phases, how LangGraph models the ADM workflow, and how the PM supervisor coordinates specialist agents. It is the architectural reference for `src/orchestration/`.

The system uses a two-layer architecture:
- **LangGraph** manages the ADM phase workflow: phase progression, gate evaluation, algedonic handling, sprint sequencing. It is the outer control loop.
- **PydanticAI** handles individual agent invocations: each agent run is a `PydanticAI Agent.run()` call with appropriate context. It is the inner execution layer.
- **EventStore** persists all state transitions. LangGraph reads state from EventStore at each node entry; agents write state to EventStore via events.

---

## 2. Coordination Model

### 2.1 Primary Model: PM Supervisor with Agent-as-Tool

The Project Manager is the **supervisor node** in the LangGraph graph. When a phase requires specialist work, the PM node calls the specialist PydanticAI agent via the `invoke_specialist` tool (`framework/agent-runtime-spec.md §7`). This is a **hierarchical, sequential coordination model**:

```
PM supervisor node
  → invoke_specialist("SA", "SA-PHASE-A", task)
  ← result + EventStore events emitted by SA
  → evaluate gate A→B
  → invoke_specialist("SA", "SA-PHASE-B", task)
  ...
```

**Why PM-as-supervisor:** The PM holds the coordination authority (VSM System 3) and is the only agent with `evaluate_gate` and `batch_cqs` tools. Routing decisions belong to the PM, not to a separate orchestration layer disconnected from the ADM protocol.

### 2.2 Optional Extension: LangGraph Fan-Out for Phase G

Phase G Solution Sprints have three concurrent agents (DE, DO, QA). For serial execution (Option A), PM calls them sequentially. For parallel execution (Option B), LangGraph's `Send` API fans out to three concurrent sub-graphs:

```
Phase G Sprint node
  → Send("de_node", sprint_state)
  → Send("do_node", sprint_state)
  → Send("qa_node", sprint_state)
  ← merge results
  → evaluate sprint close
```

Option B requires the LangGraph `Send` API and is introduced only when sequential throughput is insufficient (Stage 5 evaluation criterion: serial Phase G sprint > 5 minutes wall-clock for a typical sprint scope).

### 2.3 Algedonic Bypass

Any agent node can emit an `alg.raised` EventStore event. The LangGraph routing function at each node exit checks for open algedonics and routes to `algedonic_handler_node` before normal phase progression. This implements the algedonic bypass without polling.

### 2.4 Workflow Control Ownership Boundary

Executable workflow control is owned by the orchestration harness (LangGraph nodes, routing functions, PM tool policies), not by skill prose.

- Skills define intent and output contracts (what to produce, required checks, quality bars).
- Orchestration code defines execution control (when to run, precondition enforcement, phase/state transitions, retries, suspension/resume).
- `invoke-when` and `trigger-conditions` in skill frontmatter are documentation hints; they do not replace runtime state-machine enforcement.

This separation keeps skills reusable across entry points and future workflow profiles while preserving deterministic governance.

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

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

---

## 3. LangGraph WorkflowState

This is the LangGraph state schema — separate from the `src/events/models/state.WorkflowState` (which is the EventStore's computed state). The LangGraph state carries the information LangGraph needs to route between nodes; it does not replicate the EventStore.

```python
# src/orchestration/graph_state.py

from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages

class SDLCGraphState(TypedDict):
    # Engagement identity
    engagement_id: str
    
    # Current position in ADM workflow
    current_phase: str          # "Prelim" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H"
    current_sprint_id: str | None
    phase_visit_count: int      # read from EventStore; used for revisit detection
    
    # What triggered this node entry
    trigger: Literal[
        "initial",              # First time through this phase
        "revisit",              # Phase re-entered due to Phase H change
        "gate_rejection",       # Gate held; re-entry for resolution
        "cq_resumed",           # Resumed after CQ answer received
        "algedonic_resolved",   # Resumed after algedonic resolution
    ]
    
    # Routing signals (set by current node; consumed by routing functions)
    next_action: Literal[
        "continue",             # Current node succeeded; advance normally
        "gate_check",           # Request gate evaluation before advancing
        "invoke_specialist",    # PM needs to invoke a specialist
        "await_cq",             # Blocking CQ raised; suspend until answered
        "algedonic",            # Algedonic signal raised; route to handler
        "sprint_close",         # Solution Sprint complete; close and check phase exit
        "phase_complete",       # Phase complete; advance to next phase
        "engagement_complete",  # All phases done
        "error",                # Unrecoverable error
    ]
    
    # Specialist invocation parameters (set by PM before routing to specialist)
    pending_specialist_id: str | None    # e.g. "SA"
    pending_skill_id: str | None         # e.g. "SA-PHASE-A"
    pending_task: str | None             # Task description for specialist
    
    # Results from most recent node execution
    last_agent_output: str | None
    last_gate_result: Literal["passed", "held", "escalated"] | None
    
    # Conversation / instruction thread (for PM's deliberative reasoning)
    messages: Annotated[list, add_messages]
    
    # Error information
    error_message: str | None
```

**Note:** `SDLCGraphState` is deliberately thin. Rich state lives in EventStore. LangGraph state only carries what routing functions need. Agents reconstruct full context from EventStore via `event_store.current_state()` on each invocation.

---

## 4. Graph Topology

### 4.1 Node Inventory

| Node name | Executes | Routing function after |
|---|---|---|
| `pm_node` | PM supervisor decides next action | `route_from_pm` |
| `sa_node` | `invoke_specialist("SA", ...)` | `route_after_specialist` |
| `swa_node` | `invoke_specialist("SwA", ...)` | `route_after_specialist` |
| `do_node` | `invoke_specialist("DO", ...)` | `route_after_specialist` |
| `de_node` | `invoke_specialist("DE", ...)` | `route_after_specialist` |
| `qa_node` | `invoke_specialist("QA", ...)` | `route_after_specialist` |
| `po_node` | `invoke_specialist("PO", ...)` *(Stage 4)* | `route_after_specialist` |
| `csco_node` | `invoke_specialist("CSCO", ...)` *(Stage 4)* | `route_after_specialist` |
| `gate_check_node` | PM evaluates gate conditions | `route_after_gate` |
| `cq_user_node` | Format and deliver CQ batch to user; await answer | `route_after_cq` |
| `algedonic_handler_node` | PM routes algedonic signal; may halt or restructure | `route_after_algedonic` |
| `sprint_close_node` | PM closes Solution Sprint; exports YAML audit | `route_after_sprint_close` |
| `engagement_complete_node` | PM initiates enterprise promotion, closes engagement | → END |

### 4.2 Routing Functions

```python
# src/orchestration/routing.py (schematic)

def route_from_pm(state: SDLCGraphState) -> str:
    """Central router: PM has decided what to do next."""
    # First: check for open algedonics in EventStore
    if _has_open_algedonics(state):
        return "algedonic_handler_node"
    
    action = state["next_action"]
    match action:
        case "invoke_specialist":
            return _specialist_node(state["pending_specialist_id"])
        case "gate_check":
            return "gate_check_node"
        case "await_cq":
            return "cq_user_node"
        case "sprint_close":
            return "sprint_close_node"
        case "phase_complete":
            return "pm_node"          # PM re-enters for next phase
        case "engagement_complete":
            return "engagement_complete_node"
        case "error":
            return "algedonic_handler_node"
    return "pm_node"  # default: PM re-deliberates

def route_after_specialist(state: SDLCGraphState) -> str:
    """After any specialist run: check for algedonics, then return to PM."""
    if _has_open_algedonics(state):
        return "algedonic_handler_node"
    if state["next_action"] == "await_cq":
        return "cq_user_node"
    return "pm_node"

def route_after_gate(state: SDLCGraphState) -> str:
    """After gate evaluation."""
    match state["last_gate_result"]:
        case "passed":
            return "pm_node"          # PM advances to next phase
        case "held":
            return "pm_node"          # PM restructures sprint or raises CQ
        case "escalated":
            return "algedonic_handler_node"

def route_after_cq(state: SDLCGraphState) -> str:
    """After CQ answer received from user."""
    return "pm_node"   # PM resumes suspended agent or advances

def route_after_algedonic(state: SDLCGraphState) -> str:
    """After algedonic signal handled."""
    # May return to pm_node (resolved), or END (unresolvable halt)
    if state["next_action"] == "engagement_complete":
        return "engagement_complete_node"
    return "pm_node"

def route_after_sprint_close(state: SDLCGraphState) -> str:
    """After Solution Sprint closed."""
    return "pm_node"   # PM evaluates whether Phase G is complete

def _specialist_node(agent_id: str) -> str:
    return {
        "SA": "sa_node", "SwA": "swa_node", "DO": "do_node",
        "DE": "de_node", "QA": "qa_node",
        "PO": "po_node", "CSCO": "csco_node",
    }[agent_id]

def _has_open_algedonics(state: SDLCGraphState) -> bool:
    # Read from EventStore; algedonics bypass normal routing
    from src.events import EventStore
    store = EventStore(state["engagement_id"])
    ws = store.current_state()
    return any(
        len(cycle.open_algedonics) > 0
        for cycle in ws.active_cycles
    )
```

### 4.3 Graph Construction

```python
# src/orchestration/graph.py

from langgraph.graph import StateGraph, START, END
from .graph_state import SDLCGraphState
from .nodes import (pm_node, sa_node, swa_node, do_node, de_node, qa_node,
                    po_node, csco_node, gate_check_node, cq_user_node,
                    algedonic_handler_node, sprint_close_node, engagement_complete_node)
from .routing import (route_from_pm, route_after_specialist, route_after_gate,
                      route_after_cq, route_after_algedonic, route_after_sprint_close)

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
        ("csco_node", csco_node),
        ("gate_check_node", gate_check_node),
        ("cq_user_node", cq_user_node),
        ("algedonic_handler_node", algedonic_handler_node),
        ("sprint_close_node", sprint_close_node),
        ("engagement_complete_node", engagement_complete_node),
    ]:
        graph.add_node(name, fn)

    # Entry point
    graph.add_edge(START, "pm_node")

    # PM routes to everything
    graph.add_conditional_edges("pm_node", route_from_pm)

    # Specialists all return to PM
    for node in ["sa_node", "swa_node", "do_node", "de_node", "qa_node", "po_node", "csco_node"]:
        graph.add_conditional_edges(node, route_after_specialist)

    # Other nodes
    graph.add_conditional_edges("gate_check_node", route_after_gate)
    graph.add_conditional_edges("cq_user_node", route_after_cq)
    graph.add_conditional_edges("algedonic_handler_node", route_after_algedonic)
    graph.add_conditional_edges("sprint_close_node", route_after_sprint_close)
    graph.add_edge("engagement_complete_node", END)

    return graph.compile()
```

---

## 5. PM Supervisor Node

The PM node is the deliberative hub. It uses PydanticAI to reason about what to do next, then sets `next_action` and optionally `pending_specialist_id/skill_id/task` in the graph state.

```python
# src/orchestration/nodes.py (PM node schematic)

async def pm_node(state: SDLCGraphState) -> SDLCGraphState:
    """PM supervisor: reads EventStore state, decides next action."""
    from src.agents.project_manager import pm_agent
    from src.agents.deps import AgentDeps
    from src.events import EventStore
    
    store = EventStore(state["engagement_id"])
    workflow_state = store.current_state()
    
    deps = AgentDeps(
        engagement_id=state["engagement_id"],
        event_store=store,
        active_skill_id=_select_pm_skill(workflow_state),
        workflow_state=workflow_state,
        engagement_base_path=...,
        framework_path=...,
    )
    
    result = await pm_agent.run(
        _pm_decision_prompt(state, workflow_state),
        deps=deps,
    )
    
    # PM returns structured decision: next_action + optional specialist parameters
    decision = result.data  # typed as PMDecision (Pydantic model)
    return {
        **state,
        "next_action": decision.next_action,
        "pending_specialist_id": decision.specialist_id,
        "pending_skill_id": decision.skill_id,
        "pending_task": decision.task_description,
        "last_agent_output": decision.reasoning,
        "messages": [{"role": "assistant", "content": decision.reasoning}],
    }
```

The PM agent's `result_type` in Phase G/orchestration mode is a structured `PMDecision` Pydantic model:

```python
# src/orchestration/pm_decision.py
from pydantic import BaseModel
from typing import Literal

class PMDecision(BaseModel):
    next_action: Literal[
        "invoke_specialist", "gate_check", "await_cq",
        "sprint_close", "phase_complete", "engagement_complete", "error"
    ]
    specialist_id: str | None = None   # Required if next_action == "invoke_specialist"
    skill_id: str | None = None        # Required if next_action == "invoke_specialist"
    task_description: str | None = None
    reasoning: str                     # PM's explanation for the decision
    gate_id: str | None = None         # Required if next_action == "gate_check"
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

| Entry Point | Initial `current_phase` | Initial `trigger` | First PM action |
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

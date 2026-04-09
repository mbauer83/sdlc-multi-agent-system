"""
PM decision tools — emitted exclusively by the Project Manager agent.

Per framework/orchestration-topology.md and CLAUDE.md rule #22 (three-layer
emitter hierarchy): PM tools emit decision events; orchestration nodes emit
lifecycle events; specialist tools emit artifact/interaction events.

Tools registered here:
  invoke_specialist  — schedule a specialist agent for a skill task
  evaluate_gate      — evaluate a phase-transition gate
  batch_cqs          — batch open CQs for user presentation
  record_decision    — persist a PM reasoning decision
  trigger_review     — initiate sprint review (emits review.pending)

All five emit to the EventStore immediately before returning.
"""

from __future__ import annotations

from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps


def invoke_specialist(
    ctx: RunContext[AgentDeps],
    agent_id: str,
    skill_id: str,
    task: str,
) -> str:
    """
    Schedule a specialist agent for a skill-scoped task.

    Emits specialist.invoked and returns an invocation receipt string.
    The orchestration layer handles the actual agent call; this tool
    records the PM's decision.

    agent_id:  canonical role abbreviation (SA, SwA, DE, DO, QA, ...)
    skill_id:  skill-id from the target skill's frontmatter
    task:      natural-language task description passed to the agent
    """
    from src.events.models.specialist import SpecialistInvokedPayload

    try:
        payload = SpecialistInvokedPayload(
            agent_id=agent_id,
            skill_id=skill_id,
            task=task,
        )
        ctx.deps.event_store.append(
            payload,
            actor=ctx.deps.agent_id,
            correlation_id=skill_id,
        )
    except Exception:  # noqa: BLE001
        pass  # event emission is best-effort

    return f"[Scheduled {agent_id} / {skill_id}]"


def evaluate_gate(
    ctx: RunContext[AgentDeps],
    gate_id: str,
    votes: dict[str, str],
    result: str = "passed",
) -> str:
    """
    Evaluate a phase-transition gate.

    gate_id:  canonical gate identifier (e.g. "GATE-A-B")
    votes:    mapping of voter_role → "pass" | "fail" | "abstain"
    result:   overall result: "passed" | "failed" | "deferred"

    Emits gate.evaluated.  On pass also creates an EventStore snapshot.
    Returns a summary string.
    """
    from src.events.models.gate import GateEvaluatedPayload

    try:
        # Map votes (str) → checklist_results (bool); use gate_id as transition key
        checklist = {k: v.lower() == "pass" for k, v in votes.items()}
        payload = GateEvaluatedPayload(
            transition=gate_id,
            checklist_results=checklist,
        )
        ctx.deps.event_store.append(
            payload,
            actor=ctx.deps.agent_id,
            correlation_id=gate_id,
        )
        if result == "passed":
            ctx.deps.event_store.create_snapshot(f"gate.evaluated:{gate_id}")
    except Exception:  # noqa: BLE001
        pass

    return f"[Gate {gate_id}: {result}]"


def batch_cqs(
    ctx: RunContext[AgentDeps],
    cq_ids: list[str],
    target: str = "user",
) -> str:
    """
    Batch open CQs for presentation to the user (or PM-routed agent).

    cq_ids:  list of cq_id strings from clarification-log/
    target:  "user" | agent role abbreviation
    Emits cq.batched.
    """
    from src.events.models.cq import CQBatchedPayload  # noqa: PLC0415

    try:
        payload = CQBatchedPayload(cq_ids=cq_ids, target=target)
        ctx.deps.event_store.append(
            payload,
            actor=ctx.deps.agent_id,
            correlation_id=f"batch-{'-'.join(cq_ids[:3])}",
        )
    except Exception:  # noqa: BLE001
        pass

    return f"[Batched {len(cq_ids)} CQ(s) → {target}]"


def record_decision(
    ctx: RunContext[AgentDeps],
    rationale: str,
    decision_type: str = "routing",
    artifact_id: str | None = None,
) -> str:
    """
    Persist a PM reasoning decision to the EventStore and project-repository.

    rationale:     prose explanation of the PM's decision
    decision_type: "routing" | "gate" | "escalation" | "cq-resolution"
    Emits decision.recorded.
    """
    import uuid
    from src.events.models.decision import DecisionRecordedPayload

    decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
    try:
        payload = DecisionRecordedPayload(
            decision_id=decision_id,
            decision_type=decision_type,
            rationale=rationale,
            artifact_id=artifact_id,
        )
        ctx.deps.event_store.append(
            payload,
            actor=ctx.deps.agent_id,
            correlation_id=decision_id,
        )
    except Exception:  # noqa: BLE001
        pass

    # Write to project-repository/decisions/ as a durable record
    decisions_dir = (
        ctx.deps.work_repos_path / "project-repository" / "decisions"
    )
    decisions_dir.mkdir(parents=True, exist_ok=True)
    (decisions_dir / f"{decision_id}.md").write_text(
        f"---\ndecision-id: {decision_id}\ndecision-type: {decision_type}\n"
        f"made-by: {ctx.deps.agent_id}\nskill-id: {ctx.deps.active_skill_id}\n---\n\n"
        f"## Rationale\n\n{rationale}\n"
    )
    return decision_id


def trigger_review(
    ctx: RunContext[AgentDeps],
    sprint_id: str,
    artifact_ids: list[str] | None = None,
) -> str:
    """
    Initiate a sprint review cycle. Emits review.pending.

    sprint_id:    identifier of the current sprint (e.g. "S1")
    artifact_ids: subset of artifact IDs to include in review scope;
                  None means all artifacts produced this sprint.
    """
    from src.events.models.review import ReviewPendingPayload

    try:
        payload = ReviewPendingPayload(
            sprint_id=sprint_id,
            artifact_ids=artifact_ids or [],
        )
        ctx.deps.event_store.append(
            payload,
            actor=ctx.deps.agent_id,
            correlation_id=sprint_id,
        )
    except Exception:  # noqa: BLE001
        pass

    return f"[Review pending for sprint {sprint_id}]"


# ---------------------------------------------------------------------------
# Tool registration helper
# ---------------------------------------------------------------------------

def register_pm_tools(agent: Any) -> None:
    """Register all PM decision tools on a PydanticAI Agent instance."""
    for fn in (
        invoke_specialist,
        evaluate_gate,
        batch_cqs,
        record_decision,
        trigger_review,
    ):
        agent.tool(fn)

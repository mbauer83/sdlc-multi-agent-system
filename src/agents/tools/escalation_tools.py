"""
Escalation tools: emit_event, raise_cq, raise_algedonic.

These tools write to the EventStore and create log records in the
engagement directory. Available to all agent roles.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps


def emit_event(
    ctx: RunContext[AgentDeps],
    event_type: str,
    payload: dict[str, Any],
) -> str:
    """
    Emit a typed workflow event to the EventStore.

    Returns the event_id of the persisted event, or an error string.
    The payload dict must match the registered payload model for event_type.
    """
    from src.events.registry import EventRegistry

    try:
        cls = EventRegistry.cls_for(event_type)
        typed_payload = cls(**payload)
        envelope = ctx.deps.event_store.append(
            typed_payload,
            actor=ctx.deps.agent_id,
            correlation_id=payload.get("artifact_id") or payload.get("cq_id"),
        )
        return envelope.event_id
    except (TypeError, KeyError, Exception) as exc:  # noqa: BLE001
        return f"[emit_event failed for '{event_type}': {exc}]"


def raise_cq(
    ctx: RunContext[AgentDeps],
    question: str,
    target: str = "user",
    blocking: bool = False,
    blocks_task: str | None = None,
) -> str:
    """
    Raise a Clarification Request. Writes a CQ record and emits cq.raised.

    target:   "user" | "pm" | agent role name
    blocking: if True the phase will be suspended until this CQ is answered
    Returns the cq_id.
    """
    from src.events.models.cq import CQRaisedPayload

    cq_id = f"CQ-{uuid.uuid4().hex[:8].upper()}"
    payload = CQRaisedPayload(
        cq_id=cq_id,
        blocking=blocking,
        target=target,
        blocks_task=blocks_task,
    )
    ctx.deps.event_store.append(payload, actor=ctx.deps.agent_id, correlation_id=cq_id)

    cq_dir = ctx.deps.engagement_path / "clarification-log"
    cq_dir.mkdir(exist_ok=True)
    (cq_dir / f"{cq_id}.md").write_text(
        f"---\ncq-id: {cq_id}\nraised-by: {ctx.deps.agent_id}\n"
        f"skill-id: {ctx.deps.active_skill_id}\n"
        f"target: {target}\nblocking: {blocking}\nstatus: open\n---\n\n"
        f"## Question\n\n{question}\n"
    )
    return cq_id


def raise_algedonic(
    ctx: RunContext[AgentDeps],
    trigger_id: str,
    category: str,
    severity: str,
    description: str,
) -> str:
    """
    Raise an algedonic signal. Writes a log record and emits algedonic.raised.

    trigger_id: canonical ALG-NNN identifier (e.g. "ALG-001")
    category:   "SC" | "RB" | "TC" | "GV" | "IA" | "KG"
    severity:   "S1" | "S2" | "S3" | "S4"
    Returns the signal_id.
    """
    from src.events.models.algedonic import AlgedonicRaisedPayload

    sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"
    payload = AlgedonicRaisedPayload(
        signal_id=sig_id,
        trigger_id=trigger_id,
        category=category,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
    )
    ctx.deps.event_store.append(payload, actor=ctx.deps.agent_id, correlation_id=sig_id)

    alg_dir = ctx.deps.engagement_path / "algedonic-log"
    alg_dir.mkdir(exist_ok=True)
    (alg_dir / f"{sig_id}.md").write_text(
        f"---\nsignal-id: {sig_id}\ntrigger-id: {trigger_id}\n"
        f"category: {category}\nseverity: {severity}\nstatus: open\n"
        f"raised-by: {ctx.deps.agent_id}\nskill-id: {ctx.deps.active_skill_id}\n---\n\n"
        f"## Description\n\n{description}\n"
    )
    return sig_id

"""
ENG-DEMO setup: scaffold, infra-check, run, and verify the TaskFlow API demo scenario.

Benchmark Scenario
------------------
No off-the-shelf agentic SE benchmark covers TOGAF ADM architecture work
(the field focuses on code generation / bug-fixing).  This script implements
a *scenario-based test* with specified, machine-verifiable expected outputs,
inspired by SWE-bench methodology applied to architecture document production.

Phase A — SA (Architecture Vision):
  Target project : Python/FastAPI task-management REST API
  Agent          : SA (Solution Architect)
  Skill          : SA-PHASE-A
  Phase          : A

  Expected outputs (all verified automatically):
    1. Architecture Vision document in architecture-repository/overview/ (≥300 chars)
    2. ≥1 stakeholder entity   (model-entities/motivation/stakeholders/STK-*.md)
    3. ≥1 architecture driver  (model-entities/motivation/drivers/DRV-*.md)
    4. ≥1 architecture principle (model-entities/motivation/principles/PRI-*.md)
    5. No algedonic boundary violations (algedonic-log/ empty)
    6. ≥1 artifact event in EventStore
    7. ModelVerifier: 0 hard errors

Phase C — SwA (Application Architecture):
  Agent          : SwA (Software Architect / PE)
  Skill          : SwA-PHASE-C-APP
  Phase          : C

  Expected outputs (all verified automatically):
    8. ≥1 application component entity (model-entities/application/APP-*.md)

Usage
-----
  uv run python scripts/demo_setup.py [--verbose] [--skip-run] [--phase-a-only] [--engagement ENG-DEMO]

Requires ANTHROPIC_API_KEY in environment (skip with --skip-run for scaffold-only).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path for src.* imports
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.demo_scaffold import ENGAGEMENT_ID, scaffold_demo
from scripts.demo_verify import check_framework_infra, print_report, verify_outputs

_ENTITY_FORMAT_HINT = """\
Entity YAML frontmatter fields (required): artifact-id, artifact-type, name, version,
status, phase-produced, owner-agent, safety-relevant, produced-by-skill, last-updated,
engagement.  artifact-type for motivation entities: stakeholder | driver | principle.
artifact-type for application entities: application-component | application-interface |
application-service | application-collaboration | application-interaction.
Engagement ID for this run: {eid}.
"""

_TASK_SA = (
    "Perform Phase A (Architecture Vision) for engagement {eid}. "
    "The target project is 'TaskFlow API' — a Python/FastAPI task management REST API "
    "deployed to EU-hosted Kubernetes with GDPR constraints. "
    "Read the full project brief via read_target_repo(path='README.md') before starting. "
    "Follow your SA-PHASE-A skill instructions for what to produce and where to write it. "
    "Entity format reminder: {fmt}"
)

_TASK_SWA = (
    "Perform Phase C (Application Architecture) for engagement {eid}. "
    "Architecture Vision from Phase A is available in "
    "architecture-repository/overview/architecture-vision.md — read it via read_artifact first. "
    "Follow your SwA-PHASE-C-APP skill instructions for what to produce and where to write it. "
    "Entity format reminder: {fmt}"
)


def _print_banner(engagement_id: str, phase_a_only: bool) -> None:
    print("╔" + "═" * 60 + "╗")
    print("║  SDLC Multi-Agent System — ENG-DEMO                      ║")
    if phase_a_only:
        print("║  Scenario: TaskFlow API Phase A (SA only)                 ║")
    else:
        print("║  Scenario: TaskFlow API Phase A + Phase C                 ║")
    print("╚" + "═" * 60 + "╝")
    print(f"\nEngagement : {engagement_id}")
    if phase_a_only:
        print("Agents     : SA (Solution Architect)")
        print("Skills     : SA-PHASE-A")
        print("Phases     : A — Architecture Vision\n")
    else:
        print("Agents     : SA (Solution Architect) + SwA (Software Architect)")
        print("Skills     : SA-PHASE-A → SwA-PHASE-C-APP")
        print("Phases     : A — Architecture Vision → C — Application Architecture\n")


async def _run(args: argparse.Namespace) -> int:
    engagement_id: str = args.engagement
    verbose: bool = args.verbose
    phase_a_only: bool = args.phase_a_only

    _print_banner(engagement_id, phase_a_only)

    # 1. Scaffold — tear down first to guarantee a clean slate
    print("── Step 1/5: Scaffolding engagement and target repository ──")
    from scripts.demo_scaffold import teardown_demo
    teardown_demo(_REPO_ROOT, engagement_id, verbose=verbose)
    engagement_path = scaffold_demo(_REPO_ROOT, engagement_id, verbose)
    print(f"  Engagement ready at: {engagement_path}\n")

    if args.model:
        os.environ["SDLC_PRIMARY_MODEL"] = args.model
        print(f"  Using model: {args.model}\n")

    # 2. Framework infrastructure check (no LLM required)
    print("── Step 2/5: Framework infrastructure check ────────────────")
    infra_report = check_framework_infra(engagement_id, engagement_path)
    all_infra_passed = print_report(infra_report)
    if not all_infra_passed:
        print("  [ERROR] Framework infrastructure checks failed — aborting.", file=sys.stderr)
        return 2

    if args.skip_run:
        print("  [--skip-run] Skipping agent invocation and verification.")
        return 0

    from src.orchestration.session import EngagementSession
    session = EngagementSession(engagement_id, repo_root=_REPO_ROOT)

    # 3. Run SA agent — Phase A
    print("── Step 3/5: Running SA agent (SA-PHASE-A) ─────────────────")
    print("  (Requires ANTHROPIC_API_KEY; may take 60-120 s)\n")
    sa_task = _TASK_SA.format(eid=engagement_id, fmt=_ENTITY_FORMAT_HINT.format(eid=engagement_id))
    try:
        sa_output = await session.invoke_specialist(
            agent_id="SA", skill_id="SA-PHASE-A", task=sa_task, phase="A",
        )
    except Exception as exc:  # noqa: BLE001
        exc_type = type(exc).__name__
        print(f"\n  [ERROR] SA agent failed ({exc_type}): {exc}", file=sys.stderr)
        print("  Run with --skip-run to test scaffolding without an API key.\n")
        return 2

    print("\n── SA output (truncated to 600 chars) ───────────────────────")
    print(sa_output[:600] + ("…" if len(sa_output) > 600 else ""))

    # 4. Run SwA agent — Phase C (unless --phase-a-only)
    if not phase_a_only:
        print("\n── Step 4/5: Running SwA agent (SwA-PHASE-C-APP) ───────────")
        print("  (Phase C: Application Architecture; may take 60-120 s)\n")
        swa_task = _TASK_SWA.format(
            eid=engagement_id, fmt=_ENTITY_FORMAT_HINT.format(eid=engagement_id)
        )
        try:
            swa_output = await session.invoke_specialist(
                agent_id="SwA", skill_id="SwA-PHASE-C-APP", task=swa_task, phase="C",
            )
        except Exception as exc:  # noqa: BLE001
            exc_type = type(exc).__name__
            print(f"\n  [ERROR] SwA agent failed ({exc_type}): {exc}", file=sys.stderr)
            print("  Phase A outputs are still available; Phase C failed.\n")
            # Don't abort — verify Phase A outputs at least
            swa_output = ""

        if swa_output:
            print("\n── SwA output (truncated to 600 chars) ──────────────────────")
            print(swa_output[:600] + ("…" if len(swa_output) > 600 else ""))
    else:
        print("\n── Step 4/5: SwA Phase C skipped (--phase-a-only) ──────────")

    # 5. Verify
    print("\n── Step 5/5: Verifying outputs ──────────────────────────────")
    report = verify_outputs(
        engagement_path,
        session.event_store,
        include_phase_c=not phase_a_only,
    )
    all_passed = print_report(report)

    return 0 if all_passed else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ENG-DEMO setup: scaffold + run + verify TaskFlow Phase A scenario",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--engagement", default=ENGAGEMENT_ID,
        help=f"Engagement ID to create (default: {ENGAGEMENT_ID})",
    )
    parser.add_argument(
        "--skip-run", action="store_true",
        help="Scaffold only — do not invoke the agent or verify outputs",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show scaffold progress messages",
    )
    parser.add_argument(
        "--model", default=None,
        help=(
            "Override LLM provider (PydanticAI 'provider:model-id' string). "
            "Sets SDLC_PRIMARY_MODEL env var. "
            "Examples: anthropic:claude-sonnet-4-6  openai:gpt-4o  test"
        ),
    )
    parser.add_argument(
        "--phase-a-only", action="store_true",
        help="Run SA Phase A only — skip SwA Phase C step",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()

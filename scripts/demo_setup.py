"""
ENG-DEMO setup: scaffold, infra-check, run, and verify the TaskFlow API Phase A scenario.

Benchmark Scenario
------------------
No off-the-shelf agentic SE benchmark covers TOGAF ADM architecture work
(the field focuses on code generation / bug-fixing).  This script implements
a *scenario-based test* with specified, machine-verifiable expected outputs,
inspired by SWE-bench methodology applied to architecture document production.

Scenario: "TaskFlow API — Phase A Architecture Vision" (greenfield, EP-0)
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

Usage
-----
  uv run python scripts/demo_setup.py [--verbose] [--skip-run] [--engagement ENG-DEMO]

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

_TASK = (
    "You are the Solution Architect for the TaskFlow API project. "
    "The project brief is at target-repos/taskflow-api/README.md relative to the engagement path. "
    "Perform Phase A (Architecture Vision) for engagement {eid}. "
    "Produce: "
    "(1) Architecture Vision document (write to architecture-repository/overview/architecture-vision.md), "
    "(2) Stakeholder entity files (STK-NNN.friendly-name.md in "
    "architecture-repository/model-entities/motivation/stakeholders/), "
    "(3) Architecture Driver entity files (DRV-NNN.friendly-name.md in "
    "architecture-repository/model-entities/motivation/drivers/), "
    "(4) Architecture Principle entity files (PRI-NNN.friendly-name.md in "
    "architecture-repository/model-entities/motivation/principles/). "
    "Use the write_artifact tool for all file writes. "
    "Follow ERP v2.0 entity file conventions (frontmatter with artifact-id, name, type, status fields; "
    "<!-- §content --> and <!-- §display --> sections). "
    "Aim for 3-5 stakeholders, 3-5 drivers, and 4-6 principles appropriate for a "
    "cloud-native EU-deployed task management API with GDPR constraints."
)


def _print_banner(engagement_id: str) -> None:
    print("╔" + "═" * 60 + "╗")
    print("║  SDLC Multi-Agent System — ENG-DEMO Phase A              ║")
    print("║  Scenario: TaskFlow API Architecture Vision               ║")
    print("╚" + "═" * 60 + "╝")
    print(f"\nEngagement : {engagement_id}")
    print("Agent      : SA (Solution Architect)")
    print("Skill      : SA-PHASE-A")
    print("Phase      : A — Architecture Vision\n")


async def _run(args: argparse.Namespace) -> int:
    engagement_id: str = args.engagement
    verbose: bool = args.verbose

    _print_banner(engagement_id)

    # 1. Scaffold
    print("── Step 1/4: Scaffolding engagement and target repository ──")
    engagement_path = scaffold_demo(_REPO_ROOT, engagement_id, verbose)
    print(f"  Engagement ready at: {engagement_path}\n")

    if args.model:
        os.environ["SDLC_PRIMARY_MODEL"] = args.model
        print(f"  Using model: {args.model}\n")

    # 2. Framework infrastructure check (no LLM required)
    print("── Step 2/4: Framework infrastructure check ────────────────")
    infra_report = check_framework_infra(engagement_id, engagement_path)
    all_infra_passed = print_report(infra_report)
    if not all_infra_passed:
        print("  [ERROR] Framework infrastructure checks failed — aborting.", file=sys.stderr)
        return 2

    if args.skip_run:
        print("  [--skip-run] Skipping agent invocation and verification.")
        return 0

    # 3. Run SA agent
    print("── Step 3/4: Running SA agent (SA-PHASE-A) ─────────────────")
    print("  (Requires ANTHROPIC_API_KEY; may take 60-120 s)\n")
    from src.orchestration.session import EngagementSession

    session = EngagementSession(engagement_id, repo_root=_REPO_ROOT)
    task = _TASK.format(eid=engagement_id)
    try:
        output = await session.invoke_specialist(
            agent_id="SA",
            skill_id="SA-PHASE-A",
            task=task,
            phase="A",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"\n  [ERROR] Agent invocation failed: {exc}", file=sys.stderr)
        print("  Run with --skip-run to test scaffolding without an API key.\n")
        return 2

    print("\n── Agent output (truncated to 1000 chars) ───────────────────")
    print(output[:1000] + ("…" if len(output) > 1000 else ""))

    # 4. Verify
    print("\n── Step 4/4: Verifying outputs ──────────────────────────────")
    report = verify_outputs(engagement_path, session.event_store)
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
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()

"""
ENG-DEMO teardown: remove the TaskFlow API scenario and reset config.

Removes:
  engagements/<engagement_id>/          (entire directory tree)
  ENG-DEMO entry from engagements-config.yaml

Usage
-----
  uv run python scripts/demo_teardown.py [--yes] [--engagement ENG-DEMO] [--verbose]

Pass --yes to skip the confirmation prompt.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.demo_scaffold import ENGAGEMENT_ID, teardown_demo


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ENG-DEMO teardown: remove engagement directory and config entry",
    )
    parser.add_argument(
        "--engagement", default=ENGAGEMENT_ID,
        help=f"Engagement ID to remove (default: {ENGAGEMENT_ID})",
    )
    parser.add_argument(
        "--yes", "-y", action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show progress messages",
    )
    args = parser.parse_args()

    engagement_path = _REPO_ROOT / "engagements" / args.engagement
    print(f"Teardown target: {engagement_path}")

    if not args.yes:
        try:
            answer = input("Remove this engagement? This cannot be undone. [y/N]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)
        if answer.lower() not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    teardown_demo(_REPO_ROOT, args.engagement, verbose=args.verbose)
    print(f"  Done. Engagement '{args.engagement}' removed.")


if __name__ == "__main__":
    main()

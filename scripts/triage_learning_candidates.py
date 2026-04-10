"""
triage_learning_candidates.py — Surface learning entries for rationalization table maintenance.

Reads learnings/*.md files across all engagement directories (and enterprise-repository),
filters for entries that are candidates for rationalization table additions (error-type:
protocol-skip, gate-veto, or flagged with rationalization-candidate: true), groups by
skill-id, and formats a triage list for human review.

Usage:
    uv run python scripts/triage_learning_candidates.py [--path PATH] [--min-count N] [--skill SKILL_ID]

The human reviewer examines the output and decides which entries represent a genuine
rationalization pattern worth adding to the skill's ## Common Rationalizations (Rejected)
table. This script does NOT auto-classify — it reduces the search space for human review.

Threshold guidance (not enforced):
    2+ structurally similar corrections in the same skill → strong candidate for table entry
    1 occurrence                                          → monitor; consider adding if severe

Exit codes:
    0 — candidates found and printed
    1 — no candidates found (normal on first run or clean engagement)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_FIELD_RE = re.compile(r"^(\S[^:]*?):\s*(.+)$", re.MULTILINE)

# error-types that are candidates for rationalization analysis
_CANDIDATE_ERROR_TYPES = frozenset({"protocol-skip", "wrong-scope", "omission"})

# frontmatter field flagged by sprint review annotation
_RATIONALIZATION_FLAG = "rationalization-candidate"


def _parse_frontmatter(text: str) -> dict[str, str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    return {k.strip(): v.strip() for k, v in _FIELD_RE.findall(m.group(1))}


def _extract_correction(text: str) -> str:
    """Return the ## Correction section body, or first non-frontmatter paragraph."""
    # Try to find an explicit ## Correction section
    m = re.search(r"##\s+Correction\s*\n+(.*?)(?:\n##|\Z)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fall back: first non-empty paragraph after frontmatter
    body = _FRONTMATTER_RE.sub("", text, count=1).strip()
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    return paragraphs[0] if paragraphs else ""


def _find_learning_files(root: Path) -> list[Path]:
    """Recursively find all learning entry .md files under learnings/ directories."""
    return list(root.rglob("learnings/*.md"))


def _is_candidate(fm: dict[str, str]) -> bool:
    error_type = fm.get("error-type", "").lower()
    rationalization_flag = fm.get(_RATIONALIZATION_FLAG, "").lower()
    if rationalization_flag in ("true", "yes", "1"):
        return True
    return error_type in _CANDIDATE_ERROR_TYPES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Triage learning entries for rationalization table candidates")
    parser.add_argument(
        "--path",
        default=".",
        help="Root path to search for learnings/ directories (default: current directory)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Minimum occurrence count to include in output (default: 1)",
    )
    parser.add_argument(
        "--skill",
        default=None,
        help="Filter to a specific skill-id (e.g. SA-PHASE-A)",
    )
    parser.add_argument(
        "--flagged-only",
        action="store_true",
        help="Show only entries flagged with rationalization-candidate: true",
    )
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"ERROR: path does not exist: {root}", file=sys.stderr)
        return 2

    files = _find_learning_files(root)
    if not files:
        print("No learning files found. Run some engagements first.", file=sys.stderr)
        return 1

    # Group candidates: skill_id -> list of (file, frontmatter, correction_text)
    grouped: dict[str, list[tuple[Path, dict[str, str], str]]] = defaultdict(list)

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_frontmatter(text)
        if not fm:
            continue
        if args.skill and fm.get("skill-id", "").upper() != args.skill.upper():
            continue
        if args.flagged_only:
            if fm.get(_RATIONALIZATION_FLAG, "").lower() not in ("true", "yes", "1"):
                continue
        elif not _is_candidate(fm):
            continue
        skill_id = fm.get("skill-id", "UNKNOWN")
        correction = _extract_correction(text)
        grouped[skill_id].append((f, fm, correction))

    # Filter by min-count
    filtered = {k: v for k, v in grouped.items() if len(v) >= args.min_count}

    if not filtered:
        print("No candidates found matching the specified criteria.", file=sys.stderr)
        return 1

    # Output triage report
    total = sum(len(v) for v in filtered.values())
    print(f"=== Rationalization Table Triage Report ===")
    print(f"Root: {root}")
    print(f"Total candidate entries: {total} across {len(filtered)} skill(s)")
    print(f"Min occurrence threshold: {args.min_count}")
    print()

    for skill_id in sorted(filtered, key=lambda k: (-len(filtered[k]), k)):
        entries = filtered[skill_id]
        print(f"── {skill_id}  ({len(entries)} candidate(s)) ──────────────────────────────")
        for i, (path, fm, correction) in enumerate(entries, 1):
            error_type = fm.get("error-type", "?")
            importance = fm.get("importance", "?")
            phase = fm.get("phase", "?")
            flagged = fm.get(_RATIONALIZATION_FLAG, "false").lower() in ("true", "yes", "1")
            flag_marker = " [FLAGGED]" if flagged else ""
            print(f"  [{i}]{flag_marker} phase={phase}  error-type={error_type}  importance={importance}")
            print(f"      File: {path.relative_to(root)}")
            if correction:
                # Wrap long lines for readability
                for line in correction.splitlines()[:4]:
                    print(f"      | {line[:120]}")
            print()
        print(
            f"  ACTION: Review the {len(entries)} entries above. "
            f"If 2+ share a pattern, add a row to agents/*/{skill_id.lower().replace('_', '-')}"
            f"/skills/*.md ## Common Rationalizations (Rejected)."
        )
        print()

    print("To add an entry to a rationalization table, edit the relevant skill file and add a row:")
    print("  | <rationalization the agent might make> | <why it is wrong and what to do instead> |")
    print()
    print("To flag an entry for next triage, add  rationalization-candidate: true  to its frontmatter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

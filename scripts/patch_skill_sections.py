#!/usr/bin/env python3
"""
Patch skill files — Stage 5.7-D/E structural changes.

  mode-tags         Add <!-- workflow --> to Algedonic Triggers / End-of-Skill Memory Close.
  invoke-never-when Add invoke-never-when stub to frontmatter if missing.
  red-flags         Add ## Red Flags stub after ## Feedback Loop (complex+standard).
  verification      Add ## Verification stub after ## Algedonic Triggers (complex+standard).
  rationalizations  Add ## Common Rationalizations stub after ## Procedure (complex only).

Usage:
  uv run python scripts/patch_skill_sections.py --dry-run              # show all changes
  uv run python scripts/patch_skill_sections.py --dry-run --limit 3    # verify subset
  uv run python scripts/patch_skill_sections.py --changes mode-tags --skills SA-PHASE-B
  uv run python scripts/patch_skill_sections.py                        # apply all
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import frontmatter as fm


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_ROOT = REPO_ROOT / "agents"

ALL_CHANGES = ["mode-tags", "invoke-never-when", "red-flags", "verification", "rationalizations"]

# Sections that get mode tags
WORKFLOW_ONLY_HEADINGS = {
    "algedonic triggers",
    "end-of-skill memory close",
}

# Section stubs — will be inserted with a TODO marker
_RED_FLAGS_STUB = """\
## Red Flags

Pre-escalation observable indicators. Raise an algedonic signal or CQ if two or
more of these are true simultaneously:

<!-- TODO: add 5-7 role-specific observable indicators for this skill -->
- Outputs section of the primary artifact is blank after completing the procedure
- Any required input artifact is missing and no CQ has been raised
- Feedback loop iteration count has reached the maximum with no resolution
"""

_VERIFICATION_STUB = """\
## Verification

Before emitting the completion event for this skill, confirm:

<!-- TODO: extend with skill-specific checklist items -->
- [ ] All blocking CQs resolved or documented as PM-accepted assumptions
- [ ] Primary output artifact exists at the required minimum version
- [ ] CSCO sign-off recorded where required (`csco-sign-off: true`)
- [ ] All required EventStore events emitted in this invocation
- [ ] Handoffs to downstream agents created
- [ ] Learning entries recorded if a §3.1 trigger was met this invocation
- [ ] Memento state saved (End-of-Skill Memory Close)
"""

_RATIONALIZATIONS_STUB = """\
## Common Rationalizations (Rejected)

| Rationalization | Rejection |
|---|---|
<!-- TODO: add 2-3 skill-specific rationalization rows -->
| "I can skip discovery because I already know the context from prior sessions" | Discovery is mandatory per Step 0; any skip must be recorded as a PM-accepted assumption with a risk flag; silent assumptions are governance violations |
| "A CQ with a reasonable assumed answer is equivalent to waiting — I'll proceed with the assumption" | Assumed answers must be explicitly recorded in the artifact with a risk flag; they never silently replace CQ answers |
"""

_INVOKE_NEVER_WHEN_STUB = (
    "<!-- TODO: write plain-English condition that prevents misrouting "
    "to this skill -->"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_H2_RE = re.compile(r"^(## .+?)$", re.MULTILINE)

# Alias → canonical (mirrors _ALIAS_MAP in _skill_sections.py)
_ALIASES: dict[str, str] = {"steps": "procedure"}


def _heading_key(heading: str) -> str:
    """Normalise heading to canonical lower-case key."""
    raw = heading.removeprefix("## ").strip()
    raw = re.sub(r"\s*<!--.*?-->\s*$", "", raw).strip()
    key = raw.lower()
    if key in _ALIASES:
        return _ALIASES[key]
    # Prefix alias: "steps: ..." → "procedure"
    for alias, canonical in _ALIASES.items():
        if key.startswith(alias + ":") or key.startswith(alias + " "):
            return canonical
    return key


def apply_mode_tags(content: str) -> tuple[str, list[str]]:
    """Add <!-- workflow --> to workflow-only section headings."""
    changes: list[str] = []

    def _replace(m: re.Match[str]) -> str:  # type: ignore[type-arg]
        heading_raw = m.group(1)
        key = _heading_key(heading_raw)
        if key in WORKFLOW_ONLY_HEADINGS and "<!--" not in heading_raw:
            new_heading = f"{heading_raw} <!-- workflow -->"
            changes.append(f"  mode-tag: '{heading_raw}' → '{new_heading}'")
            return new_heading
        return heading_raw

    new_content = _H2_RE.sub(_replace, content)
    return new_content, changes


def apply_section_stubs(
    content: str,
    complexity: str,
    changes_to_apply: set[str],
) -> tuple[str, list[str]]:
    """Insert missing section stubs at the correct positions."""
    changes: list[str] = []

    # Determine what sections are already present
    existing = {_heading_key(h) for h in _H2_RE.findall(content)}

    sections_to_add: list[tuple[str, str, str]] = []
    # (section_key, stub_text, insert_after_key)

    if "rationalizations" in changes_to_apply and complexity == "complex":
        if "common rationalizations (rejected)" not in existing:
            sections_to_add.append(
                ("common rationalizations (rejected)",
                 _RATIONALIZATIONS_STUB,
                 "procedure"))

    if "red-flags" in changes_to_apply and complexity in ("complex", "standard"):
        if "red flags" not in existing:
            sections_to_add.append(
                ("red flags", _RED_FLAGS_STUB, "feedback loop"))

    if "verification" in changes_to_apply and complexity in ("complex", "standard"):
        if "verification" not in existing:
            sections_to_add.append(
                ("verification", _VERIFICATION_STUB, "algedonic triggers"))

    for section_key, stub, insert_after in sections_to_add:
        # Find the end of the "insert_after" section
        pattern = re.compile(
            r"(## [^\n]+\n.*?)(?=\n## |\Z)",
            re.DOTALL,
        )
        # Locate the target section by heading key
        inserted = False
        for m in list(_H2_RE.finditer(content)):
            if _heading_key(m.group(1)) == insert_after:
                # Find the end of this section (next ## or EOF)
                section_start = m.start()
                next_h2 = _H2_RE.search(content, m.end())
                section_end = next_h2.start() if next_h2 else len(content)
                insert_pos = section_end
                content = content[:insert_pos] + "\n" + stub + "\n" + content[insert_pos:]
                changes.append(f"  stub-insert: '## {section_key.title()}' after '## {insert_after.title()}'")
                inserted = True
                break
        if not inserted:
            # Append at end if insert_after not found
            content = content.rstrip("\n") + "\n\n" + stub
            changes.append(f"  stub-append: '## {section_key.title()}' (insert_after not found)")

    return content, changes


def apply_invoke_never_when(
    raw_text: str,
    post: fm.Post,
    changes: list[str],
) -> str:
    """Add invoke-never-when stub to frontmatter if missing."""
    if post.get("invoke-never-when"):
        return raw_text  # already present

    # Insert after invoke-when
    frontmatter_end = raw_text.index("---", 3) + 3
    fm_block = raw_text[:frontmatter_end]
    rest = raw_text[frontmatter_end:]

    stub_line = f"invoke-never-when: >\n  {_INVOKE_NEVER_WHEN_STUB}\n"

    if "invoke-when:" in fm_block:
        # Find end of invoke-when block (next key or end of frontmatter)
        m = re.search(r"^invoke-when:.*?(?=\n\w|\Z)", fm_block, re.DOTALL | re.MULTILINE)
        if m:
            insert_at = m.end()
            fm_block = fm_block[:insert_at] + "\n" + stub_line + fm_block[insert_at:]
            changes.append("  invoke-never-when: stub added to frontmatter")
            return fm_block + rest

    # Fallback: append before closing ---
    closing = fm_block.rfind("\n---")
    fm_block = fm_block[:closing] + "\n" + stub_line + fm_block[closing:]
    changes.append("  invoke-never-when: stub appended to frontmatter")
    return fm_block + rest


# ---------------------------------------------------------------------------
# Per-file processor
# ---------------------------------------------------------------------------

def process_file(
    path: Path,
    changes_to_apply: set[str],
    dry_run: bool,
) -> list[str]:
    """Apply requested changes to a skill file. Returns list of change descriptions."""
    raw = path.read_text(encoding="utf-8")
    post = fm.loads(raw)
    complexity = str(post.get("complexity-class", "standard"))
    skill_id = str(post.get("skill-id", path.stem))

    all_changes: list[str] = []
    new_raw = raw
    body_start = raw.index("---", 3) + 3  # offset past closing ---
    new_body = raw[body_start:]

    if "mode-tags" in changes_to_apply:
        patched_body, tag_changes = apply_mode_tags(new_body)
        if tag_changes:
            all_changes.extend(tag_changes)
            new_body = patched_body

    section_changes_to_apply = changes_to_apply & {"rationalizations", "red-flags", "verification"}
    if section_changes_to_apply:
        patched_body, sec_changes = apply_section_stubs(
            new_body, complexity, section_changes_to_apply
        )
        if sec_changes:
            all_changes.extend(sec_changes)
            new_body = patched_body

    if "invoke-never-when" in changes_to_apply:
        new_raw_candidate = apply_invoke_never_when(
            raw[:body_start] + new_body, post, all_changes
        )
        if new_raw_candidate != raw[:body_start] + new_body:
            new_raw = new_raw_candidate
        else:
            new_raw = raw[:body_start] + new_body
    else:
        new_raw = raw[:body_start] + new_body

    if all_changes and not dry_run:
        path.write_text(new_raw, encoding="utf-8")

    return all_changes


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch skill files with Stage 5.7-D/E structural changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files.",
    )
    parser.add_argument(
        "--changes", nargs="+", choices=ALL_CHANGES, default=ALL_CHANGES,
        metavar="CHANGE",
        help=f"Changes to apply (default: all). Choices: {ALL_CHANGES}",
    )
    parser.add_argument(
        "--skills", nargs="+", metavar="SKILL_ID",
        help="Limit to specific skill IDs (e.g. SA-PHASE-B DE-PHASE-G).",
    )
    parser.add_argument(
        "--complexity", choices=["complex", "standard", "simple"],
        help="Limit to skills of a specific complexity class.",
    )
    parser.add_argument(
        "--limit", type=int,
        help="Process at most N skill files (for verification runs).",
    )
    args = parser.parse_args()

    changes_to_apply = set(args.changes)
    skill_filter = set(args.skills) if args.skills else None

    all_paths = sorted(AGENTS_ROOT.glob("*/skills/*.md"))
    total_changed = 0
    processed = 0

    for path in all_paths:
        if args.limit and processed >= args.limit:
            break

        try:
            post = fm.load(str(path))
        except Exception as e:
            print(f"SKIP {path.name}: frontmatter parse error — {e}", file=sys.stderr)
            continue

        skill_id = str(post.get("skill-id", ""))
        complexity = str(post.get("complexity-class", "standard"))

        if skill_filter and skill_id not in skill_filter:
            continue
        if args.complexity and complexity != args.complexity:
            continue

        processed += 1
        file_changes = process_file(path, changes_to_apply, dry_run=args.dry_run)

        if file_changes:
            total_changed += 1
            prefix = "[DRY-RUN] " if args.dry_run else "[PATCHED] "
            print(f"{prefix}{skill_id} ({complexity}) — {path.relative_to(REPO_ROOT)}")
            for c in file_changes:
                print(c)

    print(
        f"\n{'[DRY-RUN] ' if args.dry_run else ''}"
        f"Total: {total_changed}/{processed} skills would be patched"
        if args.dry_run
        else f"Total: {total_changed}/{processed} skills patched"
    )


if __name__ == "__main__":
    main()

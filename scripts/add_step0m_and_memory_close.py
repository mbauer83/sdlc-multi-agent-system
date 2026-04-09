"""
Migration script: add Step 0.M (Memento Recall) + End-of-Skill Memory Close
to all agent skill files that don't already have them.

Run from the repo root:
    uv run python scripts/add_step0m_and_memory_close.py [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Template blocks
# ---------------------------------------------------------------------------

_STEP0M_TEMPLATE = """\
### Step 0.M — Memento Recall *(via `get_memento_state` tool)*

Call `get_memento_state(phase={phase})`. If state is returned: inject `key_decisions` and `open_threads` into working context as **"Prior invocation state for this phase:"** followed by numbered lists. If no state exists (first invocation for this phase): proceed to the next step. Governed by `framework/discovery-protocol.md §2` and `framework/learning-protocol.md §13`.

---

"""

_END_OF_SKILL_TEMPLATE = """\

---

## End-of-Skill Memory Close

After the primary output artifact is produced (or after the final step if no artifact), execute unconditionally:

1. `save_memento_state(phase={phase}, key_decisions=[...], open_threads=[...])` — capture key decisions made and threads left open during this invocation.
2. `record_learning(entry_type="episodic", ...)` — if a significant discovery or key decision occurred that benefits future invocations. Governed by `framework/learning-protocol.md §13.3`.
3. `record_learning(...)` — if a §3.1/§3.2 trigger condition was met during this skill. Governed by `framework/learning-protocol.md §3–4`.
"""

# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)


def _extract_trigger_phases(content: str) -> str:
    """
    Return a phase expression string for the memento tool call.
    - Single phase  → '"B"' (quoted literal)
    - Multi-phase   → '<current_phase>' (runtime placeholder)
    """
    match = _FM_RE.match(content)
    if not match:
        return "<current_phase>"

    fm_text = match.group(1)
    # Simple line-by-line parse; avoids dependency on pyyaml import overhead
    for line in fm_text.splitlines():
        if line.startswith("trigger-phases:"):
            rest = line[len("trigger-phases:"):].strip()
            # Expect YAML inline list: [A, B, ...] or [A]
            items = re.findall(r"[A-Za-z0-9]+", rest)
            if len(items) == 1:
                return f'"{items[0]}"'
            return "<current_phase>"
    return "<current_phase>"


# ---------------------------------------------------------------------------
# Insertion helpers
# ---------------------------------------------------------------------------

_STEP0L_HEADING_RE = re.compile(
    r"(### Step 0\.L[^\n]*\n(?:(?!###)(?!^---$).)*?\n)---\n",
    re.MULTILINE | re.DOTALL,
)


def _insert_step0m(content: str, phase: str) -> tuple[str, bool]:
    """
    Insert Step 0.M block immediately after the first Step 0.L section's
    trailing '---' separator.  Returns (new_content, was_changed).
    """
    step0m_block = _STEP0M_TEMPLATE.format(phase=phase)

    match = _STEP0L_HEADING_RE.search(content)
    if not match:
        return content, False

    # Insert the Step 0.M block right after the trailing '---\n' of Step 0.L
    insert_pos = match.end()
    new_content = content[:insert_pos] + step0m_block + content[insert_pos:]
    return new_content, True


def _append_end_of_skill(content: str, phase: str) -> tuple[str, bool]:
    """
    Append End-of-Skill Memory Close at the very end of the file.
    """
    block = _END_OF_SKILL_TEMPLATE.format(phase=phase)
    # Normalise trailing whitespace so we don't double-add blank lines
    new_content = content.rstrip() + "\n" + block
    return new_content, True


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_file(path: Path, dry_run: bool = False) -> str:
    """
    Process one skill file.  Returns a short status string.
    """
    content = path.read_text(encoding="utf-8")

    # --- idempotency guards ---
    has_step0m = "Step 0.M" in content or "get_memento_state" in content
    has_eos = "End-of-Skill Memory Close" in content or "save_memento_state" in content

    if has_step0m and has_eos:
        return "SKIP (already complete)"

    phase = _extract_trigger_phases(content)
    changed = False

    if not has_step0m:
        content, ok = _insert_step0m(content, phase)
        if not ok:
            return "WARN: Step 0.L not found — skipped Step 0.M insertion"
        changed = True

    if not has_eos:
        content, _ = _append_end_of_skill(content, phase)
        changed = True

    if not changed:
        return "SKIP (no changes needed)"

    if not dry_run:
        path.write_text(content, encoding="utf-8")
        return f"OK  (phase={phase})"
    else:
        return f"DRY-RUN OK (phase={phase})"


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    repo_root = Path(__file__).parent.parent
    skills_dir = repo_root / "agents"

    skill_files = sorted(skills_dir.glob("*/skills/*.md"))
    if not skill_files:
        print("No skill files found — check that you're running from the repo root.")
        sys.exit(1)

    print(f"Processing {len(skill_files)} skill files (dry_run={dry_run})\n")

    ok_count = warn_count = skip_count = 0
    for path in skill_files:
        status = process_file(path, dry_run=dry_run)
        rel = path.relative_to(repo_root)
        print(f"  {status:<40}  {rel}")
        if status.startswith("OK") or status.startswith("DRY"):
            ok_count += 1
        elif status.startswith("WARN"):
            warn_count += 1
        else:
            skip_count += 1

    print(f"\nDone: {ok_count} updated, {skip_count} skipped, {warn_count} warnings.")
    if warn_count:
        print("WARNING: some files could not be updated. Check the WARN lines above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
generate_macros.py — Regenerate _macros.puml from entity §display ###archimate blocks.

Usage:
    uv run python -m src.tools.generate_macros [REPO_ROOT]

    REPO_ROOT defaults to the engagement architecture repository at
    engagements/ENG-001/work-repositories/architecture-repository/
    relative to the project root (parent of src/).

The script scans every .md file under <REPO_ROOT>/model-entities/ for a
§display ###archimate block, extracts layer/element-type/label/alias fields,
and writes <REPO_ROOT>/diagram-catalog/_macros.puml.

Alias convention (PlantUML):
    PlantUML aliases use underscores (APP_001) so they work inside grouping
    rectangles. The entity artifact-id (APP-001, with hyphen) is used only
    as the human-readable label suffix and in the §display block itself.
    In diagram source files, reference elements by their alias (APP_001), not
    by their artifact-id (APP-001).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DISPLAY_SECTION = re.compile(r"<!--\s*§display\s*-->", re.IGNORECASE)
_ARCHIMATE_H3 = re.compile(r"###\s*archimate\b", re.IGNORECASE)
_YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL)


def _extract_archimate_block(content: str) -> dict | None:
    """Return the parsed archimate YAML block from §display, or None."""
    m = _DISPLAY_SECTION.search(content)
    if not m:
        return None
    display_text = content[m.end():]
    h3 = _ARCHIMATE_H3.search(display_text)
    if not h3:
        return None
    after_h3 = display_text[h3.end():]
    fence = _YAML_FENCE.search(after_h3)
    if not fence:
        return None
    try:
        return yaml.safe_load(fence.group(1)) or {}
    except yaml.YAMLError:
        return None


_LAYER_ORDER = {
    "motivation": 0,
    "strategy": 1,
    "business": 2,
    "application": 3,
    "technology": 4,
    "physical": 5,
    "implementation": 6,
}

_PREFIX_ORDER = [
    "STK", "DRV", "ASM", "GOL", "OUT", "PRI", "REQ", "CST", "MEA", "VAL",
    "CAP", "VS", "RES", "COA",
    "ACT", "ROL", "COL", "BIF", "BPR", "BFN", "BIA", "BEV", "BSV", "BOB",
    "APP", "AIF", "ASV", "DOB",
    "NOD", "DEV", "SYS",
    "EQP", "FAC", "DIS", "MAT",
    "WPK", "DEL", "IEV", "GAP", "PLT",
]


def _sort_key(entry: tuple[str, str, str]) -> tuple[int, int, int]:
    """Sort by layer → prefix → numeric suffix."""
    layer, _, alias = entry  # alias = APP_001
    artifact_id = alias.replace("_", "-")  # APP-001
    prefix = re.match(r"([A-Z]+)", artifact_id)
    prefix_str = prefix.group(1) if prefix else ""
    num_m = re.search(r"(\d+)$", artifact_id)
    num = int(num_m.group(1)) if num_m else 0
    layer_idx = _LAYER_ORDER.get(layer.lower(), 99)
    prefix_idx = _PREFIX_ORDER.index(prefix_str) if prefix_str in _PREFIX_ORDER else 99
    return layer_idx, prefix_idx, num


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_macros(repo_root: Path) -> Path:
    """Scan repo_root/model-entities/ and write diagram-catalog/_macros.puml.

    Returns the path to the written file.
    """
    entities_root = repo_root / "model-entities"
    if not entities_root.is_dir():
        raise FileNotFoundError(f"model-entities/ not found under {repo_root}")

    entries: list[tuple[str, str, str]] = []  # (layer, macro_line, alias)

    for md_file in sorted(entities_root.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        archimate = _extract_archimate_block(content)
        if not archimate:
            continue

        label = archimate.get("label", "")
        element_type = archimate.get("element-type", "")
        alias_raw = archimate.get("alias", "")  # e.g. APP_001

        if not (label and element_type and alias_raw):
            continue

        # Alias uses underscore (PlantUML identifier convention).
        alias = alias_raw.replace("-", "_")
        # Macro name uses DECL_ prefix so that connection lines (which reference
        # elements by alias only) do not trigger macro expansion.
        # Usage:
        #   Inside rectangle groups: DECL_APP_001  (expands → declares element)
        #   In connection lines:     APP_001        (alias only — no expansion)
        macro_name = f"DECL_{alias}"

        # Derive layer from directory path segment between model-entities/ and file
        rel = md_file.relative_to(entities_root)
        layer = rel.parts[0] if rel.parts else "unknown"

        macro_line = f'!define {macro_name} rectangle "{label}" <<{element_type}>> as {alias}'
        entries.append((layer, macro_line, alias))

    entries.sort(key=_sort_key)

    # Group by layer for section comments
    lines: list[str] = [
        "' _macros.puml — ENG-001 ArchiMate element macro library",
        "' Auto-generated from entity §display ###archimate blocks.",
        "' Do not edit manually — regenerated by generate_macros().",
        "'",
        "' USAGE CONVENTION (two-token pattern):",
        "'   Declare element inside a grouping rectangle:  DECL_APP_001",
        "'   Reference element in a connection line:       APP_001",
        "'",
        "' WHY: PlantUML !define macros expand on every token occurrence.",
        "' If macro name == alias, connection lines like 'APP_001 --> APP_002'",
        "' expand to the full rectangle declaration, causing syntax errors.",
        "' The DECL_ prefix separates the expansion trigger from the element alias.",
        "",
    ]

    current_layer = None
    for layer, macro_line, _ in entries:
        if layer != current_layer:
            if current_layer is not None:
                lines.append("")
            lines.append(f"' {'-' * 75}")
            lines.append(f"' {layer.capitalize()}")
            lines.append(f"' {'-' * 75}")
            current_layer = layer
        lines.append(macro_line)

    output = "\n".join(lines) + "\n"
    out_path = repo_root / "diagram-catalog" / "_macros.puml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    print(f"Written {len(entries)} macros → {out_path}")
    return out_path


def main() -> None:
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1]).resolve()
    else:
        # Default: project root is parent of src/tools/
        project_root = Path(__file__).resolve().parent.parent.parent
        repo_root = (
            project_root
            / "engagements"
            / "ENG-001"
            / "work-repositories"
            / "architecture-repository"
        )

    if not repo_root.is_dir():
        print(f"ERROR: repo_root does not exist: {repo_root}", file=sys.stderr)
        sys.exit(1)

    generate_macros(repo_root)


if __name__ == "__main__":
    main()

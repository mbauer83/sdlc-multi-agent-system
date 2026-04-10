"""
Internal helpers for diagram_tools: path resolution and §display block reading.

Uses ModelRepository (src/common/model_query.py) for artifact lookup — the same
registry used by universal_tools.py and the MCP model server, so there is one
canonical index across all tool surfaces.

Not a public API — import only from diagram_tools.py.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def resolve_arch_repo(ctx: RunContext[AgentDeps], override: str | None) -> Path | None:
    """Return the architecture-repository root path."""
    if override:
        p = Path(override)
        return p if p.is_dir() else None
    arch_repo = ctx.deps.work_repos_path / "architecture-repository"
    return arch_repo if arch_repo.is_dir() else None


def resolve_puml_path(ctx: RunContext[AgentDeps], puml_path: str) -> Path | None:
    """Resolve puml_path against engagement directory if relative."""
    p = Path(puml_path)
    if p.is_absolute():
        return p
    for base in (ctx.deps.engagement_path, ctx.deps.work_repos_path):
        candidate = (base / p).resolve()
        if candidate.exists():
            return candidate
    return (ctx.deps.engagement_path / p).resolve()


# ---------------------------------------------------------------------------
# Artifact display-block reading (via ModelRepository — canonical registry)
# ---------------------------------------------------------------------------


def read_er_block(arch_repo: Path, artifact_id: str) -> str | None:
    """
    Return the §display ###er block content for an artifact.

    Uses ModelRepository (same as universal_tools.list_artifacts / read_artifact
    and the MCP model_query_read_artifact tool) so all tool surfaces share one
    index rather than maintaining separate file-scan paths.
    """
    try:
        from src.common.model_query import ModelRepository

        repo = ModelRepository(arch_repo)
        result = repo.read_artifact(artifact_id, mode="full")
        if result is None:
            return None
        blocks: dict = getattr(result, "display_blocks", {}) or {}
        return blocks.get("er") or blocks.get("ER")
    except Exception:  # noqa: BLE001
        # Fall back to direct file parse if ModelRepository is unavailable
        return _direct_file_er_block(arch_repo, artifact_id)


def _direct_file_er_block(arch_repo: Path, artifact_id: str) -> str | None:
    """Fallback: scan model-entities/ directly for the §display ###er block."""
    _DISPLAY_RE = re.compile(r"<!--\s*§display\s*-->", re.IGNORECASE)
    _H3_RE = re.compile(r"###\s*(\w[\w-]*)", re.IGNORECASE)
    _FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)

    entities_root = arch_repo / "model-entities"
    if not entities_root.is_dir():
        return None

    prefix = artifact_id.split("-")[0] if "-" in artifact_id else ""
    for md in entities_root.rglob(f"{artifact_id}*.md"):
        content = md.read_text(encoding="utf-8")
        m = _DISPLAY_RE.search(content)
        if not m:
            continue
        display_text = content[m.end():]
        for h3 in _H3_RE.finditer(display_text):
            if h3.group(1).lower() == "er":
                after = display_text[h3.end():]
                fence = _FENCE_RE.search(after)
                if fence:
                    return fence.group(1)
    return None


# ---------------------------------------------------------------------------
# plantuml rendering
# ---------------------------------------------------------------------------


def run_plantuml(puml_path: Path, rendered_dir: Path) -> str:
    """
    Invoke plantuml CLI to render puml_path to SVG in rendered_dir.
    Returns path to SVG as string, or an error/skip string.
    """
    plantuml_bin = shutil.which("plantuml") or shutil.which("plantuml.jar")
    if plantuml_bin is None:
        return (
            "[Skipped] plantuml CLI not found on PATH. "
            "Install plantuml (e.g. apt install plantuml) to enable rendering. "
            "Diagram source has been written; SVG rendering is deferred."
        )
    rendered_dir.mkdir(parents=True, exist_ok=True)
    try:
        cmd = [plantuml_bin, "-tsvg", "-o", str(rendered_dir), str(puml_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            stderr = proc.stderr[:500] if proc.stderr else "(no stderr)"
            return f"[Error] plantuml exited {proc.returncode}: {stderr}"
        svg_path = rendered_dir / (puml_path.stem + ".svg")
        return str(svg_path) if svg_path.exists() else f"[Error] SVG not found at {svg_path}"
    except subprocess.TimeoutExpired:
        return "[Error] plantuml timed out (>60 s)."
    except Exception as exc:  # noqa: BLE001
        return f"[Error] render failed: {exc}"

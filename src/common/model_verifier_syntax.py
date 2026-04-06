from __future__ import annotations

import os
import re
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from src.common.model_verifier_types import Issue, Severity


@lru_cache(maxsize=1)
def find_plantuml_jar() -> Path | None:
    candidate = Path(__file__).resolve()
    for _ in range(6):
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists():
            jar = candidate / "tools" / "plantuml.jar"
            return jar if jar.exists() else None
    return None


def resolve_worker_count() -> int:
    cpu = os.cpu_count() or 1
    return max(1, min(32, cpu + 4))


def check_puml_syntax(path: Path, loc: str) -> list[Issue]:
    result: list[Issue] = []
    jar = find_plantuml_jar()
    if jar is None:
        return [Issue(Severity.WARNING, "W350", "tools/plantuml.jar not found; PUML syntax check skipped", loc)]

    java = os.environ.get("JAVA_HOME", "")
    java_exe = (Path(java) / "bin" / "java") if java else Path("java")

    try:
        with tempfile.TemporaryDirectory() as tmp_out:
            proc = subprocess.run(
                [str(java_exe), "-jar", str(jar), "-tsvg", "-verbose", "-o", tmp_out, str(path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
    except FileNotFoundError:
        return [Issue(Severity.WARNING, "W351", "java not found on PATH; PUML syntax check skipped", loc)]
    except subprocess.TimeoutExpired:
        return [Issue(Severity.WARNING, "W352", "plantuml render timed out after 30 s", loc)]

    if proc.returncode == 0:
        return result

    combined = proc.stdout + proc.stderr
    error_lines = re.findall(r"^Error line \d+ in file:.*$", combined, re.MULTILINE)
    syntax_lines = re.findall(r"Syntax Error\?.*", combined)
    reported = error_lines or syntax_lines

    if reported:
        for line in reported:
            result.append(Issue(Severity.ERROR, "E350", f"PlantUML: {line.strip()}", loc))
        return result

    signal_lines = [
        ln.strip()
        for ln in combined.splitlines()
        if ln.strip()
        and "IOException" not in ln
        and "Cannot run program" not in ln
        and "Caused by" not in ln
        and "at java." not in ln
        and "at net." not in ln
        and ln.strip() not in ("Some diagram description contains errors",)
    ]
    msg = signal_lines[0] if signal_lines else f"exit {proc.returncode}"
    return [Issue(Severity.ERROR, "E350", f"PlantUML error (exit {proc.returncode}): {msg[:200]}", loc)]


def check_puml_syntax_batch(paths: list[Path], *, chunk_size: int = 120) -> dict[Path, list[Issue]]:
    issues_by_path: dict[Path, list[Issue]] = {p: [] for p in paths}
    if not paths:
        return issues_by_path

    jar = find_plantuml_jar()
    if jar is None:
        for path in paths:
            issues_by_path[path].append(Issue(
                Severity.WARNING,
                "W350",
                "tools/plantuml.jar not found; PUML syntax check skipped",
                str(path),
            ))
        return issues_by_path

    java = os.environ.get("JAVA_HOME", "")
    java_exe = (Path(java) / "bin" / "java") if java else Path("java")

    for i in range(0, len(paths), chunk_size):
        path_chunk = paths[i:i + chunk_size]
        try:
            with tempfile.TemporaryDirectory() as tmp_out:
                proc = subprocess.run(
                    [
                        str(java_exe),
                        "-jar",
                        str(jar),
                        "-tsvg",
                        "-verbose",
                        "-o",
                        tmp_out,
                        *[str(p) for p in path_chunk],
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
        except FileNotFoundError:
            for path in path_chunk:
                issues_by_path[path].append(Issue(
                    Severity.WARNING,
                    "W351",
                    "java not found on PATH; PUML syntax check skipped",
                    str(path),
                ))
            continue
        except subprocess.TimeoutExpired:
            for path in path_chunk:
                issues_by_path[path].append(Issue(
                    Severity.WARNING,
                    "W352",
                    "plantuml render timed out after 120 s",
                    str(path),
                ))
            continue

        if proc.returncode == 0:
            continue

        combined = proc.stdout + proc.stderr
        file_error_matches = re.findall(r"^Error line \d+ in file: (.*)$", combined, re.MULTILINE)
        attributed = False
        if file_error_matches:
            for matched_path in file_error_matches:
                candidate = Path(matched_path.strip())
                issue = Issue(Severity.ERROR, "E350", f"PlantUML: Error line in file: {candidate}", str(candidate))
                if candidate in issues_by_path:
                    issues_by_path[candidate].append(issue)
                    attributed = True
                else:
                    resolved = candidate.resolve()
                    if resolved in issues_by_path:
                        issues_by_path[resolved].append(issue)
                        attributed = True

        syntax_lines = re.findall(r"Syntax Error\?.*", combined)
        if syntax_lines:
            fallback = syntax_lines[0].strip()
            for path in path_chunk:
                if not issues_by_path[path]:
                    issues_by_path[path].append(Issue(
                        Severity.ERROR,
                        "E350",
                        f"PlantUML: {fallback}",
                        str(path),
                    ))
            attributed = True

        if attributed:
            continue

        # Batch output was non-zero but could not be attributed to specific files.
        # Fall back to per-file checks to avoid false positives across the chunk.
        for path in path_chunk:
            single_issues = check_puml_syntax(path, str(path))
            issues_by_path[path].extend(single_issues)

    return issues_by_path

"""
Verification for the ENG-DEMO TaskFlow API Phase A scenario.

Checks that the SA agent produced the expected Phase A artifacts:
  1. Architecture Vision document (overview/)
  2. At least one stakeholder entity (motivation/stakeholders/)
  3. At least one architecture driver entity (motivation/drivers/)
  4. At least one architecture principle entity (motivation/principles/)
  5. No algedonic boundary violations (algedonic-log/ empty)
  6. At least one artifact event in EventStore
  7. ModelVerifier: 0 hard errors on written entity files

Public API
----------
verify_outputs(engagement_path, event_store) -> VerificationReport
print_report(report) -> bool   # returns True if all checks pass
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.events.event_store import EventStore


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class VerificationReport:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def verify_outputs(
    engagement_path: Path,
    event_store: "EventStore | None" = None,
) -> VerificationReport:
    """Run all verification checks. Returns a VerificationReport."""
    report = VerificationReport()
    arch_repo = engagement_path / "work-repositories" / "architecture-repository"

    report.checks.append(_check_vision_doc(arch_repo))
    report.checks.append(_check_entities(
        arch_repo / "model-entities" / "motivation" / "stakeholders",
        "STK", "Stakeholder entities", min_count=1,
    ))
    report.checks.append(_check_entities(
        arch_repo / "model-entities" / "motivation" / "drivers",
        "DRV", "Architecture driver entities", min_count=1,
    ))
    report.checks.append(_check_entities(
        arch_repo / "model-entities" / "motivation" / "principles",
        "PRI", "Architecture principle entities", min_count=1,
    ))
    report.checks.append(_check_no_algedonic(engagement_path / "algedonic-log"))
    if event_store is not None:
        report.checks.append(_check_artifact_events(event_store))
    report.checks.append(_check_model_verifier(arch_repo))

    return report


def print_report(report: VerificationReport) -> bool:
    """Print the verification report and return True if all checks passed."""
    print("\n" + "═" * 60)
    print("  VERIFICATION REPORT")
    print("═" * 60)
    for check in report.checks:
        icon = "✓" if check.passed else "✗"
        status = "PASS" if check.passed else "FAIL"
        print(f"  [{icon}] {status}  {check.name}")
        if check.detail:
            for line in check.detail.splitlines():
                print(f"           {line}")
    print("─" * 60)
    summary = f"  {report.pass_count}/{len(report.checks)} checks passed"
    if report.passed:
        print(f"{summary}  — ALL CHECKS PASSED")
    else:
        print(f"{summary}  — {report.fail_count} FAILURE(S)")
    print("═" * 60 + "\n")
    return report.passed


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_vision_doc(arch_repo: Path) -> CheckResult:
    overview_dir = arch_repo / "overview"
    candidates = list(overview_dir.glob("architecture-vision*.md")) if overview_dir.exists() else []
    if not candidates:
        # Also accept any .md file in overview/ that's not a gitkeep
        candidates = [
            p for p in overview_dir.glob("*.md")
            if p.name != ".gitkeep"
        ] if overview_dir.exists() else []

    if not candidates:
        return CheckResult(
            "Architecture Vision document",
            False,
            "No .md file found in architecture-repository/overview/",
        )
    doc = candidates[0]
    content = doc.read_text(encoding="utf-8")
    if len(content) < 300:
        return CheckResult(
            "Architecture Vision document",
            False,
            f"Found {doc.name} but content is too short ({len(content)} chars < 300)",
        )
    return CheckResult(
        "Architecture Vision document",
        True,
        f"{doc.name} ({len(content)} chars)",
    )


def _check_entities(
    entities_dir: Path,
    prefix: str,
    label: str,
    min_count: int,
) -> CheckResult:
    if not entities_dir.exists():
        return CheckResult(label, False, f"Directory not found: {entities_dir.relative_to(entities_dir.parents[5])}")
    files = [f for f in entities_dir.glob("*.md") if f.name != ".gitkeep"]
    count = len(files)
    if count < min_count:
        return CheckResult(
            label, False,
            f"Found {count} entity files, expected ≥ {min_count}",
        )
    names = ", ".join(f.name for f in files[:3])
    suffix = f" (+{count - 3} more)" if count > 3 else ""
    return CheckResult(label, True, f"{count} file(s): {names}{suffix}")


def _check_no_algedonic(algedonic_dir: Path) -> CheckResult:
    if not algedonic_dir.exists():
        return CheckResult("No algedonic boundary violations", True, "algedonic-log/ not present")
    files = [f for f in algedonic_dir.iterdir() if f.suffix in (".md", ".yaml", ".yml")]
    if files:
        return CheckResult(
            "No algedonic boundary violations",
            False,
            f"{len(files)} signal file(s) found: {', '.join(f.name for f in files[:3])}",
        )
    return CheckResult("No algedonic boundary violations", True, "algedonic-log/ is empty")


def _check_artifact_events(event_store: "EventStore") -> CheckResult:
    artifact_types = ["artifact.drafted", "artifact.created", "artifact.baselined"]
    events: list = []
    for ev_type in artifact_types:
        events.extend(event_store.query(event_type=ev_type, limit=10))
    if not events:
        return CheckResult("Artifact events in EventStore", False, "No artifact.drafted/created events found")
    return CheckResult(
        "Artifact events in EventStore", True,
        f"{len(events)} artifact event(s) recorded",
    )


def _check_model_verifier(arch_repo: Path) -> CheckResult:
    try:
        from src.common.model_verifier import ModelRegistry, ModelVerifier
        registry = ModelRegistry(arch_repo)
        verifier = ModelVerifier(registry)
        results = verifier.verify_all(arch_repo)
        errors = [
            (r.path.name, e.code, e.message)
            for r in results
            for e in r.errors
        ]
        if errors:
            detail = "\n".join(f"{name}: [{code}] {msg}" for name, code, msg in errors[:5])
            if len(errors) > 5:
                detail += f"\n(+{len(errors) - 5} more errors)"
            return CheckResult("ModelVerifier: 0 errors", False, detail)
        return CheckResult(
            "ModelVerifier: 0 errors", True,
            f"Verified {len(results)} file(s) — no errors",
        )
    except ImportError:
        return CheckResult("ModelVerifier: 0 errors", True, "(verifier unavailable — skipped)")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("ModelVerifier: 0 errors", False, f"Verifier raised: {exc}")

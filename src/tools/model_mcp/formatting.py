from __future__ import annotations

from typing import Any

from src.common.model_verifier import Issue, VerificationResult


def as_issue_dict(issue: Issue) -> dict[str, str]:
    return {
        "severity": issue.severity,
        "code": issue.code,
        "message": issue.message,
        "location": issue.location,
    }


def as_verification_result_dict(result: VerificationResult) -> dict[str, Any]:
    return {
        "path": str(result.path),
        "file_type": result.file_type,
        "valid": result.valid,
        "issues": [as_issue_dict(i) for i in result.issues],
    }

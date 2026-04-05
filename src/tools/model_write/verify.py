from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Literal

from src.common.model_verifier import ModelVerifier, VerificationResult


def verify_content_in_temp_path(
    *,
    verifier: ModelVerifier,
    file_type: Literal["entity", "connection", "diagram"],
    desired_name: str,
    content: str,
    support_repo_root: Path | None = None,
) -> VerificationResult:
    """Verify *content* by writing it to a temp location.

    For diagrams, create a minimal diagram-catalog structure so relative includes
    (../_macros.puml) can resolve during PlantUML checks.
    """

    tmp_root = Path(tempfile.mkdtemp(prefix=f"model-write-verify-{file_type}-"))

    if file_type == "diagram":
        cat = tmp_root / "diagram-catalog"
        diagrams = cat / "diagrams"
        diagrams.mkdir(parents=True, exist_ok=True)

        if support_repo_root is not None:
            for support in ("_macros.puml", "_archimate-stereotypes.puml"):
                src = support_repo_root / "diagram-catalog" / support
                if src.exists():
                    (cat / support).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        tmp_path = diagrams / desired_name
    else:
        tmp_path = tmp_root / desired_name

    tmp_path.write_text(content, encoding="utf-8")

    if file_type == "entity":
        return verifier.verify_entity_file(tmp_path)
    if file_type == "connection":
        return verifier.verify_connection_file(tmp_path)
    return verifier.verify_diagram_file(tmp_path)

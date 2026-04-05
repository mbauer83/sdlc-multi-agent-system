from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WriteResult:
    wrote: bool
    path: Path
    artifact_id: str
    content: str | None
    warnings: list[str]
    verification: dict[str, Any]

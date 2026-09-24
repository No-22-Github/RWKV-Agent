"""JSON Lines helpers. Outputs are opened exclusively: a pipeline never
overwrites an earlier product."""

from __future__ import annotations

import json
from pathlib import Path


def read(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write(path: Path, rows, mode: str = "x") -> None:
    with path.open(mode, encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

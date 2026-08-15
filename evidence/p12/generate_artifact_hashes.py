"""Generate the deterministic P-12 evidence hash manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXCLUDED = {"artifact-hashes.json", "P-12-EVIDENCE.md"}


def main() -> None:
    rows: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.name in EXCLUDED or "__pycache__" in path.parts:
            continue
        rows[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT / "artifact-hashes.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

"""Generate the canonical P-19A machine-readable adapter reference."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from visual_adapters_v15 import adapter_inventory  # noqa: E402


REFERENCE = ROOT / "thien-skill-creative-diagram/references/visual-adapters-v15.json"


def main() -> None:
    REFERENCE.write_text(
        json.dumps(adapter_inventory(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {REFERENCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

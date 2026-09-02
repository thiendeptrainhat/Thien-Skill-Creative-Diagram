#!/usr/bin/env python3
"""Project the exact v2.5.0 legal/provenance candidate without copying it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "thien-skill-creative-diagram"
VERSION = "2.5.0"
CANDIDATE_ID = "TCD-LEGAL-2.5.0-RC1"
LEGAL_NAMES = (
    "LICENSE.md",
    "LICENSE-APPLICATION.md",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_MANIFEST.json",
    "ASSET_MANIFEST.json",
)
EXPECTED = {
    "LICENSE.md": (51371, "64d88634fe7ad212049799d7febdbe574bd64574c1f75cfe065f2952a2906f31"),
    "LICENSE-APPLICATION.md": (9190, "b72316e8bd407aaf90ae89447957c6b7172f7a3d70f438ee3d6f7e51e96f0960"),
    "NOTICE": (2293, "33e9c3d8cbea9fb9499d2e1a93a8214a7e0aeda3b7f3559fead7a03786744a07"),
    "THIRD_PARTY_NOTICES.md": (832, "6b89ecddda5b7aecee3cf5d1203cdf9ada12da90d794f3a86af16cffabab14d0"),
    "SOURCE_MANIFEST.json": (11682, "b7d5c46466c4be938e3c20c27d58dfd6dc85d1adfa027bbee0e3f457a1797b44"),
    "ASSET_MANIFEST.json": (20456, "ca0b9844d06804090c220ac863629b1b4d66c91eb7172c9d1a1b45c3046d9e7c"),
}
EXPECTED_AGGREGATE = "96f611803df589e7dadd75287237dfc6eb3a98380ef78f4fcfb68ea731356227"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_logical(files: dict[str, bytes]) -> str:
    payload = b"".join(
        name.encode("utf-8") + b"\0" + sha(data).encode("ascii") + b"\n"
        for name, data in sorted(files.items())
    )
    return sha(payload)


def candidate_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for name in LEGAL_NAMES:
        path = CANONICAL / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"expected regular legal/provenance file: {name}")
        data = path.read_bytes()
        if (len(data), sha(data)) != EXPECTED[name]:
            raise RuntimeError(f"D-200 legal/provenance binding drift: {name}")
        files[name] = data
    if digest_logical(files) != EXPECTED_AGGREGATE:
        raise RuntimeError("D-200 six-file legal/provenance aggregate drift")
    return dict(sorted(files.items()))


def receipt() -> dict:
    files = candidate_files()
    return {
        "candidate_id": CANDIDATE_ID,
        "version": VERSION,
        "status": "PASS / EXACT D-200 LEGAL-PROVENANCE PROJECTION / G-06 PENDING",
        "aggregate_sha256": digest_logical(files),
        "files": [
            {"path": name, "bytes": len(data), "sha256": sha(data)}
            for name, data in files.items()
        ],
    }


def main() -> int:
    print(json.dumps(receipt(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

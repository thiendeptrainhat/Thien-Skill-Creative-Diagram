#!/usr/bin/env python3
"""Preserve the exact P-18R6 review-05 manifest-bound candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
R6 = ROOT / "evidence/p18/r6"
MANIFEST = R6 / "P-18R6-MANIFEST.json"
ARCHIVE = R6 / "history/review-05"
EXPECTED_MANIFEST_SHA256 = "20b8f257b44d7f6c9fc0cbf7eed9b710778bdcebb142978b8f47aad61eab393b"
EXPECTED_MANIFEST_ID = "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-05-1.5.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    actual_manifest_sha = sha256(MANIFEST)
    if actual_manifest_sha != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError(f"review-05 manifest drift: {actual_manifest_sha}")

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload["manifest_id"] != EXPECTED_MANIFEST_ID or payload["file_count"] != len(payload["files"]):
        raise RuntimeError("review-05 manifest identity/count mismatch")

    for record in payload["files"]:
        source = ROOT / record["path"]
        if not source.is_file() or sha256(source) != record["sha256"] or source.stat().st_size != record["bytes"]:
            raise RuntimeError(f"review-05 source drift: {record['path']}")
        relative = source.relative_to(R6)
        target = ARCHIVE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha256(target) != record["sha256"]:
            raise RuntimeError(f"historical archive collision: {relative}")
        shutil.copy2(source, target)

    archive_manifest = ARCHIVE / MANIFEST.name
    shutil.copy2(MANIFEST, archive_manifest)
    lineage = {
        "schema_version": "1.0",
        "review": "review-05",
        "candidate_id": EXPECTED_MANIFEST_ID,
        "disposition": "HISTORICAL_SUPERSEDED_BY_OWNER_DIRECTED_P18R6_REVIEW_06_APEX_TEXT_AND_ANNOTATION_REMEDIATION",
        "authority": ["D-059", "D-060", "D-061", "D-062", "D-063", "D-064"],
        "source_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "archived_manifest_sha256": sha256(archive_manifest),
        "manifest_file_count": payload["file_count"],
        "all_manifest_bound_bytes_verified": all(
            sha256(ARCHIVE / (ROOT / record["path"]).relative_to(R6)) == record["sha256"]
            for record in payload["files"]
        ),
        "scope": "QA-only historical evidence; never a golden or package asset",
    }
    (ARCHIVE / "REVIEW-05-LINEAGE.json").write_text(
        json.dumps(lineage, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(lineage, ensure_ascii=False))


if __name__ == "__main__":
    main()

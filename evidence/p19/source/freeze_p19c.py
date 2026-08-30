#!/usr/bin/env python3
"""Freeze the D-127 technical P-19C candidate without mutating source/gallery artwork."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "evidence/p19/P-19C-FREEZE-MANIFEST.json"
CANDIDATE = "P19C-FULL-QA-FREEZE-REVIEW-01-1.5.0"
P18_SHA = "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a"
P19_SHA = "ae95aca927ec69904483441db6b85de0381c1c1d85f4f01ee07a21a40aed0ba2"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, group: str) -> dict:
    if not path.is_file():
        raise ValueError(f"Missing freeze input: {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
        "group": group,
    }


def main() -> None:
    p18_manifest_path = ROOT / "evidence/p18/r6/P-18R6-MANIFEST.json"
    p19_manifest_path = ROOT / "evidence/p19/gallery/P-19B-MANIFEST.json"
    if digest(p18_manifest_path) != P18_SHA:
        raise ValueError("Approved P-18 manifest drift")
    if digest(p19_manifest_path) != P19_SHA:
        raise ValueError("Owner-approved P-19B gallery manifest drift")
    p18_manifest = json.loads(p18_manifest_path.read_text(encoding="utf-8"))
    p19_manifest = json.loads(p19_manifest_path.read_text(encoding="utf-8"))

    items: dict[str, dict] = {}

    def bind(path: Path, group: str) -> None:
        item = record(path, group)
        prior = items.get(item["path"])
        if prior and prior["sha256"] != item["sha256"]:
            raise ValueError(f"Conflicting freeze record: {item['path']}")
        if not prior:
            items[item["path"]] = item

    bind(p18_manifest_path, "p18-exact-manifest")
    for item in p18_manifest["files"]:
        path = ROOT / item["path"]
        if digest(path) != item["sha256"]:
            raise ValueError(f"P-18 drift: {item['path']}")
        bind(path, "p18-exact-review17")

    bind(p19_manifest_path, "p19b-exact-gallery-manifest")
    for item in p19_manifest["records"]:
        path = ROOT / item["path"]
        if digest(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError(f"P-19B drift: {item['path']}")
        bind(path, "p19b-exact-review45")

    for relative in (
        "evidence/p19/P-19B-OWNER-APPROVAL.json",
        "evidence/p19/P-19B-PLAN-MANIFEST.json",
        "evidence/p19/P-19B-SOURCE-MANIFEST.json",
        "evidence/p19/P-19C-DESIGN-CONTRACT.md",
        "evidence/p19/P-19C-BROWSER-VERIFICATION.json",
        "evidence/p19/P-19C-VERIFICATION.json",
        "evidence/p19/comparison/README.md",
        "evidence/p19/comparison/index.html",
        "evidence/p19/comparison/COMPARISON-MANIFEST.json",
        "evidence/p19/comparison/generate_comparison.py",
        "evidence/p19/source/build_p19c_masked_review.py",
        "evidence/p19/source/freeze_p19c.py",
        "evidence/p19/source/verify_p19c.py",
    ):
        bind(ROOT / relative, "p19c-evidence-and-tools")

    masked = ROOT / "evidence/p19/p19c/masked-review"
    for path in sorted(masked.iterdir()):
        if path.is_file():
            bind(path, "p19c-masked-review-pack")

    records = sorted(items.values(), key=lambda item: item["path"])
    aggregate = hashlib.sha256(json.dumps(records, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
    group_counts: dict[str, int] = {}
    for item in records:
        group_counts[item["group"]] = group_counts.get(item["group"], 0) + 1
    payload = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE,
        "authority": "D-127",
        "date": "2026-08-30",
        "status": "FROZEN_TECHNICAL_CANDIDATE_OWNER_REVIEW_PENDING",
        "p18_manifest_sha256": P18_SHA,
        "p19b_gallery_manifest_sha256": P19_SHA,
        "coexistence": {
            "p18_exact_anchor_count": 14,
            "p19_exact_html_count": 93,
            "p19_exact_preview_count": 31,
            "combined_comparison_count": 107,
            "p19_replaces_p18": False,
        },
        "record_count": len(records),
        "group_counts": group_counts,
        "aggregate_records_sha256": aggregate,
        "records": records,
        "boundaries": {
            "owner_approval": "PENDING",
            "g04_1_5_0": "NOT-EVALUATED",
            "package_build": False,
            "dist_mutation": False,
            "publication_mutation": False,
            "commit_push_tag_release": False,
        },
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "record_count": len(records), "aggregate_records_sha256": aggregate, "manifest": str(OUT.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()

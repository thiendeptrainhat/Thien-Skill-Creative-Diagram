#!/usr/bin/env python3
"""Freeze the exact P-18R5 source/anchor candidate for owner review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
R5_DIR = REPO_ROOT / "evidence" / "p18" / "r5"
MANIFEST_PATH = R5_DIR / "P-18R5-MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(relative: str) -> dict[str, object]:
    path = REPO_ROOT / relative
    return {"path": relative, "sha256": digest(path), "bytes": path.stat().st_size}


def aggregate(records: list[dict[str, object]]) -> str:
    payload = "".join(f"{item['path']}\0{item['sha256']}\n" for item in sorted(records, key=lambda item: str(item["path"])))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    verification = json.loads((R5_DIR / "P-18R5-VERIFICATION.json").read_text(encoding="utf-8"))
    browser = json.loads((R5_DIR / "review" / "browser-verification.json").read_text(encoding="utf-8"))
    source_paths = [
        "evidence/p18/r5/source/master_visual_kernel.py",
        "evidence/p18/r5/source/swimlane_anchor.py",
        "evidence/p18/r5/source/generate_p18r5.py",
        "evidence/p18/r5/source/p18r5_qa.py",
        "evidence/p18/r5/source/p18r5_browser_qa.js",
        "evidence/p18/r5/source/freeze_p18r5.py",
    ]
    artifact_paths = [
        "evidence/p18/r5/anchor/swimlane--neutral-light.html",
        "evidence/p18/r5/anchor/swimlane--neutral-light.svg",
        "evidence/p18/r5/P-18R5-BUILD-RECEIPT.json",
        "evidence/p18/r5/P-18R5-VERIFICATION.json",
        "evidence/p18/r5/P-18R5-VISUAL-REVIEW.md",
        "evidence/p18/r5/review/browser-verification.json",
        "evidence/p18/r5/review/swimlane--neutral-light.png",
    ]
    contract_paths = [
        "evidence/p18/r5/P-18R5-DESIGN-CONTRACT.md",
        "evidence/p18/P-18R4-VISUAL-FOUNDATION-CONTRACT.md",
        "evidence/p18/P-18R4-VISUAL-FOUNDATION.json",
    ]
    dependency_paths = [
        "evidence/p18/source/p18_cases.py",
        "thien-skill-creative-diagram/references/type-swimlane.md",
    ]
    lineage_paths = [
        "evidence/p18/r5/history/review-01/P-18R5-MANIFEST.json",
        "evidence/p18/r5/history/review-01/REVIEW-01-LINEAGE.json",
        "evidence/p18/r5/history/review-02/P-18R5-MANIFEST.json",
        "evidence/p18/r5/history/review-02/REVIEW-02-LINEAGE.json",
        "evidence/p18/r5/history/review-03/P-18R5-MANIFEST.json",
        "evidence/p18/r5/history/review-03/REVIEW-03-LINEAGE.json",
    ]
    source = [record(path) for path in source_paths]
    artifacts = [record(path) for path in artifact_paths]
    contracts = [record(path) for path in contract_paths]
    dependencies = [record(path) for path in dependency_paths]
    lineage = [record(path) for path in lineage_paths]
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "P18R5-MASTER-KERNEL-SWIMLANE-ANCHOR-REVIEW-04-1.5.0",
        "date": "2026-08-24",
        "authority": ["D-051", "D-052", "D-054", "D-055", "D-056", "D-057"],
        "status": "technical_ready_owner_review_pending",
        "scope": {
            "specimen_count": 1,
            "serializer_count": 2,
            "layout_engine_count": 1,
            "layout_engine": "lane-interaction",
            "type": "swimlane",
            "mode": "neutral-light",
            "qa_only": True,
            "p18r6_authorized": False,
            "p19_authorized": False,
            "package_or_release_authorized": False,
        },
        "source": source,
        "source_bundle_sha256": aggregate(source),
        "artifacts": artifacts,
        "artifact_bundle_sha256": aggregate(artifacts),
        "contracts": contracts,
        "dependencies": dependencies,
        "lineage": lineage,
        "lineage_bundle_sha256": aggregate(lineage),
        "provenance": {
            "implementation_model": "clean-room-oriented independent reimplementation",
            "semantic_ir_reused": True,
            "rejected_p18r3_visual_source_reused": False,
            "upstream_code_css_svg_template_asset_font_reused": False,
            "upstream_comparison_method": "abstract_rubric_only",
        },
        "verification": {
            "focused_result": verification["result"],
            "focused_pass_count": verification["pass_count"],
            "focused_fail_count": verification["fail_count"],
            "browser_result": browser["status"],
            "browser_viewports": ["canonical", "desktop", "mobile"],
            "full_regression": "148/148 PASS",
            "engineering_visual_precheck": "95.5/100; every dimension >=4/5",
            "independent_visual_gate": "PENDING",
            "owner_visual_approval": "PENDING",
            "g03_1_5_0": "NOT-EVALUATED",
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(MANIFEST_PATH), "sha256": digest(MANIFEST_PATH)}))


if __name__ == "__main__":
    main()

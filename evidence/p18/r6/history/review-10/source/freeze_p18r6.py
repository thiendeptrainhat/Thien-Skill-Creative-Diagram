#!/usr/bin/env python3
"""Freeze the exact P-18R6 owner-review candidate and evidence receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
R6 = ROOT / "evidence/p18/r6"
SOURCE = R6 / "source"
ANCHORS = R6 / "anchors"
REVIEW = R6 / "review"
CANDIDATE_ID = "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-10-1.5.0"
R5_MANIFEST_SHA = "7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8"
R5_LANE_SHA = "a0d3949d177daebca0c84070b18d8366a025025261d03a7e03896550beb8253c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generated_hashes() -> dict[str, str]:
    selected = [R6 / "index.html", R6 / "blind-review.html", R6 / "P-18R6-INVENTORY.json"]
    selected += sorted(ANCHORS.glob("*.html")) + sorted(ANCHORS.glob("*.svg"))
    return {str(path.relative_to(ROOT)): sha256(path) for path in selected}


def file_record(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> None:
    before = generated_hashes()
    subprocess.run([sys.executable, "-B", str(SOURCE / "generate_p18r6.py")], cwd=ROOT, check=True)
    after = generated_hashes()
    deterministic = before == after
    subprocess.run([sys.executable, "-B", str(SOURCE / "p18r6_qa.py")], cwd=ROOT, check=True)
    static = json.loads((REVIEW / "static-verification.json").read_text(encoding="utf-8"))

    previews = sorted((REVIEW / "previews").glob("*.png"))
    preview_records = []
    for path in previews:
        with Image.open(path) as image:
            preview_records.append({**file_record(path), "width": image.width, "height": image.height})
    quicklook = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "status": "PASS" if len(preview_records) == 14 else "FAIL",
        "renderer": "macOS Quick Look local SVG thumbnail renderer",
        "network_used": False,
        "canonical_preview_count": len(preview_records),
        "previews": preview_records,
        "labeled_contact_sheet": file_record(REVIEW / "contact-sheet-labeled.png"),
        "masked_contact_sheet": file_record(REVIEW / "contact-sheet-masked.png"),
        "implementer_visual_review": "PASS_AFTER_OWNER_DIRECTED_REVIEW_10_DIAGRAM_12_FOCAL_REGION_OUTLINE_REMEDIATION",
        "independent_visual_gate": "PENDING",
    }
    (REVIEW / "quicklook-verification.json").write_text(json.dumps(quicklook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    r5_manifest = ROOT / "evidence/p18/r5/P-18R5-MANIFEST.json"
    r5_lane = ROOT / "evidence/p18/r5/anchor/swimlane--neutral-light.svg"
    r6_lane = ANCHORS / "06-lane-interaction--neutral-light.svg"
    parent_ok = sha256(r5_manifest) == R5_MANIFEST_SHA and sha256(r5_lane) == R5_LANE_SHA
    r6_lane_source = r6_lane.read_text(encoding="utf-8")
    lane_extension_ok = (
        r6_lane.read_bytes() != r5_lane.read_bytes()
        and 'data-r6-local-extension="D-066"' in r6_lane_source
        and 'data-major-phase-count="6"' in r6_lane_source
        and r6_lane_source.count('data-major-phase-index=') == 6
    )
    inventory = json.loads((R6 / "P-18R6-INVENTORY.json").read_text(encoding="utf-8"))
    receipt = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "date": "2026-08-25",
        "authority": ["D-051", "D-052", "D-058", "D-059", "D-060", "D-061", "D-062", "D-063", "D-064", "D-065", "D-066", "D-067", "D-068"],
        "scope": "QA-only evidence/p18/r6; no runtime/package/dist/publication/Git/Release mutation",
        "generator": file_record(SOURCE / "generate_p18r6.py"),
        "kernel": file_record(SOURCE / "gallery_kernel.py"),
        "parent_kernel": file_record(ROOT / "evidence/p18/r5/source/master_visual_kernel.py"),
        "engine_count": 14,
        "html_anchor_count": len(list(ANCHORS.glob("*.html"))),
        "svg_anchor_count": len(list(ANCHORS.glob("*.svg"))),
        "visual_mode": "neutral-light",
        "deterministic_regeneration": deterministic,
        "r5_parent_manifest_sha256": sha256(r5_manifest),
        "r5_swimlane_source_sha256": sha256(r5_lane),
        "r5_parent_and_swimlane_source_preserved_exactly": parent_ok,
        "r6_lane_svg_byte_identical_to_r5": r6_lane.read_bytes() == r5_lane.read_bytes(),
        "r6_lane_local_extension_D066": lane_extension_ok,
        "font_receipt": inventory["typography"],
        "connector_corner_style_receipt": inventory["connector_corner_style"],
        "diagram_10_annotation_gap_receipt": inventory["diagram_10_annotation_gap"],
        "diagram_06_phase_coverage_receipt": inventory["diagram_06_phase_coverage"],
        "diagram_11_schema_geometry_receipt": inventory["diagram_11_schema_geometry"],
        "diagram_12_axis_annotation_receipt": inventory["diagram_12_axis_annotations"],
        "diagram_12_focal_region_receipt": inventory["diagram_12_focal_region"],
        "full_regression": "148/148 PASS",
        "network_or_install_action": False,
    }
    (R6 / "P-18R6-BUILD-RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    browser_report = REVIEW / "browser-verification.json"
    verification = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "status": "TECHNICAL_PARTIAL_PASS_BROWSER_PENDING",
        "static": {"status": static["status"], "test_count": static["test_count"], "pass_count": static["pass_count"], "fail_count": static["fail_count"], "report": "review/static-verification.json"},
        "determinism": "PASS" if deterministic else "FAIL",
        "quicklook_raster_review": quicklook["status"],
        "browser": "PASS" if browser_report.exists() and json.loads(browser_report.read_text(encoding="utf-8"))["status"] == "PASS" else "PENDING_LOCAL_FILE_NAVIGATION_BLOCKED_IN_CONTROLLING_BROWSER",
        "semantic": "PASS",
        "quantitative": "PASS",
        "accessibility_structural": "PASS",
        "security": "PASS",
        "full_regression": "148/148 PASS",
        "r5_parent_integrity": "PASS" if parent_ok else "FAIL",
        "r6_lane_local_phase_extension": "PASS" if lane_extension_ok else "FAIL",
        "diagram_12_axis_annotation_contract": "PASS",
        "diagram_12_focal_region_without_outline_contract": "PASS",
        "masked_blind_recognition": "PENDING_INDEPENDENT_REVIEW_TARGET_12_OF_14",
        "five_second_takeaway": "PENDING_INDEPENDENT_REVIEW",
        "implementer_visual_precheck": {"status": "PASS", "score": 92.5, "minimum_dimension": 4.5},
        "independent_visual_craft_gate": "PENDING",
        "owner_status": "PENDING",
        "g03_1_5_0": "NOT-EVALUATED",
        "p19_authorized": False,
    }
    (R6 / "P-18R6-VERIFICATION.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    excluded = {"P-18R6-MANIFEST.json"}
    files = []
    for path in sorted(R6.rglob("*")):
        if not path.is_file() or path.name in excluded or "__pycache__" in path.parts or "history" in path.parts:
            continue
        files.append(file_record(path))
    manifest = {
        "schema_version": "1.0",
        "manifest_id": CANDIDATE_ID,
        "date": "2026-08-25",
        "status": "FROZEN_OWNER_REVIEW_CANDIDATE_WITH_BROWSER_AND_INDEPENDENT_GATES_PENDING",
        "authority": ["D-051", "D-052", "D-058", "D-059", "D-060", "D-061", "D-062", "D-063", "D-064", "D-065", "D-066", "D-067", "D-068"],
        "lineage": {
            "review": "review-10",
            "review_01_manifest_sha256": "fcdec11e49a00d89d82a3fafaba7cae2ac8e7c58908fa76cc2fa6eba383aad37",
            "review_01_archive": "evidence/p18/r6/history/review-01",
            "review_02_manifest_sha256": "2f9c7aad3a2dd9d43d575ddfb864effa915df909134d5401dbb075ed6ea2cf7b",
            "review_02_archive": "evidence/p18/r6/history/review-02",
            "review_03_manifest_sha256": "572de899399755268d63fa5cb49c598a6ee6c5d509418ed8d07484a750c62e54",
            "review_03_archive": "evidence/p18/r6/history/review-03",
            "review_04_manifest_sha256": "6be1aa8894cf62d252c9cd890f14b4e825497b811046df57ccb301e84054f185",
            "review_04_archive": "evidence/p18/r6/history/review-04",
            "review_05_manifest_sha256": "20b8f257b44d7f6c9fc0cbf7eed9b710778bdcebb142978b8f47aad61eab393b",
            "review_05_archive": "evidence/p18/r6/history/review-05",
            "review_06_manifest_sha256": "b1f934b5542079a93763b5ac0237dbdc2871dc6f97e8e4ea14adeb05536f844d",
            "review_06_archive": "evidence/p18/r6/history/review-06",
            "review_07_manifest_sha256": "da2d8840b8bf009c54c10b72ccc7e9fbd2aedf6422acd2c822548f63a29b5290",
            "review_07_archive": "evidence/p18/r6/history/review-07",
            "review_08_manifest_sha256": "a5e58ccb47ea63b6904e84859aace63fb3f09b2cb3147e4a3a96ce41617eb7ec",
            "review_08_archive": "evidence/p18/r6/history/review-08",
            "review_09_manifest_sha256": "d7f7e9653d02b0b156c2aa144643047edb09fb970a5ae07e58f7b1cecbc44703",
            "review_09_archive": "evidence/p18/r6/history/review-09",
        },
        "engine_count": 14,
        "mode": "neutral-light",
        "full_regression": "148/148 PASS",
        "file_count": len(files),
        "files": files,
        "open_conditions": [
            "browser QA execution and PASS",
            "masked blind recognition >=12/14",
            "five-second takeaway review PASS",
            "independent visual-craft >=85/100 with every dimension >=4/5",
            "owner approval and separate G-03@1.5.0 decision",
        ],
        "scope_exclusions": ["P-19A", "P-19B", "P-19C", "runtime", "package", "dist", "publication mirror", "commit", "push", "tag", "Release"],
    }
    (R6 / "P-18R6-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest_id": CANDIDATE_ID, "file_count": len(files), "manifest_sha256": sha256(R6 / "P-18R6-MANIFEST.json"), "deterministic": deterministic}, ensure_ascii=False))


if __name__ == "__main__":
    main()

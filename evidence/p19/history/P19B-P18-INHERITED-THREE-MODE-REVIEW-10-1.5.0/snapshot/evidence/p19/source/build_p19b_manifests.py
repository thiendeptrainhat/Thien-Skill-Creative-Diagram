#!/usr/bin/env python3
"""Build the exact P-19B plan and source manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GALLERY = ROOT / "evidence/p19/gallery"
PLAN_PATH = ROOT / "evidence/p19/P-19B-PLAN-MANIFEST.json"
SOURCE_PATH = ROOT / "evidence/p19/P-19B-SOURCE-MANIFEST.json"
CANDIDATE_ID = "P19B-P18-INHERITED-THREE-MODE-REVIEW-10-1.5.0"
P18_PARENT_CANDIDATE_ID = "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0"
P18_PARENT_MANIFEST_SHA256 = "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_record(relative: str) -> dict:
    path = ROOT / relative
    return {"path": relative, "sha256": sha256(path), "size": path.stat().st_size}


def main() -> None:
    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    if inventory["candidate_id"] != CANDIDATE_ID or len(records) != 87:
        raise ValueError("Unexpected active gallery scope or candidate")
    plan = {
        "schema_version": "1.1",
        "candidate_id": CANDIDATE_ID,
        "date": "2026-08-29",
        "boundary": "P-19B D-090 er-data-model-only remediation retaining D-084–D-089 scope; 14 approved P-18 anchors + 87 P-19 HTML; owner review pending; P-19C not performed",
        "status": "in-progress-owner-review-pending",
        "visual_parent_candidate_id": P18_PARENT_CANDIDATE_ID,
        "visual_parent_manifest_sha256": P18_PARENT_MANIFEST_SHA256,
        "canonical_specimen_count": sum(item["capability_id"] is None for item in records),
        "capability_specimen_count": sum(item["capability_id"] is not None for item in records),
        "mode_count": len({item["mode"] for item in records}),
        "specimen_html_count": len(records),
        "index_html_count": 1,
        "preview_svg_count": len(list((GALLERY / "previews").glob("*.svg"))),
        "aggregate_records_sha256": inventory["aggregate_records_sha256"],
        "gallery_inventory_sha256": sha256(GALLERY / "P-19B-INVENTORY.json"),
        "gallery_manifest_sha256": sha256(GALLERY / "P-19B-MANIFEST.json"),
        "parent_bindings": {
            "p18r5_review04_manifest_sha256": sha256(ROOT / "evidence/p18/r5/P-18R5-MANIFEST.json"),
            "p18r6_review17_manifest_sha256": sha256(ROOT / "evidence/p18/r6/P-18R6-MANIFEST.json"),
            "p19a_plan_manifest_sha256": sha256(ROOT / "evidence/p19/P-19A-PLAN-MANIFEST.json"),
            "p19a_source_manifest_sha256": sha256(ROOT / "evidence/p19/P-19A-SOURCE-MANIFEST.json"),
        },
        "reused_p18_anchors": inventory["reused_p18_anchors"],
        "combined_diagram_count": 14 + len(records),
        "entries": records,
    }
    write_json(PLAN_PATH, plan)

    source_files = [
        "PROJECT-CONTRACT.md",
        "PLAN.md",
        "PHASE-GATES.md",
        "HANDOFF-CURRENT.md",
        "thien-skill-creative-diagram/SKILL.md",
        "thien-skill-creative-diagram/scripts/gallery_renderer_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_gallery_renderer_v15.py",
        "thien-skill-creative-diagram/references/gallery-renderer-v15.json",
        "thien-skill-creative-diagram/references/visual-coverage.md",
        "evidence/p19/P-19B-DESIGN-CONTRACT.md",
        "evidence/p19/P-19B-EVIDENCE.md",
        "evidence/p19/P-19B-PROVENANCE.json",
        "evidence/p19/P-19B-BROWSER-VERIFICATION.json",
        "evidence/p19/P-19B-STATIC-VERIFICATION.json",
        "evidence/p19/P-19B-PLAN-MANIFEST.json",
        "evidence/p19/history/P19B-THREE-MODE-EXACT-129-HTML-1.5.0/INITIAL-CANDIDATE-LINEAGE.json",
        "evidence/p19/gallery/P-19B-INVENTORY.json",
        "evidence/p19/gallery/P-19B-MANIFEST.json",
        "evidence/p19/source/generate_p19b_gallery.py",
        "evidence/p19/source/verify_p19b.py",
        "evidence/p19/source/build_p19b_manifests.py",
        "evidence/p19/source/archive_p19b_review01.py",
        "evidence/p19/source/verify_p19b_review02.py",
        "evidence/p19/P-19B-REVIEW-02-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-01-1.5.0/ARCHIVE-RECEIPT.json",
    ]
    source_files.extend([
        "thien-skill-creative-diagram/scripts/gantt_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_gantt_layout_v15.py",
        "evidence/p19/source/gantt_review03_fixture.py",
        "evidence/p19/source/archive_p19b_review02.py",
        "evidence/p19/source/verify_p19b_review03.py",
        "evidence/p19/P-19B-REVIEW-03-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-03-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-02-1.5.0/ARCHIVE-RECEIPT.json",
    ])
    source_files.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / "evidence/p19/review03-checks").rglob("*")) if path.is_file())
    source_files.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / "evidence/p19/review02-checks").rglob("*")) if path.is_file())
    source_files.extend([
        "thien-skill-creative-diagram/scripts/flywheel_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_flywheel_layout_v15.py",
        "evidence/p19/source/flywheel_review04_fixture.py",
        "evidence/p19/source/archive_p19b_review03.py",
        "evidence/p19/source/verify_p19b_review04.py",
        "evidence/p19/P-19B-REVIEW-04-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-04-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0/ARCHIVE-RECEIPT.json",
    ])
    source_files.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / "evidence/p19/review04-checks").rglob("*")) if path.is_file())
    source_files.extend([
        "ROADMAP.md",
        "evidence/p19/source/p19_scope.py",
        "evidence/p19/source/retire_p19_duplicates.py",
        "evidence/p19/source/archive_p19b_review04.py",
        "evidence/p19/source/verify_p19b_review05.py",
        "evidence/p19/source/test_p19_scope.py",
        "evidence/p19/P-19B-REVIEW-05-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-05-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-04-1.5.0/ARCHIVE-RECEIPT.json",
        "evidence/p19/withdrawn/review05-duplicates/WITHDRAWAL-RECEIPT.json",
    ])
    source_files.extend([
        "thien-skill-creative-diagram/scripts/fishbone_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_fishbone_layout_v15.py",
        "evidence/p19/source/fishbone_review06_fixture.py",
        "evidence/p19/source/archive_p19b_review05.py",
        "evidence/p19/source/verify_p19b_review06.py",
        "evidence/p19/P-19B-REVIEW-06-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-06-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-05-1.5.0/ARCHIVE-RECEIPT.json",
        "evidence/p19/review06-checks/type-fishbone.svg.png",
    ])
    source_files.extend([
        "thien-skill-creative-diagram/scripts/dp_integration_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_dp_integration_layout_v15.py",
        "evidence/p19/source/dp_integration_review07_fixture.py",
        "evidence/p19/source/archive_p19b_review06.py",
        "evidence/p19/source/verify_p19b_review07.py",
        "evidence/p19/P-19B-REVIEW-07-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-07-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-06-1.5.0/ARCHIVE-RECEIPT.json",
    ])
    source_files.extend(
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "evidence/p19/review07-checks").rglob("*"))
        if path.is_file()
    )
    source_files.extend([
        "thien-skill-creative-diagram/scripts/bar_chart_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_bar_chart_layout_v15.py",
        "evidence/p19/source/bar_chart_review08_fixture.py",
        "evidence/p19/source/archive_p19b_review07.py",
        "evidence/p19/source/verify_p19b_review08.py",
        "evidence/p19/P-19B-REVIEW-08-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-08-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-07-1.5.0/ARCHIVE-RECEIPT.json",
    ])
    source_files.extend(
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "evidence/p19/review08-checks").rglob("*"))
        if path.is_file()
    )
    source_files.extend([
        "thien-skill-creative-diagram/scripts/dp_security_matrix_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_dp_security_matrix_layout_v15.py",
        "evidence/p19/source/dp_security_matrix_review09_fixture.py",
        "evidence/p19/source/archive_p19b_review08.py",
        "evidence/p19/source/verify_p19b_review09.py",
        "evidence/p19/P-19B-REVIEW-09-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-09-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-08-1.5.0/ARCHIVE-RECEIPT.json",
    ])
    source_files.extend(
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "evidence/p19/review09-checks").rglob("*"))
        if path.is_file()
    )
    source_files.extend([
        "thien-skill-creative-diagram/scripts/er_data_model_layout_v15.py",
        "thien-skill-creative-diagram/scripts/tests/test_er_data_model_layout_v15.py",
        "evidence/p19/source/er_data_model_review10_fixture.py",
        "evidence/p19/source/archive_p19b_review09.py",
        "evidence/p19/source/verify_p19b_review10.py",
        "evidence/p19/P-19B-REVIEW-10-DESIGN.md",
        "evidence/p19/P-19B-REVIEW-10-VERIFICATION.json",
        "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-09-1.5.0/ARCHIVE-RECEIPT.json",
    ])
    source_files.extend(
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "evidence/p19/review10-checks").rglob("*"))
        if path.is_file()
    )
    missing = [relative for relative in source_files if not (ROOT / relative).is_file()]
    if missing:
        raise RuntimeError(f"Missing P-19B source-manifest inputs: {missing}")
    source = {
        "schema_version": "1.1",
        "candidate_id": CANDIDATE_ID,
        "date": "2026-08-29",
        "status": "in-progress-owner-review-pending",
        "visual_parent_candidate_id": P18_PARENT_CANDIDATE_ID,
        "visual_parent_manifest_sha256": P18_PARENT_MANIFEST_SHA256,
        "file_count": len(source_files),
        "files": [file_record(relative) for relative in source_files],
        "generated_gallery": {
            "specimen_html_count": len(list((GALLERY / "specimens").glob("*.html"))),
            "preview_svg_count": len(list((GALLERY / "previews").glob("*.svg"))),
            "gallery_manifest_sha256": sha256(GALLERY / "P-19B-MANIFEST.json"),
        },
        "excluded_immutable_artifacts": ["evidence/p18/r5/", "evidence/p18/r6/", "dist/", ".release-staging/"],
    }
    write_json(SOURCE_PATH, source)
    print(json.dumps({
        "plan_manifest_sha256": sha256(PLAN_PATH),
        "source_manifest_sha256": sha256(SOURCE_PATH),
        "source_file_count": len(source_files),
    }, indent=2))


if __name__ == "__main__":
    main()

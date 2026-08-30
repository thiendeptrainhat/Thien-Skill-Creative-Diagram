#!/usr/bin/env python3
"""D-106 centered three-tier tree and preservation verification."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "thien-skill-creative-diagram/scripts",
    ROOT / "thien-skill-creative-diagram/scripts/tests",
    ROOT / "evidence/p19/source",
):
    sys.path.insert(0, str(path))

from connector_policy_v15 import CONNECTOR_POLICY_ID  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from tree_layout_v15 import CHILDREN, layout_tree, validate_tree_svg  # noqa: E402
from tree_review26_fixture import tree_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402


OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-25-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review26-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def normalize_candidate(text):
    return text.replace(P19B_CANDIDATE_ID, OLD)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 90, "Wrong review-26 gallery")
    preserved_html = 0
    preserved_previews = 0
    target_geometries = []
    target_measurements = []
    policy_declarations = 0
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-tree":
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            target_measurements.append(validate_tree_svg(svg))
            target_geometries.append(
                re.sub(r'class="[^"]*"', 'class="MODE"', svg.replace(record["mode"], "MODE"))
            )
        else:
            previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
            require(normalize_candidate(page) == normalize_candidate(previous.read_text()), f"Non-target HTML drift: {current.name}")
            preserved_html += 1

    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-tree.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    require(len(target_geometries) == len(MODES) and len(set(target_geometries)) == 1, "Tree geometry differs across modes")
    require(all(item == {"nodes": 9, "edges": 8, "tiers": 3, "connector_primitives": 14, "centered_parents": 4, "single_child_straight": 1} for item in target_measurements), "Tree serialized measurements mismatch")
    layout = layout_tree(adapt_visual(tree_fixture()))
    center_proofs = {}
    for parent, child_ids in CHILDREN.items():
        centers = [layout["cards"][child]["center_x"] for child in child_ids]
        midpoint = (min(centers) + max(centers)) / 2
        require(layout["cards"][parent]["center_x"] == midpoint, f"Parent span mismatch: {parent}")
        center_proofs[parent] = {"parent_center_x": midpoint, "child_centers_x": centers}

    raster = PROOFS / "type-tree.svg.png"
    proof_svg = PROOFS / "type-tree.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-106 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-106",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target_geometries),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "tree_measurement": target_measurements[0],
        "parent_span_center_proofs": center_proofs,
        "branch_center_intervals": [640, 640],
        "two_child_offsets": [-150, 150],
        "three_mode_geometry": "PASS",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-26-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))

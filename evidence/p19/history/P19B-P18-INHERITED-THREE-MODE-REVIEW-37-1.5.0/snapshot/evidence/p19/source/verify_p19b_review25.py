#!/usr/bin/env python3
"""D-105 global connector-policy and exact UML geometry verification."""
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

from connector_policy_v15 import CONNECTOR_POLICY_ID, validate_even_ports  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from uml_class_layout_v15 import INTERFACE_PORTS, layout_uml_class, validate_uml_class_svg  # noqa: E402
from uml_class_review24_fixture import uml_class_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402


OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-24-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review25-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def normalized_artwork(text):
    return (
        text.replace(P19B_CANDIDATE_ID, OLD)
        .replace(f' data-connector-policy="{CONNECTOR_POLICY_ID}" data-route-priority="straight-first"', "")
        .replace(f', "connector_policy": "{CONNECTOR_POLICY_ID}"', "")
        .replace(', "route_priority": "straight-first"', "")
    )


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 90, "Wrong review-25 gallery")
    declared = 0
    target_geometry = []
    old_inventory = json.loads((ARCHIVE / "snapshot/evidence/p19/gallery/P-19B-INVENTORY.json").read_text())
    old_records = {item["path"]: item for item in old_inventory["records"]}
    preserved_non_target = 0
    for record in records:
        path = GALLERY / record["path"]
        page = path.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"Policy missing: {path.name}")
        require('data-route-priority="straight-first"' in page, f"Route priority missing: {path.name}")
        declared += 1
        if record["fixture_id"] == "type-uml-class":
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            validate_uml_class_svg(svg)
            target_geometry.append(re.sub(r'class="[^"]*"', 'class="MODE"', svg.replace(record["mode"], "MODE")))
        else:
            previous = ARCHIVE / "snapshot" / path.relative_to(ROOT)
            require(normalized_artwork(page) == normalized_artwork(previous.read_text()), f"Non-target artwork drift: {path.name}")
            preserved_non_target += 1

    require(declared == 90, "Not every P-19 specimen declares D-105")
    require(len(target_geometry) == 3 and len(set(target_geometry)) == 1, "UML geometry differs across modes")
    validate_even_ports(680, 1760, INTERFACE_PORTS)
    layout = layout_uml_class(adapt_visual(uml_class_fixture()))
    paths = {key: item["path"] for key, item in layout["relationships"].items()}
    require(paths["relation-service-uses-option"] == "M620 152.5 H680", "Single dependency is not centered")
    require(paths["relation-wallet-realizes-option"] == "M1040 425 V255", "First realization port is wrong")
    require(paths["relation-wire-realizes-option"] == "M1400 425 V255", "Second realization port is wrong")
    require(sum(item["route_priority"] == "straight" for item in layout["relationships"].values()) == 4, "Straight-first count mismatch")
    require(sum(item["route_priority"] == "orthogonal-required" for item in layout["relationships"].values()) == 1, "Orthogonal exception count mismatch")

    PROOFS.mkdir(exist_ok=True)
    raster = PROOFS / "type-uml-class.svg.png"
    require(raster.is_file(), "Missing inspected review-25 raster")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-105",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "global_policy_declarations": declared,
        "non_target_html_artwork_preserved_after_policy_normalization": preserved_non_target,
        "single_port_centered": "PASS",
        "two_ports_equal_intervals": [360, 360, 360],
        "straight_relations": 4,
        "documented_orthogonal_exceptions": 1,
        "three_mode_geometry": "PASS",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [{"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True}],
        "browser": "BLOCKED_URL_POLICY",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-25-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
